"""ยืนยัน 'เสร็จเมื่อ' ของ T-10: GET /bookings/{id} คืนรายละเอียดการจองของ booking นั้น"""
from datetime import date
from datetime import time as dt_time

from fastapi.testclient import TestClient

from app.db.models import Slot
from app.main import app

client = TestClient(app)
HEADERS = {"X-Identity-Token": "HN0003"}


def test_T10_get_booking_detail(db_session):
    slot = Slot(slot_date=date.today(), start_time=dt_time(9, 0), package_code="PKG-A", capacity=1, remaining=1)
    db_session.add(slot)
    db_session.commit()
    db_session.refresh(slot)

    created = client.post("/bookings", json={"slot_id": slot.id}, headers=HEADERS)
    booking_id = created.json()["id"]

    response = client.get(f"/bookings/{booking_id}", headers=HEADERS)

    assert response.status_code == 200
    assert response.json()["id"] == booking_id
    assert response.json()["hn"] == "HN0003"


def test_T10_returns_404_when_booking_not_found(db_session):
    response = client.get("/bookings/999999", headers=HEADERS)
    assert response.status_code == 404
