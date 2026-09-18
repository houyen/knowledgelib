---
id: self-docs/database/atlas-migration-flow-removal
canonical_question: 'Technical guide and specification: Bỏ luồng Atlas, chỉ dùng 1
  luồng migrate duy nhất — 310826'
aliases:
- Bỏ luồng Atlas, chỉ dùng 1 luồng migrate duy nhất — 310826
- Atlas Migration Flow Removal 310826
entity_type: how_to
domain: self-docs > database
last_verified: 2026-09-17
---

# Bỏ luồng Atlas, chỉ dùng 1 luồng migrate duy nhất — 310826

## Bối cảnh

User hỏi khảo sát "tìm các luồng migrate trong repo Backend" — phát hiện backend có **3 luồng
migrate song song**:

1. **Boot-time auto-migrate** (`cmd/Core System/main.go`) — `database.RunMigrations` (khối tự-hồi
   luôn chạy) + `database.RunFileMigrations` (embed `migrations/*.sql`, tracked qua bảng
   `schema_migrations`). Đây là luồng THẬT chạy mọi môi trường không qua Docker.
2. **Atlas** (`atlas.hcl` + `atlas/migrations/*.sql`, 41 file) — ban đầu tưởng chỉ là bookkeeping
   khai báo (diff/lint), nhưng phát hiện `docker-entrypoint.sh` (sửa 300826, MỚI hơn nhật ký gần
   nhất) đã chạy thật `atlas migrate apply --env prod` trước khi start server trong container
   Docker — tức là luồng migrate THẬT thứ 2 trên production.
3. `migrations/apply.sh` — script fallback cũ, không còn cần dùng.

User xác nhận: **xoá luồng Atlas, chỉ giữ luồng (1)**.

## Phát hiện quan trọng trước khi xoá

Atlas không chỉ là tooling thừa — nó là nơi DUY NHẤT tạo ra một khối lượng lớn schema đang được
dùng thật, chưa từng được port sang luồng (1):

- **approval_requests / approval_rules / approval_steps** — toàn bộ approval engine (duyệt bảng
  lương 2 cấp, duyệt công thức lương).
- **wd_organizations / wd_cost_centers** — sync tổ chức/ngày lễ Workday (`internal/service/
  adapter_sync_organization.go`, `adapter_org_holiday_merge.go` đã đọc/ghi 2 bảng này).
- **salary_component_pending_changes** — luồng duyệt sửa/tạo công thức cột lương.
- **adapter_sync_state** — bản thân TABLE chỉ được tạo ở atlas; 2 file `migrations/v59_*`/`v60_*`
  đã có sẵn trong luồng (1) lại là `ALTER TABLE` giả định bảng đã tồn tại → sẽ tự vỡ trên DB chưa
  từng chạy atlas apply.
- **Toàn bộ RBAC hybrid scoping**: `roles.parent_role_id`, `roles.priority`,
  `employee_roles.scope_company_code/scope_department_id/scope_company_id` (+ 2 FK),
  `employee_roles.email` (+ backfill + trigger `employee_roles_fill_email` + unique
  `(email, role_id)` + đổi `employee_id` sang nullable/`ON DELETE SET NULL`),
  `employees.hris_id` (backfill + NOT NULL + DEFAULT), `employees.hris_portal_employee_code`
  (vá IDOR route ESS proxy), `companies.hris_id` (+ đổi kiểu uuid→varchar), RLS trên `employees`
  (`ENABLE/FORCE ROW LEVEL SECURITY` + policy `employees_company_scope`).
- Seed dữ liệu: `role_permission_matrix_seed`, `employees_permission_seed`,
  `hr_admin_new_accounts_seed`, `payroll_record_approval` (cột + permission `Core System.approve`),
  index/CHECK constraint `salary_components_db_hardening`.

Đối chiếu với DB dev thật (`payroll_engine`) xác nhận: dev **cũng đang thiếu** `wd_organizations`/
`wd_cost_centers` (atlas migration viết ra nhưng chưa từng apply ở đây) — tức là ngay cả trước khi
xoá, atlas đã không được áp dụng nhất quán giữa các môi trường.

Đã kiểm loại trừ: các migration atlas khác (PIT system→formula, salary_component_versions,
employee_payroll_templates, approval_deadline_columns, payroll_record_versions,
attendance_department_segments_add_company_ref, attendance_summary_drop_stale_unique,
salary_components_cc_backfill dạng đã ghi đè, v46 override value...) **đã được port/duplicate**
vào luồng (1) từ trước (đánh dấu bằng comment "Trùng nội dung với atlas/migrations/...") hoặc đã bị
supersede bởi các block tự-hồi mới hơn — không cần port lại.

Các migration atlas thuần DROP (dọn bảng/cột chết đợt 170826-180826) — **không port**: đây là
one-time cleanup đã áp dụng trực tiếp qua `psql` lên các DB thật theo đúng nhật ký ngày đó, và
luồng (1) chỉ cộng thêm (self-heal luôn `CREATE TABLE IF NOT EXISTS`/`ADD COLUMN IF NOT EXISTS`),
không bao giờ tự DROP — các khối tạo-đối-tượng-đã-chết tương ứng trong `database.go` cũng đã được
gỡ ở đúng các đợt dọn dẹp đó, nên một DB mới dựng từ luồng (1) không bao giờ tạo lại chúng.

## Thi hành

**19 file migration mới** `Core System-backend/migrations/v70_*.sql` .. `v88_*.sql` — copy nguyên văn
nội dung SQL từ atlas file tương ứng vào luồng (1) (chạy 1 lần, tracked theo tên file qua
`schema_migrations`), giữ đúng thứ tự phụ thuộc (bảng tạo trước khi ALTER, `adapter_sync_state`
trước 2 seed 'organization'/'holiday_calendar'/'company', `employee_roles.email` trước
`hr_admin_new_accounts_seed`...). 2 chỗ phải sửa thêm guard trước khi copy (bản gốc không idempotent
theo kiểu re-run, an toàn cho tracked-once nhưng cần an toàn khi DB ĐÍCH đã có sẵn đối tượng do
atlas tạo từ trước):

- `v79_salary_components_db_hardening.sql`: bọc `ADD CONSTRAINT chk_salary_components_config_table`
  trong `DO $$ ... IF NOT EXISTS (SELECT 1 FROM pg_constraint ...)` (Postgres không có
  "ADD CONSTRAINT IF NOT EXISTS").
- `v73_employees_row_level_security.sql`: thêm `DROP POLICY IF EXISTS employees_company_scope`
  trước `CREATE POLICY` (Postgres không có "CREATE POLICY IF NOT EXISTS").

**Xoá plumbing Atlas**: `atlas.hcl`, thư mục `atlas/migrations/` (41 file), stage `atlas` +
3 dòng COPY trong `Dockerfile`, `docker-entrypoint.sh` (CMD đổi thẳng về `["./Core System"]`),
`Makefile` targets `atlas-diff`/`atlas-lint`/`atlas-check`, `scripts/atlas-check.sh`,
`.githooks/pre-commit` (dẫn tới thư mục `.githooks` rỗng, tự biến mất), hook atlas trong
`.claude/settings.json` (PostToolUse). Sửa comment đầu `internal/db/schema.sql` ("single source
of truth for Atlas + sqlc" → "for sqlc") và 3 chỗ comment trong `database.go` (mốc CD/CE/CF) từng
nói "trùng nội dung với atlas/migrations/X, giữ file atlas để đối chiếu tooling" — nay atlas file
không còn, bỏ phần trỏ tới file đã xoá.

## Xác minh

- **Build/vet/test**: `go build ./...`, `go vet ./...` sạch; `go test ./...` **843 passed / 0
  failed** (baseline trước đổi không có regression — thay đổi chỉ là SQL file mới + xoá
  config/script, không đụng logic Go nào).
- **Xác minh migrate mechanics thật** (không chỉ đọc code): dựng DB test bằng `pg_dump`/`pg_restore`
  full (schema + data trọng yếu: `roles`/`permissions`/`companies`/`schema_migrations`, loại trừ
  bảng `employees` và các bảng con FK theo nó để né RLS/FK-chain) từ DB dev thật
  `payroll_engine`, rồi **xoá thủ công đúng 7 bảng + toàn bộ cột/constraint/trigger/policy mà
  atlas từng tạo** (mô phỏng "môi trường chưa từng chạy atlas apply"), sau đó chạy trực tiếp
  `database.RunFileMigrations` (qua 1 `cmd/` tạm, xoá sau khi xong) trên DB đó:
  - Lần 1: cả 19 file `v70-v88` chạy sạch, 0 lỗi.
  - Lần 2 (xoá lại record `schema_migrations` rồi chạy lại): **idempotent xác nhận** — chạy lại
    trên DB đã có sẵn đối tượng, 0 lỗi (đúng mục đích 2 chỗ vá guard ở trên).
  - Đối chiếu `\d employee_roles` sau khi chạy: khớp **tuyệt đối** với schema thật trên dev DB
    (cột, FK, unique constraint, trigger).
  - Đối chiếu số bảng: DB test sau migrate = 85, dev thật = 83 — chênh đúng 2 bảng
    (`wd_organizations`/`wd_cost_centers`, dev thật cũng đang thiếu do atlas chưa từng áp dụng ở
    đó) — xác nhận luồng mới không thiếu, thậm chí bù được phần dev đang hụt.
  - Phát hiện phụ (không sửa, ngoài phạm vi): `database.RunMigrations` (khối tự-hồi luôn chạy,
    KHÔNG liên quan gì tới việc xoá atlas) có bug thứ tự tiền tồn tại — chạy trên DB HOÀN TOÀN
    TRỐNG lỗi `relation "insurance_configs" does not exist` ở migration thứ 83 trong list. Khớp
    đúng giới hạn đã tài liệu hoá sẵn ("CHỈ hỗ trợ DB đã có dữ liệu, không bootstrap từ đầu") —
    không phải lỗi do việc này gây ra, không sửa.
- Dọn sạch: xoá DB test, xoá thư mục `cmd/migrate-fresh-test` tạm, xoá file dump/scratch —
  `git status` sau khi xong chỉ còn đúng các thay đổi thật của việc này (không dính rác test).

## Trạng thái git

Nhánh `chore/remove-atlas-migration-flow` (tách từ `develop_v1`) — **chưa commit, chưa push**.
`git add -A` cho thấy: 7 file mới thật (A), 36 file xoá (D, chủ yếu `atlas/migrations/*`), 4 file
sửa (`Dockerfile`, `Makefile`, `internal/database/database.go`, `internal/db/schema.sql`), 12 cặp
git tự nhận diện là "rename" (nội dung atlas file cũ trùng phần lớn với file `migrations/v*` mới,
chỉ là git heuristic — về bản chất đây là port sang file mới, không phải rename thật).

## Quyết định còn lại chưa chốt (không thuộc phạm vi việc này)

- File `internal/db/schema.sql` hiện đã LỆCH so với DB thật cả về phía "thiếu 10 bảng + 10 cột"
  (ghi nhận từ 180826) LẪN các cột RBAC/approval/wd_* vừa port ở đây (chưa `pg_dump` lại để đưa
  vào `schema.sql`, vì việc đó cần Postgres 16 qua Docker — xem ghi chú cũ ở đầu file và
  `00-START-HERE.md` mục 3.5). File này vẫn dùng cho sqlc, không ảnh hưởng runtime.
- Không port RLS sang bảng nào khác ngoài `employees` (đúng phạm vi gốc quyết định 150726 — chỉ
  áp cho bảng nhiều PII nhất).
