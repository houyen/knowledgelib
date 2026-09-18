---
id: self-docs/engine/pit-formula-fix
canonical_question: 'Technical guide and specification: PIT  luôn = 0 — nguyên nhân,
  sửa, và bậc thuế mới theo HR'
aliases:
- PIT  luôn = 0 — nguyên nhân, sửa, và bậc thuế mới theo HR
- PIT Formula Fix 270726
entity_type: how_to
domain: self-docs > engine
last_verified: 2026-09-17
---

# PIT (thuế TNCN) luôn = 0 — nguyên nhân, sửa, và bậc thuế mới theo HR (270726)

## 1. Bối cảnh phát hiện

Phát hiện khi viết bộ test khoá bất biến cho tính năng "cấu trúc lương theo cấp bậc" (xem
`Salary-Structure-Template-Analysis-260726.md` — mục 4, Task 4.6). Đây là **2 việc hoàn toàn độc
lập**: mask-về-0 không gây ra bug này, và bug này không liên quan gì tới template — chỉ tình cờ
được phát hiện cùng lúc vì cùng chạm vào `internal/service/payroll_service.go`/`engine.go`.

## 2. Bug — PIT luôn tính ra 0, toàn bộ hệ thống, mọi kỳ

**Chuỗi nguyên nhân đã verify bằng code + dữ liệu thật:**

1. `internal/service/engine.go` — component `PIT` (`component_type='system'`) được tính qua
   `evalSystemComponent`, gọi `filterActivePITBrackets(pitBrackets, inputs.PeriodEnd)` rồi
   `calculateProgressivePIT`.
2. `CalculateInputs.PeriodStart`/`PeriodEnd` **chưa từng được gán** ở bất kỳ đâu trong
   `Calculate`/`CalculateOne`/`computeEmployee` (`internal/service/payroll_service.go`) — xác nhận
   bằng `grep -rn "PeriodStart:\|PeriodEnd:" internal/ --include="*.go" | grep -v _test.go` → 0 kết
   quả. Luôn là `time.Time` zero-value (`0001-01-01`).
3. Bảng `pit_brackets` thật trong DB có `effective_from = 2009-01-01` cho cả 7 bậc (không phải
   zero-value). `filterActivePITBrackets` tìm `effective_from` lớn nhất `<= refDate` — với
   `refDate` = zero-value, **không bậc nào thoả điều kiện** → trả về danh sách rỗng.
4. `calculateProgressivePIT(income, [])` → trả về 0 ngay từ dòng đầu (`len(brackets) == 0`).

**Xác nhận thực nghiệm** (viết 1 test tạm gọi thẳng các hàm nội bộ, đã xoá sau khi xem kết quả):
`filterActivePITBrackets(7 bracket thật, refDate=zero-value)` → 0 bracket còn lại;
`calculateProgressivePIT(20.000.000, 0 bracket)` → 0; cùng input với `refDate` = ngày thật → 7
bracket, PIT = 2.350.000.

**Xác nhận bằng dữ liệu production thật:**
```sql
SELECT count(*) FILTER (WHERE (computed_values->>'PIT')::numeric > 0), count(*)
FROM payroll_records WHERE computed_values ? 'PIT';
-- 0 / 6435
```
Kể cả dòng có `TAXABLE_INC = 20.225.000` (gấp 4 lần bậc thuế đầu 5.000.000) thì `PIT = 0`.
`PIT_ADJ` (cột điều chỉnh tay) cũng 0/6435 — không phải HR đang bù thủ công qua cột điều chỉnh.

**Đã loại trừ (không phải nguyên nhân):** `PIT.formula` rỗng trong DB — switch trong `engine.go`
gọi `evalSystemComponent` **vô điều kiện** cho `component_type="system"`, không đọc `Formula`.

**Không phải hồi quy:** đoạn code lỗi nằm nguyên văn trong commit đầu tiên của repo (`47753b4`
"INIT backend", 2026-05-19). Cả đời repo chỉ 4 commit chạm `engine.go`, không commit nào của các
đợt gần đây. Bug này có sẵn từ ngày đầu, không phải do việc nào đang làm gần đây gây ra.

**Vì sao 2 tháng không ai thấy:** `defaultPITBrackets()` (fallback khi bảng `pit_brackets` rỗng)
KHÔNG set `EffectiveFrom` (zero-value) — với bộ fallback này, `ef=zero, ref=zero` khớp nhau, PIT
tính đúng bằng may mắn. Bug chỉ lộ khi DB có bracket thật (đã có từ 2026-04-14). Không có test nào
cho nhánh PIT trước đây (`grep "PITBracket{" internal/service/*_test.go` → 0 kết quả).

## 3. Quyết định thiết kế — chuyển PIT sang `component_type='formula'`

Thay vì chỉ sửa lỗi gán `PeriodStart`/`PeriodEnd` (phương án tối thiểu, TASK-REF, đã trình bày ban đầu),
người quyết định dự án chọn **đổi kiến trúc**: chuyển PIT từ `system` (logic Go hardcode trong
`evalSystemComponent`) sang `formula` (công thức cấu hình được, chạy qua engine chuẩn như 40 cột
formula khác). Lý do người dùng nêu: "PIT cũng sẽ là 1 loại rule công thức" — nhất quán với hướng
đi chung của hệ thống, dễ chỉnh sửa qua UI thay vì phải sửa code Go.

### 3.1. Xác nhận engine đủ khả năng biểu diễn công thức thuế lũy tiến

Verify trước khi viết (không suy đoán):
- `IFS(cond1,val1, cond2,val2, ...)` có sẵn (`engine.go`), trả giá trị của cặp điều kiện đầu tiên
  đúng — đủ để mã hoá thuế lũy tiến kiểu "rút gọn" (`rate·x − hằng_số`).
- `MAX`/`MIN` nhận **≥ 2 tham số** (không giới hạn 2) — đủ cho `MAX` của 5 nhánh bậc thuế.
- `ROUND(value, decimals)` có sẵn.
- Toán tử so sánh `<=`, `>=`, `<`, `>`, `==`, `!=` trả về `1`/`0` — khớp đúng cách `IFS`/điều kiện
  logic đọc giá trị.
- Thứ tự ưu tiên toán tử: `comparison() → expr(+/-) → term(*/) → unary → atom` — `*` chạy trước `-`
  đúng chuẩn, không cần thêm ngoặc.
- **Không hỗ trợ:** literal boolean trần (`TRUE`/`FALSE` không có `(` theo sau → lỗi cú pháp — parser
  chỉ nhận diện 1 từ liền sau là TÊN HÀM, bắt buộc có `(`); so sánh chuỗi (`[CODE]="text"` bị chặn
  tường minh: `"string operand is not allowed for comparison operator"`).

### 3.2. Dữ liệu HR cung cấp có 3 nhánh — chỉ làm nhánh chính thức đợt này

Công thức HR gửi có 3 nhánh: expat không work permit (20% flat), intern (10% flat nếu >5tr, có cam
kết thuế thì 0), và "chính thức" (lũy tiến qua `ROUND(MAX(...), 0)`). Xác nhận qua code:
- **2 nhánh đầu KHÔNG viết được** ngay với engine hiện tại (dùng `=TRUE` và so sánh chuỗi, cả 2 đều
  bị chặn — xem mục 3.1).
- **3 field điều kiện** (`IS_EXPAT_NO_WP`, `EMP_TYPE`, `HAS_TAX_COMMITMENT`) **không tồn tại ở đâu**
  trong schema — grep 0 kết quả trong `internal/models`+`internal/service`, query `salary_components`
  0 kết quả. Field gần nhất, `employees.employee_type_name`, có giá trị thật `full_time`/`Full-time`/
  rỗng — không có `"Intern"`.

**Chi tiết từng field còn thiếu** (1 field cho nhánh expat, 2 field cho nhánh intern — field thứ 2
của intern là điều kiện PHỤ bên trong nhánh đó, không phải 1 nhánh thứ 3 riêng biệt):

| Field | Dùng để | Nhánh áp dụng | Kiểu dữ liệu cần |
|---|---|---|---|
| `IS_EXPAT_NO_WP` | Đánh dấu nhân viên nước ngoài **không có work permit** (giấy phép lao động) | Expat — `true` → thuế = 20% flat trên `TAXABLE_INC`, bỏ qua lũy tiến | boolean |
| `EMP_TYPE` | Loại nhân viên, để nhận diện giá trị `"Intern"` | Intern — đúng loại này thì áp nhánh thuế riêng thay vì lũy tiến | string/enum |
| `HAS_TAX_COMMITMENT` | Có **giấy cam kết thuế** (mẫu cam kết 08/CK-TNCN) hay không | Chỉ có ý nghĩa BÊN TRONG nhánh Intern — có cam kết → thuế = 0%; không có cam kết + thu nhập >5tr → thuế = 10% flat | boolean |

Field gần nhất đang có, `employees.employee_type_name`, không đủ để suy ra cả 3 field trên — không
chỉ vì thiếu giá trị `"Intern"`, mà vì `IS_EXPAT_NO_WP` (quốc tịch + tình trạng work permit) và
`HAS_TAX_COMMITMENT` (giấy cam kết, có ngày hiệu lực riêng theo từng năm thuế) là 2 khái niệm hoàn
toàn khác, không nằm trong bất kỳ cột `employees` nào hiện có — cần HR xác nhận nguồn dữ liệu (nhập
tay qua UI mới, hay đồng bộ từ hệ thống nhân sự/hợp đồng lao động khác) trước khi thiết kế schema,
không chỉ là thêm cột.

**Quyết định người dùng (270726): hoãn nhánh expat/intern, chỉ triển khai nhánh chính thức đợt
này.** Nhánh đó cần thêm dữ liệu mới (chưa ai nhập) + xử lý riêng biệt phần cú pháp không tương
thích — không phải 1 câu sửa bug nữa.

### 3.3. Bậc thuế HR đưa — LÚC ĐẦU tưởng mâu thuẫn, đã XÁC NHẬN là luật thuế mới thật (2026)

Giải mã ngược công thức "chính thức" bằng toán học (điểm giao 2 đường thẳng liền kề trong `MAX` =
ngưỡng bậc thuế thật):
```
0.05x = 0.10x−500.000       → x = 10.000.000
0.10x−500.000 = 0.20x−3.500.000  → x = 30.000.000
0.20x−3.500.000 = 0.30x−9.500.000 → x = 60.000.000
0.30x−9.500.000 = 0.35x−14.500.000 → x = 100.000.000
```
→ Bậc thuế mã hoá trong công thức HR: **0-10tr/10-30tr/30-60tr/60-100tr/>100tr @ 5/10/20/30/35%**
— 5 bậc.

**Lúc đầu (270726, trước khi search):** bậc này khác bảng `pit_brackets` trong DB (5/10/18/32/52/
80tr @ 5/10/15/20/25/30/35%, 7 bậc, `effective_from=2009-01-01`) — dựa theo kiến thức huấn luyện
của model (biểu thuế TNCN 7 bậc, luật cũ). Đã dừng lại hỏi người dùng xác nhận trước khi migration
thay vì tự chọn.

**Xác nhận sau (270726, theo yêu cầu người dùng, search Google):** đây **KHÔNG phải mâu thuẫn** —
biểu 5 bậc HR đưa chính là **Luật Thuế Thu Nhập Cá Nhân 2025, Điều 9, hiệu lực 01/01/2026**, thay
thế biểu 7 bậc cũ. Xác nhận qua 2 nguồn độc lập khớp **chính xác từng con số** kể cả hằng số trừ
(-0,5tr/-3,5tr/-9,5tr/-14,5tr):
- [thuvienphapluat.vn — Biểu thuế TNCN lũy tiến 2026 (biểu thuế 5 bậc)](https://thuvienphapluat.vn/chinh-sach-phap-luat-moi/vn/ho-tro-phap-luat/chinh-sach-moi/100277/bieu-thue-tncn-luy-tien-2026-bieu-thue-5-bac)
- [MISA SME — Bảng tính thuế TNCN 2026 mới nhất](https://sme.misa.vn/343485/bang-tinh-thue-tncn/)

Kiến thức huấn luyện của model (biểu 7 bậc) là **PRIOR đã lỗi thời** — đúng luật trước 01/01/2026,
không phải luật hiện hành. `pit_brackets` table trong DB (`effective_from=2009-01-01`) **cũng là
luật cũ, chưa từng được cập nhật theo luật mới** — xác nhận đây là dữ liệu tham khảo lỗi thời thật
sự, không chỉ là "khác công ty này dùng". `pit_brackets` **giữ nguyên** trong DB (không xoá, không
sửa — ngoài phạm vi việc đang làm), nhưng **nên cập nhật theo biểu mới** ở 1 việc riêng nếu còn
dùng cho màn hình tham khảo/cấu hình nào đó — cờ theo dõi, chưa làm.

## 4. Triển khai

### 4.1. Migration — `atlas/migrations/20260727000000_pit_system_to_formula.sql`

```sql
UPDATE salary_components
SET component_type = 'formula',
    formula = 'ROUND(MAX(0.05 * [TAXABLE_INC], 0.10 * [TAXABLE_INC] - 500000, 0.20 * [TAXABLE_INC] - 3500000, 0.30 * [TAXABLE_INC] - 9500000, 0.35 * [TAXABLE_INC] - 14500000), 0)',
    updated_at = now()
WHERE code = 'PIT';
-- + INSERT salary_component_history để giữ audit trail
```

**Phát hiện khi viết migration:** `PIT.is_system = true`, và `SalaryComponentRepo.Update` có
`WHERE id = :id AND is_system = false` — gọi qua CRUD service bình thường sẽ **no-op thầm lặng**
(đúng loại lỗi đã tìm thấy ở chỗ khác trong đợt RBAC trước — `RoleRepo.Update`). Phải `UPDATE` trực
tiếp + tự `INSERT` vào `salary_component_history` (thay cho audit tự động của service bị bỏ qua).
`is_system` **giữ nguyên `true`** — PIT vẫn được bảo vệ khỏi xoá/sửa tuỳ tiện qua UI CRUD thường.

Migration đã áp dụng thật vào DB dev `payroll_engine` (verify bằng dry-run `BEGIN;...ROLLBACK;`
trước, sau đó áp dụng thật, xác nhận `component_type='formula'` + `is_system=true` sau khi chạy).
`atlas.sum` đã re-hash.

### 4.2. Dọn code chết trong `engine.go`/`payroll_service.go`

Xác nhận **PIT là `component_type='system'` DUY NHẤT** trong toàn bộ `salary_components` (query
`WHERE component_type='system'` → 1 dòng, trước migration) — nên toàn bộ subsystem PIT hardcode
xoá sạch được, không còn nơi nào khác dùng:
- `evalSystemComponent`, `calculateSplitPeriodPIT`, `splitPeriodByTaxChange`,
  `filterActivePITBrackets`, `calculateProgressivePIT`, `defaultPITBrackets` — xoá.
- `truncateToDay`, `sortDates` (helper riêng cho split-period) — xoá (grep xác nhận không dùng ở
  đâu khác).
- `case "system":` trong `engine.Calculate` switch — xoá.
- `CalculateInputs.PeriodStart`/`PeriodEnd`/`AllPITBrackets` — xoá (grep xác nhận 0 chỗ dùng khác).
- `NewFormulaEngine(components, pitBrackets)` → `NewFormulaEngine(components)` (bỏ tham số không
  còn tiêu thụ) — cập nhật toàn bộ 10 call site (`payroll_service.go` ×3, `engine_override_test.go`
  ×6, test mới ×nhiều).
- `PayrollService.pitBracketRepo` field + wiring trong `service.go` — xoá (không còn ai gọi;
  `PITBracketService`/route `/pit-brackets` riêng cho UI cấu hình **không bị ảnh hưởng**, vẫn dùng
  chung repo `PITBracketRepo` nhưng qua instance khác).

**Phát hiện phụ khi dọn:** `engine.go` (bản HEAD trước sửa) có **CRLF line ending** trên toàn bộ
913 dòng — khác biệt so với phần còn lại của repo (LF). Việc sửa file qua công cụ chuẩn (Edit +
gofmt) đã tự chuẩn hoá về LF khớp quy ước chung của repo — xác nhận qua diff bỏ qua khác biệt
CRLF/LF chỉ còn đúng 253 dòng, khớp chính xác các thay đổi có chủ đích ở trên, không có nội dung
nào khác bị đổi ngoài ý muốn.

**Sự cố phụ đã xử lý:** `gofmt -w internal/service/*.go` (chạy blanket cho cả thư mục thay vì chỉ
file đã sửa) vô tình định dạng lại 4 file không liên quan (`attendance_compute_builder.go`,
`attendance_daily_service.go`, `hris_cookie_client.go`, `salary_component_service.go`) — 1 trong số
đó (`salary_component_service.go`) bị hỏng nội dung thật (2 dấu nháy đơn ASCII `''` bị đổi thành 1
ký tự smart-quote Unicode `”` trong 1 dòng comment — phát hiện bằng `od -c` byte-level, không phải
gofmt bình thường sẽ làm). Đã `git checkout --` revert cả 4 file về đúng HEAD, xác nhận build/vet/
test vẫn xanh sau revert.

### 4.3. Test

- `internal/service/pit_formula_integration_test.go` (mới): `TestPITFormula_MigratedToFormulaType`
  (xác nhận migration áp đúng: `component_type='formula'`, `formula` không rỗng, `is_system=true`
  còn giữ), `TestPITFormula_BoundaryValues` (8 case, cô lập `TAXABLE_INC` trực tiếp qua component
  giả `type=input` — không phụ thuộc chuỗi GROSS/attendance — khoá đúng 5 ranh giới bậc bằng công
  thức THẬT nạp từ DB, không phải bản chép tay có thể trôi khỏi migration).
- `internal/service/payroll_template_enforce_integration_test.go` — test
  `TestTemplateEnforce_StatutoryAndSystemNeverMasked` đổi tên thành
  `TestTemplateEnforce_StatutoryNeverMasked`, cập nhật lại để assert PIT tính ra **số dương thật**
  (trước đây phải né tránh assert `PIT>0` vì bug chưa sửa) — giữ nguyên phần so sánh "mask không
  phải nguyên nhân khiến PIT đổi" (guard `statutoryOverrideBlocklist` độc lập với `component_type`,
  vẫn áp dụng dù PIT nay là `formula`).

`go build`/`go vet` sạch. Full suite: 4 fail baseline cũ đã biết (`TestReportPayrollSummaryRoute...`,
`TestReportBankTransferRoute...`, `TestPipelineProtectedRun...`, `TestPipelineProtectedLogs...`), 0
hồi quy mới.

### 4.4. Xác nhận không ảnh hưởng ngoài phạm vi (theo yêu cầu người dùng, verify thêm sau khi commit)

Người dùng hỏi lại "có chắc không ảnh hưởng core engine hiện tại". Thay vì chỉ dựa vào build/vet/
test đã có, chạy thêm 2 kill-test cụ thể cho đúng 2 điểm rủi ro tiềm ẩn nhất:

1. **`SnapshotForPeriod` (`salary_component_override_repo.go:148`) lọc `WHERE component_type =
   'formula'`** — trước đây PIT là `system` nên bị loại khỏi snapshot lúc chốt kỳ; giờ là `formula`
   nên **tự động được đưa vào**. Verify bằng test tạm (viết, chạy, xoá): gọi
   `SnapshotForPeriod` trực tiếp, xác nhận PIT xuất hiện đúng trong `payroll_formula_snapshots`
   với `scope_type='global'`, đúng công thức, không lỗi, không đụng unique constraint (khác
   `scope_type` với snapshot `'template'` của Task 4.5 nên không xung đột). Đây là tác dụng phụ
   **tốt**: PIT giờ có audit trail lúc chốt kỳ như mọi cột formula khác — trước đây không có.
2. **3 report generator có tham chiếu `"PIT"`** (`report_gen_pit_nam.go`, `report_gen_chi_phi_pb_da.go`,
   `report_gen_phan_bo_gdda.go`) — đọc code xác nhận cả 3 chỉ **đọc** giá trị đã tính sẵn từ
   `computed_values` (qua `GetComponentsByPeriods`/tương tự) để hiển thị/tổng hợp, KHÔNG tính lại
   thuế, không có logic bracket trùng lặp nào. Sẽ tự động hiện đúng số PIT mới, không cần sửa code.

**Còn lại chưa verify được** (ngoài phạm vi công cụ hiện có, không phải nghi ngờ code sai): chạy
`Calculate()` thật trên 1 kỳ lương đầy đủ quy mô production (12k+ nhân viên) — mọi test trong đợt
này chỉ chạy trên kỳ cách ly tự tạo (2099-01/02) hoặc mock 1 nhân viên.

## 5. Chưa làm (theo đúng phạm vi được xác nhận)

- **Nhánh expat/intern** — hoãn, chưa có dữ liệu (3 field không tồn tại).
- **Recompute 128 record `finalized` kỳ 05/2026** — người dùng xác nhận **không cần làm lúc này**.
  `payroll_records` thật hoàn toàn không bị đụng trong đợt sửa này (chỉ test trên kỳ cách ly tự tạo
  tự dọn). PIT của các kỳ đã tính TRƯỚC migration này vẫn giữ nguyên giá trị 0 (sai) cho tới khi có
  quyết định riêng về việc recompute.
- **`pit_brackets` table — ĐÃ LÀM (270726, sau khi kế hoạch bên dưới được xác nhận):** migration
  `atlas/migrations/20260727010000_pit_brackets_2026_law.sql` đã áp dụng vào DB dev `payroll_engine`
  — INSERT thêm đúng 5 dòng `effective_from='2026-01-01'` (bảng dưới), giữ nguyên 7 dòng
  `effective_from='2009-01-01'` cũ (không UPDATE/DELETE gì). Xác nhận bằng
  `SELECT effective_from, bracket_order, income_limit, tax_rate FROM pit_brackets ORDER BY
  effective_from, bracket_order` sau khi áp dụng: đúng 12 dòng, không trùng lặp/xung đột unique
  constraint `(effective_from, bracket_order)`. `atlas.sum` đã re-hash (`atlas migrate hash`). Full
  suite `go test ./...` sau migration: đúng 4 fail baseline cũ (2 report route + 2 pipeline route,
  không liên quan), 0 hồi quy — đã kiểm 3 file test có nhắc `pit_brackets`
  (`internal/repository/pit_bracket_integration_test.go` dùng `effective_from=1999-01-01` cách ly,
  không đụng dữ liệu 2026 mới; 2 file còn lại chỉ có comment, không assertion phụ thuộc số dòng).

  **Kế hoạch đã thi hành:**
  - **Xác nhận mức độ khẩn cấp thấp:** grep toàn `Core System-frontend` xác nhận có sẵn API client
    (`getPITBrackets`/`createPITBracketSet`, `lib/api/config.ts`) nhưng **0 màn hình thật gọi tới**
    — bảng này hiện không hiển thị cho ai, nên đây là việc dọn dữ liệu cho đúng, không phải sửa lỗi
    đang gây nhầm lẫn sống. Backend CRUD đầy đủ vẫn hoạt động bình thường
    (`PITBracketRepo`/`PITBracketService`/`PITBracketHandler`, route `/pit-brackets`, gate quyền
    `Settings.PITBrackets`) — **không đổi code CRUD, chỉ thêm dữ liệu**.
  - **Cách làm — additive, không UPDATE/DELETE:** bảng có unique constraint
    `(effective_from, bracket_order)`, thiết kế sẵn cho versioning theo thời điểm hiệu lực — đúng ý
    đồ gốc là "thêm bộ bậc mới với `effective_from` mới", không phải sửa đè bộ cũ. Migration mới
    (`atlas/migrations/2026072800000X_pit_brackets_2026_law.sql`):
    ```sql
    INSERT INTO pit_brackets (effective_from, bracket_order, income_limit, tax_rate, note, is_active)
    VALUES
      ('2026-01-01', 1, 10000000,  0.05, 'Luat Thue TNCN 2025, Dieu 9 - bac 1', true),
      ('2026-01-01', 2, 30000000,  0.10, 'Luat Thue TNCN 2025, Dieu 9 - bac 2', true),
      ('2026-01-01', 3, 60000000,  0.20, 'Luat Thue TNCN 2025, Dieu 9 - bac 3', true),
      ('2026-01-01', 4, 100000000, 0.30, 'Luat Thue TNCN 2025, Dieu 9 - bac 4', true),
      ('2026-01-01', 5, 0,         0.35, 'Luat Thue TNCN 2025, Dieu 9 - bac 5 (khong gioi han)', true);
    ```
    Bậc cũ (`effective_from='2009-01-01'`) giữ nguyên, không đổi `is_active` — lịch sử vẫn tra cứu
    được đúng bản chất "point-in-time", khớp thiết kế bảng.
    **Đã xác nhận convention thật** (`SELECT bracket_order, income_limit FROM pit_brackets ORDER BY
    bracket_order` trên DB dev `payroll_engine`): bậc cuối (không giới hạn) dùng sentinel
    `income_limit = 0`, KHÔNG phải `NULL` (bậc 7 cũ: `income_limit=0.00, tax_rate=0.35`) — migration
    trên đã khớp đúng convention này, không cần đoán/hỏi thêm.
  - **Không đụng `PayrollService`/engine** — bảng này đã ngắt kết nối khỏi tính lương thật từ migration
    270726 (mục 4.2), CRUD chỉ phục vụ tra cứu/tham khảo độc lập.
  - **Việc TIẾP THEO (không thuộc phạm vi migration này):** nếu về sau có màn hình FE thật render
    `pit_brackets`, cân nhắc thêm dòng cảnh báo "bảng này không dùng để tính lương thật — xem PIT
    formula tại Cấu hình > Cột lương" để tránh hiểu nhầm 2 nguồn dữ liệu.

## 6. Trạng thái git

Commit trên `Core System-backend@feature_1` — xem `CLAUDE.md` nhật ký 270726 để lấy đúng mã commit.
