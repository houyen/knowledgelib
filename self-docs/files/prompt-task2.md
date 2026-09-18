---
id: self-docs/files/prompt-task2
canonical_question: 'Technical guide and specification: Prompt dispatch — Task 2'
aliases:
- Prompt dispatch — Task 2
- prompt Task2 050826
entity_type: how_to
domain: self-docs > files
last_verified: 2026-09-17
---

# Prompt dispatch — Task 2 (dán làm tin nhắn ĐẦU TIÊN của session mới)

Soạn 2026-08-05. Nguồn: `llmwiki/wiki/sources/draft/040826-Core System-template-on-giatbh-engine-PLAN.md`
**Task 2** + `self-docs/Salary-Structure-Template-Analysis-260726.md` **mục 16**.
Phần dưới dấu phân cách là nội dung để copy nguyên văn.

---

Đây là phiên **THI HÀNH theo brief đã chốt**, không phải phiên thiết kế. Quy tắc đã được quyết sau **hai
vòng đo trên dữ liệu thật** và **một quy tắc đã bị bác bỏ** — đừng thiết kế lại, đừng "tối ưu" quy tắc.

Repo: `/Users/thaidt/Documents/Enterprise/Core System`. Nhánh: `Core System-backend@feature_v2` (đúng nhánh rồi).
Task 0 (`6dbe1a6`), Task 1 (`b4d5ec6`), bản sửa L12+L13 (`bf42175`) đã xong và đã push — đừng làm lại.

## Mục tiêu

Dựng lại **lớp bảo vệ của mask** (đóng nợ **L5**). Hiện mask có 3 guard nhưng **2 guard đã chết**:
`statutoryOverrideBlocklist` = `{PIT, BHXH_NV, BHYT_NV, BHTN_NV}` mà **3 mã sau không tồn tại** trong DB;
guard `component_type == "system"` khớp **0 dòng** (PIT đã chuyển sang `formula`). Kết quả: `GROSS`,
`NET_PAY`, `TAXABLE_INC`, `TOTAL_INS`, `EARNED_SAL` chỉ còn được bảo vệ bởi **một** điều kiện — "không
nằm trong template nào" — tức chỉ cách một cú tick sai của HR là sai lương hàng loạt, im lặng.

## Đọc trước khi sửa

1. `llmwiki/wiki/sources/draft/040826-Core System-template-on-giatbh-engine-PLAN.md`:
   `## Global constraints` (G1–G5, **bắt buộc**) → `### Task 2` (brief chi tiết, có code mẫu).
2. `self-docs/Salary-Structure-Template-Analysis-260726.md` **mục 16** — đặc biệt **16.1** (quy tắc đã bị
   bác bỏ, đừng vô tình dựng lại nó) và **16.5** (quyết định chốt + phép đo).

## Quy tắc ĐÃ CHỐT — không thiết kế lại

```
maskable(c) =
      L1: formula của c KHÔNG tham chiếu component nào khác
          (LOẠI 6 biến bơm runtime khỏi đồ thị — xem "Bẫy 1")
   ∧  L2: c.Format      <> "days"
   ∧  L3: c.SourceField == ""
   ∧  c.Code ∉ statutoryOverrideBlocklist ∪ {"BASIC_SAL"}

→ đúng 66 mã trên DB hiện tại (140 component)
```

**L1 là lớp gánh chính**, và lý do nó đúng: nó chặn **toàn bộ 45 cột dẫn xuất mà không cần biết tên
chúng**. Đã kiểm: `GROSS`, `NET_PAY`, `NET_PAY_HOME`, `TAXABLE_INC`, `TAXABLE_GROSS`, `TOTAL_INS`,
`TOTAL_INS_CTY`, `TOTAL_DED`, `TOTAL_CTY_COST`, `TOTAL_PIT`, `EARNED_SAL`, `PIT`, `INS_SAL_BH`,
`INS_SAL_UI`, `CONTRACT_TOTAL`, `PROB_SAL`, `SI_EMP`, `HI_EMP`, `UI_EMP`, `KPCD_CTY`, `UNION_FEE` đều bị
L1 chặn. Nghĩa là cột tổng thêm sau này (đồng nghiệp `giatbh` vừa thêm 15 cột) **tự** an toàn.

**Blocklist tối thiểu — KHÔNG thêm mẫu tên.** Chấp nhận có ý thức: `ADVANCE_1`, `DEPENDENT_CNT`,
`CHARITY_DED`, nhóm `*_ADJ` **vẫn mask được nếu HR tick vào template**. Hàng rào cho nhóm đó là **UI ở
Task 3** (lỗ L6), không phải task này. **Đừng tự thêm chúng vào blocklist** — đó là quyết định đã cân
nhắc và loại.

**`MEAL_ALLOW` chấp nhận KHÔNG mask được, và KHÔNG thêm ngoại lệ nào vào thuật toán.** Nó là `formula`
tham chiếu `MEALS_TOTAL` nên L1 chặn. Nếu bạn nghĩ "nới một chút cho cột formula không phải cột tổng" —
**quy tắc đó đã được đo và bác bỏ**: nó lọt thêm 13 mã mà chỉ 1 là `MEAL_ALLOW`, 12 mã còn lại gồm
`BONUS_TOTAL` (tổng 13 cột thưởng), `CONTRACT_TOTAL` (cơ sở tính bảo hiểm), `TOTAL_SUPPORT`,
`TOTAL_POST_ADD`, `PROB_SAL`, `PROB_EARNED`, `EARNED_PAID_LEAVE`, `DEPENDENT_DED`, `PHONE_TAX`,
`PHONE_NONTAX`, `TRANSPORT_TAX`, `FAMILY_HEALTH_INS`. **Đừng dựng lại nó.**

## Sự thật đã xác minh — dùng luôn, KHÔNG đo lại

- `buildTemplateMaskFormulas` ở `internal/service/payroll_template_mask.go:35`; guard hiện tại ở dòng
  ~71: `if closure[c.Code] || statutoryOverrideBlocklist[c.Code] || c.ComponentType == "system"`.
- `statutoryOverrideBlocklist` ở `internal/service/salary_component_service.go:25`. Nó **còn được dùng bởi
  scoped-override guard** (doc ở `:22-24`) — sửa nội dung thì đừng làm hỏng công dụng cũ đó.
- `extractDeps` ở `internal/service/engine.go:49`.
- DB hiện tại: **140 component**. `component_type='system'` = **0 dòng**. Trong 4 mã blocklist chỉ `PIT`
  tồn tại; mã bảo hiểm thật đang dùng là `TOTAL_INS`, `TOTAL_INS_CTY`, `INS_SAL_BH`, `INS_SAL_UI`,
  `SI_EMP`, `HI_EMP`, `UI_EMP`, `KPCD_CTY`, `UNION_FEE` — **tất cả đều đã bị L1 chặn**, nên **không cần**
  nhồi chúng vào blocklist.
- Số đo phân lớp: L1 → 95 nguồn / 45 dẫn xuất; L2 (`format<>'days'`) → 68 (bỏ 27 cột đếm ngày);
  L3 (`source_field=''`) → 67 (bỏ 1 mã `CONS_ALLOW`); trừ blocklist → **66**.
- Baseline test: **6 case fail** (danh sách 6 test RBAC ở `HANDOVER-giatbh.md` mục 3). Có **1 test fail
  NGẪU NHIÊN** — `TestIntegrationComputeFormulaImpactComputesDeltaWithoutWriting` assert số đếm TOÀN CỤC
  `payroll_records` trong khi Go chạy package test song song trên cùng DB dev — nên con số dao động 6–7.
  Gặp nó thì **chạy cách ly** trước khi kết luận hồi quy.

## Bẫy đã biết

- **Bẫy 1 (quan trọng nhất) — 6 biến BƠM RUNTIME không phải component.** `CONTRACT_TYPE`, `EMP_TYPE`,
  `IS_FOREIGNER`, `WORK_TYPE`, `HAS_SECOND_CONTRACT`, `HAS_TAX_COMMITMENT` xuất hiện dạng `[MÃ]` trong
  công thức nhưng được bơm vào value map lúc chạy từ `employees`
  (`internal/service/payroll_service.go:1463-1472`). Khi tính L1 **chỉ đếm cạnh nếu mã đích có trong tập
  component**. Nếu coi chúng là cạnh, một cột chỉ tham chiếu biến runtime sẽ bị xếp nhầm thành "dẫn xuất"
  → mất quyền mask. Có test riêng cho bẫy này ở bước 5.
- **Bẫy 2 — đừng dựng lại quy tắc "cột lá".** Bản PLAN cũ từng đề xuất "chỉ mask cột không ai tham chiếu
  tới"; nó **chặn đúng những cột tính năng tồn tại để mask** (`PHONE_ALLOW` bị `PHONE_TAX`/`PHONE_NONTAX`
  tham chiếu, `FUEL_ALLOW` bị `GROSS`…), chỉ để lại 24/140 mã. Mask hoạt động **nhờ** lan truyền, nên "có
  người phụ thuộc" là **điều kiện để mask có tác dụng**. Xem mục 16.1.
- **Bẫy 3 — tên field struct.** Kiểm `models.SalaryComponent` bằng grep để lấy tên thật của `Format`,
  `SourceField`, `ComponentType`, `Formula` — **đừng đoán**.
- **Bẫy 4 — `gofmt -w` cả thư mục.** Đã từng làm hỏng một file không liên quan. Chỉ `gofmt -l` để xem.

## Việc phải làm

Theo `### Task 2` của PLAN, bước 1→6. Tóm ý:

1. Đo baseline (lưu ra file để so cuối task).
2. **Sửa `statutoryOverrideBlocklist` cho khớp mã thật**: giữ `PIT`, xử lý 3 mã chết
   (`BHXH_NV`/`BHYT_NV`/`BHTN_NV`) — bỏ hoặc thay, và **ghi comment nói rõ vì sao đổi**, kèm cảnh báo
   rằng biến này còn được scoped-override guard dùng.
3. **Viết hàm thuần `maskableCodes(all []models.SalaryComponent) map[string]bool`** trong
   `payroll_template_mask.go` — code mẫu có trong PLAN Task 2 bước 3, dùng đúng nó.
4. Nối vào `buildTemplateMaskFormulas`: thay guard `component_type == "system"` đã chết (giữ kèm comment
   nói rõ nó khớp 0 dòng, để người sau không tưởng nó đang bảo vệ) bằng `!maskable[c.Code] → continue`.
   **Không đổi chữ ký hàm** (G3).
5. **6 test khoá bất biến** (hàm thuần nên phần lớn **không cần DB**) — danh sách đầy đủ ở PLAN bước 5,
   trong đó bắt buộc có:
   - `TestMaskable_AllowsSourceAllowance` — `PHONE_ALLOW` **phải** maskable (test chống lại chính quy tắc
     "cột lá" đã bị bác bỏ).
   - `TestMaskable_IgnoresRuntimeInjectedVars` — cột chỉ tham chiếu `[CONTRACT_TYPE]` **vẫn** maskable
     (bắt Bẫy 1).
   - `TestMask_NeverMasksAggregateEvenIfTemplateListsIt` — template **cố ý** chứa `GROSS` → `GROSS` không
     vào mask.
6. Verify.

## Ràng buộc tuyệt đối

1. **KHÔNG đổi chữ ký** `buildTemplateMaskFormulas`, không đổi route, không sửa frontend (Task 3 mới sửa
   FE), không đổi JSON contract.
2. **KHÔNG thêm blocklist theo mẫu tên**, không thêm `ADVANCE_1`/`DEPENDENT_CNT`/`*_ADJ` vào blocklist —
   quyết định đã cân nhắc và loại.
3. **KHÔNG thêm ngoại lệ cho `MEAL_ALLOW`** hay bất kỳ cột `formula` nào.
4. **KHÔNG đổi semantics `migrationSalaryComponentsV4`** (G5), không viết vào `atlas/migrations/`.
5. **KHÔNG bật `PAYROLL_TEMPLATE_ENFORCE`.** Task này chỉ sửa thuật toán; việc bật là Task 5.
6. `maskableCodes` phải là **hàm thuần** (chỉ nhận slice component, không chạm DB) — Task 3 sẽ gọi lại nó
   ở tầng khác, và nó phải test được không cần DB.

## DỪNG và hỏi người dùng

- **Trước khi commit.** Không tự push.
- Nếu phép đo đối chứng ở bước 6 **không ra đúng 66 mã** → DỪNG, in danh sách chênh lệch. Đừng sửa
  blocklist cho khớp con số — con số là hệ quả của quy tắc, không phải mục tiêu.
- Nếu thấy buộc phải sửa `engine.go`, `payroll_service.go`, frontend, hay route → **dừng**, đó là dấu
  hiệu hiểu sai phạm vi.
- Nếu brief lệch code thật (tên hàm/field/số dòng) → **báo ngay, đừng đoán rồi làm tiếp**.

## Định nghĩa "xong"

1. `gofmt -l internal/` không liệt kê file bạn sửa; `go build ./...` + `go vet ./...` sạch.
2. **Phép đo đối chứng: `maskableCodes` trả về đúng 66 mã** trên DB hiện tại. In cả danh sách để đối
   chiếu mắt — phải thấy `PHONE_ALLOW`, `FUEL_ALLOW`, `TRANSPORT_ALLOW`, `LIVING_ALLOW`, `HEALTH_INS`,
   `OTHER_ALLOW_TAX` trong đó, và **không** thấy `GROSS`, `NET_PAY`, `TAXABLE_INC`, `TOTAL_INS`,
   `BASIC_SAL`, `PIT`, `CONTRACT_TOTAL`, `MEAL_ALLOW`.
3. 6 test mới xanh, và **ít nhất một test phải FAIL nếu revert phần sửa** — chạy thử để chứng minh test
   thật sự bắt được bug, đừng chỉ tin nó xanh.
4. `go test ./...` — không thêm fail mới so với baseline bước 1 (6, dao động 7 vì test flaky).
5. **Khẳng định không đổi số lương:** enforce đang TẮT nên `Calculate` không đi qua nhánh mask; xác nhận
   bằng cách chạy `Calculate` cho một kỳ trước/sau khi sửa và so `md5` của `computed_values` + `count(*)`
   → phải **y hệt**. Nếu khác, bạn đã chạm nhánh không được chạm.

## Khi xong thì ghi tài liệu

1. `llmwiki/wiki/sources/draft/040826-...-PLAN.md` — cột `TT` Task 2 → `xong` + commit hash + cập nhật
   dòng "Cập nhật lần cuối". Đây là nơi duy nhất ghi tiến độ.
2. `self-docs/Salary-Structure-Template-Analysis-260726.md` — thêm mục **16.6 "Kết quả thi hành"** kèm số
   đo thật (66 mã + danh sách).
3. `self-docs/00-START-HERE.md` — **xoá dòng L5** khỏi bảng lỗi (quy ước: sửa xong thì xoá). **Giữ L6**
   (picker chưa lọc) vì đó là Task 3.
4. `CLAUDE.md` — một dòng nhật ký, mới nhất lên đầu.
5. Ghi **nợ có ý thức**: `ADVANCE_1`, `DEPENDENT_CNT`, `CHARITY_DED`, nhóm `*_ADJ` vẫn mask được nếu bị
   tick — hàng rào là Task 3; và `MEAL_ALLOW` không mask được (Task 3 phải hiện disabled kèm lý do).

Bắt đầu bằng bước 1 (đo baseline) và bước 2 (kiểm mã thật của blocklist), báo kết quả cho tôi xem, rồi
mới sửa.
