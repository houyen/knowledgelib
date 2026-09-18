---
id: self-docs/engine/db-cleanup-standalone-tables-fk-columns
canonical_question: 'Technical guide and specification: Dọn dẹp bảng cô lập + cột
  FK chết'
aliases:
- Dọn dẹp bảng cô lập + cột FK chết
- DB Cleanup Standalone Tables FK Columns 170826
entity_type: how_to
domain: self-docs > engine
last_verified: 2026-09-17
---

# Dọn dẹp bảng cô lập + cột FK chết (đợt 4, 170826)

> ⚠️ **Triển khai:** backend KHÔNG chạy Atlas — các migration của đợt này phải `atlas migrate apply`
> bằng tay, và **bắt buộc deploy code TRƯỚC khi apply**. Xem `self-docs/DB-Cleanup-Deploy-Runbook-180826.md`.

**Trạng thái:** Đã thi hành, chưa merge vào `develop`.
**Nhánh:** `Core System-backend@chore/db-cleanup-legacy-tables` (đợt 4, cùng nhánh 3 đợt trước).
**Tài liệu nguồn:** `llmwiki/wiki/sources/draft/170826-db-cleanup-standalone-tables-fk-columns.md`
(SPEC) + `170826-db-cleanup-standalone-tables-fk-columns-PLAN.md` (PLAN thi hành).

## Bối cảnh

Sau 3 đợt dọn DB trước, user yêu cầu phân tích toàn diện 2 lớp còn lại: (1) bảng hoàn toàn không
có khoá ngoại (cô lập), (2) bảng có khoá ngoại với nhau — rồi đối chiếu kết quả bằng một bản dump
DB thật khác (`prd-payroll_dev-170826-173517.sql.gz`, do user tự tải và yêu cầu restore thành
`payroll_engine_1708`) trước khi chốt phạm vi cuối cùng.

**Vòng 1 — 33 bảng cô lập** (không FK ra/vào bảng nào): grep code cả 3 repo (nhánh đầy đủ nhất mỗi
repo) tìm ra 4 bảng chết hoàn toàn.

**Vòng 2 — 63 bảng có FK với nhau**: cùng phương pháp, tìm thêm 14 bảng chết.

**Xác nhận bằng dump `payroll_dev` thật** (146 bảng, 12.304 nhân viên, snapshot môi trường khác —
migration `goose` dừng ở 28/07/2026, trước mọi việc dọn dẹp trong phiên này): số dòng của toàn bộ
16 bảng ứng viên khớp gần tuyệt đối với local dev (`ref_provinces` 97=97, `job_rotation_types`
39=39, `leave_requests` 2=2...) — xác nhận không phải hiện tượng do mẫu dev nhỏ. Dump này cũng hé
lộ 41 bảng `wd_*`/`payroll_rows`/`payroll_input_*` hoàn toàn 0 dòng — tàn tích một nỗ lực nhúng
Workday trực tiếp vào `payroll_engine` đã bị bỏ dở trước khi đội chuyển sang kiến trúc
`Core System-adapter` tách biệt — không tồn tại trong schema hiện hành, không thuộc phạm vi đợt này.

**Người dùng chốt phạm vi cuối** qua 2 lượt xác nhận: đồng ý phần lớn, loại trừ
`salary_formula_configs` (tự phân tích riêng) và `work_locations` (giữ bảng dù không code dùng).
Xác nhận riêng qua `AskUserQuestion`: vẫn xoá cột `employees.work_location_id` dù giữ bảng
`work_locations` — cột chết độc lập với quyết định giữ bảng.

## Kết quả — 16 bảng + 9 cột đã xoá

### Nhóm A/A2 — 9 bảng độc lập

| Bảng | Dòng | Ghi chú |
|---|---|---|
| `ref_provinces` | 97 | Cô lập sau khi 5 cột trỏ vào đã xoá đợt 3 |
| `job_rotation_types` | 39 | Chỉ `CREATE TABLE`, 0 code |
| `payroll_table_configs` | 0 | Chỉ `CREATE TABLE`, 0 code |
| `ref_banks` | 25 | **Phát hiện thêm lúc áp dụng:** có FK chết trỏ vào từ `employee_bank_accounts.ref_bank_id` (0/10700) — dùng `CASCADE` |
| `ref_relation_types` | 11 | **Phát hiện thêm lúc áp dụng:** có FK chết trỏ vào từ `employee_dependents.ref_relation_type_id` (0/24530) — dùng `CASCADE` |
| `employee_insurance_salaries` | 0 | Chỉ `CREATE TABLE`, 0 code |
| `salary_history` | 0 | Chỉ `CREATE TABLE`, 0 code |
| `payroll_record_ot_details` | 0 | Chỉ `CREATE TABLE`, 0 code |
| `payroll_record_allowances` | 0 | Chỉ `CREATE TABLE`, 0 code |

**Lưu ý quan trọng:** SPEC ban đầu liệt kê `ref_banks`/`ref_relation_types` là "không FK ra/vào" —
sai sót từ vòng quét đầu, phát hiện lúc chạy migration thật (`psql` báo lỗi
`cannot drop table ref_banks because other objects depend on it`). Đã dừng lại, kiểm tra dữ liệu
(cả 2 FK đều 0% populated — chết), sửa migration dùng `CASCADE`, xác nhận qua preview chỉ mất đúng
1 constraint mỗi bên, không đụng `employee_bank_accounts`/`employee_dependents`, rồi mới áp dụng
thật. Đây là ví dụ cụ thể cho việc luôn preview `BEGIN/ROLLBACK` trước khi áp dụng bất kỳ migration
DB nào — kể cả khi đã "chắc chắn" từ vòng phân tích trước.

### Nhóm B — 7 bảng có FK phụ thuộc lẫn nhau, xoá đúng thứ tự

```
attendance_items, overtime_records → shift_configs
leave_budget_details → leave_budgets
leave_requests (độc lập)
sync_errors (giữ nguyên sync_jobs)
```

Cả 7 bảng: 0-4 dòng dữ liệu, chỉ `CREATE TABLE` trong `database.go`, 0 repository/service dùng.
`work_locations` loại trừ khỏi nhóm này (giữ bảng, 309 dòng — code chỉ nhắc 1 dòng comment, không
1 câu SQL nào).

### Nhóm C — 9 cột FK chết, giữ nguyên 2 bảng `employees`/`org_structures`

| Cột | Bảng | Trỏ tới |
|---|---|---|
| `birth_province_ref_id`, `org_province_id`, `perm_province_ref_id`, `recruit_province_ref_id`, `perm_district_ref_id`, `work_location_id` | `employees` | `hris_provinces`/`hris_districts`/`work_locations` |
| `province_id`, `district_id`, `work_location_id` | `org_structures` | `hris_provinces`/`hris_districts`/(không FK chính thức) |

Cả 9 cột: có dữ liệu thật (27-69% tuỳ cột) nhưng 0 code đọc/ghi ngoài khai báo struct trong
`models/employee.go`. `hris_provinces`/`hris_districts`/`work_locations` (3 bảng bị trỏ tới) hoàn
toàn không bị đụng — chỉ mất liên kết FK.

## Sự cố kỹ thuật gặp phải và cách xử lý

**Line ending CRLF bị mất:** script Python xoá khối `const migrationX` trong `database.go` (Task
2) vô tình chuyển toàn bộ file từ CRLF (quy ước gốc của file) sang LF do mở file ở chế độ text mặc
định của Python. Phát hiện qua `git commit` báo diff bất thường (3445 dòng thay đổi thay vì ~80).
Sửa bằng 1 commit riêng khôi phục CRLF (`3803f34`), xác nhận diff cuối cùng so với trước khi bắt
đầu chỉ đúng 83 dòng xoá. Task 3 (Nhóm B) rút kinh nghiệm, mở file với `newline=""` để giữ nguyên
line ending — không lặp lại sự cố.

**Drift sẵn có giữa tài liệu và DB thật:** cả `schema.sql` và `tables_db.md` đã lệch với DB thật từ
trước đợt này (thiếu 6 cột `employees`: `contract_type`, `emp_type`, `has_second_contract`,
`has_termination`, `hris_portal_employee_code`, `is_foreigner` — không liên quan gì tới đợt dọn
dẹp này, chỉ là tài liệu chưa từng được đồng bộ lại đầy đủ sau khi các cột này được thêm vào DB ở
một thời điểm nào đó). Xác nhận drift này tồn tại TRƯỚC khi đợt 4 bắt đầu (đối chiếu bản
`git show HEAD` trước khi sửa). Số cột `employees` trong `tables_db.md` sau đợt 4 đặt đúng theo số
liệu THẬT đo từ DB (213, không phải suy luận 213-6=207 dựa trên số cũ đã sai) — không mở rộng phạm
vi đợt này để sửa luôn drift đó.

## Thi hành

1. **Task 1 (GATE):** baseline `go test ./...` = 918 passed/8 failed (khớp 4 test case đã biết
   trước). Đo số dòng 16 bảng + tỷ lệ populated 9 cột, khớp SPEC.
2. **Task 2:** migration `20260817040000_drop_standalone_tables_group_a.sql` — 9 bảng (2 dùng
   `CASCADE` sau phát hiện lúc áp dụng). Xoá 6 khối `const migrationX` trong `database.go`
   (`migrationJobRotationTypes`, `migrationPayrollTableConfigs`,
   `migrationEmployeeInsuranceSalaries`, `migrationSalaryHistory`,
   `migrationPayrollRecordOTDetails`, `migrationPayrollRecordAllowances`) bằng script Python —
   xác nhận qua restart backend thật, 6 bảng không tái sinh.
3. **Task 3:** migration `20260817050000_drop_dependent_tables_group_b.sql` — 7 bảng đúng thứ tự.
   Xoá 7 khối `const migrationX` tương ứng — xác nhận qua restart backend thật.
4. **Task 4:** migration `20260817060000_drop_dead_fk_columns_group_c.sql` — 9 cột trên 2 bảng
   sống. Xác nhận không cần sửa `database.go` (9 cột được thêm bởi migration một-lần, không có
   cơ chế tự-tái-tạo).
5. **Task 5:** đồng bộ `schema.sql` (script Python xoá khối, tái dùng phương pháp đợt 2/3, mở rộng
   `FK_CONSTRAINT_NAMES`/`INDEX_NAMES` cho 2 FK phát hiện thêm) và `tables_db.md` (65 mục còn lại
   từ 81, `employees` 213 cols, `org_structures` 58 cols — cả 2 số khớp DB thật).
6. **Task 6 (tài liệu, đang làm — file này).**
7. **Task 7:** `go test ./...` sau = 918 passed/8 failed — khớp baseline tuyệt đối, 0 hồi quy.
   `go build`/`go vet` sạch. Xác nhận `salary_formula_configs`(18)/`work_locations`(309)/
   `hris_provinces`(104)/`hris_districts`(758)/`sync_jobs`(50) còn nguyên vẹn.

## Commit

Trên `Core System-backend@chore/db-cleanup-legacy-tables` (chưa push, chưa merge), nối tiếp 9 commit
3 đợt trước:
- `eb53934` — chore(db): xoá 9 bảng độc lập Nhóm A/A2 + code tự-tái-sinh
- `3803f34` — fix(db): khôi phục line ending CRLF gốc cho database.go
- `78d32d9` — chore(db): xoá 7 bảng phụ thuộc Nhóm B + code tự-tái-sinh
- `1c5c5a6` — chore(db): xoá 9 cột FK chết trên employees/org_structures
- `3607c1b` — chore(db): đồng bộ schema.sql
- `b0d4883` — docs(db): xoá 16 mục bảng + 9 cột khỏi tables_db.md

## Việc KHÔNG làm (Non-goals, ghi trong SPEC)

- Không xử lý `salary_formula_configs` — user tự phân tích riêng.
- Không xoá `work_locations` — giữ bảng theo yêu cầu người dùng.
- Không xoá `hris_provinces`/`hris_districts` — đang dùng thật (báo cáo Bảng chấm công).
- Không đụng `sync_jobs`.
- Không sửa drift sẵn có giữa `schema.sql`/`tables_db.md` và DB thật (6 cột `employees` không liên
  quan đợt này) — ghi nhận, để riêng.
- Không merge nhánh này vào `develop`/`feature_v2`.

---

## Đính chính 180826 (từ review độc lập)

Nguồn: `self-docs/Review-DB-Cleanup-Workday-Bridge-180826.md` §F6, §F3.

### 1. Lý do "không cần backup" của Nhóm A nói sai thực tế

Migration `20260817040000_drop_standalone_tables_group_a.sql` ghi:
*"Không cần backup — toàn bộ 0 hoặc vài dòng test/seed, không dữ liệu nghiệp vụ thật."*

Đo lại trên dump prod `payroll_engine_1708` thì **không phải "vài dòng"**:

| Bảng | Số dòng thật (prod) |
|---|---|
| `ref_provinces` | 97 |
| `job_rotation_types` | 39 |
| `ref_banks` | 25 |
| `ref_relation_types` | 11 |

Lý do ĐÚNG để không cần backup là: **toàn bộ đều là seed tái tạo được từ migration nhúng** —
`migrations/v3_ref_tables.sql` (ref_provinces/ref_banks/ref_relation_types),
`migrations/v3b_provinces_2025.sql` (ref_provinces 2025),
`migrations/v41_hris_employee_levels_job_rotation_schema.sql` (job_rotation_types) — chứ không
phải "ít dòng nên bỏ được".

**Đã backup bù 180826** (để đồng nhất với chính sách đợt 1 và đợt 2), dữ liệu lấy từ dump prod:

- `self-docs/files/db-cleanup-170826-groupA-ref_provinces.sql` — 97 dòng
- `self-docs/files/db-cleanup-170826-groupA-ref_banks.sql` — 25 dòng
- `self-docs/files/db-cleanup-170826-groupA-ref_relation_types.sql` — 11 dòng
- `self-docs/files/db-cleanup-170826-groupA-job_rotation_types.sql` — 39 dòng

Không sửa nội dung file migration đã áp dụng (đổi nội dung sẽ làm lệch hash trong `atlas.sum` và
`atlas_schema_revisions` của DB đã chạy) — đính chính ghi ở đây.

### 2. Ba cột FK mồ côi bị bỏ sót, đã xử lý ở migration mới

`CASCADE` ở đợt 1 và đợt 4 chỉ gỡ RÀNG BUỘC, không xoá cột. Còn sót 3 cột UUID trơn không trỏ
đi đâu (đều 0% dữ liệu): `employees.ref_hospital_id`, `employee_bank_accounts.ref_bank_id`,
`employee_dependents.ref_relation_type_id`.

Xử lý ở `atlas/migrations/20260818000000_drop_orphan_fk_columns.sql` (commit `2468a2b`).
Quét lại toàn bộ `pg_constraint` trên dump prod TRƯỚC cleanup xác nhận **không còn cột nào khác
bị bỏ sót cùng kiểu**: 26 FK trỏ vào 32 bảng đã xoá — 13 xuất phát từ bảng cũng bị xoá, 13 từ
bảng sống, trong đó 10 đã được xoá cột đúng thứ tự và 3 là 3 cột trên.

### 3. Ghi chú về triển khai

Xem `self-docs/DB-Cleanup-Deploy-Runbook-180826.md` — backend **KHÔNG chạy Atlas**, các migration
này phải `atlas migrate apply` bằng tay, và **bắt buộc deploy code trước khi apply**.
