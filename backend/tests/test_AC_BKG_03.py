"""AC-BKG-03 (FR-BKG-03)
Given ช่วง 09.00 น. เหลือ 1 ที่ และผู้ใช้อีกคนยืนยันก่อน
      และวันเดียวกันกับวันถัดไปมีช่วงที่ว่างอย่างน้อย 3 ช่วง
When  ผู้ใช้กดยืนยันช่วง 09.00 น.
Then  แจ้ง "ช่วงเวลาเต็ม" แสดง 3 ช่วงที่ว่างและใกล้ 09.00 น. ที่สุด
      ภายในวันเดียวกันและวันถัดไป และไม่มีรายการจองซ้อนเกิดขึ้น
"""
from datetime import date, timedelta
from datetime import time as dt_time

from fastapi.testclient import TestClient

from app.db.models import Booking, Slot
from app.main import app

client = TestClient(app)


def _slot(day: date, hour: int, minute: int, remaining: int) -> Slot:
    return Slot(
        slot_date=day,
        start_time=dt_time(hour, minute),
        package_code="PKG-A",
        capacity=5,
        remaining=remaining,
    )


def test_AC_BKG_03(db_session):
    today = date.today()
    tomorrow = today + timedelta(days=1)

    target_slot = _slot(today, 9, 0, remaining=1)
    near_08 = _slot(today, 8, 0, remaining=2)
    near_10 = _slot(today, 10, 0, remaining=2)
    near_11 = _slot(today, 11, 0, remaining=2)
    far_tomorrow = _slot(tomorrow, 9, 0, remaining=2)

    db_session.add_all([target_slot, near_08, near_10, near_11, far_tomorrow])
    db_session.commit()
    db_session.refresh(target_slot)

    # ผู้ใช้อีกคนยืนยันก่อน ทำให้ช่วง 09.00 เต็ม
    first = client.post(
        "/bookings", json={"slot_id": target_slot.id}, headers={"X-Identity-Token": "HN-OTHER"}
    )
    assert first.status_code == 201

    # ผู้ใช้ปัจจุบันกดยืนยันช่วง 09.00 ที่เต็มแล้ว
    response = client.post(
        "/bookings", json={"slot_id": target_slot.id}, headers={"X-Identity-Token": "HN-CURRENT"}
    )

    assert response.status_code == 409
    detail = response.json()["detail"]
    assert detail["message"] == "ช่วงเวลาเต็ม"

    nearby_keys = [(s["slot_date"], s["start_time"]) for s in detail["nearby_slots"]]
    assert len(nearby_keys) == 3
    assert (today.isoformat(), "08:00:00") in nearby_keys
    assert (today.isoformat(), "10:00:00") in nearby_keys
    assert (today.isoformat(), "11:00:00") in nearby_keys
    assert (tomorrow.isoformat(), "09:00:00") not in nearby_keys

    db_session.refresh(target_slot)
    assert target_slot.remaining == 0
    assert db_session.query(Booking).filter(Booking.hn == "HN-CURRENT").count() == 0
