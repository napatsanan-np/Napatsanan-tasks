"""ยืนยัน 'เสร็จเมื่อ' ของ T-07: POST /bookings บันทึกการจองและลด remaining ของ slot ลง 1"""
from datetime import date
from datetime import time as dt_time

from fastapi.testclient import TestClient

from app.db.models import Slot
from app.main import app

client = TestClient(app)
HEADERS = {"X-Identity-Token": "HN0001"}


def test_T07_creates_booking_and_decrements_remaining(db_session):
    slot = Slot(slot_date=date.today(), start_time=dt_time(9, 0), package_code="PKG-A", capacity=1, remaining=1)
    db_session.add(slot)
    db_session.commit()
    db_session.refresh(slot)

    response = client.post("/bookings", json={"slot_id": slot.id}, headers=HEADERS)

    assert response.status_code == 201
    body = response.json()
    assert body["hn"] == "HN0001"
    assert body["slot_id"] == slot.id

    db_session.refresh(slot)
    assert slot.remaining == 0
