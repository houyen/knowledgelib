---
id: self-docs/files/prompt-task3
canonical_question: 'Technical guide and specification: Prompt dispatch — Task 3'
aliases:
- Prompt dispatch — Task 3
- prompt Task3 050826
entity_type: how_to
domain: self-docs > files
last_verified: 2026-09-17
---

# Prompt dispatch — Task 3 (dán làm tin nhắn ĐẦU TIÊN của session mới)

Soạn 2026-08-05. Nguồn: `llmwiki/wiki/sources/draft/040826-Core System-template-on-giatbh-engine-PLAN.md`
**Task 3** + `self-docs/Salary-Structure-Template-Analysis-260726.md` mục **16.6** và **17.2**.
Phần dưới dấu phân cách là nội dung để copy nguyên văn.

---

Đây là phiên **THI HÀNH theo brief đã chốt**. Task này chạm **cả backend lẫn frontend**, nhưng **không
chạm thuật toán mask** — nếu thấy cần sửa `buildTemplateMaskFormulas` hay `maskableCodes`, dừng lại.

Repo: `/Users/thaidt/Documents/Enterprise/Core System`. Nhánh: `Core System-backend@feature_v2` và
`Core System-frontend@feature_v2`. Task 0 (`6dbe1a6`), Task 1 (`b4d5ec6`), L12+L13 (`bf42175`),
Task 2 (`1ede75d`), Task 4 (`65fed61`) đã xong — đừng làm lại.

## Mục tiêu (đóng L6)

Picker cột trong `PayrollTemplateModal.tsx` hiện là `allComponents.map(...)` **không lọc gì** — toàn bộ
140 cột kể cả `GROSS`/`NET_PAY`/`TAXABLE_INC`/`BASIC_SAL` đều tick được. Tài liệu cũ từng tuyên bố "UI chỉ
cho chọn cột phụ cấp" nhưng điều đó **chưa bao giờ được xây**.

Task 2 đã dựng lớp bảo vệ ở engine (tick nhầm `GROSS` thì engine không mask nó). Task này là **hàng rào
thứ hai, ở tầng UI**: đừng để HR tick được thứ vô tác dụng rồi tưởng tính năng hỏng.

## Ba yêu cầu, yêu cầu 2 là chỗ dễ làm sai nhất

**(1) BE trả cờ, FE KHÔNG tự đoán.** Thêm `maskable bool` + `maskReason string` vào response
`GET /api/v1/config/salary-components`. FE chỉ hiển thị. Nếu FE tự tính lại quy tắc thì FE và engine sẽ
lệch nhau — đúng loại lỗi tệ nhất.

**(2) Cờ phải phản ánh tập mask THỰC TẾ = `66 ∪ 6` = 72 mã, KHÔNG phải 66.**
`maskableCodes()` (`internal/service/payroll_template_mask.go:149`) trả **66** mã. Nhưng guard thật ở
`payroll_template_mask.go` (khoảng dòng 91) là:
```go
if !maskable[c.Code] && !templateMaskSiblingSplits[c.Code] {
    continue
}
```
tức tập mask hiệu lực = `maskableCodes()` **∪** `templateMaskSiblingSplits` (6 mã:
`MEAL_TAX`, `MEAL_NONTAX`, `PHONE_TAX`, `PHONE_NONTAX`, `TRANSPORT_TAX`, `FAMILY_HEALTH_INS`).
**Nếu bạn lấy cờ từ `maskableCodes()` một mình, UI sẽ disable 6 mã đó** — và hậu quả cụ thể: **HR mất
đường duy nhất để bỏ phụ cấp cơm** (xem yêu cầu 3). Phải rút ra một helper dùng chung cho **cả guard lẫn
API**, để một nguồn sự thật.

**(3) Giải thích quan hệ CHA–TÁCH, và KHÔNG được nói "không bỏ được phụ cấp cơm".**
`MEAL_ALLOW` là `formula` tham chiếu `MEALS_TOTAL` nên **không maskable trực tiếp**. Nhưng `GROSS` tham
chiếu **các cột tách**, không tham chiếu cột cha:
```
GROSS = [EARNED_SAL] + [MEAL_TAX] + [MEAL_NONTAX] + [PHONE_TAX] + [PHONE_NONTAX] + ...
```
và `MEAL_NONTAX = MIN([MEAL_ALLOW],730000)`, `MEAL_TAX = MAX(0,[MEAL_ALLOW]-730000)` nên
`MIN(x,730k) + MAX(0,x-730k) = x` **chính xác**. ⇒ Bỏ qua **cả hai** cột tách sẽ **gỡ trọn vẹn** phụ cấp
cơm khỏi `GROSS`. Vậy **template BỎ ĐƯỢC phụ cấp cơm**, chỉ là qua hai cột tách.

⇒ Với `MEAL_ALLOW`, `maskReason` phải là hướng dẫn đúng đường (đại ý: *"không chọn trực tiếp; điều khiển
qua `MEAL_TAX`/`MEAL_NONTAX`"*), **KHÔNG** phải câu "không bỏ được phụ cấp cơm" (câu đó **sai**).
Suy ra danh sách cột tách bằng **dữ liệu**, không hardcode: với một cột không maskable, tìm các mã trong
`templateMaskSiblingSplits` mà **công thức của chúng tham chiếu tới nó**.

## Sự thật đã xác minh — dùng luôn, KHÔNG đo lại

- Đường List: `internal/handler/salary_component_handler.go:20` (`List`) →
  `internal/service/salary_component_service.go:116` (`List` → `s.repo.ListActive(ctx)`).
  **`maskableCodes` cùng package `service`** nên `SalaryComponentService.List` gọi trực tiếp được.
- `maskableCodes(all []models.SalaryComponent) map[string]bool` ở `payroll_template_mask.go:149`.
- `templateMaskSiblingSplits` (6 mã) khai trong cùng file đó.
- Quy tắc 3 lớp của `maskableCodes`: L1 cột **nguồn** (không tham chiếu component nào — đã loại 6 biến
  bơm runtime) ∧ L2 `format <> 'days'` ∧ L3 `source_field = ''` ∧ ∉ blocklist
  (`statutoryOverrideBlocklist` = `{PIT, SI_EMP, HI_EMP, UI_EMP}` ∪ `{BASIC_SAL}`). Số đo trên DB hiện
  tại (140 component): L1 → 95/45, L2 → 68, L3 → 67, trừ blocklist → **66**.
- FE type `SalaryComponent` ở `Core System-frontend/lib/api/types.ts` (khối bắt đầu
  `export interface SalaryComponent {`) — thêm field mới **optional** để không phá call site nào.
- Picker cần sửa: `Core System-frontend/components-page/tinh-luong/PayrollTemplateModal.tsx:134`
  (`allComponents.map((c) => ( ... ))`).
- **ĐÃ CÓ SẴN, đừng làm lại**: danh sách template bên trái đã hiện `{t.componentCount ?? 0} cột lương`
  (`PayrollTemplateModal.tsx:118`), và header picker đã hiện
  `Cột lương thuộc cấu trúc này ({form.componentCodes.length} đã chọn)` (`:132`).
- `form.componentCodes` chứa **CODE**, không phải id (`:19`, toggle ở `:93-97`).
- FE **không có script `typecheck`** trong `package.json`. Bộ verify thật: `pnpm lint` → `pnpm build`
  (`next build` là nơi type được kiểm) → `pnpm test` (vitest, `environment: "node"` nên **không mount
  được component**). Package manager: **pnpm**.
- Baseline test BE: **6 case fail** (6 test RBAC ở `HANDOVER-giatbh.md` mục 3), cộng **1 test fail NGẪU
  NHIÊN** `TestIntegrationComputeFormulaImpactComputesDeltaWithoutWriting` (assert số đếm toàn cục
  `payroll_records`, các package test chạy song song) → con số dao động 6–7. Gặp thì **chạy cách ly**.

## Việc phải làm

**Backend:**

1. Rút helper dùng chung trong `payroll_template_mask.go`, ví dụ
   `func templateMaskEligible(all []models.SalaryComponent) map[string]bool` = `maskableCodes(all)` ∪
   `templateMaskSiblingSplits`. **Sửa guard để dùng chính helper này** (thay biểu thức
   `!maskable[...] && !templateMaskSiblingSplits[...]`) — một nguồn sự thật cho cả engine lẫn API.
   **Không đổi chữ ký `buildTemplateMaskFormulas`.**
2. Thêm hàm tính lý do, thuần, cùng file:
   `func templateMaskReason(c models.SalaryComponent, all []models.SalaryComponent) string` — trả `""`
   nếu eligible. Thứ tự ưu tiên lý do (cụ thể → chung), và **nội dung phải nói được điều HR làm được
   tiếp**, không chỉ nói "không được":
   - trong blocklist → cột pháp định (thuế/bảo hiểm) / lương cơ bản;
   - `format == "days"` → cột đếm ngày, là dữ liệu chấm công;
   - `source_field != ""` → cột nạp từ chấm công/HRIS;
   - cột **dẫn xuất** (tham chiếu component khác) **và có cột tách trong `templateMaskSiblingSplits` trỏ
     tới nó** → hướng dẫn điều khiển qua các cột tách đó (nêu tên chúng);
   - cột dẫn xuất còn lại → cột tổng/dẫn xuất, giá trị tính từ cột khác.
3. Thêm 2 field vào `models.SalaryComponent` với tag `db:"-"` (**tính runtime, không lưu DB**):
   `Maskable bool \`json:"maskable" db:"-"\`` và `MaskReason string \`json:"maskReason,omitempty" db:"-"\``.
   Điền trong `SalaryComponentService.List` (`:116`) — **chỉ ở endpoint List**, đừng rải khắp nơi.
   ⚠️ Kiểm `repo.ListActive` có dùng `SELECT *` + `db.Unsafe()` hay không; nếu nó map theo tên cột thì
   `db:"-"` là bắt buộc để không vỡ scan. **Chạy test sau bước này trước khi đi tiếp.**
4. Test BE (hàm thuần, không cần DB):
   - `TestTemplateMaskEligible_IncludesSiblingSplits` — 6 mã tách **phải** eligible.
   - `TestTemplateMaskEligible_MatchesGuard` — tập helper trả về **khớp đúng** điều kiện guard đang dùng
     (chống trôi khi ai đó sửa một bên).
   - `TestTemplateMaskReason_MealAllowancePointsToSplits` — `maskReason` của `MEAL_ALLOW` **có chứa** tên
     `MEAL_TAX` và `MEAL_NONTAX`, và **không chứa** ý "không bỏ được".
   - `TestTemplateMaskReason_EmptyWhenEligible` — cột eligible thì reason rỗng.

**Frontend:**

5. `lib/api/types.ts`: thêm `maskable?: boolean; maskReason?: string;` vào `SalaryComponent` (optional).
6. `PayrollTemplateModal.tsx:134`: cột `maskable === false` → checkbox **disabled**, dòng mờ đi
   (`opacity`), `title` = `maskReason`, và hiện `maskReason` dạng chữ nhỏ dưới tên cột.
   **KHÔNG ẩn cột** — ẩn thì HR tưởng thiếu dữ liệu. Cột `maskable !== false` giữ nguyên hành vi.
7. Cảnh báo dữ liệu cũ: nếu `form.componentCodes` đang chứa mã mà nay `maskable === false`, hiện một dòng
   cảnh báo (đại ý: *"N cột trong cấu trúc này không còn tác dụng mask"*) + liệt kê mã. **Không tự xoá
   chúng** — xoá im lặng là đúng thứ tài liệu này liên tục cảnh báo.
8. Tách logic thuần ra `lib/` để test được không cần mount component (khuôn `lib/permission-resolve.ts`
   đã có tiền lệ), ví dụ `lib/template-picker.ts` với hàm phân nhóm/đếm cột không hợp lệ. Thêm test
   vitest cho hàm đó.

## Ràng buộc tuyệt đối

1. **KHÔNG đổi thuật toán mask.** `maskableCodes` giữ nguyên nội dung 3 lớp + blocklist. Việc duy nhất
   được làm với guard là **rút ra helper** rồi gọi lại, không đổi hành vi.
2. **KHÔNG đổi chữ ký** `buildTemplateMaskFormulas`, không đổi route, không đổi bộ gate.
3. **KHÔNG bật `PAYROLL_TEMPLATE_ENFORCE`** (đó là Task 5).
4. **KHÔNG đổi `SALARY_STRUCTURE_FEATURE_VISIBLE`** (`TinhLuongExcel.tsx:57`) — mở lại UI là **Task 6**.
   Task này sửa nội dung modal, không mở đường vào.
5. **KHÔNG đổi giá trị lương.** Task này chỉ thêm field read-only + sửa UI. Xác nhận `payroll_records`
   md5 + `count(*)` không đổi.
6. **KHÔNG hardcode danh sách cột tách ở FE.** Quan hệ cha–tách suy ra ở BE từ dữ liệu.

## Bẫy đã biết

- **Bẫy 1 (nặng nhất) — dùng `maskableCodes()` một mình cho cờ API.** Sẽ disable 6 cột tách, và **cắt
  luôn đường bỏ phụ cấp cơm**. Phải dùng tập hợp `∪` — xem yêu cầu 2.
- **Bẫy 2 — viết `maskReason` cho `MEAL_ALLOW` là "không bỏ được phụ cấp cơm".** Câu đó **sai** (mục 16.6
  của self-docs). Có test bắt điều này.
- **Bẫy 3 — `db:"-"`.** Thiếu tag này thì `sqlx` có thể vỡ khi scan (`ListActive`). Chạy test BE ngay sau
  bước 3.
- **Bẫy 4 — làm lại thứ đã có.** `componentCount` và bộ đếm "đã chọn" **đã tồn tại** (`:118`, `:132`).
  Đừng dựng lại; nếu muốn cải thiện thì chỉ làm nổi bật hơn.
- **Bẫy 5 — `pnpm typecheck` không tồn tại.** Type được kiểm qua `pnpm build`.
- **Bẫy 6 — `gofmt -w` cả thư mục** đã từng làm hỏng file không liên quan. Chỉ `gofmt -l` để xem.

## DỪNG và hỏi người dùng

- **Trước khi commit.** Không tự push. Hai repo → hai commit riêng, đừng gộp.
- Nếu `templateMaskEligible` trả về số khác **72** trên DB hiện tại (66 + 6) → DỪNG, in danh sách chênh.
- Nếu brief lệch code thật (tên hàm/field/số dòng) → báo ngay, đừng đoán rồi làm tiếp.
- Nếu thấy buộc phải sửa `engine.go`, `payroll_service.go`, hay mở `SALARY_STRUCTURE_FEATURE_VISIBLE` →
  dừng, đó là dấu hiệu hiểu sai phạm vi.

## Định nghĩa "xong"

1. BE: `gofmt -l internal/` không liệt kê file bạn sửa; `go build ./...` + `go vet ./...` sạch;
   `go test ./...` không thêm fail mới so với baseline (6, dao động 7 vì test flaky).
2. **Phép đo đối chứng**: `templateMaskEligible` trả **đúng 72 mã** trên DB hiện tại; in danh sách và xác
   nhận **có** `MEAL_TAX`, `MEAL_NONTAX`, `PHONE_ALLOW`, `FUEL_ALLOW`, `HEALTH_INS`; **không có** `GROSS`,
   `NET_PAY`, `TAXABLE_INC`, `BASIC_SAL`, `PIT`, `CONTRACT_TOTAL`.
3. Test BE mới xanh, và **ít nhất một test phải FAIL nếu revert phần sửa** — chạy thử để chứng minh, đừng
   chỉ tin nó xanh.
4. **Kiểm bằng request thật**: `curl` `GET /api/v1/config/salary-components` (Bearer dev) → mỗi phần tử có
   `maskable`; `GROSS` có `maskable:false` + `maskReason` khác rỗng; `MEAL_ALLOW` có `maskReason` **chứa**
   `MEAL_TAX`; `PHONE_ALLOW` có `maskable:true`.
5. FE: `pnpm lint` sạch (0 error), `pnpm build` xanh, `pnpm test` xanh.
6. **Kiểm tay trên trình duyệt** — món nợ lặp lại nhiều đợt (270726, 280726, 290726 đều ghi "chưa kiểm
   tay"). Lỗi `overrideRefs = null` gây trắng màn hình ở đợt 280726 là bằng chứng `build` xanh **không**
   thay thế được bước này. Vì `SALARY_STRUCTURE_FEATURE_VISIBLE` đang `false`, tạm đổi về `true` **chỉ
   trong lúc kiểm tay**, xem modal, rồi **đổi lại `false`** trước khi commit (Task 6 mới mở thật).
7. `payroll_records` không đổi: md5 `computed_values` + `count(*)` y nguyên.

## Khi xong thì ghi tài liệu

1. `llmwiki/wiki/sources/draft/040826-...-PLAN.md` — cột `TT` Task 3 → `xong` + 2 commit hash + cập nhật
   "Cập nhật lần cuối". Đây là nơi duy nhất ghi tiến độ.
2. `self-docs/Salary-Structure-Template-Analysis-260726.md` — mục kết quả kèm **số đo thật** (72 mã +
   `maskReason` thật của `MEAL_ALLOW`).
3. `self-docs/00-START-HERE.md` — **xoá dòng L6** khỏi bảng lỗi.
4. `CLAUDE.md` — một dòng nhật ký, mới nhất lên đầu.
5. Ghi **nợ**: `vitest` chỉ có `environment: "node"` nên không test được component — chỉ test được hàm
   thuần đã tách ra `lib/`.

Bắt đầu bằng: đo baseline BE, rồi in ra tập `maskableCodes()` (66) và tập `∪ templateMaskSiblingSplits`
(72) để xác nhận con số trước khi sửa. Báo cho tôi xem rồi mới viết code.
