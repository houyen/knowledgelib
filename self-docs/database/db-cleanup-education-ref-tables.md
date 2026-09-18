---
id: self-docs/database/db-cleanup-education-ref-tables
canonical_question: 'Technical guide and specification: DB Cleanup — Xoá bảng `ref_*`
  dư thừa trong cụm học vấn'
aliases:
- DB Cleanup — Xoá bảng `ref_*` dư thừa trong cụm học vấn
- DB Cleanup Education Ref Tables 170826
entity_type: how_to
domain: self-docs > database
last_verified: 2026-09-17
---

# DB Cleanup — Xoá bảng `ref_*` dư thừa trong cụm học vấn (170826, đợt 2)

> ⚠️ **Triển khai:** backend KHÔNG chạy Atlas — các migration của đợt này phải `atlas migrate apply`
> bằng tay, và **bắt buộc deploy code TRƯỚC khi apply**. Xem `self-docs/DB-Cleanup-Deploy-Runbook-180826.md`.

**Trạng thái:** Đã thi hành, chưa merge vào `develop`/`feature_v2`.
**Nhánh:** `Core System-backend@chore/db-cleanup-legacy-tables` (cùng nhánh đợt 1).
**Tài liệu nguồn:** `llmwiki/wiki/sources/draft/170826-db-cleanup-education-ref-tables.md` (SPEC) +
`170826-db-cleanup-education-ref-tables-PLAN.md` (PLAN thi hành).
**Liên quan:** `self-docs/DB-Cleanup-Legacy-Tables-170826.md` (đợt 1, cùng nhánh, khác cụm bảng).

## Bối cảnh

Ngay sau khi hoàn tất đợt 1 (10 bảng legacy), user hỏi tiếp: kiểm tra thông tin học vấn trên
`employee_educations` đã có trên `employees` chưa, và bảng/cột nào dư thừa trong cụm bảng học vấn
hiển thị trên sơ đồ ER (`employee_educations`, `employees`, `majors`, `ref_majors`,
`ref_education_levels`, `ref_academic_degrees`, `ref_graduation_ranks`, `ref_graduate_schools`,
`ref_degree_types`, `ref_training_forms`).

## Phần 1 — Đối chiếu `employee_educations` vs `employees`

5 cột phẳng trên `employees` (`education_level/rank/school/major/year`) trùng khái niệm với 5 cột
trên `employee_educations` (`degree_level/rank/school/major/graduation_year`), nhưng **2 luồng ghi
độc lập không đồng bộ**: `employees.education_*` do HRIS bulk import ghi (`employee_repo.go`),
`employee_educations.*` do form ESS tự khai ghi (`employee_child_repos.go`). Đây là rủi ro kiến
trúc (2 nguồn sự thật) — **ghi nhận, không xử lý trong đợt dọn dẹp này** (Non-goal của SPEC).

Để đọc thông tin học vấn cho report: đọc thẳng 5 cột phẳng trên `employees` (không cần JOIN) nếu
chấp nhận dữ liệu snapshot từ HRIS import; hoặc `LEFT JOIN employee_educations ON employee_id AND
is_primary = true` nếu cần ưu tiên bản nhân viên tự sửa qua ESS (chỉ 335/12044 nhân viên có dòng
`is_primary`, đa số 7711/7742 dòng `employee_educations` là `source='pipeline'` — import hàng loạt
cũ, không có code nào trong 3 repo hiện tại còn ghi loại dòng này).

## Phần 2 — Bảng/cột dư thừa đã xoá

**Điều tra:** grep code cả 3 repo (`feature_v2`/`develop` — nhánh đầy đủ nhất mỗi repo, qua `git
worktree` tạm) đối chiếu số dòng/tỷ lệ NULL thật qua `psql`.

Mỗi bảng `ref_*` trong cụm chỉ có đúng 1 chỗ "chạm" trong code:
`internal/transport/http/ref/handler.go` (endpoint generic `GET /api/v1/ref/{table}`).
- `degree-types`/`training-forms`: có SQL trong map nhưng **frontend chưa từng gọi**.
- `academic-degrees`/`graduation-ranks`/`majors`/`graduate-schools` (tên khoá map, trỏ tới bảng
  `ref_academic_degrees`/`ref_graduation_ranks`/`ref_majors`/`ref_graduate_schools`): frontend CÓ
  gọi (`getRefTable(...)` trong `ess/profile/page.tsx`) nhưng kết quả **fetch về rồi bỏ**, không
  truyền cho component nào — chỉ `refs.educationLevels` (từ `ref_education_levels`) được dùng thật
  (truyền vào `EducationsSection`).
- `ref_majors`/`ref_graduate_schools` dễ nhầm với 2 bảng cùng chủ đề khác tên `majors`/
  `graduate_schools` (không tiền tố `ref_`) — 2 bảng này **đang sống thật** qua endpoint riêng
  (`/api/v1/majors`, `/api/v1/graduate-schools`), dùng autocomplete tự khai học vấn.

**11 cột FK chết** — xác nhận bằng SQL thật trong `employee_child_repos.go` (Create/Update không
có tham số ghi các cột này) và dữ liệu `psql` (toàn bộ 0% ở mọi cột trước khi xoá).

### Rủi ro Workday — đã hỏi, đã xác nhận xoá ngay

Giữa phiên, user cho biết dữ liệu HRIS sắp chuyển sang lấy từ Workday thay vì portal cũ. Đã kiểm
`Core System-adapter` (`feature_v1` + `origin/develop`, dùng bản `develop` đầy đủ hơn 50 commit):
`workday_mapping.md` và toàn bộ `internal/workday/*.go` **không có bất kỳ field nào** map học
vấn/bằng cấp — 0 kết quả grep `education`/`degree`/`major`/`graduat`/`training_form`. Đã hỏi qua
`AskUserQuestion` liệu có nên hoãn xoá để chờ scope Workday education (các bảng `ref_*` này *có
thể* là đích map tương lai) — **user chọn "Vẫn dọn ref_* dư thừa ngay"**, chấp nhận tạo lại bảng
sau nếu Workday thật sự cần.

### Kết quả — 6 bảng + 11 cột đã xoá

| Bảng | Số dòng trước xoá | Backup |
|---|---|---|
| `ref_majors` | 0 | không cần |
| `ref_graduate_schools` | 0 | không cần |
| `ref_academic_degrees` | 7 | `self-docs/files/db-cleanup-170826-education-ref_academic_degrees.sql` |
| `ref_graduation_ranks` | 5 | `self-docs/files/db-cleanup-170826-education-ref_graduation_ranks.sql` |
| `ref_degree_types` | 6 | `self-docs/files/db-cleanup-170826-education-ref_degree_types.sql` |
| `ref_training_forms` | 5 | `self-docs/files/db-cleanup-170826-education-ref_training_forms.sql` |

11 cột FK chết (0/7742 hoặc 0/12044 dòng có giá trị, xác nhận trước khi xoá):
`employee_educations.ref_major_id`, `ref_academic_degree_id`, `ref_rank_id`, `ref_school_id`,
`ref_degree_type_id`, `ref_training_form_id`; `employees.ref_education_level_id`,
`ref_academic_degree_id`, `ref_graduation_rank_id`, `ref_graduate_school_id`, `ref_major_id`.

**Giữ nguyên:** `employee_educations` (bảng, 30→24 cột), `employees` (bảng, 223→218 cột),
`ref_education_levels` (9 dòng, `employee_educations.ref_education_level_id` đang sống —
14/7742 dòng có giá trị, có UI dropdown thật), `majors` (662 dòng), `graduate_schools`.

## Thi hành

1. **Task 1 (GATE):** baseline `go test ./... -p 1` = 918 passed / 8 failed (4 test case đã biết
   trước, không liên quan — route-gate coverage + pipeline 502). Backup 4 bảng có dữ liệu, đối
   chiếu số dòng INSERT khớp tuyệt đối. Xác nhận 11 cột FK 100% NULL trước khi xoá.
2. **Task 2:** migration `atlas/migrations/20260817010000_drop_education_ref_tables.sql` — xoá cột
   (phía trỏ đi) trước, xoá bảng (phía bị trỏ tới) sau → không cần `CASCADE` (khác đợt 1). Preview
   `BEGIN;...ROLLBACK;` xác nhận không có `NOTICE` cascade lạ nào. Áp dụng thật sau khi
   `AskUserQuestion` xác nhận. Sau khi áp dụng: 0 bảng trong 6 bảng đã xoá, 3 bảng sống còn nguyên,
   `employee_educations`/`employees` không mất dòng nào (7742/12044 — khớp trước xoá). `atlas.sum`
   re-hash.
3. **Task 3:** `internal/transport/http/ref/handler.go` — xoá 6 dòng map (`majors`,
   `graduate-schools`, `academic-degrees`, `graduation-ranks`, `degree-types`, `training-forms`),
   giữ `education-levels`. Verify bằng restart backend thật + `curl`: 6 endpoint đã xoá trả `404`
   với `{"error":"unknown ref table: <tên>"}` (không phải lỗi SQL 500), `education-levels` vẫn trả
   `200` với đúng 9 mục.
4. **Task 4:** đồng bộ `internal/db/schema.sql` bằng script Python xoá khối thủ công (tái dùng
   phương pháp đợt 1 — ghép cặp comment-header/SQL-body, giữ nguyên định dạng gốc PG16, không chạy
   lại `pg_dump --schema-only` để tránh diff nhiễu version PG14/PG16). Diff cuối: 338 dòng xoá,
   0 dòng thêm — 0 dấu vết còn lại của 6 bảng + 11 cột, `employee_educations.ref_education_level_id`
   (cột sống, cùng tên khác bảng) còn nguyên.
5. **Task 5:** `internal/db/tables_db.md` — xoá 6 mục bảng (87→81), xoá 6+5 dòng cột tương ứng
   trong `employee_educations` (30→24 cols) và `employees` (223→218 cols).
6. **Task 6 (tài liệu, đang làm — file này):** viết doc canonical, cập nhật `document-map.md`.
7. **Task 7:** `go test ./... -p 1` sau = 918 passed / 8 failed — khớp baseline tuyệt đối, `comm`
   đối chiếu tên test fail cho kết quả rỗng (0 fail mới). `go build`/`go vet` sạch.

## Commit

Trên `Core System-backend@chore/db-cleanup-legacy-tables` (chưa push, chưa merge), nối tiếp 4 commit
đợt 1 (`032a7c2`/`672dc06`/`1c633b1`/`84d0565`):
- `ee13c7a` — chore(db): xoá 6 bảng ref_* + 11 cột FK chết trong cụm học vấn (170826) [migration]
- `a73d05b` — chore(api): xoá 6 endpoint /ref/{table} tương ứng bảng đã xoá (170826)
- `1cba84e` — chore(db): đồng bộ schema.sql sau khi xoá 6 bảng ref_* + 11 cột (170826)
- `fe2d305` — docs(db): xoá 6 mục bảng + 11 cột FK chết khỏi tables_db.md (170826)

## Việc KHÔNG làm (Non-goals, ghi trong SPEC)

- Không đồng bộ 2 luồng ghi học vấn (`employees.education_*` vs `employee_educations.*`) — quyết
  định thiết kế riêng, ngoài phạm vi "xoá bảng dư thừa".
- Không bổ sung tính năng ghi `date_from`/`date_to`/`issued_place` trên `employee_educations`
  (có dữ liệu lịch sử 978/920/56 dòng nhưng `Create`/`Update` hiện tại không ghi được nữa — thiếu
  tính năng, không phải dọn dẹp).
- Không xử lý mapping Workday cho học vấn — chưa có scope, chỉ ghi nhận rủi ro đã hỏi và được xác
  nhận xoá ngay bất kể rủi ro đó.
- Không merge nhánh này vào `develop`/`feature_v2`.
