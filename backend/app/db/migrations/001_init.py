"""Migration แรก: สร้างตาราง slots, bookings, audit_logs — รองรับ CON-TECH-01"""
from sqlalchemy.engine import Engine

from app.db.models import Base


def upgrade(engine: Engine) -> None:
    Base.metadata.create_all(engine)
