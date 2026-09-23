"""AC-BKG-05 (NFR-PERF-01): ทดสอบสมรรถนะ GET /slots แบบย่อส่วน
Given ผู้ใช้พร้อมกัน 200 คน (ย่อส่วนเป็น 20 คน เพราะรันบนเครื่องนักศึกษา ไม่ใช่เครื่องทดสอบจริง)
When  ค้นหาช่วงเวลาว่างพร้อมกัน
Then  p95 ของเวลาตอบสนองไม่เกิน 2 วินาที (ผลจริงต้องวัดซ้ำบนเครื่องทดสอบตามที่ plan.md ระบุ)
"""
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from datetime import time as dt_time

from fastapi.testclient import TestClient

from app.db.models import Slot
from app.main import app

client = TestClient(app)
HEADERS = {"X-Identity-Token": "mock-token"}

CONCURRENT_USERS = 20


def test_AC_BKG_05(db_session):
    db_session.add(
        Slot(slot_date=date.today(), start_time=dt_time(9, 0), package_code="PKG-A", capacity=100, remaining=100)
    )
    db_session.commit()

    def call(_):
        start = time.perf_counter()
        response = client.get("/slots", params={"package_code": "PKG-A"}, headers=HEADERS)
        elapsed = time.perf_counter() - start
        assert response.status_code == 200
        return elapsed

    with ThreadPoolExecutor(max_workers=CONCURRENT_USERS) as executor:
        durations = sorted(executor.map(call, range(CONCURRENT_USERS)))

    p95_index = max(int(len(durations) * 0.95) - 1, 0)
    assert durations[p95_index] <= 2.0
