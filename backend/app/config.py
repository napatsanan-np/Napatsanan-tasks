"""อ่านค่าตั้งค่าการเชื่อมต่อฐานข้อมูลจากตัวแปรแวดล้อม DATABASE_URL — รองรับ CON-TECH-01"""
import os


def get_database_url() -> str:
    value = os.environ.get("DATABASE_URL")
    if not value:
        raise RuntimeError("ต้องตั้งค่าตัวแปรแวดล้อม DATABASE_URL ก่อนเชื่อมต่อฐานข้อมูล")
    return value
