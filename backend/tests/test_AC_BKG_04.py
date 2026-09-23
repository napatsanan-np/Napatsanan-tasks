"""AC-BKG-04 (FR-BKG-05, NFR-REL-02)
Given ระบบแจ้งเตือนไม่ตอบสนอง
When  ยืนยันการจอง
Then  การจองถูกบันทึก แสดงหมายเลขคิว และมีรายการในคิวส่งซ้ำที่กำหนดส่งภายใน 5 นาที

หมายเหตุ: การตรวจ "แสดงหมายเลขคิว" ตัวจริงยังทำไม่ได้ รอ Q-02 (ดู T-15, T-16) จึงตรวจเฉพาะว่าการจอง
ถูกบันทึกสำเร็จ (มี booking id กลับมา) และมีรายการในคิวส่งซ้ำที่กำหนดส่งภายใน 5 นาที ตามที่ plan.md ข้อ 6 ระบุขอบเขตการทดสอบนี้ไว้
"""
from datetime import date, datetime, timedelta, timezone
from datetime import time as dt_time

from fastapi.testclient import TestClient

import app.notify.queue as notify_queue
from app.db.models import Slot
from app.main import app

client = TestClient(app)
HEADERS = {"X-Identity-Token": "HN0004"}


def _failing_send(job):
    raise RuntimeError("ระบบแจ้งเตือนไม่ตอบสนอง")


def test_AC_BKG_04(db_session, monkeypatch):
    monkeypatch.setattr(notify_queue, "_default_send", _failing_send)
    notify_queue.default_queue._jobs.clear()

    slot = Slot(slot_date=date.today(), start_time=dt_time(9, 0), package_code="PKG-A", capacity=1, remaining=1)
    db_session.add(slot)
    db_session.commit()
    db_session.refresh(slot)

    response = client.post("/bookings", json={"slot_id": slot.id}, headers=HEADERS)

    assert response.status_code == 201
    assert response.json()["id"] is not None

    jobs = list(notify_queue.default_queue._jobs)
    assert len(jobs) == 1
    job = jobs[0]
    assert job.status == "pending_retry"
    assert job.scheduled_at is not None
    assert job.scheduled_at <= datetime.now(timezone.utc) + timedelta(minutes=5)
