"""GET /slots — รองรับ FR-BKG-01, FR-BKG-06"""
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.idp import require_verified_identity
from app.db.session import get_db
from app.slots.service import get_available_slots

router = APIRouter()


@router.get("/slots")
def list_slots(
    package_code: str = Query(...),
    date_from: date | None = Query(default=None),
    db: Session = Depends(get_db),
    _identity: str = Depends(require_verified_identity),
):
    slots = get_available_slots(db, package_code=package_code, date_from=date_from)
    return [
        {
            "id": slot.id,
            "slot_date": slot.slot_date.isoformat(),
            "start_time": slot.start_time.isoformat(),
            "package_code": slot.package_code,
            "remaining": slot.remaining,
        }
        for slot in slots
    ]
