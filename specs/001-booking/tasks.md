# Tasks: จองคิวตรวจสุขภาพ (Booking)
Feature: SPEC-BKG-001 | อ้างอิง: spec.md (Draft v2), plan.md (plan v1) | วันที่: 2569-09-23

สรุป: ทำทั้งหมด 20 task
มี 2 task ที่ "รอ Q-02" (T-15, T-16) — ยังไม่มีคำตอบเรื่องรูปแบบหมายเลขคิว

## รายการ task

### T-01 สร้างตาราง slots, bookings, audit_logs
- รองรับ: CON-TECH-01, IF-HIS-01, DOM-PDPA-01, ASM-01
- ตรวจด้วย: ไม่มี AC ตรง ๆ เป็นงานพื้นฐานของ T-01
- ไฟล์ที่แตะ: backend/app/db/models.py
- ต้องทำหลัง: ไม่มี
- เสร็จเมื่อ: import models.py ได้โดยไม่มี error และตาราง bookings ไม่มีคอลัมน์ national_id ตามที่ plan.md ข้อ 3 กำหนด
- สถานะ: พร้อมทำ

### T-02 ตั้งค่าการเชื่อมต่อฐานข้อมูล
- รองรับ: CON-TECH-01
- ตรวจด้วย: ไม่มี AC ตรง ๆ เป็นงานพื้นฐานของ T-02
- ไฟล์ที่แตะ: backend/app/config.py, backend/app/db/session.py
- ต้องทำหลัง: T-01
- เสร็จเมื่อ: สร้าง engine/session จากตัวแปร DATABASE_URL ได้ และชี้ไป sqlite in-memory ได้ตอนทดสอบ
- สถานะ: พร้อมทำ

### T-03 สร้าง migration และเตรียมฐานข้อมูลทดสอบ
- รองรับ: CON-TECH-01
- ตรวจด้วย: ไม่มี AC ตรง ๆ เป็นงานพื้นฐานของ T-03
- ไฟล์ที่แตะ: backend/app/db/migrations/001_init.py, backend/tests/conftest.py, backend/pytest.ini
- ต้องทำหลัง: T-02
- เสร็จเมื่อ: รัน `cd backend && pytest` แล้ว fixture สร้างตาราง slots, bookings, audit_logs สำเร็จโดยไม่มี error
- สถานะ: พร้อมทำ

### T-04 สร้างตัวตรวจสอบผลยืนยันตัวตน
- รองรับ: IF-IDP-01
- ตรวจด้วย: ไม่มี AC ตรง ๆ เป็นงานพื้นฐานของ T-04
- ไฟล์ที่แตะ: backend/app/auth/idp.py
- ต้องทำหลัง: ไม่มี
- เสร็จเมื่อ: มี dependency ที่ endpoint เรียกใช้เพื่อตรวจผลยืนยันตัวตนก่อนเข้าถึงข้อมูล และ test ยืนยันว่า request ที่ไม่มีผลยืนยันตัวตนถูกปฏิเสธ
- สถานะ: พร้อมทำ

### T-05 สร้าง GET /slots หาช่วงเวลาว่างตามแพ็กเกจ
- รองรับ: FR-BKG-01, FR-BKG-06
- ตรวจด้วย: ไม่มี AC ตรง ๆ เป็นงานพื้นฐานของ T-05 (AC-BKG-05 แยกทดสอบใน T-06)
- ไฟล์ที่แตะ: backend/app/slots/router.py, backend/app/slots/service.py, backend/app/main.py
- ต้องทำหลัง: T-03, T-04
- เสร็จเมื่อ: เรียก GET /slots?date_from=...&package_code=... แล้วได้รายการช่วงเวลาภายใน 30 วันพร้อมที่นั่งคงเหลือ และเปลี่ยน package_code แล้วผลลัพธ์เปลี่ยนตาม
- สถานะ: พร้อมทำ

### T-06 ทดสอบสมรรถนะ GET /slots แบบย่อส่วน
- รองรับ: NFR-PERF-01
- ตรวจด้วย: AC-BKG-05
- ไฟล์ที่แตะ: backend/tests/test_AC_BKG_05.py
- ต้องทำหลัง: T-05
- เสร็จเมื่อ: test_AC_BKG_05 ผ่าน (ยิงคำขอพร้อมกันแบบย่อส่วนใน Codespace แล้วดู p95 ในสภาพแวดล้อมทดสอบนี้ ผลจริงต้องวัดซ้ำบนเครื่องทดสอบตามที่ plan.md ระบุ)
- สถานะ: พร้อมทำ

### T-07 สร้าง POST /bookings พื้นฐาน
- รองรับ: FR-BKG-04
- ตรวจด้วย: ไม่มี AC ตรง ๆ เป็นงานพื้นฐานของ T-07 (AC-BKG-01 ต้องรอ T-16 ซึ่งรอ Q-02)
- ไฟล์ที่แตะ: backend/app/booking/router.py, backend/app/booking/service.py, backend/app/main.py
- ต้องทำหลัง: T-05
- เสร็จเมื่อ: POST /bookings ด้วย slot_id ที่ว่าง บันทึกแถวใน bookings และลด remaining ของ slot นั้นลง 1 สำเร็จ
- สถานะ: พร้อมทำ

### T-08 กันจองซ้ำวันเดียวกัน
- รองรับ: FR-BKG-02, ASM-02
- ตรวจด้วย: AC-BKG-02
- ไฟล์ที่แตะ: backend/app/booking/service.py, backend/tests/test_AC_BKG_02.py
- ต้องทำหลัง: T-07
- เสร็จเมื่อ: test_AC_BKG_02 ผ่าน
- สถานะ: พร้อมทำ

### T-09 เสนอช่วงเวลาใกล้เคียงเมื่อช่วงที่เลือกเต็ม
- รองรับ: FR-BKG-03
- ตรวจด้วย: AC-BKG-03
- ไฟล์ที่แตะ: backend/app/booking/service.py, backend/app/booking/router.py, backend/tests/test_AC_BKG_03.py
- ต้องทำหลัง: T-08
- เสร็จเมื่อ: test_AC_BKG_03 ผ่าน
- สถานะ: พร้อมทำ

### T-10 สร้าง GET /bookings/{id} แสดงรายละเอียดการจอง
- รองรับ: FR-BKG-05
- ตรวจด้วย: ไม่มี AC ตรง ๆ เป็นงานพื้นฐานของ T-10
- ไฟล์ที่แตะ: backend/app/booking/router.py, backend/app/booking/service.py
- ต้องทำหลัง: T-07
- เสร็จเมื่อ: เรียก GET /bookings/{id} แล้วได้รายละเอียดการจองของ booking นั้นกลับมา
- สถานะ: พร้อมทำ

### T-11 สร้างคิวส่งข้อความยืนยันแบบ asynchronous
- รองรับ: IF-NOT-01
- ตรวจด้วย: ไม่มี AC ตรง ๆ เป็นงานพื้นฐานของ T-11
- ไฟล์ที่แตะ: backend/app/notify/queue.py
- ต้องทำหลัง: T-07
- เสร็จเมื่อ: มีฟังก์ชันวางงานส่งข้อความลงคิว (จำลองในหน่วยความจำตอนทดสอบ) และ POST /bookings ไม่ต้องรอฟังก์ชันนี้ทำงานเสร็จก่อนตอบกลับ
- สถานะ: พร้อมทำ

### T-12 ส่งซ้ำเมื่อส่งข้อความไม่สำเร็จ
- รองรับ: FR-BKG-05, NFR-REL-02, ASM-03
- ตรวจด้วย: AC-BKG-04
- ไฟล์ที่แตะ: backend/app/notify/queue.py, backend/app/booking/service.py, backend/tests/test_AC_BKG_04.py
- ต้องทำหลัง: T-11
- เสร็จเมื่อ: test_AC_BKG_04 ผ่าน
- สถานะ: พร้อมทำ

### T-13 สร้าง audit log middleware
- รองรับ: DOM-PDPA-01
- ตรวจด้วย: AC-BKG-06
- ไฟล์ที่แตะ: backend/app/audit/middleware.py, backend/app/main.py, backend/tests/test_AC_BKG_06.py
- ต้องทำหลัง: T-04, T-10
- เสร็จเมื่อ: test_AC_BKG_06 ผ่าน
- สถานะ: พร้อมทำ

### T-14 สร้าง GET /patients/lookup ค้น HN จาก HIS
- รองรับ: IF-HIS-01
- ตรวจด้วย: ไม่มี AC ตรง ๆ เป็นงานพื้นฐานของ T-14
- ไฟล์ที่แตะ: backend/app/his/client.py, backend/app/main.py
- ต้องทำหลัง: T-04
- เสร็จเมื่อ: เรียก GET /patients/lookup ด้วยเลขบัตรประชาชนแล้วได้ hn กลับมา และไม่มีการเก็บเลขบัตรประชาชนลงฐานข้อมูลของระบบนี้
- สถานะ: พร้อมทำ

### T-15 ออกหมายเลขคิว
- รองรับ: FR-BKG-04
- ตรวจด้วย: ไม่มี AC ตรง ๆ (T-16 ตรวจ AC-BKG-01 ต่อจากงานนี้)
- ไฟล์ที่แตะ: backend/app/booking/service.py
- ต้องทำหลัง: T-07
- เสร็จเมื่อ: -
- สถานะ: รอ Q-02 (รูปแบบหมายเลขคิว รีเซ็ตรายวันหรือนับต่อเนื่อง ยังไม่มีคำตอบจากเจ้าหน้าที่เวชระเบียน)

### T-16 ทดสอบ AC-BKG-01
- รองรับ: FR-BKG-04
- ตรวจด้วย: AC-BKG-01
- ไฟล์ที่แตะ: backend/tests/test_AC_BKG_01.py
- ต้องทำหลัง: T-15
- เสร็จเมื่อ: -
- สถานะ: รอ Q-02

### T-17 หน้าเลือกแพ็กเกจและช่วงเวลา (SlotPicker)
- รองรับ: FR-BKG-01, FR-BKG-06
- ตรวจด้วย: ไม่มี AC ตรง ๆ เป็นงานพื้นฐานของ T-17
- ไฟล์ที่แตะ: frontend/src/pages/SlotPicker.jsx, frontend/src/api/client.js
- ต้องทำหลัง: ไม่มี
- เสร็จเมื่อ: เลือกแพ็กเกจแล้วรายการช่วงเวลาที่แสดงเปลี่ยนตามข้อมูลจาก API จำลอง (ใช้สัญญาตาม plan.md ข้อ 4)
- สถานะ: พร้อมทำ

### T-18 หน้ายืนยันการจอง (ConfirmBooking) และแจ้ง "ช่วงเวลาเต็ม"
- รองรับ: FR-BKG-03, FR-BKG-04
- ตรวจด้วย: AC-BKG-03
- ไฟล์ที่แตะ: frontend/src/pages/ConfirmBooking.jsx, frontend/src/__tests__/AC-BKG-03.test.jsx
- ต้องทำหลัง: T-17
- เสร็จเมื่อ: AC-BKG-03.test.jsx ผ่าน (API จำลองตอบ 409 พร้อม 3 ช่วง แล้วหน้าจอแสดง "ช่วงเวลาเต็ม" และปุ่ม 3 ตัวเลือก)
- สถานะ: พร้อมทำ

### T-19 หน้าแสดงผลการจองและหมายเลขคิว (BookingResult)
- รองรับ: FR-BKG-04, FR-BKG-05
- ตรวจด้วย: ไม่มี AC ตรง ๆ เป็นงานพื้นฐานของ T-19
- ไฟล์ที่แตะ: frontend/src/pages/BookingResult.jsx
- ต้องทำหลัง: ไม่มี
- เสร็จเมื่อ: หน้าจอแสดงหมายเลขคิวจากค่าที่ API จำลองส่งมา ได้แม้ API จำลองตอบว่าส่งข้อความแจ้งเตือนไม่สำเร็จ
- สถานะ: พร้อมทำ

### T-20 ต่อหน้าจอกับ API จริง
- รองรับ: FR-BKG-01, FR-BKG-03, FR-BKG-06
- ตรวจด้วย: ไม่มี AC ตรง ๆ เป็นงานพื้นฐานของ T-20
- ไฟล์ที่แตะ: frontend/src/api/client.js, frontend/src/pages/SlotPicker.jsx, frontend/src/pages/ConfirmBooking.jsx
- ต้องทำหลัง: T-05, T-09, T-17, T-18
- เสร็จเมื่อ: เปิด `npm run dev` แล้วหน้าเลือกช่วงเวลาและหน้ายืนยันดึงข้อมูลช่วงเวลาว่างและช่วงใกล้เคียงเมื่อเต็มจากหลังบ้านจริงแทนข้อมูลจำลองได้ถูกต้อง
- สถานะ: พร้อมทำ

## ตารางตรวจความครบ

### AC ID | task ที่ตรวจ AC นี้
| AC ID | task |
|---|---|
| AC-BKG-01 | T-16 |
| AC-BKG-02 | T-08 |
| AC-BKG-03 | T-09 (หลังบ้าน), T-18 (หน้าจอ) |
| AC-BKG-04 | T-12 |
| AC-BKG-05 | T-06 |
| AC-BKG-06 | T-13 |

### Constraint ID | task ที่ทำให้เป็นจริง
| Constraint ID | task |
|---|---|
| CON-TECH-01 | T-01, T-02, T-03 |
| DOM-PDPA-01 | T-01, T-13 |
| IF-IDP-01 | T-04 |
| IF-HIS-01 | T-01, T-14 |
| IF-NOT-01 | T-11 |

## สิ่งที่ยังไม่ทำ
- Q-02 หมายเลขคิวรีเซ็ตรายวัน หรือนับต่อเนื่อง และมีรูปแบบอย่างไร (เช่น A001)?
  -> ถามเจ้าหน้าที่เวชระเบียน (ยังไม่ได้คำตอบ) — T-15 และ T-16 รออยู่
- FR-BKG-06 ยังไม่มี AC ใน spec.md (ตามที่ plan.md ข้อ 6 ระบุไว้) จึงยังไม่มี task ทดสอบเฉพาะสำหรับ FR-BKG-06
  โดยตรง งานที่รองรับ FR-BKG-06 (T-05, T-17, T-20) ทำได้ตามหน้าที่ทั่วไป แต่ไม่มี AC ID ให้อ้างอิงตรวจผล
  ทีมควรพิจารณาเพิ่ม AC สำหรับ FR-BKG-06 หากต้องการทดสอบอย่างเป็นทางการ
