"""AC-BKG-06 (DOM-PDPA-01)
Given มีการเปิดดูข้อมูลการจองของผู้รับบริการ
When  การเข้าถึงเสร็จสิ้น
Then  มี audit log ที่ระบุผู้เข้าถึง เวลา และรหัสผู้รับบริการ
"""
from datetime import date
from datetime import time as dt_time

from fastapi.testclient import TestClient

from app.db.models import AuditLog, Slot
from app.main import app

client = TestClient(app)


def test_AC_BKG_06(db_session):
    slot = Slot(slot_date=date.today(), start_time=dt_time(9, 0), package_code="PKG-A", capacity=1, remaining=1)
    db_session.add(slot)
    db_session.commit()
    db_session.refresh(slot)

    created = client.post("/bookings", json={"slot_id": slot.id}, headers={"X-Identity-Token": "HN0005"})
    booking_id = created.json()["id"]

    response = client.get(f"/bookings/{booking_id}", headers={"X-Identity-Token": "STAFF-001"})
    assert response.status_code == 200

    logs = db_session.query(AuditLog).filter(AuditLog.hn == "HN0005").all()
    assert len(logs) == 1
    log = logs[0]
    assert log.actor_id == "STAFF-001"
    assert log.accessed_at is not None
