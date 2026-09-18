---
id: self-docs/engine/salary-structure-template-analysis
canonical_question: 'Technical guide and specification: Salary Structure / Core System
  Template — Phân tích cấu trúc bảng DB'
aliases:
- Salary Structure / Core System Template — Phân tích cấu trúc bảng DB
- Salary Structure Template Analysis 260726
entity_type: how_to
domain: self-docs > engine
last_verified: 2026-07-26
---

# Salary Structure / Core System Template — Phân tích cấu trúc bảng DB (260726)

**Ngày viết:** 2026-07-26
**Loại tài liệu:** Phân tích kiến trúc (canonical cho chủ đề "cấu trúc lương/salary template"), không phải báo cáo công việc theo ngày.
**Liên quan tới:** `llmwiki/wiki/sources/draft/240726-salary-component-db-hardening.md` (đã triển khai), `llmwiki/wiki/sources/draft/260726-salary-structure-usage-and-grading.md` (SPEC đang chờ duyệt, dựa trên phân tích trong file này).

## Mục đích

Dự án `payroll_engine` có 5 bảng liên quan trực tiếp tới `salary_components` (thành phần lương): `salary_components`, `salary_component_history`, `salary_component_overrides`, `payroll_templates`, `template_components`. Tài liệu này trả lời 2 câu hỏi: (1) 5 bảng này đang đóng vai trò gì trong hệ thống thật — bảng nào đã dùng, bảng nào chưa; (2) nếu muốn xây "cấu trúc lương theo cấp bậc" bằng 2 bảng còn trống, nên thiết kế ra sao — dựa trên đối chiếu 3 hệ thống Core System thật đang được dùng rộng rãi (Frappe/ERPNext HRMS, Odoo, Oracle HCM Cloud) với chính engine tính lương của dự án.

## 1. Vai trò thật của từng bảng (đã xác nhận bằng query DB + đọc code, không suy đoán)

| Bảng | Vai trò | Trạng thái (26/07/2026) | Dữ liệu |
|---|---|---|---|
| `salary_components` | Bảng master định nghĩa cột lương — code, tên, loại (input/config/formula/system/manual), công thức, format hiển thị, ẩn/hiện | Wiring đầy đủ FE+BE từ `240726-formulas-tab-fe.md` | 110 dòng (102 `is_active AND is_visible`) |
| `salary_component_history` | Audit trail mỗi lần đổi `formula`/`name` của 1 cột | Wiring đầy đủ (`GET .../history`, panel "Giải thích logic") | 8 dòng |
| `salary_component_overrides` | Ghi đè công thức/giá trị theo phạm vi hẹp hơn cột gốc — `scope_type` chỉ nhận `department` hoặc `employee`, có `priority`, `effective_from/to`, `source` (`formula` hoặc `cell_pin`) | Backend + FE CRUD đầy đủ từ `240726-salary-component-db-hardening.md`, **đã xác nhận có ảnh hưởng thật tới kết quả tính lương** (xem mục 2) — nhưng 0 dòng dữ liệu vì chưa ai tạo qua app | 0 dòng |
| `payroll_templates` | Dự định: "mẫu bảng lương" — 1 tập cột lương định sẵn, có cờ `is_default` | **Hoàn toàn chưa có code Go nghiệp vụ nào** — không repository/service/route/FE nào thao tác bảng này | 0 dòng |
| `template_components` | Bảng nối N-N `payroll_templates` ↔ `salary_components`, có `sort_order` | Cùng trạng thái với `payroll_templates` | 0 dòng |

`payroll_templates`/`template_components` đã được đánh dấu chính thức "RESERVED — chưa triển khai" bằng `COMMENT ON TABLE` trong migration `Core System-backend/atlas/migrations/20260725000000_salary_components_db_hardening.sql` — không phải bảng chết vô tình bị bỏ quên, mà là quyết định có chủ ý (4c) tại thời điểm đó: không xây tính năng thật (4a), không xoá bảng (4b), chỉ ghi chú rõ ràng trong schema. Đã xác nhận lại sau khi merge `origin/develop` (commit `e76e689`, 26/07/2026): không có commit `.go` nào từ nhánh khác chạm 2 bảng này — hiện trạng RESERVED vẫn đúng, không đội nào khác đang âm thầm xây song song.

## 2. `salary_component_overrides` đã có tác dụng thật — bằng chứng từ chính engine tính lương

Đọc trực tiếp `internal/service/payroll_service.go:417`: hàm `scopedResolver.resolveFor(emp.EmployeeCode, deptCode)` build 1 `FormulaEngine` **riêng** cho từng nhân viên/phòng ban bằng cách clone toàn bộ danh sách component gốc rồi **ghi đè formula** của đúng những component đang có override hiệu lực tại thời điểm kỳ lương (dữ liệu override được load 1 lần cho cả kỳ qua `overrideRepo.ListActiveForDate(ctx, periodDate)`, dòng ~218). Điều này xác nhận: override **không phải một tính năng UI treo lơ lửng không nối backend** — nó đã sẵn sàng thay đổi số tiền lương thật ngay khi có ai tạo 1 dòng override qua app. Vấn đề duy nhất còn lại là HR/C&B chưa biết khi nào nên dùng (xem SPEC `260726-salary-structure-usage-and-grading.md` Phần A — cần 1 tài liệu hướng dẫn ngắn, không cần code thêm).

## 3. Nghiên cứu 3 hệ thống Core System thật — mô hình chuẩn cho "cấu trúc lương theo cấp bậc"

Tra cứu trực tiếp tài liệu kỹ thuật của 3 hệ thống đang được dùng rộng rãi (không suy đoán):

**Frappe/ERPNext HRMS** (đọc trực tiếp tài liệu kỹ thuật DeepWiki của repo `frappe/hrms`) dùng đúng 3 tầng:

1. **Salary Component** — định nghĩa 1 khoản (`type`: Earning/Deduction, `formula`, cờ `depends_on_payment_days` để pro-rate theo ngày công thực tế, `statistical_component` cho giá trị chỉ dùng trong công thức không cộng vào tổng, `accrual_component` cho phúc lợi tích luỹ chưa trả ngay).
2. **Salary Structure** — gom nhiều component vào 2 bảng con `earnings`/`deductions`; mỗi dòng có thể override riêng `amount`/`formula`/`condition` cho structure đó (không phải lúc nào cũng dùng y hệt định nghĩa gốc của component).
3. **Salary Structure Assignment** — bảng gán 1 structure cho **1 nhân viên cụ thể**, có `from_date` (ngày hiệu lực). Một nhân viên có thể có **nhiều assignment theo thời gian** (đổi lương, đổi vị trí, thăng chức) — hệ thống tự động chọn assignment đang hiệu lực khi tính lương cho 1 kỳ cụ thể.

**Odoo Core System**: `hr.contract` (hợp đồng nhân viên) trỏ tới 1 "structure type" — chỉ những "structure" thuộc đúng type đó mới được dùng để tính lương cho nhân viên giữ hợp đồng đó. Salary rule có category riêng, đóng góp vào tổng theo category khi tính payslip.

**Oracle HCM Cloud**: cùng khái niệm gắn cấu trúc lương (compensation structure) theo cấp bậc/vị trí nhân viên.

**Điểm chung của cả 3 hệ thống, và đây là kết luận quan trọng nhất của phần nghiên cứu này:** không hệ thống nào dừng lại ở 2 tầng "template ↔ component". Cả 3 đều bắt buộc có **tầng thứ 3**: một bảng gán template/structure cho **từng nhân viên cụ thể**, có **ngày hiệu lực**, và cho phép **nhiều bản ghi gán theo thời gian** cho cùng 1 người. Đây chính xác là mảnh còn thiếu trong schema hiện tại của dự án — `template_components` chỉ nối `payroll_templates` ↔ `salary_components` (template gồm những cột nào), **không có bảng nào nối `payroll_templates` ↔ `employees`** (nhân viên nào đang dùng template nào, từ khi nào).

## 4. Engine tính lương thật của dự án — hiện KHÔNG có khái niệm "cấp bậc quyết định tập cột"

Khảo sát trực tiếp `internal/service/engine.go` + `internal/service/payroll_service.go`:

- `FormulaEngine.components []models.SalaryComponent` (`engine.go:29`) là danh sách **cố định**, nạp 1 lần lúc khởi tạo qua `NewFormulaEngine(components, pitBrackets)` (`engine.go:37-45`) — không có tham số employee/level nào.
- `PayrollService.Calculate` gọi `componentRepo.ListActive(ctx)` **đúng 1 lần cho cả kỳ lương** (`payroll_service.go:196`), build 1 `engine` gốc dùng chung cho **mọi nhân viên** (dòng 198). `CalculateOne` (tính lại 1 người) gọi lại y hệt (dòng 461), cũng không truyền level/template nào vào query.
- Cơ chế khác biệt theo nhân viên **duy nhất** hiện có là override theo `scope_type` `department`/`employee` (mục 2) — hoàn toàn không có khái niệm "level" hay "template" ở tầng này.
- **Đã có sẵn 1 cơ chế cache đáng chú ý, tận dụng được nếu xây tính năng theo cấp bậc**: `engineCache := map[string]*FormulaEngine{"": engine}` (`payroll_service.go:230`) — cache 1 `FormulaEngine` biến thể theo "chữ ký phạm vi" (hiện chỉ dùng cho tổ hợp override employee/department) để tránh phải build lại engine cho mỗi nhân viên trong 1 kỳ có hàng nghìn người. Nếu mở rộng key cache này để bao gồm cả `template_id`, đây là cách tận dụng 1 cơ chế đã chạy thật thay vì phát minh lại từ đầu.
- **Đã có 1 cơ chế khác cho phép công thức đổi theo cấp bậc — nhưng đổi GIÁ TRỊ, không đổi TẬP CỘT**: component có sẵn `LEVEL_NUM` ("Bậc lương L1=1…L8=8", định nghĩa tại `internal/database/database.go:2218`, `source_field: employees.level_num`) là 1 input số cho phép công thức viết kiểu `IF([LEVEL_NUM] >= 5, ..., ...)`. Cơ chế này giải quyết đúng bài toán "cùng 1 cột, số tiền khác theo cấp bậc" — nhưng **không giải quyết** bài toán "cấp bậc cao có hẳn 1 cột phụ cấp riêng mà cấp thấp hoàn toàn không có cột đó". Đây là 2 bài toán khác nhau: `LEVEL_NUM` giải bài toán giá trị, template (nếu xây) giải bài toán cấu trúc/tập cột. Không nên nhầm lẫn 2 cơ chế này khi thiết kế, và SPEC `260726-salary-structure-usage-and-grading.md` không thay thế `LEVEL_NUM`.

## 5. Dữ liệu cấp bậc đã có sẵn — và 1 điểm mờ quan trọng chưa xác minh được

- `employee_levels` tồn tại thật, đồng bộ từ HRIS (có cột `hris_id`, `synced_at`) — dữ liệu thật (vd `L8`, `QL.03`, `LĐCC`...), có sẵn `order_number`, `salary_range_from/to`, `scale_coefficient` (chưa có code Go nào đọc — ngoài phạm vi phân tích này, ghi nhận để biết là tồn tại).
- `employees` có **2 cách tham chiếu tới level, không rõ cách nào nên dùng làm khoá cho tính năng mới**:
  - `models.Employee.LevelCode string` (`internal/models/employee.go:35`, cột `level_code`) — text, không FK, **đã được ứng dụng Go đọc/ghi thật** (dùng cho `LEVEL_NUM` và hàm point-in-time `ResolveLevelAsOf`).
  - `employees.employee_level_id uuid` — cột có thật trong DB (tạo bởi migration in-code `database.go:335`), **có dữ liệu thật** (đã verify bằng query: 6357/12044 dòng có giá trị — 52.8%), nhưng **không có field Go nào trong `models.Employee` map tới cột này**, và grep toàn bộ `internal/` không tìm thấy bất kỳ code Go nào ghi vào cột này. Kết luận: cột này được điền bởi 1 tiến trình **ngoài codebase `Core System-backend`** — rất có thể là pipeline đồng bộ HRIS/Workday chạy riêng (khớp đúng naming convention với `employee_levels.hris_id`/`synced_at`).
  - Có tiền lệ dùng `level_id` (uuid) làm FK thật trong chính dự án: `allowance_items.level_id` FK `employee_levels(id)` — mẫu tốt để theo nếu xác nhận `employee_level_id` đáng tin.
- **Điểm mờ cần làm rõ trước khi quyết định khoá:** chưa xác minh được tiến trình nào ghi `employee_level_id`, đồng bộ theo lịch nào, và vì sao ~44% nhân viên (5687/12044) hiện chưa có giá trị. Nếu nguyên nhân là do đồng bộ HRIS chưa phủ hết hoặc chạy trễ, xây tính năng dựa trên cột này ngay bây giờ sẽ để lại gần một nửa nhân viên "không thuộc cấp bậc nào" từ ngày đầu triển khai. Đây là lý do SPEC `260726-salary-structure-usage-and-grading.md` đưa việc xác minh này thành 1 task riêng (Task 2), làm trước, không gộp chung với quyết định thiết kế.
- `payroll_records`/`payroll_periods` xác nhận **không có cột nào** về level/template — một nhân viên tính lương ở 1 kỳ hiện không lưu vết "lúc đó đang ở cấp bậc/template nào" ngoài suy ra được từ `employee_work_histories` (cơ chế point-in-time đã có sẵn cho `ResolveLevelAsOf`/`ResolveDepartmentAsOf`).

## 6. Kết luận — 2 quyết định mở, chưa tự chọn thay

Toàn bộ phân tích trên đã được đúc kết thành SPEC `llmwiki/wiki/sources/draft/260726-salary-structure-usage-and-grading.md`, để trống 2 quyết định kiến trúc chờ người quyết định dự án chốt khi duyệt:

1. **Cơ chế enforce** — engine có thật sự lọc theo template đang gán cho từng nhân viên (đúng chuẩn cả 3 hệ thống tham chiếu, tận dụng `engineCache` đã có, nhưng đổi hành vi tính lương thật), hay template chỉ là gợi ý/preset cho UI lúc tạo nhân viên mới (an toàn hơn, nhanh hơn, nhưng không đúng tinh thần chuẩn ngành — mất đúng giá trị cốt lõi mà cả 3 hệ thống coi là bắt buộc).
2. **Cột khoá cho bảng gán nhân viên mới** — `employee_level_id` (FK thật, nhưng nguồn ghi/độ tin cậy chưa xác minh) hay `level_code` (text, đã chứng minh hoạt động trong engine hiện tại nhưng không FK).

**Cập nhật 26/07/2026 — cả 2 mục trên đã chốt:**
- Mục 2 (cột khoá): **chốt `employee_level_id`.** User xác nhận trực tiếp: cột này do 1 pipeline đồng bộ HRIS/Workday ngoài `Core System-backend` ghi, tần suất hàng ngày/gần real-time; ~44% nhân viên thiếu giá trị là **hợp lệ** (nhóm chưa được xếp cấp bậc trong HRIS gốc, vd thời vụ/thử việc) — không phải lỗi đồng bộ. Đủ tin cậy để dùng làm FK, không cần backfill.
- Mục 1 (cơ chế enforce): **vẫn đang mở, chưa chốt** — nhưng đã tách rõ ra khỏi việc xây CRUD (xem mục 7 dưới đây), nên không còn chặn tiến độ.

## 7. Task 3 (CRUD) đã tách khỏi Approach A1 — không cần chờ nhau

Rà soát lại kỹ hơn cho thấy Task 3 (migration bảng gán nhân viên + CRUD `payroll_templates`/`template_components`/`employee_payroll_templates`) và Approach A1 (engine có enforce thật hay không) nằm ở **2 tầng code hoàn toàn tách biệt**, không phụ thuộc nhau:

- **Task 3 (CRUD/UI)** chỉ chạm tầng lưu trữ/cấu hình — tạo/sửa/xoá template, chọn cột thuộc template, gán template cho nhân viên có ngày hiệu lực. Schema và API giống hệt nhau bất kể Approach A1 chọn nhánh nào.
- **Approach A1** chỉ chạm `PayrollService.Calculate`/`CalculateOne`/`engineCache` (`internal/service/payroll_service.go`) — tầng tính toán, đọc (hay không đọc) dữ liệu Task 3 đã lưu.

**Đã triển khai backend của Task 3 (260726)** — không chờ A1: migration `atlas/migrations/20260726000000_employee_payroll_templates.sql` (đã áp dụng vào `payroll_engine`), model/repo/service/handler CRUD đầy đủ (`internal/models/Core System.go`, `internal/repository/payroll_template_repo.go`, `internal/service/payroll_template_service.go`, `internal/handler/payroll_template_handler.go`), route `/config/Core System-templates` + `/config/employee-Core System-templates` (tái dùng permission `Settings.SalaryComponents`). 2 test tích hợp chạy thật trên `payroll_engine`, tự dọn dữ liệu. `go test ./...`: 759 passed, 4 failed (xác nhận qua `git stash -u` là baseline cũ, không hồi quy).

**Còn thiếu: UI quản lý (FE)** — 3 phần cụ thể:
1. **Danh sách "Cấu trúc lương"** — CRUD `payroll_templates` (tên, mô tả), xoá bị chặn nếu đang có nhân viên gán.
2. **Chọn cột lương thuộc 1 cấu trúc** — mở 1 template, tick chọn cột nào trong 110 cột thuộc về nó, sắp thứ tự hiển thị (gọi `PUT .../{id}/components`).
3. **Gán cấu trúc cho từng nhân viên** — tìm 1 nhân viên, xem lịch sử gán (nhiều bản ghi theo thời gian nếu từng đổi), thêm 1 bản ghi gán mới (chọn template + ngày hiệu lực); có công cụ tra cứu nhanh "nhân viên X đang dùng template nào tại ngày Y" (`GET .../resolve`, đã có).

**UI này KHÔNG ảnh hưởng tính lương thật cho tới khi Task 4 xong** — thuần lưu cấu hình. Đây là **điểm cần kỷ luật vận hành**, không phải rào cản kỹ thuật: dữ liệu gán tạo ra bây giờ sẽ "sống lại" và có tác dụng thật ngay lập tức nếu sau này Task 4 bật enforce (Approach A1-A) — nên cần tạo dữ liệu cẩn thận như thể nó sẽ có tác dụng thật, và UI nên có 1 dòng cảnh báo tạm thời "Chưa ảnh hưởng bảng lương thật — chỉ lưu cấu hình" (gỡ đi sau khi Task 4 hoàn tất).

Không quyết định nào trong 2 mục trên được tự chọn thay trong tài liệu phân tích này — khớp nguyên tắc chung của dự án: quyết định kiến trúc ảnh hưởng hành vi thật cho người dùng cuối là của người quyết định dự án.

---

## 7. Quyết định Approach A1 (chốt 260726) — enforce THẬT bằng cơ chế mask-về-0

**Chọn nhánh A (engine enforce thật), KHÔNG chọn nhánh B (preset UI), KHÔNG chọn phương án trung gian "làm B trước".**

Lý do bỏ phương án trung gian: khối lượng công việc của B và A **giống hệt nhau** ở phần schema + CRUD + UI gán (Task 3 không phụ thuộc A1). Làm B trước không tiết kiệm gì, chỉ tạo ra một giai đoạn có bảng gán mà engine cố tình phớt lờ — HR dễ tin nhầm là đã có hiệu lực. Đó là rủi ro vận hành, không phải phương án an toàn.

**Nhưng cách thi hành nhánh A phải khác cách mô tả ban đầu trong SPEC.** SPEC viết "lọc còn đúng tập component có trong `template_components`". Đọc code trực tiếp cho thấy lọc thô là sai:

| # | Bằng chứng | Hậu quả |
|---|---|---|
| 1 | `engine.go:89` — `buildOrder()`: `if j, ok := codeIdx[dep]; ok` | Dependency không có trong danh sách bị **bỏ qua im lặng**, không lỗi |
| 2 | `engine.go:612` — `return fromInterfaceValue(p.vals[code]), nil` | Biến thiếu → `nil` → `numberValue(0)`. Im lặng |
| 3 | `payroll_service.go:394-398` | Vòng nạp `source_field` lặp trên chính `sh.components` → lọc thô làm **cột input ngừng được nạp** từ attendance, kéo cả dây chuyền về 0 |
| 4 | `engine.go:170,192` | Lỗi eval chỉ `log.Printf` rồi gán 0 — **không tín hiệu nào nổi lên tới HR** |

Lọc ở tầng OUTPUT (chỉ ẩn cột lúc hiển thị) cũng **không đủ**: giá trị cột đó vẫn cộng vào tổng thu nhập → sai tiền, không chỉ sai hiển thị.

**Cách đúng — mask-về-0:** sinh override `formula = "0"` cho các cột ngoài cấu trúc, tái dùng nguyên `scopedResolver` → `applyResolvedFormulas` → `engineCache` (`payroll_service.go:418-438`) đã chạy thật. Component vẫn nằm trong graph nên topo sort nguyên vẹn, tổng tự tính lại đúng, `engine.go` **không sửa 1 dòng**, và số 0 là **cố ý** — truy vết được qua override/snapshot.

**Quy tắc chọn cột được mask** (giải đúng lo ngại "tập đóng phụ thuộc" của người quyết định dự án, nhưng áp theo chiều ngược lại):

```
kept    = tập CODE thuộc template
closure = kept ∪ {mọi CODE mà cột trong closure tham chiếu, đệ quy qua extractDeps}
mask    = tất cả CODE − closure − statutoryOverrideBlocklist − {component_type == "system"}
```

**Đính chính (060826):** công thức trên liệt kê 3 lớp bảo vệ (closure, `statutoryOverrideBlocklist`,
loại trừ `component_type=="system"`) — đo trên DB thật (040826) thì **2 lớp sau đã chết** (blocklist
cũ dùng 3 mã không tồn tại trong DB; guard `system` khớp 0 dòng sau khi PIT chuyển sang `formula`),
chỉ còn đúng 1 lớp (closure/universe) đang hoạt động thật. Xem mục 14.6 (1) để có bằng chứng đo được
đầy đủ — `statutoryOverrideBlocklist` đã được sửa lại đúng ở Task 2 (mục 16.6).

Cột **ngoài** template nhưng **được cột trong template phụ thuộc vào** thì GIỮ NGUYÊN, không mask. Thiếu bước này, mask 1 cột hệ số/đơn giá trung gian sẽ kéo các cột hợp lệ về 0 — đúng loại lỗi mà thiết kế này sinh ra để tránh. Dự án chưa có cờ `statistical_component` như ERPNext nên tập đóng phụ thuộc là cách thay thế duy nhất đúng.

**Cập nhật 270726 — quy tắc chọn cột mask ở trên (v1) có lỗi thiết kế nghiêm trọng, đã sửa 2 lần lúc triển khai Task 4.2, KHÔNG phải chỉ tinh chỉnh nhỏ:**

Quy tắc v1 (`mask = tất cả CODE − closure(template) − statutory − system`) chỉ xử lý chiều **XUỐNG** (dependency mà cột template cần). Nhưng các cột **TỔNG** (`GROSS`, `TAXABLE_INC`, `PIT`, `NET_PAY`...) đi chiều **LÊN** — chúng *tiêu thụ* cột template, không phải bị template phụ thuộc. Verify bằng đọc đồ thị công thức thật (110 cột, `salary_components`): `BASIC_SAL → EARNED_SAL → GROSS → TAXABLE_INC → PIT`, `GROSS − TOTAL_INS − PIT → NET_PAY`. Với quy tắc v1, 1 template chỉ liệt kê vài phụ cấp (cách tự nhiên nhất HR sẽ làm) → **toàn bộ chuỗi tổng này bị mask = 0** → payslip: `BASIC_SAL` hiện số thật nhưng `GROSS = 0, PIT = 0, NET_PAY = 0`. Sai tiền toàn tập — đúng loại lỗi mà thiết kế mask sinh ra để tránh, nhưng từ chiều ngược lại mà closure không phủ tới. Phát hiện **trước khi viết Task 4.6** (bộ test khoá bất biến), bằng cách tự tay dựng đồ thị công thức thật và mô phỏng kịch bản HR tạo template — chưa từng chạy trên dữ liệu thật (0 template/assignment trong DB lúc phát hiện) nên không gây hại ai.

Đã sửa qua 2 bước (chi tiết đầy đủ + code trong PLAN, mục Task 4.2):
- **v2 (tạm, bị bỏ ngay sau đó):** giới hạn tập có thể mask bằng 1 `map` hardcode trong Go (6 nhóm phụ cấp cố định: ăn ca/điện thoại/xăng xe/đi lại/nhà ở/phụ cấp khác). An toàn (chỉ mask đúng phụ cấp, không đụng cột tổng) nhưng **sai kiến trúc**: "cột nào là phụ cấp theo cấp bậc" là dữ liệu HR quản lý qua UI, không phải hằng số code — HR thêm/bớt phụ cấp phải sửa code + deploy.
- **v3 (final, đang chạy — `union-of-templates`, data-driven):** `maskableUniverse` = **union mọi cột xuất hiện trong bất kỳ template nào đang tồn tại** (`buildTemplateUniverse`, dựng từ `tplCodes` đã nạp sẵn ở Task 4.3, không query thêm). Ý nghĩa: 1 cột là "phụ cấp theo cấp bậc" ⟺ có ít nhất 1 template chứa nó. Quy tắc cuối: `mask = maskableUniverse − closure(templateNV)`. Cột không nằm trong template nào (mọi cột tổng/vận hành/lương cơ bản) → ngoài universe → **không bao giờ mask**, không cần liệt kê tay. HR thêm/bớt phụ cấp chỉ cần sửa template qua UI (Task 6), **0 dòng code**.

Rủi ro còn lại của v3 (chưa xảy ra, chặn ở Task 5/6): HR **lỡ** đưa 1 cột TỔNG vào 1 template → cột đó vào universe → có thể bị mask cho NV template khác. Chặn bằng: (a) UI Task 6 chỉ cho chọn cột phụ cấp/earning, ẩn cột tổng; (b) shadow-mode + kill-switch env (Task 5) trước khi bật enforce trên dữ liệu thật.

**Đối chiếu ngành (tra cứu lại 260726):** ERPNext hành xử **đúng như nhánh lọc thô** — công thức tham chiếu component không thuộc structure của nhân viên thì lấy giá trị 0, không báo lỗi; đây là nguồn gốc nhiều thread "salary component formula not evaluating" trên forum Frappe. Nghĩa là silent-0 là **lỗi thiết kế đã biết của chuẩn ngành**, không phải rủi ro riêng của dự án. Mask cho **cùng kết quả số** nhưng có dấu vết. ERPNext còn bỏ qua/để trắng slip khi NV không có assignment hiệu lực — TASK-REF của dự án (fallback tính đủ như cũ) **an toàn hơn ERPNext**, giữ nguyên.

Nguồn: [Frappe Forum — formula not evaluating](https://discuss.frappe.io/t/salary-component-formula-not-evaluating/155315) · [DeepWiki frappe/hrms — Salary Components and Structure Configuration](https://deepwiki.com/frappe/hrms/2.1.3-salary-components-and-structure-configuration) · [ERPNext Core System Setup](https://docs.erpnext.com/docs/v13/user/manual/en/human-resources/Core System-setup)

## 8. Impact khi triển khai — 5 điểm ngoài engine mà SPEC chưa nêu

1. **`base_values` bùng nổ** (`payroll_service.go:445-450`) — hiện `sig != ""` thì chạy engine gốc lần 2 để FE biết ô nào bị cascade. Nhét template vào chung `sig` → **mọi NV có template đều `sig != ""`** → chạy engine 2 lần cho 12k người/kỳ + FE hiện dấu "ô bị ghi đè" khắp bảng. Phải tách: template vào **cache key**, cờ tính `base_values` vẫn chỉ theo override thật.
2. **Snapshot lúc chốt kỳ** (`salary_component_override_repo.go:143`) — `SnapshotForPeriod` đóng băng công thức bằng `SELECT` từ `salary_components` + `salary_component_overrides`. Mask template không nằm trong 2 bảng đó → kỳ đã chốt **mất dấu** NV bị mask cột nào. Vi phạm TASK-REF. Cần thêm nhánh INSERT `scope_type='template'` (kiểm CHECK constraint trước).
3. **Export/báo cáo** (`report_service.go:44`) — dựng cột từ `ListActive` cho **cả lưới**, không theo từng dòng. Cột bị mask hiện **0**, không ẩn được theo từng NV trong file Excel phẳng. Giới hạn cố hữu, phải báo trước cho C&B.
4. **Hai điểm khởi tạo `calcShared`** — `Calculate` (~dòng 230-300) và `CalculateOne` (~dòng 518). Quên 1 chỗ = "tính lại 1 người" ra số khác "tính cả kỳ", **bug im lặng**, chỉ lộ khi HR đối chiếu tay. **Đã giải quyết tận gốc (270726):** thay vì chép code nạp dữ liệu template 2 lần rồi dựa vào test để bắt lệch, rút thành 1 helper DUY NHẤT `loadTemplateMaskData` mà cả 2 điểm gọi chung — về cấu trúc không còn khả năng "quên 1 chỗ" nữa (không phải chỉ có test khoá, mà code không còn 2 bản để lệch). Test `TestTemplateEnforce_CalculateOneMatchesCalculateAndPointInTime` vẫn giữ để khoá bất biến này ở tầng end-to-end.
5. **Hiệu năng** — không đáng kể. `NewFormulaEngine` = topo sort 110 node (µs); ~12 cấp bậc → ~12 biến thể engine/kỳ, cache đã có sẵn.

**Không bị ảnh hưởng:** `LEVEL_NUM`, `ResolveLevelAsOf/DepartmentAsOf`, `statutoryOverrideBlocklist`, cell_pin, manual inputs, RBAC/scoping, schema `payroll_records`. Không migration nào trên bảng đang có dữ liệu.

**Lợi ích:** (1) đúng tiền — cột ngoài cấu trúc góp 0 vào gross thay vì C&B nhớ trừ tay; (2) bỏ được hàng loạt override thủ công, `salary_component_overrides` quay về đúng vai ngoại lệ; (3) onboarding hết đoán 110 cột; (4) truy vết được cấu trúc theo từng kỳ; (5) mở khoá 2 bảng RESERVED; (6) rủi ro thấp bất thường vì tái dùng cơ chế đã chạy thật.

## 9. Trạng thái thật + checklist theo dõi (cập nhật 270726)

Kế hoạch thi hành chi tiết: **`llmwiki/wiki/sources/draft/260726-salary-structure-usage-and-grading-PLAN.md`** (từng bước có lệnh chạy + output kỳ vọng — **lưu ý:** nội dung Task 4.2/4.5 trong file PLAN mô tả bản THIẾT KẾ ĐẦU (v1 closure-only / SQL thô), đã bị thay bằng bản v3 union-of-templates khi thi hành thật — xem mục 7 ở trên và code thật để lấy bản cuối, PLAN giữ nguyên làm lịch sử quyết định).

Task 3.5 → 7 **đã code, test xanh, đã commit + push cả 2 repo** (`Core System-backend@feature_1` `60570b1`, `Core System-frontend@feature_1` `ea7b59a` — xem mục "Trạng thái git" cuối file để biết chi tiết 3 commit backend + 1 commit frontend). Toàn bộ PLAN 260726 coi như hoàn tất.

| # | Hạng mục | Trạng thái | Commit |
|---|---|---|---|
| 3.5 | Dọn nợ Task 3 (atlas.sum, test, commit) | [x] | `884244c` |
| 4.1 | Repo bulk resolve + bulk component codes | [x] | `eb0b626` |
| 4.2 | `buildTemplateMaskFormulas` — **3 vòng lặp thiết kế** (xem mục 7): v1 closure-only (sai, zero-hoá cột tổng) → v2 hardcode universe (an toàn nhưng sai kiến trúc) → v3 union-of-templates (final) | [x] | `5ae6a74`, sửa `9a90628`, refactor final `94b01d0` |
| 4.3 | Wire vào `calcShared`/`computeEmployee` qua 1 helper `loadTemplateMaskData` dùng chung 2 điểm khởi tạo | [x] | `b848400`, `2ae18f9` |
| 4.4 | Tách `cacheKey = tplSig+"|"+sig` khỏi cờ `base_values` (vẫn theo `sig`) | [x] | `2ae18f9` |
| 4.5 | Snapshot `scope_type='template'` — tái dùng `buildTemplateMaskFormulas`/`buildTemplateUniverse` (KHÔNG dùng SQL thô như PLAN gốc, vì SQL thô sẽ sai với thiết kế v3) | [x] | `358585a` |
| 4.6 | 7 test khoá bất biến (gộp đúng 8 bất biến PLAN yêu cầu) — **phát hiện phụ: bug PIT luôn = 0, ĐÃ SỬA 270726, xem `self-docs/PIT-Formula-Fix-270726.md`** | [x] | `8335fcc` |
| 5.1 | Kill-switch `PAYROLL_TEMPLATE_ENFORCE` (mặc định OFF) — **phát hiện phụ khi viết**: `snapshotTemplateMasksForPeriod` (Finalize) chưa gate theo kill-switch, sẽ ghi snapshot "nói dối" khi tắt — đã sửa cùng lúc | [x] | `3779ae8`/`e5683b6`/`60570b1` |
| 5.2 | Shadow-mode `GET /Core System/template-impact/{periodId}` — **route/gate PLAN gốc SAI** (`/periods/{id}/template-impact` + `requireSalaryComponentsView`), đã sửa khớp code thật (`requirePayrollCalculate, companyReadScope, requireView`, cùng nhóm `/Core System`). **Phát hiện phụ nghiêm trọng khi viết**: draft đầu để `computeEmployee` tự đọc env global — bản mô phỏng "on" sẽ vô tác dụng nếu env thật đang off; đã sửa bằng cách chuyển `templateEnforce` thành field trên `calcShared`, resolve 1 lần lúc dựng (Calculate/CalculateOne đọc env thật, `ComputeTemplateImpact` ép cứng true/false độc lập với env) | [x] | `3779ae8`/`e5683b6`/`60570b1` |
| 6 | FE: `PayrollTemplateModal.tsx` (CRUD) + `EmployeeTemplateAssignPanel.tsx` (gán NV) + nhúng `TinhLuongExcel.tsx` — **phát hiện phụ khi viết**: PLAN draft giả định sai hợp đồng API (`request<T>()` trả thẳng `Promise<T>`, không bọc `{data}` như PLAN giả định — trừ `getEmployees` dùng `requestWithTotal`), đã sửa toàn bộ điểm gọi trước khi paste. Verify bằng `next build` sản xuất thật, không chỉ `tsc`/`eslint` | [x] | `3779ae8`/`e5683b6`/`60570b1` |
| 7 | Tài liệu + nhật ký | [x] | file này + `document-map.md` + `routes-permissions.md` + `CLAUDE.md` 270726 |

Ngoài phạm vi PLAN gốc, cùng ngày: migration `atlas/migrations/20260727010000_pit_brackets_2026_law.sql` (thêm 5 bậc thuế 2026 vào `pit_brackets`, additive, không đụng 7 bậc cũ) — đã áp dụng DB dev `payroll_engine`. Chi tiết: `self-docs/PIT-Formula-Fix-270726.md` mục 5.

**Trạng thái enforce thật (270726, sau Task 5.1):** code mask-về-0 vẫn tồn tại trong `Calculate`/`CalculateOne`/`Finalize` nhưng nay được gate bởi kill-switch `PAYROLL_TEMPLATE_ENFORCE` (mặc định **OFF** — env chưa set = không enforce ai, kể cả khi có template/assignment thật). Trước Task 5.1, code này **LIVE không có công tắc tắt** — bất kỳ ai tạo 1 dòng `employee_payroll_templates` thật sẽ kích hoạt enforce ngay, không có cách tắt nhanh ngoài revert code + deploy lại; Task 5.1 đóng đúng lỗ hổng này. Bật thật (`PAYROLL_TEMPLATE_ENFORCE=on`) chỉ nên làm sau khi C&B xem báo cáo `GET /Core System/template-impact/{periodId}` (Task 5.2) và ký duyệt.

`go test ./...` sau Task 5-7: 4 fail — baseline cũ (`TestReportPayrollSummaryRouteRequiresPeriodID`, `TestReportBankTransferRouteRequiresPeriodID`, `TestPipelineProtectedRunRouteWithDevAuthReachesHandler`, `TestPipelineProtectedLogsRouteWithDevAuthReachesHandler`), không hồi quy mới qua toàn bộ Task 3.5-7. `next build` (`Core System-frontend`): 0 lỗi compile/typecheck, chỉ warning tiền tồn tại không liên quan.

## 10. Phát hiện phụ, ĐỘC LẬP với việc này — bug PIT luôn = 0 (270726, ĐÃ SỬA cùng ngày)

Phát hiện khi viết test Task 4.6 (`TestTemplateEnforce_StatutoryAndSystemNeverMasked`), **không liên quan gì đến mask-về-0** — bug có sẵn từ trước Task 4, ảnh hưởng TOÀN BỘ hệ thống tính lương, không riêng tính năng này.

**Bằng chứng (đã verify bằng code + dữ liệu thật, không suy đoán):**
- `internal/service/payroll_service.go`: `CalculateInputs.PeriodStart`/`PeriodEnd` **chưa từng được gán** ở `Calculate`/`CalculateOne`/`computeEmployee` (grep 0 kết quả trong non-test code) → luôn là `time.Time` zero-value.
- `pit_brackets` thật trong DB: cả 7 bậc thuế có `effective_from = 2009-01-01` (khác zero-value).
- `filterActivePITBrackets(bracketsThật, refDate=zero-value)` → trả về **0 bracket** (verify thực nghiệm bằng test tạm, đã xoá sau khi xem kết quả) → `calculateProgressivePIT` không có gì để áp dụng → PIT luôn = 0.
- Xác nhận qua dữ liệu production thật: `SELECT count(*) FILTER (WHERE (computed_values->>'PIT')::numeric > 0), count(*) FROM payroll_records WHERE computed_values ? 'PIT'` → **0 / 6435**, kể cả dòng `TAXABLE_INC = 20,225,000` (gấp 4 lần bậc thuế đầu 5,000,000). `PIT_ADJ` (cột điều chỉnh tay) cũng 0/6435 — không phải HR đang bù thủ công.
- **Đã loại trừ:** `PIT.Formula` rỗng trong DB KHÔNG phải nguyên nhân — `component_type="system"` khiến switch trong `engine.go` gọi `evalSystemComponent` vô điều kiện, không đọc `Formula`.

**Đã sửa (270726, cùng ngày phát hiện)** — ngoài phạm vi tính năng mask-về-0 này (bug PIT không liên quan gì tới template/cấp bậc), nhưng blast radius đủ lớn (toàn bộ PIT lịch sử) nên được xử lý ngay thay vì để treo. Quyết định người dùng chốt: **chuyển `component_type` của PIT từ `system` sang `formula`**, dùng bậc thuế theo dữ liệu HR cung cấp (đã xác nhận khớp Luật Thuế TNCN 2025, Điều 9) thay vì bậc `pit_brackets` 7 bậc cũ trong DB (khác luật, không phải sai số — lệch thật ~850k tại thu nhập 20tr). Chi tiết đầy đủ (migration, dead-code cleanup, test, xác nhận không ảnh hưởng core engine): `self-docs/PIT-Formula-Fix-270726.md`. Test `TestTemplateEnforce_StatutoryAndSystemNeverMasked` đã đổi tên thành `TestTemplateEnforce_StatutoryNeverMasked` và cập nhật để assert `PIT > 0` (trước đây phải tránh assertion này vì bug chưa sửa).

## 11. Trạng thái git (270726, cuối phiên)

**`Core System-backend@feature_1`** — 3 commit tách riêng theo đơn vị logic, đã push lên GitLab (`42fd253..60570b1`):
- `3779ae8` — kill-switch `PAYROLL_TEMPLATE_ENFORCE` + endpoint shadow-mode `GET /Core System/template-impact/{periodId}` (Task 5.1+5.2).
- `e5683b6` — migration `pit_brackets` (thêm 5 bậc thuế 2026, additive, xem `PIT-Formula-Fix-270726.md` mục 5).
- `60570b1` — un-ignore `Core System-backend/docs/` (`.gitignore` trước đó chặn toàn bộ thư mục này khỏi git — đã tách riêng phần thay đổi của mình khỏi 1 khối thay đổi KHÁC không liên quan đang uncommitted sẵn trong `.gitignore` từ trước, không commit hộ phần đó) + 3 file doc (Task 7).

**`Core System-frontend@feature_1`** — 1 commit `e340672` (Task 6, UI template + gán NV), sau đó **rebase lên `origin/develop`** theo yêu cầu người dùng (MR đang conflict) → `ea7b59a`, force-push (`--force-with-lease`) lên GitLab. 1 file xung đột duy nhất (`TinhLuongExcel.tsx`, cả 2 nhánh cùng sửa) ở 3 điểm — 2 điểm đầu chỉ là thêm state/mount độc lập (gộp cả 2 phía); điểm thứ 3 phát hiện `develop` đã dời nút "+ Cột mới" từ JSX nội tuyến sang prop `onAddColumn` của `FormulasRibbon` — đã bỏ không tái tạo lại nút trùng, chỉ giữ 2 nút mới của Task 6. Verify sau rebase: `tsc --noEmit` sạch, `next build` sản xuất thật 41/41 trang, 0 lỗi.

## 12. Review UX sau khi Task 6 lên UI thật — 3 gap phát hiện, PLAN riêng để đóng (270726)

Sau khi push xong, người dùng xem trực tiếp 2 ảnh chụp màn hình `PayrollTemplateModal`/`EmployeeTemplateAssignPanel` thật và hỏi 3 câu (qua `/orca-workflow`) — cả 3 đều lộ ra gap thật, đã verify bằng cách grep/đọc code trực tiếp, không suy đoán:

1. **Không có nơi xem danh sách record đã gán** — `ListAssignmentsByEmployee` chỉ tra được 1 NV/lần, không có endpoint nào liệt kê "ai đang gán template X" hay toàn hệ thống. `PayrollTemplateModal` chỉ hiện `componentCount`, không hiện số NV đang dùng.
2. **Banner "Chưa ảnh hưởng bảng lương thật..."** rò rỉ tham chiếu nội bộ (`"Task 5, PLAN 260726"`) vào UI người dùng cuối, và ngụ ý sai rằng C&B có thể tự "bật cấu hình enforce" trong UI — thực tế đó là biến môi trường `PAYROLL_TEMPLATE_ENFORCE`, chỉ ops đổi được. Banner còn là text TĨNH — sẽ nói sai (vẫn bảo "chưa ảnh hưởng") ngay khi ops bật enforce thật, vì FE không có cách nào đọc trạng thái enforce thật.
3. **Phát hiện quan trọng nhất:** endpoint shadow-mode `GET /Core System/template-impact/{periodId}` (Task 5.2, đã xanh ở backend) **không có màn hình FE nào gọi tới** (grep 0 kết quả) — mục đích duy nhất của Task 5.2 (C&B xem trước tác động trước khi bật enforce thật) hiện chưa dùng được vì thiếu UI.

**Kết luận:** tính năng hiện tại phù hợp **UAT** (dev/QA tự test qua API trực tiếp), **chưa sẵn sàng go-live** cho tới khi 3 gap trên đóng.

**Quyết định người dùng:** lên PLAN thi hành chi tiết (không code ngay) để thực hiện ở phiên chat mới. PLAN đầy đủ Files/Interfaces/Steps: `llmwiki/wiki/sources/draft/270726-Core System-template-audit-and-preview-ui-PLAN.md` — 4 task (A: 2 endpoint backend mới — liệt kê assignment theo template + đọc trạng thái kill-switch; B: hiện danh sách NV đang gán trong `PayrollTemplateModal`; C: màn hình mới "Xem trước tác động" nối vào `GET /Core System/template-impact` lần đầu tiên; D: sửa banner dùng trạng thái enforce thật thay vì text tĩnh). Không có migration DB nào (bảng đã đủ từ Task 3).

**Cập nhật 270727 — Task A/B/C/D đã code xong** (bởi 1 phiên khác chạy song song, xác nhận qua `git log`: `eb52c62` Task A, `30bcda7` Task B+D, `dcea23c` Task C). Sau đó theo yêu cầu người dùng: bỏ hẳn nút "Xem trước tác động" (Task C UI) — xoá `TemplateImpactReportModal.tsx` + dọn API client không còn dùng, **giữ nguyên** endpoint backend `GET /Core System/template-impact/{periodId}` (dùng lại được sau). Thêm **Task E** (không có trong PLAN gốc, phát sinh khi người dùng hỏi "record được gán ở đâu" rồi yêu cầu thêm 1 màn hình tổng hợp): `GET /config/employee-Core System-templates` (liệt kê TOÀN BỘ assignment, lọc theo phạm vi công ty của người gọi — xác nhận với người dùng chọn có lọc scope, verify bằng test 2 công ty thật Enterprise/UNI không rò rỉ chéo) + màn hình `AllAssignmentsModal.tsx` (bảng đọc-only, tìm+lọc công ty/cấu trúc). Cả 2 repo đã build/test sạch, commit + push `feature_1`.

### Hướng dẫn thao tác: bật `PAYROLL_TEMPLATE_ENFORCE` thật (270727, bổ sung — trước đây chỉ nói khái niệm, chưa ghi cách làm cụ thể)

- **Dev local:** thêm dòng `PAYROLL_TEMPLATE_ENFORCE=on` vào `Core System-backend/.env`, restart backend (`go run ./cmd/Core System` hoặc container). Xác nhận bằng `GET /api/v1/Core System/template-enforce-status` → `{"enabled":true}`, hoặc 2 banner động trong `PayrollTemplateModal`/`EmployeeTemplateAssignPanel` sẽ đổi màu/nội dung ngay.
- **Staging/production:** repo **không chứa** cấu hình deploy (không `docker-compose`, không `.gitlab-ci.yml`) — biến môi trường ở các môi trường đó được quản lý ngoài repo (secrets CI/CD hoặc cấu hình server/K8s). Cần hỏi người phụ trách hạ tầng để biết chính xác nơi đặt `PAYROLL_TEMPLATE_ENFORCE=on`.
- Không có nút nào trong UI để tự bật — đây là chủ đích thiết kế (Task 5.1), không phải thiếu sót.

### ⚠️ Phát hiện nghiêm trọng 270727 — nguồn gây PIT tự reset về bug cũ (đã xảy ra 2 lần trong phiên)

Điều tra theo yêu cầu người dùng sau khi PIT bị reset về `component_type='system'` 2 lần liên tiếp trong cùng 1 phiên làm việc. **Đã xác nhận nguyên nhân bằng đọc code trực tiếp (không suy đoán):**

- `Core System-backend/cmd/Core System/main.go:76` gọi `database.RunMigrations(db)` **VÔ ĐIỀU KIỆN MỖI LẦN BACKEND KHỞI ĐỘNG** (khi `AUTO_MIGRATE=true`, mặc định — xác nhận `.env` có `AUTO_MIGRATE=true`), KHÔNG có tracking/skip (khác hẳn `RunFileMigrations` cho `migrations/*.sql` — cái đó CÓ bảng `schema_migrations` theo dõi).
- `RunMigrations` chạy 1 danh sách ~50 chuỗi SQL Go-const, trong đó `migrationSalaryComponentsV4` (`internal/database/database.go:2546`) làm **`DELETE FROM salary_components; INSERT INTO salary_components (...) VALUES (...)`** — xoá sạch và tái tạo TOÀN BỘ bảng từ snapshot hardcode trong Go source, bao gồm dòng `(1410, 'PIT', 'Thuế TNCN', 'system', '', '', ...)` (dòng 2762) — **đúng y hệt giá trị lỗi cứ tái xuất hiện**.
- Migration `20260727000000_pit_system_to_formula.sql` của tôi (ở `atlas/migrations/`, áp bằng `psql -f` thủ công) **không nằm trong danh sách `RunMigrations`** → mỗi lần backend restart, `migrationSalaryComponentsV4` ghi đè lại PIT về giá trị cũ, xoá sạch fix của tôi. `pit_brackets` không bị ảnh hưởng vì nó là bảng khác, `migrationSalaryComponentsV4` chỉ đụng `salary_components`.
- **Bằng chứng độc lập xác nhận đây không phải bug mới**: `salary_component_history` có 5 dòng `PIT`/`changed_by='system'` trong vòng ~5 phút ngày 2026-05-27 — dấu hiệu của nhiều lần restart backend liên tiếp trong 1 phiên dev cũ, khớp đúng cơ chế này (dù entry đó không phải do chính `migrationSalaryComponentsV4` ghi — bảng DELETE+INSERT không tự ghi history, cần điều tra thêm nếu muốn biết chính xác migration nào ghi các dòng đó).
- **Quy ước ĐÚNG của chính codebase này** (xác nhận qua đối chiếu `migrationPaidDaysToFormula`, dòng 1472): khi convert 1 component từ `system` → `formula` "thật sự bền", giá trị hardcode BÊN TRONG `migrationSalaryComponentsV4` phải được sửa trực tiếp (ví dụ `PAID_DAYS` trong V4 đã là `'formula'` sẵn, không phải `'system'`) — **không đủ nếu chỉ chạy 1 migration rời ở `atlas/migrations/` hay chạy tay 1 lần**, vì `migrationSalaryComponentsV4` sẽ luôn thắng ở lần restart kế tiếp.

**Blast radius rộng hơn PIT:** đây là rủi ro áp dụng cho MỌI cột lương, không riêng PIT — bất kỳ chỉnh sửa nào qua UI (`SalaryComponentModal`, sửa formula/is_visible...) mà KHÔNG được đồng bộ vào snapshot hardcode trong `migrationSalaryComponentsV4` đều có thể bị xoá về giá trị cũ ở lần backend restart tiếp theo, nếu `AUTO_MIGRATE=true` ở môi trường đó (chưa xác nhận production có giống dev hay không — repo không có cấu hình deploy để kiểm).

**Chưa sửa** — đây là thay đổi vào file bootstrap dùng chung mọi môi trường (`database.go`), cần người dùng xác nhận hướng xử lý trước khi tôi sửa (xem hỏi trong hội thoại).

**Đã sửa 270727**: thêm `migrationPITSystemToFormula` vào `internal/database/database.go` (đặt SAU `migrationSalaryComponentsV4` trong danh sách `RunMigrations`, cùng quy ước `migrationPaidDaysToFormula` đã có sẵn — `UPDATE ... WHERE component_type='system'`, tự-hồi mỗi restart, no-op sau lần đầu). Verify bằng mô phỏng thật (reset PIT → chạy SQL lần 1 sửa đúng → chạy lần 2 xác nhận `UPDATE 0`). Commit `fe8805b`, đã push.

## 13. Quyết định HOLD toàn bộ tính năng "Cấu trúc lương theo cấp bậc" (270727)

**Cập nhật 060826: HOLD đã kết thúc.** Toàn bộ PLAN `040826-Core System-template-on-giatbh-engine-PLAN.md`
(Task 0-8) đã hoàn tất — xem PLAN mục "Tiến độ" để có tóm tắt đầy đủ + commit hash từng task. Tính
năng hiện ĐANG BẬT ở dev local (`PAYROLL_TEMPLATE_ENFORCE=on`). Phần dưới đây là lịch sử quyết định
HOLD gốc (270727), giữ nguyên làm bằng chứng — không còn phản ánh trạng thái hiện tại.

Người dùng quyết định **tạm dừng** mọi phát triển tiếp cho tính năng này (Task 4/5/6/A-E) — sẽ triển khai ở 1 phase sau, chưa xác định thời điểm. Không huỷ/rollback code đã có — chỉ dừng làm thêm.

**Xác nhận an toàn khi HOLD (đã verify bằng test, không suy đoán):** kill-switch `PAYROLL_TEMPLATE_ENFORCE` mặc định OFF khiến TOÀN BỘ engine tính lương (`Calculate`/`CalculateOne`/`Finalize`) chạy **giống hệt** như trước khi tính năng này tồn tại — khối mask-về-0 trong `computeEmployee` nằm trong `if sh.templateEnforce {...}`, không có nhánh nào đọc `employee_payroll_templates` khi cờ này false, kể cả khi đã có dữ liệu gán thật qua UI. 3 test khoá bất biến xác nhận: `TestTemplateEnforce_KillSwitchDefaultOff`, `TestTemplateEnforce_NoAssignmentUnchanged`, `TestTemplateEnforce_SnapshotSkippedWhenDisabled`. **An toàn để HOLD vô thời hạn, không ảnh hưởng Core System đang chạy thật.**

**Trạng thái dừng lại (để phiên sau đọc, không cần hỏi lại từ đầu):**
- Backend: Task 3.5→7 (260726-PLAN) + Task A/E (270726-PLAN, audit + aggregate view) + PIT self-heal fix — đều đã code, test xanh, commit, push `feature_1`.
- Frontend: Task 6 (CRUD template/assign) + Task B/D (audit list + banner động) + Task E (màn hình tổng hợp) — đã code, test xanh, commit, push `feature_1`. Task C (màn hình "Xem trước tác động") đã build rồi **bị xoá lại theo yêu cầu người dùng** (270727) — không còn UI nào gọi `GET /Core System/template-impact/{periodId}`, nhưng endpoint backend vẫn còn, dùng lại được nếu cần.
- **KHÔNG làm tiếp** cho tới khi có yêu cầu mới: không thêm task/gap nào từ `270726-Core System-template-audit-and-preview-ui-PLAN.md` nếu còn sót (đã đóng đủ 3 gap chính đợt này), không tự ý bật `PAYROLL_TEMPLATE_ENFORCE` ở bất kỳ môi trường nào.

## 14. Tái mở phase sau — tổng hợp kiến trúc + phát hiện mới (040826)

Người dùng yêu cầu mở lại tính năng đang HOLD (mục 13) và **tổng hợp lại kiến trúc + logic hoạt động trước khi mở rộng**. Phiên 040826 là phiên **thuần phân tích + lên kế hoạch, không sửa một dòng code nào**. Mọi khẳng định dưới đây được kiểm lại trực tiếp trên code và trên DB `payroll_engine` thật ở thời điểm 2026-08-04, không chép lại từ các mục cũ của chính tài liệu này — và một số kết luận cũ đã bị chính việc kiểm lại đó bác bỏ (xem 14.6).

**Lưu ý về tên gọi:** người dùng gọi tính năng này là "template cho payslip". Đúng đối tượng là "Cấu trúc lương theo cấp bậc" (`payroll_templates` + `template_components` + `employee_payroll_templates`) — nó không phải template in ấn/bố cục phiếu lương, mà là thứ quyết định **nhân viên nào được tính cột lương nào**, nên hệ quả cuối cùng là hình dạng phiếu lương. Trong repo không tồn tại bất kỳ khái niệm "payslip template" nào khác (đã grep toàn bộ 3 repo).

### 14.1 Tính năng bị tắt bằng HAI công tắc độc lập, không phải "comment lại"

Không có khối code nào bị comment. Tính năng bị vô hiệu bằng hai cơ chế nằm ở hai repo khác nhau, và **cả hai đều phải được mở** mới có hiệu lực thật:

| Công tắc | Vị trí | Giá trị hiện tại | Tắt cái gì |
|---|---|---|---|
| `SALARY_STRUCTURE_FEATURE_VISIBLE` | `Core System-frontend/components-page/tinh-luong/TinhLuongExcel.tsx:57` | `false` | Ẩn 3 nút ribbon (`:4483`, `:4491`, `:4501`) — người dùng không có đường vào UI. Modal/state/API client vẫn nằm trong bundle, import static (`:43-45`). |
| `PAYROLL_TEMPLATE_ENFORCE` | biến môi trường, đọc ở `Core System-backend/internal/service/payroll_service.go:384-386` | **không có trong `.env`** → OFF | Engine không mask gì cả. Khối mask nằm trong `if sh.templateEnforce` (`payroll_service.go:500`), snapshot lúc Finalize gate riêng (`:1541`). |

Hệ quả cần nhớ khi mở lại: **bật FE mà không bật BE** cho ra trạng thái "HR cấu hình được, gán được, nhưng lương không đổi" — đây chính là giai đoạn cấu hình an toàn có chủ đích, không phải lỗi. **Bật BE mà không bật FE** thì enforce có hiệu lực thật trên dữ liệu đã gán sẵn mà không ai nhìn thấy màn hình quản lý — nguy hiểm.

### 14.2 Kiến trúc 4 tầng và luồng chạy thật

Mô hình 3 tầng ngành (Component → Structure → Assignment) được cài đặt thành 4 tầng trong dự án này, vì tầng thi hành (mask) được tách hẳn ra khỏi tầng lưu trữ:

```
Tầng 1  salary_components (110 dòng: 69 input + 41 formula)   — cột lương + công thức
Tầng 2  payroll_templates ×  template_components               — "cấu trúc lương" = 1 TẬP cột
Tầng 3  employee_payroll_templates                             — gán NV ↔ template, CÓ ngày hiệu lực
Tầng 4  buildTemplateMaskFormulas + calcShared.templateEnforce  — thi hành: mask-về-0
```

Luồng runtime của một lần `Calculate` một kỳ, theo đúng thứ tự code:

1. `Calculate` tính `periodEnd` = ngày 20 của tháng kỳ (`payroll_service.go:211`), rồi gọi `loadTemplateMaskData(ctx, empIDs, periodEnd)` (`:300`).
2. `loadTemplateMaskData` (`:400-418`) nạp đúng hai thứ, mỗi thứ **một truy vấn bulk cho cả kỳ**, không phải per-employee: `ResolveAssignedTemplatesAsOf` (`payroll_template_repo.go:199`, dùng `SELECT DISTINCT ON (employee_id)` + `sqlx.In`) trả `tplByEmp: map[employeeID]templateID`; và `ListAllTemplateComponentCodes` (`:231`) trả `tplCodes: map[templateID][]code`. Từ `tplCodes` nó dựng luôn `tplUniverse = buildTemplateUniverse(tplCodes)` (`:417`) — không query thêm.
3. Ba giá trị đó cùng cờ `templateEnforce: templateEnforceEnabled()` (`:317`) được nhồi vào struct `calcShared` — struct dùng chung cho toàn bộ nhân viên của kỳ.
4. Với từng nhân viên, `computeEmployee` (`:499-535`) làm: nếu cờ bật **và** NV có template, tính `mask` rồi **trộn mask xuống dưới** override thật (`merged[code] = f` cho mask trước, cho `overrideFormulas` sau) — nên override phòng ban/nhân viên **luôn thắng** mask. Đây là thứ tự ưu tiên có chủ đích: template là mức thấp nhất.
5. `cacheKey = tplSig + "|" + sig` (`:524`) — engine được cache theo cặp (template, chữ ký override). Lập luận injective: `tplSig` là rỗng hoặc UUID, không chứa `|`.
6. Cột bị mask được **xoá khỏi input** (`:536-546`) để engine chạy formula `"0"` thay vì giữ giá trị input đã nạp từ attendance.
7. `base_values` (dấu "ô bị ghi đè" trên FE) **chỉ sinh khi `sig != ""`** (`:552-561`) — cố tình không sinh cho mask, nếu không 12k nhân viên có template sẽ chạy engine hai lần mỗi người.
8. Lúc `Finalize`, `snapshotTemplateMasksForPeriod` (`:1540-1588`) ghi mask đã dùng vào `payroll_formula_snapshots` với `scope_type='template'`, `scope_ref=templateID` — **tái dùng bảng snapshot công thức có sẵn**, không có bảng `payroll_template_masks` nào. Dedupe theo template nên 12k nhân viên chỉ ghi ~N dòng theo số template.

Điểm kiến trúc đáng giá nhất: **`engine.go` không bị sửa một dòng nào**. Mask được thi hành bằng cách sinh override `formula = "0"` rồi đi qua đúng đường ống `scopedResolver` → `applyResolvedFormulas` → `engineCache` mà tính năng override phòng ban/nhân viên đã dùng từ trước. Component bị mask vẫn nằm trong đồ thị phụ thuộc, nên topological sort nguyên vẹn và mọi cột tổng tự tính lại đúng.

### 14.3 Thuật toán mask v3 — công thức chính xác

`buildTemplateMaskFormulas` (`payroll_template_mask.go:35-80`):

```
closure(T) = codes(T) ∪ {mọi code mà cột trong closure tham chiếu, đệ quy qua extractDeps}
universe   = ⋃ codes(t) với t chạy hết MỌI template đang tồn tại
mask       = { code → "0" | code ∈ universe ∧ code ∉ closure(T_nv)
                                ∧ code ∉ statutoryOverrideBlocklist
                                ∧ component_type ≠ "system" }
```

Ba chốt an toàn bằng `return nil` (không mask gì): `len(templateCodes) == 0` (`:36`), `len(maskableUniverse) == 0` (`:36`), `len(mask) == 0` (`:76`). Nhân viên không có assignment thì vắng key trong `tplByEmp` nên không vào nhánh mask — đúng TASK-REF "tính đủ như cũ".

Điều khiến v3 khác hẳn hai vòng thiết kế trước: **`universe` là dữ liệu, không phải hằng số**. Một cột là "phụ cấp theo cấp bậc" khi và chỉ khi có ít nhất một template liệt kê nó. Cột không nằm trong template nào — mọi cột tổng, cột vận hành, lương cơ bản — nằm ngoài universe nên không bao giờ bị mask, và HR thêm/bớt phụ cấp chỉ cần sửa template qua UI, không sửa code.

### 14.4 Trạng thái dữ liệu thật trên `payroll_engine` (đo 2026-08-04)

| Bảng | Số dòng | Ghi chú |
|---|---|---|
| `salary_components` | 110 | 69 `input` + 41 `formula`; **0 dòng `component_type='system'`**; `is_system=true` đúng 1 dòng (PIT) |
| `payroll_templates` | **1** | `demo 1`, `is_default=false`, tạo 2026-07-27 16:51 — dữ liệu UAT còn sót |
| `template_components` | **0** | template `demo 1` **không có cột nào** |
| `employee_payroll_templates` | **1** | `THAIDT001 / Thai DT` → `demo 1`, từ `2026-07-01`, `effective_to` NULL, `created_by=user@company.test` |
| `salary_component_overrides` | 0 | |
| `employee_levels` | **29** | tài liệu cũ ước "~12 cấp bậc" — sai, thực tế 29 |
| `employees` | 12.044 | **6.357 có `employee_level_id`** (52,8%), 5.687 trống |

Dòng assignment thật đó **hiện vô hại** nhưng là mìn: template nó trỏ tới có 0 cột, nên `len(templateCodes)==0` → `return nil` → không mask; đồng thời `universe` cũng rỗng. Tức là ngay cả khi bật `PAYROLL_TEMPLATE_ENFORCE=on` lúc này, lương của `THAIDT001` **không đổi**. Nhưng nếu ai đó thêm cột vào `demo 1` rồi bật cờ, người này bị enforce ngay mà không qua bất kỳ bước duyệt nào. Phải dọn trước khi bật.

### 14.5 Hàng rào test đang có

10 test trong `internal/service/payroll_template_enforce_integration_test.go` khoá các bất biến: mask cho ra 0 (`:80`), cột mask không cộng vào GROSS (`:113`), **không assignment thì không đổi gì** (`:153`), dependency của cột template được giữ (`:190`), cột pháp định không bao giờ bị mask (`:224`), override thắng mask (`:272`), `CalculateOne` khớp `Calculate` và đúng point-in-time (`:307`), Finalize ghi snapshot khớp mask thật (`:425`), **kill-switch mặc định OFF** (`:540`), **snapshot bị bỏ khi cờ tắt** (`:576`). Thêm test repo (bulk resolve, bulk codes, snapshot, scope filter), test route permission cho cả hai endpoint `/Core System/template-impact` và `/Core System/template-enforce-status`.

Phía frontend: **0 test** cho cả ba component (`PayrollTemplateModal`, `EmployeeTemplateAssignPanel`, `AllAssignmentsModal`) — đã grep, không có unit lẫn e2e.

### 14.6 Sáu phát hiện mới của phiên 040826, xếp theo mức độ nguy hiểm

Tất cả đều đã kiểm bằng lệnh thật, không suy đoán. Ba phát hiện đầu **bác bỏ trực tiếp** các kết luận đang ghi trong chính tài liệu này.

**(1) NẶNG NHẤT — "phòng thủ nhiều lớp" của mask thực chất chỉ còn MỘT lớp.** Mục 7/9 của tài liệu này ghi mask được bảo vệ bởi ba thứ: `maskableUniverse`, `statutoryOverrideBlocklist`, và loại trừ `component_type == "system"`. Đo trên DB thật thì hai lớp sau **đã chết**:
- `statutoryOverrideBlocklist` (`salary_component_service.go:25-30`) gồm 4 mã `PIT`, `BHXH_NV`, `BHYT_NV`, `BHTN_NV`. Trong DB **chỉ `PIT` tồn tại**. Ba mã bảo hiểm kia không có; mã bảo hiểm thật đang dùng là `TOTAL_INS`, `TOTAL_INS_CTY`, `INS_SAL_BH`, `INS_SAL_UI` — **không mã nào nằm trong blocklist**.
- `component_type == "system"` khớp **0 dòng**, vì PIT đã được chuyển từ `system` sang `formula` ngày 270726 (mục 10 + `PIT-Formula-Fix-270726.md`). Guard này giờ là code chết.

Nghĩa là hôm nay `GROSS`, `NET_PAY`, `TAXABLE_INC`, `TOTAL_INS`, `EARNED_SAL` **chỉ được bảo vệ bởi đúng một điều kiện**: chúng không nằm trong template nào. Đây là hệ quả phụ ngoài ý muốn của bản fix PIT — fix đó đúng cho PIT nhưng đã âm thầm rút một lớp bảo vệ của mask mà không ai ghi lại.

**(2) NẶNG — biện pháp giảm rủi ro mà tài liệu tuyên bố đã có thực tế CHƯA BAO GIỜ được xây.** Mục 7 (dòng 131) ghi rủi ro "HR lỡ đưa cột TỔNG vào template" được chặn bằng "(a) UI Task 6 chỉ cho chọn cột phụ cấp/earning, ẩn cột tổng". Đọc code thật: `PayrollTemplateModal.tsx:134` là `allComponents.map(...)` — **không có bộ lọc nào**. Toàn bộ 110 cột kể cả `GROSS`/`NET_PAY`/`TAXABLE_INC` đều hiện thành checkbox tick được. Ghép với phát hiện (1): chỉ cần một lần HR tick nhầm `GROSS` vào một template bất kỳ là `GROSS` vào universe, và từ đó **mọi nhân viên thuộc template khác bị mask `GROSS = 0`** — sai tiền toàn tập, im lặng, không lỗi, không test nào đỏ. Đây là đường đi ngắn nhất từ "một cú tick" tới "sai lương hàng loạt".

**(3) NẶNG — báo cáo shadow-mode nói dối theo hướng an toàn giả.** `ComputeTemplateImpact` (`payroll_service.go:747-760`) truyền `salaryOverrides: map[string]float64{}` **rỗng** cho cả hai lần mô phỏng. `BASIC_SAL` không có trong DB (`source_field=''` có chủ ý, chỉ đến từ file Excel HR nạp) nên cả hai lần đều ra 0, mọi cột dẫn xuất theo lương ra 0, delta triệt tiêu. Báo cáo sẽ in ra "không có tác động" trong khi thực tế có. Điều đáng nói: **chính repo đã biết** — comment ở `:814-819` mô tả đúng lỗi này, và hàm em sinh sau nó (`ComputeFormulaImpact`) chọn cách đúng là **từ chối thẳng** bằng `ErrFormulaImpactNoSalaries` thay vì trả số dối. `ComputeTemplateImpact` chưa được sửa theo. Vì shadow-mode là **cổng duyệt duy nhất** trước khi bật enforce (mục 9 dòng 171), một cổng luôn trả "an toàn" còn tệ hơn không có cổng.

**(4) TRUNG BÌNH — `employee_payroll_templates` chỉ tồn tại trong Atlas, không có trong đường migration inline.** Bảng được tạo bởi `atlas/migrations/20260726000000_employee_payroll_templates.sql`, nhưng grep `internal/database/database.go` và `internal/db/schema.sql` đều **0 kết quả**. Môi trường nào khởi tạo schema bằng `RunMigrations` (đường inline, `AUTO_MIGRATE=true` — mặc định) sẽ **thiếu bảng**. Và `loadTemplateMaskData` **nuốt lỗi** (`:405-408`: log rồi trả nil) nên biểu hiện duy nhất là một dòng log `[templateMask] ... (bỏ qua enforce)` — enforce âm thầm không chạy, cờ vẫn báo `on`, không ai biết. Đây là cùng họ vấn đề với rủi ro `migrationSalaryComponentsV4` ở mục 12.

**(5) TRUNG BÌNH — banner chỉ người dùng tới một cái nút không tồn tại.** `PayrollTemplateModal.tsx:109` viết: *"Xem trước tác động bằng nút \"Xem trước tác động\""*. Grep toàn frontend: chuỗi đó **chỉ xuất hiện đúng ở dòng đó**, `TemplateImpactReportModal.tsx` đã bị xoá (mục 13). Đây là hệ quả trực tiếp của việc xoá Task C mà không sửa lại text Task D. Kèm theo, khi `getTemplateEnforceStatus()` lỗi thì `enforceEnabled = null` → falsy → banner hiển thị **"đang TẮT"** dù chưa biết gì — fail-unsafe, nói "chưa ảnh hưởng lương thật" trong tình huống có thể đang bật.

**(6) NHẸ nhưng chặn vận hành — không có đường sửa/xoá assignment trên UI, và `isDefault` không có control.** Ba hàm API client tồn tại nhưng **0 điểm gọi**: `updateEmployeeTemplateAssignment`, `deleteEmployeeTemplateAssignment`, `resolveEmployeeTemplate` (`lib/api/config.ts:228`, `:232`, `:236`). Gán sai chỉ còn cách sửa bằng SQL tay. Đồng thời `isDefault` được đọc và gửi lên (`PayrollTemplateModal.tsx:53`, `:66-67`) nhưng **không có checkbox nào** để bật — nên qua UI không bao giờ tạo được template mặc định, trong khi `EmployeeTemplateAssignPanel.tsx:56` lại dựa đúng vào `t.isDefault` để gợi ý template. Tính năng gợi ý theo cấp bậc vì thế **không bao giờ gợi ý được gì**.

Ngoài ra, hai kết luận cũ của mục 12 nay **đã hết hiệu lực** (đã được sửa ở commit `30bcda7`, không phải nợ nữa): banner không còn là text tĩnh (đã đọc trạng thái thật qua `getTemplateEnforceStatus`), và không còn rò tham chiếu nội bộ "Task 5, PLAN 260726" ra UI người dùng.

### 14.7 Khoảng trống kiến trúc lớn nhất: chưa có liên kết cấp bậc → template

Tên tính năng là "Cấu trúc lương theo **cấp bậc**", nhưng dữ liệu **không mô hình hoá cấp bậc ở đâu cả**: `employee_payroll_templates` khoá theo `employee_id`, không theo `employee_level_id`. Liên kết cấp bậc hiện chỉ tồn tại dưới dạng một câu gợi ý trong UI (`EmployeeTemplateAssignPanel.tsx:54-56`), mà như phát hiện (6) cho thấy còn không chạy được.

Hệ quả vận hành cụ thể: 6.357 nhân viên có cấp bậc, 29 cấp bậc, nhưng để enforce có nghĩa thì HR phải **gán tay từng nhân viên một**. SPEC gốc đã đặt "không tự động gán template cho NV hiện có" vào Non-goals và ghi rõ đó là "một bước migrate dữ liệu cần xác nhận riêng" — bước đó **chưa từng được quyết định**. Đây chính là điểm chặn go-live thật sự, lớn hơn mọi gap UI.

### 14.8 Nợ còn treo, gom lại một chỗ

| # | Hạng mục | Nguồn | Trạng thái |
|---|---|---|---|
| N1 | Lớp bảo vệ mask chỉ còn universe (blocklist + system chết) | phát hiện (1) | mới, chưa xử lý |
| N2 | Picker cột không lọc cột tổng | phát hiện (2) | mới, chưa xử lý |
| N3 | Shadow-mode trả số dối vì thiếu `salaries` | phát hiện (3) + comment `:814-819` | đã biết, chưa sửa |
| N4 | Bảng thiếu ở đường migration inline | phát hiện (4) | mới, chưa xử lý |
| N5 | Banner trỏ nút đã xoá + fail-unsafe | phát hiện (5) | mới, chưa xử lý |
| N6 | Không sửa/xoá được assignment; `isDefault` không có UI | phát hiện (6) | mới, chưa xử lý |
| N7 | Chưa có liên kết cấp bậc → template; chưa có gán hàng loạt | 14.7 + SPEC Non-goals | chờ quyết định nghiệp vụ |
| N8 | Cột bị mask không được đánh dấu trên lưới (cần `maskedComponents` trong response) | PLAN 260726 Task 6.4 bước 5 | để ngỏ có chủ đích |
| N9 | Export/báo cáo Excel không ẩn được cột theo từng NV → hiện 0 | mục 8 điểm #3 | giới hạn cố hữu, chỉ cần báo trước C&B |
| N10 | Dọn 1 template `demo 1` + 1 assignment UAT trước khi bật | 14.4 | mới, chưa xử lý |
| N11 | `migrationSalaryComponentsV4` DELETE+INSERT lại `salary_components` mỗi lần restart | mục 12 | đã sửa riêng cho PIT, rủi ro tổng quát còn |

Kết luận cho việc mở rộng: phần **lưu trữ và CRUD đã xong và chắc**; phần **thi hành (mask) đúng về kiến trúc nhưng lớp an toàn đã mỏng đi sau bản fix PIT**; phần **cổng duyệt trước khi bật (shadow-mode) đang hỏng theo hướng nguy hiểm**; và phần **nghiệp vụ cốt lõi (cấp bậc → template, gán hàng loạt) chưa từng được thiết kế**. Bất kỳ kế hoạch mở rộng nào cũng nên đóng N1/N2/N3 trước khi nói đến chuyện bật enforce, vì ba mục đó cùng nhau tạo ra một đường đi im lặng từ một cú tick sai tới sai lương hàng loạt mà cổng duyệt hiện tại không bắt được.

## 15. Đối chiếu với engine của `giatbh` — lấy engine họ làm nền (040826)

Người dùng chốt hướng: **các thay đổi engine backend từ commit của `giatbh` là chuẩn chính; việc của ta là triển khai ý tưởng "cấu trúc lương theo cấp bậc" TRÊN NỀN engine của họ**, không đi hướng riêng. Mục này so sánh logic hai bên và ghi lại những gì việc so sánh đó lộ ra.

### 15.1 Bối cảnh git — hai bên đã ở cùng một nhánh

`giatbh` là `Trần Bùi Hoàng Gia <hgia.tb@gmail.com>` (21 commit). Điểm cần biết trước khi bàn kỹ thuật: **`feature_v2` HEAD hiện tại chính là `origin/giatbh`** — cùng trỏ `bf1f46e`. Nghĩa là không có việc "merge engine của họ vào" nào phải làm: code template của ta (đi từ `feature_1` → `develop`) và engine mới của họ (base trên `develop`) **đã nằm chung một cây làm việc**. Việc so sánh ở đây là so **logic có xung đột/lệch nguyên tắc**, không phải so để hợp nhất mã.

Nhánh của họ có tài liệu bàn giao riêng: `Core System-backend/HANDOVER-giatbh.md` (116 dòng, 15 nhóm thay đổi A–O). Ba cơ chế migration mà tài liệu đó nêu là chìa khoá để hiểu mọi thứ còn lại:

| Cơ chế | Chạy khi nào | Ghi chú |
|---|---|---|
| Go self-heal trong `RunMigrations()` (`internal/database/database.go`) | **MỖI lần backend boot**, idempotent | Đây là cơ chế bootstrap DB **thật** |
| File migration `migrations/v*.sql` qua `RunFileMigrations()` | **Một lần duy nhất**, tracked ở `schema_migrations` | v53–v56 |
| **Atlas `atlas/migrations/*.sql`** | **KHÔNG BAO GIỜ tự chạy** — `cmd/Core System/main.go` không gọi Atlas | Chỉ là hồ sơ lịch sử |

### 15.2 KHUYẾT TẬT CHÍ TỬ — `template_components` bị xoá sạch mỗi lần restart

Mục K của bàn giao `giatbh` ghi một bài học kiến trúc, nguyên văn:

> *"bất kỳ bảng mới nào FK vào `salary_components.id` sẽ dính lỗi tương tự — LUÔN dùng `component_code` làm khoá tham chiếu ổn định, không dùng `id`."*

Họ rút ra bài học đó sau khi bảng `salary_component_versions` của chính họ bị xoá sạch **3 lần liên tiếp** trong lúc phát triển. Bảng `template_components` của ta vi phạm đúng điều luật đó:

```
template_components_component_id_fkey
    FOREIGN KEY (component_id) REFERENCES salary_components(id) ON DELETE CASCADE
```

Và `migrationSalaryComponentsV4` — nằm trong danh sách `RunMigrations()` nên **chạy mỗi lần backend boot** — mở đầu bằng đúng hai dòng này (`database.go:2588-2591`), kèm comment của chính tác giả V4:

```sql
-- STEP 1: XÓA TOÀN BỘ (cascade xóa template_components)
DELETE FROM salary_components;
```

Tác giả V4 **đã biết** nó cascade-xoá `template_components` và ghi thẳng vào comment như một tác dụng phụ được chấp nhận — vì lúc viết V4, tính năng template chưa tồn tại nên bảng đó luôn rỗng. Sau khi ta xây tính năng lên bảng đó, câu comment cũ trở thành mô tả một sự phá hoại dữ liệu thật.

**Bằng chứng thực nghiệm khớp hoàn hảo** (đo trên `payroll_engine` ngày 2026-08-04): `payroll_templates` còn **1 dòng** (bảng này V4 không đụng), `employee_payroll_templates` còn **1 dòng** (FK trỏ `payroll_templates`, `ON DELETE RESTRICT`, không dính cascade), nhưng `template_components` = **0 dòng**. Đây không phải "template UAT chưa kịp chọn cột" như mục 14.4 phỏng đoán ban đầu — đây là dấu vết của việc cấu hình đã bị xoá.

**Vì sao đây là chí tử chứ không phải bất tiện:** `tplCodes` được nạp từ `template_components`; sau mỗi restart mọi template có 0 cột → `len(templateCodes) == 0` → `buildTemplateMaskFormulas` trả `nil` → **enforce âm thầm trở thành no-op cho toàn bộ nhân viên**. Ghép với banner FE: khi ops bật `PAYROLL_TEMPLATE_ENFORCE=on`, `PayrollTemplateModal.tsx:108` sẽ hiển thị *"Cấu hình enforce ĐANG BẬT — cấu trúc lương bạn tạo/sửa ở đây SẼ ảnh hưởng bảng lương thật"* trong khi thực tế nó **không ảnh hưởng gì**, và HR không có tín hiệu nào để biết. Tính năng vừa không hoạt động, vừa nói dối rằng nó đang hoạt động.

Đây là hạng mục phải sửa **trước mọi thứ khác** — mọi task khác đều vô nghĩa nếu cấu hình không sống qua một lần restart.

### 15.3 Khuyết tật thứ hai — `employee_payroll_templates` chỉ tồn tại trong Atlas

Bảng này được tạo bởi `atlas/migrations/20260726000000_employee_payroll_templates.sql`, và grep `internal/database/database.go` + `internal/db/schema.sql` đều cho **0 kết quả**. Kết hợp với sự thật mà bàn giao `giatbh` nêu — **backend không bao giờ chạy Atlas** — hệ quả nặng hơn mục 14.6 (4) đã ghi: bảng này tồn tại trên DB dev **chỉ vì phiên 260726 đã `psql -f` bằng tay**. Trên bất kỳ máy/môi trường nào bootstrap từ đầu, bảng **không tồn tại**, `loadTemplateMaskData` nuốt lỗi (`payroll_service.go:405-408`: log rồi trả nil), và enforce âm thầm tắt trong khi endpoint `template-enforce-status` vẫn trả `{"enabled": true}`.

Cách sửa đúng theo nền của họ: dời định nghĩa bảng vào `RunMigrations()` dạng `CREATE TABLE IF NOT EXISTS` — đúng như họ đã làm với `migrationSalaryComponentVersionsTable` (`database.go:3026-3033`), kèm comment giải thích vì sao không dựa vào Atlas.

### 15.4 So sánh logic từng điểm giao với engine mới

| # | Thay đổi của `giatbh` | Đường mask của ta | Kết luận |
|---|---|---|---|
| J | Versioning hiệu-lực-theo-ngày: `ListActiveAsOf(periodEnd)` thay `ListActive()` tại 5 điểm (`payroll_service.go:214, 575, 705, 867, 1572`) | `buildTemplateMaskFormulas(sh.components, ...)` đọc `sh.components`, mà `sh.components` chính là kết quả `ListActiveAsOf` | **Tương thích, và tốt lên**: closure phụ thuộc giờ được tính trên công thức đúng của kỳ, không phải công thức mới nhất. Kể cả `snapshotTemplateMasksForPeriod` cũng đã dùng `ListActiveAsOf` (`:1572`). Không phải sửa gì. **⚠️ ĐÍNH CHÍNH 050826:** câu "tốt lên" đúng về THIẾT KẾ nhưng **sai về thực tế hiện tại** — `salary_component_versions` đang **0 dòng** nên COALESCE 3 tầng của `ListActiveAsOf` luôn rơi về tầng cuối `sc.formula` (công thức HÔM NAY). Closure vì vậy đang tính trên công thức hiện tại, không phải công thức của kỳ. Nguyên nhân: backfill chỉ nằm ở `atlas/migrations/` mà backend không chạy Atlas — xem `Report-Template-Config-Analysis-040826.md` mục 0.5 (L11). |
| J | Nguyên tắc nền: *mọi thứ ảnh hưởng tiền phải hiệu-lực-theo-ngày* | **`template_components` KHÔNG có ngày hiệu lực** | **Lệch nguyên tắc — xem 15.5.** |
| A | Engine thêm `AND`/`OR`, so sánh chuỗi `==`/`!=` | Closure dùng `extractDeps(c.Formula)` trích `[MÃ_CỘT]` | Tương thích: cú pháp mới không tạo dạng tham chiếu cột mới, `extractDeps` vẫn bắt đủ. **Cần một test khoá** điều này thay vì tin suy luận. |
| D | PIT → `component_type='formula'`, 3 nhánh (Intern / thử việc+nước ngoài / luỹ tiến 5 bậc) | Mask loại PIT qua `statutoryOverrideBlocklist` (theo **mã**, không theo type) | PIT vẫn được bảo vệ. Nhưng guard `component_type == "system"` giờ khớp **0 dòng** → code chết (đã ghi ở 14.6 (1)). |
| B | Thêm `CONTRACT_TYPE`/`EMP_TYPE`/`IS_FOREIGNER`/`WORK_TYPE` vào tập biến formula | Mask sinh `formula="0"` cho cột bị loại | Tương thích. Nhưng mở ra khả năng mới đáng cân nhắc: template có thể được thay bằng điều kiện trong formula — xem 15.6. |
| C/E/F | Trần BHXH 50.6tr, `HEALTH_INS`/`FAMILY_HEALTH_INS`, `OT_TAX=0` | Các mã này **đều nằm trong `maskableUniverse` nếu HR tick vào template** | Làm nặng thêm rủi ro 14.6 (2): tập cột có thể mask nhầm giờ gồm cả các cột pháp định/thuế mới. |
| H | Chặn `SetCell`/`CalculateOne` ghi đè `payroll_records` đã `finalized_at` | Snapshot mask của ta ghi vào `payroll_formula_snapshots` lúc `Finalize` | Không xung đột (khác bảng). Cần kiểm thứ tự: snapshot phải ghi được ở đúng lượt Finalize đó. |
| I | `409 ErrSystemComponentLocked` khi sửa component `is_system` | Mask không đi qua CRUD component | Không xung đột. |
| K | Bài học: khoá theo `component_code`, không theo `id` | `template_components.component_id` FK CASCADE vào `id` | **Vi phạm trực tiếp — 15.2.** |

### 15.5 Lệch nguyên tắc quan trọng: thành viên template không có ngày hiệu lực

Đóng góp lớn nhất của `giatbh` (mục J) sửa đúng một loại bug: *"sửa 1 formula hôm nay sẽ tính lại luôn các kỳ lương QUÁ KHỨ theo formula mới (sai)"*. Sau bản đó, công thức của từng cột là point-in-time, và `employee_payroll_templates` của ta cũng point-in-time (có `effective_from`/`effective_to`).

Nhưng **"template X gồm những cột nào" thì không**. `template_components` là ảnh chụp hiện tại, không có ngày. Hệ quả: HR sửa tập cột của một template hôm nay, rồi tính lại một kỳ quá khứ → mask được dựng theo **tập cột HÔM NAY**, không phải tập cột lúc kỳ đó chạy. Đây **đúng cùng một lớp bug** mà mục J vừa loại bỏ cho công thức, chỉ dịch sang một trục khác. Nếu lấy engine của họ làm chuẩn thì đây là chỗ ta chưa theo chuẩn.

Snapshot lúc `Finalize` (`scope_type='template'`) có ghi lại mask đã dùng, nhưng nó là **bằng chứng chỉ-ghi**: không có đường code nào đọc nó lại khi tính lại. Nên nó giúp truy vết, không giúp tính đúng.

Ba hướng xử lý, chưa chốt:
1. **Effective-dating `template_components`** theo đúng khuôn `salary_component_versions` (thêm `effective_from`/`effective_until`, khoá theo `component_code`). Đúng chuẩn nhất, nhất quán với engine họ; đắt nhất.
2. **Đọc lại snapshot khi tính lại kỳ đã Finalize** — biến snapshot từ bằng chứng thành nguồn sự thật. Rẻ hơn, nhưng chỉ đúng cho kỳ đã Finalize, không đúng cho kỳ đang mở.
3. **Chấp nhận + chặn bằng quy trình**: cấm sửa template của kỳ đã chốt, ghi rõ giới hạn. Rẻ nhất, để lại nợ đúng loại nợ mà mục J vừa trả.

### 15.6 Một khả năng mới mà engine của họ mở ra (cần cân nhắc, không phải đề xuất)

Mục B thêm `CONTRACT_TYPE`/`EMP_TYPE`/`IS_FOREIGNER`/`WORK_TYPE` vào tập biến formula, mục A thêm `AND`/`OR` và so sánh chuỗi. Cộng với `LEVEL_NUM` đã có từ trước, engine giờ **đủ sức biểu đạt** để viết trực tiếp `IF([LEVEL_NUM] >= 5, <giá trị>, 0)` ngay trong công thức cột — tức giải được một phần bài toán "cấp bậc nào có phụ cấp nào" mà **không cần template chút nào**.

Cần nói rõ để tránh kết luận sai: cách đó **không thay thế được** template, vì (a) nó phân tán quy tắc cấp bậc vào 110 công thức rời rạc thay vì một chỗ HR quản được, (b) nó không có ngày hiệu lực cho việc gán, (c) mọi thay đổi chính sách cấp bậc thành sửa formula — đúng thứ versioning của mục J phải gánh. Nhưng nó **là** một phương án thật cho các trường hợp đơn giản, và nên được nêu khi trình bày đánh đổi thay vì bỏ qua.

### 15.7 Phân tích sâu 2 phương án mô hình gán (người dùng yêu cầu ở lượt 040826)

Người dùng chưa chốt, yêu cầu phân tích sâu trước. Dưới đây là đối chiếu trên đúng nền engine hiện tại.

**Phương án A — thêm gán theo CẤP BẬC, giữ gán theo nhân viên làm ngoại lệ**

Thêm một bảng `level_payroll_templates` (`level_code` hoặc `employee_level_id`, `template_id`, `effective_from`, `effective_to`). Thứ tự resolve khi tính lương: assignment theo nhân viên thắng trước; không có thì rơi về template của cấp bậc; không có nữa thì tính đủ như cũ (giữ TASK-REF).

- *Chi phí cấu hình*: **29 dòng** thay vì 6.357 dòng gán tay. Đây là chênh lệch quyết định — không phải tiện lợi mà là khả thi hay không.
- *Theo kịp thay đổi nhân sự*: nhân viên được nâng cấp bậc thì cấu trúc lương **tự đổi theo** ở kỳ kế. Với phương án B thì không.
- *Khớp chuẩn ngành*: đúng mô hình Odoo (structure gắn theo hợp đồng/loại) đã dẫn ở mục 3.
- *Chi phí kỹ thuật*: `loadTemplateMaskData` phải nạp thêm một tầng và resolve 2 mức; `tplSig` trong cache key vẫn dùng được nguyên (vẫn là một `templateID` sau khi resolve xong) nên **không phải sửa cache**. Cần thêm test cho thứ tự ưu tiên.
- *Rủi ro thật*: 5.687/12.044 nhân viên (47%) **không có `employee_level_id`**. Với họ, tầng cấp bậc không cho ra gì → rơi về "tính đủ như cũ". Cần chấp nhận tường minh rằng gần một nửa nhân sự không được template chi phối, hoặc phải xử lý riêng.
- *Rủi ro thứ hai*: đây là **thay đổi có sức công phá rộng** — một dòng cấu hình sai ở cấp bậc ảnh hưởng cả trăm người cùng lúc, khác một dòng gán sai chỉ ảnh hưởng một người. Bắt buộc phải có shadow-mode tin được (tức phải sửa 14.6 (3) trước).
- *Ràng buộc nền engine*: bảng mới **không được FK vào `salary_components.id`**, và **phải được tạo trong `RunMigrations()`**, không phải Atlas — theo đúng hai bài học 15.2/15.3.

**Phương án B — giữ khoá theo nhân viên, chỉ thêm công cụ gán hàng loạt**

Không đổi schema. Thêm chức năng "gán template X cho toàn bộ nhân viên cấp bậc Y" sinh ra N dòng `employee_payroll_templates` thật.

- *Ưu*: không đụng schema, không đụng đường resolve, không đụng cache, rủi ro kỹ thuật thấp nhất. Mọi dòng gán đều tường minh và audit được từng người.
- *Nhược quyết định*: liên kết cấp bậc→cấu trúc **không được lưu ở đâu cả** — nó chỉ tồn tại trong đầu người bấm nút. Nhân viên đổi cấp bậc thì assignment **không tự đổi**; phải có người nhớ gán lại. Với 12k nhân sự và luồng HRIS đồng bộ hàng ngày, đây là nợ vận hành tích luỹ, không phải bất tiện một lần.
- *Nhược thứ hai*: 6.357 dòng gán làm bảng phình và mọi lần đổi chính sách cấp bậc thành một lần gán lại hàng loạt, mỗi lần lại sinh thêm 6.357 dòng lịch sử.
- *Nhược thứ ba*: `employee_payroll_templates_emp_from_key UNIQUE (employee_id, effective_from)` sẽ đụng nếu gán hàng loạt hai lần cùng ngày cho cùng người — cần quyết ngữ nghĩa (bỏ qua, ghi đè, hay báo lỗi).

**Nhận định để người dùng chốt**: A giải đúng bài toán tên gọi tính năng đang hứa ("theo cấp bậc") và là thứ duy nhất khả thi ở quy mô 6.357 người, nhưng chỉ an toàn sau khi cổng shadow-mode được sửa cho tin được. B an toàn về kỹ thuật nhưng để lại đúng khoảng trống nghiệp vụ mà mục 14.7 chỉ ra, và đẩy nó thành công việc tay lặp lại vô hạn. Một đường trung gian đáng nêu: **làm B trước như công cụ vận hành, rồi thêm A** — nhưng cần cảnh báo là chính lập luận ở mục 7 ("làm B trước không tiết kiệm gì, chỉ tạo giai đoạn HR dễ tin nhầm") đã từng bác một đường trung gian tương tự; ở đây khác ở chỗ B tạo ra dữ liệu thật dùng được, không phải giai đoạn giả.

### 15.8 Thứ tự ưu tiên sau khi đối chiếu

Việc lấy engine `giatbh` làm nền **đổi hẳn thứ tự ưu tiên** so với mục 14.8. Hai khuyết tật hạ tầng (15.2, 15.3) nhảy lên trước mọi thứ, vì trước khi sửa chúng thì tính năng không tồn tại về mặt thực tế — có cấu hình rồi mất, và ở môi trường sạch thì bảng còn không có. Chỉ sau đó mới đến việc vá lớp an toàn của mask (14.6 (1) và (2)), rồi sửa cổng duyệt (14.6 (3)), rồi mới bàn mở rộng nghiệp vụ.

Quyết định vận hành đã chốt cùng lượt: **bật `PAYROLL_TEMPLATE_ENFORCE=on` ở dev local để kiểm end-to-end**, không đụng staging/production.

## 16. Quy tắc "cột nào được phép mask" — đính chính quy tắc cột-lá và 3 phương án chờ chốt (050826)

Mục này thay thế đề xuất ở PLAN `040826-...-PLAN.md` Task 2 bước 2. Viết sau khi đo trên 126 component
thật của `payroll_engine` ngày 2026-08-05.

### 16.1 Quy tắc "cột lá" đã bị bác bỏ

Tôi từng đề xuất: *"cột nào có cột khác phụ thuộc vào nó thì không được mask; chỉ cột **lá** mới an
toàn"* — lập luận là "mask một cột có người phụ thuộc nghĩa là sửa số của người khác".

Đo thật thì quy tắc đó **chặn đúng những cột mà tính năng tồn tại để mask**:

| Cột | Ai tham chiếu nó | Quy tắc lá |
|---|---|---|
| `PHONE_ALLOW` | `PHONE_TAX`, `PHONE_NONTAX` | chặn ✘ |
| `MEAL_ALLOW` | `MEAL_TAX`, `MEAL_NONTAX` | chặn ✘ |
| `FUEL_ALLOW`, `LIVING_ALLOW`, `OTHER_ALLOW_TAX` | `GROSS` | chặn ✘ |
| `TRANSPORT_ALLOW` | `TRANSPORT_TAX` | chặn ✘ |
| `RESPONSIBILITY_ALLOW` | `CONTRACT_TOTAL`, `RESP_EARNED` | chặn ✘ |
| `HEALTH_INS` | `FAMILY_HEALTH_INS`, `TAXABLE_GROSS`, `TOTAL_SUPPORT` | chặn ✘ |

Chỉ **24/126** mã là lá; trong nhóm phụ cấp thăm dò chỉ `CONS_ALLOW` là lá.

**Sai ở đâu:** mask-về-0 hoạt động **nhờ** đồ thị lan truyền. Mask `PHONE_ALLOW` → `PHONE_TAX` và
`PHONE_NONTAX` tự về 0 → `GROSS` tự tính lại thấp hơn → `PIT` giảm theo. Đó chính là lý do phương án A1
chọn mask thay vì lọc danh sách (mục 7). "Có người phụ thuộc" là **điều kiện để mask có tác dụng**, chứ
không phải dấu hiệu nguy hiểm. Tôi đã đảo ngược chiều của quan hệ.

Ghi lại để người sau không lặp: nếu quy tắc này được thi hành, kết quả sẽ là **test xanh nhưng tính năng
không mask được gì có nghĩa** — loại hỏng khó phát hiện nhất, vì mọi bất biến đều được thoả.

### 16.2 Quy tắc thay thế đã đo: "chỉ mask cột NGUỒN"

**Mask được = cột không tham chiếu cột nào khác** (không có cạnh ra trong đồ thị công thức).

Đo thật: **85 cột nguồn / 41 cột dẫn xuất** (83 nguồn là `input`, 2 là `formula`).

- Tự bảo vệ **toàn bộ 41 cột dẫn xuất**, gồm `GROSS`, `NET_PAY`, `TAXABLE_INC`, `TOTAL_INS`,
  `TOTAL_INS_CTY`, `EARNED_SAL`, `PIT`, `INS_SAL_BH` — **không cần biết tên chúng**, nên HR thêm cột tổng
  mới cũng tự được bảo vệ. Đây là điều mà cả hardcode (v2) lẫn blocklist đều không làm được.
- Cho mask **8/9** phụ cấp thăm dò.

Hai lớp lọc dữ liệu bổ trợ, cũng đã đo:

| Lớp | Loại ra | Lý do |
|---|---|---|
| `format = 'days'` | **26 cột** đếm ngày (`STD_DAYS`, `PAID_LEAVE_DAYS`, `PROB_DAYS`, nhóm `*_CC`…) | mask = làm hỏng dữ liệu chấm công, không phải bỏ một khoản chính sách |
| `source_field <> ''` | **1 cột** (`CONS_ALLOW`) | cột được nạp từ attendance/HRIS |

Sau 3 lớp còn **58 ứng viên**.

### 16.3 Hai ngoại lệ mà quy tắc dữ liệu không xử được

**`BASIC_SAL`** — là nguồn, `source_field` rỗng, `format=currency`, không tham chiếu ai ⇒ **lọt cả 3
lớp**. Nhưng mask nó là thảm hoạ: mọi cột lương đều dẫn xuất từ nó (10 cột tham chiếu trực tiếp).
⇒ **buộc phải có blocklist tường minh**, quy tắc dữ liệu một mình không đủ.

**`MEAL_ALLOW`** — là `formula` tham chiếu `MEALS_TOTAL` ⇒ **bị chặn**, nên template **không thể** bỏ phụ
cấp cơm. Đây là giới hạn thật mà HR sẽ nhận ra. Nguyên nhân: nó là cột **chính sách được biểu đạt bằng
công thức**, không phải cột tổng. Quy tắc "nguồn" không phân biệt được hai thứ đó.

Ngoài ra trong 58 ứng viên còn lại vẫn có thứ **không nên** mask nếu HR tick nhầm: `ADVANCE_1` (tạm ứng —
mask nghĩa là nhân viên nhận tiền đang nợ), `DEPENDENT_CNT` (số người phụ thuộc → sai thuế),
`CHARITY_DED`, và nhóm `*_ADJ` (điều chỉnh bảo hiểm/thuế).

Nhắc lại để định vị mức rủi ro: lớp lọc **thứ nhất** vẫn là `maskableUniverse` (chỉ cột nào có template
liệt kê mới vào diện mask). Nên các cột trên chỉ nguy hiểm khi HR **tick** chúng vào một template — đúng
lỗ L6 (picker không lọc). Quy tắc ở đây là phòng thủ lớp hai, không phải lớp duy nhất.

### 16.4 Ba phương án — CHỜ NGƯỜI DÙNG CHỐT

| | Phương án | Cách làm | Đánh đổi |
|---|---|---|---|
| **A** | Quy tắc dữ liệu + blocklist tối thiểu | 3 lớp (nguồn / `format<>'days'` / `source_field=''`) + blocklist tường minh chỉ `BASIC_SAL` cộng nhóm pháp định hiện có | Rẻ nhất, thi hành ngay. Chấp nhận `ADVANCE_1`, `DEPENDENT_CNT`, `*_ADJ` vẫn mask được nếu bị tick |
| **B** | Quy tắc dữ liệu + blocklist theo nhóm | Như A, cộng blocklist theo **mẫu tên** (`*_ADJ`, `ADVANCE_*`, `DEPENDENT_CNT`, `CHARITY_DED`) | Chặn được nhóm nguy hiểm, và mẫu tên vẫn bắt được mã mới thêm sau. Nhưng mẫu tên là quy ước, không phải hợp đồng — mã mới không theo mẫu sẽ lọt |
| **C** | Đổi sang **cho phép tường minh** (default-deny) | Thêm một cột phân loại trên `salary_components` (ví dụ `is_template_maskable`), mặc định `false`; chỉ cột được C&B đánh dấu mới mask được | An toàn nhất, hết đoán. Nhưng cần migration + phân loại một lần ~58 mã + UI để C&B đánh dấu, và phải tuân G1 (cột trên `salary_components` sẽ bị V4 reseed xoá ⇒ phải tự-hồi hoặc lưu ở bảng khác khoá theo `component_code`) |

Khuyến nghị của tôi: **B**, vì nó giữ được tính chất "HR thêm cột tổng mới cũng tự an toàn" của quy tắc
dữ liệu (điều mà C không có nếu quên đánh dấu), mà vẫn chặn được nhóm nguy hiểm đã biết. Nếu chọn **C**
thì lưu ý ngay: cột phân loại đặt trên `salary_components` sẽ **bị V4 xoá mỗi boot** — phải xử lý như
`component_code` ở Task 0, tức đây không còn là "thêm một cột" mà là một task riêng.

Còn `MEAL_ALLOW` cần quyết riêng: (i) chấp nhận không mask được, ghi vào tài liệu + hiện rõ trên UI Task
3; hay (ii) cho phép mask cột `formula` nếu nó **không** phải cột tổng — nhưng lúc đó phải định nghĩa
"cột tổng" bằng gì, và ta quay lại đúng bài toán ban đầu.

### 16.5 Quyết định chốt (050826) và phép đo đã loại quy tắc nới

**Chốt: phương án A nghiêm, không ngoại lệ.** `maskable` = cột NGUỒN ∧ `format<>'days'` ∧
`source_field=''` ∧ ∉ (pháp định ∪ `BASIC_SAL`) → **đúng 66 mã** trên 140 component hiện tại. Blocklist
tối thiểu; chấp nhận có ý thức rằng `ADVANCE_1`, `DEPENDENT_CNT`, `CHARITY_DED`, nhóm `*_ADJ` vẫn mask
được **nếu HR tick vào template** — hàng rào cho nhóm đó là UI Task 3 (lỗ L6), không phải Task 2.

**`MEAL_ALLOW`: chốt chấp nhận không mask được.** Người dùng ban đầu chọn nới quy tắc ("cho mask cột
`formula` không phải cột tổng"), nhưng phép đo bác bỏ nên đã đổi quyết định. Số đo: quy tắc nới "cột
formula chỉ tham chiếu cột NGUỒN" admit thêm **13 mã**, trong đó chỉ **1** là `MEAL_ALLOW`:

| Mã lọt thêm | Bản chất | Rủi ro |
|---|---|---|
| `BONUS_TOTAL` | tổng **13** cột thưởng | tổng = 0 trong khi từng khoản còn |
| `CONTRACT_TOTAL` | `BASIC_SAL + RESP_SAL` | **cơ sở tính bảo hiểm** (một trong 10 mã lệch ở L12) |
| `TOTAL_SUPPORT`, `TOTAL_POST_ADD` | tổng 5 khoản | cột tổng |
| `PROB_SAL`, `PROB_EARNED`, `EARNED_PAID_LEAVE` | lương thử việc / đã hưởng | **sai lương** |
| `DEPENDENT_DED` | giảm trừ người phụ thuộc | **sai thuế** |
| `PHONE_TAX`, `PHONE_NONTAX`, `TRANSPORT_TAX`, `FAMILY_HEALTH_INS` | phần tách chịu/không chịu thuế | mask phần tách trong khi cột cha còn giá trị → **mâu thuẫn** |

**Lý do gốc quy tắc nới thất bại: độ sâu trong đồ thị không phản ánh "có phải cột tổng".**
`BONUS_TOTAL` tham chiếu 13 cột nguồn — nó là thứ "tổng" nhất có thể mà quy tắc lại cho qua. Ba cột tổng
lớn (`GROSS`, `NET_PAY`, `TAXABLE_INC`) may vẫn bị chặn vì tham chiếu cột dẫn xuất, nhưng đó là **may,
không phải do quy tắc**.

Bản chất vấn đề: `MEAL_ALLOW` là **cột chính sách được biểu đạt bằng công thức**, và **không có thuộc tính
dữ liệu nào hiện có** phân biệt được nó với `BONUS_TOTAL`. Muốn phân biệt đáng tin thì phải đánh dấu tường
minh — đúng phương án **C**, đã bị loại vì cột phân loại trên `salary_components` sẽ bị V4 xoá mỗi boot
(thành một task riêng). Nếu về sau nhu cầu "cột chính sách dạng formula" xuất hiện thêm vài lần nữa, đó
là **tín hiệu nên quay lại C**, đừng chồng thêm ngoại lệ có tên.

### 16.6 Kết quả thi hành Task 2 (050826) — đã xong, kèm 1 phát hiện mới khi thi hành

Thi hành đúng theo PLAN Task 2 trên `Core System-backend@feature_v2` (sau Task 0/1 + bản sửa L12/L13).
Đóng **L5**: `statutoryOverrideBlocklist` giờ khớp mã thật (`PIT`, `SI_EMP`, `HI_EMP`, `UI_EMP` — thay
3 mã chết `BHXH_NV`/`BHYT_NV`/`BHTN_NV`), và guard mask có hàm `maskableCodes()` sống thật thay cho
`component_type == "system"` đã chết.

**Baseline đo lại tại thời điểm này** (không chép "6 case" trong brief): `go test ./...` = **861
passed / 7 failed**, khớp đúng danh sách 7 fail quen thuộc (RBAC gate + report period-id), không dính
test flaky lần đo này.

**Bước 2 — `statutoryOverrideBlocklist`:** xác nhận DB thật (140 component): `PIT` tồn tại, `BHXH_NV`/
`BHYT_NV`/`BHTN_NV` **không tồn tại**. Thay 3 mã chết bằng mã bảo hiểm phía nhân viên thật đang chạy
(`SI_EMP`, `HI_EMP`, `UI_EMP` — đúng vai BHXH/BHYT/BHTN cũ), giữ nguyên `PIT`. Biến này vẫn được dùng
bởi guard scoped-override (`Create`, `SetCell`) — không đổi công dụng đó, chỉ sửa nội dung.

**Bước 3 — `maskableCodes(all []models.SalaryComponent) map[string]bool`:** hàm thuần trong
`payroll_template_mask.go`, đúng quy tắc đã chốt (L1 cột nguồn nghiêm + L2 `format<>days` + L3
`source_field=''` + blocklist ∪ `BASIC_SAL`). Đo thật trên 140 component: **đúng 66 mã** — khớp tuyệt
đối kỳ vọng PLAN, có `PHONE_ALLOW`/`FUEL_ALLOW`/`TRANSPORT_ALLOW`/`LIVING_ALLOW`/`HEALTH_INS`/
`OTHER_ALLOW_TAX`, không có `GROSS`/`NET_PAY`/`TAXABLE_INC`/`TOTAL_INS`/`BASIC_SAL`/`PIT`/
`CONTRACT_TOTAL`/`MEAL_ALLOW`.

**Bước 4 — phát hiện KHÔNG lường trước khi viết brief, đã dừng lại hỏi:** áp thẳng
`!maskable[c.Code]` vào guard của `buildTemplateMaskFormulas` (đúng như PLAN chỉ định) làm **2 test
Task 4 có sẵn vỡ** — `TestTemplateEnforce_DependencyKept` và `...FinalizeSnapshotsTemplateMask`, cùng
kịch bản: template chỉ chọn `MEAL_TAX` (không chọn `MEAL_NONTAX`, dù cả hai là sibling cùng phụ thuộc
`MEAL_ALLOW`). `maskableCodes()` (L1) coi `MEAL_NONTAX` là "dẫn xuất" nên nó không bao giờ được mask
trực tiếp nữa; trong khi `MEAL_ALLOW` phải giữ sống (dep của `MEAL_TAX`, đã chọn), `MEAL_NONTAX` tự
tính lại trên `MEAL_ALLOW` khác 0 → rò giá trị ra ngoài template, đúng loại lỗi mà bảo vệ mask được
dựng để chặn.

Đã thử và **loại cả 3** quy tắc thuần đồ thị để tách "an toàn" (như `MEAL_NONTAX`) khỏi "nguy hiểm"
(như `GROSS`):
1. *Đếm số phụ thuộc trực tiếp (breadth=1 → an toàn)* — `PROB_SAL`/`PHONE_TAX`/`TRANSPORT_TAX`/
   `DEPENDENT_DED` đều breadth=1, và đây **chính xác là 12/13 mã mục 16.5 đã đo và bác bỏ**.
2. *"An toàn nếu phụ thuộc duy nhất cũng maskable"* — `MEAL_ALLOW` **thật** trong production là
   `formula` (không phải `input`), nên bản thân nó không maskable theo L1 → quy tắc này cũng loại
   `MEAL_NONTAX`, không giải quyết được gì.
3. *"Nguy hiểm nếu có thứ NGOÀI universe phụ thuộc vào nó"* — `GROSS` bị `NET_PAY` phụ thuộc (đúng),
   nhưng `MEAL_NONTAX` cũng bị `GROSS` phụ thuộc (cũng ngoài universe) → bị loại nhầm.

**Quyết định (người dùng, 050826):** Phương án B (mục 16.4) — thêm `templateMaskSiblingSplits`, danh
sách **tường minh, nhỏ, khép kín** gồm đúng 6 mã "phần tách chịu thuế/không chịu thuế của một phụ cấp
cha", xác nhận bằng SELECT trực tiếp (không có mã nào khác cùng hình dạng):

```
MEAL_TAX/MEAL_NONTAX ← MEAL_ALLOW; PHONE_TAX/PHONE_NONTAX ← PHONE_ALLOW;
TRANSPORT_TAX ← TRANSPORT_ALLOW + TRIP_OVERRIDE; FAMILY_HEALTH_INS ← HEALTH_INS.
```

Guard cuối trong `buildTemplateMaskFormulas`: `closure[c.Code]` thắng trước tiên; nếu không, mask khi
`maskable[c.Code] || templateMaskSiblingSplits[c.Code]`. `maskableCodes()` **giữ nguyên L1 nghiêm,
không đổi** — vẫn đúng vai trò picker-eligibility cho Task 3 (66 mã không đổi sau khi thêm allowlist,
đã đo lại xác nhận). Đánh đổi có ý thức (đúng bản chất Phương án B): mã "phần tách" mới thêm sau này
có cùng hình dạng phải tự thêm vào danh sách, không tự suy luận bằng heuristic khác.

**Test:** 6 test bắt buộc của PLAN bước 5 đều xanh (`TestMaskable_NeverIncludesDerivedColumns`,
`...AllowsSourceAllowance`, `...IgnoresRuntimeInjectedVars`, `...ExcludesDayColumnsAndSourceField`,
`...BlocklistMatchesRealCodes` — cần DB, `TestMask_NeverMasksAggregateEvenIfTemplateListsIt`), cộng 1
test cũ phải sửa lại cho khớp mã blocklist mới
(`TestBuildTemplateMask_StatutoryAndSystemNeverMaskedEvenIfInUniverse` dùng `BHXH_NV` → đổi sang
`HI_EMP`). **Đã chứng minh `TestMask_NeverMasksAggregateEvenIfTemplateListsIt` bắt được bug thật**:
tạm khôi phục guard cũ (`component_type=="system"`) → test FAIL đúng kỳ vọng (`GROSS` lọt vào mask)
→ khôi phục bản sửa (diff xác nhận y hệt bản gốc) → xanh trở lại. 2 test Task 4 cũ
(`TestTemplateEnforce_DependencyKept`, `...FinalizeSnapshotsTemplateMask`) **xanh trở lại** sau khi
thêm `templateMaskSiblingSplits` — đã xác nhận bằng cách tạm bỏ allowlist đó, thấy 2 test đó vỡ lại
đúng dự đoán, rồi khôi phục.

**Verify cuối:** `gofmt -l` không thêm gì mới ngoài quirk quote pre-existing (không liên quan vùng
sửa); `go build`/`go vet` sạch. `go test ./...` sau sửa: **7 fail**, khớp tuyệt đối baseline — 0 hồi
quy. Đo đối chứng `maskableCodes()` trên DB thật: **đúng 66 mã**, không đổi sau khi thêm
`templateMaskSiblingSplits` (allowlist chỉ tác động `buildTemplateMaskFormulas`, không tác động
`maskableCodes()`).

**Khẳng định không đổi số lương thật:** `PAYROLL_TEMPLATE_ENFORCE` đang tắt (mặc định), và
`buildTemplateMaskFormulas`/`maskableCodes` chỉ được gọi bên trong `if sh.templateEnforce { ... }`
(`payroll_service.go:556`) — xác nhận bằng đọc code, không phải suy đoán. `statutoryOverrideBlocklist`
còn được `SetCell`/`Create` dùng nhưng đó là hành động ghi tay riêng biệt, không nằm trong luồng
`Calculate` bình thường. `payroll_records` thật: **6435 dòng, md5 không đổi** trong suốt phiên (chưa
từng gọi `Calculate` lên dữ liệu thật) — kết hợp với test có sẵn `TestTemplateEnforce_KillSwitchDefaultOff`
(đã xanh) xác nhận PHONE_ALLOW không bị mask khi enforce tắt.

**Nợ có ý thức (ghi để người sau không tưởng là bug):**
1. `ADVANCE_1`, `DEPENDENT_CNT`, `CHARITY_DED`, nhóm `*_ADJ` vẫn mask được nếu HR tick vào template —
   hàng rào là UI Task 3 (đóng L6), không phải Task 2.
2. `MEAL_ALLOW` không mask được (là `formula`, bị L1 chặn) — Task 3 phải hiện disabled kèm lý do,
   không để HR tưởng là lỗi.
3. `templateMaskSiblingSplits` là danh sách tường minh — mã "phần tách" mới có cùng hình dạng (single
   split của 1 cột cha) trong tương lai phải tự thêm tay vào đây.

### 16.6 Kiểm chứng độc lập Task 2 (050826) — ĐẠT, và allowlist sibling ĐÃ ĐÓNG luôn lỗ `MEAL_ALLOW`

Commit `1ede75d`. Kiểm lại bằng lệnh thật.

| Phép đo | Kết quả |
|---|---|
| `statutoryOverrideBlocklist` | `{PIT, SI_EMP, HI_EMP, UI_EMP}` — đã thay 3 mã chết bằng mã bảo hiểm thật, comment ghi rõ lý do ✓ |
| `maskableCodes()` với blocklist mới | **đúng 66 mã** (tự tính lại độc lập) ✓ |
| Tập mask thực tế tại guard | 66 ∪ 6 sibling = **72** |
| 6 test mới | **6/6 PASS** ✓ |
| Full suite | **6 case fail** = đúng baseline RBAC (phiên thi hành báo 7 — chênh 1 là test flaky `...ComputeFormulaImpact...`, không phải hồi quy) |

**Allowlist `templateMaskSiblingSplits` là ĐÚNG, và nó sửa một lo ngại sai của tôi.** Ở mục 16.5 tôi từng
xếp `PHONE_TAX`/`PHONE_NONTAX`/`TRANSPORT_TAX`/`FAMILY_HEALTH_INS` vào nhóm "nguy hiểm — mask phần tách
trong khi cột cha còn giá trị → trạng thái mâu thuẫn". Đo lại công thức thật thì **sai**:

```
GROSS = [EARNED_SAL] + [MEAL_TAX] + [MEAL_NONTAX] + [PHONE_TAX] + [PHONE_NONTAX]
      + [FUEL_ALLOW] + [FUEL_NONTAX] + [TRANSPORT_TAX] + [TRANSPORT_NONTAX] + ...
```

`GROSS` tham chiếu **các cột TÁCH**, **không** tham chiếu cột cha (`MEAL_ALLOW`, `PHONE_ALLOW`). Cột cha
chỉ là bậc trung gian. Nên mask một cột tách **loại đúng phần tiền đó khỏi GROSS** — đó là cơ chế đúng,
không phải mâu thuẫn. Việc cột cha giữ giá trị chỉ "trông lạ" khi xem giá trị trung gian, không ảnh hưởng
tiền.

Kiểm cả 6 mã: **không mã nào là cột tổng**. Mỗi mã tham chiếu đúng cột cha của nó
(`TRANSPORT_TAX` thêm `TRIP_OVERRIDE`), và đích đến là `GROSS`/`TAXABLE_GROSS`/`TOTAL_POST_DED`.

**HỆ QUẢ QUAN TRỌNG — quyết định "chấp nhận không mask được phụ cấp cơm" (16.5) nay ĐÃ LỖI THỜI.**

`MEAL_ALLOW` đi vào `GROSS` **chỉ qua** hai đường `MEAL_TAX` và `MEAL_NONTAX` (đã kiểm: không đường nào
khác). Và hai công thức đó là:

```
MEAL_NONTAX = MIN([MEAL_ALLOW], 730000)
MEAL_TAX    = MAX(0, [MEAL_ALLOW] - 730000)
```

Với mọi `x ≥ 0`: `MIN(x, 730000) + MAX(0, x − 730000) = x` **chính xác**. Nên mask **cả hai** cột tách sẽ
**gỡ trọn vẹn phụ cấp cơm khỏi `GROSS`** — không xấp xỉ, không sót đồng nào. Cả hai đều nằm trong
allowlist 6 mã.

⇒ **Template BỎ ĐƯỢC phụ cấp cơm**, chỉ là bỏ qua hai cột tách chứ không qua `MEAL_ALLOW`. Điều tương tự
đúng với điện thoại (`PHONE_TAX`/`PHONE_NONTAX`), dù ở đó còn đường trực tiếp vì `PHONE_ALLOW` là cột
nguồn nên tự maskable.

**Việc phải làm ở Task 3 (đổi so với kế hoạch cũ):** trước đây định hiện `MEAL_ALLOW` dạng disabled kèm lý
do *"không bỏ được phụ cấp cơm"* — **câu đó nay SAI, đừng hiện**. UI phải cho HR thấy đường đúng: muốn bỏ
phụ cấp cơm thì không đưa `MEAL_TAX`/`MEAL_NONTAX` vào cấu trúc. Tức UI cần giải thích **quan hệ cha–tách**,
không chỉ liệt kê cột phẳng — nếu không HR sẽ tick `MEAL_ALLOW` (không có tác dụng vì nó không maskable)
rồi kết luận tính năng hỏng.

## 17. Kết quả thi hành Task 4 (050826) — đóng cổng duyệt luôn báo "không có tác động"

Thi hành đúng theo PLAN Task 4 (bản mở rộng 2 lỗ) trên `Core System-backend@feature_v2`, sau Task 0/1/2 +
bản sửa L12/L13. Đóng **L7**: `ComputeTemplateImpact` — cổng duyệt shadow-mode duy nhất trước khi bật
`PAYROLL_TEMPLATE_ENFORCE` — trước đây **luôn** báo "không có tác động" vì **HAI lỗ**, không phải một.

**Xác nhận trước khi sửa** (đọc trực tiếp code, không chép brief): cả 4 vị trí brief nêu đều khớp chính
xác — `salaryOverrides: map[string]float64{}` ở 2 dòng dựng `calcShared` (`shOff`/`shOn`), và
`computeEmployee(shOff/shOn, emp, att, nil)` ở 2 lời gọi tính toán. `ErrFormulaImpactNoSalaries` (khuôn
mẫu) và guard `len(in.Salaries)==0` đúng vị trí brief mô tả. `ManualInputRepo.ToMap` trả
`map[uuid.UUID]map[string]float64` (khớp Bẫy 2 — key là `emp.ID`, không phải `empCode`).

**Baseline đo lại**: `go test ./...` = **867 passed / 7 failed**, khớp đúng danh sách quen thuộc (không
dính test flaky lần đo này).

**Lỗ 1 — `salaryOverrides` rỗng ở cả 2 lần mô phỏng:** sửa bằng truyền `salaries` (tham số mới của
`ComputeTemplateImpact`) vào cả `shOff` lẫn `shOn`. Thêm sentinel `ErrTemplateImpactNoSalaries` + guard
`len(salaries)==0` ở đầu hàm — đúng khuôn `ErrFormulaImpactNoSalaries`.

**Lỗ 2 — `empManual` truyền `nil`, lỗ chí tử chỉ lộ ra SAU Task 2:** sau Task 2, tập mask là 66 mã cột
NGUỒN có `source_field=''` — nghĩa là giá trị của chúng đến từ `payroll_manual_inputs`, KHÔNG từ
attendance. `nil` khiến toàn bộ 66 mã đó = 0 ở CẢ HAI lần mô phỏng, delta triệt tiêu **tuyệt đối** dù đã
sửa lỗ 1. Sửa bằng nạp `manualInputRepo.GetByPeriod` + `ToMap` đúng khuôn `Calculate:253-254`, rồi
`manualMap[emp.ID]` cho từng NV, truyền vào cả 2 lời gọi `computeEmployee` (thay `nil`), guard
`s.manualInputRepo != nil` (Bẫy 3).

**Route + handler:** đổi `GET`→`POST` (`router.go`), giữ nguyên bộ gate
(`requirePayrollCalculate, companyReadScope, requireView`). Handler chép đúng khuôn
`payroll_formula_impact_handler.go`: body `salaries[]` dạng mảng → đổi sang map, sentinel → 422, lỗi
khác → 400.

**Test — đúng phần khó nhất, và brief cũ đã sai ở đây:**
- `TestComputeTemplateImpact_RejectsWithoutSalaries` — khẳng định trả lỗi, không trả báo cáo rỗng.
- `TestComputeTemplateImpact_DetectsAllowanceMaskDelta` — **PHẢI neo vào một phụ cấp bị mask**, KHÔNG
  neo `BASIC_SAL` (blocklist, không bao giờ mask — test đó sẽ xanh giả ngay khi sửa xong lỗ 1). Brief
  gốc đề xuất `PHONE_ALLOW` làm ví dụ — **đã xác nhận sai khi đọc code**: `PHONE_ALLOW` lấy giá trị từ
  `att.PhoneAllowance` (hardcode trong `buildInputValues`), KHÔNG qua manual input. Đổi sang `ADJ_PLUS`
  (input, không `source_field`, không hardcode trong `buildInputValues` — grep xác nhận 0 hit, và nằm
  trực tiếp trong công thức `GROSS`). **Phát hiện phụ khi viết test:** template được gán cho NV nếu có
  **0 component** thì `buildTemplateMaskFormulas` trả `nil` sớm (coi như "chưa gán gì", đúng thiết kế
  TASK-REF, không phải bug) — phải cho template được gán có ít nhất 1 mã thật (nhóm ăn ca) để không rơi
  vào nhánh đó, `ADJ_PLUS` đặt ở template khác (không gán ai) chỉ để đưa vào universe.
  Số đo thật: `ADJ_PLUS` nạp `300000` qua manual input → `report.ByComponent` có dòng `ADJ_PLUS` với
  `Delta = -300000` (đúng bằng giá trị đã nạp). Thêm khẳng định magnitude `GrossBefore ≥ 10.000.000` để
  bắt riêng lỗ 1 (nếu `salaryOverrides` rỗng, `GrossBefore` sẽ chỉ còn `300000` — đúng bằng phần
  `ADJ_PLUS`, thiếu hẳn phần lương cơ bản).
- **Đã chứng minh test bắt được CẢ HAI lỗ bằng revert-và-khôi-phục** (không chỉ tin nó xanh):
  - Revert riêng lỗ 2 (`empManual` về `nil`) → `EmployeesAffected phải > 0` FAIL đúng kỳ vọng.
  - Revert riêng lỗ 1 (`salaryOverrides` về map rỗng) → `GrossBefore quá nhỏ (300000)` FAIL đúng kỳ vọng.
  - Cả hai lần khôi phục: diff y hệt bản gốc, xanh trở lại.
- Khẳng định không ghi `payroll_records`: đếm + md5 `computed_values` y nguyên trước/sau (khuôn 280726).
- `TestIntegrationPayrollTemplateImpactRouteEnforcesPermission` đổi `GET`→`POST`, giữ nguyên bảng role
  (6/6 pass).

`go test ./...` sau sửa: **7 fail**, khớp tuyệt đối baseline — 0 hồi quy.

**Nghiệm thu bằng request thật** (`go run ./cmd/Core System`): `POST` body `{}` → **422**; `POST` với
`salaries` hợp lệ → **200**, JSON hợp lệ (`employeesAffected=0` cho kỳ thật gần nhất — đúng thực tế vì
chưa có NV nào gán template thật, Task 3/5 chưa làm, không phải bug); `GET` cũ → **405** (route đã đổi
hẳn sang POST, không còn tồn tại dưới GET). `payroll_records`: **6435 dòng, md5 không đổi**
(`f780dec3bdc411c0c5e1b28cb338d565`) trước/sau toàn bộ request thật.

**Nợ có ý thức (ghi để người sau không tưởng là bug):** `ComputeFormulaImpact` (`:1016`, `:1020`) vẫn
truyền `empManual = nil` — cùng họ lỗi với lỗ 2 vừa sửa, nhưng **cố ý KHÔNG sửa kèm** (ngoài phạm vi
Task 4, và nó có test riêng đang xanh nên đổi sẽ phải đo lại baseline của chính nó). Hệ quả: ước lượng
tác động công thức (`FormulaImpact`, Task 6 cũ) vẫn thiếu đóng góp của công thức phụ thuộc phụ cấp nhập
tay qua manual input.

## 17. Kiểm chứng độc lập Task 4 (050826) — ĐẠT, kèm ĐÍNH CHÍNH phân tích của tôi

Commit `65fed61`. Kiểm lại bằng lệnh thật.

| Phép đo | Kết quả |
|---|---|
| Lỗ 1 — `salaryOverrides` | đã truyền `salaries` thật; sentinel `ErrTemplateImpactNoSalaries` (`payroll_service.go:749`), guard ở `:766` ✓ |
| Lỗ 2 — `empManual` | `computeEmployee` ở `:854`/`:855` nay nhận `empManual` thật (trước là `nil`) ✓ |
| Nợ giữ đúng chủ đích | `ComputeFormulaImpact` **vẫn** `nil` ở `:1046`/`:1050` — không sửa kèm, đúng ràng buộc ✓ |
| Route | `POST /template-impact/{periodId}` (`router.go:459`), giữ nguyên bộ gate ✓ |
| Test | 3/3 PASS, gồm `TestComputeTemplateImpact_DetectsAllowanceMaskDelta` |
| Full suite | **6 case fail** = baseline RBAC (phiên thi hành báo 7 — chênh 1 là test flaky) |

### 17.1 ĐÍNH CHÍNH: brief của tôi chọn sai mã ví dụ, và khẳng định "delta = 0 tuyệt đối" là NÓI QUÁ

Brief tôi viết yêu cầu test neo vào `PHONE_ALLOW` với lý do "nạp qua `payroll_manual_inputs`". **Sai.**
Phiên thi hành phát hiện và đổi sang `ADJ_PLUS` — đúng.

Nguyên nhân: `buildInputValues` (`payroll_service.go`) **hardcode 41 mã** lấy thẳng từ
`attendance_summary`/`employees`, **không qua `source_field`, không qua manual input** — trong đó có
`PHONE_ALLOW` (= `att.PhoneAllowance`), `FUEL_ALLOW`, `LIVING_ALLOW`, `OTHER_ALLOW_TAX`,
`TRANSPORT_ALLOW`, `TRIP_OVERRIDE`, `MEALS_BASE/OT/TOTAL`, `RESP_SAL`, `DEPENDENT_CNT`.

Nghĩa là **có BA nguồn giá trị cho cột `input`**, không phải hai như tôi mô tả:
1. `source_field <> ''` → `resolveSourceField(...)`
2. **hardcode trong `buildInputValues`** ← tôi đã bỏ sót nguồn này
3. `payroll_manual_inputs` → `empManual`

Đo lại 66 mã maskable theo nguồn giá trị:

| Nguồn | Số mã | Báo cáo CŨ (trước Task 4) |
|---|---|---|
| (A) hardcode từ `attendance_summary` | **11** | **vẫn thấy delta** — vì `att` luôn được truyền, kể cả trước khi sửa |
| (B) `payroll_manual_inputs` | **55** | **mù hoàn toàn** — `empManual = nil` nên giá trị = 0 ở cả hai lần |

⇒ Phát biểu đúng phải là: cổng duyệt cũ **mù với 55/66 mã maskable (83%)** và **báo sai số tuyệt đối cho
mọi cột dẫn xuất lương** (vì `BASIC_SAL = 0`), **chứ không phải "luôn báo không có tác động"**. Với 11 mã
nhóm (A) nó vẫn hiện delta. Câu "delta triệt tiêu" trong comment gốc của repo (`payroll_service.go` bản
cũ) và trong mục 14.6(3) của tài liệu này **đều nói quá** — mức độ hỏng thật là *mù phần lớn* + *sai thang
đo*, vẫn đủ nghiêm trọng để chặn việc bật enforce, nhưng cần phát biểu chính xác.

**Vì sao việc chọn sai mã ví dụ là nguy hiểm, không chỉ là chi tiết:** `PHONE_ALLOW` thuộc nhóm (A), nên
một test neo vào nó **sẽ XANH ngay khi chỉ sửa lỗ 1** — đúng cái bẫy "cảm giác an toàn giả" mà brief của
tôi được viết để tránh, và tôi lại tự cài vào chính brief đó. `ADJ_PLUS` thuộc nhóm (B) nên test chỉ xanh
khi **cả hai** lỗ được sửa; phiên thi hành đã chứng minh điều đó bằng revert-và-khôi-phục riêng từng lỗ.

### 17.2 Ghi chú phụ (không phải bug)

Template có **0 component** làm `buildTemplateMaskFormulas` trả `nil` sớm (guard
`len(templateCodes) == 0`). Đúng thiết kế TASK-REF ("chưa gán/chưa cấu hình → tính đủ như cũ"), không phải
khuyết tật. Nhưng nó có nghĩa: khi dựng fixture test hoặc khi C&B thử nghiệm, **template rỗng sẽ không
mask gì cả** — dễ bị đọc thành "tính năng không chạy". Task 3 nên hiện rõ số cột của template để không ai
nhầm.

## 18. Kết quả thi hành Task 3 (050826) — làm trực tiếp trong phiên phân tích, đã kiểm tay trình duyệt

Khác các task trước (dispatch cho phiên Sonnet riêng rồi kiểm chứng độc lập), Task 3 được thi hành
**ngay trong phiên đang phân tích/lên kế hoạch**, theo yêu cầu người dùng "làm rồi nghiệm thu — test
giao diện 1 lần, quay lại sửa nếu cần". Ghi lại đủ vì đây là cách làm khác các mục trước.

**Backend** (`internal/models/Core System.go`, `internal/service/payroll_template_mask.go`,
`internal/service/salary_component_service.go`, test mới
`internal/service/payroll_template_mask_eligible_test.go`):
- `templateMaskEligible` = `maskableCodes()` ∪ `templateMaskSiblingSplits` — một nguồn sự thật cho cả
  guard runtime lẫn API, đúng thiết kế đã chốt.
- `templateMaskReason` — quy tắc 5 nhánh, đo trực tiếp qua request thật (xem dưới).
- `SalaryComponent.Maskable`/`MaskReason` (`db:"-"`) điền ở `SalaryComponentService.List`.
- **Đo thật trên DB (140 component)**: `templateMaskEligible` trả **đúng 72** — khớp tuyệt đối `66 ∪ 6`
  đã tính trước. Danh sách bắt buộc (`PHONE_ALLOW`, `FUEL_ALLOW`, `HEALTH_INS`, `MEAL_TAX`,
  `MEAL_NONTAX`) đều `true`; danh sách cấm (`GROSS`, `NET_PAY`, `TAXABLE_INC`, `BASIC_SAL`, `PIT`,
  `CONTRACT_TOTAL`) đều `false`.
- **Nghiệm thu bằng request thật** (`curl` qua dev bypass): `GET /config/salary-components` trả đủ
  `maskable`/`maskReason` cho 140 dòng; `MEAL_ALLOW.maskReason` =
  *"Không chọn trực tiếp được — điều khiển qua MEAL_NONTAX, MEAL_TAX trong cấu trúc lương."* — đúng yêu
  cầu, không có câu "không bỏ được".
- `go test ./...`: **6 fail** = baseline, không hồi quy. `gofmt`/`go vet` sạch.

**Frontend** (`lib/template-picker.ts` + test, `lib/api/types.ts`,
`components-page/tinh-luong/PayrollTemplateModal.tsx`):
- `isMaskable`/`nonMaskableSelectedCodes` tách thuần, 6 test vitest xanh.
- Picker: checkbox `disabled` khi `maskable===false`, mờ (`opacity 0.5`), `title`=lý do, lý do hiện
  dưới tên cột; banner cảnh báo dữ liệu cũ (mã đã chọn nay không còn maskable) — không tự bỏ chọn.
- `pnpm lint`: 0 error. `pnpm test`: 6/6 xanh.

**Kiểm tay trình duyệt — bắt buộc theo brief, đã làm bằng Playwright + Chromium (cài tạm trong phiên,
đã gỡ lại sau khi xong) qua cơ chế dev-login có sẵn (`e2e/devLogin.ts`, header `Authorization: Bearer
dev`), không phải browser tool có sẵn của agent:**
- Luồng thật: tab "Công thức" → sheet "Danh sách cột lương" tự mở → nút "Cấu trúc lương theo cấp bậc"
  → "+ Tạo cấu trúc mới" → picker hiện đúng 140 dòng.
- `STD_DAYS`/`PROB_DAYS`/`OFFICIAL_DAYS` (format=days): disabled, lý do "Cột đếm ngày...".
- `GROSS`: disabled, lý do "Cột tổng/dẫn xuất — giá trị tính từ các cột khác, không thể mask riêng."
  **Click thật vào checkbox đã disable — trạng thái không đổi** (`false → false`), xác nhận `disabled`
  hoạt động ở tầng DOM thật, không chỉ ở style.
- `MEAL_ALLOW`: disabled, lý do đúng câu chỉ đường qua `MEAL_NONTAX, MEAL_TAX`. `MEAL_TAX` bên cạnh:
  **enabled** — đúng thiết kế cha–tách.
- `PHONE_ALLOW`: enabled. **Click thật → tick được** (`false → true`), bộ đếm "(1 đã chọn)" cập nhật
  đúng ngay lập tức.
- **Không có gì bị lưu vào DB** trong lúc kiểm (không bấm "Lưu"): `select count(*) from
  template_components` vẫn = 0 sau khi đóng trình duyệt.

**Dọn dẹp sau kiểm tay (đúng ràng buộc "không phình phạm vi"):**
- Trả `SALARY_STRUCTURE_FEATURE_VISIBLE` về `false` (chỉ tạm `true` lúc kiểm).
- Gỡ `playwright` khỏi `package.json`/`pnpm-lock.yaml` (không phải phần việc của Task 3, chỉ là công cụ
  kiểm tạm thời) và `pnpm install` lại cho khớp lockfile gốc.
- Xoá 2 script Playwright tạm (`check-task3.mjs`, `check-task3b.mjs`).

**Phát hiện phụ, không phải bug:** `pnpm add playwright` từng làm `node_modules` vỡ (thiếu
`picocolors`, gây `next dev` lỗi 500 toàn trang) — `pnpm install` lại đã tự phục hồi. Không liên quan
code Task 3, chỉ là hệ quả cài package tạm.

**Đã commit** (2026-08-06, sau khi kiểm chứng độc lập trong phiên): `Core System-backend@fed1568`,
`Core System-frontend@52b1076`, cả hai trên `feature_v2`. **Chưa push.**

## 19. Kết quả thi hành Task 5 (060826) — dọn dữ liệu demo, bật enforce dev local, nghiệm thu end-to-end

Thi hành theo `self-docs/files/prompt-Task5-060826.md`, đúng thứ tự Bước 1→5 của PLAN. **Bắt được 2
chỗ brief mô tả sai/thiếu so với code thật khi chạy — cả hai đã tự sửa, không hỏi lại vì không phải
quyết định thiết kế mở, chỉ là lệch mô tả kỹ thuật:**

1. **Body `POST /Core System/template-impact/{periodId}` — brief ghi `salaries` là OBJECT
   (`{"<mã_NV>": <lương>}`), code thật (`payroll_template_impact_handler.go:29-34`) đòi MẢNG
   `[{"empCode":"...","basicSalary":...}]`. Gửi theo brief → 400 "invalid request body". Sửa bằng đọc
   handler trước khi retry, không đoán.
2. **Phát hiện quan trọng hơn — hiểu sai cơ chế "universe" khi dựng fixture lần đầu.** Bước 3.2 của
   brief bảo gán CẢ 4 cột `PHONE_ALLOW/FUEL_ALLOW/MEAL_TAX/MEAL_NONTAX` vào MỘT template rồi gán cho
   1 NV, kỳ vọng thấy mask — **SAI, đã tự thử và xác nhận bằng số**: đưa cột NÀO vào template của
   chính NV đó thì cột đó nằm trong *closure* (phần được GIỮ), không bị mask; kết quả thật lần thử
   đầu: `template-impact` trả `employeesAffected:0`, `Calculate` cho NV đó ra `MEAL_TAX=170000`/
   `MEAL_NONTAX=730000` — không đổi gì. Đọc lại `buildTemplateMaskFormulas` (`payroll_template_mask.go:55-95`)
   mới thấy đúng: `maskableUniverse` (tham số `tplUniverse`, dựng bởi `buildTemplateUniverse` từ
   `ListAllTemplateComponentCodes()` — **union CODE của MỌI template đang tồn tại trong DB**, không
   riêng của NV) là tập cột "được phép xét mask"; một cột chỉ MASK cho một NV khi nó **có trong universe
   NHƯNG KHÔNG có trong closure của template NV đó gán**. Nếu chỉ có DUY NHẤT 1 template trong DB và nó
   chứa đúng 4 cột muốn mask, thì cả 4 cột đó tự đưa mình vào closure của chính NV được gán — không có
   cột nào "trong universe mà ngoài closure" để mask. **Sửa đúng bằng 2 template**: `T1` (gán cho NV,
   chỉ gồm `PHONE_ALLOW`+`FUEL_ALLOW`) và `T2` (KHÔNG gán ai, chỉ gồm `MEAL_TAX`+`MEAL_NONTAX` — mục
   đích DUY NHẤT là đưa 2 mã này vào universe toàn cục) — khớp đúng khuôn test đơn vị có sẵn
   `TestTemplateEnforce_MaskedColumnIsZero` (dùng tham số `maskableUniverse` tường minh gồm cả nhóm
   KHÔNG thuộc template của NV, comment "Universe (nhiều grade khác gộp lại) còn có nhóm điện thoại").
   Bài học cho phiên sau: **1 template test không đủ để chứng minh mask có tác dụng** — luôn cần ≥2
   template trong DB tại thời điểm test (hoặc dữ liệu demo/thật đã có sẵn từ trước).

### 19.1 Số đo thật (kỳ cách ly `2099-01`, 2 nhân viên MƯỢN thật `101404`/`100600` — chỉ đọc thông tin
định danh, KHÔNG sửa bảng `employees`; mọi bản ghi lương/gán template đều nằm trong `period_id`/`id`
mới tạo, xoá sạch sau khi xong)

**Lệch có ghi nhận khỏi brief:** brief đề nghị "tạo 1 employee test mới" — không làm theo, vì khuôn
test tích hợp thật của repo (`TestTemplateEnforce_CalculateOneMatchesCalculateAndPointInTime:319-324`)
chủ động MƯỢN 1 nhân viên có sẵn (`SELECT * FROM employees LIMIT 1`) để tránh đúng rủi ro brief cảnh
báo ("không rõ hết trường NOT NULL/FK") — cách ly vẫn giữ nguyên vì mọi ghi/xoá đều theo `period_id`
kỳ 2099 (chưa ai dùng), không đụng `payroll_records` của bất kỳ kỳ thật nào của 2 nhân viên này.

- Trước khi bắt đầu: `payroll_records` mọi kỳ THẬT (loại kỳ `year=2099`) — **6435 dòng**, md5
  `202a20ec949db110efa1d304b456f6b7` (khớp đúng giá trị đã ghi nhận ở các phiên trước).
- `curl .../config/salary-components` xác nhận `maskable:true` cho cả 4 mã trước khi chọn:
  `PHONE_ALLOW`, `FUEL_ALLOW`, `MEAL_TAX`, `MEAL_NONTAX`.
- `template_components` (4 dòng gộp cả 2 template) **sống nguyên qua 1 lần restart backend thật**
  (`AUTO_MIGRATE=false go run ./cmd/Core System`) — nghiệm thu Task 0 (RE-LINK theo `component_code`) ở
  tầng thật, không chỉ ở test.
- `GET /Core System/template-enforce-status` sau khi thêm `PAYROLL_TEMPLATE_ENFORCE=on` vào `.env` +
  restart: `{"enabled":true,"healthy":true}`.
- `POST /Core System/template-impact/2099-01` (body mảng, salary giả `101404→20tr`, `100600→18tr`):
  `employeesAffected:1`, `totalGrossDelta:-900000`, `byComponent` gồm `MEAL_TAX:-170000`,
  `MEAL_NONTAX:-730000`, `GROSS:-900000`, `NET_PAY:-891500`, `PIT:-8500`… — **khác 0**, xác nhận Task 4
  (sửa lỗ `salaryOverrides`/`empManual`) không hồi quy.
- `POST /Core System/calculate/2099-01` (2 NV, kỳ cách ly): NV `101404` (được gán `T1`) →
  `MEAL_ALLOW=900000` (input thô, không bị mask vì không nằm trong closure lẫn universe theo hướng
  ngược — chỉ 2 cột TÁCH bị mask), `MEAL_TAX=0`, `MEAL_NONTAX=0`, `GROSS=20000000` (đúng bằng
  `BASIC_SAL`, vì mọi cột khác = 0 với NV test tối giản này). NV `100600` (KHÔNG gán template nào) →
  `MEAL_TAX=170000`, `MEAL_NONTAX=730000`, `GROSS=18900000` — **y nguyên như enforce OFF** (TASK-REF),
  dù enforce đang bật toàn cục — đây chính là bằng chứng bước 9 (đối chứng NV không gán), không cần
  dựng thêm NV thứ ba.
- `POST /Core System/calculate-one/2099-01` cho `101404`: `MEAL_TAX=0`, `MEAL_NONTAX=0`, `GROSS=20000000`,
  `NET_PAY=17680000`, `PIT=120000` — **khớp tuyệt đối** với `Calculate` ở trên (TASK-REF, 2 đường tính
  không lệch nhau).
- `POST /Core System/finalize/2099-01`: `payroll_formula_snapshots WHERE period_id=<kỳ test> AND
  scope_type='template'` → đúng 2 dòng, `component_code` = `MEAL_TAX`, `MEAL_NONTAX` — khớp tuyệt đối
  tập cột đã mask ở bước `Calculate`.
- Sau khi xoá sạch dữ liệu test (period/attendance/2 template/assignment/payroll_records/snapshot kỳ
  2099): `payroll_records` mọi kỳ THẬT — **6435 dòng, md5 `202a20ec949db110efa1d304b456f6b7`** —
  **y nguyên tuyệt đối** so với số đo trước khi bắt đầu.

### 19.2 Trạng thái cuối

`Core System-backend/.env` có `PAYROLL_TEMPLATE_ENFORCE=on` (file không commit, xác nhận qua `git
check-ignore .env` trước khi sửa) — **enforce đang BẬT ở máy dev này**, đúng định nghĩa-xong của Task
5. `payroll_templates`/`employee_payroll_templates` trong `payroll_engine` hiện **0 dòng** (đã xoá dữ
liệu demo "demo 1"/THAIDT001 ở Bước 1, theo quyết định người dùng đã chốt 060826) — enforce bật nhưng
chưa ai được gán, nên chưa ảnh hưởng lương thật của ai cho tới khi có gán mới qua UI (Task 6, đang
HOLD).
