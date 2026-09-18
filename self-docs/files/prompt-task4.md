---
id: self-docs/files/prompt-task4
canonical_question: 'Technical guide and specification: Prompt dispatch — Task 4'
aliases:
- Prompt dispatch — Task 4
- prompt Task4 050826
entity_type: how_to
domain: self-docs > files
last_verified: 2026-09-17
---

# Prompt dispatch — Task 4 (dán làm tin nhắn ĐẦU TIÊN của session mới)

Soạn 2026-08-05. Nguồn: `llmwiki/wiki/sources/draft/040826-Core System-template-on-giatbh-engine-PLAN.md`
**Task 4** (bản mở rộng 2 lỗ). Phần dưới dấu phân cách là nội dung để copy nguyên văn.

---

Đây là phiên **THI HÀNH theo brief đã chốt**, không phải phiên thiết kế.

Repo: `/Users/thaidt/Documents/Enterprise/Core System`. Nhánh: `Core System-backend@feature_v2` (đúng nhánh rồi).
Task 0 (`6dbe1a6`), Task 1 (`b4d5ec6`), L12+L13 (`bf42175`), Task 2 (`1ede75d`) đã xong — đừng làm lại.

## Mục tiêu

Sửa `ComputeTemplateImpact` — **cổng duyệt DUY NHẤT** trước khi bật `PAYROLL_TEMPLATE_ENFORCE`. Hiện nó
**luôn** báo "không có tác động". Một cổng luôn nói an toàn còn tệ hơn không có cổng: C&B sẽ ký duyệt
bật enforce dựa trên một báo cáo trắng.

## ⚠️ Có HAI lỗ, không phải một. Sửa một lỗ là "sửa mà không sửa"

| # | Lỗ | Vị trí |
|---|---|---|
| 1 | `salaryOverrides` là map **rỗng** ở cả 2 lần mô phỏng | `internal/service/payroll_service.go:802` và `:809` |
| 2 | **`empManual` truyền `nil`** thay vì manual inputs thật | `internal/service/payroll_service.go:824` và `:825` |

**Lỗ 2 mới là lỗ chí tử**, và nó chỉ lộ ra sau Task 2. Sau Task 2, tập mask là **66 mã cột NGUỒN có
`source_field = ''`** — nghĩa là giá trị của chúng đến từ bảng `payroll_manual_inputs`, **không** từ
attendance. `Calculate` nạp chúng ở `:253-254` rồi truyền `empManual` vào `computeEmployee` (`:356`);
`CalculateOne` tương tự (`:668-669`, `:707`). **Hai hàm impact truyền `nil`.**

⇒ Trong `ComputeTemplateImpact` hiện tại: `BASIC_SAL = 0` **và** toàn bộ 66 mã maskable **= 0** ở cả hai
lần ⇒ delta bằng **0 tuyệt đối** ⇒ báo cáo luôn trắng.

⇒ Nếu chỉ sửa lỗ 1: mask một phụ cấp **vẫn** cho delta 0, báo cáo **vẫn** nói không có tác động — nhưng
lúc đó ta đã "sửa xong", test đã xanh, và không ai phát hiện nữa. **Phải sửa cả hai.**

## Sự thật đã xác minh — dùng luôn, KHÔNG đo lại

- `ComputeTemplateImpact(ctx, periodID)` hiện ở `payroll_service.go:750` — **chưa** có tham số salaries.
- Khuôn phải theo: `ComputeFormulaImpact` ở `:909`; sentinel `ErrFormulaImpactNoSalaries` ở `:873`; guard
  `if len(in.Salaries) == 0 { return nil, Err... }` ở `:911`; truyền `salaryOverrides: in.Salaries` ở
  `:988`. `FormulaImpactInput.Salaries` là `map[string]float64 // empCode -> basicSalary`.
- `computeEmployee(sh *calcShared, emp models.Employee, att *models.AttendanceSummary, empManual map[string]float64)`
  ở `:504`. Call site: `Calculate:356` (truyền thật), `CalculateOne:707` (thật),
  **`ComputeTemplateImpact:824` và `:825` (nil)**, `ComputeFormulaImpact:1016` và `:1020` (nil).
- Manual inputs nạp ở `Calculate:253-254`: `manualInputRepo.GetByPeriod(ctx, periodID)` →
  `manualInputRepo.ToMap(...)`; `Calculate:356` dùng `manualMap[emp.ID]`. **Kiểm kiểu trả về thật của
  `ToMap` bằng grep trước khi viết — đừng đoán key là gì.**
- Route hiện tại: `GET /template-impact/{periodId}` ở `internal/app/router.go:459`, gate
  `requirePayrollCalculate, companyReadScope, requireView`.
- Route mẫu để theo: `POST /formula-impact/{periodId}` ở `router.go:467` — **cùng đúng bộ gate đó**, nên
  đổi GET→POST không đổi phân quyền.
- Handler mẫu: `internal/handler/payroll_formula_impact_handler.go` — body nhận `salaries` dạng **mảng**
  `[{empCode, basicSalary}]` rồi tự đổi sang map; `errors.Is(err, ErrFormulaImpactNoSalaries)` →
  **`http.StatusUnprocessableEntity` (422)**; lỗi khác → 400; thành công → 200.
- Handler cần sửa: `internal/handler/payroll_template_impact_handler.go:16` (gọi service ở `:21`).
- **Frontend hiện có 0 client gọi `template-impact`** (grep toàn repo FE: 0 hit trong `.ts`/`.tsx`) ⇒ đổi
  GET→POST là breaking change **an toàn**.
- Baseline test: **6 case fail** (6 test RBAC ở `HANDOVER-giatbh.md` mục 3). Có **1 test fail NGẪU NHIÊN**
  — `TestIntegrationComputeFormulaImpactComputesDeltaWithoutWriting` assert số đếm TOÀN CỤC
  `payroll_records` trong khi Go chạy package test song song trên cùng DB dev — nên con số dao động 6–7.
  Gặp thì **chạy cách ly** trước khi kết luận hồi quy.

## Việc phải làm

Theo `### Task 4` của PLAN, bước 1→6. Cốt lõi:

1. Đo baseline, lưu ra file.
2. Đổi chữ ký thành
   `ComputeTemplateImpact(ctx context.Context, periodID uuid.UUID, salaries map[string]float64)`,
   thêm sentinel `ErrTemplateImpactNoSalaries`, guard `len(salaries) == 0 → trả lỗi`.
   **Sửa lỗ 1**: truyền `salaryOverrides: salaries` vào **cả hai** `calcShared`.
   **Sửa lỗ 2**: nạp manual inputs theo khuôn `Calculate:253-254` rồi truyền `manualMap[emp.ID]` vào
   **cả hai** lời gọi `computeEmployee` (thay `nil`).
3. Đổi route `GET` → `POST` (`router.go:459`), **giữ nguyên** bộ gate.
4. Sửa handler theo khuôn `payroll_formula_impact_handler.go` (mảng `salaries[]`, 422, 400, 200).
5. Test (xem mục dưới — đây là phần dễ làm sai nhất).
6. Verify + nghiệm thu bằng `curl` thật.

## Test — bản PLAN TRƯỚC đã sai ở đây, đọc kỹ

- `TestComputeTemplateImpact_RejectsWithoutSalaries` — khẳng định trả lỗi, **không** trả báo cáo rỗng.
- **`TestComputeTemplateImpact_DetectsAllowanceMaskDelta` — PHẢI neo vào một PHỤ CẤP bị mask**
  (ví dụ `PHONE_ALLOW`, nạp giá trị qua `payroll_manual_inputs`), **KHÔNG neo vào `BASIC_SAL`.**
  Lý do: neo vào `BASIC_SAL` thì test **xanh ngay khi sửa xong lỗ 1** trong khi lỗ 2 vẫn nguyên — tức test
  cho **cảm giác an toàn giả đúng cho ca dùng thật** (ca dùng thật của tính năng là mask phụ cấp, không
  phải mask lương cơ bản — `BASIC_SAL` nằm trong blocklist, **không bao giờ** bị mask).
  Khẳng định: `EmployeesAffected > 0`, và `byComponent` có dòng cho đúng mã phụ cấp đó với delta bằng
  **đúng** giá trị đã nạp vào manual input.
- Khẳng định **không ghi `payroll_records`**: md5 toàn bộ `computed_values` + `count(*)` +
  `max(updated_at)` y nguyên trước/sau (khuôn đã dùng ở đợt 280726).
- Cập nhật `internal/app/payroll_template_impact_permission_integration_test.go` sang **POST**, giữ nguyên
  bảng role đang assert.

## Ràng buộc tuyệt đối

1. **KHÔNG sửa `ComputeFormulaImpact`.** Nó cũng truyền `empManual = nil` (`:1016`, `:1020`) nên ước
   lượng thiếu cho công thức phụ thuộc phụ cấp nhập tay — **ghi thành nợ trong tài liệu, đừng sửa kèm**
   (ngoài phạm vi, và nó có test riêng đang xanh nên đổi sẽ phải đo lại baseline của nó).
2. **KHÔNG ghi `payroll_records`.** Hàm này là read-only; có test khẳng định điều đó.
3. **KHÔNG đổi** struct `TemplateImpactReport`/`TemplateImpactComponentDiff`/`TemplateImpactSample` — FE
   Task 6 sẽ dùng, giữ ổn định.
4. **KHÔNG sửa frontend** (Task 6 mới làm FE), **không đổi bộ gate** của route.
5. **KHÔNG bật `PAYROLL_TEMPLATE_ENFORCE`** (đó là Task 5). Hàm impact tự ép cứng true/false cho 2 lần mô
   phỏng, độc lập với env — giữ nguyên tính chất đó.
6. **KHÔNG đổi semantics `migrationSalaryComponentsV4`** (G5), không viết vào `atlas/migrations/`.

## Bẫy đã biết

- **Bẫy 1 — sửa nửa vời.** Xem mục "HAI lỗ". Nếu bạn thấy mình chỉ sửa `salaryOverrides` rồi test xanh,
  **quay lại đọc lỗ 2**.
- **Bẫy 2 — `manualMap` key.** `Calculate` lấy `manualMap[emp.ID]` (uuid của employee), không phải
  `empCode`. Grep `ToMap` để xác nhận kiểu thật.
- **Bẫy 3 — `s.manualInputRepo` có thể nil** trong một số đường dựng service (test dựng thủ công). Guard
  nil như `Calculate` đang làm, đừng để panic.
- **Bẫy 4 — `gofmt -w` cả thư mục** đã từng làm hỏng một file không liên quan. Chỉ `gofmt -l` để xem.

## DỪNG và hỏi người dùng

- **Trước khi commit.** Không tự push.
- Nếu sau khi sửa **cả hai** lỗ mà test neo-vào-phụ-cấp **vẫn** cho delta 0 → **DỪNG**, báo số cụ thể.
  Đó là dấu hiệu còn một đường thứ ba làm mất giá trị đầu vào, và nó quan trọng hơn việc làm test xanh.
- Nếu brief lệch code thật (tên hàm/field/số dòng) → báo ngay, đừng đoán rồi làm tiếp.
- Nếu thấy buộc phải sửa `engine.go`, frontend, hay `ComputeFormulaImpact` → dừng, đó là dấu hiệu hiểu sai
  phạm vi.

## Định nghĩa "xong"

1. `gofmt -l internal/` không liệt kê file bạn sửa; `go build ./...` + `go vet ./...` sạch.
2. Test mới xanh, và **test neo-vào-phụ-cấp phải FAIL nếu revert riêng lỗ 2** (trả `nil` lại cho
   `empManual`) — chạy thử để chứng minh nó thật sự bắt được lỗ 2, đừng chỉ tin nó xanh. Đây là phép thử
   quan trọng nhất của cả task.
3. `go test ./...` — không thêm fail mới so với baseline bước 1.
4. **Nghiệm thu bằng request thật**: `POST` có `salaries` → 200 và báo cáo có `employeesAffected > 0` +
   `byComponent` khác rỗng khi có template thật đang mask một phụ cấp; `POST` body `{}` → **422**.
5. Khẳng định `payroll_records` **không đổi**: md5 `computed_values` + `count(*)` + `max(updated_at)` y
   nguyên trước/sau khi gọi endpoint.

## Khi xong thì ghi tài liệu

1. `llmwiki/wiki/sources/draft/040826-...-PLAN.md` — cột `TT` Task 4 → `xong` + commit hash + cập nhật
   "Cập nhật lần cuối". Đây là nơi duy nhất ghi tiến độ.
2. `self-docs/Salary-Structure-Template-Analysis-260726.md` — thêm mục ghi kết quả kèm **số đo thật**
   (delta thật của phụ cấp đã test, không phải mô tả).
3. `self-docs/00-START-HERE.md` — **xoá dòng L7** khỏi bảng lỗi (quy ước: sửa xong thì xoá).
4. `CLAUDE.md` — một dòng nhật ký, mới nhất lên đầu.
5. Ghi **nợ**: `ComputeFormulaImpact` vẫn truyền `empManual = nil` nên ước lượng thiếu cho công thức phụ
   thuộc phụ cấp nhập tay — chưa sửa, có chủ đích.

Bắt đầu bằng bước 1 (đo baseline) và xác nhận lại 4 vị trí đã nêu ở mục "HAI lỗ" (`:802`, `:809`, `:824`,
`:825`) còn khớp code thật, báo cho tôi xem, rồi mới sửa.
