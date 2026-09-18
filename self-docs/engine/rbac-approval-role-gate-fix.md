---
id: self-docs/engine/rbac-approval-role-gate-fix
canonical_question: 'Technical guide and specification: RBAC Approval Role-Gate Fix
  — 030926'
aliases:
- RBAC Approval Role-Gate Fix — 030926
- RBAC Approval Role Gate Fix 030926
entity_type: troubleshooting
domain: self-docs > engine
last_verified: 2026-09-17
---

# RBAC Approval Role-Gate Fix — 030926

**Canonical duy nhất cho hạng mục này.**

## Bối cảnh

User muốn tự test luồng duyệt lương 2 cấp (`cb_lead` cấp 1 → `cb_director` cấp 2, xem
`self-docs/Core System-Multilevel-Approval-Period-Lock-250826.md`) bằng cách tự gán/đổi quyền cho
chính tài khoản mình và quan sát nút Duyệt ẩn/hiện đúng theo cấp. Trước khi viết test, khảo sát
code thật phát hiện **2 bug thật** khiến kịch bản test dự định không phản ánh đúng thiết kế.

## Bug 1 — Router-gate chặn nhầm `cb_lead`/`cb_director` đơn lẻ

`Core System-backend/internal/app/router.go`: toàn bộ nhóm `/approvals/*` (`inbox`, `submit`,
`{id}/act`, `{entityType}/{entityId}`) dùng chung `requireAdminOrCB = RequireRole("hr_admin",
"cb_staff")` — **cùng biến** dùng cho nhiều nhóm route khác (attendance, payslip SFTP...).
`cb_lead`/`cb_director` (seed 250826, `internal/database/database.go`) **không gắn
`parent_role_id`** nên không kế thừa thành `hr_admin`/`cb_staff`.

→ Tài khoản CHỈ có `cb_lead` (hoặc chỉ `cb_director`), không kèm `hr_admin`/`cb_staff`, bị
**403 ngay ở router** — trước cả khi `actorEligible` (approval_service.go) kịp lọc đúng theo cấp.
Thiết kế "role duyệt chuyên biệt" (cb_lead/cb_director) trên thực tế đòi hỏi luôn phải kèm
hr_admin/cb_staff — điều không ai ghi rõ ở đâu.

**Fix:** tách `requireApprovalActor := middleware.RequireRole("hr_admin", "cb_staff", "cb_lead",
"cb_director")` — CHỈ áp cho nhóm `/approvals` (không đổi `requireAdminOrCB` dùng chung, tránh
vô tình mở luôn quyền cb_lead/cb_director vào attendance/payslip SFTP/...). `/admin/approval-rules`
(CRUD cấu hình rule) giữ nguyên `requireAdminOrCB` — cb_lead/cb_director không được sửa rule.

## Bug 2 — `ListInbox` query theo `employee_id`, không theo `email`

Phát hiện khi viết test: tài khoản dev-bypass thuần (không có dòng `employees` tương ứng, đúng
thiết kế "gán quyền theo email" từ 110826) luôn nhận `inbox` **rỗng**, dù đã có role đúng.

`ApprovalService.ListInbox` (`approval_service.go`) query role của actor bằng
`JOIN employees e ON e.id = er.employee_id WHERE LOWER(e.email)=...` — INNER JOIN qua
`employee_id`, trong khi từ 110826 `employee_roles` đã chuyển sang so khớp trực tiếp qua cột
`email` của chính nó (`employee_id` nullable, chỉ để enrich hiển thị — xem
`self-docs/RBAC-Improvement-Analysis-110826.md`). Bất kỳ role gán CHỈ theo email (không kèm
`employee_id`) đều bị hàm này bỏ sót hoàn toàn, âm thầm — không lỗi, chỉ luôn ra rỗng.

**Fix:** đổi query so khớp thẳng `LOWER(er.email)=...`, khớp đúng pattern đã dùng ở
`getAppRoles`/`ResolveCompanyScope`/`ResolveDepartmentScope`. Đồng thời sửa nhánh "actor không có
role nào" trả `[]models.ApprovalRequestWithStep{}` thay vì `nil` — tránh JSON `null` (khác `[]`)
gây lỗi phía client khi gọi `.map()`/`.length` trên response.

## Bug 3 — Khoá kỳ không chặn được luồng duyệt mới `/approvals/{id}/act`

Phát hiện khi đánh giá lại xem case 11 (kỳ khoá → 423) có automate được không. `checkLock()`
(chặn 423 khi kỳ đã khoá thủ công — `PayrollHandler`, `internal/handler/payroll_handler.go`)
**chỉ tồn tại ở 2 route đơn cấp cũ** (`/Core System/approve|reject/{id}`). Route đa cấp mới
(`/approvals/{id}/act`, `approval_handler.go`) **không gọi `checkLock()` ở đâu cả** — kỳ đã khoá
thủ công (`payroll_periods.is_locked=true`) vẫn duyệt/từ chối được xuyên qua route mới ở cả 2 cấp.
Tài liệu 250826 nói đã "hợp nhất `checkLock()`" nhưng chỉ áp dụng cho 2 route đơn cấp, không mở
rộng sang route đa cấp — lỗ hổng có sẵn từ lúc route đa cấp ra đời, không phải do việc hôm nay.

**Fix:** thêm `ErrPeriodLockedForApproval` + kiểm `service.IsAnyPeriodLocked(ctx, db)` ngay đầu
`ApprovalService.Act()` (chỉ áp cho `entityType` liên quan Core System — không chặn nhầm
`salary_component_formula` hay entity khác dùng chung engine duyệt), trả đúng body
`{"error":"locked_manual"}` như 2 route cũ (`approval_handler.go`, `http.StatusLocked`).

## Bug 4 (040926) — `actorEligible` không kiểm actor có THẬT SỰ giữ role của bước hay không

Phát hiện qua review độc lập của đồng nghiệp (Trần Bùi Hoàng Gia, commit FE `abe3766`, cũng dùng
Claude) — họ chỉ mô tả "route cũ `/Core System/approve|reject/{id}` thiếu kiểm vai trò của bước", và
cố ý CHƯA vá backend vì "trùng vùng ThaiDT đang sửa". Xác minh lại (tái hiện thật, không chỉ đọc
code) cho thấy **gốc rễ sâu hơn**: cả route cũ (qua `SubmitOrAct→Act`) LẪN route mới
(`/approvals/{id}/act`) đều gọi chung `ApprovalService.actorEligible` — và hàm này **chưa từng**
kiểm actor có giữ 1 trong role được yêu cầu của bước hay không, chỉ kiểm scope company/site:

```go
companyOK := unlimitedCompany || companyID == nil   // companyID nil → LUÔN true
siteOK := unlimitedSite || orgStructureID == nil     // orgStructureID nil → LUÔN true
```

`cb_lead`/`cb_director` được seed **toàn cục** (`company_id`/`org_structure_id` đều NULL) —
nghĩa là `companyID`/`orgStructureID` trên MỌI request đều `nil`, khiến `companyOK`/`siteOK` LUÔN
`true` bất kể actor giữ role gì. **Tái hiện thật xác nhận**: identity chỉ giữ `cb_lead`+`hr_admin`
(không `cb_director`) gọi thẳng `/approvals/{id}/act` cho 1 request đang ở **cấp 2** — duyệt
**thành công** (200, request đóng "approved"). Việc `ListInbox` lọc đúng theo role (qua
`ListPendingStepsForRoles`) chỉ che giấu bug này ở tầng hiển thị — API vẫn hở hoàn toàn nếu biết
`requestId`.

**Fix:** thêm 1 truy vấn `EXISTS` xác nhận actor giữ ít nhất 1 `roleCodes` **trước** khi tính scope,
ngay đầu `actorEligible` — vá đúng 1 điểm, cả 2 route (cũ + mới) cùng được bảo vệ vì dùng chung hàm.
Tái hiện lại đúng kịch bản đã fail ở trên sau khi vá: `403 {"error":"actor is not eligible to act
on this approval step"}`; cùng identity sau khi được cấp đúng `cb_director` thì duyệt lại thành
công bình thường (200) — xác nhận không chặn nhầm người có quyền thật.

## Test mới — Playwright, 14 case (case 1-9, 11, 12, 13, 14) + 1 Go characterization test (case 15)

File: `Core System-frontend/e2e/Core System-approval-role-gate.spec.ts`. Theo đúng kiến trúc
`Core System-rbac.spec.ts` (dev-bypass, `psql` mutate `employee_roles` trực tiếp, roles đọc live
không cần restart backend) — case 1-6 qua API thật (`request` fixture), case 7 mở trình duyệt
thật (`devLogin` + `page.goto("/v1/approvals")`, bắt response mạng thật).

- Case 1: `cb_lead`+`hr_admin` thấy item cấp 1, không thấy item đã sang cấp 2.
- Case 2: `cb_director`+`hr_admin` thấy item cấp 2, không thấy item còn cấp 1.
- Case 3: có cả 2 role — thấy đúng item ở bất kỳ cấp nào.
- Case 4: `cb_lead` ĐƠN — trước 403, nay 200 (chứng minh bug 1 đã sửa).
- Case 5: `cb_director` ĐƠN — tương tự case 4.
- Case 6: `hr_admin` thuần (không cb_lead/cb_director) — 200 + mảng **rỗng thật** (`[]`), phân biệt
  với case 4/5 cũ (403 bị FE hiện nhầm thành "không có gì").
- Case 7: UI thật với `cb_lead` đơn — `/v1/approvals` tải được (network 200), thấy đúng item.
- Case 8: duyệt cấp 1 xong — chính actor đó (giữ nguyên role suốt, không có `cb_director`) tự mất quyền thấy item đó (đã sang cấp 2).
- Case 9: duyệt cấp 2 (cuối) — request đóng (`status=approved`) VÀ `payroll_records.approved_at` thật sự được ghi (không chỉ đổi status ở `approval_requests`).
- Case 12: cấp quyền qua DB có hiệu lực NGAY ở lần gọi API kế tiếp — không cần restart backend/re-login (tách riêng thành assertion rõ ràng, trước đó chỉ ẩn trong cách case khác đổi role giữa chừng).

- Case 11: kỳ đã khoá (`is_locked`) → `/approvals/{id}/act` PHẢI 423 ở CẢ 2 cấp — tái hiện bug 3 rồi xác nhận đã sửa (mở khoá tạm giữa chừng để đẩy request sang cấp 2, khoá lại kiểm tiếp).
- Case 13: đổi role qua DB **không** tự cập nhật khi điều hướng trong SPA (click `<Link>` thật qua `/v1/dashboard` rồi quay lại — `page.goto()` luôn là full-navigation nên KHÔNG dùng được để mô phỏng đúng trường hợp này) — cần `page.reload()` (F5) mới thấy đúng role mới trong `localStorage.payroll_user`.
- Case 14: banner quá hạn đúng deadline riêng cấp — dùng kỳ có `end_date` trong quá khứ xa (2020), không cần giả lập đồng hồ hệ thống hay chờ thời gian thật trôi qua; `isOverdue=true` ngay từ lúc submit cho cả 2 cấp (`cb_lead` +1 ngày, `cb_director` +5 ngày sau `end_date`).

**Bug 4:** test mới `"bug 4 (040926): actor giữ SAI role..."` — approve level 1 hợp lệ → đổi role
bỏ `cb_director` → gọi thẳng `/act` cho request đang ở cấp 2 → phải 403, request phải giữ nguyên
`status=pending` (không bị đóng nhầm bởi lần gọi sai role này).

**Case 10** (từ chối → đóng, resubmit xoá `rejected_reason`) đã có sẵn test Go từ 250826 (`TestIntegrationResubmitClearsRejectedReason`) — không viết lại.

**Case 15** (2 dòng quyền scope tách rời có thể quá quyền): đánh giá lại — **automate được**, nhưng đúng lớp phải test là hàm middleware (`ResolveCompanyScope`/`ResolveDepartmentScope`), không phải qua Playwright/luồng duyệt — vì `UNIQUE(email, role_id)` không cho 1 actor giữ 2 dòng CÙNG 1 role (kịch bản gốc mô tả), nên phải tái hiện bằng 2 ROLE KHÁC NHAU (`cb_lead` scope company, `cb_director` scope site) rồi gọi 2 hàm resolve với cả 2 mã role — đúng cách `actorEligible` sẽ làm nếu 1 cấp duyệt tương lai chấp nhận nhiều role OR nhau. Viết dưới dạng **test characterization** (`TestCharacterization_TwoSeparateScopedGrantsCombineIntoOverAuthorization`, `internal/middleware/`) theo đúng lựa chọn của user — không khẳng định đúng/sai, chỉ khoá lại hiện trạng để ai sửa `scope.go` sau này biết mình vừa đổi hành vi này.

**Phát hiện fixture phụ khi viết test:** `ApprovalService.Act()` cần
`employeeRepo.GetIDByEmail(actorEmail)` để ghi `ActedBy` (uuid nhân viên) — identity dev-bypass
thuần không có dòng `employees` sẽ lỗi `"resolve actor employee: sql: no rows in result set"`.
Spec tự tạo 1 dòng `employees` tạm (`employee_code='E2E_APPROVAL_ACTOR'`) trong `beforeAll`, tự
xoá trong `afterAll` — không phải bug, chỉ là yêu cầu fixture cần biết trước.

## Kết quả kiểm

- **BE:** `go build`/`go vet` sạch. `go test ./internal/...`: 1058 pass/9 fail — đúng 9 fail tiền
  tồn tại (đối chiếu bằng chạy lặp lại, không đổi danh sách) — 0 hồi quy.
- **Playwright:** 14/14 case pass (case 1-9, 11-14, bug 4) — chạy thật, không phải suy đoán, xác
  nhận qua vòng lặp: sửa router-gate → 4/5 vẫn fail (do bug 2 lộ ra) → sửa `ListInbox` → 7/7 pass
  → thêm case 8/9/12 → 10/10 → phát hiện + vá bug 3, thêm case 11/13/14 → 13/13 → phát hiện + vá
  bug 4 (review đồng nghiệp + tái hiện thật), thêm test bug 4 → 14/14 pass.
- **`go test ./internal/...`**: 1082 pass/10 fail — 9 fail cũ + 1 fail MỚI (`TestTransportFuelTax_Boundary`,
  file `formula_risk_coverage_test.go` do đồng nghiệp thêm cùng đợt pull) — xác nhận bằng `git stash`
  fail y hệt cả khi KHÔNG có fix của tôi → tiền tồn tại từ code đồng nghiệp, không phải hồi quy.
- **Go characterization (case 15):** `TestCharacterization_TwoSeparateScopedGrantsCombineIntoOverAuthorization` pass — xác nhận đúng hiện trạng đã mô tả.
- **FE (vitest/tsc/eslint):** `tsc` 3 lỗi tiền tồn tại (không liên quan), `eslint` sạch, `vitest`
  213 pass/0 fail.
- Đã dọn sạch dữ liệu test (period/record/role/employee tạm) khỏi DB dev sau khi chạy, khôi phục
  `.env`/`super_admins`/backend về đúng identity thật (`user@company.test`, super-admin) trước
  khi kết thúc.

## Trạng thái git

Làm trực tiếp trên `develop_v1` (theo lựa chọn user, không qua `sec_dev` dù đây là hạng mục
RBAC — quyết định rõ ràng của user tại thời điểm làm việc).

- `Core System-backend@develop_v1`: commit `df34b4d` (bug 1+2), `0cf632b` (bug 3 + case 15).
- `Core System-frontend@develop_v1`: commit `d7f3d41` (case 1-7), `c934a3b` (case 8/9/12), `13d691d` (case 11/13/14).
- **Chưa push.**

## Cách chạy lại bộ test này (thủ công, theo đúng đầu file spec)

```bash
# 1. Backend
cp .env .env.e2e-backup
sed -i.bak 's/^DEV_USER_EMAIL=.*/DEV_USER_EMAIL=user@company.test/' .env && rm .env.bak
# restart backend (go run ./cmd/Core System)
psql ... -c "DELETE FROM super_admins WHERE email='user@company.test'"

# 2. Chạy test
cd Core System-frontend && npx playwright test e2e/Core System-approval-role-gate.spec.ts

# 3. Khôi phục
cp .env.e2e-backup .env && rm .env.e2e-backup
# restart backend lại
```
