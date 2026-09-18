---
id: self-docs/files/prompt-task7
canonical_question: 'Technical guide and specification: Brief thi hành — Task 7'
aliases:
- Brief thi hành — Task 7
- prompt Task7 060826
entity_type: how_to
domain: self-docs > files
last_verified: 2026-09-17
---

# Brief thi hành — Task 7 (PLAN 040826-Core System-template-on-giatbh-engine)

**Đây là phiên THI HÀNH theo brief đã chốt, không phải phiên thiết kế.** Xác minh bằng lệnh thật,
dừng và hỏi nếu code thật khác brief hoặc gặp quyết định thiết kế chưa chốt.

## Bối cảnh

PLAN: `llmwiki/wiki/sources/draft/040826-Core System-template-on-giatbh-engine-PLAN.md`, mục "### Task 7
— CHỜ QUYẾT ĐỊNH: mô hình gán" (đọc nguyên văn — brief này chỉ dùng **nhánh B**, KHÔNG dùng nhánh A;
bổ sung dòng/file thật + quyết định mới đã chốt ở 060826).

**Quyết định đã chốt (060826):**
- **Q1 → Phương án/Nhánh B** — giữ khoá gán theo NHÂN VIÊN (`employee_payroll_templates`, không đổi
  mô hình dữ liệu), chỉ thêm 1 endpoint gán HÀNG LOẠT theo `level_code`. KHÔNG thêm bảng
  `level_payroll_templates` (đó là nhánh A, đã loại).
- **Ngữ nghĩa xung đột `UNIQUE (employee_id, effective_from)`** khi gán hàng loạt 2 lần cùng ngày cho
  cùng người: **GHI ĐÈ** (`ON CONFLICT ... DO UPDATE SET template_id = EXCLUDED.template_id`) — lần
  gọi sau thay thế `template_id` của dòng đã có cùng `effective_from`, không báo lỗi, không bỏ qua.

Task 5+6 đã xong (dữ liệu demo đã dọn, enforce dev local đang bật, UI đã mở lại). Task 7 build trên
nền đó — KHÔNG cần dọn thêm gì trước khi bắt đầu.

## Đối chiếu 2 field "cấp bậc" — tránh nhầm field (đo thật 060826)

`employees` có **HAI** cột liên quan cấp bậc, độ phủ khác nhau rất nhiều:

```
employees.level_code       (varchar, default '')   — 11383/12044 = 94.5% có giá trị, 58 giá trị khác nhau
employees.employee_level_id (uuid, FK employee_levels) — 6357/12044 = 52.8% có giá trị
```

**Dùng `level_code` cho Task 7** (đúng như mẫu code PLAN đã viết sẵn cho nhánh A cũng dùng
`e.level_code`, không phải `employee_level_id`) — độ phủ cao hơn nhiều, và không cần JOIN
`employee_levels`. `employee_level_id` là field một tính năng KHÁC đang dùng (gợi ý template mặc định
ở `EmployeeTemplateAssignPanel.tsx:56`, `emp.employeeLevelId ? ... : null`) — KHÔNG liên quan tới Task
7, đừng gộp nhầm 2 field này.

## Hàm/route thật đã xác nhận (grep trực tiếp 060826)

```go
// internal/repository/payroll_template_repo.go — các hàm liên quan assignment đã có
func (r *PayrollTemplateRepo) CreateAssignment(ctx context.Context, a *models.EmployeePayrollTemplate) error  // :170
func (r *PayrollTemplateRepo) ListAllAssignments(ctx context.Context, unlimited bool, allowedCompanies []string) (...)  // :149

// internal/service/payroll_template_service.go — service tương ứng
func (s *PayrollTemplateService) CreateAssignment(ctx context.Context, a *models.EmployeePayrollTemplate, by string) error  // :134

// internal/models/Core System.go
type EmployeePayrollTemplate struct {  // :240
    ID uuid.UUID; EmployeeID uuid.UUID; TemplateID uuid.UUID
    EffectiveFrom time.Time; EffectiveTo *time.Time
    CreatedBy, UpdatedBy string; CreatedAt, UpdatedAt time.Time
    EmployeeCode, EmployeeName, TemplateName string  // joined, read-only
}

// internal/app/router.go:363-373 — route block hiện có
r.Route("/employee-Core System-templates", func(r chi.Router) {
    r.With(requireSalaryComponentsView, companyReadScope).Get("/", handlers.PayrollTemplate.ListAllAssignments)
    r.With(requireSalaryComponentsCreate).Post("/", handlers.PayrollTemplate.CreateAssignment)
    r.With(requireSalaryComponentsEdit).Put("/{id}", handlers.PayrollTemplate.UpdateAssignment)
    r.With(requireSalaryComponentsDelete).Delete("/{id}", handlers.PayrollTemplate.DeleteAssignment)
    r.With(requireSalaryComponentsView).Get("/{employeeId}", handlers.PayrollTemplate.ListAssignments)
    r.With(requireSalaryComponentsView).Get("/{employeeId}/resolve", handlers.PayrollTemplate.ResolveAssignedTemplateAsOf)
})
```

Ràng buộc unique hiện có (Task 0, `database.go`): `employee_payroll_templates_emp_from_key UNIQUE
(employee_id, effective_from)` — chính là ràng buộc mà bulk insert sẽ đụng, xử lý bằng
`ON CONFLICT ON CONSTRAINT employee_payroll_templates_emp_from_key DO UPDATE`.

## Các bước

### Bước 1 — repo: bulk insert theo `level_code`

Thêm vào `Core System-backend/internal/repository/payroll_template_repo.go`, ngay sau
`CreateAssignment` (dòng 170-179):

```go
// BulkAssignByLevelCode: gán 1 template cho MỌI nhân viên có level_code khớp, 1 lần
// (Task 7, nhánh B — 060826). ON CONFLICT DO UPDATE: gán lại cùng ngày cho cùng NV
// THAY THẾ template_id cũ (quyết định đã chốt 060826, không bỏ qua/báo lỗi).
func (r *PayrollTemplateRepo) BulkAssignByLevelCode(ctx context.Context, levelCode string, templateID uuid.UUID, effectiveFrom time.Time, by string) (created int, updated int, err error) {
	rows, err := r.db.QueryxContext(ctx, `
		INSERT INTO employee_payroll_templates (employee_id, template_id, effective_from, created_by, updated_by)
		SELECT e.id, $1, $2, $3, $3 FROM employees e WHERE e.level_code = $4
		ON CONFLICT ON CONSTRAINT employee_payroll_templates_emp_from_key
		DO UPDATE SET template_id = EXCLUDED.template_id, updated_by = EXCLUDED.updated_by, updated_at = NOW()
		RETURNING (xmax = 0) AS inserted`,
		templateID, effectiveFrom, by, levelCode)
	if err != nil {
		return 0, 0, err
	}
	defer rows.Close()
	for rows.Next() {
		var inserted bool
		if err := rows.Scan(&inserted); err != nil {
			return created, updated, err
		}
		if inserted {
			created++
		} else {
			updated++
		}
	}
	return created, updated, rows.Err()
}
```

`xmax = 0` là cách chuẩn của Postgres phân biệt dòng vừa INSERT mới (xmax=0) với dòng vừa bị
UPDATE bởi ON CONFLICT (xmax khác 0) — dùng để trả `{created, updated}` chính xác cho FE hiển thị,
không phải đoán.

### Bước 2 — service: validate + gọi repo

Thêm vào `Core System-backend/internal/service/payroll_template_service.go`, ngay sau `CreateAssignment`
(dòng 134-162):

```go
// BulkAssignByLevelCode — Task 7, nhánh B. Validate template tồn tại trước khi insert hàng loạt
// (tránh tạo hàng nghìn dòng trỏ template rác nếu templateID gõ sai).
func (s *PayrollTemplateService) BulkAssignByLevelCode(ctx context.Context, levelCode string, templateID uuid.UUID, effectiveFrom time.Time, by string) (created int, updated int, err error) {
	if levelCode == "" {
		return 0, 0, fmt.Errorf("levelCode required")
	}
	if _, err := s.repo.GetByID(ctx, templateID); err != nil {
		return 0, 0, fmt.Errorf("template not found: %w", err)
	}
	return s.repo.BulkAssignByLevelCode(ctx, levelCode, templateID, effectiveFrom, by)
}
```

Kiểm `fmt` đã import trong file chưa (grep `"fmt"` ở đầu file) — nếu chưa, thêm vào khối import.

### Bước 3 — handler

Thêm vào `Core System-backend/internal/handler/payroll_template_handler.go`, cuối file:

```go
// BulkAssign — Task 7, nhánh B (060826): gán 1 template cho mọi NV cùng level_code.
func (h *PayrollTemplateHandler) BulkAssign(w http.ResponseWriter, r *http.Request) {
	var body struct {
		LevelCode     string `json:"levelCode"`
		TemplateID    string `json:"templateId"`
		EffectiveFrom string `json:"effectiveFrom"`
	}
	if err := json.NewDecoder(r.Body).Decode(&body); err != nil {
		writeError(w, http.StatusBadRequest, "invalid request body")
		return
	}
	templateID, err := uuid.Parse(body.TemplateID)
	if err != nil {
		writeError(w, http.StatusBadRequest, "invalid templateId")
		return
	}
	effectiveFrom, err := time.Parse("2006-01-02", body.EffectiveFrom)
	if err != nil {
		writeError(w, http.StatusBadRequest, "invalid effectiveFrom, expected YYYY-MM-DD")
		return
	}
	created, updated, err := h.svc.BulkAssignByLevelCode(r.Context(), body.LevelCode, templateID, effectiveFrom, actorEmail(r))
	if err != nil {
		writeError(w, http.StatusBadRequest, err.Error())
		return
	}
	writeJSON(w, http.StatusOK, map[string]int{"created": created, "updated": updated})
}
```

Kiểm import `"time"` đã có trong file handler chưa (khác `time` đã dùng ở `DevComponentAsOf` nếu có)
— thêm vào khối import nếu thiếu.

### Bước 4 — route

Sửa `internal/app/router.go`, thêm 1 dòng vào khối `r.Route("/employee-Core System-templates", ...)`
(dòng 363-373), đặt TRƯỚC `Post("/", ...)` để tránh path conflict tương tự lý do đã ghi ở comment
dòng 364-366 (route cụ thể hơn phải khai trước route chung):

```go
			r.With(requireSalaryComponentsCreate).Post("/bulk", handlers.PayrollTemplate.BulkAssign)
```

### Bước 5 — test tích hợp

Tạo `Core System-backend/internal/service/payroll_template_bulk_assign_integration_test.go`:

```go
package service

import (
	"context"
	"os"
	"testing"
	"time"

	"github.com/Enterprise/Core System/internal/models"
	"github.com/Enterprise/Core System/internal/repository"
	"github.com/jmoiron/sqlx"
	_ "github.com/lib/pq"
)

func TestBulkAssignByLevelCode_CreatesForAllMatchingEmployees(t *testing.T) {
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
	repos := repository.NewRepositories(db)
	tplSvc := &PayrollTemplateService{repo: repos.PayrollTemplate}

	// Dựng 2 nhân viên test cách ly, cùng level_code duy nhất KHÔNG trùng dữ liệu thật.
	const testLevelCode = "TEST_TASK7_060826"
	var emp1ID, emp2ID string
	if err := db.GetContext(ctx, &emp1ID, `
		INSERT INTO employees (employee_code, full_name, level_code, company_code)
		VALUES ('TEST_T7_E1', 'Test Emp 1', $1, 'Enterprise') RETURNING id`, testLevelCode); err != nil {
		t.Fatalf("insert emp1: %v", err)
	}
	defer db.ExecContext(ctx, `DELETE FROM employees WHERE id = $1`, emp1ID)
	if err := db.GetContext(ctx, &emp2ID, `
		INSERT INTO employees (employee_code, full_name, level_code, company_code)
		VALUES ('TEST_T7_E2', 'Test Emp 2', $1, 'Enterprise') RETURNING id`, testLevelCode); err != nil {
		t.Fatalf("insert emp2: %v", err)
	}
	defer db.ExecContext(ctx, `DELETE FROM employees WHERE id = $1`, emp2ID)

	tpl := &models.PayrollTemplate{Name: "TEST_T7_060826"}
	if err := tplSvc.Create(ctx, tpl, "test"); err != nil {
		t.Fatalf("create template: %v", err)
	}
	defer db.ExecContext(ctx, `DELETE FROM payroll_templates WHERE id = $1`, tpl.ID)
	defer db.ExecContext(ctx, `DELETE FROM employee_payroll_templates WHERE employee_id IN ($1, $2)`, emp1ID, emp2ID)

	from, _ := time.Parse("2006-01-02", "2026-08-01")
	created, updated, err := tplSvc.BulkAssignByLevelCode(ctx, testLevelCode, tpl.ID, from, "test")
	if err != nil {
		t.Fatalf("BulkAssignByLevelCode: %v", err)
	}
	if created != 2 || updated != 0 {
		t.Fatalf("created=%d updated=%d, want created=2 updated=0", created, updated)
	}

	// Gọi lần 2, cùng effectiveFrom, template khác — kỳ vọng GHI ĐÈ (updated=2, created=0).
	tpl2 := &models.PayrollTemplate{Name: "TEST_T7_060826_v2"}
	if err := tplSvc.Create(ctx, tpl2, "test"); err != nil {
		t.Fatalf("create template2: %v", err)
	}
	defer db.ExecContext(ctx, `DELETE FROM payroll_templates WHERE id = $1`, tpl2.ID)

	created2, updated2, err := tplSvc.BulkAssignByLevelCode(ctx, testLevelCode, tpl2.ID, from, "test")
	if err != nil {
		t.Fatalf("BulkAssignByLevelCode (lần 2): %v", err)
	}
	if created2 != 0 || updated2 != 2 {
		t.Fatalf("created2=%d updated2=%d, want created2=0 updated2=2 (ON CONFLICT DO UPDATE)", created2, updated2)
	}

	// Xác nhận template_id đã đổi thật sang tpl2 (không chỉ đếm đúng số mà giá trị cũng đúng).
	var actualTemplateID string
	if err := db.GetContext(ctx, &actualTemplateID, `
		SELECT template_id FROM employee_payroll_templates WHERE employee_id = $1 AND effective_from = $2`,
		emp1ID, from); err != nil {
		t.Fatalf("verify: %v", err)
	}
	if actualTemplateID != tpl2.ID.String() {
		t.Fatalf("template_id = %q, want %q (ghi đè chưa đúng)", actualTemplateID, tpl2.ID.String())
	}
}
```

Chạy: `cd Core System-backend && TEST_DATABASE_URL="postgres://postgres@localhost:5432/payroll_engine?sslmode=disable" go test ./internal/service/... -run TestBulkAssignByLevelCode -v`
Mong đợi: PASS.

### Bước 6 — FE: thêm nút "Gán theo cấp bậc"

Sửa `Core System-frontend/lib/api/config.ts`, thêm sau `createEmployeeTemplateAssignment` (khoảng dòng
224-226):
```ts
    bulkAssignTemplateByLevel(levelCode: string, templateId: string, effectiveFrom: string) {
      return this.request<{ created: number; updated: number }>(
        "/api/v1/config/employee-Core System-templates/bulk",
        { method: "POST", body: { levelCode, templateId, effectiveFrom } },
      );
    }
```

Sửa `Core System-frontend/components-page/tinh-luong/EmployeeTemplateAssignPanel.tsx` — thêm 1 khối UI
mới "Gán hàng loạt theo cấp bậc" (tách biệt hoàn toàn với luồng gán-từng-người hiện có, KHÔNG trộn
chung state `selected`/`history`), đặt cuối modal trước thẻ đóng `</div></div>` (dòng ~163-166):

```tsx
        <div style={{ marginTop: "18px", paddingTop: "14px", borderTop: "1px solid var(--tl-divider)" }}>
          <div style={{ fontSize: "13px", fontWeight: 600, marginBottom: "6px" }}>Gán hàng loạt theo cấp bậc</div>
          <input value={bulkLevelCode} onChange={(e) => setBulkLevelCode(e.target.value)} placeholder="Mã cấp bậc (level_code)..." style={{ width: "100%", height: "32px", padding: "0 8px", marginBottom: "6px" }} />
          <select value={bulkTemplateId} onChange={(e) => setBulkTemplateId(e.target.value)} style={{ width: "100%", height: "32px", marginBottom: "6px" }}>
            <option value="">-- Chọn cấu trúc lương --</option>
            {templates.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
          </select>
          <input type="date" value={bulkFrom} onChange={(e) => setBulkFrom(e.target.value)} style={{ width: "100%", height: "32px", marginBottom: "6px" }} />
          {bulkResult && <div style={{ fontSize: "12px", color: "var(--tl-text-tertiary)", marginBottom: "6px" }}>Đã tạo mới {bulkResult.created}, ghi đè {bulkResult.updated} bản ghi.</div>}
          {bulkError && <div style={{ color: "#c5221f", fontSize: "12.5px", marginBottom: "6px" }}>{bulkError}</div>}
          <button onClick={bulkAssign} disabled={bulkSubmitting}>{bulkSubmitting ? "Đang gán..." : "Gán hàng loạt"}</button>
        </div>
```

Thêm state + hàm (đặt cạnh state `newTemplateId`/`assign` hiện có, dòng 59-84):
```tsx
  const [bulkLevelCode, setBulkLevelCode] = useState("");
  const [bulkTemplateId, setBulkTemplateId] = useState("");
  const [bulkFrom, setBulkFrom] = useState("");
  const [bulkSubmitting, setBulkSubmitting] = useState(false);
  const [bulkError, setBulkError] = useState<string | null>(null);
  const [bulkResult, setBulkResult] = useState<{ created: number; updated: number } | null>(null);

  const bulkAssign = async () => {
    if (!bulkLevelCode.trim()) { setBulkError("Nhập mã cấp bậc"); return; }
    if (!bulkTemplateId) { setBulkError("Chọn cấu trúc lương"); return; }
    if (!bulkFrom) { setBulkError("Chọn ngày hiệu lực"); return; }
    setBulkSubmitting(true);
    setBulkError(null);
    setBulkResult(null);
    try {
      const result = await api.bulkAssignTemplateByLevel(bulkLevelCode.trim(), bulkTemplateId, bulkFrom);
      setBulkResult(result);
    } catch (e) {
      setBulkError(e instanceof Error ? e.message : String(e));
    } finally {
      setBulkSubmitting(false);
    }
  };
```

### Bước 7 — verify

`go build ./... && go vet ./...` (backend) → 0 lỗi.
`go test ./internal/service/... -run TestBulkAssignByLevelCode -v` → PASS.
`npx tsc --noEmit -p tsconfig.json 2>&1 | grep -v "^e2e/\|^playwright.config"` (frontend) → 0 lỗi.
`npx eslint components-page/tinh-luong/EmployeeTemplateAssignPanel.tsx lib/api/config.ts` → 0 error.

**Nghiệm thu request thật** (kỳ vọng khớp test tích hợp Bước 5, làm lại 1 lần bằng `curl` để chắc
chắn qua đúng route/gate thật, không chỉ qua service trong test):
```bash
curl -s -H "Authorization: Bearer dev" -X POST localhost:8080/api/v1/config/employee-Core System-templates/bulk \
  -d '{"levelCode":"<mã cấp bậc test riêng>","templateId":"<uuid template test>","effectiveFrom":"2026-08-01"}'
```
Dọn dữ liệu test ngay sau khi xác nhận (xoá employee/template/assignment test tạo cho request này).

**Kiểm tay trình duyệt** (nếu môi trường có browser tool — nếu không, ghi debt và để người dùng tự
kiểm như các Task trước): mở modal Gán cấu trúc lương, nhập mã cấp bậc + chọn template + ngày, bấm
"Gán hàng loạt", xác nhận số `created`/`updated` hiện đúng và không ảnh hưởng tới luồng gán-từng-người
hiện có.

## Ràng buộc tuyệt đối

- Dùng `level_code`, KHÔNG dùng `employee_level_id` (2 field khác nhau, khác mục đích — xem mục đối
  chiếu ở trên).
- `ON CONFLICT ... DO UPDATE` — không đổi thành DO NOTHING hay báo lỗi (quyết định đã chốt).
- KHÔNG thêm bảng `level_payroll_templates` (đó là nhánh A, đã loại).
- KHÔNG chạy bulk assign thật trên `level_code` sản xuất (chỉ dùng mã test cách ly khi nghiệm thu).

## DỪNG và hỏi khi

- `employees` không có cột `level_code` (đã kiểm 060826 là có, nhưng nếu schema đổi giữa lúc viết
  brief và lúc thi hành thì báo lại).
- Constraint `employee_payroll_templates_emp_from_key` đã đổi tên/cấu trúc.

## Định nghĩa xong

1. `BulkAssignByLevelCode` (repo+service+handler+route) hoạt động, test tích hợp PASS (cả 2 nhánh:
   tạo mới VÀ ghi đè).
2. `curl` thật xác nhận qua đúng gate/route.
3. FE có form "Gán hàng loạt theo cấp bậc", build/lint sạch.
4. Dữ liệu test đã dọn sạch.
5. Cập nhật PLAN cột TT Task 7 → `xong`, dòng nhật ký `CLAUDE.md`.
6. Commit (2 repo, 2 commit riêng) — hỏi xác nhận trước khi commit, không tự push.
