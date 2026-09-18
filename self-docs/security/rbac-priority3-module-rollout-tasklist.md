---
id: self-docs/security/rbac-priority3-module-rollout-tasklist
canonical_question: 'Technical guide and specification: RBAC-Priority3-Module-Rollout-Tasklist-210726'
aliases:
- RBAC-Priority3-Module-Rollout-Tasklist-210726
- RBAC Priority3 Module Rollout Tasklist 210726
entity_type: how_to
domain: self-docs > security
last_verified: 2026-07-21
---

# RBAC-Priority3-Module-Rollout-Tasklist-210726

**Ngày tạo:** 2026-07-21
**Vai trò tài liệu:** danh sách công việc (task list) cho việc mở rộng `RequirePermission` (lớp phân quyền mịn) ra các module còn thiếu — Ưu tiên #3 mục 3 của `self-docs/RBAC-Architecture-Reassessment-200726.md`, đã chọn Phương án A (thủ công từng module, không phải bảng khai báo route). Cập nhật liên tục file này khi làm xong từng module — không tạo file task-list mới cho cùng hạng mục.

## Cách làm chung cho mỗi module (đã áp dụng cho Employees, lặp lại cho các module sau)

1. Kiểm tra bảng `permissions` xem module đó đã có dữ liệu cấu hình sẵn từ UI "Ma trận theo Role" chưa (nếu có, dữ liệu đó sẽ có hiệu lực NGAY khi wire — cần xác nhận người dùng trước nếu có role nào đang có `granted=false` cho action mà route đó hiện đang cho phép).
2. Ánh xạ route → action theo HTTP method: GET → `view`, POST tạo mới → `create`, PUT/PATCH → `edit`, DELETE → `delete` (điều chỉnh nếu module có ngữ nghĩa khác, ví dụ export/approve).
3. Thêm `middleware.RequirePermission(db, "<Module>", action)` vào `r.With(...)` cùng `RequireRole` hiện có — KHÔNG bỏ `RequireRole` (2 lớp chồng nhau, không thay thế nhau).
4. Viết test tích hợp xác nhận enforce thật (role priority cao + permission rows riêng, tách khỏi dữ liệu production thật — xem mẫu `internal/app/employee_routes_permission_integration_test.go`).
5. Chạy `go test ./...` trên `payroll_engine`, xác nhận đúng 9 fail baseline cũ, không hồi quy.
6. Cập nhật mục 3 của `self-docs/RBAC-Architecture-Reassessment-200726.md` (coverage report sẽ tự tăng % qua `permission_gate_coverage_test.go`, không cần tính tay).

## Trạng thái

| # | Module | Trạng thái | Ghi chú |
|---|---|---|---|
| 1 | **Employees** | ✅ Xong (2026-07-21) | 30 route, action view/create/edit/delete. Dữ liệu `permissions` đã có sẵn từ trước (cb_staff, config_admin) — xác nhận người dùng giữ nguyên, cho enforce ngay (cb_staff mất quyền xóa dependents/educations/experiences/languages/work-histories, đúng ý cấu hình cũ). Test: `internal/app/employee_routes_permission_integration_test.go`. Coverage: 49/184 (27%), tăng từ 19/184 (10%). |
| 2 | **Roles/\*** (chính bề mặt cấu hình RBAC) | ✅ Xong (2026-07-21) | 9 route, action view/create/edit/delete. Dữ liệu `permissions` đã có sẵn (`config_admin`: tất cả action=true; `cb_staff`/`employee`: tất cả false nhưng KHÔNG liên quan vì cả hai không nằm trong `RequireRole("hr_admin","config_admin")` của nhóm route này) — kiểm tra kỹ cho thấy **wire module này không đổi hành vi thật nào ngay lập tức** (khác Employees). AssignRole/RemoveRole ánh xạ create/delete (không phải edit — đây là tạo/xoá 1 dòng gán quyền, không sửa role). Test: `internal/app/roles_routes_permission_integration_test.go`. Coverage: 58/184 (32%), tăng từ 49/184 (27%). |
| 3 | **Departments / Companies** | ✅ Xong (2026-07-21) | Departments (4 route): dữ liệu `permissions` có sẵn (cb_staff/config_admin/employee) nhưng chỉ `hr_admin` nằm trong `RequireRole` của nhóm này, và `hr_admin` có 0 dòng (allow-all) — wire không đổi hành vi thật. Companies (5 route): module CHƯA từng tồn tại trong UI "Ma trận theo Role" — đã thêm `"Companies"` vào `MODULES`/`MODULE_LABELS` (`Core System-frontend/lib/rbac-constants.ts`) trước khi wire backend, để admin có chỗ cấu hình sau này. Action mapping: GET→view, POST tạo mới→create, PUT→edit, DELETE→delete; Sync/UploadOrgStructure (Departments) →edit. Test: `internal/app/departments_companies_routes_permission_integration_test.go`. Coverage: 67/184 (36%), tăng từ 58/184 (32%). |
| 4 | Config/* (~30 route: salary-components, pit-brackets, insurance, ot-multipliers, leave-types, public-holidays, period-config, system, transport-allowances, employee-levels, overtime-types) | ✅ Xong (2026-07-21) | Tách riêng từng sub-resource theo quyết định người dùng (nhất quán Insurance/LeaveTypes/PublicHolidays đã tách trước): thêm 5 module mới `Settings.SalaryComponents`, `Settings.PITBrackets`, `Settings.TransportAllowances`, `Settings.PeriodConfig`, `Settings.EmployeeLevels` vào `rbac-constants.ts`; `ot-multipliers`/`overtime-types` dùng chung `Settings.Overtime` có sẵn. Route `/config` chỉ `RequireRole("hr_admin")`, hr_admin có 0 dòng `permissions` cho MỌI module Settings.* → wire KHÔNG đổi hành vi thật nào (giống Roles/Departments/Companies, khác Employees). Test: `internal/app/config_routes_permission_integration_test.go` (spot-check 4 sub-module đại diện, không test hết cả 10). |
| 5 | Attendance / Timesheets / AllowanceOverrides | ✅ Xong (2026-07-21) | Tách `AttendanceSummary`, `AttendanceComputed` thành 2 module mới riêng (theo quyết định người dùng, khớp 2 nhóm route độc lập trong router.go); `AllowanceOverrides` module hoàn toàn mới (0 dòng permission, an toàn tuyệt đối). `AttendanceDaily`/`Timesheets` đã có dữ liệu `permissions` cấu hình sẵn cho cb_staff nhưng CHỈ cho action không map vào route thật nào đang dùng (approve/delete với AttendanceDaily; create/delete/export với Timesheets) hoặc đã true đúng khớp action thật dùng → wire KHÔNG đổi hành vi thật nào. Route `/attendance/items`, `/attendance/records` (stub rỗng, tính năng đã gỡ) — theo quyết định người dùng, **bỏ qua không wire** (đã có RequireRole che, không phải lỗ hổng). Test: `internal/app/attendance_timesheet_allowance_permission_integration_test.go`. Coverage (module #4+#5 gộp): 137/184 (74%), tăng từ 67/184 (36%). |
| 6 | HRIS Connector / Sync / Pipeline | 🚫 Bỏ qua (2026-07-21, quyết định người dùng) | Không triển khai `RequirePermission` cho nhóm này — vẫn giữ nguyên lớp `RequireRole("hr_admin")` hiện có (không phải lỗ hổng, chỉ dừng ở role-gate-only trong coverage report, không phải "unknown"). Coi như Ưu tiên #3 mục 3 đã hoàn tất ở mức người dùng chấp nhận (5/6 module, module còn lại chủ động bỏ qua). |

## Lưu ý xuyên suốt

- **Luôn kiểm tra dữ liệu `permissions` có sẵn trước khi wire** — bài học từ Employees: module đã tồn tại trong UI "Ma trận theo Role" từ lâu (`Core System-frontend/lib/rbac-constants.ts`) nhưng backend chưa từng enforce, nghĩa là có thể đã có dữ liệu cấu hình "ngủ yên" chờ có tác dụng — không giả định bảng trống.
- **Một số module ở bảng trên chưa có tên trong `MODULES`/`MODULE_LABELS`** (`Core System-frontend/lib/rbac-constants.ts`) — cần thêm tên module mới ở đó TRƯỚC khi wire backend, nếu không UI "Ma trận theo Role" sẽ không có chỗ để cấu hình module đó (dù backend enforce, admin không có màn hình để bật/tắt).
- File này thay thế việc phải tự nhớ thứ tự — mỗi phiên làm việc tiếp theo đọc bảng trạng thái ở trên để biết module nào tiếp theo, không cần hỏi lại.
