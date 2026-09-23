"""ยืนยัน 'เสร็จเมื่อ' ของ T-05: GET /slots คืนช่วงเวลาใน 30 วันตามแพ็กเกจ และเปลี่ยน package_code แล้วผลลัพธ์เปลี่ยนตาม"""
from datetime import date, time, timedelta

from fastapi.testclient import TestClient

from app.db.models import Slot
from app.main import app

client = TestClient(app)
HEADERS = {"X-Identity-Token": "mock-token"}


def _seed_slot(db_session, package_code: str, days_ahead: int, remaining: int) -> None:
    db_session.add(
        Slot(
            slot_date=date.today() + timedelta(days=days_ahead),
            start_time=time(9, 0),
            package_code=package_code,
            capacity=10,
            remaining=remaining,
        )
    )
    db_session.commit()


def test_T05_lists_slots_within_30_days_and_excludes_beyond(db_session):
    _seed_slot(db_session, package_code="PKG-A", days_ahead=5, remaining=3)
    _seed_slot(db_session, package_code="PKG-A", days_ahead=40, remaining=3)

    response = client.get("/slots", params={"package_code": "PKG-A"}, headers=HEADERS)

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["package_code"] == "PKG-A"
    assert body[0]["remaining"] == 3


def test_T05_changing_package_code_returns_different_slots(db_session):
    _seed_slot(db_session, package_code="PKG-A", days_ahead=2, remaining=5)
    _seed_slot(db_session, package_code="PKG-B", days_ahead=2, remaining=7)

    response_a = client.get("/slots", params={"package_code": "PKG-A"}, headers=HEADERS)
    response_b = client.get("/slots", params={"package_code": "PKG-B"}, headers=HEADERS)

    assert [s["package_code"] for s in response_a.json()] == ["PKG-A"]
    assert [s["package_code"] for s in response_b.json()] == ["PKG-B"]
