---
id: self-docs/engine/approval-flow-huy-chot-cong
canonical_question: 'Technical guide and specification: Approval Flow — "Huỷ chốt
  công" + gate sửa ô/chốt công theo tiến độ duyệt'
aliases:
- Approval Flow — "Huỷ chốt công" + gate sửa ô/chốt công theo tiến độ duyệt
- Approval Flow Huy Chot Cong 170926
entity_type: how_to
domain: self-docs > engine
last_verified: 2026-09-17
---

# Approval Flow — "Huỷ chốt công" + gate sửa ô/chốt công theo tiến độ duyệt (170926)

**Ngày:** 17/09/2026
**Nhánh:** `feature/approval-flow-buttons` (cả 2 repo, tách từ `origin/develop_v1`)
**SPEC/PLAN:** `llmwiki/wiki/sources/draft/170926-approval-flow-huy-chot-cong.md` + `...-PLAN.md`
**Trạng thái:** Code xong cả 10 task + 1 bug fix (xem mục "Đợt bổ sung" cuối file), đã **push** cả 2 repo lên GitLab (`feature/approval-flow-buttons`), user tự tạo MR.

## Đợt bổ sung 170926-b — bug user báo qua UI: bấm "Huỷ chốt công" xong dòng vẫn còn trên Bảng lương

User tự kiểm trên UI (server local do tôi start), báo: bấm "Huỷ chốt công" nhưng dòng KHÔNG biến mất khỏi Bảng lương, và hỏi thẳng "bạn đã test playwright chưa" — **chưa**, tôi chỉ kiểm qua curl (status code) ở Task 10, không click-through UI thật. Đây là lỗi thiết kế thật của tôi, không phải hiểu lầm của user.

**Nguyên nhân gốc:** `GetRows` (`payroll_record_repo.go:388-390`) — `FROM attendance_segment att INNER JOIN payroll_periods pp ON ... AND att.is_finalized = true`. Dòng trên lưới Bảng lương tồn tại vì **CHẤM CÔNG đã chốt** (`attendance_segment.is_finalized=true`), KHÔNG phải vì `payroll_record` tồn tại — `computed_values` chỉ là `COALESCE(att.computed_values, pr.computed_values, '{}')`. `WithdrawRecord` (Task 5) chỉ xoá `payroll_record`, chưa hề đụng `attendance_segment.is_finalized` → dòng vẫn hiện (rơi về `computed_values` từ attendance nếu có, hoặc rỗng) — đúng khớp cái user thấy.

**Sửa:** `WithdrawRecord` gọi thêm `AttendanceSummaryRepo.UnfinalizeByEmpCodes` (tái dùng ĐÚNG cơ chế "Gỡ công" đã có sẵn cho chấm công — không viết lại) NGAY SAU KHI transaction xoá record + huỷ approval commit thành công. Gọi ngoài transaction (hàm này không nhận `*sqlx.Tx`) — nếu lỗi ở bước này, ghi log để vận hành tự gỡ tay, không rollback việc xoá record (đã hợp lệ). Đúng khớp ý user gốc: "phải qua Bảng công để chốt công lại tạo record mới" — sau khi is_finalized=false, nhân viên đó xuất hiện lại ở Bảng công như "chưa chốt", HR chọn lại rồi bấm "Chốt công" bình thường để tạo `payroll_record` mới.

**Kiểm chứng qua UI thật (Orca browser automation — tương đương Playwright, dùng vì Playwright không có sẵn trong công cụ phiên này):** dựng fixture `pending_first_level` thật trên kỳ `Tháng 09/2026` đang hiện trên UI, đăng nhập qua dev-toolkit, mở sheet "Bảng lương 09/2026", thấy đúng nút "Huỷ chốt công" trên dòng — bấm → dòng **biến mất khỏi lưới**. Đối chiếu DB ngay sau: `payroll_records` count=0, `attendance_segment.is_finalized=false`, `approval_requests.status='cancelled'` — đúng cả 3. Dọn sạch fixture sau khi kiểm. Cập nhật `TestWithdrawRecord` (integration test DB thật) thêm assertion `is_finalized` cho cả 5 case (đúng khi được xoá, giữ nguyên khi bị chặn).

Commit `b730055` (BE), đã push.

## Việc đã làm

User yêu cầu 4 việc trên luồng phê duyệt phiếu lương:
1. Tìm hiểu luồng duyệt hiện tại (khảo sát trước khi code — xem SPEC mục Context).
2. Thêm nút "Huỷ chốt công": xoá payroll_record đang chờ duyệt lần đầu/trình duyệt lại (khác "Gỡ công" đã có, vốn là unfinalize chấm công).
3. Cho sửa ô khi chưa duyệt/trình duyệt lại, chặn sửa khi đang duyệt/đã duyệt.
4. Chốt công phải bỏ qua (không ghi đè) record đang duyệt/đã duyệt, vẫn xử lý bình thường record khác trong cùng lượt.

## Kiến trúc

Một nguồn sự thật duy nhất — `approvalprogress.Classify()` (package mới `internal/approvalprogress`, BE) — phân loại mỗi payroll_record vào 1 trong 5 trạng thái: `not_submitted` / `pending_first_level` / `in_review` / `approved` / `rejected`, dựa trên `approval_requests` mới nhất (nếu có) + `payroll_records.approved_at`/`rejected_reason` (đường đơn cấp cũ 230726, khi company/site chưa cấu hình `approval_rules`). Tách riêng package (không đặt trong `service`) để `internal/repository` cũng import được mà không tạo vòng phụ thuộc (service đã import repository).

Hàm này dùng chung ở 3 điểm gate + 1 điểm đọc:
- `writeOverrideCell` (sửa ô) — chặn khi `in_review`/`approved`.
- `upsertComputedLatestWins` (chốt công / Calculate/CalculateBatch) — bỏ hẳn khỏi batch ghi khi `in_review`/`approved`.
- `WithdrawRecord` (API mới) — chỉ cho xoá khi KHÔNG `in_review`/`approved`.
- `GetRows` (đọc bảng lương) — trả `approvalProgress` cho FE gate đúng ngay từ lúc tải trang (không chỉ dựa vào state React tạm thời sau khi bấm nút).

## Phát hiện quan trọng lúc viết PLAN (gap so với SPEC, đã tự lấp — không cần quay lại `/propose`)

`models.PayrollRow` (response `GetRows`) trước đây KHÔNG có field nào phản ánh `approval_requests.current_level` — FE chỉ suy trạng thái duyệt qua `deriveApproval(approvedAt, rejectedReason, status)` (2 giá trị: pending/approved/rejected, không phân biệt "chờ duyệt lần đầu" với "đang duyệt cấp 2"). Sau khi tải lại trang, phân biệt cấp CHỈ tồn tại tạm thời trong `state.approvalLevelOverride` (React), mất khi F5. Đã thêm cột thô `ar.status/current_level/total_levels` (LEFT JOIN LATERAL vào `approval_requests`) trực tiếp trong SQL của `GetRows`, populate `PayrollRow.ApprovalProgress` bằng `approvalprogress.Classify` — vá đúng gap này, để nút mới + gate sửa ô hoạt động đúng ngay từ lúc mở trang, không chỉ trong session vừa hành động.

## Xung đột với behavior cũ (040926) — đã sửa 2 test tiền tồn tại

`upsertComputedLatestWins` (040926, "latest-wins") trước đây ghi đè **vô điều kiện mọi trạng thái duyệt** khi chốt-công-lại không forceReset — kể cả record `approved`/`in_review`. Yêu cầu #4 của user (170926) đảo ngược tường minh quyết định đó. 2 test tích hợp cũ minh chứng hành vi cũ:
- `TestIntegration_UpsertComputedLatestWins_CancelsApprovalAndResetsTracklog` (fixture `approved`)
- `TestIntegration_UpsertComputedLatestWins_PendingApproval_StatusStillCalculated_AlsoResets` (fixture `pending` current_level=2/2, tức `in_review`)

Đã đổi tên + đảo ngược assertion (`SkipsWhenApproved`/`SkipsWhenInReview`) để khớp hành vi MỚI — đây là thay đổi CÓ CHỦ Ý theo đúng yêu cầu user, không phải bug.

## Quyết định đã chốt qua `AskUserQuestion` trong phiên

1. Tên nút mới: **"Huỷ chốt công"** (tránh trùng "Gỡ công" đã dùng cho chấm công).
2. Xoá payroll_record: **hard-delete** (không soft-delete).
3. `approval_requests` đang active khi xoá: chuyển **`cancelled`** (lý do `payroll_record_deleted`), giữ lịch sử `approval_steps`.

Cộng 1 câu hỏi kỹ thuật hạ tầng: cho phép chạy AUTO_MIGRATE lên DB dev cục bộ (thiếu 4 migration `v102-104`, bảng `attendance_segment` chưa tồn tại) — user đồng ý, đã áp thành công (4 applied, 0 baselined).

## Danh sách file đã sửa

### Backend (`Core System-backend`, nhánh `feature/approval-flow-buttons`)
- Tạo `internal/approvalprogress/approvalprogress.go` — hàm thuần `Classify`.
- Sửa `internal/repository/approval_repo.go` — `GetLatestRequestByEntity`, `FindLatestRequestsByEntities`.
- Sửa `internal/service/approval_service.go` — re-export hằng, `ResolveApprovalProgress(Batch)`.
- Sửa `internal/models/dto.go` — `PayrollRow.ApprovalProgress/CurrentLevel/TotalLevels`.
- Sửa `internal/repository/payroll_record_repo.go` — `GetRows` (LEFT JOIN LATERAL + populate), `DeleteTx`.
- Sửa `internal/service/payroll_service.go` — `ResolveApprovalProgressForRecord`, gate `writeOverrideCell`, sửa `upsertComputedLatestWins` (skip + trả `[]uuid.UUID` skipped), đổi chữ ký `Calculate` (thêm `skippedApproval`), `WithdrawRecord` + `ErrCannotWithdrawRecord`.
- Sửa `internal/handler/payroll_handler.go` — response `Calculate` thêm `skippedApprovalEmployees`, handler `Withdraw`.
- Sửa `internal/app/router.go` — route `POST /Core System/withdraw/{id}`.
- Sửa thêm do đổi chữ ký `Calculate` (compiler tự bắt, đúng như PLAN dự đoán): `internal/service/payroll_period_scheduler.go`, `internal/service/sync_service.go`, `cmd/e2e-simulation/main.go`, `cmd/Core System-recalc/main.go`.
- Test mới: `approval_progress_test.go` (unit, 8 case), `payroll_record_repo_getrows_progress_test.go` (integration), `payroll_write_override_progress_integration_test.go` (integration, 4 case), `payroll_calculate_skip_approved_integration_test.go` (integration), `payroll_withdraw_integration_test.go` (integration, 5 case).
- Test sửa (đảo hành vi, xem mục "Xung đột" trên): `payroll_refinalize_latest_wins_integration_test.go` (2 test đổi tên + assertion).

### Frontend (`Core System-frontend`, nhánh `feature/approval-flow-buttons`)
- Sửa `lib/api/types.ts` — `PayrollRow.approvalProgress/CurrentLevel/TotalLevels`.
- Sửa `lib/api/approvals.ts` — `withdrawPayrollRecord`.
- Sửa `lib/api/Core System.ts` — `calculatePayroll` trả thêm `skippedApprovalEmployees`.
- Sửa `components-page/tinh-luong/data.ts` — `ApprovalProgress` type, `Emp.approvalProgress`, `mapRow` (export + đọc field mới).
- Sửa `components-page/tinh-luong/i18n.ts` — nhãn `withdrawFinalization`.
- Sửa `components-page/tinh-luong/TinhLuongExcel.tsx` — `Cell.showWithdraw/onWithdraw`, hàm `withdrawFinalization`, cột "approval" thêm điều kiện hiện nút, JSX render nút, `isRowEditableByApproval`, đổi chữ ký `cellEditable(c)` → `cellEditable(r,c)` (10 call site), toast skip-count sau chốt công.
- Test mới: `components-page/tinh-luong/__tests__/mapRow.approvalProgress.test.ts`.

## Bằng chứng test

- **BE unit + integration** (DB dev thật `payroll_engine`, không mock): package `internal/service` — 343 pass / 7 fail. Cả 7 fail đối chiếu là **tiền tồn tại, không liên quan** (`TestTransportFuelTax_Boundary`, 4 test `TestTemplateEnforce_*`, `TestComputeTemplateImpact_ReadOnlyDiff`, `TestReplayCapsAndPITTrenDuLieuThat` — data-drift/infra, đã xác nhận fail giống hệt khi chạy trước lúc có bất kỳ thay đổi nào của PLAN này qua `git stash` ở 2 checkpoint giữa đường). 1 panic tiền tồn tại (`TestIntegrationFormulaApprovalAndRecalcE2E`, nil pointer dòng 263) làm gián đoạn lượt `go test` gộp cả package — xác nhận pre-existing bằng `git stash` trước khi có Task 3.
- **BE build/vet:** `go build ./...` + `go vet ./...` sạch toàn repo (0 lỗi) sau mỗi task.
- **BE kiểm chứng qua HTTP thật** (server thật, port 8099, DB dev thật, dọn sạch sau khi kiểm):
  - `POST /Core System/withdraw/{id}` record `not_submitted` → `200 {"message":"record withdrawn"}`, record biến mất khỏi DB.
  - `POST /Core System/withdraw/{id}` record `approved` → `409 {"error":"...không thể huỷ chốt công"}`.
  - `POST /Core System/cell-set/{periodId}` cho record `approved` → `400 {"error":"...đang duyệt hoặc đã duyệt — không thể sửa"}`.
  - `POST /Core System/calculate/{periodId}` với 1 NV `in_review` → `200`, `skippedApprovalEmployees` chứa đúng mã NV đó.
- **FE:** `tsc --noEmit` sạch, `eslint` sạch trên toàn bộ file đã sửa, `vitest run` 358/358 pass (0 hồi quy, +2 test mới).
- **Chưa làm:** click-through Playwright/dev-server đầy đủ trên UI thật (nút hiện/ẩn, double-click edit) — user sẽ tự kiểm tại local như đã nói trước.

## Trạng thái git

- Backend: 6 commit trên `feature/approval-flow-buttons` (`86e160e`, `7fc30e2`, `d0babf8`, `b77205e`, `8de2f4c`, `b730055`).
- Frontend: 4 commit trên `feature/approval-flow-buttons` (`374a8e5`, `8feda20`, `072166c`, `bdc7938`).
- **Đã push** cả 2 repo lên GitLab — user tự tạo MR (link ở đầu file/báo cáo trong hội thoại).

## Ghi chú vận hành

- DB dev cục bộ (`payroll_engine`) đã được AUTO_MIGRATE nâng lên `v104` trong phiên này (từ `v99`) — cần thiết cho `GetRows`/test dùng bảng `attendance_segment`. Migration có sẵn trên `develop_v1`, không phải migration mới viết trong PLAN này.
- Route mới `/Core System/withdraw/{id}` dùng đúng middleware chain của `/approve|reject/{id}` (`requirePayrollCalculate, requireRecordCompanyScope, requireApprove`) — không viết middleware riêng.
