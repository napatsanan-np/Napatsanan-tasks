"""ตรวจผลยืนยันตัวตนจากระบบยืนยันตัวตนก่อนเข้าถึงข้อมูลผู้รับบริการ — รองรับ IF-IDP-01

หมายเหตุ: ระบบยืนยันตัวตนจริง (UC-13) อยู่นอกขอบเขตของฟีเจอร์นี้ (spec.md ระบุเป็น precondition)
จึงจำลองผลยืนยันตัวตนด้วย HTTP header X-Identity-Token ที่ endpoint ทุกตัวต้องได้รับมาก่อน
(ตามที่ทีมตัดสินใจไว้ตอน /implement T-04 — ยังไม่ใช่การเชื่อมต่อระบบยืนยันตัวตนจริง)
"""
from fastapi import Header, HTTPException, status


def require_verified_identity(x_identity_token: str | None = Header(default=None)) -> str:
    if not x_identity_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ต้องผ่านการยืนยันตัวตนก่อนเข้าถึงข้อมูลผู้รับบริการ (IF-IDP-01)",
        )
    return x_identity_token
