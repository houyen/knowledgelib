---
id: self-docs/files/prompt-task5
canonical_question: 'Technical guide and specification: Brief thi hành — Task 5'
aliases:
- Brief thi hành — Task 5
- prompt Task5 060826
entity_type: how_to
domain: self-docs > files
last_verified: 2099-01-01
---

# Brief thi hành — Task 5 (PLAN 040826-Core System-template-on-giatbh-engine)

**Đây là phiên THI HÀNH theo brief đã chốt, không phải phiên thiết kế.** Mọi quyết định thiết kế đã
chốt trong các phiên trước — thực thi đúng theo đây, xác minh bằng lệnh thật, dừng và hỏi nếu code
thật khác brief hoặc gặp quyết định thiết kế chưa chốt.

## Bối cảnh — đọc trước khi làm

PLAN: `llmwiki/wiki/sources/draft/040826-Core System-template-on-giatbh-engine-PLAN.md`, mục "### Task 5
— Dọn dữ liệu demo, bật enforce dev local, nghiệm thu end-to-end" (đọc nguyên văn mục đó trước, brief
này bổ sung số đo thật + quyết định đã chốt thêm ở phiên 060826, không thay thế PLAN).

Task 0-4 đã xong, đã push lên `origin/feature_v2` cả 2 repo. Task 5 là **GATE nghiệm thu** — chứng
minh toàn bộ engine mask-về-0 hoạt động đúng ở tầng thật (Calculate/CalculateOne/Finalize), không chỉ
ở test đơn vị. Không có quyết định thiết kế nào còn mở ở task này.

## Trạng thái DB thật đã xác nhận (060826, ngay trước khi giao brief này)

```
payroll_templates: 1 dòng — id=9d76ca57-22dd-424a-af1e-0c8a4758a979, name="demo 1", is_default=false
template_components: 0 dòng cho template trên (template rỗng — đây là lý do PLAN gọi nó "mìn")
employee_payroll_templates: 1 dòng — id=20ef820e-ed08-46c8-94a7-fe8944f4342e,
  employee_id=15c3ddc8-9d41-458f-9bb1-5c3a33d311ae (mã NV: THAIDT001, tên: Thai DT),
  template_id=9d76ca57..., effective_from=2026-07-01, effective_to=NULL
PAYROLL_TEMPLATE_ENFORCE: KHÔNG có trong Core System-backend/.env (enforce đang OFF)
```

**Quyết định người dùng đã chốt (060826): XOÁ SẠCH cả 2 dòng trên** trước khi bật enforce (đúng Q4 —
đây là dữ liệu UAT thử nghiệm, không phải cấu hình thật). KHÔNG hỏi lại quyết định này.

Kỳ lương thật có sẵn để test (không cần tạo kỳ mới):
```
Tháng 05/2026 — id=bae87d46-7be8-4545-8076-df4a30c145fe, 2026-04-21→2026-05-20, 3273 dòng payroll_records
Tháng 02/2026 — id=a86c682e-4ca1-4c59-8aee-ed659259739b, 2026-01-21→2026-02-20, 3162 dòng payroll_records
```
Cả hai đều có `computed_values.GROSS`/`NET_PAY` khác 0 cho nhiều dòng (không phải tất cả — `BASIC_SAL`
riêng bằng 0 ở mọi dòng trong 2 kỳ này, đã xác nhận bằng SELECT, không phải bug). Dùng kỳ 05/2026 cho
bước nghiệm thu — KHÔNG đụng dữ liệu thật của kỳ này bằng cách chỉ dùng `CalculateOne` (tính 1 nhân
viên, không ghi hàng loạt) hoặc dựng 1 kỳ cách ly mới (khuyến nghị, xem Bẫy 1).

## Hàm/route thật đã xác nhận (grep trực tiếp, không suy đoán)

```go
// internal/service/payroll_service.go
func (s *PayrollService) TemplateEnforceHealth(ctx context.Context) (enabled bool, healthy bool, reason string)  // :405
func (s *PayrollService) Calculate(ctx context.Context, periodID uuid.UUID, salaryOverrides map[string]float64) error  // :204
func (s *PayrollService) CalculateOne(ctx context.Context, periodID uuid.UUID, empCode string, basicSalary float64) (models.ComputedValues, models.ComputedValues, error)  // :620
func (s *PayrollService) Finalize(ctx context.Context, periodID uuid.UUID) error  // :1606
func (s *PayrollService) ComputeTemplateImpact(ctx context.Context, periodID uuid.UUID, salaries map[string]float64) (*TemplateImpactReport, error)  // :764
```

```go
// internal/app/router.go
POST /api/v1/Core System/template-impact/{periodId}       // :489, gate: requirePayrollCalculate+companyReadScope+requireView
GET  /api/v1/Core System/template-enforce-status           // :492, cùng gate
```

## Các bước (theo đúng thứ tự PLAN Task 5)

### Bước 1 — dọn dữ liệu demo

```sql
-- Xác nhận lại lần cuối TRƯỚC KHI xoá (đề phòng ai đã sửa DB giữa lúc brief này viết và lúc thi hành)
SELECT id, name, is_default FROM payroll_templates;
SELECT id, employee_id, template_id, effective_from, effective_to FROM employee_payroll_templates;
-- Nếu khớp đúng 2 dòng ở trên (id, employee_id, template_id giống hệt) → xoá:
DELETE FROM employee_payroll_templates WHERE id = '20ef820e-ed08-46c8-94a7-fe8944f4342e';
DELETE FROM payroll_templates WHERE id = '9d76ca57-22dd-424a-af1e-0c8a4758a979';
```

Nếu dữ liệu KHÔNG khớp (id khác, có thêm dòng mới) — DỪNG, báo lại, không tự đoán xoá cái nào.

### Bước 2 — bật enforce dev local

Thêm 1 dòng vào `Core System-backend/.env` (file này KHÔNG được commit — kiểm bằng `git check-ignore
Core System-backend/.env` trước, nếu không bị ignore thì DỪNG và hỏi, đừng tự thêm `.gitignore`):
```
PAYROLL_TEMPLATE_ENFORCE=on
```

Restart backend (`AUTO_MIGRATE=false go run ./cmd/Core System`), xác nhận:
```bash
curl -s -H "Authorization: Bearer dev" localhost:8080/api/v1/Core System/template-enforce-status
```
Kỳ vọng: `{"enabled":true,"healthy":true}` (vì `template_components`/`employee_payroll_templates` đã
tồn tại từ Task 1, `Ping()` sẽ không lỗi dù bảng rỗng sau bước 1 — xem `TemplateEnforceHealth` ở trên,
`sql.ErrNoRows` không tính là lỗi).

### Bước 3 — nghiệm thu chuỗi thật, kỳ cách ly

**Bẫy 1 — KHÔNG dùng `Calculate` (ghi hàng loạt) trên kỳ 05/2026 hay 02/2026 thật** — nó ghi đè
`payroll_records` của 3273/3162 nhân viên thật. Dựng 1 kỳ cách ly mới (khuôn `2099-xx` như các test
tích hợp cũ trong repo đã dùng — grep `2099-01` trong `internal/service/*_test.go` để thấy khuôn),
kèm 1 nhân viên test cách ly (tạo mới, KHÔNG dùng nhân viên thật) để không đụng dữ liệu ai.

Các bước cụ thể:
1. Tạo 1 `payroll_period` mới (`start_date`/`end_date` bất kỳ trong tương lai xa, ví dụ 2099-01-01→
   2099-01-31), 1 `employee` test mới (mã ví dụ `TEST_TASK5_060826`), có đủ dữ liệu tối thiểu để
   `Calculate` chạy được (xem cách các test tích hợp cũ trong `internal/service/` dựng fixture — copy
   đúng khuôn, đừng tự sáng tác trường mới).
2. Tạo 1 `payroll_templates` mới (ví dụ tên "TEST_TASK5_e2e"), thêm 2-3 cột phụ cấp LÁ vào
   `template_components` (dùng mã đã xác nhận maskable ở Task 3 — ví dụ `PHONE_ALLOW`, `FUEL_ALLOW`,
   `MEAL_TAX`+`MEAL_NONTAX` — xác nhận lại bằng `curl .../config/salary-components` xem `maskable:true`
   trước khi chọn, đừng chọn mù).
3. Gán nhân viên test vào template test (`employee_payroll_templates`, `effective_from` = ngày trong
   kỳ test).
4. **Restart backend** — xác nhận `template_components` còn nguyên sau restart (nghiệm thu Task 0 ở
   tầng thật, không chỉ ở test — đây là điểm PLAN yêu cầu tường minh).
5. `POST /api/v1/Core System/template-impact/{periodId}` (kỳ test) với body `{"salaries":
   {"<mã_NV_test>": <basic_salary_giả>}}` → kỳ vọng response có `delta` khác 0 cho các cột bị mask
   (đã sửa ở Task 4 — nếu vẫn trả 0 tuyệt đối thì DỪNG, đó là hồi quy của Task 4, không phải việc của
   Task 5).
6. `POST /api/v1/Core System/calculate/{periodId}` (kỳ TEST, không phải kỳ thật) → kiểm
   `payroll_records.computed_values` của nhân viên test: cột bị mask (nằm trong template_components
   của template gán) = 0; cột KHÔNG bị mask (không nằm trong template, hoặc là dependency của cột
   trong template) giữ giá trị thật; `GROSS`/`NET_PAY`/`PIT` tính lại đúng theo dữ liệu đã mask (không
   phải cả 3 đều = 0 — nếu vậy là bug, không phải kỳ vọng).
7. `POST /api/v1/Core System/calculate-one/{periodId}` cho cùng nhân viên → so khớp kết quả với bước 6
   (phải khớp tuyệt đối `computed_values`).
8. `POST /api/v1/Core System/finalize/{periodId}` → kiểm `payroll_formula_snapshots WHERE period_id=<kỳ
   test> AND scope_type='template'` có dòng, `component_code` khớp đúng tập cột đã mask ở bước 6.
9. Tạo thêm 1 nhân viên test thứ hai **KHÔNG gán template nào** → `Calculate` lại kỳ test → xác nhận
   mọi giá trị của nhân viên này y nguyên như khi enforce OFF (TASK-REF, không bị ảnh hưởng bởi enforce
   bật).

### Bước 4 — dọn dẹp dữ liệu test

Xoá sạch: `payroll_records`/`employee_payroll_templates`/`template_components`/`payroll_templates`/
`payroll_formula_snapshots`/`employees`/`payroll_periods` liên quan tới kỳ test 2099 và 2 nhân viên
test vừa tạo. Xác nhận bằng SELECT lại — 0 dòng còn sót ở mọi bảng liên quan tới kỳ 2099.

### Bước 5 — ghi lại số đo thật

Ghi vào `self-docs/Salary-Structure-Template-Analysis-260726.md` (mục mới, số tiếp theo mục 18):
toàn bộ số đo thật ở bước 3 (giá trị `computed_values` cụ thể trước/sau mask, nội dung response
`template-impact`, dòng snapshot thật). Đây là bằng chứng DUY NHẤT cho câu "tính năng hoạt động" —
không được viết tài liệu nói "đã nghiệm thu" mà không có số thật kèm theo.

## Ràng buộc tuyệt đối

- KHÔNG dùng `Calculate` (ghi hàng loạt) trên kỳ 05/2026 hoặc 02/2026 thật (Bẫy 1).
- KHÔNG commit `Core System-backend/.env` (biến `PAYROLL_TEMPLATE_ENFORCE=on` là dev-local only, PLAN nói
  rõ "chỉ dev local", không chạm staging/production).
- KHÔNG để sót dữ liệu test trong DB sau khi xong (bước 4 bắt buộc).
- `payroll_records` của các kỳ THẬT (01-05/2026 và mọi kỳ khác không phải kỳ test 2099) phải y nguyên
  trước/sau toàn bộ Task 5 — xác nhận bằng `SELECT count(*), md5(string_agg(computed_values::text,''
  ORDER BY id)) FROM payroll_records WHERE period_id != '<kỳ test 2099>'` trước và sau.

## DỪNG và hỏi khi

- Dữ liệu demo ở bước 1 không khớp mô tả trên (đã bị ai sửa từ 060826 tới lúc thi hành).
- `template-impact` vẫn trả delta=0 tuyệt đối sau khi enforce bật (nghi ngờ hồi quy Task 4).
- Cần tạo fixture employee/period mà không rõ trường bắt buộc tối thiểu (đọc test tích hợp cũ trước,
  đừng đoán).

## Định nghĩa xong

1. Dữ liệu demo cũ đã xoá, xác nhận bằng SELECT.
2. `PAYROLL_TEMPLATE_ENFORCE=on` trong `.env` local, `template-enforce-status` trả `healthy:true`.
3. Toàn bộ 9 bước ở mục "Bước 3" chạy thật, có số đo cụ thể (không phải "đã test" suông).
4. Dữ liệu test đã dọn sạch, DB thật (payroll_records mọi kỳ thật) không đổi.
5. Tài liệu ghi số đo thật (bước 5).
6. Cập nhật PLAN cột TT Task 5 → `xong` kèm ghi chú số đo, `00-START-HERE.md` nếu có lỗi nào đóng
   theo (không có lỗi L nào gắn trực tiếp với Task 5), dòng nhật ký `CLAUDE.md`.
7. Commit (backend only — Task 5 không sửa FE) — **hỏi xác nhận trước khi commit**, không tự push.
