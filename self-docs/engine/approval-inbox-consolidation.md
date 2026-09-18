---
id: self-docs/engine/approval-inbox-consolidation
canonical_question: 'Technical guide and specification: Duyệt Của Tôi — chuyển vào
  /Core System, quy về 1 mối'
aliases:
- Duyệt Của Tôi — chuyển vào /Core System, quy về 1 mối
- Approval Inbox Consolidation 070926
entity_type: how_to
domain: self-docs > engine
last_verified: 2026-09-17
---

# Duyệt Của Tôi — chuyển vào /Core System, quy về 1 mối (070926)

## Bối cảnh

Trang "Duyệt Của Tôi" (`/v1/approvals`, dựng đợt Multilevel Approval 250826) là một route Next.js
riêng, có nav item riêng trong sidebar. Trong lúc đó, một phiên khác (song song, cùng máy, cùng
nhánh `feature/bonus-engine-phase1`) đã làm y hệt việc này cho tính năng "Tính Thưởng": gỡ trang
`/v1/bonus` độc lập, chuyển toàn bộ UI + logic vào một sheet mới bên trong
`components-page/tinh-luong/TinhLuongExcel.tsx`, mở qua ribbon "Cấu hình". User xem ảnh chụp màn
hình tính năng thưởng, hỏi luồng duyệt tiếp theo nằm ở đâu, rồi yêu cầu thẳng: "Đưa menu này vào
lại trong app Core System, quy về 1 mối" — tức áp dụng đúng khuôn đã có cho "Duyệt Của Tôi".

**Nhánh làm việc:** tiếp tục trực tiếp trên `feature/bonus-engine-phase1` (không tạo nhánh mới,
không chuyển `develop_v1`) — xác nhận qua `AskUserQuestion` vì nhánh này lúc đó đã có 2 commit chưa
push từ phiên song song nói trên; user chọn "Tiếp tục ngay trên feature/bonus-engine-phase1".

## Việc đã làm

**Xoá hẳn:**
- `app/(app)/v1/approvals/page.tsx`, `overdue.ts`, `__tests__/overdue.test.ts` (toàn bộ UI/logic cũ)
- Nav item "Duyệt Của Tôi" trong `app/(app)/layout.tsx` (`navItems`) + 2 chỗ nhắc `/v1/approvals`
  trong `ALLOWED_PATHS_BY_ROLE` (`site_admin`, `cb_staff` — bản thân map này đã ghi chú sẵn là dead
  code, không được `useRoleGuard()` dùng, nhưng vẫn dọn theo cho đồng bộ)

**Thêm mới (`components-page/tinh-luong/`):**
- `i18n.ts` — key `cfgApprovalInbox` ("Duyệt Của Tôi" / "My Approvals")
- `TinhLuongExcel.tsx`:
  - `APPROVAL_INBOX_ENTITY_LABELS` — nhãn hiển thị theo `entity_type`, port từ `ENTITY_TYPE_LABELS`
    cũ (chỉ 2 mục) + bổ sung 3 loại mới đã nối vào `ApprovalService` từ các đợt trước:
    `salary_component_formula`, `insurance_config`, `bonus_period`
  - `Sheet` interface: thêm `approvalInboxItems`/`approvalInboxLoading`/`approvalActingId`/
    `approvalRejectTargetId`/`approvalRejectReason`
  - `openApprovalInboxSheet()`, `loadApprovalInbox()`, `approveInboxItem()`,
    `openRejectInboxItem()`/`submitRejectInboxItem()` — gọi lại đúng `api.getApprovalInbox()`/
    `api.actOnApproval()` đã có sẵn trong `lib/api/approvals.ts`, không đổi API client
  - Router `onSettingsClick`: thêm nhánh `label === "Duyệt Của Tôi"`
  - Khối JSX render mới (absolute-overlay, cùng khuôn với sheet "Cấu Hình Duyệt"/"Tính Thưởng"):
    banner cảnh báo quá hạn, bảng danh sách (Loại·nội dung thay đổi / Cấp / Tạo lúc / Thao tác) với
    khối `detail` (before→after, người yêu cầu, lý do) khi backend trả được, nút Duyệt/Từ chối, modal
    nhập lý do từ chối
  - `SettingsRibbon.tsx`: thêm 1 `<Tile>` mới trong nhóm "Quản lý Lương" — cố ý KHÔNG gắn
    `data-rbac-only`, vì `approval_rules` có thể gán bất kỳ role nào làm người duyệt, không riêng
    hr_admin/cb_staff (đúng comment gốc ở layout.tsx cũ trước khi gỡ)
- `lib/api/types.ts`: `ApprovalRequestWithStep.detail?: ApprovalChangeDetail` + interface
  `ApprovalChangeDetail` mới (khớp `models.ApprovalChangeDetail` phía BE)

**Sửa test:** `e2e/Core System-approval-role-gate.spec.ts`
- Case 13 (đổi role qua DB không tự cập nhật khi điều hướng SPA): đổi điểm điều hướng thứ 2 từ
  `/v1/approvals` (đã xoá) sang `/v1/report` — bản chất test (SPA-nav vs reload) không phụ thuộc
  trang cụ thể nào
- Case 7 (cb_lead đơn mở UI thật, thấy đúng item của mình): đổi từ `page.goto("/v1/approvals")`
  sang mở thật đường người dùng sẽ đi — `page.goto("/Core System")` → click `.xtab` "Cấu hình" → click
  tile "Duyệt Của Tôi" (định vị bằng class `.xbtn` lọc theo text, vì `getByTitle` bị trùng với 1
  phần tử badge số khác cũng vô tình có cùng title) → chờ đúng response `/approvals/inbox` như cũ

## Kiểm chứng

- `npx tsc --noEmit`: chỉ còn 3 lỗi tiền tồn tại ở `public/backup/payslip-lib.test.ts` (không liên
  quan, xác nhận không tăng thêm)
- `npx eslint` trên 6 file đã sửa: sạch
- `npx vitest run`: 235/0 pass
- `npx playwright test e2e/Core System-approval-role-gate.spec.ts`: **14/14 pass** (chạy full file, không
  chỉ 2 case sửa) — theo đúng quy trình bật/tắt `DEV_USER_EMAIL` ghi sẵn đầu file: backup `.env`,
  đổi `DEV_USER_EMAIL=user@company.test`, restart backend, xoá dòng seed khỏi
  `super_admins`, chạy test, khôi phục `.env` + restart lại — xác nhận `/me` trả đúng
  `user@company.test` + 8 role sau khi khôi phục, 0 dữ liệu test còn sót trong `employees`/
  `super_admins`
- Kiểm tay bằng Playwright script tạm (mở `/Core System` → tab "Cấu hình" → tile "Duyệt Của Tôi",
  chụp ảnh màn hình thật, sau đó xoá script): sheet hiện đúng banner "Có 8 hồ sơ đang chờ duyệt đã
  quá hạn chót", danh sách thật gồm cả `Dòng bảng lương` lẫn `Đợt xét thưởng` (xác nhận nhãn entity
  mới hoạt động đúng trên dữ liệu thật), nút Duyệt/Từ chối hiển thị đúng theo cấp — script tạm đã
  xoá sau khi kiểm, không để lại trong repo

## Trạng thái

Đã commit `Core System-frontend@cccfaac` trên `feature/bonus-engine-phase1` (nối tiếp 2 commit có sẵn
`c38a7bd`/`93ab516` từ phiên song song làm việc tương tự cho "Tính Thưởng"). **Chưa push.**

## Đợt bổ sung 080926 — Duyệt hàng loạt ("Duyệt tất cả" / "Duyệt đã chọn")

User hỏi: "tính năng duyệt của tôi đang phải duyệt từng line, có thể duyệt nhiều/duyệt tất cả
trong tính năng duyệt của tôi không". Chốt 2 quyết định qua `AskUserQuestion` trước khi code (ảnh
hưởng hành vi duyệt thật):
1. **Phạm vi**: làm CẢ HAI — nút "Duyệt tất cả" (duyệt mọi hồ sơ đang hiện, không cần chọn) VÀ
   "Duyệt đã chọn" (chọn nhiều dòng rồi duyệt theo lô), thay vì chỉ 1 trong 2.
2. **Từ chối**: KHÔNG làm hàng loạt — giữ nguyên hành vi từng dòng, vì mỗi hồ sơ bị từ chối nên có
   lý do riêng, gộp chung 1 lý do dễ thiếu trách nhiệm giải trình.

**Cơ chế chọn nhiều dòng:** tái dùng NGUYÊN VẸN hạ tầng vừa dựng cho "Xóa theo lô" ở sheet "Tính
Thưởng" (070926-4, cùng ngày trước đó) — `rowIdsSrc` (tham số có sẵn trong `buildPreviewView`,
trước chỉ Bảng công phụ cấp dùng cho diff) giờ nhận `sheet.approvalInboxItems?.map(it => it.id)`
tại call site chung (`if (sheet.preview) return buildPreviewView(...)`), gộp bằng `??` với nhánh
bonus đã có — 2 sheet không bao giờ cùng có dữ liệu 1 lúc nên không lẫn nguồn. `rowIdsSrc` → cấp
`view.rowIds` → `rowSelectionIds` → `state.selected` (chọn dòng bằng Shift/Ctrl+click số dòng ở
gutter — cơ chế Excel-clone CHUNG của lưới, vốn đã tồn tại cho lưới lương, chỉ chưa từng "cấp
nguồn" cho sheet cfgGrid nào khác trước bonus 070926-4). Không viết cơ chế chọn dòng mới.

**Duyệt hàng loạt:** hàm `approveTargets(sheetId, items)` dùng `runBatched` (giới hạn số request
song song, `lib/batched.ts`) — bắt buộc, không phải tuỳ chọn, vì đúng file đó ghi lại sự cố thật
300826: bắn hết `Promise.allSettled` không giới hạn cho ~3.800 người từng làm cạn pool kết nối DB
(`max_connections=100`, cap `SetMaxOpenConns(25)`), ra 33% request 500 timeout 30s. `approveAllInbox`
= gọi `approveTargets` với toàn bộ `sheet.approvalInboxItems`; `approveSelectedInbox` = lọc theo
`state.selected`, cảnh báo nếu chưa chọn dòng nào. Cả hai gọi `api.actOnApproval(id, "approve")`
(API có sẵn, không đổi), 1 `window.confirm` + 1 toast tiến độ dùng chung cho cả lô, tải lại
`loadApprovalInbox` sau khi xong.

**UI:** 2 tile mới trong `SettingsRibbon.tsx` (props `onApproveAllInbox`/`onApproveSelectedInbox`),
cùng khuôn `onAddReportLine` đã có (chỉ hiện khi đang mở sheet "Duyệt Của Tôi", truyền có điều kiện
từ `TinhLuongExcel.tsx`, không nhét cứng vào `SETTINGS_STATIC`). 2 key i18n mới
(`cfgApproveAllInbox`/`cfgApproveSelectedInbox`).

**Verify:** `tsc --noEmit` sạch (3 lỗi tiền tồn tại không liên quan), `eslint` sạch trên cả 3 file
sửa. Chưa kiểm tay/Playwright trên dev server trong phiên này — khuyến nghị user tự thử Shift/Ctrl
+click chọn nhiều dòng rồi "Duyệt đã chọn", và "Duyệt tất cả" trên danh sách có nhiều loại
entity_type khác nhau trước khi merge/deploy. Commit `Core System-frontend@5c502d0`, đã push
`feature/bonus-engine-phase1` (0 conflict với `develop_v1`).
