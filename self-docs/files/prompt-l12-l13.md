---
id: self-docs/files/prompt-l12-l13
canonical_question: 'Technical guide and specification: Prompt dispatch — sửa L12
  + L13'
aliases:
- Prompt dispatch — sửa L12 + L13
- prompt L12 L13 050826
entity_type: how_to
domain: self-docs > files
last_verified: 2026-09-17
---

# Prompt dispatch — sửa L12 + L13 (dán làm tin nhắn ĐẦU TIÊN của session mới)

Soạn 2026-08-05. Nguồn: `self-docs/Formula-Versioning-PointInTime-050826.md` mục **8** (đặc biệt 8.3,
8.4, 8.5). **Không gộp với Task 2** — Task 2 đang chờ một quyết định thiết kế, xem cuối file này.
Phần dưới dấu phân cách là nội dung để copy nguyên văn.

---

Đây là phiên **THI HÀNH một bản sửa nhỏ nhưng nền tảng**, không phải phiên thiết kế. Phạm vi hẹp: **một
migration** trong `internal/database/database.go` + test. Không đụng gì khác.

Repo: `/Users/thaidt/Documents/Enterprise/Core System`. Nhánh: `Core System-backend@feature_v2` (đúng nhánh rồi,
đừng checkout). Task 0 (`6dbe1a6`) và Task 1 (`b4d5ec6`) đã xong và **đã push** — đừng làm lại.

## Bối cảnh: Task 1 đã cài một cái bẫy, chưa gây hại nhưng đã nạp đạn

Task 1 seed một dòng version khởi điểm cho mọi component. Hệ quả không ai lường trước:

`ListActiveAsOf` là COALESCE 3 tầng — tầng 1 (version đúng ngày), tầng 2 (**version sớm nhất, KHÔNG lọc
theo ngày**), tầng 3 (`sc.formula`). Vì sau khi seed **cả 126/126 mã đều có version**, tầng 2 **luôn**
khớp ⇒ **tầng 3 không bao giờ được với tới nữa** ⇒ **`salary_components.formula` không còn ảnh hưởng kết
quả tính lương**.

Hệ quả nghiêm trọng (**L12**): quy ước sửa công thức của repo này là **thêm một migration self-heal ghi
thẳng vào `salary_components`** — đã dùng ít nhất 8 lần (`BG` PIT, `BH` trần BHXH, `BI` HEALTH_INS, `BJ`
OT_TAX, và `BO`–`BU` của đồng nghiệp `giatbh`). Grep xác nhận `database.go` chỉ có **đúng 1** câu
`INSERT INTO salary_component_versions` (chính seed), tức **không migration nào tạo version**. Nên lần
sửa công thức tiếp theo sẽ:

1. đổi `sc.formula` đúng → 2. `psql` kiểm thấy đúng → 3. version đang mở vẫn giữ formula **CŨ** →
4. `Calculate` đọc tầng 1 → **formula CŨ** → 5. **bản sửa vô hiệu, không lỗi, không cảnh báo**.

Đúng loại lỗi tệ nhất: bằng chứng bề mặt nói đã sửa, hành vi thật thì không — và người sửa sẽ đi kiểm
đúng chỗ rồi thấy đúng. Đường CRUD qua UI **không** bị (nó gọi `InsertVersion`, đóng version cũ rồi mở
version mới). Chỉ đường migration bị.

Kèm **L13**: `OT_TAX` và `TRANSPORT_ALLOW` hiện **không có version nào đang mở** (124/126) — rác test
(một test gọi `InsertVersion` rồi `t.Cleanup` xoá dòng mới nhưng không mở lại dòng seed). Nhẹ vì tầng 2
vẫn đỡ, nhưng **seed hiện tại không tự chữa được**: guard của nó là `NOT EXISTS (version nào)` chứ không
phải `NOT EXISTS (version ĐANG MỞ)`.

## Đọc trước khi sửa

1. **`self-docs/Formula-Versioning-PointInTime-050826.md` — mục 2 (cơ chế), mục 8 (toàn bộ).** Đây là
   tài liệu chính. Mục 8.5 có SQL đề xuất.
2. `llmwiki/wiki/sources/draft/040826-Core System-template-on-giatbh-engine-PLAN.md` → `## Global constraints`
   (G1–G5, bắt buộc).

## Sự thật đã xác minh — dùng luôn, KHÔNG đo lại

- Seed hiện tại là const `MigrationSeedInitialComponentVersions` (mốc **BQ**) trong
  `internal/database/database.go`, guard `WHERE NOT EXISTS (SELECT 1 FROM salary_component_versions v
  WHERE v.component_code = sc.code)`.
- `RunMigrations` (`database.go:288-296`): lặp `db.Exec`, **không transaction, không tracking,
  fail-fast** ⇒ migration chạy lại **mỗi boot**, phải idempotent.
- `salary_component_versions` **KHÔNG có unique constraint nào trên `component_code`** (chỉ PK `id` +
  index `idx_salary_component_versions_lookup` không unique) ⇒ **`ON CONFLICT` vô dụng**.
- `InsertVersion` (`internal/repository/salary_component_repo.go:155`) = 2 câu trong transaction: đóng
  version đang mở, rồi chèn version mới. Bất biến mong muốn: **mỗi mã có ĐÚNG MỘT version đang mở**.
- Đo thật 050826: **126 dòng version / 126 component**, **124** mã có version đang mở, **0/126 lệch**
  giữa `sc.formula` và formula của version. Chân trời: `2026-08-05 10:06:06.333616+07`.
- Hai mã mồ côi: `TRANSPORT_ALLOW` (đóng lúc 10:06:40), `OT_TAX` (đóng lúc 10:06:17). Tổng vẫn 126 ⇒
  **không có dòng thay thế nào được chèn**.
- Baseline test đo thật: **6 case fail** (đúng danh sách 6 test RBAC trong `HANDOVER-giatbh.md` mục 3).
  Có thêm **một test fail NGẪU NHIÊN** — `TestIntegrationComputeFormulaImpactComputesDeltaWithoutWriting`
  assert số đếm TOÀN CỤC `payroll_records` trong khi Go chạy package test song song trên cùng DB dev.
  Gặp nó thì **chạy cách ly** trước khi kết luận hồi quy.

## Việc phải làm

**Thay thế** const seed hiện tại (`MigrationSeedInitialComponentVersions`) bằng một migration "hoà giải"
gồm **hai câu**, đặt ở **đúng vị trí cũ** (cuối slice `migrations`). Câu (2) có guard chặt hơn guard cũ
nên **thay luôn được** seed — không giữ hai migration song song.

```sql
-- (1) Đóng version đang mở nếu sc.formula/name/rounding đã lệch (do migration self-heal ghi trực tiếp
--     vào salary_components mà không tạo version — xem L12).
UPDATE salary_component_versions v SET effective_until = now()
  FROM salary_components sc
 WHERE v.component_code = sc.code
   AND v.effective_until IS NULL
   AND (v.formula <> sc.formula OR v.name <> sc.name OR v.rounding <> sc.rounding);

-- (2) Mở version mới cho MỌI mã không còn version đang mở.
--     Bao gồm: mã vừa bị đóng ở (1), component mới thêm, và 2 mã mồ côi do rác test (L13).
INSERT INTO salary_component_versions
  (component_code, formula, name, rounding, effective_from, effective_until, created_by, reason)
SELECT sc.code, sc.formula, sc.name, sc.rounding, now(), NULL, 'reconcile-050826',
       'Dong bo version voi salary_components (self-doc: Formula-Versioning-PointInTime-050826.md muc 8)'
FROM salary_components sc
WHERE NOT EXISTS (
  SELECT 1 FROM salary_component_versions v
   WHERE v.component_code = sc.code AND v.effective_until IS NULL);
```

Giữ nguyên tên const cũ hoặc đổi tên đều được — nhưng **nếu đổi tên thì phải grep test đang tham chiếu**
(Task 0 đã có tiền lệ: tên const `MigrationDurableComponentCode` bị test tham chiếu nên không được đổi).

## Ràng buộc tuyệt đối

1. **KHÔNG đổi semantics `migrationSalaryComponentsV4`** (G5).
2. **KHÔNG viết vào `atlas/migrations/`** — backend không chạy Atlas.
3. **KHÔNG sửa `ListActiveAsOf`**, không sửa COALESCE 3 tầng, không sửa `InsertVersion`. Bản sửa này chỉ
   đồng bộ **dữ liệu**, không đổi cơ chế đọc.
4. **KHÔNG sửa frontend, không đổi route, không đổi chữ ký hàm nào.**
5. **KHÔNG đổi giá trị lương.** Hiện `0/126` lệch, nên câu (1) phải khớp **0 dòng** và câu (2) chỉ chèn
   **2 dòng** (cho 2 mã mồ côi). Có bước nghiệm thu riêng — nếu số khác, DỪNG và báo.
6. **KHÔNG sửa test đang làm rác** (`OT_TAX`/`TRANSPORT_ALLOW`) trong phiên này. Bản sửa migration làm
   nó tự lành mỗi boot; sửa test là việc riêng, ghi thành nợ.

## Bẫy đã biết

- **Bẫy 1 — câu (1) và (2) phải theo ĐÚNG thứ tự đó** trong cùng một chuỗi SQL. Đảo lại thì câu (2) chèn
  trước khi câu (1) đóng, và mã lệch sẽ có **hai** version đang mở → phá đúng bất biến ta đang khôi phục.
- **Bẫy 2 — idempotency.** Chạy lần hai: câu (1) khớp 0 dòng (hết lệch), câu (2) chèn 0 dòng (mọi mã đã
  có version mở). **Phải kiểm bằng cách chạy hai lần và so `count(*)`.**
- **Bẫy 3 — `<>` với NULL.** `v.formula <> sc.formula` sẽ **không** khớp nếu một bên NULL. Kiểm schema:
  `salary_components.formula` và `salary_component_versions.formula` đều `NOT NULL DEFAULT ''` nên an
  toàn — **nhưng hãy tự xác nhận bằng `\d`** trước khi tin. Nếu có cột nullable thì dù
  `IS DISTINCT FROM`.
- **Bẫy 4 — vị trí trong slice.** Phải ở **cuối**, sau toàn bộ self-heal (`BG→BN`), sau `BO`
  (`MigrationDurableComponentCode`) và `BP` (`employee_payroll_templates`). Đặt giữa chuỗi sẽ chụp giá
  trị dở dang — ví dụ `INS_SAL_BH` với trần BHXH cũ 46.8tr thay vì 50.6tr mà `BH` sửa sau đó.
- **Bẫy 5 — `gofmt -w` cả thư mục.** Đã từng làm hỏng một file không liên quan. Chỉ `gofmt -l` để xem.

## DỪNG và hỏi người dùng

- **Trước khi áp migration vào DB dev `payroll_engine`** — trình bày SQL + số dòng sẽ ảnh hưởng, chờ xác
  nhận. (`BEGIN; … ROLLBACK;` để xem trước thì không cần hỏi.)
- **Trước khi commit.** Không tự push.
- Nếu nghiệm thu "số lương không đổi" thất bại, hoặc câu (1) khớp nhiều hơn 0 dòng ở lần chạy đầu →
  **DỪNG**, báo mã nào lệch và lệch thế nào. Đó có thể là dấu hiệu một migration self-heal đã bị vô hiệu
  từ trước mà chưa ai biết — thông tin quan trọng, đừng âm thầm sửa.

## Định nghĩa "xong"

1. `gofmt -l internal/` không liệt kê file bạn sửa; `go build ./...` + `go vet ./...` sạch.
2. Chạy chuỗi SQL **hai lần liên tiếp**: lần một chèn **2 dòng** (2 mã mồ côi) và đóng **0 dòng**; lần
   hai **0/0**. Dán output thật.
3. `select count(*) filter (where effective_until is null)||'/'||count(distinct component_code) from
   salary_component_versions;` → phải là **126/126** (mọi mã có đúng một version đang mở).
4. `select count(*) from salary_components sc join salary_component_versions v on
   v.component_code=sc.code and v.effective_until is null where v.formula <> sc.formula;` → **0**.
5. **Test khoá bất biến mới** — đây là phần quan trọng nhất, đặt trong `internal/repository`
   (dùng `dbtest.Open(t)`, tự `t.Cleanup`):
   `TestReconcile_MigrationFormulaFixTakesEffect` — tạo component `ZZ_L12_TEST` (formula `1`), chạy
   migration để nó có version mở, rồi **mô phỏng một self-heal migration**: `UPDATE salary_components SET
   formula='2' WHERE code='ZZ_L12_TEST'`, chạy lại chuỗi migration, rồi khẳng định
   `ListActiveAsOf(now())` trả **`2`**. **Test này phải FAIL nếu bỏ câu (1)** — chạy thử để chứng minh nó
   thật sự bắt được bug, đừng chỉ tin nó xanh.
   Thêm `TestReconcile_RepairsCodeWithNoOpenVersion` cho L13: đóng tay version đang mở của một component
   dùng-một-lần, chạy migration, khẳng định lại có đúng một version mở.
6. `go test ./...` — vẫn **6 case fail** (không thêm). Nếu thấy 7, chạy cách ly test flaky ở trên để loại
   trừ rồi ghi rõ.
7. **Nghiệm thu tầng thật:** `restart backend thật`, rồi kiểm lại (3) và (4) — phải giữ nguyên, và
   `count(*)` tổng **không tăng** (chứng minh idempotent qua đường `RunMigrations` thật, không chỉ psql).

## Khi xong thì ghi tài liệu

1. `self-docs/Formula-Versioning-PointInTime-050826.md` — thêm mục **9 "Kết quả thi hành bản hoà giải"**
   kèm số đo thật; cập nhật mục **8.5** thành "đã làm" và mục **8.6** (quy ước sửa công thức bằng
   migration nay đã hoạt động lại — nói rõ điều đó).
2. `self-docs/00-START-HERE.md` — **xoá L12 và L13** khỏi bảng lỗi (quy ước: sửa xong thì xoá, không đánh
   dấu "đã sửa" rồi để tích tụ).
3. `llmwiki/wiki/sources/draft/040826-...-PLAN.md` — đây **không phải** task trong PLAN đó, nên chỉ thêm
   một dòng ghi chú ở mục `## Tiến độ` rằng bản sửa L12/L13 đã chen vào trước Task 2, kèm commit.
4. `CLAUDE.md` — một dòng nhật ký, mới nhất lên đầu.
5. Ghi **nợ còn lại**: test làm rác version (`OT_TAX`/`TRANSPORT_ALLOW`) chưa sửa — migration tự lành
   nhưng gốc vẫn còn; và test `...ComputeFormulaImpact...` assert số đếm toàn cục nên fail ngẫu nhiên.

Bắt đầu bằng: đo baseline + chạy `BEGIN; <2 câu> ROLLBACK;` để xem trước số dòng ảnh hưởng, báo cho tôi,
rồi mới sửa code.
