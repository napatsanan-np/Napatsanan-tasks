"""ยืนยัน 'เสร็จเมื่อ' ของ T-11: มีฟังก์ชันวางงานส่งข้อความลงคิว (จำลองในหน่วยความจำ) และทำงานแบบไม่บล็อก"""
import time

from app.notify.queue import InMemoryNotificationQueue, enqueue_confirmation_message


def test_T11_enqueue_adds_job_to_queue():
    queue = InMemoryNotificationQueue()
    job = queue.enqueue(booking_id=1, hn="HN001", message="ยืนยันการจองสำเร็จ")

    assert len(queue) == 1
    assert queue.pop() is job


def test_T11_enqueue_confirmation_message_does_not_block():
    start = time.perf_counter()
    enqueue_confirmation_message(booking_id=2, hn="HN002", message="ยืนยันการจองสำเร็จ")
    elapsed = time.perf_counter() - start

    assert elapsed < 0.1
