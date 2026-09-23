# Prompt Log

บันทึกนี้เพิ่มต่อท้ายเท่านั้น ห้ามแก้หรือลบของเดิม

## 2569-09-23 — /tasks specs/001-booking/spec.md
คำสั่งที่ใช้: `/tasks specs/001-booking/spec.md`
อ่าน spec.md (SPEC-BKG-001, Status: Draft v2, ผ่าน /clarify แล้ว) และ plan.md (plan v1) ของฟีเจอร์ 001-booking
แล้วแตกเป็น `specs/001-booking/tasks.md`

ผลลัพธ์: สร้าง task ทั้งหมด 20 task (T-01 ถึง T-20) เรียงตามการพึ่งพา: โมเดลข้อมูล -> API หลังบ้าน -> หน้าจอ (ใช้ API จำลอง) -> เชื่อมหน้าจอกับ API จริง
- ทุก AC (AC-BKG-01 ถึง AC-BKG-06) มี task ที่ "ตรวจด้วย" ครบ
- ทุก Constraint (CON-TECH-01, DOM-PDPA-01, IF-IDP-01, IF-HIS-01, IF-NOT-01) มี task ที่ทำให้เป็นจริงครบ
- 2 task (T-15 ออกหมายเลขคิว, T-16 ทดสอบ AC-BKG-01) มีสถานะ "รอ Q-02" เพราะยังไม่มีคำตอบเรื่องรูปแบบหมายเลขคิวจากเจ้าหน้าที่เวชระเบียน ไม่ได้เดาคำตอบ
- บันทึกไว้ใน tasks.md ว่า FR-BKG-06 ยังไม่มี AC ในสเปก จึงยังไม่มี task ทดสอบเฉพาะ ให้ทีมพิจารณาว่าจะเพิ่ม AC หรือไม่

ยังไม่เริ่มลงมือทำ task ใด ๆ ตามกติกาโปรเจกต์ รอทีมสั่งแยกต่างหาก

## 2569-09-23 — /implement T-01 specs/001-booking/tasks.md
คำสั่งที่ใช้: `/implement T-01 specs/001-booking/tasks.md`

ไฟล์ที่สร้าง:
- backend/app/db/models.py (ตาม "ไฟล์ที่แตะ" ของ T-01) — ตาราง Slot, Booking, AuditLog
- backend/app/__init__.py, backend/app/db/__init__.py — โครงพื้นฐานให้ import path `app.db.models` ใช้งานได้ ไม่ได้อยู่ในช่อง "ไฟล์ที่แตะ" ของ tasks.md แต่จำเป็นให้ "เสร็จเมื่อ" (import ได้ไม่ error) เป็นจริง
- backend/tests/test_T01_models.py — เทสยืนยัน "เสร็จเมื่อ" (สร้างตารางได้ครบ, bookings ไม่มีคอลัมน์ national_id) ก็ไม่ได้อยู่ในช่อง "ไฟล์ที่แตะ" เช่นกัน

สิ่งที่เกือบต้องเดาแต่ถามทีมแทน: tasks.md ระบุ "ไฟล์ที่แตะ" ของ T-01 ไว้แค่ backend/app/db/models.py ไฟล์เดียว
แต่กติกา /implement ข้อ 1 บังคับให้เขียน test เล็ก ๆ ยืนยัน "เสร็จเมื่อ" เมื่อ task ไม่มี AC ตรง ๆ ซึ่งขัดกับกติกา "ห้ามแตะไฟล์นอกช่องไฟล์ที่แตะ"
ถามทีมผ่าน AskUserQuestion แล้วได้คำตอบ: ให้สร้างไฟล์ test เพิ่ม และสร้าง __init__.py ให้ด้วย

ผล test: **ยังไม่ได้รัน** เครื่องนี้ไม่มี Python ติดตั้งจริง (มีแค่ Microsoft Store alias ของ python/python3 ที่เรียกใช้ไม่ได้)
ทีมต้องติดตั้ง Python 3.12 แล้วรัน `cd backend && pip install -r requirements.txt && pytest tests/test_T01_models.py -v` เพื่อยืนยันผลจริงก่อน commit
