---
id: self-docs/security/rbac-settings-modules-followup
canonical_question: 'Technical guide and specification: RBAC-Settings-Modules-UI-Audit-040926
  — Follow-up thi hành'
aliases:
- RBAC-Settings-Modules-UI-Audit-040926 — Follow-up thi hành
- RBAC Settings Modules Followup 080926
entity_type: how_to
domain: self-docs > security
last_verified: 2026-09-17
---

# RBAC-Settings-Modules-UI-Audit-040926 — Follow-up thi hành (080926)

**Canonical doc** cho việc thi hành theo `self-docs/RBAC-Settings-Modules-UI-Audit-040926.md` (báo
cáo thuần nghiên cứu, không sửa code). User đọc lại báo cáo, đồng ý với đề xuất thứ tự ưu tiên, yêu
cầu lên plan + code luôn, tự hỏi lại khi có điểm chưa rõ trong lúc làm.

## Nhánh làm việc

Cả 2 repo ban đầu ở `sec_dev` (đúng quy ước RBAC của `CLAUDE.md`) — nhưng `sec_dev` phía frontend
quá cũ (từ 250826), 8 commit riêng của nó là bản CŨ của tính năng duyệt đa cấp đã được làm LẠI tốt
hơn trên `develop_v1` (trang `/v1/approvals` cũ đã bị xoá, chuyển thành sheet trong app chính) —
merge thẳng `develop_v1` vào gây conflict thật (modify/delete trang đó + nhiều file khác). Chốt qua
`AskUserQuestion`: tạo nhánh sạch từ `develop_v1` (không đụng `sec_dev` cũ). Backend `sec_dev` clean
(merge 0 conflict) nên giữ nguyên nhánh, chỉ đổi tên cho khớp cả 2 repo. Cuối cùng đổi tên cả 2
thành `chore/rbac-settings-audit-080926` (theo yêu cầu user "đổi tên nhánh khác cho dễ theo dõi"),
push mới hoàn toàn — không force, không đụng `sec_dev` cũ trên remote.

## Thứ tự ưu tiên đã làm (theo đề xuất gốc, user đồng ý)

### 1. Nav wiring nhanh (nhóm C + Companies) — Core System-frontend

- `layout.tsx`: thêm nav "Pháp Nhân / Công Ty" → `/v1/companies` (`roles: ["hr_admin"]`, khớp ĐÚNG
  gate backend `RegisterCompanyRoutes` chỉ `RequireRole("hr_admin")`, không có `cb_staff`).
- `app/(app)/v1/admin/page.tsx`: thêm 2 tab mới trong nhóm "Cài đặt" — "Hệ Số Tăng Ca"
  (`OvertimePage`) và "Phụ Cấp Đi Lại" (`TransportAllowancesPage`) — cả 2 trang đã viết xong CRUD
  đầy đủ, gọi đúng API thật (`ot_multiplier_configs`, `allowance_configs WHERE code='TRANSPORT_KM'`),
  chỉ thiếu 1 dòng import+route.

### 2. Ghost permissions — 3 quyết định chốt qua `AskUserQuestion`

1. **`Settings.Audit`** → nối gate thật. Backend: `RegisterAuditLogRoutes` nhận thêm `db`, build
   `requireAuditView := middleware.RequirePermission(db, "Settings.Audit", "view")`, truyền vào
   `transportauditlog.RegisterRoutes` làm middleware THỨ 2 (giữ nguyên `requireAdmin`, không nới
   lỏng — combine role+permission, khớp pattern `RegisterConfigRoutes` đã dùng cho các module khác).
2. **`Dashboard`/`Timesheets`** → xoá khỏi ma trận (rủi ro nối gate thật cao hơn lợi ích: 2 trang
   lưu lượng cao nhất, ai đăng nhập cũng vào được theo thiết kế hiện tại).
3. **`HrisApi`/`HrisPayrollReport`** → xoá cả hai (không route/trang nào ứng đúng permission string
   này; `HrisPayrollReport` không có gì cả 2 phía).

`lib/rbac-constants.ts`: xoá 4 module khỏi `MODULES`/`MODULE_LABELS`. Backend: grep xác nhận 0 chỗ
nào trong `internal/` tham chiếu 4 string này — an toàn xoá phía FE, dữ liệu `role_permissions` cũ
(nếu có) trở thành hàng vô hại.

### 3. ESS Phase 1 — phát hiện quan trọng làm đổi hẳn phạm vi

Khảo sát ban đầu (dùng Explore agent) map đầy đủ hợp đồng dữ liệu 7 route `/api/v1/ess/*` mà FE gọi
(`lib/api/ess.ts`) — tất cả 404. Hỏi qua `AskUserQuestion` lần 1: user chọn "làm cả 7 route".

**Trước khi code, phát hiện bằng `git log`/`git show`:** toàn bộ `ess_handler.go` (362 dòng),
`hris_cookie_client.go` (595 dòng, client scrape cổng portal HRIS qua cookie), route `/ess/*` +
`/timesheet/*` **đã bị XOÁ CÓ CHỦ ĐÍCH** đúng 5 ngày trước (03/09/2026, commit `f6b64ca "Remove
legacy ESS and timesheet stacks"`, tác giả đồng nghiệp Phạm Bằng), nằm giữa 1 chuỗi commit rõ ràng:
`Remove legacy HRIS connector sync paths` → `Disable automated HRIS sync scheduling` → **`Remove
legacy ESS and timesheet stacks`** → `Add per-diem & special allowances to attendance` — khớp hướng
dứt điểm rời HRIS-cookie sang Workday (đã thấy nhiều ở `Core System-adapter`). File
`internal/service/employee_profile.go` có comment xác nhận: 2 hàm `UpdateProfile`/`UpdateProfileRef`
được cố tình giữ lại (đổi tên file để "không ai xoá nhầm") vì HR-admin path vẫn cần, còn lại toàn bộ
cơ chế ESS-tự-scrape thì bỏ hẳn.

**Báo lại user, hỏi lần 2 (qua `AskUserQuestion`):** dựng lại đúng 7 route kiểu cũ có thể trùng/lệch
hướng đồng nghiệp đang làm. User chốt: **chỉ Profile+Payslip** (dữ liệu DB thuần, không đụng HRIS),
dừng ở đó cho timesheet/calendar/leave-details.

**Thi hành (Core System-backend):**
- `internal/handler/employee_handler.go`: tách hàm `applyEmployeeProfilePatch(current, patch)` từ
  `UpdateProfileByID` — merge-patch logic dùng CHUNG cho cả đường HR-admin (id từ URL) lẫn
  self-service (id từ actor email) — không lệch dần theo thời gian.
- `internal/handler/ess_handler.go` (mới): `EssHandler.GetProfile`/`UpdateProfile`/`GetPayslip` —
  employeeID LUÔN suy từ `actorEmail(r)` (email trong JWT/dev-auth), KHÔNG BAO GIỜ nhận từ
  query/body — an toàn để mở cho MỌI role đã đăng nhập, không có đường IDOR.
- `internal/service/payroll_service.go`: thêm `GetRecordForEmployeePeriod` — wrapper mỏng lộ
  `recordRepo.GetByEmployeePeriod` (trước chỉ dùng nội bộ) ra ngoài cho `EssHandler.GetPayslip`.
- `internal/app/router.go`: `RegisterEssRoutes` — KHÔNG gate role/permission nào (khớp đúng bản gốc
  trước khi gỡ, xem `git show f6b64ca^`), chỉ 3 route (`GET/PUT /ess/profile`, `GET /ess/payslip`),
  bỏ hẳn `timesheet`/`leave-details`/`timesheet-raw`/`attendance-calendar`.
- `internal/handler/ess_handler_integration_test.go` (mới, DB thật): 6 test — trong đó 2 test IDOR
  cốt lõi (`TestIntegrationEssUpdateProfile_PersistsPatchForOwnRecordOnly`,
  `TestIntegrationEssGetPayslip_ReturnsOwnRecordOnlyNotOtherEmployeeSamePeriod`) dựng 2 nhân viên
  A/B, xác nhận A không bao giờ thấy/sửa được dữ liệu B dù cùng kỳ lương.

**Thi hành (Core System-frontend):**
- `lib/api/ess.ts`: xoá 4 hàm gọi route không còn tồn tại (`getESTimesheet`, `getESLeaveDetails`,
  `getESTimesheetRaw`, `getESAttendanceCalendar`).
- `app/(app)/v1/ess/page.tsx`: bỏ "Leave Balance Card", "Attendance Log (Calendar View)", "Monthly
  Standard Circular Chart" (tất cả phụ thuộc 2 nguồn dữ liệu đã gỡ) — giữ nguyên phần thu nhập ước
  tính + phụ cấp (dựa trên payslip thật, vẫn hoạt động).
- `app/(app)/layout.tsx`: **phát hiện phụ, sửa luôn** — `navItems` trước hoàn toàn không có mục nào
  href bắt đầu `/v1/ess`, dù `ALLOWED_PATHS_BY_ROLE` (dead code, không được `useRoleGuard` đọc) tưởng
  đã cho phép role `employee`/`search_profile` vào `/v1/ess/profile`. `useRoleGuard.isAllowed` (chỉ
  đọc `navItems`) do đó luôn coi `/v1/ess/*` là KHÔNG được phép với MỌI role — thêm 2 nav "Hồ Sơ Của
  Tôi"/"Phiếu Lương Của Tôi" (không `roles` = mọi người đăng nhập, khớp thiết kế ESS không gate role).

## Việc cố ý KHÔNG làm (để đợt sau, cần quyết định thêm)

- **ESS timesheet/attendance-calendar/leave-details/timesheet-raw**: nguồn dữ liệu HRIS-portal-scrape
  cũ đã gỡ, cần thiết kế MỚI từ `attendance_department_segments`/`attendance_segment_aggregates`
  (không có sẵn per-ngày status như bản cũ) — hoặc quyết định bỏ hẳn tính năng lịch/phép trong ESS.
- **`Settings.PITBrackets`**: có API đầy đủ, chưa có UI — nhưng dữ liệu đang lẫn 2 bộ bậc thuế (7
  dòng "2009" cũ + 5 dòng "Luật TNCN 2025" mới, cùng `is_active=true`) — cần C&B xác nhận bộ nào
  đang dùng thật trước khi dựng UI hiển thị.
- **`Settings.System`**: có API, chưa có UI — phạm vi "Cấu Hình" hệ thống chưa rõ ranh giới (gộp
  cùng cấu hình đồng bộ HRIS ở tile "Đồng bộ" hay tách riêng) — cần quyết định phạm vi trước khi
  thiết kế.

## Kiểm chứng

- **Backend**: `go build ./...`, `go vet ./...` sạch. `go test ./internal/...` với
  `TEST_DATABASE_URL` bật: baseline đo bằng `git stash` = 989 passed/8 failed → sau = 998 passed/8
  failed (đúng 8 tên fail tiền tồn tại, +9 test mới kể cả 6 test ESS) — **0 hồi quy**. Dọn sạch dữ
  liệu test ESS khỏi DB dev sau khi chạy (xác nhận bằng `psql` — 0 dòng còn sót các mã NV
  `099801/099811/099812/099821/099831/099832/099841`).
- **Frontend**: `tsc --noEmit` sạch (3 lỗi tiền tồn tại không liên quan,
  `public/backup/payslip-lib.test.ts`). `eslint` sạch trên mọi file sửa. `vitest run`: 235/0 (khớp
  baseline).
- Chưa kiểm bằng Playwright/tay trên dev server trong phiên này (không khởi động được trình duyệt).
  Khuyến nghị user tự kiểm: (1) tab "Hệ Số Tăng Ca"/"Phụ Cấp Đi Lại" trong `/admin`; (2) nav "Pháp
  Nhân / Công Ty"; (3) trang `/v1/ess/profile` (xem+sửa hồ sơ) và `/v1/ess/payslip` với tài khoản
  role `employee` thật.

## Đợt bổ sung 080926-2 — Chuyển 3 view "nhóm C" vào Excel /Core System

Sau khi hoàn tất đợt 1 (nav wiring nhanh cho Overtime/TransportAllowances/Companies bằng
trang React cũ), user yêu cầu tiếp: "mọi view, giao diện luôn xem ở version 'excel' /Core System,
những view nào ở version cũ nếu sử dụng tới ở thay đổi này thì hãy thay đổi về format mới và đưa
vào /Core System". Chốt qua `AskUserQuestion` phạm vi: chỉ 3 view admin (Companies/Overtime/
TransportAllowances) — **không** gồm ESS Profile/Payslip (form cá nhân cho nhân viên thường, khác
đối tượng người dùng, không hợp khuôn bảng Excel).

Khảo sát mẫu sheet CRUD hiện có trong `TinhLuongExcel.tsx` trước khi code (dùng Explore agent) —
phát hiện quan trọng: chỉ sheet **"Phân quyền" (Roles)** có đủ create+edit+delete, không phải
"Loại ngày nghỉ" như giả định ban đầu (sheet đó chỉ có edit). Dùng "Phân quyền" làm khuôn mẫu thật.

**Chuyển đổi:**
- **"Pháp Nhân / Công Ty"** (CompanyManager cũ) — CRUD đầy đủ, đúng khuôn Roles 100%: `companyModal`
  state (mirror `roleModal`), `openCompanyModal`/`saveCompanyModal`/`deleteCompanyWithConfirm`,
  modal `<Modal>` inline với các field từ `CompanyDrawer` cũ (mã khoá khi sửa, các field liên hệ).
  Xoá = xoá MỀM (backend tự đánh dấu `is_active=false`), câu confirm nói rõ để không nhầm vĩnh viễn.
- **"Hệ Số Tăng Ca"** (OvertimePage cũ) — create+edit (không delete, khớp API cũ không có). Giữ 2
  cột suy diễn "Loại ngày"/"Ca" từ quy ước tiền tố mã (`getDayType`/`getTimeSlot` cũ, port nguyên
  logic). Modal sửa chỉ cho đổi hệ số (khớp `handleSave` cũ chỉ gửi `{multiplier}` partial).
- **"Phụ Cấp Đi Lại"** (TransportAllowancesPage cũ) — **khác bản chất** 2 sheet trên: không phải
  danh sách CRUD mà là **ma trận cố định** 3 nhóm bậc × 5 mốc km (15 ô), không có create/delete API
  ở bản gốc. Chuyển đúng bản chất: `buildTransportAllowanceGrid` pivot dữ liệu phẳng thành bảng 2
  chiều (khớp cách trang cũ làm), sửa từng Ô tại chỗ bằng double-click — dựng mới cơ chế
  `isTransportAmountEdit`/`commitInlineTransportAmountEdit`, **cùng khuôn** `isBonusAmountEdit` đã
  có cho sheet "Tính Thưởng" (070926-4), chỉ khác định danh: 1 ô ở đây là cặp `(group, tier)` thay
  vì 1 `id` đơn — tái dùng `rowIdsSrc` (đã tổng quát hoá 2 đợt trước cho Bonus/Approval Inbox) mang
  mảng mã nhóm bậc cố định `["G1","G2","G3"]` thay vì id thật, để đúng dòng dù người dùng lỡ sort/lọc.

**Dọn lối vào cũ:** bỏ nav "Pháp Nhân / Công Ty" + 2 tab admin "Hệ Số Tăng Ca"/"Phụ Cấp Đi Lại"
vừa thêm sáng cùng ngày (đợt 1) — không giữ 2 lối vào cho cùng 1 chức năng, đúng tinh thần yêu cầu.
**Phát hiện phụ:** `CompanyManager` còn 1 chỗ dùng khác — embed trong `/v1/departments/page.tsx`
(`<CompanyManager refreshKey={companyRefresh} />`) — NGOÀI phạm vi đổi hôm nay (Departments page
không phải 1 trong 3 view được yêu cầu chuyển), cố tình giữ nguyên, ghi lại để cân nhắc dọn ở đợt
sau (hiện tại là 1 dạng trùng lặp UI y hệt case Audit/ApprovalRules đã ghi nhận ở báo cáo gốc).

**Kiểm chứng:** `tsc --noEmit` sạch (3 lỗi tiền tồn tại không liên quan), `eslint` sạch trên 5 file
sửa, `vitest run` 235/0 (khớp baseline). Chưa kiểm tay/Playwright trên dev server trong phiên này.

**Trạng thái:** commit `Core System-frontend@4066997` trên `chore/rbac-settings-audit-080926`, đã push
(0 conflict với `develop_v1`).

## Trạng thái git

Nhánh `chore/rbac-settings-audit-080926` (cả 2 repo, từ `develop_v1`). Backend: 1 commit
(`30fcf7e`), đã push (nhánh mới trên remote). Frontend: 1 commit (`3f888b5`), đã push (nhánh mới
trên remote, KHÔNG đụng `sec_dev` cũ vẫn còn nguyên trên remote để tham chiếu).

## Nguồn

- `self-docs/RBAC-Settings-Modules-UI-Audit-040926.md` — báo cáo gốc (thuần nghiên cứu)
- `Core System-backend` commit `f6b64ca` — "Remove legacy ESS and timesheet stacks" (03/09/2026, bối
  cảnh quan trọng làm thu hẹp phạm vi ESS Phase 1)
