"""ยืนยัน 'เสร็จเมื่อ' ของ T-01: models.py import ได้ไม่มี error และ bookings ไม่มีคอลัมน์ national_id (IF-HIS-01)"""
from sqlalchemy import create_engine, inspect

from app.db.models import AuditLog, Base, Booking, Slot


def test_T01_all_tables_are_created():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    table_names = set(inspect(engine).get_table_names())
    assert {"slots", "bookings", "audit_logs"}.issubset(table_names)


def test_T01_bookings_table_has_no_national_id_column():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    column_names = {col["name"] for col in inspect(engine).get_columns("bookings")}
    assert "national_id" not in column_names
    assert {"id", "hn", "slot_id", "booking_date", "queue_no", "status", "created_at"}.issubset(column_names)
