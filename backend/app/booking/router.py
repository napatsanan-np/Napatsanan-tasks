"""POST /bookings — รองรับ FR-BKG-04, FR-BKG-02, FR-BKG-03"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.idp import require_verified_identity
from app.booking.service import (
    DuplicateBookingError,
    SlotFullError,
    SlotNotFoundError,
    create_booking,
    find_nearby_slots,
    get_booking,
)
from app.db.session import get_db

router = APIRouter()


class BookingRequest(BaseModel):
    slot_id: int


def _booking_to_dict(booking) -> dict:
    return {
        "id": booking.id,
        "hn": booking.hn,
        "slot_id": booking.slot_id,
        "booking_date": booking.booking_date.isoformat(),
        "queue_no": booking.queue_no,
        "status": booking.status,
    }


def _slot_to_dict(slot) -> dict:
    return {
        "id": slot.id,
        "slot_date": slot.slot_date.isoformat(),
        "start_time": slot.start_time.isoformat(),
        "package_code": slot.package_code,
        "remaining": slot.remaining,
    }


@router.post("/bookings", status_code=status.HTTP_201_CREATED)
def book_slot(
    payload: BookingRequest,
    db: Session = Depends(get_db),
    identity: str = Depends(require_verified_identity),
):
    try:
        booking = create_booking(db, hn=identity, slot_id=payload.slot_id)
    except DuplicateBookingError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "มีคิวที่ยังไม่ได้ใช้ในวันเดียวกันอยู่แล้ว",
                "booking": _booking_to_dict(exc.existing_booking),
            },
        )
    except SlotFullError as exc:
        nearby = find_nearby_slots(
            db,
            package_code=exc.slot.package_code,
            target_date=exc.slot.slot_date,
            target_time=exc.slot.start_time,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "ช่วงเวลาเต็ม",
                "nearby_slots": [_slot_to_dict(s) for s in nearby],
            },
        )
    except SlotNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบช่วงเวลาที่ระบุ")

    return _booking_to_dict(booking)


@router.get("/bookings/{booking_id}")
def get_booking_detail(
    booking_id: int,
    db: Session = Depends(get_db),
    _identity: str = Depends(require_verified_identity),
):
    booking = get_booking(db, booking_id)
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบการจองที่ระบุ")
    return _booking_to_dict(booking)
