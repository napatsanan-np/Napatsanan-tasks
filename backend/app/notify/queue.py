"""วางงานส่งข้อความยืนยันลงคิวแบบ asynchronous และส่งซ้ำเมื่อไม่สำเร็จ — รองรับ IF-NOT-01, FR-BKG-05

หมายเหตุ: plan.md เลือกใช้ Redis เป็นคิวจริงตอน production แต่ยังไม่มี redis client อยู่ใน
requirements.txt และ "ไฟล์ที่แตะ" ของ T-11/T-12 ไม่ได้รวม requirements.txt จึงทำคิวจำลองในหน่วยความจำไว้ก่อน
ตามที่ "เสร็จเมื่อ" ต้องการ ("จำลองในหน่วยความจำตอนทดสอบ") การต่อ Redis จริงเป็นงานแยกที่ทีมต้องตัดสินใจ
เพิ่มไลบรารีและรายละเอียดการเชื่อมต่อภายหลัง เช่นเดียวกับช่องทางส่ง SMS/LINE จริงที่ spec/plan ยังไม่ได้ระบุ
รายละเอียดการเชื่อมต่อ จึงใช้ _default_send เป็น stub ที่ถือว่าส่งสำเร็จเสมอไปก่อน
"""
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta

MAX_ATTEMPTS = 3  # ASM-03: ส่งซ้ำสูงสุด 3 ครั้ง
RETRY_INTERVAL = timedelta(minutes=5)  # ASM-03, NFR-REL-02: ห่างกัน/ภายใน 5 นาที


@dataclass
class NotificationJob:
    booking_id: int
    hn: str
    message: str
    attempts: int = 0
    status: str = "pending"  # pending | sent | pending_retry | failed_permanently
    scheduled_at: datetime | None = None


class InMemoryNotificationQueue:
    """คิวส่งข้อความจำลองในหน่วยความจำ — ใช้แทน Redis ตอนทดสอบ/รันในเครื่องนักศึกษา"""

    def __init__(self) -> None:
        self._jobs: deque[NotificationJob] = deque()

    def enqueue(self, booking_id: int, hn: str, message: str) -> NotificationJob:
        job = NotificationJob(booking_id=booking_id, hn=hn, message=message)
        self._jobs.append(job)
        return job

    def __len__(self) -> int:
        return len(self._jobs)

    def pop(self) -> NotificationJob | None:
        return self._jobs.popleft() if self._jobs else None


default_queue = InMemoryNotificationQueue()


def _default_send(job: NotificationJob) -> None:
    """จุดเชื่อมต่อระบบแจ้งเตือน SMS/LINE จริง ยังไม่ได้ระบุรายละเอียดใน spec/plan จึง stub ว่าสำเร็จเสมอ"""
    return None


def enqueue_confirmation_message(booking_id: int, hn: str, message: str) -> NotificationJob:
    """วางงานส่งข้อความยืนยันลงคิว โดยไม่รอผลการส่ง — รองรับ IF-NOT-01"""
    return default_queue.enqueue(booking_id=booking_id, hn=hn, message=message)


def send_confirmation(
    booking_id: int,
    hn: str,
    message: str,
    send_fn=None,
    queue: InMemoryNotificationQueue | None = None,
) -> NotificationJob:
    """ส่งข้อความยืนยัน ถ้าไม่สำเร็จให้นัดส่งซ้ำภายใน 5 นาที สูงสุด 3 ครั้ง — รองรับ FR-BKG-05, NFR-REL-02, ASM-03"""
    active_queue = queue or default_queue
    job = active_queue.enqueue(booking_id=booking_id, hn=hn, message=message)
    sender = send_fn or _default_send

    job.attempts += 1
    try:
        sender(job)
        job.status = "sent"
        job.scheduled_at = None
    except Exception:
        if job.attempts >= MAX_ATTEMPTS:
            job.status = "failed_permanently"
            job.scheduled_at = None
        else:
            job.status = "pending_retry"
            job.scheduled_at = datetime.utcnow() + RETRY_INTERVAL

    return job
