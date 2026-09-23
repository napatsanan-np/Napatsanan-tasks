"""ยืนยัน 'เสร็จเมื่อ' ของ T-14: GET /patients/lookup คืน hn จากเลขบัตร และไม่มีการเก็บเลขบัตรลงฐานข้อมูล"""
from fastapi.testclient import TestClient
from sqlalchemy import inspect

from app.main import app

client = TestClient(app)
HEADERS = {"X-Identity-Token": "STAFF-001"}


def test_T14_lookup_returns_hn():
    response = client.get("/patients/lookup", params={"national_id": "1234567890123"}, headers=HEADERS)
    assert response.status_code == 200
    assert response.json()["hn"]


def test_T14_bookings_table_still_has_no_national_id_column(db_session):
    columns = {col["name"] for col in inspect(db_session.get_bind()).get_columns("bookings")}
    assert "national_id" not in columns
