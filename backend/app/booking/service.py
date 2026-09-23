"""ตัดที่นั่งและบันทึกการจอง — รองรับ FR-BKG-04

หมายเหตุ hn: ใช้ค่าที่ได้จาก require_verified_identity (IF-IDP-01) โดยตรงเป็น HN
ตาม design ของ /implement T-04 ที่จำลองผลยืนยันตัวตนด้วย header เดียว (ยังไม่ต่อ HIS lookup จริงจาก T-14)
"""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.db.models import Booking, Slot
from app.notify.queue import send_confirmation

BANGKOK_TZ = ZoneInfo("Asia/Bangkok")


class SlotNotFoundError(Exception):
    """ไม่พบ slot_id ที่ระบุ"""

    def __init__(self, slot_id: int):
        self.slot_id = slot_id


class SlotFullError(Exception):
    """ช่วงเวลาที่เลือกเต็มแล้ว — รองรับ FR-BKG-03"""

    def __init__(self, slot: Slot):
        self.slot = slot


class DuplicateBookingError(Exception):
    """มีคิวที่ยังไม่ได้ใช้ในวันเดียวกันอยู่แล้ว — รองรับ FR-BKG-02"""

    def __init__(self, existing_booking: Booking):
        self.existing_booking = existing_booking


def _find_unused_booking_on_date(db: Session, hn: str, booking_date) -> Booking | None:
    return (
        db.query(Booking)
        .filter(Booking.hn == hn)
        .filter(Booking.booking_date == booking_date)
        .filter(Booking.status == "confirmed")
        .first()
    )


def find_nearby_slots(db: Session, package_code: str, target_date, target_time, limit: int = 3) -> list[Slot]:
    """หาช่วงเวลาที่ว่างใกล้เคียงที่สุด ภายในวันเดียวกันและวันถัดไป — รองรับ FR-BKG-03"""
    next_date = target_date + timedelta(days=1)
    candidates = (
        db.query(Slot)
        .filter(Slot.package_code == package_code)
        .filter(Slot.slot_date.in_([target_date, next_date]))
        .filter(Slot.remaining > 0)
        .all()
    )

    target_dt = datetime.combine(target_date, target_time)

    def distance_seconds(slot: Slot) -> float:
        return abs((datetime.combine(slot.slot_date, slot.start_time) - target_dt).total_seconds())

    candidates.sort(key=distance_seconds)
    return candidates[:limit]


def create_booking(db: Session, hn: str, slot_id: int) -> Booking:
    slot = db.get(Slot, slot_id)
    if slot is None:
        raise SlotNotFoundError(slot_id)
    if slot.remaining <= 0:
        raise SlotFullError(slot)

    existing = _find_unused_booking_on_date(db, hn=hn, booking_date=slot.slot_date)
    if existing is not None:
        raise DuplicateBookingError(existing)

    slot.remaining -= 1
    booking = Booking(
        hn=hn,
        slot_id=slot_id,
        booking_date=slot.slot_date,
        status="confirmed",
        created_at=datetime.now(BANGKOK_TZ),
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)

    # ส่งคำขอส่งข้อความยืนยันแบบ asynchronous โดยไม่รอผลและไม่ทำให้การจองล้มเหลว — รองรับ FR-BKG-05, IF-NOT-01
    send_confirmation(booking_id=booking.id, hn=hn, message="ยืนยันการจองสำเร็จ")

    return booking


def get_booking(db: Session, booking_id: int) -> Booking | None:
    """ดึงรายละเอียดการจอง 1 รายการ — รองรับ FR-BKG-05"""
    return db.get(Booking, booking_id)
