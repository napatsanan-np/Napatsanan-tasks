"""เตรียมฐานข้อมูลทดสอบ (sqlite in-memory) ให้ทุก test ใช้ — รองรับ CON-TECH-01

หมายเหตุ: ตั้งแต่ /implement T-05 เป็นต้นไป get_engine() ถูก cache ไว้ตัวเดียวทั้งโปรเซส (เพื่อให้ทุก
router ใช้ฐานข้อมูลเดียวกันจริงตอนทดสอบ) fixture นี้จึงต้อง drop_all แล้ว create_all ใหม่ก่อนทุก test
เพื่อไม่ให้ข้อมูลจาก test ก่อนหน้าตกค้างข้ามไปยัง test ถัดไป
"""
import importlib
import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

import pytest
from sqlalchemy.orm import sessionmaker

from app.db.models import Base
from app.db.session import get_engine

_migration = importlib.import_module("app.db.migrations.001_init")


@pytest.fixture()
def db_session():
    engine = get_engine()
    Base.metadata.drop_all(engine)
    _migration.upgrade(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
