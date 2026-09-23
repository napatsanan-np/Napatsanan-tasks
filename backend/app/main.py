"""สร้าง FastAPI app และรวม router ของฟีเจอร์จองคิวตรวจสุขภาพ (SPEC-BKG-001)"""
from fastapi import Depends, FastAPI, Query

from app.audit.middleware import AuditLogMiddleware
from app.auth.idp import require_verified_identity
from app.booking.router import router as booking_router
from app.his.client import lookup_hn_by_national_id
from app.slots.router import router as slots_router

app = FastAPI(title="Booking API")
app.include_router(slots_router)
app.include_router(booking_router)
app.add_middleware(AuditLogMiddleware)


@app.get("/patients/lookup")
def lookup_patient(
    national_id: str = Query(...),
    _identity: str = Depends(require_verified_identity),
):
    """ค้นข้อมูลผู้รับบริการจาก HIS ด้วยเลขบัตรประชาชน แล้วคืน HN — รองรับ IF-HIS-01"""
    return {"hn": lookup_hn_by_national_id(national_id)}
