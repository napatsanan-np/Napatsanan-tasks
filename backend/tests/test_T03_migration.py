"""ยืนยัน 'เสร็จเมื่อ' ของ T-03: fixture db_session สร้างตาราง slots, bookings, audit_logs สำเร็จ"""
from sqlalchemy import inspect


def test_T03_db_session_fixture_creates_all_tables(db_session):
    table_names = set(inspect(db_session.get_bind()).get_table_names())
    assert {"slots", "bookings", "audit_logs"}.issubset(table_names)
