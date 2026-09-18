---
id: self-docs/engine/payroll-engine-rule-flow
canonical_question: 'Technical guide and specification: Engine tính lương theo rule
  và bảng lương — mô tả cách hoạt động'
aliases:
- Engine tính lương theo rule và bảng lương — mô tả cách hoạt động
- Core System Engine Rule Flow 290726
entity_type: architecture_explainer
domain: self-docs > engine
last_verified: 2026-07-27
---

# Engine tính lương theo rule và bảng lương — mô tả cách hoạt động (2026-07-29)

**Loại tài liệu:** giải thích kiến trúc (explainer), viết theo yêu cầu "tóm tắt cách hoạt động của engine tính lương theo rule và bảng lương". Không phải báo cáo triển khai, không đề xuất thay đổi nào, không sửa dòng code nào trong phiên viết tài liệu này.

**Nguồn:** đọc trực tiếp code thật và truy vấn DB dev `payroll_engine` (không dựa vào tài liệu cũ):
`Core System-backend/internal/service/engine.go`, `payroll_service.go`, `payroll_scoped_resolver.go`,
`payroll_template_mask.go`, `internal/repository/payroll_record_repo.go`, `internal/models/Core System.go`.

---

## 1. Ý tưởng gốc: bảng lương là dữ liệu, không phải code

Toàn bộ "rule" tính lương không nằm trong Go. Mỗi cột của bảng lương là một dòng trong bảng
`salary_components`, và công thức của cột là một chuỗi text trong cột `formula` của chính dòng đó.
Engine Go chỉ là bộ thông dịch: nó đọc danh sách cột đang active, xếp thứ tự phụ thuộc, rồi tính từng
cột theo đúng công thức người dùng đã cấu hình. Muốn thêm một khoản phụ cấp mới hay đổi cách tính
thuế thì sửa dữ liệu qua UI, không cần build lại backend.

Mỗi cột có `component_type` quyết định *nguồn giá trị* của nó:

| `component_type` | Nguồn giá trị | Số cột trong DB dev (2026-07-29) |
|---|---|---|
| `input` | Nạp từ bên ngoài engine — bảng công, hồ sơ nhân viên, cấu hình bảo hiểm, nhập tay | 70 |
| `formula` | Engine tự tính từ công thức tham chiếu cột khác | 41 |
| `config` / `manual` / `system` | Về mặt thiết kế vẫn tồn tại nhưng hiện **không có dòng nào** | 0 |

Lưu ý quan trọng về `system`: từ 2026-07-27 (khi PIT chuyển sang `formula`) engine **không còn nhánh
`case "system"` lẫn `default:`** trong vòng tính. Một cột tạo mới với loại `system` sẽ không bao giờ
được engine gán giá trị. Chi tiết xem `PIT-Formula-Fix-270726.md` và
`Salary-Component-Modal-Type-Gating-290726.md`.

---

## 2. Engine công thức (`engine.go`) — thông dịch rule

### 2.1 Xếp thứ tự tính (topological sort)

`NewFormulaEngine(components)` gọi `buildOrder()`: với mỗi cột loại `formula`, nó rút các mã cột được
tham chiếu bằng regex `\[([A-Z0-9_]+)\]` (`extractDeps`), rồi duyệt sâu để cột phụ thuộc luôn được
tính trước. Trạng thái duyệt ba mức (chưa thăm / đang thăm / đã xong) cho phép phát hiện phụ thuộc
vòng và trả lỗi `circular dependency detected at [CODE]` ngay lúc dựng engine, trước khi tính đồng nào.

Hai điểm cần biết:

- `buildOrder` **chỉ** rút phụ thuộc cho cột loại `formula` (`engine.go:86`). Nếu một cột loại `input`
  có công thức, công thức đó vẫn được thi hành (mục 2.2) nhưng **không được đảm bảo thứ tự topo** —
  nó có thể chạy trước khi cột nó tham chiếu có giá trị.
- `seq` trong `salary_components` **không** phải thứ tự tính. `seq` chỉ là thứ tự hiển thị/sắp cột
  trong lưới; thứ tự tính do topological sort quyết định độc lập.

### 2.2 Vòng tính cho một nhân viên

`Calculate(inputs)` nhận sẵn một map `CODE → giá trị` (đã chứa mọi thứ nạp từ ngoài) rồi đi theo
`e.order`:

- Cột `input`/`config`/`manual`: **nếu map đã có giá trị thì giữ nguyên**. Chỉ khi thiếu, engine mới
  thử `evalExpression(c.Formula, vals)` như một giá trị mặc định; công thức lỗi hoặc rỗng thì gán `0`.
- Cột `formula`: công thức rỗng thì giữ giá trị đang có (hoặc `0`); công thức có nội dung thì evaluate.

Sau khi có số, `applyRounding` áp `rounding` của cột: `unit` làm tròn về đơn vị đồng, `thousand` làm
tròn về nghìn, `none` giữ nguyên.

### 2.3 Cú pháp công thức được hỗ trợ

Parser viết tay (đệ quy xuống) trong `engine.go`, thứ tự ưu tiên: so sánh → cộng/trừ/nối chuỗi →
nhân/chia → dấu âm một toán hạng → nguyên tử.

- Số học `+ - * /`, ngoặc, dấu âm.
- So sánh `== != < > <= >=`, trả về `1.0` (đúng) hoặc `0.0` (sai) — nên `IF([A] > 0, x, y)` chạy được.
- Tham chiếu cột `[MÃ_CỘT]`. **Mã không tồn tại trong map không phải lỗi — nó lặng lẽ thành `0`**
  (`fromInterfaceValue(nil)`). Đây là nguồn gốc của cả một họ lỗi "im lặng ra 0".
- Chuỗi: literal `"..."`/`'...'`, nối bằng `&` hoặc bằng `+` khi một vế là chuỗi. Chuỗi bị chặn ở
  mọi phép toán số học và so sánh (trả lỗi rõ ràng).
- Hàm: `MIN`, `MAX` (≥2 tham số), `ABS`, `ROUND` (1–2 tham số), `IF` (đúng 3), `IFS` (các cặp
  điều kiện/giá trị), `SUM`. Cả bảy hàm chỉ nhận tham số số.
- Tiền tố `=` kiểu Excel được cắt bỏ trước khi parse.

Không có: vòng lặp, biến tạm, so sánh chuỗi, hàm ngày tháng, hàm tài chính.

### 2.4 Xử lý lỗi: fail-soft, ghi log

Một công thức lỗi (chia cho 0, thiếu ngoặc, toán tử sai) **không làm hỏng cả lượt tính**. Engine ghi
`log.Printf("[Engine] formula %s eval error: ...")`, gán cột đó `= 0`, rồi đi tiếp. Hệ quả thực tế cần
nhớ: một rule viết sai biểu hiện ra ngoài giống hệt một rule đúng mà kết quả bằng 0 — chỉ log phân
biệt được. `ValidateFormula` (gọi từ UI khi thêm/sửa cột và bấm "Kiểm tra công thức") là chốt chặn
chủ động duy nhất: nó kiểm mã cột lạ và chạy thử công thức với mọi biến = 1.

---

## 3. Pipeline tính lương một kỳ (`PayrollService.Calculate`)

`Calculate(ctx, periodID, salaryOverrides)` là đường tính cả kỳ. Trình tự:

1. **Nạp định nghĩa cột** — `componentRepo.ListActive` → dựng engine gốc (`baseEngine`).
2. **Nạp cấu hình bảo hiểm** đang hiệu lực (`insuranceRepo.GetAllActive`) — các tỷ lệ này vào thẳng
   map giá trị như biến thường.
3. **Nạp bảng công** theo tháng/năm của kỳ (`attSummaryRepo.GetSummaryMapByMonth`). **Tập nhân viên
   được tính = tập mã có bảng công trong tháng đó**, không phải toàn bộ danh sách nhân viên.
4. **Nạp override công thức** đang hiệu lực tại ngày đầu kỳ → dựng `scopedResolver` (mục 4).
5. **Nạp nhập tay** (`payroll_manual_inputs`) theo kỳ: thưởng, điều chỉnh. Riêng `BASIC_SAL` bị loại
   ra ở bước áp dụng.
6. **Nạp bốn nhóm dữ liệu point-in-time** tính tại **ngày 20 của tháng kỳ** (khớp cửa sổ chấm công
   21→20), để kỳ cũ không bị tính theo trạng thái hiện tại của nhân viên:
   - `ResolveLevelAsOf` → `LEVEL_NUM` theo cấp bậc hiệu lực lúc đó;
   - `ResolveDepartmentAsOf` → phòng ban dùng để giải override theo phòng;
   - `CountDependentsAsOf` → `DEPENDENT_CNT` cho giảm trừ thuế;
   - `loadTemplateMaskData` → cấu trúc lương theo cấp bậc (mục 5).
   Vắng dữ liệu lịch sử thì fallback về giá trị hiện tại trên `employees`.
7. **Dựng `calcShared`** — gom tất cả thứ trên vào một struct dùng chung, đọc kill-switch
   `PAYROLL_TEMPLATE_ENFORCE` **một lần** tại đây.
8. **Lặp từng nhân viên** → `computeEmployee`, gom kết quả vào batch, ghi bằng
   `recordRepo.UpsertBatchComputed` theo lô (kích thước lấy từ env, xem `getPayrollBatchSize`). Lỗi
   tính của một người chỉ log và bỏ qua người đó, không dừng cả kỳ.

`CalculateOne(periodID, empCode, basicSalary)` là đường tính lại đúng một người (dùng khi HR sửa một
ô). Nó lặp lại đúng các bước trên cho một nhân viên, **dùng chung `loadTemplateMaskData` và chung
`computeEmployee`** — chủ đích để "tính lại một người" không bao giờ lệch "tính cả kỳ".

### 3.1 Giá trị đầu vào đến từ đâu (`buildInputValues` + `resolveSourceField`)

`buildInputValues` gán sẵn một tập biến cố định: định danh nhân viên, `DEPENDENT_CNT`, `LEVEL_NUM`,
`SENIORITY_MONTHS`, `AVG_SALARY_12M`, mã số thuế/sổ BH, toàn bộ nhóm ngày công (`STD_DAYS`,
`ACTUAL_DAYS`, `PAID_DAYS`, `PROB_DAYS`, `OFFICIAL_DAYS`...), nhóm nghỉ (lễ, bù, ốm, phép, chế độ,
không lương, lễ đi làm), nhóm bữa ăn, nhóm phụ cấp trên bảng công, cộng các tỷ lệ bảo hiểm.

Ngoài tập cố định đó, mỗi cột `input` có thể khai `source_field` dạng `"bảng.cột"` và
`resolveSourceField` map tường minh sang field Go tương ứng (~30 nhánh `switch` cho
`attendance_summary.*` và `employees.*`). Đây là cách thêm một input mới **không cần sửa
`buildInputValues`** — nhưng `source_field` không có trong bảng liệt kê thì trả `(0, false)` và cột
lặng lẽ không được nạp.

**`BASIC_SAL` là ngoại lệ đáng nhớ nhất:** nó **không** đọc từ `employees` trong đường tính này. Nó
đến từ tham số `salaryOverrides` — bảng lương HR upload lên, frontend giữ trong `sessionStorage`. Gọi
`Calculate` với body rỗng sẽ zero-out lương cơ bản của cả kỳ. Đây cũng là lý do mọi hàm mô phỏng tác
động (`ComputeFormulaImpact`, `ComputeTemplateImpact`) phải nhận và truyền `salaries` vào cả hai lần
tính, nếu không phần chênh lệch báo về sẽ vô nghĩa.

Thứ tự ghi đè trong map giá trị, từ thấp đến cao: `buildInputValues` → point-in-time
(`LEVEL_NUM`, `DEPENDENT_CNT`) → `salaryOverrides[BASIC_SAL]` → `source_field` của cột `input` →
nhập tay (`payroll_manual_inputs`, trừ `BASIC_SAL`).

---

## 4. Override công thức theo phạm vi (`payroll_scoped_resolver.go`)

Một cột có thể có công thức khác nhau cho từng phòng ban hoặc từng nhân viên. Bảng
`salary_component_overrides` giữ các bản ghi này với `scope_type` = `department` | `employee`,
`scope_ref` là mã phòng/mã nhân viên, kèm khoảng hiệu lực và `priority`.

- Repo trả danh sách đã sắp theo `priority` giảm dần rồi ngày hiệu lực giảm dần; `buildScopedResolver`
  giữ **bản ghi đầu tiên** cho mỗi cặp (mã cột, scope_ref) — tức bản ưu tiên cao nhất.
- `resolveFor(empCode, deptCode)` áp override phòng ban trước, override nhân viên sau, nên **nhân
  viên luôn thắng phòng ban**. Hàm trả về map các cột bị đổi công thức, kèm một *signature* (nối
  `code=formula` đã sắp) dùng làm khoá cache.
- `applyResolvedFormulas` thay chuỗi `formula` trên một bản **clone** của danh sách cột, rồi dựng
  engine mới từ bản clone. Engine gốc không bị đụng. Override áp cho cả `formula` và
  `input`/`config`/`manual` (cơ chế "ghim ô").
- Với các cột bị override, `computeEmployee` **xoá giá trị đã nạp khỏi map đầu vào** trước khi tính —
  nếu không, nhánh "giữ nguyên nếu đã có giá trị" ở mục 2.2 sẽ khiến công thức override không bao giờ
  chạy.

**Cache engine:** dựng engine cho từng nhân viên sẽ rất đắt ở kỳ hàng chục nghìn người, nên engine
được cache theo khoá `tplSig + "|" + sig` (template + override thật). Khoá phải gồm **cả hai** thành
phần: nếu chỉ khoá theo `sig`, hai nhân viên cùng "không override" nhưng khác cấu trúc lương sẽ dùng
lẫn engine của nhau — sai tiền và im lặng.

**Cột pháp định không cho ghi đè trực tiếp:** `statutoryOverrideBlocklist` (trong
`salary_component_service.go`) chặn cả ở tầng tạo override, ở `SetCell`, và một lần nữa ở bước dựng
mask. Muốn điều chỉnh thì đi qua các cột `*_ADJ` tương ứng.

---

## 5. Cấu trúc lương theo cấp bậc — enforce bằng "mask về 0"

Tính năng gán template lương theo cấp bậc (`payroll_templates` / `template_components` /
`employee_payroll_templates`) không lọc danh sách cột. Nó enforce bằng cách **sinh override
`formula = "0"`** cho những cột phụ cấp không thuộc cấu trúc lương của nhân viên, rồi đi tiếp qua
đúng cơ chế override ở mục 4 — nhờ vậy `engine.go` không phải sửa một dòng nào.

Quy tắc chọn cột bị mask (`buildTemplateMaskFormulas`):

```
mask = maskableUniverse − closure(template của nhân viên) − cột pháp định − cột type=system
```

- `maskableUniverse` = hợp mọi mã cột xuất hiện trong **bất kỳ** template nào đang tồn tại
  (data-driven, dựng từ `template_components` sống, không hardcode). Ý nghĩa: một cột là "phụ cấp
  theo cấp bậc" khi và chỉ khi có ít nhất một template chứa nó. Các cột tổng (`GROSS`, `TAXABLE_INC`,
  `PIT`, `NET_PAY`) và các input vận hành không nằm trong template nào nên **không bao giờ bị mask** —
  chúng tự cộng đúng vì phụ cấp bị mask đã bằng 0.
- `closure` đi **chiều xuống**: cột trong template cộng với mọi cột mà chúng phụ thuộc (đệ quy qua
  `extractDeps`), để không kéo nhầm về 0 một cột hợp lệ mà cột trong template cần.
- Override thật (phòng ban/nhân viên) **đè lên mask**: HR cấp ngoại lệ cho một người vẫn thắng cấu
  trúc chung của cấp bậc.

Hai chốt an toàn: (a) nhân viên **chưa được gán** template thì không mask gì cả, và bất kỳ lỗi DB nào
trong `loadTemplateMaskData` cũng trả về ba map `nil` → không mask ai (thà tính đủ như cũ còn hơn để
trắng lương); (b) toàn bộ cơ chế nằm sau kill-switch `PAYROLL_TEMPLATE_ENFORCE`, **mặc định OFF**.
Trạng thái thật đọc qua `TemplateEnforceStatus()`; endpoint xem trước tác động
(`ComputeTemplateImpact`) ép cứng on/off cho từng kịch bản mô phỏng nên không phụ thuộc giá trị env
lúc gọi. Bối cảnh đầy đủ: `Salary-Structure-Template-Analysis-260726.md`.

Cảnh báo về UI: một "khoản phụ cấp" thường gồm nhiều cột con (ăn ca = `MEAL_ALLOW` + `MEAL_TAX` +
`MEAL_NONTAX`). `closure` không tự nối các cột con không phụ thuộc nhau, nên template phải chứa cả
nhóm nếu muốn giữ khoản đó.

---

## 6. Chuỗi rule thật đang chạy trong DB dev

41 cột `formula` tạo thành một chuỗi bốn tầng. Trích các mốc chính (đọc trực tiếp từ
`salary_components`, sắp theo `seq`):

**Tầng 1 — ngày công và lương theo ngày**

| Cột | Công thức |
|---|---|
| `PAID_DAYS` | `[ACTUAL_DAYS] + [HOLIDAY_DAYS] + [PAID_LEAVE_DAYS] + [COMP_DAYS] + [REGIME_DAYS] + [SI_DAYS] + [ADJ_DAYS]` |
| `PROB_EARNED` | `[PROB_DAYS] * [BASIC_SAL] * 0.85 / [STD_DAYS]` |
| `OFFICIAL_EARNED` | `([PAID_DAYS] - [PROB_DAYS]) * [BASIC_SAL] / [STD_DAYS]` |
| `RESP_EARNED` | `[PAID_DAYS] * [RESPONSIBILITY_ALLOW] / [STD_DAYS]` |
| `EARNED_SAL` | `[PROB_EARNED] + [OFFICIAL_EARNED] + [RESP_EARNED]` |

**Tầng 2 — tách phụ cấp chịu thuế / không chịu thuế** (ngưỡng nằm ngay trong công thức, không hardcode
trong Go): `MEAL_ALLOW = [MEALS_TOTAL] * 45000`, `MEAL_TAX = MAX(0, [MEAL_ALLOW] - 730000)`,
`MEAL_NONTAX = MIN([MEAL_ALLOW], 730000)`; tương tự cặp `PHONE_TAX`/`PHONE_NONTAX` ở ngưỡng 400.000.

**Tầng 3 — tổng thu nhập, bảo hiểm, thuế**

| Cột | Công thức |
|---|---|
| `GROSS` | tổng `EARNED_SAL` + toàn bộ phụ cấp chịu/không chịu thuế + OT + `BONUS_TOTAL` + `TOTAL_SUPPORT` + `ADJ_PLUS` − `ADJ_MINUS` |
| `TAXABLE_GROSS` | `[GROSS]` trừ hết các khoản không chịu thuế, trợ cấp thôi việc, chế độ BH, thưởng du lịch |
| `SI_EMP` / `HI_EMP` | `MIN([BASIC_SAL], 46800000) * 0.08` / `* 0.015` (trần 20 lần lương cơ sở) |
| `UI_EMP` | `MIN([BASIC_SAL], 106200000) * 0.01` (trần riêng của BHTN) |
| `TOTAL_INS` | `[SI_EMP] + [SI_ADJ] + [HI_EMP] + [HI_ADJ] + [UI_EMP] + [UI_ADJ]` |
| `PERSONAL_DED` | `15500000` (hằng số — vẫn là một "công thức") |
| `DEPENDENT_DED` | `[DEPENDENT_CNT] * 6200000` |
| `TAXABLE_INC` | `MAX(0, [TAXABLE_GROSS] - [TOTAL_INS] - [TOTAL_DED] - [CHARITY_DED])` |
| `PIT` | `ROUND(MAX(0.05*[TAXABLE_INC], 0.10*[TAXABLE_INC]-500000, 0.20*[TAXABLE_INC]-3500000, 0.30*[TAXABLE_INC]-9500000, 0.35*[TAXABLE_INC]-14500000), 0)` |

Công thức `PIT` là chỗ đáng chú ý nhất về mặt kỹ thuật: thuế bậc thang được viết lại thành **hàm
`MAX` của năm đường thẳng** thay vì vòng lặp qua bảng bậc thuế. Đây là hệ quả của việc engine không
có vòng lặp, và là kết quả của đợt chuyển PIT từ `component_type='system'` (logic Go) sang `formula`
ngày 2026-07-27 — xem `PIT-Formula-Fix-270726.md`. Bảng `pit_brackets` vẫn tồn tại trong DB nhưng
đường tính hiện tại **không đọc nó**.

**Tầng 4 — thực lãnh và chi phí công ty**

`NET_INCOME = [GROSS] - [TOTAL_INS] - [PIT] - [PIT_ADJ]`;
`NET_PAY = [GROSS] - [TOTAL_INS] - [TOTAL_PIT] - [TOTAL_POST_DED] + [TOTAL_POST_ADD]`;
`NET_PAY_2 = [NET_PAY] - [ADVANCE_1]`. Sau đó là nhóm chi phí phía công ty (`SI_CTY` 17%, `TNLD_CTY`
0,5%, `HI_CTY` 3%, `UI_CTY` 1%, `TOTAL_INS_CTY`, `KPCD_CTY` 2%) và `UNION_FEE = [BASIC_SAL] * 0.005`.

Vì `GROSS` và `NET_PAY` là *tổng của các cột con*, một khoản bị mask hoặc bị lỗi công thức về 0 sẽ
làm tổng lệch **mà không có dấu hiệu lỗi nào** trên số cuối. Đó là lý do các báo cáo xem trước tác
động tồn tại.

---

## 7. Bảng lương: lưu ở đâu, hiện ra sao

### 7.1 Lưu trữ

Kết quả của một nhân viên trong một kỳ là một dòng `payroll_records`, khoá duy nhất
`(employee_id, period_id)`. Bảng có nhiều cột quan hệ truyền thống (mã, tên, phòng ban, ngày công,
giờ OT...) nhưng **kết quả tính thật nằm trong hai cột JSONB**:

- `computed_values` — map `mã cột → giá trị` (số hoặc chuỗi) sau khi đã áp override/mask;
- `base_values` — kết quả tính lại bằng **engine gốc** (không override), **chỉ sinh khi nhân viên có
  override thật** (`sig != ""`), để frontend biết ô nào bị thay đổi và ô nào bị ảnh hưởng lan truyền.
  Mask theo template chủ đích **không** sinh `base_values` (nó không phải "người dùng ghi đè", và
  sinh thêm sẽ chạy engine lần hai cho toàn bộ nhân viên có template).

Vì lưu JSONB, thêm một cột lương mới **không cần migration** — nó chỉ là một khoá mới trong map.

`status` của record là `draft | calculated | finalized`. `approved_at` / `approved_by` /
`rejected_reason` là trục **độc lập** với `status`/finalize (thiết kế 2026-07-23).

### 7.2 Hiển thị (lưới Excel)

`PayrollRecordRepo.GetRows` dựng lưới bằng cách đi **từ `attendance_summary`** (chỉ tháng khớp kỳ và
`is_finalized = true`), `LEFT JOIN employees`, rồi `LEFT JOIN payroll_records`. Hai hệ quả trực tiếp:

- **Số dòng của bảng lương do bảng công quyết định**, không do `payroll_records`. Người có bảng công
  nhưng chưa tính lương vẫn hiện, với `computed_values` rỗng (`COALESCE(..., '{}')`).
- Cột hiển thị và thứ tự cột lấy từ `salary_components` (`seq`), giá trị từng ô lấy từ
  `computed_values` theo mã cột. Frontend không chứa công thức nào.

Truy vấn chạy qua `scopedExecutor` và nhận `unlimited` / `allowedCompanies` — trần phạm vi công ty của
người gọi, áp ở tầng SQL, không thể vượt bằng query string. Chi tiết ở tài liệu RBAC.

### 7.3 Sửa một ô (`SetCell` / `UndoCell`)

Sửa một ô trên lưới **không** ghi thẳng vào `computed_values`. Luồng thật:

1. Chặn nếu cột nằm trong `statutoryOverrideBlocklist`; resolve `component_id` từ **mã cột** chứ
   không tin id do client gửi.
2. Ghi một `salary_component_overrides` phạm vi `employee`, `source = cell_pin`, `priority = 1000`
   (để ghim thắng mọi override công thức khác), hiệu lực đúng khoảng thời gian của kỳ. Nếu người dùng
   xoá giá trị thì xoá bản ghi override đó. Bước này **commit ngay, cố ý nằm ngoài transaction** phía
   sau — vì `CalculateOne` chạy tiếp theo dùng kết nối DB khác và phải nhìn thấy override mới.
3. Gọi `CalculateOne` → tính lại toàn bộ chuỗi cho đúng một người, upsert record, trả `{computed, base}`
   để frontend patch đúng một hàng.
4. Trong **một transaction**: lưu giá trị đã tính vào override (khi người dùng chỉ gửi công thức),
   ghi `cell_edits` (append-only, có `seq`, giá trị cũ/mới, lý do bắt buộc), và ghi `audit_logs`.
   Audit ghi lỗi thì cell edit cũng rollback — không có lịch sử sửa ô nào tồn tại mà thiếu audit.

`UndoCell` không xoá lịch sử: nó append một bản ghi hoàn tác, có kiểm `expectedSeq` (compare-and-set)
để hai người sửa cùng ô không ghi đè nhau.

### 7.4 Chốt kỳ

`Finalize` đổi trạng thái record của kỳ, rồi gọi `overrideRepo.SnapshotForPeriod` ghi lại **bộ công
thức đã dùng** (mặc định + override hiệu lực) vào `payroll_formula_snapshots`. Nhờ đó sửa rule sau
này không làm mất khả năng giải thích một kỳ đã chốt. Snapshot mask theo template cũng bị gate theo
cùng kill-switch — để snapshot không nói "cột này bị mask" trong khi số thật của kỳ không hề bị mask.

---

## 8. Xem trước tác động trước khi đổi rule

Hai hàm mô phỏng, cùng một nguyên tắc: tính **hai lần trong bộ nhớ** cho cả kỳ, khác đúng một biến,
so sánh, **không ghi DB dòng nào**.

- `ComputeFormulaImpact` — đổi công thức của một cột: "nếu sửa rule này thì ai lệch bao nhiêu".
- `ComputeTemplateImpact` — bật/tắt mask theo cấu trúc lương: hai kịch bản ép cứng `templateEnforce`
  true/false, độc lập với env thật.

Cả hai **phải** nhận `salaries` (xem mục 3.1) và trả 422 khi thiếu; thiếu thì cả hai lần tính đều
dùng `BASIC_SAL = 0` và kết quả so sánh sẽ vô nghĩa. Một điểm UX đã biết chưa xử lý: `totalNetDelta`
có thể bằng 0 trong khi một cột khác lệch thật (cột không nằm trên đường tới `NET_PAY`) — câu "Tổng
thực lãnh lệch 0 đ" dễ bị đọc thành "không ảnh hưởng gì". Xem `Salary-Column-Sync-Impact-280726.md`.

---

## 9. Những chỗ dễ hiểu sai — tóm gọn

| Ngộ nhận | Thực tế |
|---|---|
| Sửa cách tính lương phải sửa code Go | Sửa dữ liệu `salary_components` là đủ; engine chỉ thông dịch |
| `seq` là thứ tự tính | `seq` chỉ là thứ tự hiển thị; thứ tự tính do topological sort |
| Mã cột viết sai sẽ báo lỗi | Không — nó thành `0` im lặng (`fromInterfaceValue(nil)`) |
| Công thức lỗi làm hỏng lượt tính | Không — log rồi gán `0` cho cột đó, đi tiếp |
| `BASIC_SAL` đọc từ `employees` | Không — đến từ bảng lương HR upload (`salaryOverrides`) |
| Bảng lương lấy dòng từ `payroll_records` | Lấy từ `attendance_summary` đã chốt, LEFT JOIN sang records |
| Thêm cột lương cần migration | Không — `computed_values` là JSONB |
| Sửa một ô là ghi vào kết quả | Ghi một override `cell_pin`, rồi tính lại cả chuỗi cho người đó |
| Cột `system` vẫn hoạt động | Không — engine không còn nhánh `system`, cột đó không bao giờ có giá trị |
| PIT tính từ bảng `pit_brackets` | Không — PIT là `formula` viết bằng `MAX` của 5 đường thẳng |
| Template lương lọc bớt cột | Không — nó sinh override `formula="0"`, và mặc định đang TẮT |

---

## 10. Tài liệu liên quan

- `PIT-Formula-Fix-270726.md` — vì sao PIT là `formula` chứ không phải logic Go, và bảng bậc thuế.
- `Salary-Structure-Template-Analysis-260726.md` — thiết kế mask-về-0, ba vòng thiết kế, kill-switch.
- `Salary-Column-Sync-Impact-280726.md` — đồng bộ cột lương, `usage`, `reorder`, xem trước tác động.
- `Salary-Component-Modal-Type-Gating-290726.md` — điều kiện lưu theo loại cột ở modal thêm/sửa cột.
- `Core System-backend/docs/formulas-name-manager-backend.md` — mô tả backend engine cho đội frontend.
