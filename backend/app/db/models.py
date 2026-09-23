"""ตารางฐานข้อมูลของฟีเจอร์จองคิวตรวจสุขภาพ (SPEC-BKG-001) — T-01"""
from datetime import date, datetime, time, timezone

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Time
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Slot(Base):
    """ช่วงเวลาตรวจและที่นั่งคงเหลือ — รองรับ FR-BKG-01, FR-BKG-06, ASM-01"""

    __tablename__ = "slots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slot_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    package_code: Mapped[str] = mapped_column(String(50), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    remaining: Mapped[int] = mapped_column(Integer, nullable=False)


class Booking(Base):
    """การจองของผู้รับบริการ เก็บเฉพาะ HN ไม่เก็บเลขบัตรประชาชน — รองรับ FR-BKG-02, FR-BKG-04, IF-HIS-01"""

    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hn: Mapped[str] = mapped_column(String(20), nullable=False)
    slot_id: Mapped[int] = mapped_column(ForeignKey("slots.id"), nullable=False)
    booking_date: Mapped[date] = mapped_column(Date, nullable=False)
    # รูปแบบและวิธีออกเลขคิวยังไม่กำหนด รอคำตอบ Q-02 จึงเก็บเป็นช่องว่างได้ไปก่อน (ดู T-15)
    queue_no: Mapped[str | None] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="confirmed")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)


class AuditLog(Base):
    """บันทึกทุกครั้งที่เข้าถึงข้อมูลการจอง — รองรับ DOM-PDPA-01"""

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    actor_id: Mapped[str] = mapped_column(String(50), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    hn: Mapped[str] = mapped_column(String(20), nullable=False)
    accessed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)
