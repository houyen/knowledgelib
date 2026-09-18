---
id: self-docs/engine/rbac-settings-modules-ui-audit
canonical_question: 'Technical guide and specification: Rà soát 29 module RBAC trước
  khi tái cấu trúc UI phân quyền — 04/09/2026'
aliases:
- Rà soát 29 module RBAC trước khi tái cấu trúc UI phân quyền — 04/09/2026
- RBAC Settings Modules UI Audit 040926
entity_type: how_to
domain: self-docs > engine
last_verified: 2026-09-17
---

# Rà soát 29 module RBAC trước khi tái cấu trúc UI phân quyền — 04/09/2026

## Bối cảnh

Trong lúc kiểm tra tính năng "chốt công lại → ghi đè lương" (xem
`self-docs/RBAC-Improvement-Analysis-040926.md`), user mở màn "Ma trận theo User"
(`components-page/tinh-luong/TinhLuongExcel.tsx`, `MATRIX_SHEET_ID`) và thấy 13 module nhóm
"Cài đặt (Settings.\*)" — mỗi module có 6 cột hành động (View/Edit/Export/Approve/Lock...) để tick
quyền. Câu hỏi đặt ra: **các module này thật sự cấu hình ở đâu trên giao diện, và nếu chưa có nơi
cấu hình thì dữ liệu đứng sau đang lấy từ đâu?**

Tài liệu này rà soát toàn bộ **29 module** trong `lib/rbac-constants.ts` (13 module `Settings.*` ở
Phần 1, và 16 module "Main nav" còn lại ở Phần 2) — bảng DB đứng sau, route backend, vị trí UI
thật (nếu có), và đưa ra đánh giá ưu/nhược để cân nhắc trước khi tái cấu trúc màn hình phân quyền.
**Chỉ nghiên cứu, không sửa code.**

## Cách đọc bảng dưới

- **Có view** = có 1 màn hình thật, được gắn vào menu/ribbon/tab, người dùng bấm tới được mà không
  cần gõ URL tay.
- **Có trang, mồ côi (orphan)** = code trang tồn tại, chạy được, gọi đúng API thật — nhưng KHÔNG
  được liên kết từ bất kỳ menu/ribbon/nút nào trong app. Chỉ vào được nếu biết gõ đúng URL.
- **Không có view** = không có bất kỳ file trang nào trong FE ứng với module đó.
- **Dữ liệu "đông cứng"** = bảng DB có thật, có API sửa thật, nhưng toàn bộ các dòng hiện tại có
  cùng 1 `created_at`/`updated_at` — tức được nạp 1 lần bằng migration seed, chưa từng có ai sửa
  qua API kể từ đó (khác với "hardcode trong code Go", nhưng hệ quả thực tế tương đương: đổi số
  phải qua API/psql tay).

## Phần 1 — 13 module "Cài đặt" (Settings.*)

## Bảng tổng hợp 13 module

| # | Module (`Settings.*`) | Nhãn hiển thị | Bảng DB | API backend | Vị trí UI thật | Trạng thái |
|---|---|---|---|---|---|---|
| 1 | `Insurance` | Bảo Hiểm & Thuế | `insurance_configs` | `GET/POST /insurance` | Ribbon "Cấu hình" → mở rộng → tile "Bảo hiểm & Thuế" | **Có view** |
| 2 | `LeaveTypes` | Loại Ngày Nghỉ | `leave_type_configs` | `GET/POST/PUT/DELETE /leave-types` | Ribbon "Cấu hình" → mở rộng → tile "Loại ngày nghỉ" | **Có view** |
| 3 | `PublicHolidays` | Ngày Lễ | `public_holidays` | `GET/POST/PUT/DELETE /public-holidays` | Ribbon "Cấu hình" → mở rộng → tile "Ngày lễ" | **Có view** |
| 4 | `Roles` | Phân Quyền | `roles` | `GET/POST/PUT/DELETE /roles` | Ribbon "Cấu hình" → tile "Phân quyền" | **Có view** |
| 5 | `System` | Cấu Hình | `system_config` (key-value) | `GET/PUT /system` | — | **Không có view** |
| 6 | `Overtime` | Tăng Ca | `ot_multiplier_configs` | `GET/POST/PUT /ot-multipliers` (CRUD đầy đủ) | Trang `/v1/settings/overtime/page.tsx` tồn tại, code hoàn chỉnh (view+edit+create) | **Có trang, mồ côi hoàn toàn** — không import ở bất kỳ đâu, kể cả `/admin` |
| 7 | `Audit` | Audit Logs | `audit_logs` | `GET /audit-logs` (gate thật bằng `requireAdmin`, **KHÔNG PHẢI** `Settings.Audit`) | 2 nơi trùng lặp: (a) sheet "Audit log" trong app chính, mở qua tab "Lịch sử" — **đang dùng thật**; (b) trang `/v1/settings/audit/page.tsx`, cùng gọi `api.getAuditLogs()`, chỉ tới được qua `/admin` → tab "Audit Logs" | **Quyền ma + trùng lặp UI** (xem phân tích riêng bên dưới) |
| 8 | `SalaryComponents` | Thành Phần Lương | `salary_components` | CRUD đầy đủ | Tab **"Công thức"** trên thanh tab chính → sheet "Danh sách cột lương" | **Có view** (nhưng khác biệt hẳn vị trí — không nằm trong ribbon "Cấu hình" như 4 module trên) |
| 9 | `PITBrackets` | Bậc Thuế TNCN | `pit_brackets` | `GET/POST/PUT/DELETE /pit-brackets` (CRUD đầy đủ) | — | **Không có view** |
| 10 | `TransportAllowances` | Phụ Cấp Đi Lại | `allowance_configs WHERE code='TRANSPORT_KM'` | `GET/PUT /transport-allowances` | Trang `/v1/settings/transport-allowances/page.tsx` tồn tại | **Có trang, mồ côi hoàn toàn** — không import ở bất kỳ đâu |
| 11 | `PeriodConfig` | Cấu Hình Kỳ Lương | `payroll_period_config` | `GET/PUT /period-config` | `/admin?tab=Core System-period-config` (nhãn "Chu Kỳ & Lịch Tự Động", nhóm "Vận hành") | **Có view** (qua `/admin`) |
| 12 | `EmployeeLevels` | Bậc Nhân Viên | `employee_levels` | CRUD | Ribbon "Cấu hình" → mở rộng → tile "Cấp bậc nhân viên" | **Có view** |
| 13 | `ApprovalRules` | Cấu Hình Duyệt | `approval_rules` | `/admin/approval-rules` CRUD | 2 nơi: (a) sheet "Ma trận theo Role", 2 dòng "Duyệt bảng lương — cấp 1/2", gọi **cùng API thật** (`getApprovalRules`/`createApprovalRule`/`updateApprovalRule`) — **đang dùng thật**; (b) trang `/v1/settings/approval-rules/page.tsx`, orphan, chỉ tới qua `/admin` → tab riêng | **Quyền hợp lệ, UI đã hợp nhất có chủ đích** — nút ribbon riêng bị ẩn CÓ GHI CHÚ RÕ LÝ DO (03/09/2026: "gộp cấu hình duyệt vào ma trận theo role") |

## Phát hiện quan trọng — không chỉ "thiếu UI"

### 1. `Settings.Audit` là "quyền ma" (ghost permission) — 100% không có tác dụng

Grep toàn bộ `internal/` của backend: **không có route nào gate theo `Settings.Audit`**. Route
thật trả dữ liệu audit log (`GET /audit-logs`) được bảo vệ bằng `requireAdmin` (role-based), hoàn
toàn độc lập với module/action permission `Settings.Audit` mà màn "Ma trận theo User"/"Ma trận
theo Role" đang cho tick/bỏ tick. Nghĩa là:

- Tick hay bỏ tick "Audit Logs" cho bất kỳ role nào trong ma trận **không thay đổi bất kỳ hành vi
  thật nào** của hệ thống.
- Đây là ví dụ cụ thể của "quyền ma" đã từng được ghi nhận trong đợt rà soát RBAC trước (`self-docs/
  RBAC-Enhancement-Batch-200826.md`, phát hiện `cb_staff` có `Reports.export=true` nhưng vẫn bị
  chặn bởi `RequireRole` cứng ở tầng ngoài) — cùng loại lỗi, khác chiều (ở đây là quyền tồn tại
  trong UI nhưng backend không đọc nó, thay vì quyền có tồn tại ở DB nhưng bị chặn cứng phía trên).

### 2. Audit Logs có 2 màn hình FE hiển thị CÙNG 1 dữ liệu — dư thừa, dễ lệch UX

`app/(app)/v1/settings/audit/page.tsx` và sheet "Audit log" trong `TinhLuongExcel.tsx` đều gọi
đúng `api.getAuditLogs(limit, offset)` — cùng một nguồn dữ liệu, 2 lần triển khai UI độc lập, khác
hẳn cách phân trang (trang admin dùng `page`/`pageSize` chuẩn; sheet trong app chính tự lặp tới
tối đa 50 trang × 200 dòng = 10.000 dòng rồi dừng). Trang trong `/admin` gần như chắc chắn là bản
cũ hơn, bị bỏ quên sau khi tính năng "Audit log" được port vào app chính (tab "Lịch sử").

### 3. "Ma trận theo User"/"Ma trận theo Role" liệt kê module theo RBAC constant, KHÔNG theo UI thật đang có

`lib/rbac-constants.ts` định nghĩa 13 `MODULE`s cho `Settings.*` — danh sách này được dùng để
DỰNG BẢNG MA TRẬN, hoàn toàn độc lập với việc module đó có màn cấu hình tương ứng hay không. Đây
chính là lý do user thấy 13 dòng đều "đẹp đẽ" như nhau trong ma trận, dù thực tế chỉ 7/13 có UI
thật dễ tìm (Insurance, LeaveTypes, PublicHolidays, Roles, SalaryComponents, PeriodConfig,
EmployeeLevels), 2/13 UI đã hợp nhất có chủ đích vào chỗ khác (Audit → tab Lịch sử, ApprovalRules
→ Ma trận theo Role), và **4/13 hoặc mồ côi hoàn toàn hoặc không tồn tại** (System, Overtime,
PITBrackets, TransportAllowances).

### 4. 2 trang mồ côi (Overtime, TransportAllowances) là code CHẤT LƯỢNG TỐT, không phải nháp bỏ dở

Đọc `app/(app)/v1/settings/overtime/page.tsx`: đầy đủ grid + modal sửa + modal tạo mới + validate
input (`0.1 ≤ hệ số ≤ 10`) + toast thành công/lỗi + chú thích "Điều 98, Bộ Luật Lao động 2019" +
công thức tính. Đây KHÔNG phải trang thử nghiệm — là 1 tính năng hoàn chỉnh bị bỏ quên lúc gắn
route, giống hệt tình huống `otMultiplierRepo` đã ghi nhận trước đó ("có API sửa mà KHÔNG ai đọc"
— nay hoá ra không chỉ thiếu người ĐỌC, mà UI SỬA cũng đã được viết xong, chỉ thiếu 1 dòng
import+route trong `TAB_GROUPS`).

### 5. `system_config` có 1 dòng rác thật trong DB dev

```
key=test_key | value=v | category=test | description=d
```
Không liên quan tính năng nào — rõ ràng là dữ liệu test còn sót lại, nên dọn nếu seed lại DB dev
sạch, không phải việc của tài liệu này nhưng ghi nhận để tránh nhầm là cấu hình thật.

## Ưu/nhược nếu TÁI HIỆN (dựng UI mới) cho từng nhóm — góc nhìn tái cấu trúc

### Nhóm A — Đã có UI, chỉ cần chuẩn hoá vị trí (Insurance, LeaveTypes, PublicHolidays, Roles, EmployeeLevels)

- **Ưu điểm nếu giữ nguyên:** ổn định, đã test qua sử dụng thật, rủi ro thấp nhất.
- **Nhược điểm hiện tại:** nằm trong "Cấu hình ít dùng" (phải bấm mũi `‹›` mở rộng ribbon) — với
  người dùng mới, đây là UX ẩn (progressive disclosure) dễ khiến quản trị viên nghĩ tính năng
  không tồn tại. Nếu tái cấu trúc, nên cân nhắc: các module này có tần suất sửa thấp (đúng lý do
  ban đầu ẩn), nên việc giữ ẩn không sai — chỉ cần đảm bảo LIÊN KẾT trực tiếp từ chính màn ma trận
  phân quyền (bấm vào tên module → nhảy thẳng tới màn cấu hình tương ứng) thay vì phải tự tìm.

### Nhóm B — UI đã hợp nhất có chủ đích (Audit, ApprovalRules)

- **Ưu điểm nếu giữ nguyên:** đúng hướng thiết kế đã chọn (03/09/2026, "gộp cấu hình duyệt vào ma
  trận theo role") — giảm số màn hình rời rạc, đặt cấu hình ngay tại nơi liên quan ngữ nghĩa nhất.
- **Nhược điểm:** khi tái cấu trúc UI phân quyền, nếu chỉ nhìn theo danh sách 13 module RBAC mà
  không biết 2 module này đã "chuyển nhà", rất dễ **vô tình dựng lại UI trùng lặp lần 2** (giống
  case Audit đã trùng lặp thật ở trên) — hoặc ngược lại, xoá nhầm route/API tưởng là orphan trong
  khi nó vẫn đang được sheet khác gọi tới.
- **Khuyến nghị:** nếu tái cấu trúc, nên **xoá hẳn 2 trang orphan trùng lặp** (`/v1/settings/
  audit/page.tsx`, `/v1/settings/approval-rules/page.tsx`) sau khi xác nhận không còn route nào
  trỏ tới, thay vì để tồn tại song song 2 bản — giảm bề mặt bảo trì, tránh 2 bản lệch nhau theo
  thời gian (bản audit hiện đã lệch cách phân trang, là bằng chứng cụ thể việc "để trùng lặp" gây
  drift).

### Nhóm C — Có trang mồ côi, chỉ cần gắn route (Overtime, TransportAllowances)

- **Ưu điểm nếu tái hiện:** **rẻ nhất trong tất cả các nhóm** — code UI đã viết xong, đã gọi đúng
  API thật, chỉ cần thêm 1 dòng import + 1 entry trong danh sách tab (giống các tab khác trong
  `/admin` hoặc thêm tile vào ribbon "Cấu hình"). Không cần thiết kế lại từ đầu, không rủi ro API
  (đã có, đã chạy được).
- **Nhược điểm:** dữ liệu hiện tại (`ot_multiplier_configs`, `allowance_configs` mã
  `TRANSPORT_KM`) đã "đông cứng" từ lúc seed — nếu bật UI sửa cho người dùng thật ngay lập tức, cần
  xác nhận với nghiệp vụ (C&B) rằng các mức hiện tại (hệ số OT theo luật 2019, định mức đi lại theo
  cấp bậc G1/G2/G3 × 5 mốc km) vẫn đúng trước khi mở quyền sửa rộng rãi — mở UI sửa cho 1 bảng dữ
  liệu chưa từng qua ai kiểm tra kỹ có thể làm lộ ra các giá trị sai mà trước giờ không ai để ý vì
  không ai vào xem.
- **Rủi ro kỹ thuật nếu tái hiện:** thấp — không cần đổi schema, không cần đổi backend, chỉ đổi
  routing FE.

### Nhóm D — Có API, không có UI, không có trang mồ côi nào (PITBrackets)

- **Ưu điểm nếu tái hiện:** API đã đầy đủ CRUD (`GET/POST/PUT/DELETE /pit-brackets`), có sẵn
  `ListForDate` (tra bậc thuế hiệu lực tại 1 thời điểm) — làm UI mới không cần đụng backend.
- **Nhược điểm:** phải viết UI **từ đầu, không có sẵn khung để tái dùng** như nhóm C. Dữ liệu hiện
  tại đang lẫn 2 bộ bậc thuế từ 2 đợt seed khác nhau (7 dòng "2009" cũ + 5 dòng "Luật TNCN 2025"
  mới, cùng đang `is_active=true`) — **cần làm rõ với nghiệp vụ bộ nào đang thật sự được dùng để
  tính lương** trước khi dựng UI hiển thị, nếu không UI mới sẽ phơi bày ngay 1 sự mập mờ dữ liệu đã
  tồn tại âm thầm từ trước (đang không ai nhìn thấy vì chưa có màn hình nào hiển thị hết cả 12
  dòng cùng lúc để so sánh).
- **Rủi ro kỹ thuật nếu tái hiện:** trung bình — chủ yếu là rủi ro NGHIỆP VỤ (bậc thuế sai ảnh
  hưởng trực tiếp tới PIT của toàn bộ nhân viên), không phải rủi ro kỹ thuật.

### Nhóm E — Có API, không có UI, không có trang mồ côi (System)

- **Ưu điểm nếu tái hiện:** API đơn giản nhất trong tất cả (key-value generic, `GET/PUT /system`)
  — UI có thể là 1 bảng key/value đơn giản, không cần form riêng cho từng loại.
- **Nhược điểm:** đúng 4 dòng dữ liệu hiện tại (`hris_sync_enabled`, `hris_sync_interval_hours`,
  `ref_tables_enabled`, và 1 dòng rác `test_key`) — phạm vi nhỏ, không rõ có đáng để dựng riêng 1
  màn hình hay nên gộp vào 1 trang "Cấu hình hệ thống" chung rộng hơn (vd gộp cùng cấu hình
  đồng bộ HRIS đang nằm ở tile "Đồng bộ" riêng) — cần quyết định phạm vi trước khi thiết kế, vì
  tên module "Cấu Hình" (System) quá chung chung để suy ra biên giới rõ ràng.
- **Rủi ro kỹ thuật nếu tái hiện:** thấp — API generic, an toàn.

## Tóm tắt cho quyết định tái cấu trúc

| Tiêu chí | A (5 module) | B (2 module) | C (2 module) | D (1 module) | E (1 module) |
|---|---|---|---|---|---|
| Cần code UI mới? | Không | Không (nhưng cân nhắc xoá trùng lặp) | Không (chỉ gắn route) | **Có** | **Có** |
| Rủi ro kỹ thuật | Thấp | Thấp | Thấp | Trung bình | Thấp |
| Rủi ro nghiệp vụ | Thấp | Thấp | Trung bình (dữ liệu chưa ai duyệt lại) | Cao (ảnh hưởng PIT toàn bộ NV) | Thấp |
| Việc cần làm trước khi tái hiện | Thêm liên kết từ ma trận | Xoá bản orphan trùng lặp | Xác nhận số liệu với C&B rồi gắn route | Làm rõ bộ bậc thuế nào đang dùng thật | Quyết định phạm vi "Cấu Hình" gồm những gì |

**Riêng `Settings.Audit`:** không thuộc nhóm nào ở trên vì đây không phải vấn đề "thiếu UI" — đây
là 1 quyền không có tác dụng thật (ghost permission). Nếu tái cấu trúc màn ma trận phân quyền, nên
cân nhắc: (a) xoá hẳn dòng "Audit Logs" khỏi ma trận nếu quyết định audit log mãi mãi chỉ gate theo
role `requireAdmin`, hoặc (b) nối `Settings.Audit` vào đúng route `/audit-logs` để ma trận phân
quyền có tác dụng thật — đây là quyết định thiết kế bảo mật cần user chốt, không tự suy luận.

## Nguồn tra cứu (file:line chính, để đối chiếu khi cần)

- `lib/rbac-constants.ts:23-35,55-67` — danh sách 13 module + nhãn hiển thị
- `internal/app/router.go:238-240,255-256,267-270,578-579` — khai báo permission gate
- `internal/app/router.go:282-284,304,319-320,395-400` — route CRUD Overtime/System/PITBrackets
- `internal/app/router.go:191,590,701` — route Audit logs (`requireAdmin`) và ApprovalRules
- `internal/handler/config_handler.go:99-119` — `GetSystem`/`UpdateSystem`
- `internal/repository/transport_allowance_config_repo.go` — bảng `allowance_configs` mã
  `TRANSPORT_KM`
- `app/(app)/v1/admin/page.tsx:23-49` — danh sách tab thật trong `/admin`, xác nhận Overtime/
  TransportAllowances KHÔNG có mặt
- `app/(app)/v1/settings/overtime/page.tsx`, `app/(app)/v1/settings/transport-allowances/page.tsx`,
  `app/(app)/v1/settings/approval-rules/page.tsx`, `app/(app)/v1/settings/audit/page.tsx` — 4 trang
  đã kiểm orphan/trùng lặp
- `components-page/tinh-luong/TinhLuongExcel.tsx:247-275` (`CONFIG_SOURCES`), `:3093-3108`
  (`onSettingsClick`), `:3343-3372` (sheet Audit log), `:4155-4310` (sheet Ma trận theo Role,
  gồm cả logic Duyệt bảng lương cấp 1/2), `:4049-4155` (sheet Ma trận theo User)
- `components-page/tinh-luong/SettingsRibbon.tsx:143-207` — toàn bộ nút ribbon "Cấu hình" thật
  đang render, bao gồm ghi chú lý do ẩn "Cấu Hình Duyệt"/"Ma trận theo User"

## Phần 2 — 16 module chính (ngoài Settings.*)

16 module còn lại trong `lib/rbac-constants.ts` (dòng 4-19) — nhóm "Main nav", khớp `navItems`
trong `app/(app)/layout.tsx`. Cùng phương pháp Phần 1: route backend nào thật sự
`RequirePermission(db, "<Module>", ...)`, bảng DB, vị trí UI thật, có phải quyền ma không.

### Bảng tổng hợp 16 module

| # | Module | Nhãn hiển thị | Bảng DB | Gate backend thật | Vị trí UI thật | Trạng thái |
|---|---|---|---|---|---|---|
| 14 | `Dashboard` | Dashboard | Không có bảng riêng — tổng hợp từ `employees`/`payroll_records`/`attendance_summary` qua `DashboardService` | **Không có** — `RegisterDashboardRoutes` (`router.go:186-188`) gọi thẳng `transportdashboard.RegisterRoutes(r, handlers.Dashboard)`, **0 middleware permission nào** | `/v1/dashboard`, có trong `navItems` (`app/(app)/layout.tsx:42-47`) | **Quyền ma** — ai đăng nhập cũng gọi được route, tick/bỏ tick vô nghĩa |
| 15 | `PayrollPeriods` | Kỳ Lương | `payroll_periods` | `router.go:457-458` (`view`/`edit`) — có thật | 2 nơi: ribbon "Cấu hình" (app chính) → tile "Kỳ lương" (CRUD đầy đủ, có modal sửa); VÀ `/admin?tab=Core System-periods` (cùng `PayrollPeriodsPage`, import ở `admin/page.tsx:29`) | **Có view, 2 nơi cùng 1 trang** (không trùng lặp thật — `/admin` chỉ nhúng lại cùng component, không phải bản viết riêng) |
| 16 | `Timesheets` | Bảng Công Tổng Hợp | Không có bảng riêng cho chính module này — trang thật đọc `attendance_summary` qua `getAttendanceSummaries` | **Không có** — grep `"Timesheets"` (đúng chuỗi) trong `router.go` ra 0 kết quả thật (chỉ 2 dòng COMMENT nhắc tới, không có lệnh `RequirePermission` nào). **Dễ nhầm** với `TimesheetAdapter` (`router.go:177`, `requireTimesheetView := middleware.RequirePermission(db, "TimesheetAdapter", "view")`) — TÊN GẦN GIỐNG nhưng là 2 permission string HOÀN TOÀN KHÁC NHAU, gate 1 route sync-adapter khác, không liên quan | `/v1/timesheets`, có trong `navItems` (`app/(app)/layout.tsx:54-58`) — trang **thật, hoạt động**, nhưng dùng API của module `AttendanceSummary`, không phải của chính nó | **Quyền ma** — và dễ gây nhầm lẫn nhất trong toàn bộ 29 module vì có 1 permission tên rất giống (`TimesheetAdapter`) THẬT SỰ tồn tại ở chỗ khác |
| 17 | `AttendanceDaily` | Bảng Công Chi Tiết | `hris_attendance_daily` | `router.go:653-655` (`view`/`edit`/`export`) — có thật | `/v1/attendance-daily/v2`, có trong `navItems` | **Có view** |
| 18 | `AttendanceSummary` | Chốt Công Tổng Hợp | `attendance_summary` | `router.go:711-712` (`view`/`edit`) — có thật | **Không có trang riêng mang tên này** — dữ liệu hiển thị chung trong trang `/v1/timesheets` (module #16 ở trên gọi `getAttendanceSummaries`) | **Có view, nhưng dùng ké UI của "Timesheets"** — ranh giới 2 module mờ, cùng 1 màn hình |
| 19 | `AttendanceComputed` | Chốt Công Chi Tiết (Per Org) | `attendance_computed` | `router.go:728-729` (`view`/`edit`) — có thật | **Không tìm thấy** — grep `AttendanceComputed`/`getAttendanceComputed` trong toàn bộ `app/` ra 0 kết quả | **Không có view** |
| 20 | `AllowanceOverrides` | Ghi Đè Phụ Cấp | `allowance_overrides` | `router.go:838-841` (`view`/`create`/`edit`/`delete`, đủ 4) — có thật | `/v1/Core System-inputs` (nhãn "Phụ Cấp Duyệt Riêng"), có trong `navItems` | **Có view** |
| 21 | `Core System` | Tính Lương | `payroll_records` (+ toàn bộ engine tính lương) | `router.go:503-507` (`view`/`edit`/`approve`) — có thật | `/v1/Core System` — bảng tính lương Excel-style chính của app, có trong `navItems` | **Có view** |
| 22 | `Employees` | Nhân Viên | `employees` | `router.go:794-797` (`view`/`create`/`edit`/`delete`, đủ 4) — có thật | `/v1/employees`, có trong `navItems` | **Có view** |
| 23 | `Departments` | Phòng Ban | `org_structures` | `router.go:753-754` (`view`/`edit`) — có thật | `/v1/departments`, có trong `navItems` | **Có view** |
| 24 | `Companies` | Pháp Nhân / Công Ty | `companies` | `router.go:759-762` (`view`/`create`/`edit`/`delete`, đủ 4 — CRUD ĐẦY ĐỦ NHẤT trong nhóm này) — có thật | `/v1/companies` → `CompanyManager` component (CRUD hoàn chỉnh: form tạo/sửa/xoá, `api.getCompanies/createCompany/updateCompany/deleteCompany`) — nhưng **KHÔNG có trong `navItems`** | **Có trang, mồ côi hoàn toàn** — giống hệt mẫu Overtime/TransportAllowances ở Phần 1: code CRUD đầy đủ, chỉ thiếu 1 dòng trong `navItems` |
| 25 | `Reports` | Báo Cáo | Nhiều bảng tuỳ loại báo cáo (không có 1 bảng cố định) | `router.go:197` (`export`, ít nhất) — có thật | `/v1/report`, có trong `navItems` | **Có view** |
| 26 | `HrisApi` | HRIS API | Không có bảng riêng | **Không có** — grep chuỗi `"HrisApi"` trong toàn bộ `internal/` ra **0 kết quả** | Có thể liên quan `/admin?tab=sync`/`workday-sync` (`SyncControlPage`/`WorkdaySyncPage`, nhóm "Vận hành") nhưng 2 route đó gate bằng `requireAdmin` (role), không đọc `HrisApi` | **Quyền ma** |
| 27 | `HrisPayrollReport` | Báo Cáo Phụ Cấp HRIS | Không rõ | **Không có** — 0 kết quả cho `HrisPayrollReport` trong `internal/` | **Không tìm thấy trang nào** trong `app/` ứng với nhãn này | **Quyền ma + không có view** — nặng nhất trong nhóm ghost, không có gì cả 2 phía |
| 28 | `EssProfile` | Hồ Sơ Nhân Viên (ESS) | `employees` (qua các API `getEmployee*` dùng chung) | **Không có route `/ess/*` nào tồn tại trong backend** — grep `"/ess"` trong toàn bộ `internal/` ra 0 kết quả | `/v1/ess/profile` — trang **thật, code hoàn chỉnh** (form hồ sơ + phụ thuộc + học vấn + kinh nghiệm...), gọi `api.getESProfile()`→`/api/v1/ess/profile` | **UI có thật nhưng API 404 — TÍNH NĂNG HỎNG HOÀN TOÀN**, xem phân tích riêng bên dưới |
| 29 | `EssPayslip` | Phiếu Lương (ESS) | `payroll_records` (qua API riêng) | **Không có** — cùng lý do #28, route `/ess/payslip` không tồn tại | `/v1/ess/payslip` — trang thật, gọi `api.getESPayslip(periodId)` → `/api/v1/ess/payslip` | **UI có thật nhưng API 404 — TÍNH NĂNG HỎNG HOÀN TOÀN** |

### Phát hiện quan trọng — Phần 2

#### 6. Portal tự phục vụ nhân viên (ESS) đang HỎNG HOÀN TOÀN — không phải thiếu UI, mà API không tồn tại

Đây là phát hiện nghiêm trọng nhất trong toàn bộ 29 module. `app/(app)/v1/ess/{page,profile/page,payslip/page}.tsx` là 3 trang FE **viết đầy đủ, chất lượng tốt** (trang hồ sơ có form sửa dependents/education/work-history/experience/bank-account; trang phiếu lương có chọn kỳ + xem chi tiết) — nhưng gọi tới `/api/v1/ess/profile`, `/api/v1/ess/payslip`, `/api/v1/ess/timesheet`, `/api/v1/ess/leave-details` (khai trong `lib/api/ess.ts`), và **không route nào trong 4 route đó tồn tại ở backend** (grep `"/ess"` trong toàn bộ `internal/` ra 0 kết quả, không phải do đặt tên khác — thật sự không có).

Mức độ nghiêm trọng: `app/(app)/layout.tsx:132-133` cho thấy 2 role `employee` và `search_profile` có **`/v1/ess/profile` là trang DUY NHẤT họ được phép vào** (`ALLOWED_PATHS_BY_ROLE`). Nghĩa là bất kỳ tài khoản nào đang giữ 1 trong 2 role này, đăng nhập vào app, chỉ thấy đúng 1 trang — và trang đó gọi API 404 ngay khi tải. Đây không phải "thiếu view" như PITBrackets/System ở Phần 1 — đây là 1 tính năng tưởng đã xong nhưng chưa từng hoạt động được với dữ liệu thật.

*(Lưu ý phạm vi: không chạy thử UI/API thật trong lần rà soát này để xác nhận response 404 — chỉ xác nhận bằng grep route đăng ký. Nên xác nhận lại bằng 1 request thật trước khi báo cáo lên như sự cố chính thức, dù xác suất route thật sự thiếu là rất cao dựa trên bằng chứng grep.)*

#### 7. `Timesheets` là quyền ma DỄ NHẦM LẪN nhất — có 1 permission tên gần giống thật sự tồn tại

Khác các quyền ma khác (hoàn toàn không có gì gần giống), `Timesheets` dễ đánh lừa người review nhanh vì có `TimesheetAdapter` (`router.go:177`) là 1 permission THẬT, gate 1 route thật (`httpadapter` sync). Ai chỉ `grep -i timesheet` rồi thấy có kết quả sẽ dễ kết luận nhầm là module đã được wire — phải so khớp **chính xác từng ký tự** chuỗi permission mới phát hiện ra đây là 2 thứ khác nhau.

#### 8. `Companies` là bản sao chính xác của mẫu "trang mồ côi chất lượng tốt" đã thấy ở Phần 1

`CompanyManager` component có CRUD đầy đủ (tạo/sửa/xoá công ty, validate, gọi đúng 4 API thật) và backend gate đủ cả 4 action — nhưng **không có dòng nào trong `navItems`** để tới được ngoài gõ URL `/v1/companies` tay. Cùng mẫu với `Overtime`/`TransportAllowances` ở Phần 1: rẻ nhất để "tái hiện" vì chỉ cần thêm 1 dòng nav, không cần đụng code.

#### 9. Ranh giới `Timesheets`/`AttendanceSummary` bị nhoè — 2 module, 1 màn hình

Trang `/v1/timesheets` (nav "Bảng Công Tổng Hợp", ứng với module `Timesheets`) thực chất đọc dữ liệu qua `getAttendanceSummaries` — API đúng ra thuộc phạm vi module `AttendanceSummary`. Nếu tái cấu trúc ma trận phân quyền theo đúng ranh giới module RBAC, sẽ lộ ra câu hỏi: tick quyền `AttendanceSummary.view` có nên là điều kiện thật để vào trang này không, hay nó vẫn tiếp tục không được đọc (vì hiện route thật của trang này không gate theo module RBAC nào rõ ràng — cần xác nhận thêm route cụ thể `getAttendanceSummaries` gọi tới gate nào, việc này nằm ngoài phạm vi rà soát nhanh ở đây).

### Ưu/nhược nếu TÁI HIỆN — nhóm bổ sung từ Phần 2

#### Nhóm F — Ghost permission, KHÔNG liên quan UI thiếu hay đủ (Dashboard, Timesheets, HrisApi, HrisPayrollReport)

- **Đặc điểm chung:** cả 4 đều có string permission trong `lib/rbac-constants.ts`, xuất hiện trong ma trận, nhưng **0 route nào trong backend đọc đúng string đó**. Khác nhóm D/E ở Phần 1 (có API, thiếu UI) — nhóm này có thể có hoặc không có UI, nhưng **API đằng sau không đọc quyền** dù UI có tồn tại hay không.
- **Ưu điểm nếu "sửa" (nối vào route thật):** làm ma trận phân quyền có tác dụng thật — hiện tại tick/bỏ tick 4 dòng này là vô nghĩa, gây hiểu lầm cho người quản trị đang cấu hình.
- **Nhược điểm/rủi ro:** với `Dashboard` và `Timesheets`, đây là 2 trang MỌI role thường dùng — nối permission thật vào có thể vô tình CHẶN người đang dùng nếu default-seed sai (mô hình đang là opt-out: role chưa cấu hình dòng nào = allow-all, nên nối thêm gate mới về lý thuyết an toàn, nhưng cần test kỹ trước khi bật vì đây là 2 trang lưu lượng cao nhất). `HrisApi`/`HrisPayrollReport` rủi ro thấp hơn nhiều vì phạm vi hẹp, ít người dùng.
- **Khuyến nghị khi tái cấu trúc:** quyết định cho từng dòng riêng — không xử lý đồng loạt 4 module này như 1 nhóm, vì mức độ rủi ro/lưu lượng dùng khác nhau rất xa.

#### Nhóm G — API hoàn toàn không tồn tại, UI đã viết xong (EssProfile, EssPayslip)

- **Ưu điểm nếu tái hiện:** UI KHÔNG cần viết lại — đã có sẵn, chất lượng tốt. Chỉ cần XÂY BACKEND (4 route `/ess/*`) — phần thiếu là ngược hẳn với nhóm C ở Phần 1 (ở đó thiếu route FE, có API; ở đây thiếu route BE, có UI).
- **Nhược điểm:** đây là backend MỚI hoàn toàn, không phải "gắn thêm 1 dòng" — cần thiết kế route thật (query đúng nhân viên theo actor đăng nhập, không phải theo `employeeId` truyền vào — rủi ro bảo mật nếu làm ẩu: 1 nhân viên có thể xem hồ sơ/phiếu lương người khác nếu route không tự suy actor từ token). Rủi ro kỹ thuật + bảo mật đều **cao nhất trong toàn bộ 29 module** vì đây là bề mặt duy nhất user thường (role `employee`) chạm tới.
- **Ưu tiên xử lý:** nên xếp cao nhất trong toàn bộ danh sách "cần làm" — không phải vì tái cấu trúc UI phân quyền, mà vì đây là 1 tính năng cho user thường (không phải admin/C&B) đang hỏng hoàn toàn, ảnh hưởng trải nghiệm nhiều người nhất so với mọi module khác đã liệt kê.

#### Nhóm H — Có đủ view + gate thật, chỉ cần chuẩn hoá (PayrollPeriods, AttendanceDaily, AllowanceOverrides, Core System, Employees, Departments, Reports)

- 7 module này đã đúng chuẩn: có bảng DB rõ ràng, gate backend thật khớp đúng tên module, có UI thật dễ tìm trong `navItems`. Không cần hành động gì khi tái cấu trúc UI phân quyền — nhóm tham chiếu "đúng chuẩn" để so sánh khi thiết kế lại ma trận.

#### Nhóm I — Có gate thật, không có UI riêng (AttendanceComputed)

- Giống nhóm D ở Phần 1 (PITBrackets) — API/permission đã có, chưa từng có màn hình. Rủi ro thấp hơn PITBrackets (dữ liệu per-org attendance, không ảnh hưởng trực tiếp số tiền như bậc thuế), nhưng vẫn cần xác nhận có thật sự cần thiết dựng UI hay đây là 1 permission dự phòng chưa dùng tới.

## Tóm tắt tổng quan — cả 29 module

| Nhóm | Số module | Mô tả ngắn |
|---|---|---|
| A | 5 | Đã có UI, chỉ cần chuẩn hoá vị trí (Insurance, LeaveTypes, PublicHolidays, Roles, EmployeeLevels) |
| B | 2 | UI đã hợp nhất có chủ đích, còn bản orphan trùng lặp (Audit, ApprovalRules) |
| C | 2 | Có trang mồ côi, chỉ cần gắn route (Overtime, TransportAllowances) |
| D | 1 | Có API, không UI, không trang mồ côi — rủi ro nghiệp vụ cao (PITBrackets) |
| E | 1 | Có API, không UI, phạm vi mơ hồ (System) |
| F | 4 | Quyền ma — API không đọc permission (Dashboard, Timesheets, HrisApi, HrisPayrollReport) |
| G | 2 | UI xong, API 404 — tính năng hỏng hoàn toàn, ưu tiên cao nhất (EssProfile, EssPayslip) |
| H | 7 | Đúng chuẩn — có bảng, có gate thật, có UI (PayrollPeriods, AttendanceDaily, AllowanceOverrides, Core System, Employees, Departments, Reports) |
| I | 1 | Có gate thật, không UI riêng (AttendanceComputed) |
| — | 1 | Companies — trang mồ côi chất lượng tốt, cùng mẫu nhóm C nhưng tách riêng vì CRUD đủ cả 4 action (đầy đủ nhất trong mọi module mồ côi) |

**Tổng cộng quyền ma phát hiện được: 5/29** (`Settings.Audit`, `Dashboard`, `Timesheets`, `HrisApi`,
`HrisPayrollReport`) — gần 1/6 tổng số module trong ma trận phân quyền hiện KHÔNG có tác dụng thật
nào khi tick/bỏ tick. Đây là con số cần cân nhắc nghiêm túc trước khi đầu tư công sức tái cấu trúc
GIAO DIỆN ma trận — nếu không xử lý song song phần BACKEND đọc đúng các permission này, giao diện
đẹp hơn vẫn không giải quyết được vấn đề gốc là 1/6 số dòng trong đó không có ý nghĩa gì.

## Nguồn tra cứu bổ sung — Phần 2

- `lib/rbac-constants.ts:4-19,37-52` — danh sách 16 module Main nav + nhãn hiển thị
- `app/(app)/layout.tsx:41-124` — `navItems` thật, `132-133` (`ALLOWED_PATHS_BY_ROLE` cho
  `employee`/`search_profile` chỉ có `/v1/ess/profile`)
- `internal/app/router.go:177` (`TimesheetAdapter`, dễ nhầm với `Timesheets`), `:186-188`
  (Dashboard, 0 middleware), `:457-458` (PayrollPeriods), `:503-507` (Core System), `:653-655`
  (AttendanceDaily), `:711-712` (AttendanceSummary), `:728-729` (AttendanceComputed), `:753-754`
  (Departments), `:759-762` (Companies), `:794-797` (Employees), `:838-841` (AllowanceOverrides),
  `:197` (Reports export)
- `internal/transport/http/dashboard/handler.go` — xác nhận 0 permission middleware
- `lib/api/ess.ts`, `lib/api/timesheets.ts` — API client gọi route không tồn tại
  (`/api/v1/ess/*`) hoặc route tồn tại nhưng không FE nào gọi (`getTimesheets`, dead code)
- `app/(app)/v1/ess/{page,profile/page,payslip/page}.tsx` — 3 trang ESS thật, UI hoàn chỉnh
- `app/(app)/v1/companies/page.tsx` → `components-page/companies/CompanyManager.tsx` — CRUD đầy
  đủ, không có trong `navItems`
- `app/(app)/v1/timesheets/page.tsx` — xác nhận gọi `api.getAttendanceSummaries` chứ không phải
  API riêng của module `Timesheets`

## Trạng thái

Tài liệu nghiên cứu thuần tuý — **không sửa file code nào**. Dùng làm đầu vào cho quyết định thiết
kế lại UI phân quyền cho cả 29 module. Các quyết định cần user chốt trước khi triển khai: (1) số
phận của 5 quyền ma (`Settings.Audit`, `Dashboard`, `Timesheets`, `HrisApi`, `HrisPayrollReport`)
— xoá khỏi ma trận hay nối vào route thật; (2) độ ưu tiên sửa backend ESS (`EssProfile`/
`EssPayslip`, hiện đang hỏng hoàn toàn) so với việc tái cấu trúc UI phân quyền — đây là 2 việc
khác nhau nhưng dễ bị gộp chung nếu chỉ nhìn theo danh sách module; (3) phạm vi "Cấu Hình" hệ
thống (`Settings.System`); (4) xoá orphan trùng lặp đã liệt kê ở Phần 1.
