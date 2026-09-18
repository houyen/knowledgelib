---
id: self-docs/engine/attendance-payroll-approval-gate
canonical_question: 'Technical guide and specification: Attendance-Core System Approval
  Gate — 240826'
aliases:
- Attendance-Core System Approval Gate — 240826
- Attendance Core System Approval Gate 240826
entity_type: how_to
domain: self-docs > engine
last_verified: 2026-08-26
---

# Attendance-Core System Approval Gate — 240826

**Canonical duy nhất** cho hạng mục: nút "Duyệt tất cả" bảng lương + gate tính lương theo chốt công + chu kỳ lương 21-20 (khoá nút + schedule tự động). Bắt đầu từ yêu cầu "kiểm tra luồng duyệt bảng công để tạo bảng lương" ngày 240826, mở rộng qua 4 lượt trao đổi thành 1 SPEC + PLAN, đã thi hành xong 8/9 task (Task 9 = chính tài liệu này + test tổng hợp).

## Tài liệu nguồn

- SPEC: `llmwiki/wiki/sources/draft/240826-attendance-Core System-approval-gate.md`
- PLAN: `llmwiki/wiki/sources/draft/240826-attendance-Core System-approval-gate-PLAN.md`
- Sequence diagram: `llmwiki/html/240826-attendance-Core System-approval-gate-seq.html`

## Quyết định nhánh

`feature/Core System-period-schedule-gate` (từ `origin/develop`, cả 2 repo) — KHÔNG dùng `sec_dev` vì đây là business logic (chu kỳ lương/scheduler), không phải RBAC/company-scoping/role definition theo đúng carve-out của `CLAUDE.md`. Chưa push, chưa merge.

## 3 phát hiện "mồ côi / dead code" quan trọng (để tránh ai đó khảo sát lại từ đầu)

1. **Bảng công đã có sẵn wizard scope Tất cả/Trang/Đã chọn** từ trước — `AttendanceDailyPage.tsx` (AG Grid) + `AttendanceDailyFinalizeModal.tsx` + `useAttendanceDailyFinalized.tsx` → `POST /hris/attendance-summary/finalize-from-daily`. Không có việc gì cần làm ở phía này.
2. **`payroll_period_config`** (`period_start_day=21`/`period_end_day=20`) tồn tại trong DB từ lâu, có đủ repo/service/handler/route (`GET/PUT /config/period-config`) nhưng **chưa từng được đọc** để tạo kỳ lương thật — `PayrollPeriodService.Create` nhận thẳng ngày từ FE. Nối dây ở Task 1/2 của đợt này.
3. **Nhánh `scope="all"` của bảng lương đã viết sẵn** trong `confirmModal()` (`TinhLuongExcel.tsx:~4975`) và kiểu `onOpenModal(action, scope: "selected"|"all")` đã hỗ trợ `"all"` từ trước — nhưng KHÔNG nút nào từng gọi tới nhánh đó (dead branch). Việc thật cần làm chỉ là thêm 1 nút, không phải route BE bulk mới (đã cân nhắc và loại bỏ phương án route bulk qua `AskUserQuestion`).

Ngoài ra: FE **không có bất kỳ UI nào** cho `payroll_period_config` trước đợt này (chỉ có route BE, 0 tham chiếu FE) — Task 5 phải tạo trang mới hoàn toàn (`/v1/settings/Core System-period`), không phải "mở rộng" như giả định ban đầu trong SPEC.

## Các quyết định nghiệp vụ đã chốt (qua `AskUserQuestion`, không tự đoán)

- NV chưa chốt công khi bật gate: **chỉ cảnh báo, không chặn** — loại khỏi kết quả tính lương, không chặn duyệt các NV khác.
- Gate lọc `is_finalized` áp dụng **từ kỳ lương tháng 09/2026 trở đi** — kỳ ≤08/2026 giữ hành vi cũ kể cả khi `Calculate` gọi lại sau deploy.
- Quyền chốt công: chỉ `hr_admin` — xác nhận đã đúng sẵn trong code (`RequireRole("hr_admin")`), không cần permission mới.
- Schedule tự tạo `payroll_period` mới nếu chưa có (không giả định luôn được tạo tay trước).
- Khoảng khoá tự dịch theo `period_start_day` cấu hình (không hardcode 21/24); số ngày khoá (`lock_days`) cấu hình được, mặc định 4.
- Schedule dùng chung 1 cấu hình toàn hệ thống (không theo công ty) — khớp thực tế `payroll_periods` không có `company_id`.
- Lỗi từng phần khi schedule chạy: tiếp tục phần được, log/cảnh báo, không dừng toàn bộ.
- Múi giờ "địa phương" = Asia/Ho_Chi_Minh (UTC+7) cố định.
- Nút "Duyệt tất cả" bảng lương: dùng nhánh `scope="all"` có sẵn (N lời gọi API song song từ FE), KHÔNG làm route bulk BE riêng.

## Việc đã làm (8 task, Backend + Frontend)

**Backend (`Core System-backend`):**
1. Migration `migrations/v58_payroll_period_config_schedule.sql` — thêm `schedule_hour`/`schedule_minute`/`lock_days`/`last_auto_run_period_id` vào `payroll_period_config`.
2. `ComputeNextPeriodRange`/`IsWithinLockWindow` (`payroll_period_service.go`) — hàm dùng chung; `Create` cảnh báo (không chặn) khi ngày lệch cấu hình.
3. `PayrollPeriodScheduler` (`payroll_period_scheduler.go`, file mới) — ticker 1 phút, giờ Asia/Ho_Chi_Minh, tự tạo kỳ + chốt công (`AttendanceDailyService.FinalizeEmployeesFromDaily`, hàm mới trích từ `FinalizeFromDaily` cũ để dùng chung) + tính lương. Luôn bật từ `cmd/Core System/main.go`.
4. Khoá 4 route (`Approve`, `Calculate`, `Finalize`, `FinalizeFromDaily`) — trả `423 Locked` qua `checkLock()` ở mỗi handler.
5. (FE) — xem dưới.
6. (FE) — xem dưới.
7. `PayrollService.Calculate` đổi chữ ký thêm `excludedEmpCodes []string` trả về, lọc `is_finalized` từ kỳ 09/2026 (`applyFinalizeGate`). Cập nhật 6 call site (handler, `cmd/Core System-recalc`, scheduler, 4 test tích hợp cũ).

**Frontend (`Core System-frontend`):**
4. `usePayrollLockStatus()` hook mới + disable nút Duyệt/Từ chối/3 nút wizard khi khoá.
5. Trang mới `/v1/settings/Core System-period` (đăng ký tab "Chu Kỳ & Lịch Tự Động" trong `/v1/admin`).
6. Nút "Duyệt tất cả" mới trong `HomeRibbon.tsx` (chỉ tab Bảng lương) — gọi `onOpenModal("approve","all")`.
8. Banner cảnh báo NV bị loại — 3 điểm gọi `calculatePayroll` thật (chốt công tab Chấm công, nút Tính lương chính + auto-calc trong `PayrollPage.tsx`).

## Bằng chứng test

- **Go:** `go build ./...` sạch, `go vet ./...` sạch, `go test ./internal/...`: **795 passed, 0 failed** (baseline trước đợt này: 794/0 — +1 test mới, 0 hồi quy).
- **Frontend:** `npx tsc --noEmit` — 0 lỗi mới (3 lỗi tiền tồn tại trong `public/backup/payslip-lib.test.ts`, không liên quan). `npm run test` (vitest): **106/106 passed**.
- **Xác minh thật trên DB dev** (`payroll_engine`, server chạy local `go run ./cmd/Core System`, dừng ngay sau khi kiểm, không để chạy nền):
  - Migration `v58` áp dụng sạch trên DB dev thật (log `[migrate] applying v58_payroll_period_config_schedule.sql ... xong: 1 applied`).
  - `GET /config/period-config` trả đúng field mới với giá trị mặc định (`scheduleHour:0, scheduleMinute:0, lockDays:4`).
  - `PUT /config/period-config` ghi + validate đúng.
  - Đặt `periodStartDay=24, lockDays=2` (ép hôm nay 24/08/2026 vào khoảng khoá) → `POST /Core System/calculate/{periodId}`, `POST /hris/attendance-summary/finalize-from-daily`, `POST /Core System/approve/{id}` đều trả đúng **`423`** kèm `unlockDate` chính xác (2026-08-26).
  - Đặt lại `periodStartDay=1, lockDays=2` (hôm nay ngoài khoảng khoá) → `Calculate` trả `200` bình thường, `excludedEmployees:null` đúng cho kỳ 06/2026 (< ngưỡng 09/2026, không lọc).
  - **Phát hiện phụ đáng chú ý:** cấu hình MẶC ĐỊNH (`period_start_day=21, lock_days=4`) khiến hôm nay (24/08/2026) đang nằm TRONG khoảng khoá thật (21→24) — xác nhận gate hoạt động đúng với dữ liệu lịch thật, không phải chỉ đúng trên input giả lập.
  - Scheduler khởi động không lỗi (`Core System-period-scheduler: đã bật`), không tự trigger sai giờ trong ~2 phút theo dõi log.
  - Đã đặt lại config về mặc định (`21/20/0/0/4`) trước khi tắt server — không để lại trạng thái test trên DB dev.
- **Đã kiểm bằng Playwright thật** (lượt sau, user yêu cầu "kiểm tra bằng playwright") — khởi động `go run ./cmd/Core System` (:8080) + `npm run dev` (:3000) thật, script tạm dùng `@playwright/test` (đã xoá sau khi kiểm), dev-login qua `Authorization: Bearer dev`:
  - Trang `/v1/settings/Core System-period` load đúng 5 field, giá trị khớp DB.
  - Sheet Bảng công: nút "Duyệt tất cả" KHÔNG hiện (đúng `!isCham`).
  - Sheet Bảng lương: nút "Duyệt tất cả" hiện đúng vị trí, đang khoá (opacity 0.4, tooltip đúng ngày mở khoá) vì hôm nay 24/08 nằm trong khoảng khoá mặc định 21→24.
  - Đổi cấu hình cho khoảng khoá lệch khỏi hôm nay → nút mở, bấm "Duyệt tất cả" → modal "Phê duyệt cả bảng" hiện đúng → bấm "Duyệt" → gửi đúng **3 request** `POST /Core System/approve/{id}` (khớp 3 dòng "Chờ duyệt" thật) → UI cập nhật "Đã duyệt" cả 3 dòng, footer "Đã duyệt tất cả". Dùng đúng kỳ Tháng 06/2026 (period seed dành riêng cho QA theo ghi chú cũ) — đã revert 3 dòng về `pending` bằng SQL ngay sau khi kiểm.
  - **2 bug thật tự phát hiện qua Playwright, đã sửa ngay:** (1) FE `usePayrollLockStatus` dùng `toISOString()` làm lùi 1 ngày `unlockDate` trên múi giờ lệch UTC; (2) BE `IsWithinLockWindow` dùng `.UTC()` thay vì Asia/Ho_Chi_Minh như TASK-REF — cùng gốc lỗi, sửa cả 2 phía, xác nhận lại đúng (`2026-08-25`) sau fix bằng cả Playwright lẫn `curl` trực tiếp.
  - Đã trả DB dev về nguyên trạng (cấu hình `21/20/0/0/4`, 3 record về `pending`), dừng cả 2 server, xoá script Playwright tạm.

## Trạng thái git

Chưa push, chưa merge. 8 commit trên `feature/Core System-period-schedule-gate` ở mỗi repo (backend: Task 1→8 gồm cả docs; frontend: Task 4/5/6/8 gồm cả docs).

## Rủi ro/giới hạn đã biết, cố ý không sửa trong đợt này

- `period.Month/Year` suy từ `end_date` dùng làm khoá tra `attendance_summary` theo tháng lịch thường — việc `attendance_summary` có tổng hợp đúng dải ngày 21→20 hay không nằm ở tầng khác, ngoài phạm vi.
- 3 cơ chế chọn-dòng khác nhau (AG Grid checkbox / vùng-ô-Excel tab Chấm công / gutter Shift-Ctrl-click tab Bảng lương) vẫn tồn tại song song, không hợp nhất.
- Không có leader-election cho scheduler nếu deploy nhiều instance backend song song — chấp nhận rủi ro lý thuyết, giảm thiểu bằng marker `last_auto_run_period_id`.
- Chưa kiểm UI thật bằng browser (xem mục Bằng chứng test).
