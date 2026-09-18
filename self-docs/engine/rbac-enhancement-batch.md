---
type: draft
title: RBAC — vá 4 route unknown + audit quyền ma + mở rộng fine-gate + rate-limit
  + audit trail
status: approved
timestamp: 2026-08-20
task: null
id: self-docs/engine/rbac-enhancement-batch
canonical_question: 'Technical guide and specification: Rbac Enhancement Batch 200826'
aliases:
- Rbac Enhancement Batch 200826
entity_type: how_to
domain: self-docs > engine
last_verified: 2026-09-17
---

**Quyết định của user (20/08/2026):** Hạng mục 3 → chỉ làm **Approvals + Pipeline** đợt này (Phương án B), 4 domain còn lại để đợt sau. Hạng mục 4 → ngưỡng **30 request/phút/user**.

## Yêu cầu (một câu)

Thi hành 5 hạng mục RBAC user đã chọn từ danh sách đề xuất (`self-docs/RBAC-Permission-Gate-Coverage-Report-200826.md`, `self-docs/Handoff-Salary-Rule-Security-Configurability-200826.md` mục 7): đóng 4 route "unknown", viết audit tìm "quyền ma" toàn hệ thống, nâng 36 route "role-gate only" lên fine-gated, thêm rate-limit cho route ghi/xuất hàng loạt, tổng quát hoá pattern audit trail.

## Context

Nguồn gốc: phiên làm việc 20/08/2026, sau khi test RBAC + reports thật trên `release/uat-180826` (xem `Handoff-...md` mục 7) và chạy `TestPermissionGateCoverageReport` (báo cáo đầy đủ ở `RBAC-Permission-Gate-Coverage-Report-200826.md`). User đã quyết định **giữ nguyên** 2 mục khác trong danh sách gốc (quyền `cb_staff` trên `Reports`, vai trò `config_admin`) — không nằm trong SPEC này.

Sự thật kỹ thuật đã xác minh trực tiếp (nền cho các quyết định dưới đây):

- **4 route "unknown"** (`GET /adapter-sync/state`, `GET /Core System/payslip-sftp/{status,ws,history}`) — đọc code (`internal/app/router.go:629-650`) cho thấy đây là **thiết kế cố ý**, không phải sơ sót: comment tại chỗ ghi rõ "/ws KHÔNG bọc requireEdit: đây là kênh CHỈ ĐỌC trạng thái... vẫn nằm trong nhóm route đã xác thực" và "/history cùng mức xác thực với /status và /ws — chỉ đọc, ai đã đăng nhập cũng tra được". Tức: mọi user đã qua `AuthJWT` (đăng nhập hợp lệ) đều được xem trạng thái đẩy SFTP/đồng bộ adapter — không phân biệt role. Lý do hợp lý: đây là dữ liệu **tiến độ/trạng thái**, không phải dữ liệu lương hay PII. Route ghi (POST `/pull`, `/push`, `/upload-ws`) đã có `requireAdminOrCB + requireEdit` đầy đủ, không nằm trong 4 route lỗi này.
- **"Quyền ma"** — case `cb_staff`/`Reports` (đã tìm) xảy ra vì route `/reports/*` có OUTER `RequireRole("hr_admin")` (`router.go:175-176`) bọc NGOÀI cùng, trong khi INNER `RequirePermission(db, "Reports", "export")` chỉ là lớp lọc thêm — 1 role có permission=true trên module đó nhưng không nằm trong outer role list thì permission đó "chết". Đây là pattern có thể lặp lại ở bất kỳ route nào có CẢ 2 lớp áp cùng lúc (fine-gated, 180/241 route) — chỉ audit được nếu đối chiếu ĐÚNG outer role list với bảng `permissions` thật.
- **36 route "role-gate only"** — đã liệt kê đủ trong `RBAC-Permission-Gate-Coverage-Report-200826.md`, nhóm theo domain: `approvals/*` (2 route), `pipeline/*` (13 route, đa số là `pipeline/hris/sync/*`), `attendance/items|records` (5 route), `sync/*` (4 route), `hris/connectors/*` (3 route), `audit-logs/` (1), `config/salary-components/dev/component-as-of` (1, dev-only đã có comment riêng), còn lại lẻ tẻ.
- **Rate limit** — `go.mod` hiện **không có** thư viện rate-limit nào (`grep -i "rate\|limiter"` = 0 kết quả); phải hoặc viết middleware tối giản (in-memory token bucket, không phụ thuộc ngoài) hoặc thêm dependency (`golang.org/x/time/rate`, đã là extended stdlib, ít rủi ro nhất).
- **Audit trail pattern** — toàn bộ schema chỉ có **2 bảng `_history`**: `salary_component_history` (đã vá ở Việc 1-A, xem `Salary-Formula-Audit-Orphan-Config-Hardening-200826.md`) và `employee_history`. Khảo sát `employee_history` cho thấy đây là bảng theo dõi thay đổi field HRIS theo thời gian (`RecordEmployeeChanges`, `internal/repository/employee_repo.go:678`) — mục đích khác (lịch sử dữ liệu nghiệp vụ để tính lương prorate, không phải audit "ai sửa gì" như `salary_component_history`) và đã được gọi nhất quán qua 1 hàm duy nhất, KHÔNG có UPDATE thẳng SQL nào bỏ qua nó (đã grep toàn bộ `internal/`, không thấy `UPDATE employees SET` nào trong `database.go` chạm các field `trackedHistoryFields` mà không qua `RecordEmployeeChanges`). Tức: **phạm vi tổng quát hoá thực tế hẹp hơn dự kiến ban đầu** — không có bảng `_history` thứ 3 nào khác đang bị bỏ qua theo kiểu Việc 1-A.

Chưa tìm thấy concept/ADR liên quan trong `llmwiki/wiki/` cho các hạng mục này — nguồn chân lý là các file `self-docs/` liệt kê ở trên.

## Global constraints

- **Nhánh làm việc:** `release/uat-180826` — tiếp tục nhánh đang dùng cho các hạng mục bảo mật/RBAC trong phiên này (đã xác nhận chứa toàn bộ `develop` + nội dung `feature_v2`/dọn DB/Workday, chưa merge ngược).
- **`go test ./...` không được hồi quy** — baseline hiện tại 759 passed/6 failed (đo lại tại thời điểm bắt đầu mỗi task, không tin số cũ mù quáng). Việc 1 (đóng 4 route) dự kiến **giảm** số fail xuống 5 (khớp `TestPermissionGateCoverageReport` hết fail) — đây là kỳ vọng rõ ràng, không phải hồi quy.
- Mọi thay đổi ảnh hưởng HÀNH VI phân quyền thật (module mới, role nào có quyền gì, route nào mở/đóng) phải trình bày phương án + hỏi trước khi thi hành — theo đúng quy ước `CLAUDE.md` gốc repo.
- Máy local: KHÔNG tạo HTML trong `llmwiki/html/`; SPEC này đặt ở `self-docs/` (không phải `llmwiki/wiki/sources/draft/`) cùng lý do đã áp dụng ở các SPEC trước (né validator R7 đòi companion HTML).
- Không phá vỡ cơ chế versioning/audit đã có (`InsertVersion`, `salary_component_history`) khi tổng quát hoá pattern audit trail.

## Non-goals

- **Không** đụng tới quyền `cb_staff` trên `Reports` hay vai trò `config_admin` — user đã quyết định giữ nguyên.
- **Không** làm Phase 2 (ABAC/OPA/ngưỡng duyệt theo tiền/mã hoá token) — đã ghi nhận là roadmap riêng, ngoài phạm vi SPEC này.
- **Không** tự sửa bất kỳ "quyền ma" nào tìm được ở Tầng 0-3 — chỉ audit + báo cáo, quyết định sửa để đợt sau (rủi ro nghiệp vụ, cần hỏi từng case).
- **Không** thêm bảng `_history` mới cho bất kỳ bảng cấu hình nào khác — khảo sát cho thấy không có ứng viên thứ 2 ngoài `employee_history` (đã an toàn) và `salary_component_history` (đã vá).
- **Không** dùng Redis/dịch vụ ngoài cho rate-limit trong đợt này (trừ khi user chọn phương án đó ở câu hỏi bên dưới) — ưu tiên giải pháp không thêm hạ tầng.

## Approaches

### Hạng mục 1 — Đóng 4 route "unknown" (rủi ro thấp, đề xuất rõ luôn)

**Phương án A — Thêm vào allowlist `allowRoutesWithoutRoleGate`, kèm comment giải thích (KHUYẾN NGHỊ)**
Thêm 4 route vào map đã có sẵn ở `internal/app/router_role_gate_test.go`, dùng đúng câu giải thích đã có trong comment tại chỗ (`router.go:629-650`) làm lý do — vì đây đúng là allowlist tự-giới-hạn hợp lệ (chỉ đọc trạng thái, không có PII), khớp mọi tiêu chí allowlist khác đã có (`ess/profile`, `dashboard/stats`...).
- *Ưu:* khớp đúng chủ ý thiết kế đã ghi trong code, không đổi hành vi thật, sửa nhỏ (4 dòng), đóng ngay `TestPermissionGateCoverageReport`.
- *Nhược:* không có.

**Phương án B — Thêm `RequireRole` giới hạn (vd `hr_admin`/`cb_staff`) cho 4 route này**
- *Ưu:* thu hẹp bề mặt lộ trạng thái.
- *Nhược:* **đổi hành vi thật ngược lại chủ ý đã ghi trong code** ("ai đã đăng nhập cũng tra được") — cần xác nhận với nghiệp vụ trước, không phải sửa test đơn thuần.

*(Chọn Phương án A — khớp chủ ý thiết kế đã có, không cần hỏi thêm.)*

### Hạng mục 2 — Audit "quyền ma" toàn hệ thống (rủi ro thấp, đề xuất rõ luôn)

**Phương án A — Test tích hợp mới, đối chiếu router + DB thật (KHUYẾN NGHỊ)**
Viết `internal/app/dead_permission_audit_test.go` (cần `TEST_DATABASE_URL`, theo đúng convention có sẵn của repo — nhiều file `*_permission_integration_test.go` đã dùng): tái dùng kỹ thuật `chi.Walk` của `TestPermissionGateCoverageReport` để lấy, với MỖI route fine-gated, (outer role list nếu có `RequireRole` cùng chuỗi middleware) + (module.action của `RequirePermission`). Với mỗi (module, action), query `permissions` xem role nào `granted=true`; nếu role đó dùng route này nhưng KHÔNG nằm trong outer role list (hoặc route không có outer RequireRole nhưng role đó thực tế chưa từng được gán cho ai — trường hợp phụ) → in ra như "quyền ma" ứng viên. Test chỉ **log**, không **assert fail** (giống `TestPermissionGateCoverageReport` — mục đích quan sát).
- *Ưu:* tái dùng hạ tầng đã có, chạy lại được mỗi lần cần audit, không tốn công join tay bảng permissions.
- *Nhược:* cần `TEST_DATABASE_URL` (không chạy trong `go test ./...` mặc định không set biến này — giống các integration test khác trong repo, chấp nhận được vì đây là quy ước sẵn có).

**Phương án B — Script SQL một lần, không phải test lâu dài**
Viết 1 file `.sql` chạy tay đối chiếu, không lưu thành test.
- *Ưu:* nhanh hơn cho lần này.
- *Nhược:* không chạy lại được tự động về sau — sẽ lặp lại đúng lỗi "phát hiện tình cờ" mà audit này muốn tránh.

*(Chọn Phương án A.)*

### Hạng mục 3 — Nâng 36 route "role-gate only" lên fine-gated

**Phương án A — Nâng toàn bộ 36 route trong 1 đợt, đặt tên module theo domain (Approvals, Pipeline, Attendance, SyncJobs, HrisConnectors, AuditLogs)**
- *Ưu:* dứt điểm, nhất quán.
- *Nhược:* khối lượng lớn — 36 route × seed permission cho 6 role hiện có = quyết định nghiệp vụ lớn (role nào được action gì trên MỖI module mới), rủi ro cao nếu đoán sai (khoá nhầm quyền của người đang thao tác thật trên các luồng đồng bộ HRIS/duyệt — production-sensitive).

**Phương án B — Nâng theo đợt, ưu tiên route nhạy cảm nhất trước (KHUYẾN NGHỊ cho đợt này)**
Chỉ làm 2 domain nhạy cảm nhất trước: **Approvals** (`approvals/inbox`, `approvals/{entityType}/{entityId}`, `approvals/{requestId}/act` — duyệt/từ chối, ảnh hưởng quy trình phê duyệt lương) và **Pipeline** (11 route `pipeline/hris/sync/*` + `pipeline/run` — đồng bộ dữ liệu HRIS, có thể ghi đè dữ liệu nhân viên hàng loạt). Các domain còn lại (Attendance, SyncJobs, HrisConnectors, AuditLogs — phần lớn là route ĐỌC, rủi ro thấp hơn) để đợt sau.
- *Ưu:* thu hẹp phạm vi quyết định nghiệp vụ cần hỏi ngay, vẫn giải quyết 2 domain rủi ro cao nhất.
- *Nhược:* chưa dứt điểm toàn bộ 36 route trong 1 lần.

*(Đề xuất chọn B — nhưng đây LÀ quyết định nghiệp vụ, xem câu hỏi ở cuối SPEC.)*

**Nếu chọn làm Approvals + Pipeline, cần quyết định thêm (không tự chọn):** vai trò nào được `view`/`create`(chạy đồng bộ)/`edit`/`approve` trên 2 module mới `Approvals` và `Pipeline` — mặc định đề xuất **giữ nguyên đúng tập role hiện đang có trong outer `RequireRole`** của các route đó (tra ở `router.go`, ví dụ nếu `approvals/*` hiện yêu cầu role X thì seed `granted=true` cho X, `false` cho role khác) để KHÔNG đổi hành vi thật ngay lập tức — chỉ thêm lớp permission mịn hơn PHÍA TRONG, giữ outer role gate y nguyên (giống cách `AttendanceDaily` đã làm ở comment `router.go:608-615`: "cb_staff hiện đã true cho đúng 3 action thật dùng... wire KHÔNG đổi hành vi thật nào ngay lập tức").

### Hạng mục 4 — Rate limit cho route ghi/xuất hàng loạt

**Phương án A — `golang.org/x/time/rate`, per-user token bucket, in-memory (KHUYẾN NGHỊ)**
Thêm middleware dùng `golang.org/x/time/rate` (extended Go stdlib, Google giữ, rủi ro dependency thấp nhất), khoá theo `UserEmailKey` trong context, áp cho 4 route: `cells/bulk-set`, `reports/{code}/export`, `reports/raw-export`, `hris/attendance-daily/sync`.
- *Ưu:* không cần hạ tầng ngoài (Redis), đơn giản, đủ dùng cho quy mô 1 instance backend hiện tại.
- *Nhược:* per-instance (nếu sau này chạy nhiều instance/pod thì mỗi instance có bucket riêng, giới hạn thực tế cao hơn số khai báo) — chấp nhận được vì hiện backend chạy 1 instance.

**Phương án B — Redis-backed rate limiter**
- *Ưu:* đúng khi scale nhiều instance.
- *Nhược:* thêm hạ tầng mới (Redis chưa có trong stack hiện tại), quá mức cần thiết cho quy mô hiện tại.

*(Đề xuất chọn A — nhưng NGƯỠNG cụ thể (bao nhiêu request/phút cho mỗi route) là quyết định nghiệp vụ, xem câu hỏi ở cuối SPEC.)*

### Hạng mục 5 — Tổng quát hoá pattern audit trail

**Phát hiện khi khảo sát: phạm vi hẹp hơn dự kiến.** Chỉ có 2 bảng `_history` trong toàn schema; `employee_history` đã an toàn (ghi nhất quán qua `RecordEmployeeChanges`, không có đường tắt SQL thô nào bỏ qua nó). Không có bảng `_history` thứ 3 nào khác bị bỏ sót kiểu Việc 1-A.

**Phương án A — Đóng hạng mục này bằng 1 dòng xác nhận "đã khảo sát, không còn ca nào khác" (KHUYẾN NGHỊ)**
Ghi nhận vào tài liệu, không cần thi hành gì thêm — Việc 1-A (đã xong) chính là toàn bộ phạm vi generalize khả thi hiện tại.
- *Ưu:* trung thực với những gì tìm được, không làm việc thừa.
- *Nhược:* không có — đây là kết quả khảo sát thật.

**Phương án B — Mở rộng khái niệm "audit trail" sang cả các bảng KHÔNG có `_history` riêng nhưng có `changed_by`/`updated_by` cột trực tiếp** (ví dụ `salary_component_overrides.updated_by` nếu có, hay các bảng config khác) — kiểm tra self-heal migration có ghi đúng các cột này không.
- *Ưu:* mở rộng phạm vi audit hợp lý hơn nếu muốn triệt để.
- *Nhược:* phạm vi khảo sát lớn hơn nhiều (phải rà toàn bộ cột `*_by` trong schema), có thể là 1 SPEC riêng sau này thay vì gộp vào đây.

*(Đề xuất chọn A cho đợt này — B để dành SPEC riêng nếu user muốn mở rộng.)*

## Requirements (FR)

**TASK-REF**: 4 route `adapter-sync/state`, `payslip-sftp/{status,ws,history}` phải nằm trong `allowRoutesWithoutRoleGate` với comment giải thích, và `TestPermissionGateCoverageReport` + `TestG1...` phải PASS sau khi sửa (0 route "unknown").
**TASK-REF**: Test audit "quyền ma" mới phải liệt kê được TOÀN BỘ case (role, module, action, route) mà permission `granted=true` nhưng route không bao giờ tới được vì outer role gate loại trừ — bao gồm lại đúng case `cb_staff`/`Reports` đã biết (dùng làm test-case xác nhận test viết đúng).
**TASK-REF**: (Nếu làm Hạng mục 3) Module `Approvals`/`Pipeline` mới không được đổi hành vi cho phép/từ chối thật của bất kỳ role nào đang dùng các route đó hiện tại (chỉ thêm lớp permission mịn hơn, giữ nguyên outer role gate).
**TASK-REF**: Rate limit middleware không được áp cho route KHÁC ngoài 4 route đã liệt kê, và không được chặn nhầm request hợp lệ dưới ngưỡng đã chọn.
**TASK-REF**: Không thêm bảng `_history` mới nào (Hạng mục 5 đóng bằng xác nhận, không thi hành code).

## Success criteria (SC)

**TASK-REF**: Chạy `go test ./internal/app/... -run "TestPermissionGateCoverageReport|TestG1"` cho 0 fail — người review thấy ngay 4 route trước đây "unknown" nay đã phân loại rõ ràng.
**TASK-REF**: Người phụ trách bảo mật chạy audit test mới, nhận được danh sách đầy đủ case "quyền ma" (nếu còn ngoài case đã biết) mà không cần tự tra tay bảng `permissions` — tiết kiệm thời gian audit thủ công.
**TASK-REF**: (Nếu làm Hạng mục 3) Người dùng `Approvals`/`Pipeline` hiện tại (role đang thao tác thật) không báo mất quyền sau khi seed permission mới — 0 report hồi quy trong 1 tuần đầu.
**TASK-REF**: Route ghi/xuất hàng loạt không còn bị lạm dụng gọi liên tục không giới hạn (verify bằng test tích hợp: vượt ngưỡng → 429).

## Plan

- [x] Đo baseline `go test ./...` trên `release/uat-180826` trước khi sửa: **759 passed / 6 failed** (đúng 6 fail đã biết — 4 sub-test `TestG1...` + `TestG1...` parent + `TestPermissionGateCoverageReport`, tất cả do 4 route "unknown").
- [x] **Hạng mục 1**: thêm 4 route vào `allowRoutesWithoutRoleGate` (`internal/app/router_role_gate_test.go`), kèm comment giải thích lấy nguyên văn từ chủ ý thiết kế đã có trong `router.go`. Kết quả: `TestPermissionGateCoverageReport`/`TestG1...` PASS — **toàn bộ 6 fail baseline biến mất** (không phải hồi quy, đúng kỳ vọng).
- [x] **Hạng mục 2**: viết `internal/app/dead_permission_audit_test.go` — bảng tra cứu thủ công `moduleActionOuterRoles` (xây từ đọc `router.go`, ánh xạ từng `module.action` với outer `RequireRole` thật) đối chiếu bảng `permissions` thật qua `TEST_DATABASE_URL`. Chạy trên **bản clone dữ liệu dev** (`payroll_engine_audit3_200826`, xoá sau khi xong — không đụng DB thật): **bắt đúng lại case `cb_staff`/`Reports.export` đã biết** (assert riêng xác nhận test viết đúng) + tìm thêm **35 "quyền ma" mới**: `cb_staff` bị chặn ngoài trên hầu hết module `Settings.*` (EmployeeLevels, Insurance, LeaveTypes, Overtime, PITBrackets, PeriodConfig, PublicHolidays, SalaryComponents, System, TransportAllowances), `Core System.approve`, `PayrollPeriods.edit`, `Companies.view`, `Departments.view`, `AttendanceSummary.edit`, `AttendanceComputed.edit`; `config_admin` trên `Departments.view`/`Employees.view`/`Settings.System.*`; `search_profile` trên `Employees.view`; `site_admin` trên 4 module Attendance. Cộng thêm **107 `module.action` "unmapped"** (có dòng `granted=true` trong DB nhưng module đó CHƯA từng được `RequirePermission` nào trong code kiểm tới — vd `Dashboard.*`, `EssPayslip.*`, `EssProfile.*`, `HrisApi.*`, `HrisPayrollReport.*`, `Settings.Audit.*` toàn bộ 6 action mỗi module) — khác loại với "quyền ma" (đây là "quyền chưa nối dây", giống pattern `ot_multiplier_configs`/`config_admin` đã ghi ở Handoff mục 6, không phải do outer role gate chặn). **Chỉ audit + báo cáo, không tự sửa quyền nào** — danh sách đầy đủ để hỏi HR/nghiệp vụ ở đợt khác.
- [x] **Hạng mục 3** (đã chọn: chỉ Approvals + Pipeline): thêm `RequirePermission(db, "Approvals", "view"/"act")` vào `/approvals/*` (`router.go`, `RegisterApprovalRoutes`) và `RequirePermission(db, "Pipeline", "view"/"run")` vào `/pipeline/*` (`internal/transport/http/pipeline/routes.go`). **Phát hiện quan trọng lúc thi hành**: `RequirePermission` mặc định ALLOW khi bảng `permissions` chưa có dòng nào cho module (mô hình opt-out, xem comment đầu `permission.go`) — nghĩa là KHÔNG cần seed migration nào, thêm middleware không đổi hành vi hiện tại của `hr_admin`/`cb_staff` (đúng TASK-REF), chỉ có tác dụng khi Admin sau này chủ động cấu hình qua tab "Ma trận quyền hạn". Sửa kèm 2 call site test có sẵn (`pipeline_route_test.go` — chữ ký `RegisterRoutes` đổi từ 3 xuống 5 tham số).
- [x] **Hạng mục 4** (ngưỡng đã chọn: 30 request/phút/user): thêm `golang.org/x/time/rate` (`go get`), viết `internal/middleware/rate_limit.go` (`RateLimitPerUser`, in-memory token bucket khoá theo `UserEmailKey`). Áp cho đúng 4 route đã quyết định: `Core System/cells/bulk-set/{periodId}`, `reports/{code}/export`, `reports/raw-export`, `hris/attendance-daily/sync` — KHÔNG áp `reports/Core System-summary`/`bank-transfer` (ngoài phạm vi đã chốt). Viết `internal/middleware/rate_limit_test.go` (2 test: chặn đúng ở request thứ N+1, cô lập theo từng user — user khác không bị ảnh hưởng). Sửa kèm 2 call site test có sẵn (`report/handler_test.go`, `admin_read_route_test.go` — chữ ký `report.RegisterRoutes` đổi từ 4 xuống 5 tham số).
- [x] **Hạng mục 5**: xác nhận — đã khảo sát ở bước Context, không còn bảng `_history` nào khác cần vá (chỉ `employee_history` + `salary_component_history`, cả 2 đã an toàn). Không sửa code.
- [x] Chạy lại `go test ./...` toàn bộ: **765 passed, 0 failed** (baseline 759/6 → 765/0 — không chỉ 0 hồi quy mà còn dọn sạch 6 fail cũ). `go build ./...`, `go vet ./...` sạch. `gofmt -l` xác nhận toàn bộ file đã sửa/tạo trong đợt này đều format sạch (drift gofmt còn lại trong repo là nợ cũ tiền tồn tại, không liên quan đợt này).
- [x] Cập nhật `self-docs/Handoff-Salary-Rule-Security-Configurability-200826.md` với kết quả thi hành.
- [x] Ghi 1 dòng vào "Nhật ký công việc theo ngày" (`CLAUDE.md`).
- [ ] **Chưa commit** — chờ user xác nhận trước khi commit + push lên `release/uat-180826`.

## Assumptions

- (default) Baseline test hiện tại là 759 pass/6 fail như đo gần nhất trong phiên — sẽ tự đo lại trước khi sửa.
- (default) Đóng Hạng mục 1 bằng Phương án A (allowlist) — khớp chủ ý thiết kế đã ghi rõ trong code, không cần hỏi thêm vì đây không phải quyết định nghiệp vụ mới mà là SỬA ĐÚNG phân loại test cho khớp thiết kế đã có.
- (default) Đóng Hạng mục 2 bằng Phương án A (test tích hợp, dùng `TEST_DATABASE_URL`) — khớp convention có sẵn của repo.
- (default) Đóng Hạng mục 5 bằng xác nhận (Phương án A) — kết quả khảo sát thật cho thấy không có việc gì thêm để làm.
- (default, find-out-later) Hạng mục 3/4 cần quyết định nghiệp vụ cụ thể — xem câu hỏi bên dưới, KHÔNG tự chọn.

## Self-review

1. **Phủ yêu cầu** — cả 5 hạng mục user chọn đều có mục Approaches + Plan tương ứng.
2. **Quét placeholder** — không còn `TBD`/`TODO` nào; các nhánh chưa quyết được đánh dấu rõ "[Chờ user quyết định]" thay vì để trống mơ hồ.
3. **Nhất quán tên** — dùng thống nhất `allowRoutesWithoutRoleGate`, `RequirePermission`, `dead_permission_audit_test.go`, `golang.org/x/time/rate` xuyên suốt.
