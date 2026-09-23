"""คำนวณช่วงเวลาว่างตามแพ็กเกจ — รองรับ FR-BKG-01, FR-BKG-06"""
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.db.models import Slot

# ASM-02: "วันเดียวกัน" ใช้เขตเวลา Asia/Bangkok
BANGKOK_TZ = ZoneInfo("Asia/Bangkok")


def today_bangkok() -> date:
    return datetime.now(BANGKOK_TZ).date()


def get_available_slots(db: Session, package_code: str, date_from: date | None = None) -> list[Slot]:
    """หาช่วงเวลาของแต่ละวันภายใน 30 วันข้างหน้า ตามแพ็กเกจที่เลือก — รองรับ FR-BKG-01, FR-BKG-06"""
    start = date_from or today_bangkok()
    end = start + timedelta(days=30)
    return (
        db.query(Slot)
        .filter(Slot.package_code == package_code)
        .filter(Slot.slot_date >= start)
        .filter(Slot.slot_date <= end)
        .order_by(Slot.slot_date, Slot.start_time)
        .all()
    )
