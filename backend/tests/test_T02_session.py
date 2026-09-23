"""ยืนยัน 'เสร็จเมื่อ' ของ T-02: สร้าง engine/session จาก DATABASE_URL ได้ และชี้ไป sqlite in-memory ได้ตอนทดสอบ"""
import pytest

from app.config import get_database_url
from app.db.session import get_engine, get_sessionmaker


def test_T02_get_database_url_reads_env_var(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    assert get_database_url() == "sqlite:///:memory:"


def test_T02_get_database_url_raises_when_not_set(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(RuntimeError):
        get_database_url()


def test_T02_engine_and_session_point_to_sqlite_in_memory(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")

    engine = get_engine()
    assert str(engine.url) == "sqlite:///:memory:"

    session_factory = get_sessionmaker()
    with session_factory() as session:
        assert session.is_active
