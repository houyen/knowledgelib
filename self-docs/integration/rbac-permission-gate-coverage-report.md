---
id: self-docs/integration/rbac-permission-gate-coverage-report
canonical_question: 'Technical guide and specification: Báo cáo bao phủ RBAC — 241
  route API backend'
aliases:
- Báo cáo bao phủ RBAC — 241 route API backend
- RBAC Permission Gate Coverage Report 200826
entity_type: how_to
domain: self-docs > integration
last_verified: 2026-09-17
---

# Báo cáo bao phủ RBAC — 241 route API backend (Core System-backend)

**Ngày:** 20/08/2026 · **Nhánh:** `release/uat-180826` (commit `6184c13`) · **Nguồn:** `go test ./internal/app/... -run TestPermissionGateCoverageReport -v` (test tự động có sẵn trong repo, `internal/app/permission_gate_coverage_test.go`) + kiểm chứng thật bằng request HTTP thật trên bản clone dữ liệu dev.

## Cách đọc báo cáo này

Test tự động duyệt (`chi.Walk`) toàn bộ router thật của backend và phân loại MỖI route API vào đúng 1 trong 4 nhóm theo middleware đang áp:

| Nhóm | Ý nghĩa |
|---|---|
| **`[fine]`** Fine-gated | Có cả `RequireRole` (vai trò) lẫn `RequirePermission` (quyền mịn theo module.action) — mức bảo vệ chặt nhất. |
| **`[role-only]`** Role-gate only | Chỉ kiểm vai trò (`RequireRole`), không có lớp quyền mịn theo module — vẫn được bảo vệ, nhưng thô hơn (không phân biệt view/create/edit/delete trong cùng vai trò). |
| **`[allowlist]`** Allowlist self-scoped | Không có role-gate ở tầng router, nhưng route tự giới hạn phạm vi bên trong handler (ví dụ `/me`, `/ess/*` — nhân viên chỉ xem được dữ liệu của chính mình). Nằm trong danh sách đã rà soát và xác nhận an toàn (`allowRoutesWithoutRoleGate`). |
| **`unknown`** (khiến test FAIL) | Route **mới**, chưa được phân loại — không có role-gate, không có permission-gate, cũng chưa có trong allowlist đã duyệt. Đây là tín hiệu "có ai vừa thêm route mà quên nghĩ tới phân quyền". |

Test này **không assert phải đạt bao nhiêu %** — mục đích là làm cho con số bao phủ nhìn thấy được mỗi lần chạy, chỉ fail cứng khi có route rơi vào nhóm `unknown`.

## Kết quả hiện tại: 241 route

- **Fine-gated: 180/241 (75%)**
- **Role-gate only: 36/241 (15%)**
- **Allowlist self-scoped: 21/241 (9%)**
- **Unknown (test FAIL): 4/241** — xem mục "Vấn đề đang mở" bên dưới.

### Danh sách đầy đủ — Fine-gated (180 route)

```
DELETE /api/v1/admin/approval-rules/{id}
DELETE /api/v1/allowance-overrides/{id}
DELETE /api/v1/companies/{id}
DELETE /api/v1/config/employee-Core System-templates/{id}
DELETE /api/v1/config/leave-types/{id}
DELETE /api/v1/config/Core System-templates/{id}
DELETE /api/v1/config/pit-brackets/{id}
DELETE /api/v1/config/public-holidays/{id}
DELETE /api/v1/config/report-templates/{id}
DELETE /api/v1/config/salary-components/{id}
DELETE /api/v1/config/salary-components/{id}/overrides/{ovId}
DELETE /api/v1/employees/{id}/dependents/{depId}
DELETE /api/v1/employees/{id}/educations/{eduId}
DELETE /api/v1/employees/{id}/experiences/{expId}
DELETE /api/v1/employees/{id}/languages/{langId}
DELETE /api/v1/employees/{id}/work-histories/{whId}
DELETE /api/v1/Core System-periods/{id}
DELETE /api/v1/roles/employees
GET /api/v1/adapter/attendance
GET /api/v1/adapter/timesheet
GET /api/v1/admin/approval-rules/
GET /api/v1/allowance-overrides/
GET /api/v1/allowance-overrides/batches
GET /api/v1/allowance-overrides/template
GET /api/v1/companies/
GET /api/v1/config/employee-levels
GET /api/v1/config/employee-Core System-templates/
GET /api/v1/config/employee-Core System-templates/{employeeId}
GET /api/v1/config/employee-Core System-templates/{employeeId}/resolve
GET /api/v1/config/insurance/
GET /api/v1/config/leave-types/
GET /api/v1/config/ot-multipliers/
GET /api/v1/config/overtime-types
GET /api/v1/config/Core System-templates/
GET /api/v1/config/Core System-templates/{id}
GET /api/v1/config/Core System-templates/{id}/assignments
GET /api/v1/config/Core System-templates/{id}/components
GET /api/v1/config/period-config/
GET /api/v1/config/pit-brackets/
GET /api/v1/config/pit-brackets/effective
GET /api/v1/config/public-holidays/
GET /api/v1/config/report-templates/
GET /api/v1/config/report-templates/{id}
GET /api/v1/config/salary-components/
GET /api/v1/config/salary-components/history
GET /api/v1/config/salary-components/{id}
GET /api/v1/config/salary-components/{id}/history
GET /api/v1/config/salary-components/{id}/overrides
GET /api/v1/config/salary-components/{id}/usage
GET /api/v1/config/system/
GET /api/v1/config/transport-allowances/
GET /api/v1/departments/
GET /api/v1/employees/
GET /api/v1/employees/work-histories
GET /api/v1/employees/{id}
GET /api/v1/employees/{id}/bank-accounts
GET /api/v1/employees/{id}/contracts
GET /api/v1/employees/{id}/dependents
GET /api/v1/employees/{id}/educations
GET /api/v1/employees/{id}/experiences
GET /api/v1/employees/{id}/languages
GET /api/v1/employees/{id}/work-histories
GET /api/v1/hris/attendance-audit-logs
GET /api/v1/hris/attendance-computed/
GET /api/v1/hris/attendance-daily/
GET /api/v1/hris/attendance-daily/matrix
GET /api/v1/hris/attendance-daily/orgs
GET /api/v1/hris/attendance-summary/
GET /api/v1/Core System-periods/
GET /api/v1/Core System-periods/{id}
GET /api/v1/Core System/attendance-codes/{periodId}
GET /api/v1/Core System/cell-edits/{periodId}
GET /api/v1/Core System/cell-overrides/{periodId}
GET /api/v1/Core System/payslip-sftp/upload-ws
GET /api/v1/Core System/period/{periodId}
GET /api/v1/Core System/rows/{periodId}
GET /api/v1/Core System/summary/{periodId}
GET /api/v1/Core System/template-enforce-status
GET /api/v1/reports/bank-transfer
GET /api/v1/reports/Core System-summary
GET /api/v1/roles/
GET /api/v1/roles/access-review
GET /api/v1/roles/email-drift
GET /api/v1/roles/employees
GET /api/v1/roles/{id}/permissions
GET /api/v1/timesheets/
GET /api/v1/timesheets/{employeeCode}
PATCH /api/v1/allowance-overrides/{id}/close
PATCH /api/v1/hris/attendance-daily/{id}
POST /api/v1/adapter-sync/pull
POST /api/v1/adapter/sync
POST /api/v1/admin/approval-rules/
POST /api/v1/allowance-overrides/conflicts
POST /api/v1/allowance-overrides/parse
POST /api/v1/allowance-overrides/submit
POST /api/v1/companies/
POST /api/v1/companies/sync-from-hris
POST /api/v1/config/employee-Core System-templates/
POST /api/v1/config/employee-Core System-templates/bulk
POST /api/v1/config/insurance/
POST /api/v1/config/leave-types/
POST /api/v1/config/ot-multipliers/
POST /api/v1/config/Core System-templates/
POST /api/v1/config/pit-brackets/
POST /api/v1/config/public-holidays/
POST /api/v1/config/report-templates/
POST /api/v1/config/salary-components/
POST /api/v1/config/salary-components/validate
POST /api/v1/config/salary-components/{id}/overrides
POST /api/v1/departments/sync
POST /api/v1/departments/upload-org-structure
POST /api/v1/employees/
POST /api/v1/employees/bulk-company
POST /api/v1/employees/sync
POST /api/v1/employees/{id}/dependents
POST /api/v1/employees/{id}/educations
POST /api/v1/employees/{id}/experiences
POST /api/v1/employees/{id}/languages
POST /api/v1/employees/{id}/work-histories
POST /api/v1/hris/attendance-computed/upsert
POST /api/v1/hris/attendance-daily/compute-allowances
POST /api/v1/hris/attendance-daily/compute-summary
POST /api/v1/hris/attendance-daily/compute-transport
POST /api/v1/hris/attendance-daily/export
POST /api/v1/hris/attendance-daily/preview
POST /api/v1/hris/attendance-daily/recompute
POST /api/v1/hris/attendance-daily/sync
POST /api/v1/hris/attendance-summary/finalize
POST /api/v1/hris/attendance-summary/finalize-from-daily
POST /api/v1/hris/attendance-summary/generate-from-daily
POST /api/v1/hris/attendance-summary/save
POST /api/v1/hris/attendance-summary/unfinalize
POST /api/v1/Core System-periods/
POST /api/v1/Core System/approve/{id}
POST /api/v1/Core System/calculate-one/{periodId}
POST /api/v1/Core System/calculate/{periodId}
POST /api/v1/Core System/cell-set/{periodId}
POST /api/v1/Core System/cell-undo/{periodId}
POST /api/v1/Core System/cells/bulk-set/{periodId}
POST /api/v1/Core System/formula-impact/{periodId}
POST /api/v1/Core System/payslip-sftp/push
POST /api/v1/Core System/reject/{id}
POST /api/v1/Core System/template-impact/{periodId}
POST /api/v1/reports/config/validate-expr
POST /api/v1/reports/config/{templateId}/run
POST /api/v1/reports/raw-export
POST /api/v1/reports/{code}/export
POST /api/v1/roles/
POST /api/v1/roles/employees
POST /api/v1/timesheets/sync
PUT /api/v1/admin/approval-rules/{id}
PUT /api/v1/companies/{id}
PUT /api/v1/config/employee-Core System-templates/{id}
PUT /api/v1/config/leave-types/{id}
PUT /api/v1/config/ot-multipliers/{id}
PUT /api/v1/config/Core System-templates/{id}
PUT /api/v1/config/Core System-templates/{id}/components
PUT /api/v1/config/period-config/
PUT /api/v1/config/pit-brackets/{id}
PUT /api/v1/config/public-holidays/{id}
PUT /api/v1/config/report-templates/{id}
PUT /api/v1/config/salary-components/reorder
PUT /api/v1/config/salary-components/{id}
PUT /api/v1/config/salary-components/{id}/overrides/{ovId}
PUT /api/v1/config/salary-components/{id}/visible
PUT /api/v1/config/system/
PUT /api/v1/config/transport-allowances/
PUT /api/v1/departments/{id}/policy
PUT /api/v1/employees/{id}
PUT /api/v1/employees/{id}/dependents/{depId}
PUT /api/v1/employees/{id}/educations/{eduId}
PUT /api/v1/employees/{id}/educations/{eduId}/primary
PUT /api/v1/employees/{id}/experiences/{expId}
PUT /api/v1/employees/{id}/languages/{langId}
PUT /api/v1/employees/{id}/profile
PUT /api/v1/employees/{id}/work-histories/{whId}
PUT /api/v1/Core System-periods/{id}
PUT /api/v1/roles/{id}
PUT /api/v1/roles/{id}/permissions
PUT /api/v1/roles/{id}/priority
```

### Danh sách đầy đủ — Role-gate only (36 route)

```
GET /api/v1/approvals/inbox
GET /api/v1/approvals/{entityType}/{entityId}
GET /api/v1/attendance/items
GET /api/v1/attendance/items/{employeeId}/period/{periodId}
GET /api/v1/attendance/records
GET /api/v1/attendance/records/{employeeId}/period/{periodId}
GET /api/v1/audit-logs/
GET /api/v1/config/salary-components/dev/component-as-of
GET /api/v1/hris/connectors/
GET /api/v1/hris/connectors/{jobType}/logs
GET /api/v1/pipeline/logs
GET /api/v1/pipeline/status
GET /api/v1/reports/catalog
GET /api/v1/sync/jobs
GET /api/v1/sync/jobs/{id}
GET /api/v1/sync/status
POST /api/v1/approvals/{requestId}/act
POST /api/v1/hris/connectors/{jobType}/sync
POST /api/v1/Core System-periods/{id}/lock
POST /api/v1/Core System-periods/{id}/unlock
POST /api/v1/Core System/finalize/{periodId}
POST /api/v1/pipeline/hris/sync/all
POST /api/v1/pipeline/hris/sync/cost-centers
POST /api/v1/pipeline/hris/sync/districts
POST /api/v1/pipeline/hris/sync/employee-levels
POST /api/v1/pipeline/hris/sync/employees
POST /api/v1/pipeline/hris/sync/job-rotation-types
POST /api/v1/pipeline/hris/sync/locations
POST /api/v1/pipeline/hris/sync/org-structures
POST /api/v1/pipeline/hris/sync/provinces
POST /api/v1/pipeline/hris/sync/regions
POST /api/v1/pipeline/hris/sync/work-histories
POST /api/v1/pipeline/run
POST /api/v1/sync/
PUT /api/v1/attendance/items/{id}/override
PUT /api/v1/hris/connectors/{jobType}
```

### Danh sách đầy đủ — Allowlist self-scoped (21 route)

```
GET /api/v1/dashboard/stats
GET /api/v1/ess/attendance-calendar
GET /api/v1/ess/leave-details
GET /api/v1/ess/payslip
GET /api/v1/ess/profile
GET /api/v1/ess/timesheet
GET /api/v1/ess/timesheet-raw
GET /api/v1/geo/map-ward
GET /api/v1/geo/provinces
GET /api/v1/geo/wards
GET /api/v1/graduate-schools
GET /api/v1/majors
GET /api/v1/me
GET /api/v1/pipeline/health
GET /api/v1/ref/{table}
GET /api/v1/versions/{domain}/{scopeKey}/
GET /api/v1/versions/{domain}/{scopeKey}/head
POST /api/v1/Core System/dev/seed-test-data/{periodId}
POST /api/v1/versions/{domain}/{scopeKey}/
POST /api/v1/versions/{domain}/{scopeKey}/restore/{versionId}
PUT /api/v1/ess/profile
```

## Vấn đề đang mở — 4 route "unknown" (khiến test FAIL, tiền tồn tại, KHÔNG liên quan salary-components/reports)

```
GET /api/v1/adapter-sync/state
GET /api/v1/Core System/payslip-sftp/history
GET /api/v1/Core System/payslip-sftp/status
GET /api/v1/Core System/payslip-sftp/ws
```

4 route này **không có role-gate, không có permission-gate, chưa nằm trong allowlist đã duyệt** — cần một trong hai hướng xử lý: (a) thêm `RequireRole`/`RequirePermission` phù hợp, hoặc (b) nếu cố ý mở công khai/tự-giới-hạn trong handler thì thêm vào allowlist `allowRoutesWithoutRoleGate` kèm lý do rõ ràng. Đây là lỗi tiền tồn tại (đã có trước đợt làm việc 20/08/2026 của phiên này), **chưa sửa**.

## Đối chiếu với 2 tính năng vừa kiểm chứng thật (20/08/2026)

Ngoài báo cáo tĩnh ở trên, đã test bằng request HTTP thật (trên bản clone dữ liệu dev, xoá sau khi test) để xác nhận gate không chỉ "có tồn tại" mà còn **chặn/cho đúng theo vai trò thật**:

| Route/module | Vai trò test | Kết quả thật |
|---|---|---|
| `/config/salary-components` | không role | 403 |
| `/config/salary-components` | `config_admin` | 403 (đúng — 0/6 quyền `Settings.SalaryComponents`) |
| `/config/salary-components` | `hr_admin` | 200, trả đúng dữ liệu component thật |
| `/reports/*` (mọi route) | không role | 403 |
| `/reports/catalog` | `hr_admin` | 200 — danh mục 17 báo cáo |
| `/reports/bank-transfer` (download) | `hr_admin` | 200 — file Excel thật, mở ra có dữ liệu nhân viên/ngân hàng thật (không phải file rỗng) |
| `/reports/*` (mọi route) | `cb_staff` | **403 — dù `cb_staff` có `Reports.export=true` trong bảng `permissions`** |

### Phát hiện: "quyền ma" trên module Reports (cần hỏi lại nghiệp vụ, chưa sửa)

`cb_staff` được gán `Reports.view/create/edit/delete/export = true` trong bảng `permissions`, nhưng **không có route `/reports/*` nào dùng tới lớp quyền này** — toàn bộ bị chặn cứng ở tầng ngoài bởi `RequireRole("hr_admin")` (`internal/app/router.go:175-176`, comment "Reports (HR Admin only)") TRƯỚC KHI request chạm tới `RequirePermission(Reports, export)`. Về mặt kỹ thuật đây KHÔNG phải lỗ hổng (route vẫn bị chặn đúng), nhưng là dữ liệu quyền "chết" — dễ gây hiểu nhầm khi tra bảng `permissions` (tưởng `cb_staff` xuất được báo cáo). Cần hỏi HR/nghiệp vụ: đây có phải chủ ý (dự phòng cho tương lai / hoặc dùng chung tên module với chỗ khác) hay là cấu hình sai nên dọn — **chưa tự xử lý**.

## Nguồn / cách chạy lại

```bash
cd Core System-backend
go test ./internal/app/... -run TestPermissionGateCoverageReport -v
```

Test này chạy như một phần của `go test ./...` bình thường (không cần `TEST_DATABASE_URL` — chỉ duyệt router trong bộ nhớ, không cần kết nối DB thật).

Tài liệu liên quan: `self-docs/Handoff-Salary-Rule-Security-Configurability-200826.md` (mục 7), `self-docs/RBAC-Hybrid-Scoping-Implementation-140726.md` (schema RBAC canonical).
