"""สร้าง engine และ session ตาม DATABASE_URL ที่ตั้งค่าไว้ — รองรับ CON-TECH-01"""
import threading
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import get_database_url

# sqlite in-memory ใช้ connection เดียวร่วมกันทุก thread (ดู get_engine) การยิงคำขอพร้อมกันจริง ๆ
# (เช่นตอนทดสอบ AC-BKG-05) จึงชนกันในระดับ DBAPI ได้ ล็อกนี้จึงทำให้แต่ละ request เข้าถึงฐานข้อมูล
# ทีละคำขอเฉพาะตอนใช้ sqlite เท่านั้น (PostgreSQL ใน production มี connection pool ของตัวเองอยู่แล้ว ไม่ต้องล็อก)
_sqlite_access_lock = threading.Lock()


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """สร้าง engine เดียวใช้ร่วมกันทั้งแอป

    หมายเหตุ: sqlite in-memory ผูก connection กับ thread ที่สร้างมันโดยปกติ (SingletonThreadPool)
    แต่ FastAPI รันแต่ละ request ใน thread ของ threadpool ทำให้แต่ละ request เจอฐานข้อมูล in-memory
    คนละก้อนกัน (ว่างเปล่า ไม่มีตาราง) จึงต้องใช้ StaticPool + check_same_thread=False กับ sqlite
    เพื่อให้ทุก thread แชร์ connection เดียวกันจริง (ไม่กระทบ PostgreSQL ที่ใช้ใน production)
    """
    url = get_database_url()
    if url.startswith("sqlite"):
        return create_engine(url, connect_args={"check_same_thread": False}, poolclass=StaticPool)
    return create_engine(url)


def get_sessionmaker(engine: Engine | None = None):
    return sessionmaker(bind=engine or get_engine(), autoflush=False, autocommit=False)


def get_db() -> Session:
    """FastAPI dependency: เปิด session จาก engine เดียวกันทั้งแอป แล้วปิดหลังใช้งานเสร็จ — รองรับ CON-TECH-01

    เพิ่มเข้ามาตอน /implement T-05 (ทีมอนุมัติให้ขยายไฟล์นี้นอกช่อง "ไฟล์ที่แตะ" ของ T-05)
    เพื่อให้ทุก router ใช้ engine/session เดียวกันจริง ไม่สร้าง engine ซ้ำจนข้อมูลแยกฐานกันตอนทดสอบ
    """
    session_factory = get_sessionmaker()
    session = session_factory()
    is_sqlite = get_database_url().startswith("sqlite")
    try:
        if is_sqlite:
            with _sqlite_access_lock:
                yield session
        else:
            yield session
    finally:
        session.close()
