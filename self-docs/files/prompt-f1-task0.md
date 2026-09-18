---
id: self-docs/files/prompt-f1-task0
canonical_question: 'Technical guide and specification: Prompt dispatch — F1 / Task
  0'
aliases:
- Prompt dispatch — F1 / Task 0
- prompt F1 Task0 040826
entity_type: how_to
domain: self-docs > files
last_verified: 2026-08-04
---

# Prompt dispatch — F1 / Task 0 (dán làm tin nhắn ĐẦU TIÊN của session mới)

Soạn 2026-08-04. Nguồn: `llmwiki/wiki/sources/draft/040826-Core System-template-on-giatbh-engine-PLAN.md`
Task 0 (bản RE-LINK). Phần dưới dấu phân cách là nội dung để copy nguyên văn.

---

Đây là phiên **THI HÀNH theo brief đã chốt**, không phải phiên thiết kế. Thiết kế đã được quyết ở phiên
trước sau khi đo bề mặt code thật; việc của bạn là làm đúng, kiểm bằng lệnh thật, và **dừng lại hỏi** ở
đúng những chỗ được liệt kê — không tự đổi phương án.

Repo: `/Users/thaidt/Documents/Enterprise/Core System`. Nhánh làm việc: `Core System-backend@feature_v2`
(đã đúng nhánh, đừng checkout sang nhánh khác).

## Mục tiêu

Làm cho dữ liệu của **`template_components`** và **`salary_component_overrides`** sống qua mỗi lần
backend restart. Hiện cả hai FK `ON DELETE CASCADE` vào `salary_components(id)`, và
`migrationSalaryComponentsV4` chạy `DELETE FROM salary_components` **mỗi lần boot** → hai bảng con bị
xoá sạch.

Vì sao gấp: `salary_component_overrides` là tính năng **đang chạy thật** (override công thức lương theo
phòng ban/nhân viên, `payroll_service.go` đọc ở 4 điểm tính lương `:240`, `:609`, `:729`, `:914`, có UI
`SalaryComponentOverridesPanel.tsx` từ 250726). HR cấu hình một ngoại lệ lương → restart → ngoại lệ
biến mất **không dấu vết** → lương lặng lẽ về mặc định. Sai tiền, không báo lỗi, không truy vết được.

## Đọc trước khi sửa (đúng 3 chỗ, đừng đọc lan)

1. `llmwiki/wiki/sources/draft/040826-Core System-template-on-giatbh-engine-PLAN.md`:
   - `## Global constraints` (G1–G5) — **bắt buộc**, ràng buộc bao trùm.
   - `### Task 0` — **đây là brief chi tiết của bạn**, 8 bước, có SQL và code mẫu. Làm đúng theo nó.
2. `self-docs/Report-Template-Config-Analysis-040826.md` mục **0** — bằng chứng đo được của khuyết tật.
3. `self-docs/00-START-HERE.md` mục **1** — 5 sự thật kỹ thuật của repo này.

## Sự thật đã xác minh — dùng luôn, KHÔNG đo lại từ đầu

Tất cả đã được kiểm bằng đọc code và truy vấn DB ngày 2026-08-04:

- `migrationSalaryComponentsV4` = `database.go:2587`, mở đầu bằng `DELETE FROM salary_components;`
  (`:2591`, comment của chính nó ghi `-- STEP 1: XÓA TOÀN BỘ (cascade xóa template_components)`),
  **không có `ON CONFLICT`**, không chỉ định cột `id` → mọi component nhận `id` mới mỗi boot.
- Nó nằm trong slice `migrations` (khai báo `database.go:64`, đóng `:286`), phần tử **cuối hiện tại** là
  `migrationSelfHealHideOfficialDays` (`:285`). Mốc comment chữ cái kế tiếp là **BO**.
- `RunMigrations` (`database.go:288-296`): lặp `db.Exec` từng chuỗi, **không transaction, không
  tracking, fail-fast**. ⇒ mọi migration phải **idempotent**, chạy lại mỗi boot.
- `salary_components` có `UNIQUE (code)` → tên constraint `salary_components_code_key`. Đây là điều
  kiện làm phép re-link tất định.
- DDL `template_components` nằm **inline trong `database.go:946`** (const `migrationPayrollTemplates`
  `:937`, wired ở slice `:97`) — **không** ở `migrations/*.sql`. DDL `salary_component_overrides` nằm ở
  `migrations/v38_salary_component_overrides.sql`.
- Tên FK cần drop (tên thật, đã lấy từ `pg_constraint`):
  `template_components_component_id_fkey` và `salary_component_overrides_component_id_fkey`.
- `models.TemplateComponent` (`internal/models/Core System.go:215`) và `models.SalaryComponentOverride`
  (`:130`) **đã có sẵn** field `ComponentCode` dạng joined read-only (`:222` và `:149`) →
  **không cần sửa struct**.
- Hiện `template_components` = **0 dòng**, `salary_component_overrides` = **0 dòng**,
  `payroll_templates` = 1 dòng. ⇒ không có dữ liệu nào bị mất trong lúc bạn làm.
- Helper test: `internal/testutil/dbtest` — `dbtest.Open(t)` tự `t.Skip` khi thiếu `TEST_DATABASE_URL`,
  `dbtest.Exec(t, db, sql, args...)`. **Chưa có file test nào** cho `salary_component_override_repo.go`.
- Backend **không bao giờ chạy Atlas** (`cmd/Core System/main.go:67-82` chỉ gọi `RunMigrations` +
  `RunFileMigrations`) ⇒ **đừng viết gì vào `atlas/migrations/`**.

## Phương án đã chốt: RE-LINK (không re-key)

`component_code` là **khoá bền**. `component_id` **giữ nguyên** nhưng hạ cấp thành **cột dẫn xuất**,
được nối lại từ `component_code` mỗi boot bằng một `UPDATE ... FROM salary_components` đặt **sau** V4.

**Đã cân nhắc và LOẠI phương án re-key** (bỏ `component_id`) — nếu bạn thấy re-key "sạch hơn" thì đó là
đúng về mô hình dữ liệu nhưng **sai về phạm vi đã chốt**: nó đụng 14 hàm của
`salary_component_override_repo.go` (7 hàm là write-path cell-pin của `SetCell`/`UndoCell`), 4 câu SQL
ngoài file đó, **đổi hợp đồng route** `/config/salary-components/{id}/overrides`, và **13 call site
frontend** mà `tsc` không bắt được. **Không làm re-key trong phiên này.**

## Ràng buộc tuyệt đối — vi phạm là DỪNG, không "sửa cho hợp"

1. **KHÔNG đổi semantics `migrationSalaryComponentsV4`** (G5). Không đổi `DELETE+INSERT` thành UPSERT.
   Đó là quyết định riêng chưa chốt và nó sẽ phá chuỗi self-heal BF→BN.
2. **KHÔNG đổi chữ ký hàm nào** ở repo/service/handler. **KHÔNG đổi route.** **KHÔNG đổi JSON
   contract.** **KHÔNG sửa frontend.** **KHÔNG sửa e2e.**
3. **KHÔNG viết vào `atlas/migrations/`** — backend không chạy Atlas.
4. **KHÔNG `DELETE` dòng có `component_code IS NULL`.** Xoá im lặng chính là thứ task này đang sửa. Để
   lại, và viết test đếm/khẳng định hành vi.
5. **KHÔNG đổi** UNIQUE `salary_component_overrides_component_id_scope_type_scope_re_key` sang khoá
   code — đổi nó buộc phải sửa `ON CONFLICT` trong `Create`/`CreateTx`, phình phạm vi. Ghi thành nợ
   trong tài liệu thay vì làm.
6. **KHÔNG sửa `migrationPayrollTemplates`** (`database.go:937`). Const mới chạy sau nó và luôn dọn —
   giữ một nguồn sự thật.
7. Const migration mới phải **exported** (`MigrationDurableComponentCode`) để test chạy lại **chính
   chuỗi SQL đó**, không chép SQL sang test (chép là mời drift).

## Bẫy đã biết (đã có người sập, đừng sập lại)

- **Bẫy 1 — quên đường GHI.** Nếu chỉ thêm cột + backfill mà không sửa 3 câu `INSERT`, mọi dòng MỚI sẽ
  có `component_code = NULL` và mất ở reseed kế → đúng bug đang sửa, chỉ chậm hơn. Ba câu INSERT:
  `payroll_template_repo.go` `ReplaceComponents` (~`:93`), `salary_component_override_repo.go` `Create`
  (~`:81`) và `CreateTx` (~`:110`). Hai câu sau **giống nhau từng chữ** — sửa cả hai như nhau.
- **Bẫy 2 — không idempotent.** `ADD CONSTRAINT`/`ADD PRIMARY KEY` không có `IF NOT EXISTS`. Tiền lệ
  của repo cho việc này là guard `DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE
  conname='…') THEN … END IF; END $$;` (xem `database.go:806-812` và `:1928-1932`). Repo dùng `DO $$`,
  **không** dùng `DO $do$`. Chưa có tiền lệ `ADD PRIMARY KEY` idempotent.
- **Bẫy 3 — test đè DB dev.** Test tích hợp chạy trên `payroll_engine` **thật** (110 component thật).
  **Đừng** chạy `DELETE FROM salary_components` trong test. Mô phỏng reseed bằng một component
  dùng-một-lần (`ZZ_F1_TEST`): xoá đúng nó rồi INSERT lại cùng `code` để nhận `id` mới. Mọi test phải
  `t.Cleanup` dọn sạch.
- **Bẫy 4 — import cycle.** Test ở `internal/repository` cần dùng `database.MigrationDurableComponentCode`.
  Kiểm `internal/database` có import `internal/repository` không **trước khi** viết import. Nếu vướng,
  đặt test trong `internal/database`, hoặc dựng repo bằng struct literal như
  `salary_component_usage_integration_test.go:18` (`repo := &SalaryComponentRepo{db: db}`) đã làm.
- **Bẫy 5 — chép baseline test từ tài liệu.** Tài liệu ghi "6 test RBAC fail sẵn" nhưng con số có thể
  đã lỗi thời. **Tự đo baseline ở bước 1**, lưu ra file, cuối task so đúng danh sách đó.
- **Bẫy 6 — `gofmt -w` cả thư mục.** Đã từng làm hỏng một file không liên quan
  (`salary_component_service.go`, comment bị đổi thành smart-quote). Chỉ chạy `gofmt -l` để **xem**, và
  chỉ format đúng file mình sửa.

## DỪNG và hỏi người dùng, không tự quyết

- **Trước khi áp migration vào DB dev `payroll_engine`.** Trình bày SQL sẽ chạy + ảnh hưởng, chờ xác
  nhận. (Chạy thử trong `BEGIN; … ROLLBACK;` thì không cần hỏi.)
- **Trước khi commit.** Không tự push.
- Nếu phát hiện brief sai so với code thật (tên hàm/cột/constraint không khớp) → **báo ngay, đừng đoán
  rồi làm tiếp**. Repo này đã nhiều lần trả giá vì brief lệch code.
- Nếu thấy buộc phải sửa `engine.go`, `payroll_service.go`, frontend, hoặc route → **dừng**, đó là dấu
  hiệu hiểu sai phạm vi.

## Định nghĩa "xong"

1. `gofmt -l internal/` không liệt kê file bạn sửa; `go build ./...` và `go vet ./...` sạch.
2. `go test ./...` (có `TEST_DATABASE_URL`) — danh sách FAIL **khớp đúng** baseline tự đo ở bước 1,
   không thêm fail mới.
3. Chuỗi SQL migration chạy **hai lần liên tiếp** không lỗi (chứng minh idempotent).
4. `psql payroll_engine -c "\d template_components"` và `"\d salary_component_overrides"` — **không còn**
   constraint `*_component_id_fkey`, và **có** cột `component_code` + index tương ứng.
5. Test mới xanh, và **phải FAIL nếu revert phần sửa** — chạy thử để chứng minh test thật sự bắt được
   bug, đừng chỉ tin nó xanh.
6. **Nghiệm thu ở tầng thật (bắt buộc — đây là điều duy nhất chứng minh mục tiêu đã đạt):** tạo 1
   override thật, **restart backend thật**, kiểm dòng đó **còn nguyên** và `component_id` đã trỏ `id`
   mới của component.

## Khi xong thì ghi tài liệu (đừng bỏ, quy ước repo)

1. `llmwiki/wiki/sources/draft/040826-Core System-template-on-giatbh-engine-PLAN.md` — đổi cột `TT` của
   Task 0 sang `xong` + điền commit + cập nhật dòng "Cập nhật lần cuối". **Đây là nơi duy nhất ghi tiến
   độ.**
2. `self-docs/Report-Template-Config-Analysis-040826.md` — thêm mục kết quả thi hành kèm **số đo thật**
   (output lệnh, không phải mô tả).
3. `self-docs/00-START-HERE.md` — **xoá dòng L1 và L3** khỏi bảng "lỗi đã biết chưa sửa" (quy ước: sửa
   xong thì xoá, không đánh dấu "đã sửa" rồi để tích tụ); cập nhật dòng trạng thái luồng F1 ở mục 3.1.
4. `CLAUDE.md` — thêm một dòng nhật ký, mới nhất lên đầu, format
   `- **DDMMYY** — <việc đã làm> — <tham chiếu file/commit>`.
5. Ghi lại **nợ có ý thức** của phương án re-link: `component_id` là cột dẫn xuất phải nối lại sau V4
   mỗi boot; UNIQUE của overrides vẫn theo `component_id`; dòng mồ côi khi component bị xoá thật.

Bắt đầu bằng bước 1 và bước 2 của Task 0 (đo baseline + chứng minh khuyết tật), báo kết quả cho tôi
xem, rồi mới sửa.
