"""AC-BKG-02 (FR-BKG-02)
Given มีคิวที่ยังไม่ได้ใช้ในวันเดียวกัน
When  จองคิวใหม่ในวันเดียวกัน
Then  ปฏิเสธ และแสดงหมายเลขคิวเดิม
"""
from datetime import date
from datetime import time as dt_time

from fastapi.testclient import TestClient

from app.db.models import Slot
from app.main import app

client = TestClient(app)
HEADERS = {"X-Identity-Token": "HN0002"}


def test_AC_BKG_02(db_session):
    slot1 = Slot(slot_date=date.today(), start_time=dt_time(9, 0), package_code="PKG-A", capacity=5, remaining=5)
    slot2 = Slot(slot_date=date.today(), start_time=dt_time(10, 0), package_code="PKG-A", capacity=5, remaining=5)
    db_session.add_all([slot1, slot2])
    db_session.commit()
    db_session.refresh(slot1)
    db_session.refresh(slot2)

    first = client.post("/bookings", json={"slot_id": slot1.id}, headers=HEADERS)
    assert first.status_code == 201
    first_booking_id = first.json()["id"]

    second = client.post("/bookings", json={"slot_id": slot2.id}, headers=HEADERS)

    assert second.status_code == 409
    assert second.json()["detail"]["booking"]["id"] == first_booking_id

    db_session.refresh(slot2)
    assert slot2.remaining == 5
