---
id: self-docs/engine/db-cleanup-deploy-runbook
canonical_question: 'Technical guide and specification: Runbook triển khai — dọn dẹp
  DB 170826 + 180826'
aliases:
- Runbook triển khai — dọn dẹp DB 170826 + 180826
- DB Cleanup Deploy Runbook 180826
entity_type: runbook
domain: self-docs > engine
last_verified: 2026-09-17
---

# Runbook triển khai — dọn dẹp DB 170826 + 180826

**Áp dụng cho:** nhánh `Core System-backend@chore/db-cleanup-legacy-tables` (4 đợt dọn 170826 + F1/F3
của review 180826). 7 migration: `atlas/migrations/2026081700*` (6) + `20260818000000` (1).

**Nguồn:** `self-docs/Review-DB-Cleanup-Workday-Bridge-180826.md` §F4.
**Số liệu kiểm chứng:** replay toàn bộ 7 migration trên bản sao dump prod `payroll_engine_1708`.

---

## 1. Sự thật nền — ĐỌC TRƯỚC KHI LÀM BẤT CỨ GÌ

**Backend KHÔNG chạy Atlas.** Ghi rõ tại `internal/database/database.go:2912`.
`cmd/Core System/main.go` khi `AUTO_MIGRATE=true` chỉ chạy đúng 2 thứ:

1. `database.RunMigrations(db)` — chuỗi hằng Go trong `internal/database/database.go`,
   `CREATE TABLE IF NOT EXISTS ...`, chạy lại mỗi lần khởi động.
2. `database.RunFileMigrations(db, baseline)` — `migrations/v*.sql` nhúng, track theo TÊN FILE
   trong bảng `schema_migrations`.

Toàn bộ `atlas/migrations/*.sql` nằm NGOÀI hai đường đó ⇒ **phải chạy `atlas migrate apply` bằng tay.**

## 2. THỨ TỰ BẮT BUỘC

> **Deploy code TRƯỚC. Apply migration SAU. Không được đảo.**

Nếu apply migration trong khi bản code CŨ vẫn đang chạy, thì ở lần khởi động lại kế tiếp
`RunMigrations` sẽ **tạo lại 15 bảng vừa xoá** (rỗng, nhưng schema quay về trạng thái cũ):

```
sync_errors                    employee_insurance_salaries    shift_configs
attendance_items               leave_budgets                  leave_budget_details
leave_requests                 overtime_records               payroll_table_configs
payroll_record_allowances      payroll_record_ot_details      hris_payroll_snapshots
hris_payroll_detail_snapshots  salary_history                 job_rotation_types
```

Bản code trên nhánh này đã gỡ hết 15 khối `CREATE TABLE IF NOT EXISTS` đó
(commit `032a7c2`, `672dc06`, `eb53934`, `78d32d9`) — nên chỉ cần deploy trước là an toàn.

**Đã kiểm chứng:** khởi động server bản nhánh này trên bản sao DB dev đã dọn (79 bảng) →
sau khi `RunMigrations` chạy xong vẫn đúng **79 bảng**, không bảng nào tái sinh.

## 3. Quy trình

### B0 — Sao lưu (bắt buộc)
```bash
pg_dump -h <host> -U <user> -d <db> -Fc -f Core System-pre-cleanup-$(date +%Y%m%d%H%M).dump
```

### B1 — Deploy code
Đưa bản build của nhánh này lên trước. Xác nhận service khởi động sạch
(`Database migrations completed successfully` trong log) rồi mới sang B2.

### B2 — Apply migration

> ### ⛔ KHÔNG dùng `atlas migrate apply` trên UAT/production
>
> **Đo thật 180826 trên bản sao dump prod:** bảng revision của Atlas trên prod chỉ ghi nhận **2**
> mục — `20260612000000 baseline` và `20260812000000 add_employee_roles_email` (mục thứ hai
> **không khớp file nào trong repo**). Trong khi thư mục migration có 32 file. Chạy
> `atlas migrate status` cho ra:
>
> ```
> Migration Status: PENDING
>   -- Current Version: 20260812000000
>   -- Executed Files:  2
>   -- Pending Files:   30 (21 out of order)
>   ERROR: migration files ... were added out of order.
> ```
>
> Nghĩa là **Atlas sẽ TỪ CHỐI chạy**, và kể cả có ép chạy thì nó sẽ thử áp 30 migration mà phần lớn
> đã được apply tay từ trước → lỗi "already exists" hoặc áp dụng nửa vời. Trên thực tế **prod không
> dùng Atlas làm cơ chế migration** — mọi thứ được apply bằng tay.
>
> Việc dọn dẹp lại lịch sử revision của Atlas trên prod là một task riêng, **ngoài phạm vi** đợt này.

**Cách đúng: apply từng file bằng `psql`, đúng thứ tự, trong MỘT transaction.**

Kiểm điều kiện trước — migration `20260817020000` cần bảng `adapter_sync_state` đã tồn tại:
```sql
SELECT to_regclass('public.adapter_sync_state');   -- NULL nghĩa là chưa có
```
Nếu `NULL` thì phải apply `20260813000000_adapter_sync_state.sql` trước. (Trên dump prod 17/08 nó
**chưa có** — migration đó chưa từng chạy trên prod.)

Kiểm hai điều kiện trước:
```sql
SELECT to_regclass('public.adapter_sync_state');   -- NULL -> phải apply 20260813000000 trước
SELECT to_regclass('public.approval_requests');    -- NULL -> phải apply 20260724000000 trước
```
Trên dump prod 17/08 **cả hai đều NULL**. Riêng `approval_*` là lỗi tiền tồn tại: `origin/develop`
đã có sẵn `approval_repo.go`/`approval_service.go` và 2 route `/approvals`, `/admin/approval-rules`
nhưng 3 bảng chưa từng được tạo trên prod — nghĩa là 2 route đó đang hỏng sẵn. Vá luôn trong đợt này
theo xác nhận của người dùng (180826).

**Toàn bộ 11 file, một transaction, đúng thứ tự này:**
```bash
cd Core System-backend
psql -d "$DATABASE_URL" -v ON_ERROR_STOP=1 <<'SQL'
BEGIN;
\i atlas/migrations/20260724000000_approval_engine.sql               -- chỉ khi to_regclass ra NULL
\i atlas/migrations/20260813000000_adapter_sync_state.sql            -- chỉ khi to_regclass ra NULL
\i atlas/migrations/20260817000000_drop_legacy_tables.sql
\i atlas/migrations/20260817010000_drop_education_ref_tables.sql
\i atlas/migrations/20260817020000_adapter_sync_state_worker_transfer_event.sql
\i atlas/migrations/20260817030000_drop_employees_ref_provinces_columns.sql
\i atlas/migrations/20260817040000_drop_standalone_tables_group_a.sql
\i atlas/migrations/20260817050000_drop_dependent_tables_group_b.sql
\i atlas/migrations/20260817060000_drop_dead_fk_columns_group_c.sql
\i atlas/migrations/20260818000000_drop_orphan_fk_columns.sql
\i atlas/migrations/20260818010000_drop_prod_legacy_tables.sql       -- 43 bảng di sản, đưa prod = dev
COMMIT;
SQL
```

Chạy thử một lượt với `ROLLBACK;` thay cho `COMMIT;` trước, đọc kỹ NOTICE, rồi mới chạy thật.
`DROP TABLE`/`DROP COLUMN` của PostgreSQL đều nằm trong transaction được, nên hoặc ăn cả hoặc
không gì cả.

Kỳ vọng: **đúng 4 NOTICE** — tất cả đều là `drop cascades to constraint` đã ghi sẵn trong comment
của migration:
```
payroll_record_allowances_allowance_item_id_fkey
employees_ref_hospital_id_fkey
employee_bank_accounts_ref_bank_id_fkey
employee_dependents_ref_relation_type_id_fkey
```
**Bất kỳ NOTICE nào khác 4 cái trên ⇒ DỪNG, không tiếp tục, khôi phục từ B0.**

### B3 — Kiểm sau apply
```sql
SELECT count(*) FROM information_schema.tables
  WHERE table_schema='public' AND table_type='BASE TABLE';                 -- xem §3b
SELECT count(*) FROM information_schema.columns WHERE table_name='employees';           -- 228 → 211
SELECT count(*) FROM information_schema.columns WHERE table_name='org_structures';      -- 61  → 58
SELECT count(*) FROM information_schema.columns WHERE table_name='employee_educations'; -- 30  → 24
SELECT count(*) FROM employees;                                            -- KHÔNG ĐỔI (12.304 ở prod 17/08)
```
Xem §3b cho số bảng đích. Ba con số cột và số dòng `employees` thì tuyệt đối, không tuỳ môi trường.

### B3b — Số bảng đích: **79**, bằng đúng dev

Diễn tập đủ chuỗi (deploy code merged → apply migration) trên bản sao `payroll_engine_1708`:

Diễn tập đủ chuỗi trên bản sao dump prod, chạy thật 18/08:

| Mốc | Số bảng |
|---|---|
| Dump prod 17/08, nguyên trạng | **146** |
| Sau khi boot code đã merge — `RunMigrations` tự tạo 4 bảng của `feature_v2` (`employee_payroll_templates`, `report_templates`, `report_template_lines`, `template_component_versions`) | **150** |
| Sau khi apply 11 migration ở §B2 | **79** |

Phép tính: `146 + 4 + 3 (approval_*) + 1 (adapter_sync_state) − 32 (đợt dọn) − 43 (di sản) = 79`.

**Danh sách bảng khớp GIỐNG HỆT DB dev `payroll_engine` (79 bảng) — `diff` ra rỗng.**

Dữ liệu nghiệp vụ nguyên vẹn tuyệt đối, đếm trước/sau:

| Bảng | Trước | Sau |
|---|---|---|
| `employees` | 12.304 | 12.304 |
| `employee_contracts` | 25.865 | 25.865 |
| `employee_work_histories` | 76.856 | 76.856 |
| `employee_bank_accounts` | 10.700 | 10.700 |
| `employee_dependents` | 24.530 | 24.530 |
| `employee_educations` | 7.742 | 7.742 |
| `org_structures` | 892 | 892 |
| `payroll_records` | 6.435 | 6.435 |

Khởi động lại backend trên DB đã dọn **3 lần**: vẫn đúng 79 bảng, **không bảng nào tái sinh**.
Kiểm route: `/ref/education-levels` → 200 kèm dữ liệu, `/ref/provinces` → 404 `unknown ref table`,
`/adapter-sync/state` → 200 trả mảng 2 entity (`worker`, `worker_transfer_event`).

### B4 — Kiểm ứng dụng
```bash
curl -H "Authorization: Bearer <token>" <host>/api/v1/ref/education-levels   # 200
curl -H "Authorization: Bearer <token>" <host>/api/v1/ref/provinces          # 404 unknown ref table
```
Rồi mở màn hình Nhân viên + Bảng lương một lượt.

## 4. Rollback

Rollback schema **không có** migration `down` — phải khôi phục thủ công.

**Dữ liệu:** `self-docs/files/db-cleanup-170826-*.sql` (`pg_dump --data-only`)
- Đợt 1 (7 bảng có dòng): `db-cleanup-170826-<tên>.sql`
- Đợt 2 (4 bảng seed học vấn): `db-cleanup-170826-education-<tên>.sql`
- Đợt 4 (4 bảng seed, backup bù 180826): `db-cleanup-170826-groupA-<tên>.sql`
- 21 bảng còn lại: 0 dòng ở prod, không cần dữ liệu.

**DDL:** lấy từ git, các khối đã bị xoá khỏi `database.go`:
```bash
git show 032a7c2^:internal/database/database.go     # trước đợt 1
git show eb53934^:internal/database/database.go     # trước đợt 4 nhóm A
git show 78d32d9^:internal/database/database.go     # trước đợt 4 nhóm B
git show origin/develop:internal/db/schema.sql      # schema đầy đủ trước toàn bộ đợt dọn
```
Hoặc nhanh hơn: khôi phục thẳng dump ở B0.

**Cột đã xoá** (25 cột 170826 + 3 cột 180826): toàn bộ đều 0% dữ liệu ở prod tại thời điểm đo,
trừ 9 cột nhóm C (`employees.birth_province_ref_id`, `org_province_id`, `perm_province_ref_id`,
`recruit_province_ref_id`, `perm_district_ref_id`, `work_location_id`; `org_structures.province_id`,
`district_id`, `work_location_id`) — 27–69% có dữ liệu. Nếu cần khôi phục 9 cột đó thì phải lấy
lại từ dump B0, không tái tạo được từ nguồn khác. Dữ liệu gốc mà chúng trỏ tới vẫn còn nguyên
trong `hris_provinces`/`hris_districts`/`work_locations` (3 bảng không bị đụng).

## 4b. Thứ tự đã chốt 180826 (bản cuối) — một nhánh tích hợp, một MR, một lần apply

`develop` đang chạy UAT. Gộp tất cả vào nhánh **`release/uat-180826`** (đã dựng, đã push,
`origin/release/uat-180826` @ `6d612f2`) rồi mở **đúng một MR** — UAT chỉ nhận một lần deploy:

```
release/uat-180826 = feature_v2
                   + chore/db-cleanup-legacy-tables
                   + feature/workday-bridge-contracts-workhistories
```

1. `pg_dump -Fc` DB UAT
2. MR `release/uat-180826` → `develop`, merge → UAT nhận code *(2 xung đột `atlas.sum` +
   `docs/routes-permissions.md` đã giải sẵn trên nhánh, không phải làm lại)*
3. `pg_dump -Fc` lần nữa, sát giờ
4. **Apply 11 migration bằng `psql` trong một transaction** — §B2 dưới đây
5. Sau khi merge: **bắt buộc** `git checkout feature_v2 && git merge origin/develop`, nếu không lần
   merge `feature_v2` kế tiếp sẽ mang 15 khối `CREATE TABLE IF NOT EXISTS` quay lại

Hai MR cũ nhắm thẳng `develop` (MR !29 cho `chore/db-cleanup-legacy-tables`, và MR của nhánh
Workday nếu đã mở) **giờ đã thừa** — đóng lại, giữ nhánh nguồn để truy vết.

Gộp làm một lần apply thay vì hai vì trạng thái ở giữa — code mới, DB chưa đổi — đã kiểm chứng là an
toàn vô thời hạn: 32 bảng vẫn còn, code không dùng tới. Quy tắc §2 (deploy code TRƯỚC, apply SAU)
vẫn được giữ nguyên và là lý do apply nằm ở bước cuối.

Bước 5 chỉ được chạy sau khi UAT đã thật sự khởi động bằng code của bước 2. Nếu UAT còn đợt nghiệm
thu chạy dở thì hoãn riêng bước 4-5, bước 1-3 không rủi ro DB.

---

## 5. Sau khi vào `develop`

**Bắt buộc merge `develop` → `feature_v2` trước khi `feature_v2` lên bất kỳ môi trường nào.**
`feature_v2` đi trước `develop` 20 commit và vẫn còn nguyên các khối `CREATE TABLE IF NOT EXISTS`
trong `database.go`. Đã kiểm: `feature_v2` chỉ THÊM 220 dòng vào file đó và không sửa
`ref/handler.go`, nên merge sẽ giữ được các dòng đã xoá — nhưng phải merge thật rồi
`grep -c 'CREATE TABLE IF NOT EXISTS attendance_items' internal/database/database.go` → `0`
để xác nhận, không tin suông.

## 6. Liên quan

- `self-docs/DB-Cleanup-Legacy-Tables-170826.md` — đợt 1 (10 bảng)
- `self-docs/DB-Cleanup-Education-Ref-Tables-170826.md` — đợt 2 (6 bảng + 11 cột)
- `self-docs/DB-Cleanup-Standalone-Tables-FK-Columns-170826.md` — đợt 4 (16 bảng + 9 cột) + đính chính 180826
- `self-docs/Review-DB-Cleanup-Workday-Bridge-180826.md` — review độc lập, nguồn của runbook này
