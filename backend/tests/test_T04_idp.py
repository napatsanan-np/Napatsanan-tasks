"""ยืนยัน 'เสร็จเมื่อ' ของ T-04: dependency ปฏิเสธ request ที่ไม่มีผลยืนยันตัวตน และผ่านเมื่อมี header"""
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.auth.idp import require_verified_identity


def _build_app() -> FastAPI:
    app = FastAPI()

    @app.get("/protected")
    def protected(identity: str = Depends(require_verified_identity)):
        return {"identity": identity}

    return app


def test_T04_rejects_request_without_identity_header():
    client = TestClient(_build_app())
    response = client.get("/protected")
    assert response.status_code == 401


def test_T04_allows_request_with_identity_header():
    client = TestClient(_build_app())
    response = client.get("/protected", headers={"X-Identity-Token": "mock-token-123"})
    assert response.status_code == 200
    assert response.json() == {"identity": "mock-token-123"}
