---
id: self-docs/database/db-cleanup-legacy-tables
canonical_question: 'Technical guide and specification: DB Cleanup — Xoá bảng legacy
  không còn dùng'
aliases:
- DB Cleanup — Xoá bảng legacy không còn dùng
- DB Cleanup Legacy Tables 170826
entity_type: how_to
domain: self-docs > database
last_verified: 2026-09-17
---

# DB Cleanup — Xoá bảng legacy không còn dùng (170826)

> ⚠️ **Triển khai:** backend KHÔNG chạy Atlas — các migration của đợt này phải `atlas migrate apply`
> bằng tay, và **bắt buộc deploy code TRƯỚC khi apply**. Xem `self-docs/DB-Cleanup-Deploy-Runbook-180826.md`.

**Trạng thái:** Đã thi hành, chưa merge vào `develop`/`feature_v2`.
**Nhánh:** `Core System-backend@chore/db-cleanup-legacy-tables` (tạo từ `origin/develop`).
**Tài liệu nguồn:** `llmwiki/wiki/sources/draft/170826-db-cleanup-legacy-tables.md` (SPEC) +
`170826-db-cleanup-legacy-tables-PLAN.md` (PLAN thi hành).

## Bối cảnh

User yêu cầu rà soát bảng có tiền tố `hris_` xem bảng nào còn dùng/bảng nào là dữ liệu cũ, với
điều kiện: nếu cần sửa code thì chuyển sang nhánh mới, không đụng `feature_v2` đang mở merge vào
`develop`. Sau đó phạm vi được mở rộng theo yêu cầu tiếp theo của user thành rà soát **toàn bộ
107 bảng** trong DB (không chỉ `hris_*`), đối chiếu cả 3 repo (`Core System-backend`,
`Core System-frontend`, `Core System-adapter`).

## Phương pháp — 2 vòng, có một lỗi tự bắt được giữa chừng

**Vòng 1** (chỉ 6 bảng `hris_*`): grep thủ công từng bảng trên `Core System-backend`.

**Vòng 2** (toàn bộ 107 bảng, sau khi user yêu cầu mở rộng): quét tự động bằng grep tên bảng
qua mọi file Go/TS không phải test, loại trừ `internal/db/schema.sql` và `internal/db/gen/`
(code sinh bởi `sqlc`, xác nhận **không package nào import** `internal/db/gen` — chết hoàn toàn
bất kể bảng có dùng hay không).

**Lỗi tự bắt được:** lần quét đầu của Vòng 2 chạy trên nhánh `chore/db-cleanup-legacy-tables`
(dựa trên `develop`) và báo sai `report_templates`/`report_template_lines`/
`template_component_versions` là "0 code dùng" — thực ra code của 3 bảng này (tính năng cấu hình
báo cáo, xây dựng 060826) chỉ tồn tại trên `feature_v2`, **chưa merge vào `develop`** tại thời
điểm quét. Đã dựng lại `git worktree` từ `feature_v2` (nhánh đầy đủ nhất — đã hấp thụ toàn bộ
`develop` qua rebase trước đó) để quét lại cho đúng.

**Bẫy thứ hai đã lường trước:** một bảng "có code chạm tới" chưa chắc là dùng thật — nếu chỉ có
đúng một dòng `CREATE TABLE IF NOT EXISTS` trong `database.go` mà không repository/service/handler
nào đọc/ghi thì vẫn là code chết. Áp cách kiểm này lên `payroll_record_allowances` (bảng có FK từ
`allowance_items`) phát hiện nó **cũng chết hoàn toàn** — nhưng KHÔNG đưa vào phạm vi xoá đợt này
(ghi thành Non-goal trong SPEC, để tránh phình phạm vi phút chót).

## Kết quả: 10 bảng xoá, 1 bảng giữ lại có chủ đích

### Nhóm A — 0 dòng dữ liệu, xoá thẳng không cần backup
- `hris_oauth_tokens`
- `hris_payroll_reports`
- `ref_hospitals` (có FK **trỏ vào** từ `employees.ref_hospital_id`, cột 100% NULL — xác nhận
  trước khi viết migration — dùng `CASCADE` để tự gỡ đúng constraint đó, không đụng cột/dữ liệu
  khác của `employees`)

### Nhóm B — có dữ liệu thật, backup `pg_dump --table --data-only --column-inserts` trước khi xoá
| Bảng | Số dòng | File backup |
|---|---|---|
| `hris_payroll_snapshots` | 2 | `self-docs/files/db-cleanup-170826-hris_payroll_snapshots.sql` |
| `hris_payroll_detail_snapshots` | 2 | `self-docs/files/db-cleanup-170826-hris_payroll_detail_snapshots.sql` |
| `hris_allowance_override` | 2140 | `self-docs/files/db-cleanup-170826-hris_allowance_override.sql` |
| `allowance_overrides_bak_20260624` | 1302 | `self-docs/files/db-cleanup-170826-allowance_overrides_bak_20260624.sql` |
| `allowance_items` | 58 | `self-docs/files/db-cleanup-170826-allowance_items.sql` (có FK **trỏ vào** từ `payroll_record_allowances.allowance_item_id`, bảng 0 dòng — `CASCADE`) |
| `allowance_types` | 5 | `self-docs/files/db-cleanup-170826-allowance_types.sql` |
| `employee_change_requests` | 21 | `self-docs/files/db-cleanup-170826-employee_change_requests.sql` |

Số dòng INSERT trong mỗi file backup đã đối chiếu khớp tuyệt đối với số dòng đo trước khi xoá.

### Giữ lại có chủ đích
- **`hris_districts`** (758 dòng) — **không có code nào dùng**, nhưng theo quyết định trực tiếp
  của user ("hris_districts giữ lại") vẫn giữ nguyên, không nằm trong migration.

## Thi hành

1. **Task 1 (GATE):** đo baseline `go test ./... -p 1` = 917 passed / 9 failed (đã biết trước,
   không liên quan); backup 7 bảng Nhóm B.
2. **Task 2:** migration `atlas/migrations/20260817000000_drop_legacy_tables.sql` — thứ tự xoá
   tôn trọng FK con→cha (`hris_payroll_detail_snapshots` trước `hris_payroll_snapshots`,
   `allowance_items` trước `allowance_types`). Preview bằng `BEGIN;...ROLLBACK;` trước — xác nhận
   đúng 2 dòng `NOTICE: drop cascades to constraint ...`
   (`payroll_record_allowances_allowance_item_id_fkey`, `employees_ref_hospital_id_fkey`), không
   có notice nào khác. Áp dụng thật sau khi xác nhận qua `AskUserQuestion`. Sau khi áp dụng:
   0 dòng ở cả 10 bảng, `hris_districts` còn nguyên 758 dòng, 9 bảng `hris_%` còn lại
   (`hris_attendance_daily`, `hris_connectors`, `hris_districts`, `hris_night_meal`,
   `hris_provinces`, `hris_regions`, `hris_timesheets`, `hris_transport_config`,
   `hris_transport_l6_override`). `atlas.sum` re-hash qua `atlas migrate hash`.
3. **Task 3:** `internal/database/database.go` — xoá 2 khối `const` (`migrationHRISPayrollSnapshots`,
   `migrationHRISPayrollDetailSnapshots`) và 2 dòng gọi trong `RunMigrations()`. Bắt buộc vì cả
   hai bảng được tạo lại bằng `CREATE TABLE IF NOT EXISTS` **mỗi lần backend boot** — nếu không
   sửa, migration DROP ở Task 2 sẽ bị vô hiệu ngay ở lần restart kế tiếp. Xác nhận bằng cách
   restart backend thật (`go run ./cmd/Core System`) và kiểm `psql` — 2 bảng không tái xuất hiện.
4. **Task 4:** đồng bộ `internal/db/schema.sql`. File gốc được `pg_dump` từ PostgreSQL **16.14**
   (môi trường khác, có thể staging), trong khi máy local chạy PostgreSQL **14.18** — chạy lại
   `pg_dump --schema-only` tại local tạo ra diff ~3652 dòng nhiễu không liên quan (khác version
   dump-tool, khác `SET` statement, khác annotation `Owner:`). Đã đổi sang cách **xoá thủ công
   theo khối** bằng script Python ghép cặp comment-header (`-- Name: ...`) với câu SQL đứng sau nó
   (pg_dump tách 2 phần này bằng dòng trống nên chúng là 2 "chunk" riêng khi split theo `\n\n`) —
   giữ nguyên toàn bộ định dạng/metadata gốc của file, chỉ xoá đúng khối liên quan tới 10 bảng
   (TABLE, SEQUENCE, SEQUENCE OWNED BY, DEFAULT, PRIMARY KEY/UNIQUE CONSTRAINT, INDEX, và 2 khối
   FK CONSTRAINT tham chiếu chéo). Xác nhận: 0 dòng còn nhắc tên cả 10 bảng, `hris_districts`
   không đổi, `employees`/`payroll_record_allowances` (2 bảng bị CASCADE gỡ FK) vẫn còn nguyên
   là bảng — diff cuối cùng: **487 dòng xoá, 0 dòng thêm**, không đụng dòng nào ngoài phạm vi.
5. **Task 5:** `internal/db/tables_db.md` — xoá đúng 10/10 mục `### <bảng> (N cols)` tương ứng
   (87 mục còn lại từ 97, `hris_districts` còn nguyên).
6. **Task 6 (tài liệu, đang làm — file này):** viết doc canonical, cập nhật `document-map.md`,
   append nhật ký `CLAUDE.md`.
7. **Task 7 (còn lại):** chạy lại `go test ./... -p 1` đối chiếu baseline Task 1, `go build`/`go vet`.

## Commit

Trên `Core System-backend@chore/db-cleanup-legacy-tables` (chưa push, chưa merge):
- `032a7c2` — chore(db): xoá 10 bảng DB không còn dùng (170826) [migration]
- `672dc06` — chore(db): xoá code tạo lại hris_payroll_snapshots/hris_payroll_detail_snapshots mỗi boot (170826)
- `1c633b1` — chore(db): xoá định nghĩa 10 bảng legacy khỏi schema.sql
- `84d0565` — chore(db): xoá 10 mục bảng legacy khỏi tables_db.md

## Việc KHÔNG làm (Non-goals, ghi trong SPEC)

- Không xoá `payroll_record_allowances` dù xác nhận là code chết — ngoài phạm vi rà soát này,
  cần quyết định riêng.
- Không xoá cột `employees.ref_hospital_id` — chỉ gỡ đúng FK constraint trỏ tới `ref_hospitals`.
- Không merge nhánh này vào `develop`/`feature_v2` — để user tự quyết định thời điểm.
