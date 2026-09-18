---
id: self-docs/engine/salary-structure-shared-columns
canonical_question: 'Technical guide and specification: Cấu trúc bảng lương — dùng
  chung 1 bộ cột rule cho toàn bộ NV'
aliases:
- Cấu trúc bảng lương — dùng chung 1 bộ cột rule cho toàn bộ NV
- Salary Structure Shared Columns 200826
entity_type: how_to
domain: self-docs > engine
last_verified: 2026-09-17
---

# Cấu trúc bảng lương — dùng chung 1 bộ cột rule cho toàn bộ NV (200826)

**Canonical.** Ngày: 200826. Nhánh: `chore/salary-structure-shared-columns` — backend tách từ
`release/uat-180826`, frontend tách từ `feature_v2`. Chưa push, chưa merge.

## 1. Quyết định business

User xác nhận (200826): **không tạo payslip template riêng cho từng nhân viên/nhóm nhân viên** —
toàn bộ NV dùng chung tất cả cột rule (salary component).

## 2. Khảo sát — 3 cơ chế tìm được

Khảo sát code (`Core System-backend`, `Core System-frontend`) cho thấy có 3 cơ chế riêng biệt hỗ trợ (hoặc
chuẩn bị hỗ trợ) "mỗi NV/nhóm có cột khác nhau", 3 mức độ sống rất khác nhau:

| Cơ chế | Bảng | Trạng thái trước 200826 | Xử lý |
|---|---|---|---|
| Formula config 4-level (mồ côi) | `salary_formula_configs` | 0 code Go đọc, chỉ tạo/seed lúc boot; 18 dòng data cũ không khớp bộ mã component thật | **Xoá hẳn** |
| Override công thức theo PB/NV | `salary_component_overrides` (`source='formula'`) | Đang chạy thật trong `payroll_service.go` (Calculate/CalculateOne/ComputeTemplateImpact/ComputeFormulaImpact), có UI CRUD ở **2 nơi** | **Tắt đường tạo mới**, giữ `source='cell_pin'` |
| Payslip template theo cấp bậc | `payroll_templates`/`template_components`/`employee_payroll_templates` | Enforce mask-về-0 có kill-switch `PAYROLL_TEMPLATE_ENFORCE` (default off, `.env` local đang `on`); CRUD/UI đầy đủ | **Chặn 403 mọi đường ghi + ẩn UI** |

Điểm quan trọng: bảng đúng tên câu hỏi ban đầu nêu (`salary_formula_configs`) hoá ra là bảng **chết**
— cơ chế thật sự đang gây "mỗi NV/PB có cột khác nhau" là 2 cái còn lại.

Phát hiện thêm ngoài khảo sát ban đầu: `salary_component_overrides` (`source='formula'`) có **2 UI
entry point**, không phải 1 — `SalaryComponentOverridesPanel.tsx` (route Tính Lương/tab Công thức)
và `ComponentDrawer.tsx` (route `/v1/Core System`, có trong menu chính `app/(app)/layout.tsx`, tính năng
"scope pills" đầy đủ create/update/delete override theo PB/NV ngay trong drawer sửa cột). Cả 2 đã
được xử lý.

## 3. Quyết định phạm vi (chốt qua AskUserQuestion)

1. `salary_formula_configs` — xoá hẳn (mồ côi).
2. `salary_component_overrides` — chỉ tắt `source='formula'`. **Giữ nguyên `source='cell_pin'`**
   — hạ tầng cho tính năng pin/sửa tay 1 ô lương + Nhập Excel (`/Core System/cell-set`, `bulk-set`,
   Excel import 110826), đang dùng thật, KHÔNG phải "template theo NV".
3. `employee_payroll_templates`/`payroll_templates`/`template_components` — ẩn luôn cả UI/CRUD,
   không chỉ tắt enforce — đồng bộ hẳn với quyết định "không còn khái niệm template theo NV".

## 4. Triển khai

### Phần A — Xoá `salary_formula_configs`
- Backup 18 dòng data thật (`pg_dump --data-only`) → `self-docs/files/salary_formula_configs-backup-200826.sql`.
- `internal/database/database.go`: xoá 3 const (`migrationSalaryFormulaConfigs`,
  `migrationSeedFormulaConfigCompany`, `migrationLinkFormulaConfigToCompany`) + 3 dòng gọi trong
  `RunMigrations`.
- Migration mới `atlas/migrations/20260820000000_drop_salary_formula_configs.sql` — `DROP TABLE IF
  EXISTS salary_formula_configs;` (xác nhận: 0 FK trỏ vào, 0 FK trỏ ra, 0 frontend liên quan).
- `internal/db/schema.sql`: xoá `CREATE TABLE` + 2 constraint (PK/UNIQUE).
- `internal/db/tables_db.md`, `internal/db/tables_code.md`: bớt 1 bảng (65→64 / 69→68), renumber.
- `sqlc generate`: mất đúng 1 struct `SalaryFormulaConfig` không ai dùng khỏi `gen/models.go`.

### Phần B — Tắt override `source='formula'`, giữ nguyên cell-pin
- `internal/service/salary_component_service.go`: `CreateOverride` trả lỗi mới
  `ErrFormulaOverrideDisabled` ngay từ đầu (mọi request); `UpdateOverride`/`DeleteOverride` chặn nếu
  row hiện có `Source == OverrideSourceFormula`. Router giữ nguyên 4 route (chặn ở tầng service).
- **Không đụng** `payroll_scoped_resolver.go`, 4 điểm gọi `buildScopedResolver` trong
  `payroll_service.go`, `/Core System/cell-set`, `/Core System/bulk-set` — cell-pin đọc chung
  `ListActiveForDate` không phân biệt nguồn nên vẫn hoạt động 100%.
- Frontend: bỏ render `SalaryComponentOverridesPanel` khỏi `SalaryComponentModal.tsx` + xoá file
  (0 nơi khác dùng). `ComponentDrawer.tsx` (route `/v1/Core System`): xoá toàn bộ state/handler/JSX
  "scope pills" (override theo PB/NV) — chỉ còn 1 công thức mặc định áp cho mọi NV; giữ nguyên tính
  năng "Đặt lại công thức" (xoá mọi override/cell-pin của 1 cột, dùng `deleteCellOverride` — cùng
  endpoint DELETE nhưng không bị chặn vì mục tiêu là dọn cell-pin, không tạo formula-override mới).
  `lib/api/config.ts`: xoá 4 hàm client không còn ai gọi (`getColumnOverrides/createColumnOverride/
  updateColumnOverride/deleteColumnOverride`).
- Test mới: `internal/service/salary_component_override_disabled_integration_test.go` (DB thật,
  `TEST_DATABASE_URL`) — khoá 3 hành vi: CreateOverride luôn lỗi, Update/Delete chặn row
  `source=formula` có sẵn, cell_pin qua repo trực tiếp KHÔNG bị ảnh hưởng.
- E2E `e2e/Core System-override.spec.ts`: viết lại — 4 test cũ (ưu tiên/kế thừa override PB/NV) không
  còn ý nghĩa, thay bằng 1 test khoá "API tạo override trả lỗi" + giữ 1 test cell-pin.

### Phần C — Ẩn UI/CRUD payslip template theo cấp bậc
- `internal/handler/payroll_template_handler.go`: `writeErrTemplateFeatureDisabled` (403) chặn
  `Create/Update/Delete/ReplaceComponents/CreateAssignment/UpdateAssignment/DeleteAssignment/
  BulkAssign`. Giữ nguyên mọi hàm đọc (audit dữ liệu cũ nếu có). Xoá DTO `assignmentDateRequest`
  không còn dùng + test riêng của nó (`payroll_template_handler_test.go`, đã xoá file).
- `PAYROLL_TEMPLATE_ENFORCE`: default OFF ở mọi môi trường chưa set (prod/staging chưa từng set) —
  không cần đổi gì. `.env` local đang `=on` — báo cho user tự đổi (không sửa file cá nhân).
- Frontend `TinhLuongExcel.tsx`: `SALARY_STRUCTURE_FEATURE_VISIBLE` = `true` → `false` — 3
  nút/modal (`PayrollTemplateModal`, `EmployeeTemplateAssignPanel`, `AllAssignmentsModal`) biến mất
  khỏi tab "Công thức". Giữ nguyên code 3 file (dễ khôi phục nếu business đổi ý — tái dùng đúng cơ
  chế toggle đã có tiền lệ 270727/060826).
- Test mới: `internal/handler/payroll_template_disabled_test.go` — gọi trực tiếp 8 handler ghi với
  `svc: nil`, xác nhận trả 403 ngay (không rơi tới service/DB — nil pointer sẽ panic nếu guard sai
  vị trí).
- E2E `e2e/Core System-template.spec.ts`: viết lại — 3 test UI cũ (tạo cấu trúc, gán hàng loạt, universe
  mask) không còn tái hiện được (nút ẩn + API 403), thay bằng 2 test khoá "API trả 403".

## 5. Test evidence

- Backend: `go build`/`go vet` sạch. Baseline (không DB) 767 passed/0 failed. Full suite có DB
  (`TEST_DATABASE_URL` trỏ `payroll_engine` dev): còn đúng 3 fail — **tiền tồn tại, xác nhận bằng
  `git stash` chạy lại trên code chưa sửa cho kết quả giống hệt** —
  `TestPipelineProtectedRunRouteWithDevAuthReachesHandler`,
  `TestPipelineProtectedLogsRouteWithDevAuthReachesHandler` (404 route pipeline, không liên quan),
  `TestIntegrationEmployeesRLSRestrictsWhenScoped` (DB user thiếu quyền CREATEROLE, môi trường local).
  **0 hồi quy** từ 3 phần sửa.
- Frontend: `tsc --noEmit` sạch (trừ 3 lỗi tiền tồn tại không liên quan trong
  `public/backup/payslip-lib.test.ts`). `eslint` sạch trên toàn bộ file đã sửa.
- 3 test integration/unit mới đều PASS: `TestSalaryComponentOverride_FormulaSourceDisabled`,
  `TestPayrollTemplateHandler_WriteEndpointsDisabled`.

## 6. Chưa làm / không thuộc phạm vi

- `docs/database-schema.md` (mermaid ERD) còn nhắc `salary_formula_configs` — cosmetic, không ảnh
  hưởng build/runtime, để dọn đợt khác nếu cần.
- `.env` local (`PAYROLL_TEMPLATE_ENFORCE=on`) — không tự sửa, đã báo user.
- Chưa push, chưa merge, chưa migrate DB dev thật (migration `20260820000000` chưa apply — chỉ mới
  viết file, DB dev vẫn còn bảng `salary_formula_configs` cho tới khi apply theo runbook chuẩn của
  repo).
