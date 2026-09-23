"""สร้าง engine และ session ตาม DATABASE_URL ที่ตั้งค่าไว้ — รองรับ CON-TECH-01"""
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_database_url


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    return create_engine(get_database_url())


def get_sessionmaker(engine: Engine | None = None):
    return sessionmaker(bind=engine or get_engine(), autoflush=False, autocommit=False)


def get_db() -> Session:
    """FastAPI dependency: เปิด session จาก engine เดียวกันทั้งแอป แล้วปิดหลังใช้งานเสร็จ — รองรับ CON-TECH-01

    เพิ่มเข้ามาตอน /implement T-05 (ทีมอนุมัติให้ขยายไฟล์นี้นอกช่อง "ไฟล์ที่แตะ" ของ T-05)
    เพื่อให้ทุก router ใช้ engine/session เดียวกันจริง ไม่สร้าง engine ซ้ำจนข้อมูลแยกฐานกันตอนทดสอบ
    """
    session_factory = get_sessionmaker()
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
