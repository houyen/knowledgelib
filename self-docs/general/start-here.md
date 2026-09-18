---
id: self-docs/general/start-here
canonical_question: 'Technical guide and specification: 00 — Đầu tài liệu: mở file
  này trước'
aliases:
- '00 — Đầu tài liệu: mở file này trước'
- 00 START HERE
entity_type: how_to
domain: self-docs > general
last_verified: 2026-08-05
---

# 00 — Đầu tài liệu: mở file này trước

**Cập nhật: 2026-08-05.** Đây là trang **trạng thái + điều hướng** cho toàn bộ `self-docs/`. Mở nó ra
là biết: đang có mấy luồng việc, luồng nào đang chờ gì, lỗi nào đã biết mà chưa sửa, và cần đọc file
nào để làm tiếp.

**File này cố ý KHÔNG chứa chi tiết.** Chi tiết nằm trong các file canonical theo hạng mục. Nếu file
này nói khác file canonical thì **file canonical đúng** — và hãy sửa lại dòng ở đây. Giữ nó mỏng là
điều kiện để nó không mục đi như một bản tóm tắt lỗi thời.

Phân vai với hai file index đã có:

| File | Trả lời câu hỏi |
|---|---|
| **`00-START-HERE.md`** (file này) | *Đang ở đâu? Làm gì tiếp? Đọc file nào?* |
| `document-map.md` | *File X là gì?* — catalog đầy đủ mọi tài liệu, 60 mục |
| `CLAUDE.md` mục "Nhật ký công việc theo ngày" (ở thư mục gốc) | *Hôm đó đã làm gì?* — lịch sử theo ngày, mới nhất lên đầu |

---

## 0. Bắt đầu làm việc — mở theo đúng thứ tự này

Ba loại thông tin nằm ở ba loại file khác nhau. Biết trước cái nào ở đâu thì không phải đi tìm:

| Cần gì | Ở đâu |
|---|---|
| **Tiến độ** (task nào xong/chưa, việc kế tiếp) | mục **"Tiến độ + bảng trạng thái task"** ngay đầu file PLAN — cột `TT` + dòng "Cập nhật lần cuối". **Đây là nơi duy nhất ghi tiến độ**, đừng tìm ở chỗ khác |
| **Chi tiết thi hành** (sửa file nào, bước nào, code mẫu, lệnh verify) | file **PLAN** trong `llmwiki/wiki/sources/draft/` — mỗi task có `Files` + `Interfaces` + các bước có code thật |
| **Phân tích / bằng chứng** (vì sao làm thế, đo được gì) | file **canonical** trong `self-docs/` |

Nói ngắn: **`self-docs/` trả lời "vì sao", `llmwiki/.../*-PLAN.md` trả lời "làm thế nào".** File PLAN
nằm ngoài `self-docs/` vì harness bắt buộc PLAN ở `llmwiki/` để nó gác chuẩn dispatch (R7/R18) — nên
đường dẫn đầy đủ được ghi rõ ở từng luồng việc trong mục 3 bên dưới.

### Việc kế tiếp (180826): **mục 3.4 — đưa `feature_v2` + dọn DB + cầu nối Workday lên `develop`/UAT.**
### Thứ tự đã chốt: merge 3 MR (`feature_v2` → dọn DB → Workday) rồi mới `atlas migrate apply` MỘT
### lần cho cả 8 migration. **Đọc mục 3.4 trước khi merge bất cứ MR nào** — có 2 xung đột đã biết
### trước kèm cách giải, và một quy tắc không được đảo: code lên trước, DB đổi sau.

1. **File này**, mục 1 (5 sự thật kỹ thuật) và mục 2 (lỗi còn mở — không còn cái nào, L1-L11 đã đóng
   hết). Khoảng 5 phút.
2. **`llmwiki/wiki/sources/draft/040826-Core System-template-on-giatbh-engine-PLAN.md`** — đọc
   `## Global constraints` (G1–G5, **bắt buộc**, mọi task ngầm mang theo), rồi `## Tiến độ` (Task
   0-9 đều xong, tóm tắt đầy đủ ở dòng "Cập nhật lần cuối", kèm commit hash từng task).
3. **`RBAC-Backlog-Tracklist-160726.md` mục A3** — L10 (RLS/superuser), đã đóng ở dev local
   (`payroll_app_role`), số đo thật + phạm vi (chưa đẩy staging/production).
4. **`Report-Template-Config-Analysis-040826.md` mục 0** — bằng chứng đo được cho L1/L3/L4 (bảng phù
   du, CASCADE, bootstrap đặt sai chỗ) + mục 0.4/0.6 (kết quả thi hành Task 0/Task 1 kèm số đo thật).
5. **`Salary-Structure-Template-Analysis-260726.md` mục 16 + 17** — quy tắc mask "cột nguồn nghiêm" +
   `templateMaskSiblingSplits` (mục 16.5/16.6/16.7 — Task 3 đã dùng lại đúng các hàm này qua
   `templateMaskEligible`), và mục 17 (kết quả thi hành Task 4 — đóng cổng duyệt shadow-mode).

Nếu chỉ có 10 phút và muốn bắt tay ngay: file này mục 1 → PLAN `Global constraints` → PLAN mục Tiến độ.

---

## 1. Sự thật kỹ thuật phải biết TRƯỚC khi sửa bất cứ thứ gì

Năm điều này đã làm sai lệch nhiều phiên trước. Đọc hết mục này trước khi chạm code.

| # | Sự thật | Hệ quả nếu không biết |
|---|---|---|
| 1 | **`salary_components` là bảng PHÙ DU.** `migrationSalaryComponentsV4` chạy `DELETE FROM salary_components` + reseed 109 mã hardcode **mỗi lần backend boot** (`AUTO_MIGRATE=true` là mặc định) | Mọi cột lương HR tạo qua UI biến mất sau restart; mọi bảng FK vào `salary_components(id)` bị xoá theo |
| 2 | **Backend KHÔNG BAO GIỜ chạy Atlas.** `cmd/Core System/main.go` chỉ gọi `RunMigrations()` + `RunFileMigrations()` | Migration viết trong `atlas/migrations/` **không bao giờ tự chạy** — bảng sẽ thiếu ở môi trường sạch |
| 3 | **File `migrations/vNN.sql` sống đúng MỘT boot.** `RunMigrations()` (chứa V4) chạy TRƯỚC `RunFileMigrations()`; lần sau `schema_migrations` coi file đã chạy nên không chạy lại, còn V4 vẫn xoá | Fix trong `vNN.sql` mất sau restart kế. Đã xảy ra thật: 13 mã của `v51_*.sql` mất sạch |
| 4 | **Nhánh làm việc là `feature_v2`** (backend + frontend), `feature_v1` (adapter). `feature_v2` HEAD **chính là `origin/giatbh`** (`bf1f46e`) | Tài liệu cũ ghi `sec_dev`/`feature_1` đã lỗi thời. Engine hiện tại là engine của `giatbh` |
| 5 | **Test có fail sẵn từ trước — đo thật 050826 là 7 case** ở `HEAD~1` của `036cd67` (`HANDOVER-giatbh.md` mục 3 ghi 6, **thiếu** `TestIntegrationCalculateOnePointInTimeFormula`). Thêm nữa: `TestIntegrationComputeFormulaImpactComputesDeltaWithoutWriting` **fail ngẫu nhiên** vì nó assert số đếm TOÀN CỤC `payroll_records` trong khi Go chạy các package test song song trên cùng DB dev | Đừng chép con số từ tài liệu nào — **tự đo baseline trước khi sửa dòng đầu tiên**. Và nếu thấy 1 fail lạ, **chạy cách ly test đó** trước khi kết luận hồi quy |

Nguồn: `Report-Template-Config-Analysis-040826.md` mục 0 (có bằng chứng đo được),
`Core System-backend/HANDOVER-giatbh.md`.

---

## 2. Lỗi đã biết, CHƯA SỬA — xếp theo mức gây hại

Đây là mục quan trọng nhất của file này. Tất cả đều đã có bằng chứng, không phải phỏng đoán.

**Không còn lỗi nào trong bảng này (060826) — L1-L11 đều đã đóng.** L10 (RLS vô hiệu vì app chạy bằng
superuser) là lỗi cuối cùng, đóng bằng đổi DB role sang `payroll_app_role` (NOSUPERUSER/NOBYPASSRLS)
— **chỉ ở dev local**, xem `RBAC-Backlog-Tracklist-160726.md` mục A3 để có số đo thật + phạm vi (chưa
làm ở staging/production).

---

## 3. Ba luồng việc đang mở

### 3.1 NỀN — hai bảng con thoát khỏi CASCADE + bootstrap ra khỏi Atlas (F1/F2) — **xong 050826**

Đóng L1, L3 (Task 0), L4 + L11 (Task 1). Không cần quyết định thiết kế nào. Cả 2 task đã xong trong
cùng ngày 050826.

- Đọc: `llmwiki/wiki/sources/draft/040826-Core System-template-on-giatbh-engine-PLAN.md` **Task 0** (RE-LINK
  — `component_code` là khoá bền, đã kiểm chứng độc lập) và **Task 1** (bootstrap 2 nạn nhân cùng gốc
  — `employee_payroll_templates` + backfill `salary_component_versions`).
- **Task 0: xong** — migration `database.MigrationDurableComponentCode` (mốc BO), 3 câu INSERT đã sửa
  ghi `component_code`, 4 test mới, nghiệm thu qua restart backend thật. Commit `036cd67`, chưa push.
- **Task 1: xong** — `MigrationEmployeePayrollTemplatesTable` (mốc BP) + `MigrationSeedInitialComponentVersions`
  (mốc BQ, `effective_from=now()`), `TemplateEnforceHealth` fail-loud khi bảng thiếu, 2 test mới
  (rename bảng thật + phục hồi), nghiệm thu qua restart backend thật (`healthy:false` + `reason` khi
  đổi tên bảng). Chưa commit (chờ xác nhận).
- Bối cảnh: `Report-Template-Config-Analysis-040826.md` mục 0 (mục 0.4/0.6 — kết quả thi hành Task 0/1
  kèm số đo thật), `Formula-Versioning-PointInTime-050826.md` mục 6 (nghiệm thu L11).
- **Toàn bộ PLAN template (Task 0–9) đã xong (050826/060826).** Không còn việc mở cho luồng này.

### 3.2 Cấu trúc lương theo cấp bậc (Core System template)

Tính năng đã code xong từ 270726–270727 rồi **HOLD**, mở lại 040826 với hướng: lấy engine `giatbh` làm
chuẩn, ta triển khai ý tưởng trên nền đó.

- Canonical: `Salary-Structure-Template-Analysis-260726.md` — **đọc mục 14 và 15 trước**, chúng đính
  chính nhiều kết luận ở mục 7/9/12.
- PLAN thi hành: `llmwiki/wiki/sources/draft/040826-Core System-template-on-giatbh-engine-PLAN.md` (10 task,
  ràng buộc G1–G5).
- **Task 0-8 đã xong (060826).** `SALARY_STRUCTURE_FEATURE_VISIBLE=true` (mở lại ở Task 6),
  `PAYROLL_TEMPLATE_ENFORCE=on` (bật ở Task 5, dev local). Task 9 (tài liệu tổng kết) đã xong.

### 3.3 Cấu hình template báo cáo + tái dùng rule cho payslip

Hạng mục mới 040826. Phân tích xong, phạm vi v1 đã chốt, **PLAN chưa viết**.

- Canonical: `Report-Template-Config-Analysis-040826.md`.
- Đã chốt: v1 chỉ **Nhóm 1** (một dòng mỗi nhân viên + lọc + nhóm + dòng tổng); schema có `doc_type`
  ngay nhưng v1 chỉ thi hành `report`; rule lưu ở **bảng dòng-bố-cục riêng** trỏ `component_code`
  (không nhồi vào `salary_components`).
- **Không phụ thuộc việc sửa V4** — bảng mới khoá theo `code` nên miễn nhiễm sẵn.

---

### 3.4 Dọn dẹp DB + cầu nối Workday (170826 → 180826) — **có việc BẮT BUỘC cho đội `feature_v2`**

Hai luồng độc lập, cả hai đã xong phần code, chưa merge.

| Nhánh | Nội dung | Trạng thái |
|---|---|---|
| `Core System-backend@chore/db-cleanup-legacy-tables` (`d5a8c78`) | 4 đợt dọn DB 170826 (32 bảng + 25 cột) + 5 commit sửa theo review 180826 | **đã push GitLab**, chờ tạo MR vào `develop` |
| `Core System-backend@feature/workday-bridge-contracts-workhistories` (`1a7d43b`) | Cầu nối Workday → `employee_contracts` + `employee_work_histories` | **đã push GitLab**, chờ tạo MR vào `develop` |

> **Thứ tự merge:** merge MR dọn DB trước, MR Workday sau. MR nào merge **sau** sẽ xung đột
> `atlas/migrations/atlas.sum` (đã thử thật, chắc chắn xảy ra) — giữ **cả hai** khối entry rồi chạy
> `atlas migrate hash --dir "file://atlas/migrations"`, sau đó `atlas migrate validate` phải sạch.

#### ⚠️ BẮT BUỘC: ngay sau khi MR dọn DB merge vào `develop`

**Phải merge `develop` → `feature_v2` trước khi `feature_v2` lên bất kỳ môi trường nào.**

`feature_v2` đi trước `develop` và vẫn còn nguyên các khối `CREATE TABLE IF NOT EXISTS` trong
`internal/database/database.go`. Nếu apply migration xoá bảng mà `feature_v2` chưa nuốt bản xoá code
đó, thì ở lần restart backend kế tiếp `RunMigrations()` sẽ **tạo lại 15 bảng vừa xoá**:

```
sync_errors                    employee_insurance_salaries    shift_configs
attendance_items               leave_budgets                  leave_budget_details
leave_requests                 overtime_records               payroll_table_configs
payroll_record_allowances      payroll_record_ot_details      hris_payroll_snapshots
hris_payroll_detail_snapshots  salary_history                 job_rotation_types
```

**Lệnh kiểm sau khi merge — cả 3 phải ra `0`:**

```bash
grep -c 'CREATE TABLE IF NOT EXISTS attendance_items' internal/database/database.go
grep -c 'CREATE TABLE IF NOT EXISTS hris_payroll_snapshots' internal/database/database.go
grep -c 'ref_provinces\|ref_banks\|ref_relation_types' internal/transport/http/ref/handler.go
```

#### Đã diễn tập merge này trên local (180826) — kết quả

Chạy thật trong worktree tạm, không đụng nhánh local nào:

| Bước | Kết quả |
|---|---|
| `develop` ← `chore/db-cleanup-legacy-tables` | merge sạch, **0 file xung đột** |
| `feature_v2` ← `develop` (đã có cleanup) | merge sạch, **0 file xung đột** |
| 15 bảng × `CREATE TABLE IF NOT EXISTS` | **tổng = 0** ✓ |
| 3 endpoint `/ref/*` đã xoá | **0** ✓ |
| 32 bảng đã DROP còn tham chiếu trong `.go` | **không còn cái nào** ✓ |
| `go build` / `go vet` | rc=0 |
| Test `feature_v2` trước merge | **953 pass / 20 fail** |
| Test `feature_v2` sau merge | **953 pass / 20 fail**, danh sách tên fail IDENTICAL ⇒ **0 hồi quy** |

20 fail là tiền tồn tại của `feature_v2`, không liên quan đợt dọn. Đo trên bản sao `payroll_engine`
tạo bằng `pg_dump`/`pg_restore` — **không dùng `CREATE DATABASE ... TEMPLATE payroll_engine`**: nếu
đang mở DBeaver (hoặc client nào) nối vào `payroll_engine` thì lệnh đó **thất bại**, và nếu nuốt
output thì toàn bộ test chạy trên DB không tồn tại và cho ra con số fail vô nghĩa. Đã dính đúng bẫy
này một lần trong phiên 180826.

#### Thứ tự merge + triển khai — **ĐÃ CHỐT 180826 (bản cuối)**

`develop` đang phục vụ UAT. Thay vì 3 MR liên tiếp vào `develop` (mỗi lần là một lượt deploy UAT),
gộp tất cả vào **một nhánh tích hợp** rồi mở **đúng một MR**. UAT chỉ nhận **một** lần deploy, và
mọi xung đột được giải + kiểm xong trên nhánh trước khi `develop` bị chạm tới.

Nguyên tắc vẫn giữ: **merge hết CODE trước, đổi DB một lần duy nhất sau cùng.** Trạng thái ở giữa
(code mới + DB chưa đổi) đã kiểm chứng an toàn vô thời hạn — 32 bảng vẫn còn, code không dùng tới.

##### Giai đoạn 1 — nhánh tích hợp (một MR duy nhất)

Nhánh **`release/uat-180826`** đã dựng và đã push, `origin/release/uat-180826` @ `6d612f2`:

```
release/uat-180826  =  feature_v2
                     + chore/db-cleanup-legacy-tables
                     + feature/workday-bridge-contracts-workhistories
```

| Bước | Việc | Cổng phải qua |
|---|---|---|
| **B0** | `pg_dump -Fc` DB UAT | có backup trước khi bắt đầu |
| **B1** | Mở MR `release/uat-180826` → `develop`, merge | UAT nhận toàn bộ trong một lần. 4 bảng mới của `feature_v2` **tự tạo lúc boot**, không cần thao tác DB. Smoke test UAT |

**Hai MR cũ nhắm thẳng vào `develop` giờ đã thừa** — nhánh tích hợp bao trọn nội dung của chúng.
Đóng MR !29 (`chore/db-cleanup-legacy-tables` → `develop`) và MR của nhánh Workday nếu đã mở. Hai
nhánh nguồn cứ giữ lại để truy vết, không cần xoá.

**Xung đột đã giải sẵn trên nhánh tích hợp**, không phải làm lại lúc merge:
- `atlas/migrations/atlas.sum` — giữ cả hai khối entry rồi `atlas migrate hash`. Kết quả: 33 file,
  33 dòng trong sum.
- `docs/routes-permissions.md` — cả hai nhánh cùng chèn một mục mới trước `## Cross-reference`.
  Giữ cả hai: `## Report Templates …` → `## Cầu nối Workday …` → `## Cross-reference`.

##### Sau khi MR merge — BẮT BUỘC đồng bộ ngược `feature_v2`

`release/uat-180826` tách ra từ `feature_v2`, nên sau khi nó vào `develop` thì `feature_v2` vẫn
**chưa** có phần dọn DB + Workday. Ai còn làm việc trên `feature_v2` phải kéo về:

```bash
git checkout feature_v2 && git merge origin/develop
grep -c 'CREATE TABLE IF NOT EXISTS attendance_items' internal/database/database.go   # phải 0
grep -c 'ref_provinces\|ref_banks\|ref_relation_types' internal/transport/http/ref/handler.go  # phải 0
```

Bỏ bước này thì lần merge `feature_v2` kế tiếp sẽ mang 15 khối `CREATE TABLE IF NOT EXISTS` quay
lại — và chúng sẽ tái tạo đúng những bảng vừa xoá ở lần restart backend kế.

##### Giai đoạn 2 — đổi database (một lần duy nhất)

| Bước | Việc | Cổng phải qua |
|---|---|---|
| **B2** | `pg_dump -Fc` DB UAT lần nữa (ảnh chụp sát giờ) | có backup mới |
| **B3** | Apply **11 migration** lên DB UAT **bằng `psql`, KHÔNG dùng `atlas migrate apply`** | **Chỉ được làm SAU khi UAT đã chạy code của B1.** Ngược lại thì lần restart kế `RunMigrations()` tái sinh 15 bảng. Kỳ vọng: đúng **4 NOTICE** `drop cascades to constraint`. Lệnh + thứ tự file: `DB-Cleanup-Deploy-Runbook-180826.md` §B2 |

> ### ⛔ Đừng chạy `atlas migrate apply` trên UAT/production
>
> Đo thật 180826 trên bản sao dump prod: bảng revision Atlas trên prod chỉ ghi **2** mục, trong khi
> thư mục có 32 file. `atlas migrate status` trả `Pending Files: 30 (21 out of order)` kèm
> `ERROR: ... were added out of order` — **Atlas từ chối chạy**. Prod trên thực tế không dùng Atlas
> làm cơ chế migration; mọi thứ apply bằng tay. Apply từng file bằng `psql` trong một transaction.
>
> **Điều kiện trước:** `20260817020000` cần bảng `adapter_sync_state`. Trên dump prod 17/08 nó
> **chưa tồn tại** (`20260813000000_adapter_sync_state.sql` chưa từng chạy trên prod) — phải apply
> file đó trước, nếu không `20260817020000` lỗi `relation "adapter_sync_state" does not exist`.

##### Số bảng sau khi xong tất cả: **79** — bằng đúng dev

Quyết định 180826: đưa prod về **giống hệt** dev, không phải dừng ở 119. Không cần làm trống DB —
42/43 bảng di sản trên prod **rỗng hoàn toàn**, bảng còn lại là `goose_db_version` (31 dòng lịch sử
của công cụ `goose` không còn dùng), và **không bảng đang sống nào FK trỏ vào chúng**.

Chạy thật trên bản sao dump prod 18/08:

| Mốc | Số bảng |
|---|---|
| Dump prod 17/08 nguyên trạng | **146** |
| Sau B1 (boot code đã merge → `RunMigrations` tự tạo 4 bảng của `feature_v2`) | **150** |
| Sau B3 (apply 11 migration) | **79** |

`146 + 4 + 3 (approval_*) + 1 (adapter_sync_state) − 32 (đợt dọn) − 43 (di sản) = 79`

**Danh sách bảng `diff` với dev ra RỖNG.** Dữ liệu nghiệp vụ nguyên vẹn tuyệt đối: `employees`
12.304, `employee_contracts` 25.865, `employee_work_histories` 76.856, `employee_bank_accounts`
10.700, `employee_dependents` 24.530, `employee_educations` 7.742, `org_structures` 892,
`payroll_records` 6.435 — trước = sau. Khởi động lại backend 3 lần: vẫn 79 bảng, không bảng nào
tái sinh. `/adapter-sync/state` trả 200 kèm mảng 2 entity.

Hai điều kiện trước khi apply, **cả hai đều NULL trên dump prod 17/08** — phải apply file tương ứng
trước, xem `DB-Cleanup-Deploy-Runbook-180826.md` §B2:
```sql
SELECT to_regclass('public.adapter_sync_state');   -- cần 20260813000000
SELECT to_regclass('public.approval_requests');    -- cần 20260724000000
```

> **Lỗi prod tiền tồn tại, vá luôn trong đợt này:** `origin/develop` đã có sẵn `approval_repo.go`,
> `approval_service.go` và 2 route `/approvals`, `/admin/approval-rules`, nhưng 3 bảng `approval_*`
> **chưa từng được tạo trên prod** — nghĩa là 2 route đó đang hỏng sẵn trên UAT. Không do đợt dọn
> gây ra. Tự xác nhận trên DB UAT thật bằng câu `to_regclass` ở trên.

Nếu UAT đang có đợt nghiệm thu chạy dở: **giai đoạn 1 vẫn an toàn**, hoãn riêng giai đoạn 2 tới sau
đợt. Hai giai đoạn tách rời được hoàn toàn.

##### Kết quả kiểm trên chính nhánh `release/uat-180826` (180826)

| Kiểm | Kết quả |
|---|---|
| `feature_v2` ← dọn DB | 0 xung đột — **các dòng đã xoá KHÔNG bị `feature_v2` kéo ngược lại** |
| ← Workday | 2 xung đột, đã giải sẵn trên nhánh |
| 15 bảng × `CREATE TABLE IF NOT EXISTS` | tổng = **0** ✓ |
| 3 endpoint `/ref/*` đã xoá | **0** ✓ |
| Code cả 3 nhánh có mặt đủ | ✓ `SAVEPOINT sp_contract`, `allEntitiesFailed`, `report_templates`, `bulk-set` |
| `go build` / `go vet` | rc=0 |
| Test trên `release/uat-180826` | **975 pass / 20 fail** — 953 của `feature_v2` + 22 test mới, fail list IDENTICAL `feature_v2` thuần ⇒ **0 hồi quy** |

##### Điều phải nhớ, không phụ thuộc thứ tự

- **`atlas migrate apply` luôn đi SAU khi môi trường đã chạy code mới.**
- **UAT phải để trống `WD_ADAPTER_URL`.** Nếu set, scheduler chạy 5 phút/lần và ghi thật vào
  `employees`/`employee_contracts`/`employee_work_histories` bằng dữ liệu Workday **chưa được xác
  minh**. Chỉ bật sau khi đội adapter xong V0–V4 và hai bên đã cùng soi một lượt sync thật.
- Migration của nhánh Workday chỉ là **1 câu `INSERT`** vào `adapter_sync_state` — vô hại.
- `feature_v2` **không thêm** file `migrations/v*.sql` nào, **không có** atlas migration riêng, và
  **không có dòng nào chạm** 32 bảng đã xoá.

Chi tiết thi hành B5: `DB-Cleanup-Deploy-Runbook-180826.md` — backend **KHÔNG chạy Atlas** (mục 1
của file này, dòng số 2).

#### Cầu nối Workday — phần của đội adapter

Gửi đội `Core System-adapter` đúng **2 file**:
`Adapter-Workday-Handover-180826.md` (điểm vào — thứ tự việc V0→V4, điều kiện xong) và
`Adapter-Workday-ChangeLog-Mapping-Template-180826.md` (hợp đồng dữ liệu — bảng field, giới hạn cột,
SQL tự kiểm). Bản web của file thứ hai:
https://claude.ai/code/artifact/f493bbe8-5c80-4dd0-8e1c-4dbf7638f1f7

Phần của họ gồm 4 việc có thứ tự phụ thuộc nhau (đường ghi cơ bản → múi giờ → đường refresh →
backfill); chưa làm thì tính năng chỉ chạy một nửa và **mọi cách hỏng đều im lặng**, không có lỗi
nào để lần ra.

- Canonical: `Review-DB-Cleanup-Workday-Bridge-180826.md` (review độc lập 18 phát hiện + mục THI HÀNH).
- PLAN: `llmwiki/wiki/sources/draft/180826-fix-review-db-cleanup-workday-PLAN.md`.

---

### 3.5 Nợ hạ tầng schema — Atlas + `schema.sql` (đo 180826, **chưa sửa**)

Hai thứ này **không chặn** đợt merge UAT, nhưng ai sắp đụng vào migration cần biết trước.

| | Hiện trạng đo được 180826 | Hệ quả |
|---|---|---|
| **C1** | Bảng revision Atlas ghi **1** dòng ở dev, **2** dòng ở prod, trong khi thư mục có **33** file. `atlas migrate status` → `Pending Files: 30 (21 out of order)` + ERROR non-linear. Trên prod dòng `20260812000000` còn có description `add_employee_roles_email` ≠ tên file trong repo (`hr_admin_new_accounts_seed`) | **`atlas migrate apply` không dùng được ở bất kỳ môi trường nào.** Migration phải apply tay bằng `psql` — runbook §B2. `atlas migrate diff`/`validate`/`lint` VẪN dùng bình thường vì không đọc DB |
| **C2** | `internal/db/schema.sql` thiếu **10 bảng** + **10 cột**, thừa 0 (chỉ đi sau, chưa bao giờ sai). 7/10 bảng do `database.go`/`migrations/v*.sql` tạo — atlas không quản; 3 bảng do atlas migration tạo nhưng file chưa sinh lại | `atlas migrate diff` không biết 10 bảng đó tồn tại; `sqlc` sinh models thiếu chúng (vô hại chừng nào `db_gen` chưa ai import) |

**Gốc rễ chung:** hai nguồn schema cạnh tranh — `atlas`/`schema.sql` và `database.go`+`migrations/v*.sql`.
Không nguồn nào đầy đủ.

**Quyết định 180826: làm Mức 1 — chỉ ghi cảnh báo tại chỗ. ✅ ĐÃ XONG.**
Nhánh `chore/atlas-schema-truth-notes` @ `52eddb0`, tách từ **`release/uat-180826`** (không phải
`develop` như dự kiến ban đầu — người dùng đổi để làm ngay, sẽ merge/rebase sau).
**Đã push, CHƯA merge, sẽ cần rebase khi `release/uat-180826` vào `develop`** — dùng
`git push --force-with-lease` sau khi rebase.

Nội dung: khối cảnh báo ở đầu `internal/db/schema.sql` (thay 2 dòng đang nói sai "single source of
truth"/"DO NOT EDIT BY HAND") + khối cảnh báo trong `atlas.hcl` (kèm output thật của
`atlas migrate status`). Verify: `sqlc generate` chạy sạch **không sinh diff**,
`atlas migrate validate` rc=0, `atlas.hcl` vẫn parse, `go build`/`vet` rc=0, 0 file `.go` bị đổi.

**Mức 1 không sửa được lỗi nào** — nó chỉ làm lỗi hiện rõ tại chỗ thay vì để người sau tự vấp.
Cách sửa dứt điểm (baseline Atlas + regen `schema.sql` bằng `pg_dump` 16 qua Docker + migration bù)
nằm ở mục 2 "Mức 3" của cùng file PLAN, kèm 3 cổng chặn — **phần đo đạc đã xong, không phải đo lại**.

---

## 4. Quyết định đang chờ bạn

| # | Quyết định | Chặn việc gì | Phân tích ở |
|---|---|---|---|
| Q3 | **Đổi semantics V4 sang UPSERT**: `DO UPDATE` ghi đè sửa tay của HR, còn `DO NOTHING` làm fix ship trong V4 không áp được — mà chuỗi self-heal BF→BN của `giatbh` đang dựa vào việc V4 luôn thắng | Việc HR tự tạo cột lương và giữ được nó. **Không chặn báo cáo v1** | `Report-Template-Config-Analysis-040826.md` mục 0, ràng buộc **G5** trong PLAN |

Đã chốt trong phiên 040826, ghi lại để không hỏi lại: lấy engine `giatbh` làm chuẩn chính; bật
`PAYROLL_TEMPLATE_ENFORCE=on` **chỉ ở dev local**; sửa nền trước.

Đã chốt trong phiên 060826, ghi lại để không hỏi lại:
- **Q1 → Phương án B** (giữ gán theo nhân viên + công cụ gán hàng loạt, không thêm bảng cấp bậc).
- **Q2 → Hướng 1** (effective-dating đầy đủ cho `template_components`, bảng mới `template_component_versions`).
- **Q4 → xoá sạch** `demo 1` + assignment `THAIDT001` trước khi bật enforce dev local (Task 5).
Chi tiết + ràng buộc thi hành: PLAN mục "Tiến độ" (đoạn ngay dưới bảng task) + Task 7/8/5 tương ứng.

---

## 5. Đọc gì theo chủ đề

| Muốn biết | Mở file |
|---|---|
| Engine tính lương hoạt động thế nào (rule là dữ liệu, topo sort, fail-soft) | `Core System-Engine-Rule-Flow-290726.md` |
| Engine hiện tại của `giatbh` đổi những gì (15 nhóm A–O, versioning hiệu-lực-theo-ngày) | `Core System-backend/HANDOVER-giatbh.md` |
| Ai gọi được route nào (role gate + scope gate) | `Core System-backend/docs/routes-permissions.md` + bản song sinh ở `Core System-frontend/docs/` |
| Toàn cảnh RBAC/phân quyền đã làm gì | `RBAC-Hybrid-Scoping-Implementation-140726.md` (canonical gốc), rồi `RBAC-Backlog-Tracklist-160726.md` (còn nợ gì) |
| Thứ tự ưu tiên giữa 4 cơ chế authorization | `[DOCS]RBAC-Permission-Precedence-220726.md` |
| Versioning công thức theo thời điểm (vì sao kỳ cũ tính sai, chân trời lịch sử, quyết định `effective_from=now()`) | **`Formula-Versioning-PointInTime-050826.md`** — đọc trước khi chạm `salary_component_versions` hoặc `ListActiveAsOf` |
| Thuế TNCN (PIT) | `PIT-Formula-Fix-270726.md` — **lưu ý**: `giatbh` đã sửa PIT lần nữa trên nhánh của họ (commit `cfe2cb9`, 3 nhánh Intern/nước ngoài/luỹ tiến), nên đọc kèm `HANDOVER-giatbh.md` mục D |
| Đồng bộ cột lương + xem trước tác động khi sửa công thức | `Salary-Column-Sync-Impact-280726.md` |
| Bảng chấm công xuất Excel (repo `Core System-adapter`, nhánh `feature_v1`) | `BangCong-Xlsx-Template-Golang-310726.md` |
| Danh mục đầy đủ mọi tài liệu | `document-map.md` |

---

## 6. Quy ước cập nhật file này

**Tiến độ từng task KHÔNG ghi ở đây** — nó ghi ở cột `TT` trong mục "Tiến độ" của file PLAN tương ứng.
File này chỉ giữ trạng thái ở mức luồng việc ("chưa làm", "chờ quyết định"), một dòng mỗi luồng.

Khi làm xong một phần việc có nghĩa, cập nhật **ba** chỗ (bốn nếu có PLAN):

1. **File canonical** của hạng mục đó (chi tiết, bằng chứng, số đo thật) — theo quy ước
   `<Hạng-mục>-DDMMYY.md`, gộp vào file có sẵn thay vì tạo file rời.
2. **File này** — chỉ sửa dòng trạng thái tương ứng (mục 2, 3, 4). Không thêm chi tiết vào đây.
3. **`CLAUDE.md`** mục "Nhật ký công việc theo ngày" — một dòng, mới nhất lên đầu.

Và `document-map.md` nếu có file mới.

Hai điều làm file này mất giá trị nhanh nhất, nên tránh: nhồi chi tiết vào đây (nó sẽ mâu thuẫn với
file canonical), và để một dòng ở mục 2 nằm lại sau khi lỗi đã được sửa (khi sửa xong thì **xoá dòng
đó**, đừng đánh dấu "đã sửa" rồi để tích tụ — lịch sử đã có ở `CLAUDE.md`).
