---
id: self-docs/engine/review-db-cleanup-workday-bridge
canonical_question: 'Technical guide and specification: Review độc lập — Dọn dẹp DB  +
  Cầu nối Workday  — 180826'
aliases:
- Review độc lập — Dọn dẹp DB  + Cầu nối Workday  — 180826
- Review DB Cleanup Workday Bridge 180826
entity_type: how_to
domain: self-docs > engine
last_verified: 2006-01-02
---

# Review độc lập — Dọn dẹp DB (4 đợt) + Cầu nối Workday (2 nhánh) — 180826

**Vai trò:** reviewer độc lập, KHÔNG có context phiên 170826. Mọi số liệu dưới đây tự đo lại,
không lấy từ self-docs của phiên trước.

**Phạm vi:**
- `Core System-backend@chore/db-cleanup-legacy-tables` (17 commit, `032a7c2`..`b0d4883`)
- `Core System-backend@feature/workday-bridge-contracts-workhistories` (4 commit, `8321f37`..`319793d`)
- `Core System-adapter@feature/workday-bridge-transfer-changelog` (1 commit, `a152d98`)

**Môi trường kiểm chứng:** DB `payroll_engine` (dev, đã áp dụng cleanup), `payroll_engine_1708`
(dump prod 146 bảng/12.304 NV, TRƯỚC cleanup — dùng làm bàn thử migration), `payroll_adapter`
(8.429 payload worker thật). Bản sao tạm đã xoá sạch sau khi kiểm; worktree tạm đã gỡ.

---

## KẾT LUẬN

| Luồng | Verdict |
|---|---|
| 1 — Dọn DB | **Merge được sau khi sửa F1 + F2 và viết runbook F4.** Bản thân việc xoá là đúng: 0 hồi quy test, 0 mất dữ liệu, migration replay sạch trên dump prod. |
| 2 — Cầu nối Workday | **CHƯA nên merge.** G1 (kẹt cứng luồng sync employees) là lỗi chặn; G2/G3 làm mất dữ liệu âm thầm; nhánh hợp đồng chưa có 1 mẫu Workday thật nào. |

---

## LUỒNG 1 — Phát hiện

### F1 [MEDIUM] 3 endpoint `/ref/*` trỏ vào bảng đã xoá → HTTP 500 thay vì 404
`internal/transport/http/ref/handler.go:25,27,28` còn `provinces` → `ref_provinces`,
`banks` → `ref_banks`, `relation-types` → `ref_relation_types`. Cả 3 bảng bị DROP ở
`20260817040000_drop_standalone_tables_group_a.sql`.

Đợt 2 (`a73d05b`) đã lập tiền lệ xoá 6 endpoint tương ứng bảng đã xoá — đợt 4 quên làm.

Bằng chứng (chạy đúng 3 câu SQL trong handler trên `payroll_engine`):
```
ERROR:  relation "ref_provinces" does not exist
ERROR:  relation "ref_banks" does not exist
ERROR:  relation "ref_relation_types" does not exist
```
5 entry còn lại (`marital-statuses`, `ethnicities`, `religions`, `countries`,
`education-levels`) chạy OK; `hospitals` đọc `employees.health_ins_hospital`, không liên quan.

Ảnh hưởng thực tế thấp: grep `Core System-frontend@feature_v2/src` → **0** lời gọi `/ref/*` nào.
Nhưng route vẫn 500 thay vì 404 "unknown ref table" như đợt 2 đã chuẩn hoá.

**Sửa:** xoá 3 dòng khỏi `allowedRefTables`.

### F2 [LOW-MED] `internal/db/tables_db.md` — header `Total tables` sai
`**Total tables**: 97` nhưng file chỉ còn **65** mục `### ` (97−10−6−16 = 65 ✓ số mục đúng, chỉ
header sai), và DB dev thật có **79** bảng. Sai theo mọi cách đọc. Header chưa từng được sửa qua
cả 4 đợt.

> **ĐÍNH CHÍNH 180826 (bản review đầu tiên nói sai):** tôi đã báo `### employees (213 cols)` vs 207
> bullet là lỗi thứ hai. **Không phải lỗi.** Commit `b0d4883` cố ý đặt 213 và nói rõ lý do trong
> message; đo lại: `payroll_engine.employees` có **đúng 213 cột thật**. File chỉ thiếu 6 *bullet*
> (`contract_type`, `emp_type`, `has_second_contract`, `has_termination`,
> `hris_portal_employee_code`, `is_foreigner`) — đúng 6 cột drift tiền tồn tại đã nêu ở mục
> schema.sql bên dưới. Số khai báo đúng, danh sách liệt kê thiếu.

Đo toàn diện `tables_db.md` vs DB dev (180826) — **toàn bộ đều là drift tiền tồn tại, không phải do
đợt dọn**: thiếu 14 bảng; thiếu 20 cột ở 8 bảng; 7 mục có số `(N cols)` chưa cập nhật
(`companies` 14→15, `employee_roles` 4→8, `payroll_records` 47→50, `roles` 7→9,
`salary_component_overrides` 15→17, `salary_components` 22→23, `template_components` 3→4).
`employees` là mục DUY NHẤT có số đúng.

### F3 [LOW-MED] Còn 3 cột FK mồ côi sau `CASCADE`
`employees.ref_hospital_id`, `employee_bank_accounts.ref_bank_id`,
`employee_dependents.ref_relation_type_id` — constraint đã bị `CASCADE` gỡ, cột vẫn còn, không
trỏ đi đâu nữa. Cả 3 đều 0% dữ liệu (đo trên dump prod). Mâu thuẫn chính sách của chính nhánh này
(đợt 2/3/4 đều xoá cột FK chết).

Đã quét `pg_constraint` trên dump prod TRƯỚC cleanup: **đúng 26 FK trỏ vào 32 bảng bị xoá**, trong
đó 13 xuất phát từ bảng cũng bị xoá (tự biến mất), 13 từ bảng sống — 10 cái đã được xoá cột đúng
thứ tự (không cần CASCADE), 3 cái còn lại chính là 3 cột trên. **Không còn FK nào bị bỏ sót.**

### F4 [MEDIUM] Không có runbook triển khai — backend KHÔNG tự chạy Atlas
`internal/database/database.go:2912` ghi rõ: *"backend KHÔNG chạy Atlas"*. `cmd/Core System/main.go`
chỉ chạy `RunMigrations` (hằng Go) + `RunFileMigrations` (`migrations/v*.sql` nhúng).
6 migration DROP nằm trong `atlas/migrations/` ⇒ **phải `atlas migrate apply` bằng tay**.

Không self-doc/commit message nào nói điều này, và cũng không nói **thứ tự bắt buộc: deploy code
TRƯỚC, apply migration SAU**. Nếu apply trước trong khi code cũ còn chạy, 15 bảng sẽ được
`RunMigrations` tạo lại ở lần restart kế: `sync_errors`, `employee_insurance_salaries`,
`shift_configs`, `attendance_items`, `leave_budgets`, `leave_budget_details`, `leave_requests`,
`overtime_records`, `payroll_table_configs`, `payroll_record_allowances`,
`payroll_record_ot_details`, `hris_payroll_snapshots`, `hris_payroll_detail_snapshots`,
`salary_history`, `job_rotation_types`.

### F5 [LOW] `migrations/v*.sql` nhúng vẫn tạo lại đối tượng đã xoá
`v3_ref_tables.sql` (ref_provinces/ref_banks/ref_relation_types/ref_hospitals/ref_majors/
ref_graduate_schools/ref_academic_degrees/ref_graduation_ranks/ref_degree_types/
ref_training_forms + các cột `employees.ref_*`), `v9_allowance_types.sql`,
`v15_education_schema.sql`, `v22`/`v23`/`v24`/`v25`/`v26b` (work_location_id, org_province_id…),
`v41` (job_rotation_types).

Trên DB đã có `schema_migrations` thì không chạy lại nên không vỡ hôm nay, và `main.go` từ chối
bootstrap DB trống. Nhưng repo giờ có 2 lớp migration mâu thuẫn nhau mà không có ghi chú nào.

*Mặt tích cực:* chính các file này là nơi khôi phục được seed mà đợt 4 không backup.

### F6 [LOW] Lý do "không cần backup" của đợt 4 nói sai thực tế
Migration `..._group_a.sql` ghi *"toàn bộ 0 hoặc vài dòng test/seed"*. Đo trên dump prod:
`ref_provinces` 97, `job_rotation_types` 39, `ref_banks` 25, `ref_relation_types` 11,
`allowance_items` 58, `hris_allowance_override` 2140, `allowance_overrides_bak` 1302.
Lý do ĐÚNG phải là "seed tái tạo được từ `migrations/v3_ref_tables.sql`, `v3b`, `v41`" — chứ không
phải "ít dòng". (Đợt 1 và 2 có backup đầy đủ trong `self-docs/files/`; đợt 4 không có file nào.)

### F7 [INFO] Artefact sinh tự động chưa cập nhật
`internal/db/gen/models.go` (sqlc), `internal/db/tables_code.md`, `internal/models/employee.go`
vẫn khai báo 20+ cột đã xoá. **Không vỡ** — đã grep xác nhận mọi `SELECT * FROM employees` đều
dùng `.Unsafe()`, và không có `INSERT`/`UPDATE` nào chạm cột đã xoá
(`employee_educations.ref_education_level_id` ở `employee_child_repos.go:325,345` là cột KHÁC,
vẫn sống). Nên regenerate cho sạch.

### F8 [INFO] `feature_v2` còn khối `CREATE TABLE` của các bảng đã xoá
`feature_v2` đi trước develop 20 commit và chỉ *thêm* 220 dòng vào `database.go`; `ref/handler.go`
thì giống hệt develop. Merge develop → feature_v2 sẽ giữ được các dòng đã xoá, nhưng phải làm
bước đó trước khi feature_v2 lên, nếu không 15 bảng sẽ tái sinh.

---

## LUỒNG 1 — Đã kiểm và ĐÚNG

**Grep độc lập 3 repo** (`Core System-backend@feature_v2`, `Core System-frontend@feature_v2`,
`Core System-adapter@develop` + `feature_v1`), loại trừ `atlas/migrations/`, `schema.sql`,
`tables_db.md`: 32 bảng + 25 cột — **0 tham chiếu code sống nào ngoài F1**. Các hit còn lại chỉ là
khối `CREATE TABLE` trong `database.go` (đã bị nhánh này xoá) và 2 comment không liên quan trong
`Core System-adapter` (`leave_requests` là bảng của Workday phía adapter, khác bảng cùng tên bên
backend). FE: 0 hit cho mọi tên cột đã xoá (camelCase lẫn snake_case).

**Replay 6 migration trên bản sao dump prod `payroll_engine_1708`:**
- 0 lỗi, **đúng 4 NOTICE**, cả 4 đều là CASCADE đã ghi sẵn trong comment migration
  (`payroll_record_allowances_allowance_item_id_fkey`, `employees_ref_hospital_id_fkey`,
  `employee_bank_accounts_ref_bank_id_fkey`, `employee_dependents_ref_relation_type_id_fkey`).
  Không có NOTICE ngoài dự kiến.
- 146 → **114** bảng (−32 đúng); `employees` 228 → **212** cột (−16); `org_structures` 61 → **58**;
  `employee_educations` 30 → **24**; `employees` **12.304 dòng trước = sau**; 0 view bị cascade.

**Số liệu "0% dữ liệu" đo lại trên dump prod (không tin số cũ):**
- 11 cột `ref_*` trên `employees`/`employee_educations`: **tất cả = 0**.
- 6 cột nhóm C có dữ liệu thật: `work_location_id` 8324, `perm_district_ref_id` 8008,
  `recruit_province_ref_id` 8116, `perm_province_ref_id` 8077, `birth_province_ref_id` 8529,
  `org_province_id` 8287 — khớp tài liệu.
- `org_structures`: 428 / 245 / 431.
- `employee_bank_accounts.ref_bank_id` = 0/10.700; `employee_dependents.ref_relation_type_id` = 0/24.530.

**Line ending:** `database.go` hiện **3264 CR / 3264 dòng** (CRLF toàn file, khớp develop
3543/3543). Xác nhận `eb53934` đúng là làm mất CRLF (CR=0) và `3803f34` khôi phục (CR=3423/3423).
**Không file Go nào khác bị đổi line ending** — `ref/handler.go` LF ở cả 2 bên; 6 file migration
mới + `atlas.sum` + `schema.sql` + `tables_db.md` đều LF, giống các file cùng loại sẵn có.

**`schema.sql` vs schema thật:** dựng 2 DB sạch từ chính `atlas/migrations/` của mỗi nhánh rồi so
cột với `schema.sql` tương ứng — **drift y hệt nhau, 8 mismatch trước và sau** ⇒ cleanup KHÔNG
thêm drift, và đã xoá đúng 25 cột + 32 bảng khỏi `schema.sql`. Bảng: develop có 2 bảng thừa
(`allowance_overrides_bak_20260624`, `hris_allowance_override`) đã được nhánh này gỡ đúng.

Drift **tiền tồn tại** (có sẵn trên develop, KHÔNG do đợt này gây thêm) — thực tế nhiều hơn con số
"6 cột employees" tài liệu nêu:
- `employees`: `contract_type`, `emp_type`, `has_second_contract`, `has_termination`,
  `hris_portal_employee_code`, `is_foreigner` (6)
- thêm: `employee_roles.email`, `salary_component_overrides.component_code`,
  `salary_components.business_note`, `template_components.component_code` (4)
- `schema.sql` thiếu hẳn 3 bảng do atlas tạo: `adapter_sync_state`, `employee_payroll_templates`,
  `salary_component_versions`
- `tables_db.md` sinh từ một DB khác (`payroll_dev` docker PG16) nên thiếu 14 bảng so với dev DB.

**5 đối tượng chủ động giữ lại — nguyên vẹn 100%** (dòng và cột, trước/sau replay):
`hris_districts` 759/759, `work_locations` 313/313, `salary_formula_configs` 18/18,
`ref_education_levels` 9/9, `majors` 662/662, `graduate_schools` 1123/1123, `hris_provinces`
104/104, `sync_jobs` 51/51.
`employee_educations.ref_education_level_id` (khác `employees.ref_education_level_id` đã xoá) còn
nguyên và vẫn được ghi bởi `employee_child_repos.go:325,345`.

**Test / build / vet** (cùng 1 bản sao DB dựng lại giữa 2 lượt để không nhiễm chéo):
- nhánh cleanup: **917 pass / 9 fail**
- `origin/develop`: **917 pass / 9 fail**
- `diff` danh sách tên test fail: **IDENTICAL** ⇒ **0 hồi quy**
- `go build ./...` rc=0, `go vet ./...` rc=0

Tài liệu ghi "918 passed / 8 failed" — chênh do cách đếm subtest, không phải chênh thực chất
(9 = 5 test cha + 4 subtest của `TestG1AllProtectedRoutesRequireRoleGateExceptAllowlist`).

---

## LUỒNG 2 — Phát hiện

### G1 [HIGH — chặn merge] Lỗi upsert hợp đồng làm KẸT VĨNH VIỄN luồng đồng bộ employees
`internal/service/adapter_sync_contract.go:70-73`: nếu `upsertEmployeeContract` lỗi,
`applyWorkerBatch` trả err → `applyBatch` rollback → **con trỏ `worker` không tiến** → lượt sau đọc
lại đúng lô đó → lỗi lại, mãi mãi. Trước 170826 luồng worker không có failure mode này.

Xác suất xảy ra không nhỏ vì chưa từng thấy dữ liệu hợp đồng thật và **không có truncate/guard nào**:
- `contract_no VARCHAR(100)` ← `Contract_ID`
- `contract_type_name VARCHAR(255)` ← `Employee_Contract_Type_ID`
- `sign_status VARCHAR(50)` ← `Employee_Contract_Status_ID`

Một giá trị dài quá ⇒ `value too long for type character varying(50)` ⇒ toàn bộ đồng bộ nhân viên
chết cứng, không phải chỉ hợp đồng.

**Sửa:** log-and-skip phần hợp đồng (giống cách `mapWorkerToContract` trả `ok=false` được xử lý),
hoặc truncate theo độ dài cột.

### G2 [MEDIUM] `RefreshWorkerTransferEvent` không ghi `wd_change_log`
Change log chỉ được ghi trong `InsertWorkerTransferEvent`. Đường "re-fetch and replace"
(`worker_transfer_events.go:112`) không ghi gì — mà **đúng những dòng cần refresh là dòng thiếu
`Employment_Data`**, tức thiếu `Position_Data.Business_Title`, tức đúng field DUY NHẤT backend lấy.

Hệ quả: backend ghi `employee_work_histories` với `position_name`/`job_title_name` RỖNG (test
`TestMapWorkerTransferEvent_MissingWorkerJobData_ReturnsEmptyTitleNotCrash` khẳng định đây là hành
vi cố ý) và **không bao giờ được sửa** vì bản snapshot đã vá không sinh change log.

**Sửa:** `RefreshWorkerTransferEvent` ghi thêm 1 dòng change log `change_type='update'`.

### G3 [MEDIUM] Không có backfill cho transfer event đã tồn tại
Change log chỉ ghi khi `tag.RowsAffected() > 0`, tức **chỉ dòng MỚI**. Mọi dòng
`wd_worker_transfer_events` đã có sẵn trong adapter prod (tính năng có từ 05/08) sẽ không bao giờ
sang backend. Local có 0 dòng nên không đo được — **phải đếm trên adapter prod trước khi merge**;
nếu > 0 thì cần script backfill (chèn change log cho các `log_wid` đã có).

### G4 [MEDIUM] Đổi hình dạng API mà không ghi nhận ở đâu
`State()`/`Run()` đổi từ 1 object thành mảng ⇒ `GET /api/v1/adapter-sync/state` và
`POST /api/v1/adapter-sync/pull` đổi payload từ `{...}` thành `[...]`.
`internal/handler/adapter_sync_handler.go` pass-through, không sửa gì.
FE hiện chưa gọi (grep 0 hit) nên chưa vỡ, nhưng là breaking change không có trong self-docs cũng
không trong `docs/routes-permissions.md`.

### G5 [MEDIUM] `Run()` nuốt lỗi → nút "Cập nhật" luôn báo thành công
Trước: `run` lỗi → `Run` trả err → handler trả 500. Nay `Run` luôn trả `nil` (trừ `ErrAdapterSyncBusy`),
lỗi chỉ nằm trong `results[i].Error` ⇒ HTTP **200** kể cả khi cả 2 entity đều hỏng. Không client nào
đang đọc field `error` đó.

### G6 [LOW-MED] `applied` đếm sai cho work history
`internal/service/adapter_sync_workhistory.go:56-58`: `applied++` sau `upsertEmployeeWorkHistory`
mà không kiểm `RowsAffected`. `INSERT ... SELECT ... FROM employees WHERE employee_code=$2` khớp 0
dòng thì chèn 0 dòng và KHÔNG lỗi — đã chứng minh bằng SQL thật trên bản sao DB: `INSERT 0 0`.
Nhánh worker thì có kiểm `RowsAffected()`. ⇒ `adapter_sync_state.last_applied` và log "ghi N" thổi phồng.

### G7 [LOW-MED] Sinh dòng `employee_contracts` trùng với 25.865 dòng snapshot sẵn có
Đo trên dump prod: **toàn bộ 25.865 dòng `employee_contracts` có `source='pipeline'` và `hris_id`
NULL 100%**. Dòng Workday có `hris_id` riêng ⇒ không dedup được với dòng pipeline của cùng hợp đồng.
`employee_child_repos.go:17` (`SELECT * ... ORDER BY date_start DESC`) sẽ trả cả hai ⇒ UI hiện 2 hợp
đồng. Dòng Workday cũng không set `is_current` (mặc định false) và `date_end` (NULL).

### G8 [LOW] `ON CONFLICT (hris_id) DO UPDATE` không giới hạn theo `source`
Nếu một `hris_id` sinh từ Workday trùng `hris_id` sẵn có, lệnh ghi đè dòng HRIS trong im lặng.
Hiện xác suất ~0 (cột đang NULL 100%), nhưng dữ liệu HRIS tương lai có thể điền.
Thêm `WHERE employee_contracts.source = 'workday'` vào `DO UPDATE` là an toàn.

### G9 [LOW] Rủi ro lệch 1 ngày ở `effectiveDate`
`wd_worker_transaction_logs.effective_moment` là `timestamptz`. `InsertWorkerTransferEvent` ghi
`time.Time` đó vào cột `DATE` (PostgreSQL quy đổi theo `TimeZone` của session) **nhưng** chuỗi trong
change log dùng `effectiveDate.Format("2006-01-02")` (theo location của `time.Time` trong Go — pgx
trả UTC). Hai đường có thể lệch 1 ngày với các mốc nửa đêm giờ VN. Chưa đo được (0 dòng local).
Nên lấy chuỗi từ cùng một nguồn (ép `.In(loc)` tường minh, hoặc đọc lại cột `DATE` vừa ghi).

### G10 [MEDIUM] Xung đột merge chắc chắn ở `atlas/migrations/atlas.sum` (đã thử thật)
Merge cleanup vào develop: OK. Merge tiếp workday:
```
CONFLICT (content): Merge conflict in atlas/migrations/atlas.sum
```
Nguyên nhân: 2 nhánh cùng sửa dòng `h1:` tổng và cùng append entry. Đáng chú ý, workday dùng
timestamp `20260817020000` — đúng khe trống giữa đợt 2 (`010000`) và đợt 3 (`030000`) của luồng 1.

Cách xử lý đúng đã kiểm chứng: giữ cả 2 khối rồi chạy `atlas migrate hash`. Sau đó
`atlas migrate validate` sạch, apply tuần tự 31 migration lên DB trống → 68 bảng,
`adapter_sync_state` có đủ 2 dòng (`worker`, `worker_transfer_event`), `go build`/`go vet` rc=0.

---

## LUỒNG 2 — Trả lời trực tiếp 6 câu hỏi

**1. Hình dạng JSON có đủ căn cứ tin cậy không?** Khá hơn "suy đoán" nhiều, nhưng KHÔNG đồng đều:

- `Employment_Data.Worker_Job_Data[].Position_Data.Business_Title` — **đã xác minh trên dữ liệu
  thật.** `workerBusinessTitleFromRaw` là bản sao đúng từng dòng của
  `Core System-adapter/internal/workday/get_workers.go:570 workerPositionData`. Tôi chạy đúng đường dẫn
  đó trên **8.429 payload worker thật** trong `wd_change_log` local:
  `with_employment 8429/8429`, `with_jobdata 8429/8429`, `Worker_ID 8429/8429`, và giá trị
  `Business_Title` hợp lý ("Managing Director, MEP", "Deputy Director of Design Management Center",
  "CEO of Business Unit"). Đường này coi như đã kiểm.
- `Worker_Data.Employee_Contracts_Data.Employee_Contract_Data` — **chưa có 1 mẫu thật nào**:
  `with_contract 0/8429`. Chỗ dựa duy nhất là code adapter + comment *"verified live 2026-08-01"*
  và fixture `TestWorkerEmployeeContract`. `mapWorkerToContract` là bản sao trung thực của
  `workerEmployeeContract` (kể cả `AsList`/`IDsByType`), nên rủi ro sai đường dẫn thấp — nhưng rủi
  ro **giá trị** (độ dài, ký tự) thì chưa loại trừ, và G1 biến rủi ro đó thành kẹt cứng.
  ⇒ **Bắt buộc chạy 1 lượt sync thật trên môi trường có Workday và kiểm 5-10 dòng
  `employee_contracts` trước khi bật scheduler ở prod.**
- Snapshot transfer event: `FetchWorkerOrgSnapshot` chỉ bật
  `Include_Reference/Organizations/Employment_Information`. Backend chỉ cần `Worker_ID` +
  `Business_Title`, cả hai nằm trong nhóm đó ⇒ hợp lý, nhưng chưa có mẫu thật (0 dòng
  `wd_worker_transfer_events` local).

**2. `uuid.NewSHA1` có an toàn/ổn định không?** Có — lựa chọn đúng. Xác định, ổn định qua nhiều
lượt sync, namespace riêng cho từng bảng nên không đụng nhau. Với ~26k khoá trên 122 bit hiệu dụng,
xác suất va chạm là không đáng kể (~1e-29). **Rủi ro thật không nằm ở hash** mà ở giả định
*"Contract_ID / log_wid duy nhất toàn cục"* — nếu Workday tái sử dụng `Contract_ID` giữa 2 công ty
thì 2 hợp đồng khác nhau gộp thành 1 dòng, im lặng. Nên ghi rõ giả định đó, kèm G8.

**3. `LIMIT 1` có đúng cách không?** Nên siết, nhưng vấn đề thực tế nhỏ hơn tài liệu nghĩ:
mã trùng DUY NHẤT trong cả DB dev lẫn dump prod là `employee_code = '-1'` (Enterprise + UNI) — dòng rác
sentinel; Workday không bao giờ gửi `Worker_ID = "-1"`. Hai điểm vẫn nên sửa:
(a) `LIMIT 1` không có `ORDER BY` ⇒ nếu có mã trùng thật thì chọn dòng nào là **không xác định** và
có thể đổi giữa các lượt sync; (b) **không nhất quán** với câu `UPDATE employees ... WHERE
employee_code = $1` ngay phía trên trong CÙNG hàm — câu đó KHÔNG có `LIMIT` nên cập nhật CẢ HAI
dòng trùng. Đề xuất: `ORDER BY company_code, id` cho ổn định; tốt hơn là đếm > 1 thì bỏ qua + log
(báo lỗi to) vì sự mơ hồ đã biết trước.

**4. `AdapterSyncService` sau khi tổng quát hoá có đổi hành vi entity `worker` không?**
Câu `UPDATE employees` giữ nguyên từng ký tự; skip-khi-thiếu-mã và skip-khi-`RowsAffected=0` giữ
nguyên; `applyBatch` vẫn trả `0, err` khi apply lỗi; con trỏ vẫn tiến trong cùng transaction;
`lastID = changes[len-1].ID` bằng đúng biến `lastID` của vòng lặp cũ. **Đúng là refactor thuần —
TRỪ** việc thêm upsert hợp đồng vào cùng transaction (⇒ G1) và G4/G5 ở tầng API.
Cô lập lỗi giữa 2 entity thì **đúng**: `run()` gọi `runEntity` từng cái, gán `res.Error`, không
return sớm; mỗi entity có con trỏ riêng trong `adapter_sync_state`.

**5. `InsertWorkerTransferEvent` có idempotent thật không?** **Có — đã kiểm chứng bằng test chạy
thật trên DB `payroll_adapter` local, không phải fixture.**
`TestInsertWorkerTransferEvent_WritesChangeLog` gọi 2 lần cùng `log_wid` → `wd_change_log` vẫn
đúng 1 dòng. Test **PASS** trong lượt chạy của tôi. Cả 2 câu ghi nằm trong 1 transaction ✓.
Đã xác nhận DB sạch sau khi chạy (`wid like 'test-log-wid-170826%'` = 0 dòng).

**6. Test 2 repo:**
| Repo / nhánh | pass | fail | so với develop |
|---|---|---|---|
| backend `feature/workday-bridge-...` | **924** | 9 | develop 917/9 — danh sách fail IDENTICAL, +7 test mới, **0 hồi quy** |
| adapter `feature/workday-bridge-...` | **163** | 0 | develop 162/0 — +1 test, **0 hồi quy** |

`go build ./...` và `go vet ./...` rc=0 trên cả 2 nhánh của cả 2 repo.

---

## Thứ tự đề xuất trước khi merge

1. Sửa **F1** (3 dòng) + **F2** (2 con số).
2. Viết runbook **F4** (backend không chạy Atlas; deploy code trước, `atlas migrate apply` sau).
3. Merge luồng 1 vào develop.
4. Sửa **G1** (chặn) → **G2**, **G3** → cân nhắc G5/G6/G8.
5. Chạy 1 lượt sync thật có Workday, kiểm mẫu `employee_contracts` + `employee_work_histories`.
6. Merge luồng 2, sau đó chạy `atlas migrate hash` để giải **G10**.

---

# THI HÀNH 180826 — kết quả sửa theo review

SPEC/PLAN: `llmwiki/wiki/sources/draft/180826-fix-review-db-cleanup-workday(.md/-PLAN.md)`.
4 quyết định của người dùng: sửa tại chỗ 2 nhánh cũ · G7 dùng `NOT EXISTS` theo `contract_no` ·
giữ payload mảng + 500 khi mọi entity lỗi · xoá nhánh adapter, giao template thuần.

## Phase 1 — `Core System-backend@chore/db-cleanup-legacy-tables` (5 commit)

| Commit | Việc |
|---|---|
| `6bdd893` | **F1** xoá 3 endpoint `/ref/{provinces,banks,relation-types}` |
| `ebfd4a2` | **F2** header `Total tables` + khối cảnh báo drift trong `tables_db.md` |
| `2468a2b` | **F3** migration `20260818000000` xoá 3 cột FK mồ côi + đồng bộ `schema.sql`/`tables_db.md` |
| `d5a8c78` | **F5** cảnh báo 2 lớp migration trong `migrate_files.go` |
| — | **F4** runbook + **F6** backup bù (self-docs, không nằm trong git repo) |

**F1 kiểm bằng server thật** trên bản sao DB dev: 3 route trả `404 unknown ref table`, 6 route còn
lại trả `200` kèm dữ liệu. Đồng thời xác nhận được một việc khác: boot server bản nhánh này trên
bản sao DB đã dọn (79 bảng) → sau `RunMigrations` vẫn đúng **79 bảng**, không bảng nào tái sinh.

**ĐÍNH CHÍNH quan trọng đối với review gốc** — xem §F2: khẳng định "`employees (213 cols)` sai" của
tôi là **sai**. `payroll_engine.employees` có đúng 213 cột thật, commit `b0d4883` đặt số đó cố ý và
nói rõ lý do trong message. Chỉ có header `Total tables` là sai thật. Đo lại toàn diện thì file còn
thiếu 14 bảng + 20 cột ở 8 bảng + 7 mục lệch số cột — **toàn bộ là drift tiền tồn tại**, nay đã ghi
thẳng vào đầu file thay vì để trong một commit message không ai đọc.

**F3 đã apply lên DB dev `payroll_engine`** (người dùng xác nhận), có `pg_dump -Fc` 43 MB trước khi
chạy: 3× `ALTER TABLE`, 0 NOTICE, `employees` 213→212 cột, 12.044 dòng không đổi, 79 bảng không đổi.
Kiểm lại `tables_db.md` vs DB dev sau khi apply: 65 mục = 65, **0 bullet thừa**, `employees` khớp,
chỉ còn đúng 7 mục drift tiền tồn tại đã ghi trong khối cảnh báo.

**Gate T7:** `go build`/`go vet` rc=0, **917 pass / 9 fail**, danh sách tên test fail IDENTICAL
`origin/develop`. 0 hồi quy.

## Phase 3 — `Core System-backend@feature/workday-bridge-contracts-workhistories` (3 commit)

| Commit | Việc |
|---|---|
| `d628271` | **G1** truncate theo rune + SAVEPOINT quanh upsert hợp đồng (+3 unit test) |
| `257c676` | **G7/G8/G6/TASK-REF** siết 2 câu upsert + 7 test tích hợp DB thật |
| `1a7d43b` | **D3/G4/G5** `POST /adapter-sync/pull` trả 500 khi mọi entity lỗi (+6 test) |

### Hai điều học được lúc thi hành, không có trong PLAN

**1. `NOT EXISTS` đặt chung `WHERE` là SAI với mã trùng.** Bản đầu viết
`... FROM employees e WHERE e.employee_code=$6 AND NOT EXISTS (...) ORDER BY ... LIMIT 1`.
Chạy thử trên dump prod với `employee_code='-1'` (mã trùng 2 công ty): **vẫn chèn**. Lý do:
`NOT EXISTS` được đánh giá trên TỪNG dòng ứng viên TRƯỚC khi `LIMIT` cắt — dòng đã có hợp đồng bị
loại, dòng anh em cùng mã lọt qua. Phải đổi sang CTE `target` chọn nhân viên TRƯỚC rồi mới kiểm
trùng. Sau khi đổi, cả 4 case đều đúng kể cả với mã trùng.

**2. Test tích hợp bắt được lỗi mà kiểm bằng psql không lộ.** Ngay lần chạy đầu:
`pq: inconsistent types deduced for parameter $2`. `INSERT ... SELECT` KHÔNG truyền kiểu cột đích
xuống tham số nằm trong SELECT-list (khác `VALUES`), nên `$2` suy ra `text` ở đó nhưng
`character varying` trong `NOT EXISTS`. Bản kiểm psql thủ công trước đó không lộ vì dùng literal
chứ không dùng tham số. Đã ép kiểu tường minh toàn bộ tham số ở cả 2 câu. **Đây chính là lý do
TASK-REF tồn tại** — nếu chỉ tin unit test fixture thì lỗi này ra thẳng production.

**Gate T13:** `go build`/`go vet` rc=0, **939 pass / 9 fail** (924 + 15 test mới), danh sách tên
test fail IDENTICAL baseline. 0 dòng rác trong DB test sau khi chạy.

## Phase 4 — bàn giao Adapter

- **T14** Nhánh `Core System-adapter@feature/workday-bridge-transfer-changelog` (`a152d98`) **đã xoá**
  theo xác nhận. Patch lưu tại
  `self-docs/files/archive-adapter-workday-transfer-changelog-180826/0001-*.patch` (8.8 KB, đủ cả
  2 file). Repo `Core System-adapter` nay không còn commit nào của luồng việc này —
  `develop` @ `a49095b`, working tree sạch.
- **T15** `self-docs/Adapter-Workday-ChangeLog-Mapping-Template-180826.md` — hợp đồng dữ liệu đầy
  đủ: ranh giới kênh, giao thức con trỏ, bảng field cho `worker` + `worker_transfer_event` kèm
  giới hạn độ dài từng cột, **3 yêu cầu bắt buộc phía Adapter** (G2 refresh phải sinh change log ·
  G3 backfill · G9 múi giờ), bảng "Adapter đổi X → Backend hỏng Y", và 5 câu SQL để đội Adapter tự
  kiểm trước khi báo xong.

## Còn lại (chưa làm, có chủ ý)

- **Phase 2 / Phase 5** — merge vào `develop` và `atlas migrate hash` sau khi merge cả 2 luồng:
  người dùng quyết, chưa push nhánh nào.
- **F7** regen `sqlc` + `tables_code.md` — diff lớn, không ảnh hưởng hành vi, để task riêng.
- **Phase 6** — xác minh Workday thật cho nhánh hợp đồng; điều kiện bật scheduler prod, không phải
  điều kiện merge.
- **G2/G3/G9** — thuộc `Core System-adapter`, đã chuyển thành yêu cầu trong template mapping.

---

# BỔ SUNG 180826 (đợt 2 thi hành) — nhóm A xong + một lỗi review BỎ SÓT

3 commit trên `release/uat-180826`, đã push.

| Commit | Việc |
|---|---|
| `ffdbaed` | **A1** xoá 14 field chết khỏi struct `Employee` + 10 khối gán trong `ApplyESSOverrides` |
| `5e90522` | **A3** sinh lại `internal/db/tables_code.md` từ `schema.sql` |
| `1065d2e` | **A2** sửa dấu phẩy thừa làm `schema.sql` không parse được + regen `sqlc` |

## Lỗi bản review 180826 BỎ SÓT

`internal/db/schema.sql` có **dấu phẩy thừa** ở cuối khối `CREATE TABLE employee_educations`:

```sql
    major_description text DEFAULT ''::text NOT NULL,
);
```

SQL không hợp lệ. Hệ quả: `sqlc generate` chết ngay
(`schema.sql:541:2: syntax error at or near ")"`), và vì `schema.sql` cũng là `src` của
`atlas.hcl` nên luồng *"sửa schema.sql → `atlas migrate diff`"* hỏng theo. Đó là lý do `sqlc` chưa
từng chạy lại kể từ đợt dọn.

Xuất hiện từ commit **`1cba84e`** (đợt 2, 170826) — xoá cột cuối khỏi khối nhưng không gỡ dấu phẩy
của dòng trước. `origin/develop` sạch. Quét lại toàn file: chỉ đúng một khối bị lỗi, nay còn 0.

**Vì sao review không bắt được:** tôi đối chiếu `schema.sql` bằng cách parse bảng/cột bằng regex tự
viết, so số lượng và tên — cách đó vẫn "đọc" được file hỏng. **Bài học: kiểm `schema.sql` bằng chính
công cụ tiêu thụ nó (`sqlc generate`, `atlas migrate diff`), không tự viết parser.**

## Kết quả A1–A3

- `internal/models/employee.go`: −44 dòng. Trước khi xoá đã kiểm dữ liệu thật — 14 dòng
  `employees` có `ess_overrides` khác rỗng, **không dòng nào** chứa 10 key sắp gỡ. Giữ nguyên
  `EmployeeEducation.RefEducationLevelID` (cột khác, vẫn sống).
- `internal/db/gen/models.go`: −456 dòng sau khi `sqlc generate` chạy được. Package `db_gen` vẫn
  **không có file nào import** nên không ảnh hưởng runtime.
- `internal/db/tables_code.md`: sinh lại, 69 bảng (loại `atlas_schema_revisions` vì nằm schema
  riêng), đếm lại 42 repo thật thay cho "~38", thêm cảnh báo drift của chính `schema.sql`.
  Đối chiếu chéo `employee_educations` giữa `tables_code.md` và `sqlc` models: **24 = 24, 0 lệch**.
- `sqlc` v1.31.1 đã cài vào `$(go env GOPATH)/bin` (Makefile vốn đã có target `sqlc generate`).

Mỗi bước đều: `go build`/`go vet` rc=0, `gofmt` sạch, test **975 pass / 20 fail** với fail list
**IDENTICAL** — 0 hồi quy.

---

# ĐÍNH CHÍNH 190826 — con số `Business_Title` tôi đưa ra là SAI

**Đã nói:** *"`Business_Title` đã kiểm trên 8.429/8.429 payload `worker` thật"*.
**Đúng là 8.427/8.429.**

Phát hiện khi tạo dump DB `payroll_adapter` ngày 19/08 và đếm lại bằng SQL trực tiếp thay vì suy ra.

**Sai ở đâu:** ở §1 mục "Trả lời trực tiếp 6 câu hỏi" tôi đo `with_jobdata 8429/8429` — tức
`Worker_Job_Data` khác NULL — rồi **suy ra** rằng `Business_Title` cũng có đủ. Hai chuyện đó không
tương đương. Đếm đúng trường `Business_Title`:

```sql
SELECT count(*) FILTER (WHERE new_raw->'Worker_Data'->'Employment_Data'->'Worker_Job_Data'
                             ->'Position_Data'->>'Business_Title' IS NOT NULL) || ' / ' || count(*)
FROM wd_change_log WHERE entity_type='worker';
--  8427 / 8429
```

**Hai payload thiếu:** `Worker_ID` = **100206** và **EE26000162**. Cả hai CÓ `Position_Data` với 12
khoá (`Position_ID`, `Position_Reference`, `Scheduled_Weekly_Hours`, `Working_FTE`…) nhưng **không
có khoá `Business_Title`**. Không phải sai đường dẫn, không phải `Worker_Job_Data` dạng mảng — đã
kiểm: cả 8429 payload đều có `Worker_Job_Data` kiểu `object`, không có mảng nào.

**Hệ quả thật:** với 2 worker đó backend sẽ ghi `employee_work_histories.position_name` và
`job_title_name` **rỗng**. Đây là hành vi ĐÚNG và đã có test bao
(`TestMapWorkerTransferEvent_MissingWorkerJobData_ReturnsEmptyTitleNotCrash`) — không phải lỗi cần
sửa. `Worker_ID` 100206 **có** trong `employees` của backend (EE26000162 thì không), nên đây là một
ca thật sẽ xảy ra chứ không phải giả thuyết.

**Kết luận không đổi:** nhánh `Business_Title` vẫn là nhánh có căn cứ dữ liệu thật mạnh
(8.427/8.429 = 99,98%), khác hẳn nhánh `Employee_Contracts_Data` vẫn **0/8.429**. Nhưng con số phải
ghi đúng, và bài học lặp lại đúng bài học của lỗi dấu phẩy `schema.sql`: **đo trực tiếp thứ mình
khẳng định, đừng suy ra từ một phép đo lân cận.**

Đã sửa con số ở: `Adapter-Workday-Handover-180826.md`,
`Adapter-Workday-ChangeLog-Mapping-Template-180826.md` (+ bản `.html`),
`Adapter-Workday-Implementation-And-Local-Test-180826.md`,
`llmwiki/wiki/sources/draft/180826-fix-review-db-cleanup-workday-PLAN.md`.
