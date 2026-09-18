---
id: self-docs/files/adapt-checklist-attendance-segments
canonical_question: 'Technical guide and specification: Adapt-checklist — attendance_department_segments'
aliases:
- Adapt-checklist — attendance_department_segments
- ADAPT CHECKLIST attendance segments 210826
entity_type: how_to
domain: self-docs > files
last_verified: 2026-09-17
---

# Adapt-checklist — attendance_department_segments (khi đội adapter có dữ liệu thật)

**Nguồn:** Task 5/5 của `llmwiki/wiki/sources/draft/210826-Core System-be-attendance-segments-PLAN.md`.
**Trạng thái code liên quan:** Task 1-4 đã thi hành trên nhánh `local/attendance-segments-210826-v2`
(dựa `release/uat-180826`), build/test xanh, **chưa push, chưa merge, chưa chạy migration trên
DB dev/UAT thật**.

1. **Xác nhận với HR** nhánh "≥14 ngày" trong `ComputeSegmentAggregates`
 (`internal/service/attendance_segment_aggregator.go`) trả full allowance (không giảm) — hiện là
 ASSUMPTION `verified:false`. Nếu HR nói khác, sửa hàm `prorate()` + cập nhật lại 2 test case
 `AboveThreshold` cho khớp, KHÔNG chỉ sửa code mà không sửa test.
2. **Xác nhận đơn vị** `Calculated_Quantity` (Cash_1x/2x/3x) là giờ hay ngày — nếu là GIỜ, sửa
 `ComputeSegmentAggregates` chia thêm cho số giờ chuẩn/ngày (8) trước khi nhân hệ số OT, giống
 cách `AR9`/`AS9` của file Excel Workday làm (`div 8`).
3. **Xác nhận nguồn ca đêm OT** (`OT_PAY_WD_NIGHT`/`WE_NIGHT`/`HLD_NIGHT`) — nếu đội adapter tìm được
 tag/report (xem `self-docs/Adapter-Workday-Salary-Rules-Data-Request-210826.md` mục 1b), thêm
 field `OTWeekdayNightUnits` v.v. (đã có sẵn trong model, đang luôn nhận 0) — không cần sửa
 schema, chỉ cần adapter bắt đầu ghi số khác 0 vào các cột đã có.
4. **Chạy conformance test bằng dữ liệu thật**: dùng đúng số đã đo được ở `raas_monthly_attendance`
 (DB `payroll_adapter`, ví dụ nhân viên `002987` kỳ `2026-06-21` có `cash_1x=1.0`) — viết 1 test
 mới `TestComputeSegmentAggregates_RealWorkdaySample` với input y hệt số thật này, so khớp kết
 quả tay tính trước (không suy ra từ code) — CHỈ SAU KHI test này pass mới được coi dữ liệu đáng
 tin.
5. **Kích hoạt thật** (bước cuối, chỉ làm sau 1–4 đều xong):
  - Sửa `PayrollService.Calculate` (`internal/service/payroll_service.go:185`) gọi
   `AttendanceSegmentRepo.ListByEmpAndMonth` → `ComputeSegmentAggregates` →
   `AttendanceSegmentRepo.UpsertAggregate` cho mỗi nhân viên trước khi tính lương.
  - Đổi các điểm gọi `resolveSourceField` (dòng ~525-531, khu vực build `vals` cho từng nhân
  viên) sang `resolveSourceFieldV2`, truyền thêm `agg` đọc qua `GetAggregate`.
  - Sửa `GROSS`/`MEAL_ALLOW`/`PHONE_TAX`/`PHONE_NONTAX`/`TRANSPORT_TAX`/`FUEL_ALLOW`/`OT_TAX`/
  `OT_NONTAX` để tham chiếu tới các component mới (`MEAL_ALLOW_SEG`, `PHONE_TAX_SEG`,
  `OT_PAY_WD_NORMAL`... ) — bước này ĐI QUA `SalaryComponentService.Update` + `InsertVersion`
  như thường, có `reason` trỏ rõ "kích hoạt attendance-segment engine, xem
  self-docs/Core System-Formula-Excel-Reconciliation-190826.md 210826", có xác nhận
  `AskUserQuestion` trước khi chạy trên DB dev/UAT thật (đã có 207 version + 6 kỳ lương thật —
  không phải DB trống, không được bypass versioning).

