---
id: self-docs/engine/payroll-bulk-set-calculate-batch-perf
canonical_question: 'Technical guide and specification: Core System Bulk-Set CalculateBatch
  Perf — 030926'
aliases:
- Core System Bulk-Set CalculateBatch Perf — 030926
- Core System Bulk Set Calculate Batch Perf 030926
entity_type: how_to
domain: self-docs > engine
last_verified: 2026-09-17
---

# Core System Bulk-Set CalculateBatch Perf — 030926

**Canonical duy nhất cho hạng mục này.**

## Bối cảnh

Phát hiện khi test thật tính năng "Nhập Excel" mới (xem `self-docs/Core System-Import-Template-Toolbar-Export-030926.md`, cùng ngày): import file ~2872 dòng NV qua `POST /Core System/cells/bulk-set/{periodId}` mất hơn 1 phút để ghi xong. Không treo vĩnh viễn (server có `WriteTimeout`/`IdleTimeout` 10 phút), nhưng chậm bất thường.

## Nguyên nhân gốc

`BulkSetCells` (`payroll_bulk_cell_set.go`) đúng như thiết kế — chỉ tính lại lương **1 lần/NV** (không phải 1 lần/ô) — nhưng gọi `CalculateOne` (`payroll_service.go:807-910`), hàm vốn viết cho luồng sửa **1 ô lẻ** (`SetCell`). Mỗi lần gọi, `CalculateOne` **load lại từ đầu** các bảng KHÔNG lọc theo NV: `componentRepo.ListActiveAsOf`, `attSummaryRepo.GetSummaryMapByMonth` (toàn bộ chấm công cả tháng, mọi công ty — nặng nhất), `insuranceRepo.GetAllActive`, `overrideRepo.ListActiveForDate`, `templateRepo.ListAllTemplateComponentCodesAsOf`. Gọi N lần (N = số NV trong lượt import) = quét lại các bảng cỡ N đó N lần — **O(n²)** đúng nghĩa. Ước tính ~25.000-35.000 câu SQL cho 1 lượt 2872 NV.

`Calculate()` (tính cả kỳ) đã giải đúng bài toán này từ trước bằng cách load mọi dữ liệu dùng chung vào 1 struct `calcShared` đúng 1 lần rồi lặp thuần trong bộ nhớ — nhưng `BulkSetCells` chưa từng tái dùng pattern này.

## Quyết định

User xác nhận qua `AskUserQuestion` (2026-09-03): sửa ngay trong phiên này. `/propose` trình 3 phương án (SPEC `030926-Core System-bulk-set-calculate-batch-perf.md`), chọn **Phương án A** — thêm hàm mới `CalculateBatch` tái dùng `calcShared`/`computeEmployee`, **không sửa 1 dòng nào** trong `CalculateOne`/`Calculate`/`computeEmployee`/`computeEmployeeMultiLocation` — an toàn hơn cả mức rủi ro user đã chấp nhận ban đầu (0 thay đổi cho luồng `SetCell`).

## Thi hành

`/plan` → PLAN `030926-Core System-bulk-set-calculate-batch-perf-PLAN.md`, 1 task, nhánh `Core System-backend@fix/bulk-set-calculate-batch-perf` (từ `develop_v1`).

- **`CalculateBatch`** (mới, `payroll_service.go`, chèn sau `CalculateOne`): nạp `components`/`engine`/`attMap` (qua `GetSummaryMapByMonth`, giữ nguyên nguồn single-row của `CalculateOne` — KHÔNG chuyển sang multi-location của `Calculate`)/`insMap`/`resolver`/`levelAsOf`/`deptAsOf`/`depCntByID`/mask-template/`pitBrackets`/`otRates`/`manualMap` đúng 1 lần cho cả danh sách `empCodes`, dựng 1 `calcShared`, lặp gọi `computeEmployee` thuần (không round-trip DB thêm), gom `UpsertBatchComputed` 1 lần cuối. Trả `(succeeded []string, failed map[string]error, err error)` — `failed` cho lỗi riêng từng NV (thiếu chấm công, bản ghi đã finalized...), `err` cho lỗi thiết lập cấp lượt (period không tồn tại).
- **`BulkSetCells`** (`payroll_bulk_cell_set.go`): thay vòng lặp gọi `CalculateOne` bằng 1 lần gọi `CalculateBatch` cho toàn bộ NV có ≥1 ô ghi thành công. Thêm helper `markEmpFailed` dùng chung cho 2 điểm đánh dấu lỗi theo NV (lỗi `resolveBulkBasicSalary` và lỗi từ `CalculateBatch`).
- Test mới `payroll_calculate_batch_integration_test.go` (DB thật qua `dbtest`):
  - `TestIntegrationCalculateBatch_MultipleEmployeesIndependentValues` — 15 NV cùng lượt, mỗi NV giá trị `BASIC_SAL` RIÊNG biệt, xác nhận không lẫn dữ liệu giữa các NV.
  - `TestIntegrationCalculateBatch_MissingAttendanceFailsAloneOthersSucceed` — 1 NV thiếu `attendance_summary` (kịch bản thật `writeOverrideCell` KHÔNG kiểm chấm công nên override vẫn ghi được, lỗi chỉ lộ ở bước tính lại — đúng hành vi cũ của `CalculateOne`, nay qua `CalculateBatch`) chỉ làm đúng NV đó lỗi, NV còn lại vẫn tính đúng.

## Kết quả kiểm

- **Test mới:** 2/2 pass (chạy trước khi đổi code để xác nhận baseline hành vi ngoài của `BulkSetCells` không đổi — cả 2 pass cả trước lẫn sau khi thêm `CalculateBatch`, đúng TASK-REF "kết quả giống hệt").
- **2 test tích hợp cũ của `BulkSetCells`** (`TestIntegrationBulkSetCells_*`): pass, không sửa, không hồi quy.
- **`go build`/`go vet`**: sạch.
- **`go test ./internal/...` toàn bộ suite**: **1110 pass / 7 fail / 3 skip cả TRƯỚC (qua `git stash`) lẫn SAU** — danh sách 7 fail giống hệt (tiền tồn tại, không liên quan: `repository` 2, `handler` 2, `service` 3 — đã đối chiếu tên test khớp tuyệt đối) → **0 hồi quy**.
- **Hiệu năng thật trên dev server** (khởi động lại `go run ./cmd/Core System` trên nhánh này, dùng lại chính 2872 cặp `emp_code`/`BASIC_SAL` đã ghi vào `payroll_cell_edits` từ lần test thật trước đó qua UI, gọi thẳng `POST /Core System/cells/bulk-set/{periodId}` bằng `curl` với dev-auth bypass `Authorization: Bearer dev`):
  - **Trước:** ước tính hơn 1 phút (đo gián tiếp qua timestamp `payroll_cell_edits` lúc test UI thật lúc 12:56-12:57).
  - **Sau: 4.588 giây** cho đúng 2872 NV/2872 ô — `{employeesAffected: 2872, cellsWritten: 2872, cellsFailed: 0}`, đối chiếu 3 giá trị `BASIC_SAL` thật trong DB khớp tuyệt đối input (004335=120000, 005047=0, 007313=0).
  - **TASK-REF (SetCell không đổi):** gọi `POST /Core System/cell-set/{periodId}` sửa 1 ô lẻ (NV 004335, BASIC_SAL 120000→130000) — 0.137 giây, `computed_values` cập nhật đúng toàn bộ ~180 trường (GROSS/NET_PAY/PIT/bảo hiểm... tính lại đúng theo giá trị mới). Đã khôi phục lại 120000 sau khi kiểm xong.

## Trạng thái git

Nhánh `Core System-backend@fix/bulk-set-calculate-batch-perf` (từ `develop_v1`), 1 commit (`a926e3a`). **Chưa push, chưa merge.**

## Dữ liệu dev đã dọn

Payload kiểm hiệu năng dùng lại đúng dữ liệu đã có sẵn từ lần test UI thật trước đó (không tạo NV/kỳ giả mới) — bulk-set 2872 dòng là replay y hệt giá trị cũ (không đổi trạng thái DB). Riêng bước kiểm `SetCell` đã tạm đổi `BASIC_SAL` của NV `004335` sang 130000 rồi **khôi phục lại 120000** ngay sau đó — xác nhận bằng truy vấn lại DB, khớp đúng giá trị gốc.
