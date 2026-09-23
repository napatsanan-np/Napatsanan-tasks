"""บันทึก audit log ทุกครั้งที่มีการเปิดดูข้อมูลการจอง — รองรับ DOM-PDPA-01"""
import re

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.db.models import AuditLog, Booking
from app.db.session import get_sessionmaker

_BOOKING_DETAIL_PATH = re.compile(r"^/bookings/(?P<booking_id>\d+)$")


class AuditLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        match = _BOOKING_DETAIL_PATH.match(request.url.path)
        if request.method == "GET" and match and response.status_code == 200:
            self._record_access(request, booking_id=int(match.group("booking_id")))

        return response

    def _record_access(self, request: Request, booking_id: int) -> None:
        session_factory = get_sessionmaker()
        db = session_factory()
        try:
            booking = db.get(Booking, booking_id)
            if booking is None:
                return
            db.add(
                AuditLog(
                    actor_id=request.headers.get("X-Identity-Token", "unknown"),
                    action="view_booking",
                    hn=booking.hn,
                )
            )
            db.commit()
        finally:
            db.close()
