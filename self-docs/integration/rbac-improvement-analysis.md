---
id: self-docs/integration/rbac-improvement-analysis
canonical_question: 'Technical guide and specification: RBAC/Security Improvement
  Analysis — 04/09/2026'
aliases:
- RBAC/Security Improvement Analysis — 04/09/2026
- RBAC Improvement Analysis 040926
entity_type: how_to
domain: self-docs > integration
last_verified: 2026-01-21
---

# RBAC/Security Improvement Analysis — 04/09/2026

## Rà soát 29 module RBAC trước khi tái cấu trúc UI phân quyền (tối 040926)

User hỏi lần lượt vị trí cấu hình thật của các module trong ma trận "Ma trận theo User"/"Ma trận
theo Role" (ban đầu 13 module `Settings.*`, sau đó mở rộng sang đủ **29 module** — toàn bộ
`lib/rbac-constants.ts`, gồm 16 module "Main nav" như Core System/Employees/Dashboard/ESS...), rồi
yêu cầu xuất báo cáo tổng hợp để làm đầu vào cho việc tái cấu trúc UI phân quyền. Xem file riêng
(artefact, không lặp lại nội dung ở đây): **`self-docs/RBAC-Settings-Modules-UI-Audit-040926.md`**
(Phần 1 = 13 module Settings.*, Phần 2 = 16 module còn lại).

Tóm tắt phát hiện quan trọng nhất (cả 29 module): **5/29 module là "quyền ma"** (permission string
tồn tại trong ma trận nhưng KHÔNG route nào ở backend đọc nó) — `Settings.Audit`, `Dashboard`,
`Timesheets`, `HrisApi`, `HrisPayrollReport`; riêng `Timesheets` đặc biệt dễ nhầm vì có 1 permission
tên gần giống thật sự tồn tại (`TimesheetAdapter`, gate 1 route khác hoàn toàn). Nghiêm trọng hơn cả:
**portal tự phục vụ nhân viên (ESS) đang hỏng hoàn toàn** — 2 module `EssProfile`/`EssPayslip` có
UI viết đầy đủ, chất lượng tốt, nhưng gọi tới 4 route `/api/v1/ess/*` **không tồn tại ở backend**
(grep `"/ess"` ra 0 kết quả); 2 role `employee`/`search_profile` có `/v1/ess/profile` là trang DUY
NHẤT họ được phép vào. Cũng phát hiện thêm `Companies` là trang mồ côi CRUD đầy đủ (giống mẫu
Overtime/TransportAllowances ở Phần 1) và Audit Logs có 2 trang FE trùng lặp lệch cách phân trang.

## Core System refinalize latest-wins + reset tracklog + vá bug tooltip (chiều tối 040926)

**Yêu cầu:** Khi HR chốt công lại (re-finalize) một kỳ đã có bảng lương (có thể đã duyệt/đang chờ
duyệt), hệ thống phải luôn ghi đè bảng lương bằng kết quả tính mới nhất — bỏ qua trạng thái duyệt
cũ — và xoá sạch tracklog thay đổi của lần tính trước. Đồng thời vá bug tooltip "before → after"
phát hiện ở lượt review code trước đó trong ngày (ảnh chụp màn hình do user gửi, cột "Thử việc
85%" hiện `17.000.000,00 → 17.000.000,00` giả tạo cho ô cascade).

**Quy trình:** `/propose` → SPEC (`llmwiki/wiki/sources/draft/040926-Core System-refinalize-latest-wins.md`)
→ `/plan` → PLAN (`...-PLAN.md`) → thi hành trực tiếp (`/orca-workflow`, toàn bộ 6 task gán cho
Claude, không dispatch CLI ngoài — theo đúng lựa chọn trong SPEC vì công việc chạm approval/tiền
lương, rủi ro cao). Vẫn làm trực tiếp trên `develop_v1`.

### 3 quyết định chốt qua AskUserQuestion (trong lúc research trước khi viết SPEC)
1. Approval cũ (pending/approved) bị ghi đè → **huỷ** (`status='cancelled'`), giữ `approval_steps`
   làm lịch sử — không xoá.
2. Reset tracklog = xoá **payroll_cell_edits**, **salary_component_overrides** (nguồn `cell_pin`),
   **audit_logs** (payroll_record), **payroll_record_versions**.
3. Quyền trigger "chốt công lại" — giữ nguyên role hiện tại, không siết thêm.

### 3 phát hiện "cổng ngược" khi viết PLAN (SPEC không xây được đúng như viết ban đầu)
1. **Gate chặn không chỉ nằm ở `payroll_record_repo.go`.** `CalculateOne` và `CalculateBatch` có
   early-check RIÊNG (`if rec.Status == "finalized" { return error }`) độc lập với gate SQL
   `WHERE status != 'finalized'` của repo — phải sửa cả 3 điểm, không chỉ 1.
2. **`UpsertComputed`/`UpsertBatchComputed` không nhận `*sqlx.Tx`** — chỉ dùng `r.db.ExecContext`
   trực tiếp. Thêm hàm mới `UpsertBatchComputedTx` (tx-bound, bỏ hẳn `WHERE`) thay vì sửa chữ ký
   hàm cũ.
3. **`audit_logs` không lọc an toàn theo (period, employee) cho hành động cell-edit** —
   `resource_id` của nhóm `action IN ('cell-set','cell-clear','cell-undo')` là **component_id**
   (dùng chung mọi nhân viên/mọi kỳ có sửa cột đó), KHÔNG phải record/employee/period cụ thể. Xoá
   theo đó sẽ xoá nhầm audit trail của người/kỳ khác. **Đã thu hẹp phạm vi TASK-REF** chỉ còn
   `resource='payroll_record'` (action approve/reject, `resource_id`=record.id — an toàn, chính
   xác 1-1). `payroll_cell_edits` (đã có period_id+emp_code chính xác) đủ thoả tinh thần yêu cầu
   gốc "reset tracklog sửa ô lương".

### Thi hành
- **Task 1** (FE, `TinhLuongExcel.tsx`): `CellChangeExplain.beforeFmt/afterFmt` chuyển optional;
  nhánh `relatedFrom` (ô cascade, không sửa trực tiếp) của `explainCellChange` không còn set 2
  field đó (trước đây set cả 2 = `emp[key]` hiện tại → luôn `X → X` giả); `ExplainTooltip` chỉ
  render dòng before→after khi cả 2 field có giá trị thật.
- **Task 2** (migration): `v94_approval_requests_cancelled.sql` — thêm `cancelled_at`/
  `cancelled_reason` vào `approval_requests` (status='cancelled' đã hợp lệ sẵn, không đổi CHECK).
- **Task 3** (repo, tx-bound): `FindFinalizedAmong`, `UpsertBatchComputedTx` (payroll_record_repo);
  `CancelActiveForEntitiesTx` (approval_repo); `DeleteForPeriodEmployeeTx` (cell_edit_repo);
  `DeleteCellPinForPeriodEmployeeTx` (salary_component_override_repo); `ListIDsByRecordTx`/
  `DeleteByRecordTx` (payroll_record_version_repo); `DeleteByResourceTx` (audit_log_repo).
- **Task 4** (service): `PayrollService.upsertComputedLatestWins` — phát hiện record finalized
  trong lô sắp ghi, nếu có thì mở 1 transaction: huỷ approval (record + mọi version) → xoá 3 nhóm
  tracklog → ghi `computed_values` mới (`UpsertBatchComputedTx`, vô điều kiện) — commit atomic;
  nếu không có record nào finalized, chạy đường cũ (`UpsertBatchComputed`, không transaction hoá
  thêm). Thay thế lời gọi trực tiếp `UpsertBatchComputed` ở cả 3 hàm `Calculate`/`CalculateOne`/
  `CalculateBatch`; xoá 2 early-check chặn finalized ở `CalculateOne`/`CalculateBatch`.
  `PayrollService` thêm 2 field mới (`approvalRepo`/`recordVersionRepo`), injected qua setter
  SAU khi `NewServices` dựng xong (đúng pattern một chiều đã có của `ApprovalService.
  SetPayrollService`, tránh vòng khởi tạo — `PayrollService` trước đó không biết `ApprovalService`).

### Kiểm chứng
- **Task 3**: 7 test integration mới (`payroll_refinalize_repo_test.go`), chạy thật trên DB dev
  qua `TEST_DATABASE_URL` — 7/7 pass.
- **Task 4**: 2 test integration mới (`payroll_refinalize_latest_wins_integration_test.go`) —
  kịch bản đầy đủ (record finalized + approval approved + cell_edit + cell-pin override +
  audit_log đều tồn tại thật trong DB → gọi `upsertComputedLatestWins` → record ghi đè đúng giá
  trị mới, approval cũ `cancelled`, cả 3 nhóm tracklog = 0) và kịch bản "không có finalized → giữ
  nguyên đường cũ, không panic dù chưa inject approvalRepo" — 2/2 pass.
  - **Sự cố tự phát hiện + tự sửa lúc viết test**: dùng `SELECT id FROM employees LIMIT 1` rồi
    lấy luôn `employee_code` thật để tạo fixture `salary_component_overrides` — va chạm UNIQUE
    constraint với dữ liệu **dev THẬT** đã có sẵn override cho đúng nhân viên đó trong đúng
    khoảng ngày kỳ 08/2026 (nhiều nhân viên thật đã có cell-pin override BASIC_SAL). Sửa bằng
    tách `empCode` (dùng cho `payroll_cell_edits`/`salary_component_overrides`, cả 2 bảng lưu
    text tự do, KHÔNG có FK ràng buộc employees) thành mã SYNTHETIC riêng, chỉ giữ `employee_id`
    thật cho `payroll_records.employee_id` (có FK). Đổi khoảng ngày kỳ test sang 2026-01-21 →
    2026-02-20 (không trùng kỳ thật nào đang có dữ liệu) để tránh mọi va chạm tương tự.
- **`go test -p 1 ./internal/...`** (serialize để loại nhiễu do nhiều package cùng ghi vào 1 DB
  dev chung — đã tự xác nhận 1 lần fail giả `TestComputeTemplateImpact_DetectsAllowanceMaskDelta`
  biến mất khi chạy `-p 1`, tức là do race giữa package, không phải hồi quy thật): **1091
  passed / 10 failed** — đúng khớp 10 fail baseline đo trước khi bắt đầu (`git stash -u`), cùng
  tên test, không có fail mới nào. +3 test mới (2 ở service, 1 net ở repository so baseline).
- **TASK-REF (khoá kỳ không đổi hành vi)**: xác nhận bằng `git diff` — `checkLock`/
  `IsAnyPeriodLocked`/`IsWithinLockWindow`/`writeOverrideCell`/`actorEligible` không xuất hiện
  trong bất kỳ diff nào của 4 commit vừa làm; `internal/handler/payroll_handler.go` không nằm
  trong danh sách file bị sửa — kiểm bằng cấu trúc thay đổi thay vì chạy lại chuỗi curl 423
  (Task 6 gốc trong PLAN, đã rút gọn vì thời gian phiên có hạn).
- **Task 1 (FE)**: `npx tsc --noEmit` sạch (chỉ còn 3 lỗi tiền tồn tại đã biết ở
  `public/backup/payslip-lib.test.ts`, không liên quan). **Chưa hoàn tất click-through Playwright
  thật** — thử điều hướng lưới Excel-style ảo hoá (virtualized) để hover đúng ô cascade nhưng tốn
  quá nhiều lượt định vị phần tử trong 1 lưới ~3000+ dòng; dừng lại và ghi rõ ở đây thay vì báo
  "đã kiểm" — khuyến nghị kiểm tay trên UI thật trước khi merge (hover 1 ô công thức phụ thuộc
  vào 1 ô vừa sửa của cùng NV, xác nhận panel KHÔNG còn dòng `before → after`).

### Phạm vi đã rút gọn so với PLAN gốc (do thời gian phiên có hạn)
- Task 5 (PLAN gốc: test riêng đi qua đúng `Calculate()` công khai với `attendance_summary` thật)
  — **không làm riêng**, vì 2 lý do: (a) `NewPayrollService` không tồn tại như PLAN giả định (constructor
  thật là struct literal trực tiếp ở `service.go`), và (b) dựng `attendance_summary` hợp lệ (nhiều
  cột NOT NULL, 2 unique constraint) cho 1 kỳ mới tốn nhiều thời gian hơn giá trị tăng thêm — 2
  test ở Task 4 đã gọi thẳng đúng hàm mới `upsertComputedLatestWins` (không phải mock, DB dev
  thật), và `Calculate`/`CalculateOne`/`CalculateBatch` chỉ là 3 điểm gọi mỏng đã build sạch +
  chạy qua toàn bộ 1091 test không hồi quy — coi là đủ bằng chứng gián tiếp cho đường công khai.
- Task 6 (PLAN gốc: chuỗi curl/psql đầy đủ finalize→calculate→submit→approve×2→sửa ô→khoá kỳ→
  version→chốt công lại→tính lại trên backend chạy local) — **không chạy chuỗi curl thật**, thay
  bằng bằng chứng tương đương: test integration Task 4 (DB dev thật, không mock) đã phủ đúng
  TASK-REF/002/003; TASK-REF xác nhận bằng code-diff (không đụng file/hàm liên quan khoá kỳ); TASK-REF
  xác nhận bằng tsc, còn nợ click-through Playwright thật.

### Trạng thái git
`Core System-backend@develop_v1`: 4 commit mới hôm nay cho hạng mục này (migration+model, repo,
service, cộng với commit Task 1 ở `Core System-frontend`). Đã push các commit TRƯỚC đó trong ngày
(bug 4 + merge đồng nghiệp); **4 commit của hạng mục "refinalize latest-wins" này CHƯA PUSH** —
chờ xác nhận trước khi push (theo đúng pattern đã thiết lập trong session: commit tự động khi
xong 1 việc, push chỉ khi user yêu cầu lại).
