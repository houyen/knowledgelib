---
id: self-docs/engine/company-select-all
canonical_question: 'Technical guide and specification: Xem tất cả công ty  cho HR-admin
  — 090926'
aliases:
- Xem tất cả công ty  cho HR-admin — 090926
- Company Select All 090926
entity_type: how_to
domain: self-docs > engine
last_verified: 2026-09-17
---

# Xem tất cả công ty (Select All) cho HR-admin — 090926

**Canonical doc** cho `llmwiki/wiki/sources/draft/090926-company-select-all.md` (SPEC) +
`090926-company-select-all-PLAN.md` (PLAN).

## Bối cảnh

User (HR-admin) yêu cầu 2 việc từ 2 ảnh chụp màn hình:
1. Dropdown "Chọn công ty" ở thanh tiêu đề `/Core System` hiện chỉ single-select — phải đổi qua lại
   giữa Enterprise/UNI/CVT để xem dữ liệu từng công ty. Muốn thêm "Tất cả" để xem gộp Bảng lương/Bảng
   công/Bảng công phụ cấp trong 1 lần, mặc định (lần hiển thị đầu) sort liên tiếp theo mã NV.
2. Trang cấu hình quyền (khối "Công ty được thấy — Enterprise/UNI/CVT" trong Ma trận theo Role) thêm 1
   cờ "Tất cả" — tick đủ 3 công ty thì cờ tự bật; role có cờ này tự thấy công ty MỚI thêm sau này.

## Quyết định đã chốt qua AskUserQuestion

1. **Phạm vi kỹ thuật**: làm cả 3 sheet ngay (kể cả Bảng công/phụ cấp — dù khó hơn Bảng lương vì
   proxy sang Workday adapter chỉ nhận 1 `company_id`/lần gọi — chấp nhận cần N request song song).
2. **Ý nghĩa cờ "Tất cả"**: tự động thấy công ty MỚI sau này (không phải chỉ tick nhanh 3 ô hiện
   có) — đồng bộ 2 chiều với 3 ô Enterprise/UNI/CVT.
3. **Nút "Tất cả" ở dropdown**: CHỈ hiện cho role `hr_admin` (hardcode, không áp dụng role khác dù
   được thấy ≥2 công ty).
4. **Làm rõ bổ sung** (090926, giữa lúc viết SPEC): "hiển thị liên tiếp theo mã NV" chỉ là thứ tự
   MẶC ĐỊNH lúc hiển thị lần đầu — không khoá cứng, người dùng vẫn tự sort cột khác được sau đó.

## Phát hiện quan trọng lúc khảo sát (trước khi code)

- **Bảng lương dễ hơn dự tính ban đầu**: `payroll_record_repo.go` `GetRows` đã có sẵn cơ chế
  `company="" → không lọc` — "Tất cả" chỉ cần 1 sentinel FE dịch sang `undefined`, KHÔNG cần đổi
  backend chút nào (khác SPEC ban đầu tưởng cần sửa SQL).
- **Bảng công/Bảng công phụ cấp khó hơn hẳn**: 2 sheet này KHÔNG đọc DB Core System-backend — proxy
  sang Workday adapter ngoài (`/api/v1/adapter/attendance`, `/timesheet`), chỉ nhận đúng 1
  `company_id`. Đây CHÍNH LÀ lý do "Tất cả" từng bị gỡ khỏi dropdown ở commit 240826.
- **1 mã NV có thể có nhiều dòng payroll_records trong CÙNG kỳ ở nhiều công ty — xác nhận CÓ
  THẬT** (không phải giả định): `employees` có `UNIQUE(employee_code, company_code)`, còn
  `payroll_records` khoá theo `employee_id` (UUID) chứ không theo mã NV.
- **`role_companies`** (khối "Công ty được thấy") xác nhận đúng là bộ lọc giao diện thuần (chính
  migration `v93_role_companies.sql` ghi rõ), tách biệt hoàn toàn với hàng rào bảo mật thật
  (`employee_roles.scope_company_id`, qua `ResolveCompanyScope`) — việc này không đụng tới cơ chế
  bảo mật thật, chỉ mở rộng bộ lọc giao diện.

## Việc đã làm

### Backend (`Core System-backend`, nhánh `feature/company-select-all-090926`)

- `migrations/v99_roles_sees_all_companies.sql` — cột `roles.sees_all_companies boolean NOT NULL
  DEFAULT false`. Đã áp dụng lên DB dev (xác nhận bằng `\d roles`).
- `internal/middleware/role_company.go` (`RoleCompanyCodes`) — nếu bất kỳ role nào trong danh sách
  có cờ true, bỏ qua `role_companies`, trả thẳng toàn bộ công ty active (role tự thấy công ty mới).
- `internal/handler/role_handler.go` (`GetCompanies`/`UpdateCompanies`) — đổi contract từ
  `[]string` trần sang `{codes, seesAll}`. `UpdateCompanies` đồng bộ 2 chiều trong 1 transaction:
  tick đủ toàn bộ công ty active hiện có → tự bật `seesAll=true`; `seesAll=true` gửi lên → tự tick
  đủ toàn bộ hiện có.
- `internal/handler/role_companies_integration_test.go` (mới, 2 test DB thật) — xác nhận cả 2
  chiều đồng bộ + việc role đã `seesAll=true` tự thấy 1 công ty vừa thêm sau đó.

### Frontend (`Core System-frontend`, cùng nhánh)

- `lib/api/roles.ts` — `getRoleCompanies`/`updateRoleCompanies` đổi theo contract backend mới.
- `components-page/tinh-luong/data.ts`:
  - `ALL_COMPANIES_SENTINEL` + `resolvePayrollRowsCompanyFilter` — Bảng lương dịch sentinel sang
    `undefined` (tái dùng cơ chế có sẵn, 0 thay đổi backend).
  - `fetchAdapterAllCompanies` — Bảng công/phụ cấp: N request song song (`Promise.allSettled`),
    gộp + sort theo mã NV, trả kèm danh sách tên công ty lỗi (không chặn công ty còn lại).
  - `adapterRes`/`timesheetRes` branch theo sentinel; 2 field mới
    `adapterAllFailedCompanies`/`timesheetAllFailedCompanies` trong `PayrollData`.
  - `data.test.ts` (mới) — 5 test cho 2 hàm thuần trên.
- `components-page/tinh-luong/TinhLuongExcel.tsx`:
  - Dropdown "Chọn công ty" thêm dòng "Tất cả" (`auth.hasRole("hr_admin")`), sửa
    `companyToAutoSelect`/`companyInScope` call site để không tự huỷ/ẩn nhầm nút Duyệt khi đang ở
    sentinel.
  - 2 `useEffect` toast báo công ty nào tải lỗi (Bảng công/phụ cấp, "Tất cả" đang bật).
  - Ma trận theo Role: state `roleSeesAllCompanies`, `toggleRoleSeesAllCompanies` mới, dòng "Công
    ty được thấy — Tất cả" trong bảng quyền (đồng bộ 2 chiều UI với 3 ô hiện có).

## Kiểm chứng

- **Backend**: `go build`/`go vet` sạch. `go test ./internal/...`: baseline đo bằng `git stash -u`
  = 1007 passed/9 failed → sau = 1008 passed/10 failed — +1 fail là
  `TestIntegration_FindAmong_ReturnsAllRegardlessOfStatus`, xác nhận **FLAKY tiền tồn tại** (pass
  khi chạy riêng lẻ `-run` đúng test đó), không phải hồi quy do đổi này. +2 test mới (Task 2) pass.
  Dọn sạch dữ liệu test (`test_role_090926*`, `TEST090926`) khỏi DB dev sau khi chạy.
- **Frontend**: `tsc --noEmit` sạch (3 lỗi tiền tồn tại không liên quan,
  `public/backup/payslip-lib.test.ts`). `eslint` sạch trên mọi file sửa. `vitest run`: 243/0 (+5
  test mới so với baseline 235, 0 hồi quy).
- Chưa kiểm bằng Playwright/tay trên dev server trong phiên này (không khởi động được trình
  duyệt). Khuyến nghị user tự kiểm: (1) dropdown "Tất cả" chỉ hiện cho tài khoản hr_admin; (2)
  chọn "Tất cả" ở cả 3 sheet, xác nhận dữ liệu gộp đúng + 1 mã NV nhiều dòng nằm liên tiếp; (3)
  trang Ma trận theo Role — tick đủ 3 công ty tự bật cờ "Tất cả", bật cờ trực tiếp tự tick đủ 3 ô;
  (4) mô phỏng 1 công ty adapter lỗi để xác nhận banner lỗi từng phần không chặn 2 công ty còn lại.

## Trạng thái git

Nhánh `feature/company-select-all-090926` (cả 2 repo, tạo mới từ `develop_v1` mới nhất theo chỉ
định trực tiếp của user — KHÔNG dùng `sec_dev`/`chore/rbac-settings-audit-080926`).

- **Backend**: 2 commit — `15909c9` (migration), `630c1ea` (đồng bộ 2 chiều `RoleCompanyCodes` +
  `RoleHandler`). 0 conflict với `develop_v1`.
- **Frontend**: 2 commit — `760ca39` (API client + Ma trận theo Role), `384059c` (sentinel Bảng
  lương + N-request Bảng công/phụ cấp). 0 conflict với `develop_v1`.

Đã push cả 2 repo (nhánh mới hoàn toàn, không force) — chờ user tạo MR sau khi tự kiểm tay.

## SPEC/PLAN nguồn

- `llmwiki/wiki/sources/draft/090926-company-select-all.md` (SPEC, đã duyệt 090926)
- `llmwiki/wiki/sources/draft/090926-company-select-all-PLAN.md` (PLAN, 7 task)
