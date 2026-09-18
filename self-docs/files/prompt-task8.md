---
id: self-docs/files/prompt-task8
canonical_question: 'Technical guide and specification: Brief thi hành — Task 8'
aliases:
- Brief thi hành — Task 8
- prompt Task8 060826
entity_type: how_to
domain: self-docs > files
last_verified: 2026-09-17
---

# Brief thi hành — Task 8 (PLAN 040826-Core System-template-on-giatbh-engine)

**Đây là phiên THI HÀNH theo brief đã chốt, không phải phiên thiết kế.** Xác minh bằng lệnh thật,
dừng và hỏi nếu code thật khác brief hoặc gặp quyết định thiết kế chưa chốt.

**Chạy SAU Task 7** (PLAN: Task 8 bị chặn bởi Task 7). Task 7 sửa
`internal/repository/payroll_template_repo.go` (thêm `BulkAssignByLevelCode` ngay sau
`CreateAssignment`, dòng ~170-179) — brief này CŨNG sửa file đó nhưng ở vị trí khác (gần
`ListAllTemplateComponentCodes`, dòng ~246, và `ReplaceComponents`, dòng ~96-118). **Trước khi sửa,
chạy `grep -n "^func (r \*PayrollTemplateRepo)" internal/repository/payroll_template_repo.go` để lấy
lại đúng số dòng thật sau khi Task 7 đã chèn code — brief này ghi số dòng tại thời điểm viết (060826,
trước Task 7), có thể lệch vài dòng sau khi Task 7 chạy xong, KHÔNG lệch về nội dung/cách tiếp cận.**

## Bối cảnh

PLAN: `llmwiki/wiki/sources/draft/040826-Core System-template-on-giatbh-engine-PLAN.md`, mục "### Task 8
— CHỜ QUYẾT ĐỊNH: ngày hiệu lực cho thành viên template" (đọc nguyên văn — brief này dùng **Hướng 1**
đã chốt: effective-dating đầy đủ cho `template_components`, khuôn `salary_component_versions`).

**Vấn đề đang sửa:** `employee_payroll_templates` có ngày hiệu lực, công thức từng cột
(`salary_component_versions`) có ngày hiệu lực (đóng góp lớn nhất của `giatbh`), nhưng **"template X
gồm cột nào" thì KHÔNG** — sửa danh sách cột của 1 template hôm nay rồi tính lại kỳ QUÁ KHỨ sẽ mask
theo danh sách cột HÔM NAY, đúng lớp bug mà cơ chế versioning công thức vừa loại bỏ ở trục khác.

## Khuôn mẫu đã có — dùng lại nguyên xi, không thiết kế lại (grep xác nhận 060826)

```go
// internal/repository/salary_component_repo.go:43-75 — COALESCE 3 tầng: đúng-ngày → sớm-nhất → hiện tại
func (r *SalaryComponentRepo) ListActiveAsOf(ctx context.Context, asOf time.Time) ([]models.SalaryComponent, error)

// internal/repository/salary_component_repo.go:155-180 — đóng version cũ + mở version mới, 1 transaction
func (r *SalaryComponentRepo) InsertVersion(ctx context.Context, v *models.SalaryComponentVersion) error {
	// UPDATE salary_component_versions SET effective_until=$1 WHERE component_code=$2 AND effective_until IS NULL
	// rồi INSERT dòng mới
}
```

```go
// internal/service/payroll_service.go:440-458 — điểm DUY NHẤT cần đổi để nhất quán với ListActiveAsOf
func (s *PayrollService) loadTemplateMaskData(ctx context.Context, empIDs []uuid.UUID, asOf time.Time) (...) {
	...
	tplCodes, err := s.templateRepo.ListAllTemplateComponentCodes(ctx)  // :452 — KHÔNG lọc ngày, đây là chỗ sửa
	...
}
```

```go
// internal/repository/payroll_template_repo.go — khuôn ReplaceComponents hiện tại (đo 060826, trước Task 7)
func (r *PayrollTemplateRepo) ReplaceComponents(ctx context.Context, templateID uuid.UUID, items []models.TemplateComponent) error {
	// tx.ExecContext: DELETE FROM template_components WHERE template_id = $1
	// for each item: INSERT INTO template_components (template_id, component_id, component_code, sort_order) ...
	// tx.Commit()
}
```

## Các bước

### Bước 1 — bảng mới `template_component_versions`

Sửa `Core System-backend/internal/database/database.go`. Tìm dòng cuối cùng trong slice `migrations`
(chạy `grep -n "^\t\tmigrationReportTemplateTables,\|^\t}" internal/database/database.go` để xác nhận
dòng cuối thật sau khi Task 1 của Report v1 PLAN đã chèn `migrationReportTemplateTables` — mốc chữ
cái tiếp theo sau **BY** là **BZ**). Thêm ngay sau:

```go
		// BZ. 060826 (Task 8, PLAN template): template_component_versions — effective-dating cho
		//     "template X gồm cột nào", khuôn salary_component_versions. Không hàm nào đọc bảng này
		//     cho tới khi Bước 3 sửa loadTemplateMaskData.
		migrationTemplateComponentVersions,
```

Thêm hằng SQL ở cuối file:

```go
const migrationTemplateComponentVersions = `
CREATE TABLE IF NOT EXISTS template_component_versions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id     UUID NOT NULL REFERENCES payroll_templates(id) ON DELETE CASCADE,
    component_code  VARCHAR(50) NOT NULL,
    sort_order      INTEGER NOT NULL DEFAULT 0,
    effective_from  TIMESTAMPTZ NOT NULL,
    effective_until TIMESTAMPTZ,
    created_by      TEXT NOT NULL DEFAULT '',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_tcv_template_from
    ON template_component_versions (template_id, effective_from DESC);

CREATE INDEX IF NOT EXISTS idx_tcv_code_from
    ON template_component_versions (component_code, effective_from DESC);`
```

Khoá theo `component_code` (không FK `salary_components.id`) — tuân G1 (bảng đó phù du). FK
`template_id` vào `payroll_templates(id)` là AN TOÀN (khác `salary_components`, `payroll_templates`
KHÔNG bị V4 xoá mỗi boot).

### Bước 2 — repo: `ListAllTemplateComponentCodesAsOf` + sửa `ReplaceComponents`

Sửa `Core System-backend/internal/repository/payroll_template_repo.go`. Thêm hàm mới ngay sau
`ListAllTemplateComponentCodes` (tìm bằng grep, brief viết trước Task 7 nên số dòng có thể lệch):

```go
// ListAllTemplateComponentCodesAsOf: bản AS-OF của ListAllTemplateComponentCodes (Task 8, 060826) —
// đọc template_component_versions thay vì template_components, nhất quán với ListActiveAsOf của
// giatbh (COALESCE-style: nếu 1 template chưa từng có version nào — vd tạo trước khi Task 8 chạy —
// rơi về template_components hiện tại để không phá vỡ dữ liệu cũ).
func (r *PayrollTemplateRepo) ListAllTemplateComponentCodesAsOf(ctx context.Context, asOf time.Time) (map[uuid.UUID][]string, error) {
	var rows []struct {
		TemplateID uuid.UUID `db:"template_id"`
		Code       string    `db:"code"`
	}
	err := r.db.SelectContext(ctx, &rows, `
		SELECT template_id, component_code AS code
		FROM template_component_versions
		WHERE effective_from <= $1 AND (effective_until IS NULL OR effective_until > $1)
		ORDER BY template_id, sort_order`, asOf)
	if err != nil {
		return nil, err
	}
	out := map[uuid.UUID][]string{}
	haveVersions := map[uuid.UUID]bool{}
	for _, row := range rows {
		out[row.TemplateID] = append(out[row.TemplateID], row.Code)
		haveVersions[row.TemplateID] = true
	}
	// Fallback: template CHƯA từng qua ReplaceComponents sau khi Task 8 triển khai (0 dòng version) —
	// đọc template_components hiện tại để không mất mask của dữ liệu cũ.
	var fallback []struct {
		TemplateID uuid.UUID `db:"template_id"`
		Code       string    `db:"code"`
	}
	if err := r.db.SelectContext(ctx, &fallback, `
		SELECT tc.template_id, c.code
		FROM template_components tc
		JOIN salary_components c ON c.id = tc.component_id
		ORDER BY tc.template_id, tc.sort_order`); err != nil {
		return nil, err
	}
	for _, row := range fallback {
		if !haveVersions[row.TemplateID] {
			out[row.TemplateID] = append(out[row.TemplateID], row.Code)
		}
	}
	return out, nil
}
```

Sửa `ReplaceComponents` — thêm 2 câu vào TRONG transaction hiện có (sau DELETE+INSERT vào
`template_components`, trước `tx.Commit()`):

```go
	// Task 8 (060826): ghi thêm version mới cho template_component_versions — đóng version đang mở,
	// mở version mới đúng tập cột vừa lưu. Cùng transaction với đoạn DELETE+INSERT template_components
	// ở trên — cả hai PHẢI cùng thành công hoặc cùng rollback (không được lệch nhau).
	if _, err := tx.ExecContext(ctx, `
		UPDATE template_component_versions SET effective_until = NOW()
		WHERE template_id = $1 AND effective_until IS NULL`, templateID); err != nil {
		return fmt.Errorf("close previous template component version: %w", err)
	}
	for _, it := range items {
		if _, err := tx.ExecContext(ctx, `
			INSERT INTO template_component_versions (template_id, component_code, sort_order, effective_from)
			VALUES ($1, (SELECT code FROM salary_components WHERE id = $2), $3, NOW())`,
			templateID, it.ComponentID, it.SortOrder); err != nil {
			return fmt.Errorf("insert new template component version: %w", err)
		}
	}
```

Kiểm import `"fmt"` đã có trong file chưa (grep `"fmt"` đầu file) — thêm vào khối import nếu thiếu.

### Bước 3 — wire vào engine

Sửa `Core System-backend/internal/service/payroll_service.go`, dòng ~452 (grep lại số dòng thật — brief
viết trước Task 7, có thể lệch):

```go
	// TRƯỚC: tplCodes, err := s.templateRepo.ListAllTemplateComponentCodes(ctx)
	tplCodes, err := s.templateRepo.ListAllTemplateComponentCodesAsOf(ctx, asOf)
```

Hàm `loadTemplateMaskData` đã nhận `asOf time.Time` sẵn làm tham số (dòng 440) — dùng lại, KHÔNG cần
thêm tham số mới, KHÔNG cần sửa chữ ký hàm hay bất kỳ nơi gọi `loadTemplateMaskData` nào khác.

### Bước 4 — test tích hợp

Tạo `Core System-backend/internal/repository/template_components_versioning_integration_test.go`:

```go
package repository

import (
	"context"
	"os"
	"testing"
	"time"

	"github.com/Enterprise/Core System/internal/models"
	"github.com/jmoiron/sqlx"
	_ "github.com/lib/pq"
)

func TestListAllTemplateComponentCodesAsOf_RespectsHistoricalMembership(t *testing.T) {
	dsn := os.Getenv("TEST_DATABASE_URL")
	if dsn == "" {
		t.Skip("TEST_DATABASE_URL not set")
	}
	db, err := sqlx.Connect("postgres", dsn)
	if err != nil {
		t.Fatalf("connect: %v", err)
	}
	defer db.Close()
	ctx := context.Background()
	repo := &PayrollTemplateRepo{db: db}

	tpl := &models.PayrollTemplate{Name: "TEST_T8_060826"}
	if err := repo.Create(ctx, tpl); err != nil {
		t.Fatalf("create template: %v", err)
	}
	defer db.ExecContext(ctx, `DELETE FROM payroll_templates WHERE id = $1`, tpl.ID)
	defer db.ExecContext(ctx, `DELETE FROM template_component_versions WHERE template_id = $1`, tpl.ID)

	var phoneAllowID string
	if err := db.GetContext(ctx, &phoneAllowID, `SELECT id FROM salary_components WHERE code = 'PHONE_ALLOW'`); err != nil {
		t.Skipf("PHONE_ALLOW không có trong DB test: %v", err)
	}
	var fuelAllowID string
	if err := db.GetContext(ctx, &fuelAllowID, `SELECT id FROM salary_components WHERE code = 'FUEL_ALLOW'`); err != nil {
		t.Skipf("FUEL_ALLOW không có trong DB test: %v", err)
	}

	past := time.Now().Add(-1 * time.Hour)

	// Version 1 (quá khứ): chỉ PHONE_ALLOW.
	if err := repo.ReplaceComponents(ctx, tpl.ID, []models.TemplateComponent{
		{TemplateID: tpl.ID, ComponentID: mustParseUUID(t, phoneAllowID), SortOrder: 0},
	}); err != nil {
		t.Fatalf("ReplaceComponents v1: %v", err)
	}

	// Version 2 (hiện tại): đổi sang FUEL_ALLOW.
	if err := repo.ReplaceComponents(ctx, tpl.ID, []models.TemplateComponent{
		{TemplateID: tpl.ID, ComponentID: mustParseUUID(t, fuelAllowID), SortOrder: 0},
	}); err != nil {
		t.Fatalf("ReplaceComponents v2: %v", err)
	}

	// Đọc AS-OF quá khứ (trước lần đổi thứ 2) — PHẢI vẫn thấy PHONE_ALLOW, KHÔNG phải FUEL_ALLOW.
	codesAtPast, err := repo.ListAllTemplateComponentCodesAsOf(ctx, past)
	if err != nil {
		t.Fatalf("ListAllTemplateComponentCodesAsOf(past): %v", err)
	}
	_ = codesAtPast // past nằm TRƯỚC cả version 1 (được tạo trong test này) nên sẽ rỗng cho template
	                 // này — bài test thật nằm ở đối chiếu NGAY BÂY GIỜ dưới đây.

	codesNow, err := repo.ListAllTemplateComponentCodesAsOf(ctx, time.Now())
	if err != nil {
		t.Fatalf("ListAllTemplateComponentCodesAsOf(now): %v", err)
	}
	found := false
	for _, c := range codesNow[tpl.ID] {
		if c == "FUEL_ALLOW" {
			found = true
		}
		if c == "PHONE_ALLOW" {
			t.Fatalf("version cũ (PHONE_ALLOW) vẫn còn hiệu lực tại NOW() — đóng version cũ chưa đúng")
		}
	}
	if !found {
		t.Fatalf("FUEL_ALLOW (version mới nhất) không có trong kết quả tại NOW(), got %v", codesNow[tpl.ID])
	}
}

func mustParseUUID(t *testing.T, s string) (u [16]byte) {
	t.Helper()
	id, err := parseUUIDHelper(s)
	if err != nil {
		t.Fatalf("parse uuid %q: %v", s, err)
	}
	return id
}
```

**Sửa `mustParseUUID`/`parseUUIDHelper` — đây là chỗ phác thảo còn thiếu, PHẢI hoàn thiện trước khi
chạy, không để lại nguyên văn:** `models.TemplateComponent.ComponentID` có kiểu `uuid.UUID`
(`github.com/google/uuid`), không phải `[16]byte` tự chế — xoá hàm `mustParseUUID`/`parseUUIDHelper`
phác thảo ở trên, dùng thẳng:
```go
componentID, err := uuid.Parse(phoneAllowID)
if err != nil { t.Fatalf("parse uuid: %v", err) }
```
(import `"github.com/google/uuid"`) tại đúng 2 chỗ gọi `ReplaceComponents` ở trên, thay
`mustParseUUID(t, phoneAllowID)` bằng biến `componentID` đã parse.

Chạy: `cd Core System-backend && TEST_DATABASE_URL="postgres://postgres@localhost:5432/payroll_engine?sslmode=disable" go test ./internal/repository/... -run TestListAllTemplateComponentCodesAsOf -v`
Mong đợi: PASS.

### Bước 5 — nghiệm thu ở tầng `loadTemplateMaskData` thật (không chỉ unit test repo)

Chạy lại chuỗi nghiệm thu tương tự Task 5 (kỳ cách ly `2099-xx`, template test, 1 NV test): tạo
template với cột A, gán NV, `Calculate` kỳ test → xác nhận cột A bị mask. Sau đó `ReplaceComponents`
đổi template sang cột B (KHÔNG xoá version cũ theo cách nào khác ngoài `ReplaceComponents`), `Calculate`
LẠI kỳ test CŨ (cùng `periodID`, không phải kỳ mới) → xác nhận mask VẪN áp dụng cho cột A (theo tập
cột tại THỜI ĐIỂM kỳ đó), KHÔNG chuyển sang mask cột B — đây là bằng chứng chính cho việc Task 8 sửa
đúng bug đang nhắm tới.

### Bước 6 — verify

`go build ./... && go vet ./...` → 0 lỗi.
`go test ./internal/repository/... ./internal/service/... -run 'TestListAllTemplateComponentCodesAsOf|TestBuildTemplateMask' -v` → PASS toàn bộ (test cũ của Task 2/Task 4 KHÔNG được vỡ — nếu vỡ, kiểm xem có phải do fallback logic ở Bước 2 xử lý sai template CHƯA từng qua `ReplaceComponents` sau Task 8, các test cũ tạo template bằng đường khác có thể rơi vào nhánh fallback).
Full suite: `go test ./...` → đúng 6 fail baseline, 0 mới.

## Ràng buộc tuyệt đối

- KHÔNG sửa chữ ký `loadTemplateMaskData` (vẫn nhận `asOf` sẵn có, chỉ đổi lời gọi bên trong).
- Version cũ/mới PHẢI trong CÙNG 1 transaction với DELETE+INSERT `template_components` hiện có (không
  tách riêng — lệch nhau sẽ tạo ra tình trạng `template_components` nói khác `template_component_versions`).
- Test dùng mã component thật đã xác nhận tồn tại (`PHONE_ALLOW`/`FUEL_ALLOW`) — nếu 1 trong 2 không
  còn tồn tại lúc thi hành (V4 reseed đổi mã), chọn 2 mã maskable khác còn tồn tại, không tự bịa mã.

## DỪNG và hỏi khi

- Task 7 chưa xong (số dòng `payroll_template_repo.go` sẽ không khớp, dễ chèn nhầm vị trí).
- `PHONE_ALLOW`/`FUEL_ALLOW` không còn tồn tại trong `salary_components` lúc thi hành.
- Test cũ của Task 2/Task 4 vỡ vì fallback logic (Bước 2) — báo lại cụ thể test nào, đừng tự sửa logic
  fallback cho khớp mà không hiểu tại sao vỡ.

## Định nghĩa xong

1. Bảng `template_component_versions` tồn tại, mốc BZ trong `RunMigrations()`.
2. `ListAllTemplateComponentCodesAsOf` hoạt động đúng cả 2 nhánh (có version / fallback không version).
3. `ReplaceComponents` ghi version mới trong cùng transaction.
4. Test tích hợp Bước 4 PASS, nghiệm thu tầng thật Bước 5 xác nhận mask theo đúng thời điểm lịch sử.
5. Full suite đúng baseline, 0 hồi quy.
6. Cập nhật PLAN cột TT Task 8 → `xong`, dòng nhật ký `CLAUDE.md`, và Task 9 (tài liệu tổng kết toàn
   PLAN 040826, tất cả Task 0-8 giờ đã xong) — brief Task 9 sẽ viết riêng sau khi Task 8 xác nhận xong.
7. Commit (backend only) — hỏi xác nhận trước khi commit, không tự push.
