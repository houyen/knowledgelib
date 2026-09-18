---
id: self-docs/files/prompt-f2-task1
canonical_question: 'Technical guide and specification: Prompt dispatch — F2 / Task
  1'
aliases:
- Prompt dispatch — F2 / Task 1
- prompt F2 Task1 050826
entity_type: how_to
domain: self-docs > files
last_verified: 2026-09-17
---

# Prompt dispatch — F2 / Task 1 (dán làm tin nhắn ĐẦU TIÊN của session mới)

Soạn 2026-08-05. Nguồn: `llmwiki/wiki/sources/draft/040826-Core System-template-on-giatbh-engine-PLAN.md`
Task 1 (bản mở rộng 2 nạn nhân) + `self-docs/Formula-Versioning-PointInTime-050826.md`.
Phần dưới dấu phân cách là nội dung để copy nguyên văn.

---

Đây là phiên **THI HÀNH theo brief đã chốt**, không phải phiên thiết kế. Mọi quyết định thiết kế đã
quyết ở các phiên trước sau khi đo code thật; việc của bạn là làm đúng, kiểm bằng lệnh thật, và **dừng
lại hỏi** ở đúng những chỗ được liệt kê — không tự đổi phương án.

Repo: `/Users/thaidt/Documents/Enterprise/Core System`. Nhánh: `Core System-backend@feature_v2` (đã đúng nhánh,
đừng checkout sang nhánh khác). Task 0 đã xong ở commit `036cd67` — đừng làm lại.

## Mục tiêu

Đưa **bootstrap ra khỏi Atlas**. Có **hai nạn nhân của cùng một gốc**, sửa cả hai trong task này:

- **Phần A (L4)** — `employee_payroll_templates` chỉ được định nghĩa trong `atlas/migrations/`, mà
  backend **không bao giờ chạy Atlas**. Bảng tồn tại trên DB dev này chỉ vì một phiên cũ `psql -f` bằng
  tay. Môi trường sạch → thiếu bảng → `loadTemplateMaskData` nuốt lỗi → enforce âm thầm tắt trong khi
  `GET /Core System/template-enforce-status` vẫn trả `{"enabled": true}`.
- **Phần B (L11, nặng hơn)** — backfill `salary_component_versions` cũng chỉ nằm trong Atlas → bảng
  **tồn tại nhưng 0 dòng** → `ListActiveAsOf` (COALESCE 3 tầng) luôn rơi về tầng cuối `sc.formula` →
  **mọi kỳ lương tính bằng công thức HÔM NAY**. Tức tính năng versioning hiệu-lực-theo-ngày của
  `giatbh` (đóng góp lớn nhất của nhánh đó) đang **vô hiệu**, và đúng cái bug nó được xây để diệt vẫn
  còn nguyên.

## Đọc trước khi sửa

1. `llmwiki/wiki/sources/draft/040826-Core System-template-on-giatbh-engine-PLAN.md`:
   `## Global constraints` (G1–G5, **bắt buộc**) → `## Tiến độ` → `### Task 1` (brief chi tiết của bạn).
2. **`self-docs/Formula-Versioning-PointInTime-050826.md` — ĐỌC HẾT trước khi viết SQL của Phần B.**
   Nó có cơ chế 3 tầng, bảng diễn biến 6 ca, và 4 bẫy đã xác minh. Đây là tài liệu quan trọng nhất của
   phiên này.
3. `self-docs/00-START-HERE.md` mục 1 (5 sự thật kỹ thuật) + mục 2 (bảng lỗi, xem L4 và L11).

## Sự thật đã xác minh — dùng luôn, KHÔNG đo lại từ đầu

- `cmd/Core System/main.go:67-82` chỉ gọi `RunMigrations()` + `RunFileMigrations()` → **Atlas không bao giờ
  chạy**. `AUTO_MIGRATE` mặc định **true** (`internal/config/config.go:110`).
- `RunMigrations` (`internal/database/database.go:288-296`): lặp `db.Exec` từng chuỗi, **không
  transaction, không tracking, fail-fast** ⇒ mọi migration phải **idempotent**, chạy lại mỗi boot.
- Slice `migrations` khai ở `database.go:64`, đóng `:286`... **và đã được Task 0 thêm phần tử ở `:294`**
  (`MigrationDurableComponentCode`). Grep lại để lấy số dòng thật của phần tử cuối trước khi append.
  Mốc comment chữ cái: Task 0 đã dùng **BO**, nên bạn dùng **BP** (Phần A) và **BQ** (Phần B).
- **Phần A rất rẻ:** DDL trong `atlas/migrations/20260726000000_employee_payroll_templates.sql:23-49`
  **vốn đã idempotent** — `CREATE TABLE IF NOT EXISTS`, `CREATE UNIQUE INDEX IF NOT EXISTS`, 2 ×
  `CREATE INDEX IF NOT EXISTS`. Gần như copy được nguyên. **Nhưng** file đó có `COMMENT ON TABLE` ở
  cuối với nội dung **đã lỗi thời** ("Task 4 … CHƯA làm — chờ Approach A1") — **đừng chép comment đó**,
  Task 4 đã làm xong từ 270726.
- **Phần B là cái bẫy:** file Atlas backfill
  `atlas/migrations/20260803020000_salary_component_versions_fix_key.sql:28` là
  `INSERT ... SELECT ... FROM salary_components` **KHÔNG có guard nào** và dùng
  `effective_from = sc.created_at`. **Không được chép.** Xem mục "Bẫy" bên dưới.
- `salary_component_versions` **KHÔNG có unique constraint nào trên `component_code`** (chỉ PK `id` +
  index `idx_salary_component_versions_lookup` không unique) ⇒ **`ON CONFLICT` vô dụng**.
- `InsertVersion` (`internal/repository/salary_component_repo.go:155`) đóng version đang mở
  (`UPDATE ... SET effective_until WHERE effective_until IS NULL`) rồi mới `INSERT` version mới ⇒ bất
  biến "mỗi mã tối đa MỘT version mở". Lưu ý `SalaryComponentRepo.Update` (`:121`) **không** ghi version.
- `loadTemplateMaskData` = `internal/service/payroll_service.go:400`; nó nuốt lỗi thành `nil` ở **hai**
  chỗ `log.Printf("[templateMask] ...(bỏ qua enforce)")`.
- `TemplateEnforceStatus()` = `payroll_service.go:391`, trả `bool`. Handler
  `internal/handler/payroll_template_enforce_status_handler.go` hiện trả
  `map[string]bool{"enabled": ...}` — muốn thêm `reason` (string) thì phải đổi sang `map[string]any`.
- Frontend chỉ đọc `.enabled` (`lib/api/config.ts` khai `{ enabled: boolean }`) ⇒ thêm field mới
  **không phá FE**. **Đừng sửa FE** — việc đó thuộc Task 6.
- **Baseline test ĐO THẬT 050826: 7 case fail** (không phải 6 như `HANDOVER-giatbh.md` mục 3 ghi, cũng
  không phải 24 như một báo cáo cũ). Trong đó `TestIntegrationCalculateOnePointInTimeFormula` fail **tất
  định** vì đúng L11 → **task này phải làm nó chuyển XANH**, tức baseline sau task còn **6**.
- Có **một test fail NGẪU NHIÊN**: `TestIntegrationComputeFormulaImpactComputesDeltaWithoutWriting` —
  nó assert số đếm **TOÀN CỤC** `payroll_records` trong khi Go chạy các package test song song trên cùng
  DB dev. Gặp nó thì **chạy cách ly test đó** trước khi kết luận hồi quy; đừng sửa code vì nó.

## Quyết định đã chốt — không hỏi lại, không tự đổi

**`effective_from = now()`** cho dòng version khởi điểm (người dùng chốt 050826). Mốc đó là **"chân trời
lịch sử"**: từ đó trở đi mọi thay đổi công thức được ghi lại và tính lại kỳ nào cũng đúng; trước đó
không tái tạo được vì lịch sử **chưa từng được ghi**. Lý do đầy đủ + bảng diễn biến 6 ca ở
`self-docs/Formula-Versioning-PointInTime-050826.md` mục 4.

## Ràng buộc tuyệt đối — vi phạm là DỪNG, không "sửa cho hợp"

1. **KHÔNG đổi semantics `migrationSalaryComponentsV4`** (G5).
2. **KHÔNG viết vào `atlas/migrations/`** — backend không chạy Atlas. Mọi thứ vào `RunMigrations()`.
3. **KHÔNG sửa frontend, KHÔNG đổi route, KHÔNG đổi chữ ký hàm nào đang có.** Chỉ được **thêm** method
   mới và **thêm** field vào JSON response.
4. **KHÔNG đổi giá trị lương.** Seed lấy đúng `sc.formula`/`name`/`rounding` hiện tại nên mọi tầng
   COALESCE trả cùng một giá trị ⇒ **số phải KHÔNG đổi**. Có bước nghiệm thu riêng cho điều này — nếu số
   đổi thì bạn đã làm sai, **DỪNG**.
5. **KHÔNG mở rộng phạm vi health-check.** Chỉ kiểm sự tồn tại của `employee_payroll_templates`. Đừng
   kiểm thêm bảng khác, đừng thêm endpoint mới.

## Bẫy đã biết

- **Bẫy 1 (Phần B, nặng nhất) — idempotency: PHẢI `WHERE NOT EXISTS`, KHÔNG `ON CONFLICT`.** Không có
  unique trên `component_code` nên `ON CONFLICT` không có gì để bám. Migration chạy lại **mỗi boot** →
  thiếu guard là chèn thêm ~110 dòng **mỗi lần restart**, bảng phình vô hạn, chuỗi version thành rác.
  SQL đúng nằm nguyên văn trong PLAN Task 1 bước 5 và trong
  `Formula-Versioning-PointInTime-050826.md` mục 5 — dùng đúng bản đó.
- **Bẫy 2 — KHÔNG dùng `sc.created_at` làm `effective_from`.** `salary_components` bị V4 xoá + chèn lại
  mỗi boot nên `created_at` của **mọi** component là *thời điểm boot gần nhất* (đo thật: 110 dòng cùng
  4 ms). Nó nói dối về tuổi component. Dùng `now()` tường minh.
- **Bẫy 3 — `effective_until` của dòng seed phải là `NULL`** (đang mở), để `InsertVersion` đóng nó đúng
  cách ở lần sửa đầu tiên. Seed mà đóng luôn sẽ tạo lỗ giữa hai mốc ở tầng 1.
- **Bẫy 4 — vị trí trong slice.** Seed chụp lại `sc.formula`, nên phải đặt **CUỐI slice**, sau cả chuỗi
  self-heal `BG → BN` **và** `BO` của Task 0. Đặt giữa chuỗi sẽ đóng băng giá trị dở dang — ví dụ
  `INS_SAL_BH` với trần BHXH cũ 46.8tr thay vì 50.6tr mà `BH` sửa sau đó.
- **Bẫy 5 — chép `COMMENT ON TABLE` lỗi thời** từ file Atlas Phần A (nói "Task 4 CHƯA làm"). Viết
  comment mới đúng hiện trạng, hoặc bỏ.
- **Bẫy 6 — `gofmt -w` cả thư mục.** Đã từng làm hỏng một file không liên quan. Chỉ `gofmt -l` để xem,
  format đúng file mình sửa.

## Việc phải làm

Theo đúng PLAN Task 1 (bước 1→6). Tóm ý để bạn định hướng:

- **Phần A:** thêm const `migrationEmployeePayrollTemplatesTable` (port từ Atlas, bỏ comment lỗi thời) +
  append vào slice. Thêm `AssignmentsTableExists(ctx) (bool, error)` cho `PayrollTemplateRepo` bằng
  `SELECT to_regclass('employee_payroll_templates') IS NOT NULL`. Thêm
  `func (s *PayrollService) TemplateEnforceHealth(ctx context.Context) (enabled bool, healthy bool, reason string)`
  — **giữ nguyên** `TemplateEnforceStatus()` cũ (có thể còn caller). Handler trả thêm
  `healthy` + `reason`. Khi `enabled=false` thì `healthy=true`, `reason=""` (không có gì để hỏng).
- **Phần B:** thêm const seed version (SQL đã cho), append **cuối** slice.

## DỪNG và hỏi người dùng, không tự quyết

- **Trước khi áp migration vào DB dev `payroll_engine`** — trình bày SQL + ảnh hưởng, chờ xác nhận.
  (Chạy thử `BEGIN; … ROLLBACK;` thì không cần hỏi.)
- **Trước khi commit.** Không tự push.
- Nếu bước nghiệm thu "số lương không đổi" **thất bại** → DỪNG ngay, báo số cụ thể. Đây là tín hiệu đỏ.
- Nếu brief lệch code thật (tên hàm/cột/số dòng không khớp) → **báo ngay, đừng đoán rồi làm tiếp**.
- Nếu thấy buộc phải sửa `engine.go`, frontend, hoặc route → **dừng**, đó là dấu hiệu hiểu sai phạm vi.

## Định nghĩa "xong"

1. `gofmt -l internal/` không liệt kê file bạn sửa; `go build ./...` + `go vet ./...` sạch.
2. Chạy **chuỗi SQL của cả 2 phần hai lần liên tiếp** không lỗi, và lần hai
   `select count(*) from salary_component_versions` **không đổi** (chứng minh Bẫy 1 đã đóng).
3. `select count(*) from salary_component_versions;` > 0 và **bằng số component**;
   `select min(effective_from), max(effective_from)` — mọi dòng seed cùng một mốc. **Ghi mốc đó lại**
   (đó là chân trời của môi trường dev).
4. **`TestIntegrationCalculateOnePointInTimeFormula` chuyển XANH** — chạy **cách ly** để xác nhận:
   `go test ./internal/service/ -run TestIntegrationCalculateOnePointInTimeFormula -count=1`.
5. `go test ./...` — baseline còn **6 case fail** (giảm 1 so với 7). Nếu thấy 7 vì test flaky ở trên thì
   chạy cách ly nó để loại trừ, và ghi rõ trong báo cáo.
6. **NGHIỆM THU "số không đổi" — bắt buộc.** Trước khi seed: chọn 1 kỳ có dữ liệu, chạy `Calculate`, lưu
   `md5` của toàn bộ `computed_values` + `count(*)` + `sum(...)` của một cột tiền. Sau khi seed: chạy lại
   và **so khớp tuyệt đối**. Khác nhau = làm sai.
7. **Nghiệm thu Phần A ở tầng thật:** đổi tên bảng `employee_payroll_templates` tạm thời (trong
   transaction hoặc rename rồi rename lại), gọi `GET /api/v1/Core System/template-enforce-status` với
   `PAYROLL_TEMPLATE_ENFORCE=on` → phải trả `healthy:false` + `reason` nói rõ, **không** trả
   `{"enabled":true}` trơn như trước.

## Khi xong thì ghi tài liệu (đừng bỏ, quy ước repo)

1. `llmwiki/wiki/sources/draft/040826-...-PLAN.md` — cột `TT` Task 1 → `xong` + commit hash + cập nhật
   dòng "Cập nhật lần cuối". **Đây là nơi duy nhất ghi tiến độ.**
2. `self-docs/Formula-Versioning-PointInTime-050826.md` — thêm mục "kết quả thi hành" kèm **số đo thật**
   (output lệnh), và **ghi mốc chân trời của môi trường dev**.
3. `self-docs/00-START-HERE.md` — **xoá dòng L4 và L11** khỏi bảng "lỗi đã biết chưa sửa" (quy ước: sửa
   xong thì xoá, không đánh dấu "đã sửa" rồi để tích tụ); cập nhật trạng thái luồng F1/F2 ở mục 3.1 và
   "sự thật #5" nếu baseline đổi.
4. `CLAUDE.md` — một dòng nhật ký, mới nhất lên đầu.
5. Ghi lại **nợ còn lại**: không tái tạo được lịch sử công thức trước chân trời; chân trời khác nhau
   giữa dev/staging/prod nên cùng một kỳ có thể ra số khác nhau giữa 2 môi trường.

Bắt đầu bằng bước 1 (đo baseline + xác nhận hiện trạng 2 bảng) và báo kết quả cho tôi xem, rồi mới sửa.
