---
id: self-docs/engine/report-template-config-analysis
canonical_question: 'Technical guide and specification: Cấu hình template báo cáo
  + tái dùng rule cho payslip — phân tích'
aliases:
- Cấu hình template báo cáo + tái dùng rule cho payslip — phân tích
- Report Template Config Analysis 040826
entity_type: how_to
domain: self-docs > engine
last_verified: 2026-08-04
---

# Cấu hình template báo cáo + tái dùng rule cho payslip — phân tích (040826)

Tài liệu canonical cho hạng mục **"bảng cấu hình template báo cáo"** bắt đầu 2026-08-04. Phiên này là
phiên phân tích/thảo luận, **chưa chia task, chưa lên plan, không sửa code**. Người dùng yêu cầu tạm
treo việc phân rã task để detail từng ý trước.

Năm ý người dùng nêu (giữ nguyên số để tham chiếu về sau):

1. Có sheet Báo cáo nhưng chưa có nơi tạo ra báo cáo. Báo cáo về bản chất là tổng hợp theo từng
   cột/từng rule của từng nhân viên rồi cộng lại theo một mẫu template được cung cấp → muốn một
   **bảng cấu hình template cho báo cáo** thay vì code từng dòng dữ liệu.
2. **Tái sử dụng bảng rule cho payslip**, thêm một `type` để phân biệt rule đó dùng trên report hay
   payslip.
3. Có một **bảng lưu các template báo cáo** đã tạo — cần đề xuất tạo bảng mới hay tái dùng bảng có sẵn.
4. Bỏ qua các nút báo cáo trên header hiện tại; thêm **một selection box** chọn template báo cáo đã
   cấu hình rồi show lên sheet.
5. Nơi cấu hình template báo cáo **nằm trong sheet Cấu hình** cho đồng bộ giao diện hiện tại.

Mọi khẳng định dưới đây được kiểm bằng đọc code thật và truy vấn DB `payroll_engine` ngày 2026-08-04.

---

## 0. RÀNG BUỘC NỀN CHẶN CẢ NĂM Ý — `salary_components` là bảng phù du

Đây là phát hiện quan trọng hơn cả năm ý trên, và nó **quyết định câu trả lời cho ý 2 và ý 3**.

`migrationSalaryComponentsV4` nằm trong `RunMigrations()` (`internal/database/database.go:232`) nên
chạy **mỗi lần backend khởi động** (`AUTO_MIGRATE=true` là mặc định, `cmd/Core System/main.go:67-80`).
Nó mở đầu bằng:

```sql
-- STEP 1: XÓA TOÀN BỘ (cascade xóa template_components)
DELETE FROM salary_components;
-- STEP 2: INSERT TẤT CẢ THEO CẤU TRÚC EXCEL
INSERT INTO salary_components (seq, code, name, ...) VALUES ...   -- 109 mã hardcode, KHÔNG có ON CONFLICT
```

Không chỉ định cột `id` → mọi dòng nhận `gen_random_uuid()` **mới** mỗi lần boot.

### 0.1 Bằng chứng đo được, không suy đoán

| Phép đo | Kết quả |
|---|---|
| `select min(created_at), max(created_at) from salary_components` | `2026-07-29 16:21:29.11226+07` .. `.11685+07` — **toàn bộ 110 dòng sinh trong cùng 4 ms** |
| Tập mã DB so với tập mã V4 seed | DB = đúng 109 mã của V4 **+ `CONS_ALLOW`** (mã duy nhất đến từ một self-heal đặt sau V4). Không có mã nào do người dùng tạo. |
| 13 mã mà `migrations/v51_add_missing_salary_components.sql` từng INSERT (`BHBV_COLLECT`, `PROV_13M`, `PROV_TET_AM`, `REGIME_LEAVE_DAYS`, `PENDING_LEAVE_PAY`…) | **0 mã còn tồn tại** — file migration đó đã `applied` trong `schema_migrations` nên không chạy lại, còn V4 thì xoá nó mỗi boot |
| `salary_component_history` — số dòng có `component_id IS NULL` | **11/11** — FK `ON DELETE SET NULL` đã nổ cho 100% số dòng, chứng minh `DELETE` đã thực sự chạy và cắt đứt mọi liên kết theo `id` |
| `salary_formula_configs` — dòng trỏ mã không tồn tại | **15/18** |

### 0.2 Ba bảng FK vào `salary_components(id)` và số phận của chúng

```
salary_component_history    . component_id  -> SET NULL
salary_component_overrides  . component_id  -> CASCADE
template_components         . component_id  -> CASCADE
```

Hai bảng `CASCADE` bị **xoá sạch mỗi lần restart**. Cả hai hiện đều **0 dòng**.

Điều nghiêm trọng nhất, và nó nằm ngoài phạm vi cả tính năng template lẫn báo cáo:
**`salary_component_overrides` là tính năng đang chạy thật** — override công thức theo phòng ban/nhân
viên, được `payroll_service.go` đọc ở **bốn** điểm tính lương (`:240`, `:609`, `:729`, `:914`) qua
`overrideRepo.ListActiveForDate`, và đã có UI riêng (`SalaryComponentOverridesPanel.tsx`, dựng 250726).
Nghĩa là: **mọi ngoại lệ lương mà HR cấu hình cho một phòng ban hay một nhân viên sẽ bị xoá không dấu
vết ở lần backend restart kế tiếp**, không audit trail, không cách phục hồi (bảng này không có cột
`component_code` để cứu như `salary_component_history`).

### 0.3 Hệ quả trực tiếp lên năm ý

- **Ý 2 không khả thi ở dạng nêu.** Nếu rule báo cáo/payslip được lưu **trong** `salary_components`
  (thêm một `type` mới), thì mọi rule HR tạo qua UI **biến mất sau lần restart đầu tiên**. Đã chứng
  minh bằng 21 mã đã mất thật.
- **Ý 3 không được tái dùng `template_components`** — bảng đó đang bị CASCADE xoá mỗi boot.
- Mọi bảng mới sinh ra cho báo cáo **phải khoá theo `component_code` (varchar)**, tuyệt đối không FK
  vào `salary_components(id)`. Đây đúng là bài học mục K trong `HANDOVER-giatbh.md` mà đồng nghiệp
  `giatbh` đã rút ra khi bảng `salary_component_versions` của họ bị xoá 3 lần liên tiếp; họ đã sửa cho
  bảng của họ, phần còn lại của hệ thống chưa.

Xem thêm `Salary-Structure-Template-Analysis-260726.md` mục 15.2 (cùng gốc nguyên nhân, phát hiện cùng
ngày trên hạng mục template lương).

### 0.4 Kết quả thi hành Task 0 (040826-F1, RE-LINK) — đã xong

Thi hành đúng theo `llmwiki/wiki/sources/draft/040826-Core System-template-on-giatbh-engine-PLAN.md` Task 0
trên `Core System-backend@feature_v2`. Phương án **RE-LINK**: `component_code` là khoá bền,
`component_id` hạ xuống cột dẫn xuất, nối lại từ code mỗi boot bằng migration mới
`database.MigrationDurableComponentCode` (mốc chữ cái **BO**, chạy sau V4).

**Baseline đo được trước khi sửa** (G4 — không chép con số cũ trong tài liệu, tự đo lại):
`go test ./...` = **736 passed / 24 failed** (con số "6 test RBAC" ghi trong PLAN mục G4 đã lỗi thời —
phần lớn 24 fail hiện tại là do bảng `salary_component_versions` chưa tồn tại trên DB dev, không liên
quan Task 0). `tc=0 sco=0` khớp mục 0.2 ở trên.

**Chứng minh khuyết tật trước khi sửa** (`BEGIN; ... ROLLBACK;`, không đụng DB thật):
```
truoc=1
sau=0
```
1 dòng `template_components` bị xoá sạch ngay khi `DELETE FROM salary_components` chạy — đúng khuyết
tật ở mục 0.2.

**3 câu INSERT đã sửa (đường ghi, Bẫy 1 trong brief)**: `payroll_template_repo.go` `ReplaceComponents`,
`salary_component_override_repo.go` `Create` và `CreateTx` — cả ba nay ghi thêm `component_code` bằng
subquery `(SELECT code FROM salary_components WHERE id = $2)` tại thời điểm insert.

**Idempotent**: chạy chuỗi SQL migration BO **2 lần liên tiếp** vào `payroll_engine` — cả hai lần
`ALTER TABLE`/`UPDATE 0`/`CREATE INDEX` không lỗi.

**Schema sau khi áp** — `\d template_components` và `\d salary_component_overrides`: không còn
constraint `template_components_component_id_fkey` / `salary_component_overrides_component_id_fkey`;
có cột `component_code varchar(50)` + index `idx_tc_component_code` / `idx_sco_component_code` ở cả
hai bảng; UNIQUE `salary_component_overrides_component_id_scope_type_scope_re_key` giữ nguyên theo
`component_id` (đúng ràng buộc 5 của brief — không đổi để tránh phình phạm vi `ON CONFLICT`).

**4 test mới** (`internal/repository/payroll_template_integration_test.go` thêm 2,
`internal/repository/salary_component_override_durability_integration_test.go` file mới):
- `TestTemplateComponents_SurvivesComponentReseed`
- `TestTemplateComponents_OrphanedRowNotDeletedButHiddenFromListComponents`
- `TestSalaryComponentOverrides_SurvivesComponentReseed`
- `TestSalaryComponentOverrides_OrphanedRowNotDeletedButHiddenFromActiveList`

Cả 4 xanh. **Đã chứng minh test thật sự bắt được bug** (không chỉ tin nó xanh): `git checkout --`
tạm 2 file sửa đường ghi → 2 test durability FAIL đúng như kỳ vọng (`row missing after reseed`) →
`git apply` áp lại bản sửa → xanh trở lại. `go test ./...` sau khi sửa xong: **24 fail, danh sách
tên test khớp tuyệt đối với baseline** (so bằng `diff`, không thêm/bớt fail nào).

**Nghiệm thu ở tầng thật (bắt buộc theo brief)** — tạo 1 override thật cho `MEAL_ALLOW`
(`component_id` lúc tạo: `bad6e748-6e36-41dc-a4b7-f9725d87f821`), **restart backend thật**
(`go run ./cmd/Core System`, log xác nhận `Database migrations completed successfully` rồi
`Server starting on :8080`), sau đó kiểm:
- `salary_components` không còn dòng nào có `id = bad6e748-...` (V4 đã reseed thật, sinh id mới).
- Dòng override **còn nguyên**, `component_code = 'MEAL_ALLOW'`, và `component_id` đã tự nối lại
  thành `242183c1-d632-41ab-9ef4-4ce6c4fbe13d` — đúng bằng id mới của `MEAL_ALLOW` sau reseed.

Đã dọn override nghiệm thu + 1 dòng rác rò ra từ vòng revert-để-chứng-minh (test cleanup cũ khớp
theo `component_code`, bản revert không ghi cột đó nên sót lại — đã sửa cleanup khớp thêm theo
`scope_ref` cho chắc). DB dev về lại `tc=0 sco=0` sau toàn bộ quá trình.

**Nợ có ý thức của phương án RE-LINK** (ghi để người sau không tưởng là bug — xem PLAN Task 0 mục
"Nợ có ý thức"):
1. `component_id` là cột **dẫn xuất/cache**, chỉ đúng sau khi migration BO chạy — an toàn vì
   `RunMigrations()` luôn chạy xong trước khi HTTP server bắt đầu phục vụ (`cmd/Core System/main.go`).
2. UNIQUE của `salary_component_overrides` vẫn khoá theo `component_id` (không đổi sang `code`) —
   re-link làm id hội tụ đúng nên tính duy nhất vẫn đúng; đổi khoá UNIQUE sẽ buộc sửa `ON CONFLICT`
   trong `Create`/`CreateTx`, phình phạm vi ngoài Task 0.
3. Component bị xoá **thật** (mã không còn tồn tại) → dòng con thành mồ côi: **không bị xoá** (tốt
   hơn hành vi CASCADE cũ) nhưng biến mất khỏi mọi read path vì `ListComponents`/`ListActiveForDate`
   đều JOIN `salary_components` — hành vi này đã được 2 test orphan ở trên khẳng định tường minh.

---

## 1. Báo cáo hiện tại thật sự là gì — hai thế hệ song song

Trước khi bàn "bảng cấu hình", cần đính chính một điểm trong ý 1: **hệ thống đã có nơi tạo ra báo cáo**,
chỉ là nó nằm hoàn toàn trong Go source chứ không phải trong DB.

### 1.1 Gen-1 — dựng workbook từ số 0 (2 báo cáo)

`internal/service/report_service.go` chỉ có hai generator: `GeneratePayrollSummary` (`:33`) và
`GenerateBankTransfer` (`:143`). Đây là **thế hệ duy nhất có cột động từ DB**: `GeneratePayrollSummary`
gọi `componentRepo.ListActive(ctx)` (`:44`) rồi lấy mọi component làm cột, giá trị đọc từ
`rec.ComputedValues`.

### 1.2 Gen-2 — 17 template `.xlsx` nhúng bằng `go:embed`

Dispatch trung tâm là `ExportReport` (`internal/service/report_export.go:25`), chọn generator bằng hai
lần tra map (`reportDefByCode` → `reportGeneratorRegistry`, `report_registry.go:63-92`), **không phải
`switch`**. Danh mục 17 báo cáo là slice hardcode `reportDefs` (`report_registry.go:71-89`); mỗi
generator là một file `report_gen_*.go` với một file `.xlsx` nhúng sẵn tại
`internal/service/templates/reports/`.

**17/17 báo cáo này KHÔNG hề gọi `componentRepo`.** Cột của chúng do file `.xlsx` quyết định, và mã
component được **hardcode trong Go**, rải rác 15 chỗ. Vài ví dụ:

| Nơi hardcode | Nội dung |
|---|---|
| `report_gen_chi_phi_pb_da.go:81-96` | `cpdColMap` — map chỉ số cột → mã component, 13 entry |
| `report_gen_bao_hiem.go:193-252` | ~20 lệnh `cv.Get("...")` cứng theo từng ô A..AP |
| `report_gen_so_lieu_ke_toan.go:99-111` | 7 bút toán TK ↔ 18 mã component |
| `report_gen_muc_luong.go:44` | `const mlSalaryCode = "GROSS"` |
| `report_gen_tang_ca.go:62-63` | `OT_TAX`, `OT_NONTAX` |

Đây chính là nỗi đau ý 1 muốn giải, và nó có thật.

### 1.3 Phân loại hai nhóm — điểm then chốt cho phạm vi khả thi

Câu "báo cáo về bản chất là tổng hợp theo từng cột của từng nhân viên rồi cộng lại" **đúng với đa số
nhưng không đúng với tất cả**:

**Nhóm 1 — một dòng mỗi nhân viên, cột là mã component (khoảng 13/20).** `GeneratePayrollSummary`,
`GenerateBankTransfer`, `muc-luong-hang-thang`, `bao-hiem`, `bank-tpbank`, `bank-khac`,
`phu-cap-thang`, `tang-ca`, `dieu-chinh-bo-sung`, `tach-cong-tv-ct`, `thuong-dot-xuat`,
`bao-viet-bhsk`, `pit-nam`, `gioi-thieu-ung-vien`. Nhóm này **cấu hình hoá được** một cách sạch sẽ.

**Nhóm 2 — hình dạng khác hẳn (khoảng 5/20).**
- `so-lieu-ke-toan`: không có dòng nào theo nhân viên; output là **11 ô số** tổng hợp toàn công ty,
  mỗi ô là một bút toán tài khoản = tổng của một tập mã component.
- `kinh-phi-doan-phi`: tương tự, vài ô tổng.
- `chi-phi-pb-da`: **pivot hai tầng** (Phòng ban × Dự án × Tháng × CC) và (Phòng ban × Tháng), hai
  sheet, và **nhân tiền với `AllocRatio` lấy từ `attendance_computed`** — tức join một nguồn ngoài
  `payroll_records`.
- `phan-bo-gdda`: group theo nhân viên × org/WBS, cũng dùng `AllocRatio`.
- `trich-thuong-luy-ke`: mỗi Phòng ban/Công trình một dòng, lũy kế 12 tháng của năm tài chính.

Nhóm 2 cần khái niệm **group-by key**, **hàm tổng hợp**, và **nguồn dữ liệu ngoài payroll_records**.
Một bảng cấu hình v1 phủ được Nhóm 1 là thắng lợi thật; hứa phủ luôn Nhóm 2 là hứa quá.

### 1.4 Chưa có endpoint preview — và đây là cơ hội

Toàn bộ route báo cáo là **tải file**, không có JSON preview nào
(`internal/transport/http/report/routes.go:16-25`: `Core System-summary`, `bank-transfer`, `catalog`,
`raw-export`, `{code}/export`). Cái mà UI gọi là "preview" thực chất là: gọi
`POST /reports/{code}/export` lấy Blob `.xlsx`, rồi **parse lại ở trình duyệt** bằng `exceljs`
(`report-preview.ts:73` `parseReportBlob`, dynamic import) để dựng `PreviewGrid`.

Với báo cáo cấu hình-hoá, ta **không cần đi vòng đó**: backend trả JSON rows thẳng, FE dựng
`PreviewGrid` trực tiếp. Nhanh hơn, ít phụ thuộc hơn, và bỏ được cả bước đoán header
(`HEADER_KEYWORDS`, `report-preview.ts:22`).

---

## 2. Ý 1 — bảng cấu hình template báo cáo: phạm vi nào là thật

Đề xuất phạm vi v1, đủ để có giá trị ngay mà không hứa quá:

Một template báo cáo v1 = **chọn tập cột (theo mã component) + chọn tập dòng (nhân viên, có bộ lọc) +
tuỳ chọn nhóm và dòng tổng**. Cụ thể cấu hình được:

- Cột định danh nào hiện (mã NV, họ tên, phòng ban, chức vụ, cấp bậc, công ty, ngày vào/ra…).
- Cột giá trị: danh sách mã component theo thứ tự, mỗi cột có nhãn hiển thị riêng (không buộc dùng
  `name` của component) và định dạng (tiền/số/ngày).
- Cột dẫn xuất đơn giản: tổng của nhiều mã (ví dụ `AH = TOTAL_INS + TOTAL_INS_CTY` mà `bao-hiem` đang
  hardcode ở `report_gen_bao_hiem.go:256`).
- Bộ lọc dòng: theo công ty, phòng ban, trạng thái record, và điều kiện đơn giản trên một mã
  (ví dụ `NET_PAY > 0` mà `GenerateBankTransfer` đang hardcode ở `report_service.go:164`).
- Sắp xếp, nhóm theo một khoá (phòng ban/công ty) và dòng tổng cuối bảng hoặc cuối nhóm.

**Nằm ngoài v1, cần nói rõ với người dùng:** pivot nhiều tầng, phân bổ theo `AllocRatio`, đa sheet, và
báo cáo đọc nguồn ngoài `payroll_records`. Năm báo cáo Nhóm 2 vẫn giữ generator Go như hiện tại.

Một điểm cần chốt: 17 template `.xlsx` nhúng có định dạng rất giàu (merge, numFmt, công thức
`SUBTOTAL`, block tổng do HR tự điền). Cấu hình-hoá **không** tái tạo được các file đó pixel-perfect.
Nên v1 nên nhắm vào **báo cáo mới do HR tự định nghĩa**, không nhắm vào việc thay thế 17 báo cáo cũ.

---

## 3. Ý 2 — tái dùng bảng rule + thêm `type`: phân tích và khuyến nghị

Ý này có hạt nhân đúng: payslip và report đều cần khái niệm "dòng này lấy số từ đâu", nên đáng chia sẻ
một mô hình. Nhưng "tái dùng **bảng** `salary_components`" thì có bốn vấn đề, ngoài vấn đề phù du ở
mục 0.

**(a) Engine sẽ tính rule báo cáo cho từng nhân viên.** `buildOrder` sắp thứ tự topo trên **toàn bộ**
component, `computeEmployee` chạy cho **mọi** nhân viên (12.044 người). Rule chỉ dùng để in báo cáo
tổng hợp sẽ bị tính 12k lần và ghi vào `payroll_records.computed_values` của từng người.

**(b) Năm đường đọc hiện tại không có bộ lọc nào, nên rule báo cáo sẽ rò khắp nơi.**
`componentRepo.ListActive` (`salary_component_repo.go:22-27`) — **tên gọi sai bản chất, nó
`SELECT *` không `WHERE` gì cả** — được dùng bởi lưới bảng lương, bởi `GeneratePayrollSummary`
(`report_service.go:44`), và bởi `report_service.go` nói chung; `ListVisible` (`:77`) được `raw-export`
dùng; và `maskableUniverse` của tính năng cấu trúc lương cũng đi từ tập component. Thêm dòng loại mới
vào bảng này mà không sửa **tất cả** các đường đọc đó thì rule báo cáo sẽ hiện thành cột trong bảng
lương và trong báo cáo tổng hợp.

**(c) `component_type` lạ sẽ ra 0 im lặng.** `engine.go` phân nhánh `ct == "formula" || ct == "bracket"`
(`:89`) và `case "input", "config", "manual"` (`:158`), `case "formula"` (`:175`). Một type mới không
được xử lý sẽ rơi vào nhánh mặc định và cho 0 mà không báo lỗi — đúng chế độ hỏng mà tài liệu dự án
này đã cảnh báo nhiều lần.

**(d) Rule báo cáo không cùng "hình" với rule lương.** Rule lương là *một số cho một nhân viên*. Rule
báo cáo/payslip là *một dòng trong bố cục*: có nhãn hiển thị, thứ tự, cấp độ thụt lề, có thể là tổng
của nhiều mã, có thể là group-by. Nhồi hai hình này vào một bảng sẽ sinh ra một loạt cột chỉ có nghĩa
với một nửa số dòng.

**Khuyến nghị:** giữ đúng *tinh thần* ý 2 nhưng dịch sang tầng khác — **tái dùng bằng cách tham chiếu
theo `component_code`, không phải bằng cách ở chung bảng**. Cụ thể: một bảng dòng-bố-cục riêng, có
đúng cái `type` mà người dùng muốn (`doc_type ∈ {report, payslip}`), và mỗi dòng trỏ tới một hoặc
nhiều `component_code`. Như vậy:

- `salary_components` giữ nguyên vai trò duy nhất: *một con số được tính thế nào cho một nhân viên*.
- Payslip và report dùng chung một mô hình dòng, phân biệt bằng `doc_type` — đúng ý người dùng.
- Không rò vào engine, không rò vào lưới lương, không bị V4 xoá.

Nếu người dùng vẫn muốn dùng chung một bảng, thì điều kiện tối thiểu là: sửa mục 0 trước (để bảng
không còn phù du), thêm cột phân loại `NOT NULL DEFAULT`, và sửa **cả năm** đường đọc ở điểm (b) —
mỗi đường bỏ sót là một chỗ rule báo cáo hiện nhầm thành cột lương.

---

## 4. Ý 3 — bảng mới hay tái dùng bảng có sẵn

Đã soi từng ứng viên trong DB thật.

| Ứng viên | Thực trạng | Kết luận |
|---|---|---|
| `payroll_templates` + `template_components` | Tên nghe khớp, nhưng ngữ nghĩa là "cấu trúc lương theo cấp bậc" (tính năng riêng, đang HOLD). `payroll_templates` không có cột phân loại. `template_components` **bị CASCADE xoá mỗi restart**. | **Không tái dùng.** Sẽ gộp hai tính năng khác nhau vào một bảng và thừa hưởng luôn khuyết tật. |
| `salary_formula_configs` (18 dòng) | Cột `scope_type/scope_id/component_code/override_type/formula/fixed_value` — trông giống bảng cấu hình. Nhưng **không một dòng Go nào đọc nó**: grep toàn repo chỉ ra `database.go:1213` (CREATE), `:1290` (DELETE), `:1295` (INSERT seed). **15/18 dòng trỏ mã component không tồn tại**. | **Bảng chết, di sản của một lần thử trước.** Không tái dùng, nhưng là bài học đáng ghi: một bảng cấu hình được migration seed mà không có code nào đọc sẽ mục ra đúng như vậy. |
| `hris_payroll_reports` (0 dòng) | Cột `employee_code/payroll_month/raw_data jsonb` — là bảng **hạ cánh dữ liệu HRIS**, không phải cấu hình báo cáo. **Không có tham chiếu Go nào.** | Không liên quan. |

**Không có bảng nào lưu cấu hình báo cáo.** Grep `report_template`, `report_config`,
`report_definition`, `report_column`, `doc_version`, `payroll_doc` toàn repo: **0 kết quả**.

**Đề xuất: tạo mới, hai bảng.**

- Một bảng **header** — mỗi dòng là một template báo cáo đã cấu hình: mã, tên, `doc_type`
  (`report`/`payslip` — chỗ đặt cái `type` của ý 2), loại kỳ (tháng/năm/khoảng), phạm vi công ty,
  tuỳ chọn nhóm/tổng, trạng thái bật-tắt, người tạo, thời điểm.
- Một bảng **dòng/cột** — mỗi dòng là một cột (hoặc một dòng bố cục với payslip): thứ tự, nhãn hiển
  thị, loại nguồn (`identity` = field nhân viên / `component` = một mã / `sum` = tổng nhiều mã /
  `expr` = biểu thức), giá trị nguồn (`component_code` hoặc danh sách mã), hàm tổng hợp, định dạng.

Hai ràng buộc bắt buộc, rút từ mục 0: **khoá theo `component_code` varchar**, và **định nghĩa bảng đặt
trong `RunMigrations()`** (`database.go`) chứ không phải `atlas/migrations/` — vì backend **không bao
giờ chạy Atlas** (`cmd/Core System/main.go` chỉ gọi `RunMigrations` + `RunFileMigrations`).

Câu hỏi mở cần người dùng chốt: có gộp payslip vào cùng cặp bảng này ngay từ đầu (một `doc_type`), hay
làm report trước rồi mở rộng sau. Gộp ngay thì mô hình phải chịu cả hai hình dạng; làm sau thì rủi ro
phải đổi schema.

---

## 5. Ý 4 — selection box trên sheet Báo cáo

Khảo sát FE cho thấy ý này rẻ hơn dự kiến, và có một cái móc đã nằm sẵn.

**Xác nhận các nút hiện tại đúng là bỏ qua được.** Trong `ReportsRibbon.tsx`: "Lọc ▾" (`:73`) và
"Sắp xếp ▾" (`:74`) **không có `onClick`**, chỉ có `title="… (chưa hỗ trợ)"`. "Trường báo cáo"
(`:82-86`) gọi `onToggleFieldsPanel` nhưng gated bởi `canToggleFields = isReport && !!sheet.repKey &&
!!sheet.generated` (`TinhLuongExcel.tsx:3443`), mà `repKey` là **đường legacy không còn tạo mới**
(ghi chú `:118`) → nút đó thực tế luôn tắt. Thêm một control mới **không đụng** ba nút này.

**Móc có sẵn:** state `reportCompany` (`TinhLuongExcel.tsx:576`) được **ĐỌC** ở hai chỗ (`:985` lọc
bảng chấm công, `:2232` chọn công ty chạy báo cáo) nhưng **không chỗ nào SET** — comment `:983` nói
"dropdown Công ty trên ribbon" mà dropdown đó chưa từng tồn tại. Tức là đã có tiền lệ và chỗ cắm.

**Vị trí chèn an toàn:** thêm một prop vào `ReportsRibbonProps` (`:15-22`) rồi chèn một nhóm JSX giữa
`{commonControls}` (`:34`) và `{reportGroups.map(...)}` (`:35`), hoặc sau khối "Bộ lọc" (`:78`).

**Đường render kết quả:** không cần component bảng mới. Cơ chế generic đã có là cặp `PreviewGrid`
(`report-preview.ts:13-18` — `{sheetName, columns:{label,w}[], rows: string[][], truncated}`) và
`buildPreviewView(...)` (`TinhLuongExcel.tsx:2553`). Có sẵn cả helper `cfgGrid(sheetName, defs, rows)`
(`:77-95`) biến mảng object bất kỳ thành `PreviewGrid`, và tiền lệ dựng `PreviewGrid` **thủ công**
hoàn toàn không qua `.xlsx` ở sheet "Ma trận theo User" (`:1859-1871`). Nên luồng đề xuất là: chọn
template → gọi endpoint mới trả **JSON** → `cfgGrid` → `buildPreviewView`. Bỏ hẳn vòng
export-`.xlsx`-rồi-parse-`exceljs` mà luồng báo cáo hiện tại đang dùng.

---

## 6. Ý 5 — nơi cấu hình nằm trong sheet Cấu hình

Khớp hoàn toàn với kiến trúc hiện có, và **sheet Cấu hình không phải danh sách link sang `/admin`**
như có thể tưởng: trong 14 mục của `settingsListItems()` (`TinhLuongExcel.tsx:2032-2049`), **13 mục mở
sheet nhúng ngay trong lưới**, chỉ đúng một mục ("Đồng bộ") điều hướng ra `/admin?tab=sync` (`:1568`).

Thêm mục mới gồm ba việc:

1. Thêm một dòng vào `settingsListItems()` — ví dụ
   `{ name: "Template báo cáo", group: "Danh mục", action: openReportTemplatesSheet }`. Hàm này đọc
   sống mỗi lần render nên dòng mới xuất hiện ngay, không cần snapshot.
2. Viết `openReportTemplatesSheet()` theo một trong hai khuôn có sẵn:
   - **Khuôn `openConfigSheet`** (`:1575-1637`) + một entry trong `CONFIG_SOURCES` (`:97-110`): ít code
     nhất, dùng chung loading/error, phù hợp nếu chỉ cần xem danh sách.
   - **Khuôn `FORMULAS_LIST_SHEET_ID`** (sheet "Danh sách cột lương", render ở `:2648-2662`): đọc thẳng
     từ state mỗi render (cố ý không dùng `sheet.preview` để list cập nhật ngay sau Thêm/Sửa/Xoá), có
     sửa-tại-chỗ trên ô, có `rowActions` xoá, có modal thêm. **Đây là khuôn đúng** cho việc cấu hình
     template vì cần CRUD thật.
3. Modal thêm/sửa template + các dòng của nó, theo khuôn `SalaryComponentModal` (`:4153`).

Hai chi tiết dễ quên: sheet id mới cần được thêm vào danh sách loại trừ của empty-hint (`:4514`), và
nếu muốn nó thuộc tab Cấu hình thì mapping tab ở `:3432` đã tự lo (mặc định về `"data"`).

---

## 7. Những gì cần người dùng chốt

1. **Xử lý mục 0 trước hay song song?** Rule/cấu hình mới không thể bền nếu `salary_components` còn bị
   `DELETE` mỗi boot; và tính năng override đang chạy thật cũng đang mất dữ liệu mỗi restart. Đây là
   việc nền, ảnh hưởng cả tính năng cấu trúc lương đang HOLD.
2. **Ý 2 — chấp nhận khuyến nghị "tái dùng bằng tham chiếu theo `component_code`, bảng dòng-bố-cục
   riêng"**, hay vẫn muốn thêm `type` vào chính `salary_components`?
3. **Phạm vi v1 của báo cáo cấu hình-hoá**: chỉ Nhóm 1 (một dòng mỗi nhân viên + nhóm + tổng), hay
   phải phủ luôn Nhóm 2 (pivot/`AllocRatio`/đa sheet)?
4. **Có gộp payslip vào cùng cặp bảng ngay từ đầu** (một `doc_type`) hay làm report trước?
5. **Báo cáo cấu hình-hoá trả JSON** (khuyến nghị, dựng `PreviewGrid` trực tiếp) hay vẫn sinh `.xlsx`
   rồi parse như luồng hiện tại (để dùng lại đường tải file)?
6. 17 báo cáo `.xlsx` nhúng hiện tại: **giữ nguyên song song** (khuyến nghị) hay có ý định dần chuyển
   sang cấu hình?

---

## 8. Trả lời câu hỏi "có dùng được chính các code/formula như payslip không?" (040826, lượt 2)

Người dùng chốt bốn điểm: **sửa mục 0 trước** (việc nền chặn cả ba tính năng), **phạm vi v1 chỉ Nhóm 1**,
**schema có `doc_type` ngay nhưng v1 chỉ thi hành report**, và với ý 2 thì hỏi ngược: nếu dùng bảng
dòng-bố-cục riêng trỏ `component_code` thì *có dùng được chính những code/formula mà payslip đang dùng
không*.

### 8.1 Câu trả lời: được, vì hai bên VỐN ĐÃ dùng chung một không gian mã

Kiểm code thật, payslip và báo cáo lấy số theo đúng một cách:

| | Payslip | Báo cáo (Gen-1) |
|---|---|---|
| Danh sách mã | `components: SalaryComponent[]`, lọc `c.isVisible`, sort `seq` (`PayslipSummaryModal.tsx:32-34`) | `componentRepo.ListActive(ctx)` (`report_service.go:44`) |
| Lấy giá trị | `row.values[code]` (`:41-42`) | `row.Values.Get(vc.Code)` (`report_service.go:118`) |
| Nguồn thật | `payroll_records.computed_values` | `payroll_records.computed_values` |

Nên một bảng dòng-bố-cục trỏ `component_code` phục vụ được **cả hai** mà **không cần khái niệm formula
mới nào**: cả payslip lẫn report đều chỉ là "chọn mã + đọc giá trị theo mã".

Cần phân biệt rạch ròi hai thứ dễ lẫn:

- **Dùng lại `code`** — được, và nên. Đó chính là điểm gắn kết giữa payslip, báo cáo và engine.
- **Dùng lại `formula`** — không cần, và không nên tạo component mới chỉ để phục vụ báo cáo. Công thức
  nằm ở `salary_components.formula` và được engine tính **cho từng nhân viên**; nếu báo cáo cần một con
  số dẫn xuất (ví dụ `TOTAL_INS + TOTAL_INS_CTY` mà `bao-hiem` đang hardcode ở
  `report_gen_bao_hiem.go:256`), hãy làm nó ở **tầng bố cục** (loại dòng `sum` của nhiều mã) chứ đừng
  thêm một component mới: component mới sẽ bị V4 xoá (mục 0) **và** khiến engine tính thêm một cột cho
  cả 12.044 nhân viên.

### 8.2 Ba thứ KHÔNG dùng chung được và phải khai tường minh trên dòng bố cục

1. **Vai của dòng** (thu nhập / khấu trừ / chi phí công ty / tổng / thông tin). Đây là chỗ đắt giá
   nhất — xem 8.3.
2. **Chiều trình bày.** Payslip là các dòng dọc, một nhân viên một trang; báo cáo là các cột ngang, một
   dòng một nhân viên. Cùng một tập định nghĩa dòng, hai cách render — đúng việc mà `doc_type` giải.
3. **Nhãn hiển thị.** Payslip thường cần nhãn khác `salary_components.name`. Nên `label` phải nằm trên
   dòng bố cục, không lấy cứng từ component.

### 8.3 Phát hiện: payslip hiện phân loại thu nhập/khấu trừ bằng ĐOÁN CHUỖI, và đoán sai 21 mã

`PayslipSummaryModal.tsx:19-24` phân loại bằng cách tìm chuỗi con trong mã:

```ts
const DEDUCTION_KEYWORDS = ["bhxh","bhyt","bhtn","pit","thue","khau_tru","deduct","ins_emp","si_emp","hi_emp","ui_emp"];
function isDeduction(code: string) { return DEDUCTION_KEYWORDS.some(k => code.toLowerCase().includes(k)); }
```

Đối chiếu với **102 mã `is_visible` thật** trong DB: chỉ **9 mã** được nhận là khấu trừ
(`SI_EMP`, `HI_EMP`, `UI_EMP`, `PIT`, `PIT_ADJ`, `TOTAL_PIT`, `PIT_SETTLE`, `DEDUCT_LOC`,
`PIT_SETTLE_DED`). **21 mã rõ ràng không phải thu nhập của nhân viên nhưng đang bị xếp vào cột THU
NHẬP**:

- Khấu trừ/giảm trừ bị tính thành thu nhập: `TOTAL_INS`, `TOTAL_DED`, `TOTAL_POST_DED`,
  `OTHER_POST_DED`, `ADVANCE_1` (tạm ứng), `CHARITY_DED`, `PERSONAL_DED`, `DEPENDENT_DED`,
  `SEVER_FUND`, `UNION_FEE`.
- **Chi phí phía công ty, đúng ra không nên xuất hiện trên phiếu lương của nhân viên**:
  `SI_CTY`, `SI_CTY_ADJ`, `HI_CTY`, `HI_CTY_ADJ`, `UI_CTY`, `UI_CTY_ADJ`, `TNLD_CTY`,
  `TNLD_CTY_ADJ`, `KPCD_CTY`, `TOTAL_INS_CTY`, `TOTAL_CTY_COST`.

Nguyên nhân là khớp chuỗi không bao giờ khớp được ngữ nghĩa: từ khoá `"si_emp"` không khớp `SI_CTY`,
`"deduct"` không khớp `_DED`, và `TOTAL_INS` không chứa từ khoá nào. Modal này **đang được dùng thật**
(`components-page/Core System/PayrollPage/PayrollPage.tsx:2876`).

Điều này biến ý 2 của người dùng từ "một cách tổ chức code gọn hơn" thành **bản sửa cho một lỗi số
liệu đang tồn tại**: khi mỗi dòng bố cục khai tường minh `role`, phiếu lương thôi phải đoán, và cùng
một khai báo đó cho báo cáo biết dòng nào được cộng vào dòng tổng nào.

*(Chưa sửa — thuộc phạm vi hạng mục này, ghi lại để không thất lạc.)*

### 8.4 Chốt lại mô hình sau lượt 2

Một cặp bảng mới, khoá theo `component_code`, đặt trong `RunMigrations()`:

- **Header**: mã, tên, `doc_type` (`report` | `payslip` — có sẵn từ đầu, v1 chỉ thi hành `report`),
  loại kỳ, phạm vi công ty, tuỳ chọn nhóm/tổng, bật-tắt, người tạo/thời điểm.
- **Dòng**: thứ tự, `label`, `role` (`earning`|`deduction`|`employer_cost`|`total`|`info`),
  `source_kind` (`identity`|`component`|`sum`|`expr`), giá trị nguồn (`component_code` hoặc danh sách
  mã), định dạng.

`role` phục vụ cả hai phía: payslip dùng để chia khối thu nhập/khấu trừ (thay cho đoán chuỗi), báo cáo
dùng để biết cột nào cộng vào dòng tổng.

---

## 9. Quan hệ với PLAN template — dùng lại phân tích này ở đâu (040826, lượt 3)

Người dùng hỏi phân tích này có dùng được trong `llmwiki/wiki/sources/draft/040826-Core System-template-on-giatbh-engine-PLAN.md` không. Trả lời: **có, ở đúng ba chỗ — nhưng không gộp hai hạng mục vào một file.**

Lý do không gộp: PLAN kia có danh tính là "mở lại tính năng Cấu trúc lương theo cấp bậc"; báo cáo là
hạng mục riêng với phạm vi riêng. Gộp vào sẽ tạo ra một file làm hai việc, trái đúng quy ước
"không tạo nhiều file rời rạc cho cùng một hạng mục" hiểu theo cả hai chiều. Báo cáo sẽ có PLAN riêng.

Nhưng hai hạng mục **dùng chung đúng một cái nền**, nên phân tích này đã được đưa vào PLAN kia:

1. **Task 0 mở rộng từ MỘT bảng thành HAI.** Bản PLAN viết lúc chưa biết `salary_component_overrides`
   cũng bị cùng CASCADE đó. Nay Task 0 gồm Phần A (`template_components`, bước 1-8) và **Phần B
   (`salary_component_overrides`, bước 9-12)** trong cùng một migration. Đây là chỗ sửa quan trọng
   nhất: nếu chỉ vá `template_components` thì ta để nguyên lỗi **nặng hơn** — bảng override đang gây
   sai tiền im lặng ngay bây giờ, còn `template_components` thì chỉ làm một tính năng đang tắt không
   chạy được.
2. **G1 được bổ sung bằng chứng đo được** (4 ms `created_at`, 11/11 history mồ côi, 13 mã v51 đã mất,
   15/18 dòng `salary_formula_configs` mồ côi) để người thi hành không phải đo lại từ đầu.
3. **Thêm ràng buộc G5 — không đổi semantics V4 trong phạm vi PLAN đó.** Mục 0 của tài liệu này tách
   được hai vấn đề: (a) CASCADE xoá bảng con, (b) component do người dùng tạo bị xoá. PLAN chỉ đóng
   (a). Đóng (b) là một quyết định thật chưa chốt, và nếu không ghi ràng buộc này thì một phiên sau rất
   dễ "sửa luôn cho gọn" rồi phá cả chuỗi self-heal BF→BN của `giatbh`.

### 9.1 Thứ tự thi hành đã chốt sau lượt 3

| # | Việc | Trạng thái |
|---|---|---|
| F1 | Task 0 của PLAN template (nay gồm cả `salary_component_overrides`) | **làm trước** — không cần quyết định nào, và là chỗ duy nhất đang gây hại thật |
| F2 | Task 1 của PLAN template (`employee_payroll_templates` vào `RunMigrations()`) | làm ngay sau F1 |
| B | Báo cáo cấu hình-hoá v1 (Nhóm 1) — PLAN riêng, chưa viết | sau F1+F2; phạm vi đã chốt, không còn quyết định treo |
| A | Task 2/3/4/5/6 của PLAN template | còn treo 2 quyết định (mô hình gán, ngày hiệu lực) |
| — | Đổi semantics V4 sang UPSERT | hoãn có ý thức (G5); **không chặn báo cáo v1** vì bảng báo cáo khoá theo `code` nên miễn nhiễm sẵn |

Ghi rõ để phiên sau không nhầm: **báo cáo v1 không cần V4 được sửa.** Dòng bố cục chỉ tham chiếu mã
component **đã tồn tại**; chỉ khi nào HR cần tự tạo cột lương mới và giữ được nó thì (b) mới thành điều
kiện chặn.

### 0.5 Kiểm chứng độc lập Task 0 (050826) — đạt, kèm 2 đính chính và 1 phát hiện mới

Phiên khác thi hành Task 0 và báo hoàn tất. Phiên này kiểm lại bằng lệnh thật, **không tin báo cáo**.

**ĐẠT — 4 khẳng định cốt lõi đều đúng chính xác:**

| Kiểm gì | Kết quả |
|---|---|
| Commit `036cd67` trên `feature_v2`, chưa push | Đúng. Diff **5 file / +330 −6**: `database.go` (+44), 2 repo, 2 file test. **Không đụng** handler/service/route/frontend/e2e — khớp đúng ràng buộc đã chốt |
| 2 FK CASCADE đã bị bỏ | Đúng. `pg_constraint` xác nhận `template_components` chỉ còn `..._template_id_fkey`; `salary_component_overrides` **không còn FK nào**. Bảng duy nhất còn FK vào `salary_components(id)` là `salary_component_history` (`ON DELETE SET NULL` — vô hại) |
| Cột + index mới | Đúng: `component_code varchar(50)` trên cả 2 bảng, `idx_tc_component_code`, `idx_sco_component_code` |
| Đường GHI đã điền `component_code` (bẫy số 1 của brief) | Đúng cả 3 câu INSERT — `payroll_template_repo.go:94`, `salary_component_override_repo.go:82` và `:111`, đều dùng `(SELECT code FROM salary_components WHERE id = $2)`; `ON CONFLICT` giữ nguyên như yêu cầu |
| Const exported + đặt cuối slice | Đúng: `MigrationDurableComponentCode` khai ở `database.go:3125`, wired ở `:294` (sau `:285` = phần tử cuối cũ) |

**ĐÍNH CHÍNH 1 — con số baseline test không phải 24.** Đo lại bằng cách chạy full suite ở **cả hai**
commit (dựng `git worktree` tại `HEAD~1`):

| | Số case fail |
|---|---|
| `HEAD~1` (trước Task 0) | **7** |
| `HEAD` (`036cd67`) | **8** |

Chênh đúng 1: `TestIntegrationComputeFormulaImpactComputesDeltaWithoutWriting`. **Không phải hồi quy** —
chạy cách ly ở HEAD thì **pass 3/3**. Lỗi thật là `payroll_records đổi từ 6435 thành 6436`, tức test này
khẳng định một **số đếm TOÀN CỤC** của `payroll_records` không đổi, trong khi Go chạy các package test
**song song** trên **cùng một DB dev**; một test ở package khác gọi `Calculate` (log
`[Calculate] Processing 1/1: empCode=000001`) đã ghi 1 dòng vào đúng lúc. Task 0 thêm 4 test ở
`internal/repository` → đổi thời điểm → làm cú đụng này dễ xảy ra hơn.

⇒ Kết luận: **code của Task 0 sạch, không hồi quy.** Nhưng có một **nợ mới về hạ tầng test**: một test
đang khẳng định số đếm toàn cục trên DB dùng chung — nó sẽ còn fail ngẫu nhiên. Cách sửa đúng là đổi
assert sang phạm vi hẹp (đếm theo `period_id` của chính test) chứ không phải `-p 1` cho cả repo.

**ĐÍNH CHÍNH 2 — danh sách baseline trong `HANDOVER-giatbh.md` mục 3 thiếu 1 test.** Tài liệu đó liệt
kê 6 test fail sẵn; đo thật ở `HEAD~1` là **7**. Test thiếu là
`TestIntegrationCalculateOnePointInTimeFormula`, và nó fail **tất định** (2/2 khi chạy cách ly) ở **cả
hai** commit → không liên quan Task 0.

**PHÁT HIỆN MỚI (L11) — tính năng versioning hiệu-lực-theo-ngày của `giatbh` đang VÔ HIỆU trên DB này,
cùng một gốc nguyên nhân với L4.**

Lỗi của test trên nói thẳng ra: `TASK-REF fail: ListActiveAsOf(kỳ CŨ) sau khi sửa = "1", muốn vẫn "0"
(kỳ cũ không được đổi theo)`. Truy nguyên:

- `salary_component_versions` **tồn tại nhưng 0 dòng** (`select count(*)` = 0).
- `ListActiveAsOf` (`salary_component_repo.go`) là **COALESCE 3 tầng**:
  `COALESCE(ver.formula, earliest.formula, sc.formula)` — tầng 1 = version hiệu lực tại ngày, tầng 2 =
  version sớm nhất, **tầng 3 = `sc.formula` tức công thức HIỆN TẠI**.
- Bảng rỗng ⇒ tầng 1 và 2 luôn NULL ⇒ **luôn rơi về tầng 3**. Nghĩa là `ListActiveAsOf(bất kỳ ngày nào)`
  trả về công thức của **hôm nay** cho **mọi kỳ**.
- Vì sao rỗng: `database.go` chỉ có `CREATE TABLE IF NOT EXISTS` (const
  `migrationSalaryComponentVersionsTable`), **không có `INSERT` nào**. Backfill nằm **duy nhất** ở
  `atlas/migrations/20260803000000_salary_component_versions.sql:26` và
  `20260803020000_salary_component_versions_fix_key.sql:28` — mà **backend không bao giờ chạy Atlas**.

⇒ Đóng góp lớn nhất của nhánh `giatbh` (mục J bàn giao: *"trước đây sửa 1 formula hôm nay sẽ tính lại
luôn cả các kỳ QUÁ KHỨ theo formula mới (sai)"*) hiện **chưa có tác dụng** — đúng cái bug nó được xây để
diệt vẫn còn nguyên. Đây **không phải** lỗi logic của họ; là lỗi cùng họ L4: việc bootstrap đặt sai chỗ
(Atlas thay vì `RunMigrations()`).

**Hệ quả trực tiếp lên tài liệu của chính tôi:** `Salary-Structure-Template-Analysis-260726.md` mục 15.4
ghi rằng mask "tương thích, và tốt lên — closure phụ thuộc giờ được tính trên công thức đúng của kỳ".
Câu đó **đúng về thiết kế nhưng sai về thực tế hiện tại**: vì `ListActiveAsOf` đang inert, closure được
tính trên công thức HÔM NAY. Đã ghi đính chính vào mục 15.4.

**Hệ quả lên Task 1:** Task 1 vốn chỉ nhắm `employee_payroll_templates`. Nay đã có **hai nạn nhân** của
cùng một gốc — nên Task 1 phải xử lý cả backfill `salary_component_versions`, hoặc tối thiểu brief phải
nêu để người thi hành không bỏ sót.

**Đã tách thành hạng mục riêng (050826):** phân tích đầy đủ cơ chế 3 tầng, bảng diễn biến từng ca, quyết định `effective_from = now()` (chân trời lịch sử) và 4 bẫy thi hành nằm ở **`self-docs/Formula-Versioning-PointInTime-050826.md`** — mục 0.5 này chỉ giữ phần *phát hiện*, không lặp lại nội dung đó.

### 0.6 Kết quả thi hành Task 1 (050826-F1) — đã xong, cả 2 nạn nhân cùng gốc

Thi hành đúng theo PLAN Task 1 trên `Core System-backend@feature_v2` (sau commit Task 0 `036cd67`).
Đóng **L4** (`employee_payroll_templates` chỉ có trong Atlas) và **L11** (`salary_component_versions`
rỗng, versioning vô hiệu) trong cùng một task vì cùng một gốc: bootstrap đặt sai chỗ.

**Baseline đo lại tại thời điểm này** (không chép con số 7/8/24 của các phiên trước — tự đo): sau
commit Task 0, chạy `go run ./cmd/Core System` để nghiệm thu (dòng nhật ký 050826 trước) đã vô tình tạo
bảng `salary_component_versions` lần đầu như một hiệu ứng phụ, làm 16/24 fail cũ (đều là lỗi
`relation "salary_component_versions" does not exist`) tự biến mất. Baseline thật trước Task 1: **8
fail**. Danh sách khớp đúng đính chính 0.5 ở trên (7 case cũ + `TestIntegrationCalculateOnePointInTimeFormula`
không nằm trong 6 test `HANDOVER-giatbh.md` liệt kê).

**Bước 1 — grep xác nhận trước khi sửa:** `grep -c employee_payroll_templates database.go
schema.sql` = `0`/`0`; `main.go` chỉ gọi `RunMigrations`+`RunFileMigrations`, không có Atlas — khớp
đúng kỳ vọng brief.

**Bước 2 — `MigrationEmployeePayrollTemplatesTable` (mốc BP):** chép nguyên schema từ
`atlas/migrations/20260726000000_*.sql` (đã idempotent sẵn — `IF NOT EXISTS` cả bảng lẫn 3 index) —
**chủ ý bỏ `COMMENT ON TABLE`** ở cuối vì nội dung lỗi thời ("Task 4 chưa làm — chờ Approach A1",
trong khi Task 4 xong từ 270726 — chép nguyên sẽ đưa một câu sai vào DB).

**Bước 3 — fail-loud cho lỗi hạ tầng:** thêm `PayrollTemplateRepo.Ping` (phân biệt bảng thật-không-tồn-tại
SQLSTATE `42P01` với `sql.ErrNoRows` bình thường), `isUndefinedTableError` (dùng `pq.Error`), và
`PayrollService.TemplateEnforceHealth(ctx) (enabled, healthy, reason)` — enforce đang bật mà bảng
thiếu thì `slog.Error` (fail-loud) nhưng `Calculate` vẫn tiếp tục fail-safe (TASK-REF, không sập tính
lương vì tính năng phụ), đúng khuyến nghị brief. Handler `GET /Core System/template-enforce-status` đổi
từ `map[string]bool` sang `map[string]any`, thêm `healthy`/`reason` — **không phá FE cũ** (chỉ đọc
`.enabled`, field mới chỉ cộng thêm).

**Bước 4 — test:** `TestTemplateEnforceStatus_ReportsUnhealthyWhenTableMissing` (rename bảng thật
trong test, không dùng transaction vì `Ping()` đọc qua `*sqlx.DB` có thể lấy connection khác trong
pool không thấy DDL chưa commit — rename thật rồi rename lại ngay, `t.Cleanup` đảm bảo phục hồi kể cả
khi assert fail giữa chừng) + `TestTemplateEnforceStatus_HealthyWhenDisabledRegardlessOfTable`. Cả 2
xanh, xác nhận bảng thật còn nguyên sau test.

**Bước 5 — backfill `salary_component_versions` (mốc BQ), đặt cuối slice sau BO:** guard
`WHERE NOT EXISTS` (bảng không có unique constraint trên `component_code` nên `ON CONFLICT` không
dùng được), `effective_from = now()` (đã chốt bởi người dùng 050826), **không** chép nguyên file Atlas
`fix_key.sql` (không guard + dùng `sc.created_at` nói dối tuổi component vì bị V4 xoá/chèn lại mỗi
boot). Preview bằng `BEGIN;...ROLLBACK;` trước — 126 dòng, 1 mốc chân trời duy nhất — rồi áp thật vào
`payroll_engine` sau khi xác nhận qua `AskUserQuestion`. Chạy lại lần 2: `INSERT 0 0`, `count(*)` vẫn
126 — idempotent xác nhận. `TestIntegrationCalculateOnePointInTimeFormula` chạy cách ly: **chuyển
xanh** — đúng nghiệm thu tự nhiên của bước này.

**Bước 6 — verify cuối:** `gofmt -l` không thêm gì mới ngoài `database.go` (drift pre-existing từ
trước, đã xác nhận qua `git stash` ở Task 0); `go build`/`go vet` sạch. `go test ./...` sau sửa: **7
fail**, khớp đúng baseline 8 trừ đi 1 (`TestIntegrationCalculateOnePointInTimeFormula`) — không có fail
mới, không hồi quy.

**Nghiệm thu ở tầng thật (Phần A):** start backend thật với `PAYROLL_TEMPLATE_ENFORCE=on` —
`GET /Core System/template-enforce-status` trả `{"enabled":true,"healthy":true}`. Đổi tên bảng thật
`employee_payroll_templates` → gọi lại: `{"enabled":true,"healthy":false,"reason":"bảng
employee_payroll_templates không tồn tại — chạy migration (RunMigrations) trước khi bật
PAYROLL_TEMPLATE_ENFORCE"}` — đúng yêu cầu, không còn trả `{"enabled":true}` trơn như hiện nay. Đổi
tên bảng lại, gọi lần cuối: về `healthy:true`. Dừng backend, xác nhận bảng thật đúng tên, không sót
bảng đổi tên tạm.

**Nợ có ý thức (ghi để người sau không tưởng là bug):**
1. `TestIntegrationComputeFormulaImpactComputesDeltaWithoutWriting` **fail ngẫu nhiên** (không liên
   quan Task 1) vì assert số đếm toàn cục `payroll_records` trong khi Go chạy package test song song
   trên cùng DB dev — xem mục 0.5 ĐÍNH CHÍNH 1 và V4 ở `Formula-Versioning-PointInTime-050826.md`
   mục 7. Nếu gặp fail này ở lần chạy sau, **đừng vội quy cho Task 1** — chạy cách ly trước.
2. Chân trời lịch sử (`effective_from`) của `salary_component_versions` = thời điểm migration BQ chạy
   lần đầu ở `payroll_engine` (`2026-08-05 10:06:06+07`) — môi trường khác (staging/production) sẽ có
   chân trời khác. Xem V2 ở `Formula-Versioning-PointInTime-050826.md` mục 7.
3. Không tái tạo được lịch sử công thức **trước** chân trời (V1, cùng tài liệu) — nếu cần đối chiếu
   thanh tra cho kỳ 05–07/2026 thì phải nhập tay từ nguồn khác, chưa làm, chưa có kế hoạch.

## 10. Kết quả thi hành Report v1 (060826)

PLAN `llmwiki/wiki/sources/draft/060826-report-template-config-v1-PLAN.md` (7 task, soạn bởi một
phiên khác, kiểm chứng độc lập rồi thi hành trong phiên này) — cả 7 task đã xong, thi hành ngay
trong phiên, xác nhận từng bước bằng lệnh thật (không tin PLAN mù).

### 10.1 Bảng commit

| Task | Nội dung | Commit |
|---|---|---|
| 1 | `report_templates` + `report_template_lines` (migration idempotent trong `RunMigrations()`, khoá `component_code`, không FK `salary_components.id` — G1) | `Core System-backend@bb7fa8a` |
| 2 | CRUD backend (model/repo/service/handler), gate quyền `Settings.ReportTemplates` (view/create/edit/delete, opt-out default-allow), route `/config/report-templates*` | `Core System-backend@79d48db` |
| 3 | `POST /reports/config/{templateId}/run` — đọc thẳng `payroll_records.computed_values`, không qua engine (G3), 422 nếu `component_code` không tồn tại (TASK-REF) | `Core System-backend@a2f107d` |
| 4+5 | 2 sheet FE: `cfg-Template báo cáo` (liệt kê/xoá) + `rep-Chạy template báo cáo` (chọn/chạy/xem) | `Core System-frontend@c1e2250` |
| 6 | `computePayslipRole()` (19 deduction + 11 employer_cost), sửa `PayslipSummaryModal.tsx` dùng field `role` thay `DEDUCTION_KEYWORDS` | `Core System-backend@a9ce55f` + `Core System-frontend@4d08838` |

### 10.2 Hai lỗi PLAN bắt được trước khi chạy mù (không phải lỗi do thi hành gây ra)

1. **Task 1, Step 1**: test code PLAN viết `var n int; db.GetContext(ctx, &n, "SELECT to_regclass(...)
   IS NOT NULL")` — scan một biểu thức Postgres `BOOLEAN` vào Go `int`, lỗi xảy ra ở MỌI trạng thái
   migration (kể cả sau khi bảng đã tồn tại). Xác nhận bằng script Go tối giản trước khi sửa thành
   `var exists bool`. Nếu chạy mù theo PLAN, "definition of done" của Task 1 sẽ không bao giờ đạt được.
2. **Task 3, Step 5**: PLAN định đặt route mới trong `RegisterReportRoutes` và tái dùng biến
   `requireReportTemplatesView` — biến đó khai trong `RegisterConfigRoutes`, một hàm Go **khác**,
   không cùng scope. Theo đúng chỉ dẫn PLAN, route sẽ nằm NGOÀI khối `r.Use(requireAdmin)` mà mọi
   route `/reports/*` khác có — một người chỉ có role `employee` gọi được endpoint đọc dữ liệu lương.
   Bắt được ngay khi chạy full suite (`TestG1AllProtectedRoutesRequireRoleGateExceptAllowlist` —
   test-guard chuyên bắt lỗi "quên RequireRole" từ 150726). Sửa: khai `requireReportTemplatesView`
   cục bộ trong `RegisterReportRoutes` + thêm `requireAdmin` vào middleware chain.

### 10.3 Số đo thật

- Backend: `go test ./... -p 1` (Postgres dev thật) → **881 passed / 7 failed** sau mỗi task, khớp
  đúng baseline đo bằng `git stash` (3 fail ở `internal/app` — pre-existing, không liên quan route
  mới; 4 fail ở `internal/handler` — đã biết từ trước), 0 hồi quy xuyên suốt 6 task.
- Frontend: `tsc --noEmit` sạch (0 lỗi ngoài `DevToolkit.tsx` — lỗi build có sẵn từ trước, xác nhận
  lại bằng `git stash` + `next build` là baseline, không phải do việc này), `eslint` sạch, `vitest`
  26/26 PASS.
- Kiểm tay bằng dữ liệu thật (curl + psql trực tiếp trên `payroll_engine`, kỳ 05/2026 thật, 3273 bản
  ghi): tạo/đọc/xoá template qua API (POST 201 → GET 200 → DELETE 200 → GET 404); chạy báo cáo với
  cột `identity` (mã NV), `component` (GROSS — giá trị thay đổi theo NV, đối chiếu khớp DB), `sum`
  (MEAL_TAX+MEAL_NONTAX — khớp DB); phân loại payslip qua API thật: 19 deduction + 11 employer_cost +
  2 total + 108 earning, khớp đúng audit 30/30 mã.
- Mọi template/dữ liệu test đều xoá sạch sau khi kiểm — không còn dữ liệu rác trong `payroll_engine`.

### 10.4 Nợ có ý thức (Task 4, TASK-REF)

Sheet Cấu hình v1 **chỉ liệt kê + xoá**. Tạo/sửa template (chọn `sourceKind`, nhập `sourceCode`/
`sumCodes` cho từng dòng bố cục) chưa có form UI — làm qua `curl`/Postman trực tiếp vào
`POST/PUT /config/report-templates*` (đã xác nhận hoạt động đầy đủ ở Task 2/3). Đây là nợ **có chủ
đích**, không phải thiếu sót bỏ quên — PLAN ghi rõ ngay từ đầu, chưa có kế hoạch làm form UI đầy đủ.
