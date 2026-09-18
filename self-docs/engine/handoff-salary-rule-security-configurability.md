---
id: self-docs/engine/handoff-salary-rule-security-configurability
canonical_question: 'Technical guide and specification: Bàn giao context — Review
  bảo mật + phần "configurable" của rule/công thức lương'
aliases:
- Bàn giao context — Review bảo mật + phần "configurable" của rule/công thức lương
- Handoff Salary Rule Security Configurability 200826
entity_type: specification
domain: self-docs > engine
last_verified: 2026-09-17
---

# Bàn giao context — Review bảo mật + phần "configurable" của rule/công thức lương

**Ngày:** 20/08/2026 · **Mục đích:** context cho 1 session KHÁC (mở mới) tiếp tục việc review bảo mật + khả năng cấu hình (configurability) của hệ thống rule lương `salary_components`, trong khi session hiện tại tạm dừng chờ HR trả lời câu hỏi nghiệp vụ (xem cuối file). Session mới **không cần đọc lại toàn bộ lịch sử** — file này tóm tắt đủ để bắt đầu.

## 1. Việc đang làm ở session gốc (KHÔNG phải việc của session mới, chỉ để hiểu bối cảnh)

User đưa 1 file Excel HR (`Payroll_BRD_Tracker_Item.xlsx`) mô tả công thức lương thật, yêu cầu đối chiếu với DB `payroll_engine` (bảng `salary_components`). Kết quả: viết `self-docs/Core System-Formula-Excel-Reconciliation-190826.md` (báo cáo đối chiếu, liệt kê khớp/lệch/thiếu), rồi lên `/propose` cho từng cụm sửa (`llmwiki/wiki/sources/draft/190826-Core System-formula-rules-update.md` + `190826-Core System-ot-engine.md`). Hiện đang **tạm dừng chờ 19 câu hỏi HR/kế toán/Workday xác nhận** (phụ lục cuối file báo cáo) — chưa sửa DB/code nào, chỉ có SPEC/tài liệu. Session mới không cần làm tiếp việc này.

## 2. Việc session mới cần làm: review bảo mật + configurability của rule lương

### 2.1 Hai bảng cấu hình công thức — chỉ 1 bảng đang sống

- **`salary_components`** (148 dòng) — bảng "cây công thức" **đang được engine đọc thật** (dùng trong `internal/repository/salary_component_repo.go` và payroll_service.go). Đây là đối tượng chính cần review.
- **`salary_formula_configs`** (18 dòng, `scope_type=company, scope_id=CTC`) — **bảng mồ côi**: chỉ được `internal/database/database.go` tạo/seed lúc boot, **không có bất kỳ repo/handler nào đọc**. Dùng bộ mã khác hẳn (`SAL_BASE`, `GROSS_PAY`...) và số liệu luật cũ (giảm trừ 11tr/4.4tr, trần BHXH 36tr) — không khớp `salary_components`. Đã ghi nhận, chưa dọn. Nếu review bảo mật/config kiểm tra bảng này thì cần biết trước là nó KHÔNG ảnh hưởng hành vi tính lương thật, tránh mất công phân tích nhầm đối tượng.

### 2.2 Cơ chế versioning theo thời điểm (điểm mấu chốt phải hiểu trước khi review bất kỳ đường ghi nào)

Tài liệu canonical đầy đủ: `self-docs/Formula-Versioning-PointInTime-050826.md` — bắt buộc đọc trước.

Tóm tắt: mỗi lần sửa `formula`/`fixed_value` phải đi qua `InsertVersion` (`salary_component_repo.go:155`) để ghi vào bảng `salary_component_versions` (khoá theo `component_code`, `effective_until IS NULL` = version đang mở). Mục đích: kỳ lương quá khứ đã chốt vẫn tính đúng bằng công thức TẠI THỜI ĐIỂM đó, không bị công thức mới ghi đè ngược khi mở lại. **Đã từng có nhiều lỗ hổng tinh vi quanh cơ chế này** (self-heal migration ghi đè version âm thầm, seed làm version "đang mở" hết tác dụng khiến `salary_components.formula` thành code chết — xem mục L11/L12/L13 trong tài liệu trên) — review bảo mật/tính toàn vẹn nên đọc kỹ các mục đó, vì đây chính là loại lỗi "trông như đã sửa đúng nhưng số tính ra vẫn dùng công thức cũ, không cảnh báo gì".

### 2.3 Quyền truy cập (RBAC) hiện tại trên route sửa công thức

`internal/app/router.go:272-275` — 4 permission action riêng cho module `Settings.SalaryComponents`:
```go
requireSalaryComponentsView   := middleware.RequirePermission(db, "Settings.SalaryComponents", "view")
requireSalaryComponentsCreate := middleware.RequirePermission(db, "Settings.SalaryComponents", "create")
requireSalaryComponentsEdit   := middleware.RequirePermission(db, "Settings.SalaryComponents", "edit")
requireSalaryComponentsDelete := middleware.RequirePermission(db, "Settings.SalaryComponents", "delete")
```
Áp cho toàn bộ route `/salary-components/*` (`router.go:338-366`) và `/Core System-templates/*` (dùng chung permission này, không tách module riêng — xem comment dòng 382). Route sửa (`PUT /{id}`, `PUT /{id}/visible`, `DELETE /{id}`, override CRUD) đều có `requireSalaryComponentsEdit`/`Delete`. Có 1 route dev-only `GET /dev/component-as-of` (dòng 348) — cần xác nhận nó chỉ đăng ký khi `DEV_USER_EMAIL` set (không lộ ra prod) như comment nói.

**Chưa kiểm (việc của session mới):**
- Vai trò nào hiện đang thực sự được gán 4 permission action trên (bảng phân quyền thật — DB `role_permissions`/tương đương, tên bảng chính xác cần tự tra vì lần thử nhanh ở đây báo lỗi "relation không tồn tại", có thể do tên bảng RBAC khác, xem `self-docs/RBAC-Hybrid-Scoping-Implementation-140726.md` để biết đúng schema RBAC).
- Có kiểm soát/giới hạn nào cho việc AI/script gọi API sửa công thức hàng loạt không (rate limit, audit log riêng ngoài `salary_component_history`)?
- `salary_component_history` (audit log đổi formula, KHÔNG phải lịch sử lương nhân viên — dễ nhầm, xem session gốc đã nhầm điều này 1 lần) có ghi đủ `changed_by` cho mọi đường ghi không, hay có đường tắt (migration self-heal) ghi mà không qua log này?
- Endpoint `Validate` (`POST /salary-components/validate`) — kiểm công thức trước khi lưu — có chặn được injection/code lạ trong chuỗi `formula` không (đây là DSL công thức nội bộ, không phải SQL, nhưng vẫn nên xác nhận cách parse/eval an toàn, không cho phép gọi hàm tuỳ ý).
- Route `/reorder`, `/{id}/visible` chỉ đổi thứ tự/hiển thị — xác nhận chúng KHÔNG có đường tắt nào vô tình đổi luôn `formula` (kiểm handler `Reorder`/`ToggleVisible` trong `internal/handler/salary_component_handler.go`).

### 2.4 Configurability — mức độ "cấu hình được" thực tế của hệ thống

Từ khảo sát session gốc (khi làm cụm OT), phát hiện liên quan tới câu hỏi "hệ thống có configurable đủ không":
- Có những cấu hình **tưởng như configurable qua DB nhưng thực ra chưa nối dây** — ví dụ bảng `ot_multiplier_configs` (hệ số tăng ca) đã tồn tại với dữ liệu thật, nhưng KHÔNG component nào trong `salary_components` tham chiếu tới nó (đã kiểm — 0 kết quả), tức về mặt vận hành **hoàn toàn không ảnh hưởng số lương tính ra** dù nhìn vào DB tưởng đã có sẵn cấu hình. Đây là kiểu rủi ro "cấu hình ma" (config tồn tại, không ai đọc) — nên là 1 hạng mục review cụ thể: liệt kê bảng config nào trong `payroll_engine` KHÔNG có code nào SELECT từ nó (giống cách đã tìm ra `salary_formula_configs` mồ côi).
- Từng có 1 nhóm 8 component OT bị **migration xoá chủ ý** (`migrationSalaryComponentsV3`, comment "chưa cần tính") — nghĩa là hệ thống migration/seed có khả năng **âm thầm xoá cấu hình đang có** khi chạy migration mới; cần xác nhận cơ chế này (chạy tự động lúc boot hay chỉ 1 lần, có `DELETE FROM salary_components` vô điều kiện ở đâu khác không) không tạo rủi ro mất cấu hình HR đã tự chỉnh qua UI.
- Việc sửa Giai đoạn 1 (mục 3.3/3.10 báo cáo 190826) rốt cuộc đã xác nhận **giữ nguyên, không sửa** — tức phần lớn "sai lệch" hoá ra là chủ ý nghiệp vụ đúng, không phải lỗ hổng. Bài học cho review mới: đừng vội kết luận DB "cấu hình sai" chỉ vì khác Excel — luôn kiểm chứng đây có phải quyết định nghiệp vụ đã ghi chú (như trường hợp `OT_TAX=0`, xem `internal/database/database.go:2997`) trước khi báo là lỗi.

## 3. Tài liệu bắt buộc đọc trước khi review (theo đúng thứ tự)

1. `self-docs/Formula-Versioning-PointInTime-050826.md` — cơ chế versioning + các lỗ hổng đã tìm thấy (L1–L13).
2. `self-docs/Core System-Formula-Excel-Reconciliation-190826.md` — báo cáo đối chiếu Excel vs DB (mục 0 có phần "2 bảng, 1 bảng mồ côi"), phụ lục cuối có 19 câu hỏi đang chờ trả lời (không phải việc của review bảo mật, chỉ để biết bối cảnh).
3. `self-docs/RBAC-Hybrid-Scoping-Implementation-140726.md` — tài liệu canonical RBAC/company-scoping của repo, cần đọc để biết đúng schema bảng phân quyền trước khi tra role nào có quyền sửa `Settings.SalaryComponents`.
4. `internal/app/router.go` dòng 272-410 (route + permission gate của `/salary-components`, `/Core System-templates`).
5. `internal/handler/salary_component_handler.go` (toàn bộ — chỉ ~300 dòng, đọc hết không tốn nhiều).

## 4. Nhánh làm việc

Theo quy ước `CLAUDE.md` gốc repo: hạng mục bảo mật/phân quyền phải làm trên nhánh `sec_dev`. Trước khi sửa code, `cd Core System-backend && git branch --show-current` — nếu chưa ở `sec_dev` thì checkout/tạo nhánh đó. **Lưu ý:** phiên gốc hiện đang ở `release/uat-180826` (không liên quan) và không fetch được `origin/develop` do mất kết nối mạng lúc 19/08 — session mới nên tự `git fetch` trước khi tách nhánh để có ref mới nhất.

## 6. Kết quả đối chiếu 7 mục "chưa kiểm" (cập nhật 20/08/2026, verify bằng psql/grep thật trên `payroll_engine` dev + code repo `release/uat-180826`)

1. **Vai trò có 4 quyền `Settings.SalaryComponents`** — Chỉ **`cb_staff`** (C&B Staff) và **`hr_admin`** (HR Administrator) có `granted=true` đủ view/create/edit/delete (psql bảng `permissions`/`roles`). Role `config_admin` tồn tại nhưng **toàn bộ 6 action = false** — tên gợi ý có quyền config nhưng chưa được cấp gì, dễ hiểu nhầm nếu chỉ đọc tên role.
2. **Rate limit / audit log riêng cho sửa hàng loạt** — **Không có**: `grep -rniE "ratelimit|rate_limit" internal/middleware/ internal/app/router.go` = 0 kết quả. Audit chỉ có `salary_component_history` (`SaveHistory`) + `AuditLog` chung trong `Reorder`/`Delete`.
3. **`salary_component_history` có ghi đủ mọi đường ghi formula không** — **Còn rủi ro, đúng nghi ngờ trong doc**: `SaveHistory` (`repo.go:194-203`) luôn nhận `changed_by` khi gọi qua handler, NHƯNG các migration self-heal trong `database.go` (dòng 2890-3053, ví dụ `UPDATE salary_components SET formula = ... WHERE code = 'SI_CTY'`) **UPDATE trực tiếp bằng SQL thô, không gọi `SaveHistory` cũng không qua `InsertVersion`** — đường tắt này không để lại dấu vết trong audit log. Comment tại `database.go:362-376` tự thừa nhận đây từng gây bug thật (version cũ che formula mới nhiều đợt fix mà không ai biết — cùng họ lỗi với L11/L12/L13 ở `Formula-Versioning-PointInTime-050826.md`).
4. **Endpoint `Validate`** — **An toàn**: `Validate` → `service.Validate` → `engine.ValidateFormula` → `evalExpression` (`engine.go:280`) dùng parser recursive-descent tự viết, không `eval`/`govaluate`/reflection nào gọi hàm tuỳ ý; `go.mod` không có thư viện expression-eval nào.
5. **`/reorder`, `/{id}/visible`** — **An toàn**: `ReorderSeq` (`repo.go:314-329`) chỉ `UPDATE ... SET seq = $1`; `SetVisible` (`repo.go:188-192`) chỉ `UPDATE ... SET is_visible = $1`. Không chạm `formula`/`fixed_value`.
6. **Cấu hình ma khác ngoài `salary_formula_configs`** — **1 ca mới: `ot_multiplier_configs`**. Có repo riêng (`ot_multiplier_repo.go`) với `SELECT` thật từ bảng, nhưng `grep -rn "NewOtMultiplierRepo\|OtMultiplierRepo{"` trong `internal/` (ngoài file định nghĩa) = **0 kết quả** — không nơi nào khởi tạo/gọi repo này. Dữ liệu thật + code đọc thật nhưng không dây nối — cùng loại rủi ro như `salary_formula_configs`, khác lớp (repo mồ côi thay vì bảng mồ côi hoàn toàn). Các bảng `*_configs` khác đã kiểm (`allowance_configs`, `insurance_configs`, `leave_type_configs`, `system_config`, `payroll_period_config`) đều có ≥2 nơi gọi SELECT thật — chưa phát hiện thêm ca mồ côi ở nhóm này (chưa verify sâu từng cái, có thể còn sót).
7. **Migration xoá cấu hình — cơ chế + có DELETE vô điều kiện không** — **An toàn**: `migrationSalaryComponentsV3` (chứa `DELETE FROM salary_components WHERE code IN (...)`, dòng 2283) **đã bị vô hiệu hoá**, comment dòng 2262 ghi rõ "KHÔNG CÒN CHẠY". Các migration Go-const khác trong `RunMigrations()` chạy lại mỗi boot (tự idempotent qua WHERE-match, không qua bảng `schema_migrations`), còn 2 `DELETE FROM salary_components WHERE code = '...'` có điều kiện (dòng 3226, 3484, xoá đích danh 1 code/lần) vẫn chạy mỗi boot nhưng không vô điều kiện — không có `DELETE FROM salary_components;` trần nào trong repo.

**Việc còn mở sau đợt đối chiếu này — CẬP NHẬT 20/08/2026, đã xử lý theo SPEC `self-docs/Salary-Formula-Audit-Orphan-Config-Hardening-200826.md` (user duyệt):**
- **Mục 3 (audit gap) → ĐÃ VÁ.** Chọn Phương án A (chỉ ghi log, không đổi cơ chế ghi đè), nhưng cách triển khai đổi khác literal mô tả ban đầu sau khi phát hiện phạm vi thực tế lớn hơn (11 khối SelfHeal, không phải 1 khối): thay vì sửa tay từng khối, thêm **1 câu INSERT tổng quát** vào `MigrationSeedInitialComponentVersions` (`internal/database/database.go`, ~dòng 3346) tái dùng điều kiện đối chiếu `v.formula <> sc.formula` đã có sẵn — bắt được audit trail cho toàn bộ self-heal hiện tại + tương lai, chỉ sửa 1 vị trí. Verify thật trên bản clone dữ liệu dev (không đụng DB thật): cố ý tạo drift, chạy `RunMigrations`, xác nhận ghi đúng 1 dòng audit + không ghi trùng khi chạy lại lần 2. `go test ./...` giữ nguyên baseline 759 pass/6 fail (fail-list giống hệt, không liên quan). Chi tiết đầy đủ + bằng chứng: `self-docs/Salary-Formula-Audit-Orphan-Config-Hardening-200826.md` mục Plan. **Chưa commit** — chờ user xác nhận.
- **Mục 6 (`ot_multiplier_configs` mồ côi) → GIỮ NGUYÊN, chưa xử lý.** User chọn Phương án 3 (không xoá không nối dây đợt này) — vẫn là câu hỏi mở cần hỏi HR/nghiệp vụ xem đây là tính năng dở dang hay đã bỏ trước khi quyết định dọn hay hoàn thiện.
- Chưa verify sâu toàn bộ danh sách bảng `*_configs` khác trong schema — mới kiểm nhóm đã liệt kê ở trên.

**Phát hiện thêm ngoài phạm vi 2 việc trên (câu hỏi phụ của user 20/08/2026):** tính năng reports **đã có download file thật** (Excel `.xlsx`, không chỉ view) — 4 route ở `internal/transport/http/report/handler.go` (`GET /Core System-summary`, `GET /bank-transfer`, `POST /{code}/export`, `POST /raw-export`) dùng `excelize` trả file thật với `Content-Disposition: attachment`; frontend tách rõ `previewReport()` (xem trước, không tải) và `exportReport()` (nút Download riêng, tải `.xlsx` thật) ở `lib/api/reports.ts`/`ReportsRibbon.tsx`.

## 7. Test RBAC + reports end-to-end thật (20/08/2026) — trên `release/uat-180826`

Verify bằng cách boot backend thật trỏ vào **bản clone dữ liệu dev** (`pg_dump`/`pg_restore` DB tạm, xoá sạch sau khi xong — không đụng DB thật), dùng dev-bypass `Authorization: Bearer dev` + đổi role gán cho 1 email test qua `employee_roles` (không dùng chính `DEV_USER_EMAIL` để test hạn chế quyền — email đó LUÔN bị `EnsureSuperAdmins` ép thành super-admin ở mọi lần boot, không thể dùng để test role bị giới hạn).

**Sự cố môi trường tự phát hiện (không liên quan code, ghi lại để tránh lặp lại):** DSN kiểu `key=value` với `password=` để RỖNG (khi `DB_PASSWORD` không set) khiến kết nối Postgres cục bộ trên máy này lệch sang một backend/route khác (roles trả về sai — chỉ 2 mã lạ `debug_scope_role`/`site_admin` thay vì 6 mã thật) — **không tái hiện được khi dùng `-h`/`-U` dạng flag hoặc password thật khác rỗng**. Chưa xác định nguyên nhân gốc (nghi ngờ liên quan tới Docker Desktop hoặc PgBouncer proxy trên port 5432 của máy local này), nhưng đã né được bằng cách luôn dùng `payroll_app_role` + mật khẩu thật khi test thay vì `postgres` không mật khẩu.

**Kết quả xác nhận (đều bằng request thật, không suy đoán):**
- **Không role nào** → 403 ở mọi route (`/reports/*`, `/config/salary-components`).
- **`hr_admin`** → `GET /reports/catalog` 200 (VIEW đúng — danh mục 17 báo cáo); `GET /reports/bank-transfer?periodId=...` 200, file trả về là **Excel thật** (`file` xác nhận "Microsoft Excel 2007+"), mở `sharedStrings.xml` bên trong thấy **dữ liệu nhân viên thật** (tên, ngân hàng, số tài khoản, nội dung chuyển khoản — DOWNLOAD đúng nghĩa, không phải file rỗng/giả). `GET /config/salary-components` 200, trả đúng dữ liệu component thật.
- **`config_admin`** → `GET /config/salary-components` 403 — khớp đúng phát hiện tĩnh ở mục 6 (0/6 permission trên `Settings.SalaryComponents`).
- **`cb_staff`** → **phát hiện mới**: dù có `Reports.export=true` (và cả view/create/edit/delete=true) trong bảng `permissions`, **KHÔNG BAO GIỜ vào được bất kỳ route `/reports/*` nào** — bị chặn ở tầng ngoài `RequireRole("hr_admin")` cứng (comment `router.go:175` "Reports (HR Admin only)") TRƯỚC KHI tới được lớp `RequirePermission(Reports, export)`. Đây là "quyền ma" — cùng họ rủi ro với "cấu hình ma" (`ot_multiplier_configs`) đã tìm ở mục 6: dữ liệu quyền tồn tại trong DB, không sai kỹ thuật, nhưng không vai trò nào có thể thực sự dùng tới nó. Chưa rõ đây là chủ ý (chỉ hr_admin được xuất báo cáo, quyền `cb_staff` trên `Reports` chỉ tồn tại "phòng khi" hoặc để dùng cho module khác cùng tên) hay sai sót cấu hình — **cần hỏi lại nghiệp vụ/HR trước khi sửa**, không tự xoá quyền hay tự nới role gate.
- Đối chiếu với bộ test tự động sẵn có (`TestPermissionGateCoverageReport`, `TestG1AllProtectedRoutesRequireRoleGateExceptAllowlist` — bao phủ toàn bộ 241 route): 6 fail hiện tại đều thuộc `adapter-sync`/`payslip-sftp`, không liên quan `salary-components`/`reports` — 2 tính năng này đã có role-gate đầy đủ theo test tự động.

**Việc còn mở mới:** hỏi HR/nghiệp vụ xem quyền `Reports.export`/view/create/edit/delete=true đã gán cho `cb_staff` có phải "quyền ma" nên dọn, hay có ý định mở rộng route `/reports/*` cho `cb_staff` trong tương lai (nếu vậy phải sửa `RequireRole("hr_admin")` ở `router.go:176`).

## 8. Thi hành 5 hạng mục RBAC đã chọn (20/08/2026) — xem `self-docs/RBAC-Enhancement-Batch-200826.md` (SPEC + Plan đầy đủ)

Trên `release/uat-180826`, **chưa commit**:

1. **Đóng 4 route "unknown"** — thêm vào allowlist `router_role_gate_test.go`, khớp chủ ý thiết kế đã ghi sẵn trong code. Kết quả: `go test ./...` từ 759/6 fail → **765/0 fail** (dọn sạch cả 6 fail baseline).
2. **Audit "quyền ma" toàn hệ thống** — test mới `internal/app/dead_permission_audit_test.go`, chạy trên bản clone dữ liệu dev, bắt đúng lại case `cb_staff`/`Reports` + tìm thêm **35 case mới** (`cb_staff` trên hầu hết `Settings.*`, `Core System.approve`, `PayrollPeriods.edit`, `Companies.view`, `Departments.view`...; `config_admin`/`search_profile` trên `Employees.view`; `site_admin` trên 4 module Attendance) + **107 module.action "chưa nối dây"** (có permission trong DB nhưng code chưa từng kiểm module đó). Chỉ audit, chưa sửa quyền nào.
3. **Nâng fine-gate cho Approvals + Pipeline** — thêm `RequirePermission` cho 2 module mới, không cần seed migration nhờ cơ chế opt-out mặc định ALLOW của `RequirePermission` — không đổi hành vi hiện tại.
4. **Rate limit 30 req/phút/user** — middleware mới `internal/middleware/rate_limit.go` (in-memory, `golang.org/x/time/rate`), áp cho `cells/bulk-set`, `reports/{code}/export`, `raw-export`, `hris/attendance-daily/sync`.
5. **Audit trail** — xác nhận không còn bảng `_history` nào khác cần vá ngoài `salary_component_history` (đã xong ở Việc 1-A) và `employee_history` (đã an toàn sẵn).

Toàn bộ chi tiết + bằng chứng: `self-docs/RBAC-Enhancement-Batch-200826.md`.

## 5. Việc KHÔNG cần làm ở session mới

- Không cần trả lời/tiếp tục 19 câu hỏi HR đang chờ (thuộc việc đối chiếu công thức, không phải bảo mật).
- Không cần động vào `salary_formula_configs` (bảng mồ côi) trừ khi tự phát hiện nó gây rủi ro bảo mật thật (ví dụ lộ số liệu qua API nào đó) — nếu chỉ là dọn dẹp thì đó là việc khác, ghi nhận riêng.
- Không tự sửa cấu hình `ot_multiplier_configs`/component OT — đó thuộc phạm vi cụm OT đang chờ HR ở session gốc.
