---
id: self-docs/engine/brd-61-notification-frequency-config
canonical_question: 'Technical guide and specification: TASK-REF — Cấu hình Tần suất/Giờ
  Nhắc Duyệt'
aliases:
- TASK-REF — Cấu hình Tần suất/Giờ Nhắc Duyệt
- BRD 61 Notification Frequency Config 080926
entity_type: how_to
domain: self-docs > engine
last_verified: 2026-09-17
---

# TASK-REF — Cấu hình Tần suất/Giờ Nhắc Duyệt (080926)

## Bối cảnh

User đưa 2 file tracker BRD (`Payroll_BRD_Tracker_Item.xlsx`, `PRD__Payroll_System_v2.1.docx`) yêu cầu
phân tích TASK-REF + TASK-REF. Cả 2 đều nhóm "Thao tác Người dùng", PT `thoaidd`, trạng thái "xong v1"
(đã có nguyên mẫu).

- **TASK-REF** "Thao tác Cấu hình Thông báo": HR set tần suất/giờ nhắc duyệt qua Teams. Trích PRD1
  §6.2 — khớp đúng. Gap: PRD không nêu range hợp lệ cho input tần suất/giờ.
- **TASK-REF** "Thao tác CRUD Bảng phụ cấp Mắt Bão": trích PRD1 §4.3 — **sai mục** (đó là "Khóa kỳ
  lương"), đúng phải là §6.1 "Quản lý nhân sự Mắt Bão" (khớp mô tả "Quản trị viên thiết lập bảng
  định mức phụ cấp Grid trực tiếp trên Core System"). Chỉ là lỗi trích dẫn trong tracker, không phải
  việc code — không thuộc phạm vi phần triển khai này.

## Quyết định (chốt qua `AskUserQuestion`)

- Tần suất nhắc: ~~1-3 lần/ngày, default 1~~ **→ đã đổi, xem "Đợt sửa lại 080926" bên dưới.**
- Giờ gửi: ~~8h-18h (giờ hành chính), default 09:00~~ **→ đã đổi.**
- Cấu hình **luôn sửa được** — không khoá sau khi chốt lần đầu (yêu cầu user, vẫn giữ nguyên).

## Khảo sát trước khi code

Tìm thấy nguyên mẫu ("Đã có nguyên mẫu" ghi trong tracker) đã tồn tại sẵn trên remote
`Core System-frontend@feat/notification-config-sheet` (commit `c253a38`, tác giả đồng nghiệp Trần Bùi
Hoàng Gia, 070926) — chuyển màn "Cấu hình Thông báo" từ trang riêng `/v1/settings/notifications`
vào sheet trong `/Core System` (theo đúng pattern consolidation đã dùng cho "Duyệt Của Tôi" cùng đợt).
Nguyên mẫu này có lưới sự kiện × kênh (Email/Teams/Người nhận/Mẫu nội dung) lưu vào
`system_config` key `notification.events` (dùng route generic `GET/PUT /config/system` đã có sẵn ở
`Core System-backend/internal/app/router.go:337-340` — **không cần route/bảng BE mới**), nhưng **chưa
có field tần suất/giờ gửi** — đúng gap mà TASK-REF nêu.

Backend: xác nhận `SystemConfigRepo` (`internal/repository/system_config_repo.go`) là key-value
generic (`key`/`value`/`updated_by`/`updated_at`), route `/config/system` (`GetSystem`/
`UpdateSystem`) đã wire sẵn — 0 thay đổi BE cho việc này.

## Thi hành

Nhánh `Core System-frontend@feat/notification-config-frequency` (tách từ `origin/develop_v1`, vì nhánh
này KHÔNG phải hạng mục RBAC/bảo mật nên không cần `sec_dev`):

1. Cherry-pick commit nguyên mẫu `c253a38` từ `feat/notification-config-sheet` lên `develop_v1`
   (1 conflict ở `TinhLuongExcel.tsx` — trùng vị trí chèn code với batch-approve 080926 đã merge
   vào `develop_v1` sau đó; giải bằng giữ cả 2 khối, không mất code nào).
2. Thêm field `frequencyPerDay`/`hour` vào `NotifyEvent` — **optional**, chỉ có giá trị cho sự kiện
   mang tính "nhắc lặp lại theo lịch" (hiện chỉ `pending_reminder` = "Nhắc phiếu chờ duyệt quá
   hạn"); các sự kiện theo trigger khác (`escalate`/`payroll_closed`/`rejected`) không có khái niệm
   tần suất/giờ cố định nên để `undefined`, modal ẩn 2 input này khi không áp dụng.
3. `NOTIFY_FREQUENCY_RANGE`/`NOTIFY_HOUR_RANGE` — hằng số range+default đã chốt, validate trong
   `saveNotifyEditModal` trước khi ghi (chặn toast lỗi nếu ngoài range), không lưu xuống DB.
4. Cột lưới mới "Tần suất/ngày"/"Giờ gửi" (hiển thị `HH:00`) trong sheet "Cấu hình Thông báo".
5. Cấu hình vẫn ghi đè cả mảng vào `system_config.notification.events` như nguyên mẫu cũ — **luôn
   sửa lại được** qua modal "Sửa thông báo" bất kỳ lúc nào (đúng yêu cầu user, không có cơ chế khoá).

## Kết quả kiểm

- `tsc --noEmit`: 3 lỗi tiền tồn tại (`public/backup/payslip-lib.test.ts`, không liên quan) — sạch.
- `eslint` trên file đã sửa: sạch.
- `vitest`: 235/0 — khớp baseline, 0 hồi quy.
- **Kiểm tay bằng Playwright thật** (script tạm `verify-notify-freq.mjs`, chạy trên dev server local
  đang sống sẵn `:8080`/`:3000`, dev-bypass `Authorization: Bearer dev` — identity thật
  `user@company.test`, đã xoá script + ảnh chụp sau khi kiểm):
  - Mở sheet "Cấu hình Thông báo" (nhóm ribbon "Chế độ & Chính sách", mặc định thu gọn — bấm mũi
    "›" để mở) → cột "Tần suất/ngày"/"Giờ gửi" hiện đúng, chỉ có giá trị ở dòng "Nhắc phiếu chờ
    duyệt quá hạn" (4 dòng khác trống, đúng thiết kế).
  - Nhập tần suất = 5 (ngoài 1-3) → toast đỏ "Tần suất nhắc phải từ 1 đến 3 lần/ngày", modal không
    đóng, KHÔNG lưu.
  - Nhập giờ = 20 (ngoài 8-18) → toast đỏ "Giờ gửi phải trong khoảng 8h-18h", không lưu.
  - Nhập giá trị hợp lệ (2 lần/ngày, 10h) → toast xanh "Đã lưu thông báo...", grid cập nhật đúng
    `2` / `10:00`.
  - Mở lại modal lần 2 (xác nhận "luôn sửa được") → prefill đúng giá trị vừa lưu (2/10), sửa lại
    thành công.
  - Đối chiếu trực tiếp `GET /api/v1/config/system` (key `notification.events`) sau khi khôi phục
    về default (1, 9) — xác nhận DB dev sạch, không để lại dữ liệu test lệch.

## Trạng thái git

Commit `Core System-frontend@e5c11d4` trên `feat/notification-config-frequency` (2 commit: cherry-pick
nguyên mẫu `f96c993` + field mới `e5c11d4`), merge `--no-ff` vào `develop_v1` @ `f574d7c`, đã push
`origin/develop_v1` (MR !61 tự cập nhật). Nhánh tạm đã xoá sau merge. Backend: không có thay đổi
(dùng route generic có sẵn).

## Còn treo (ngoài phạm vi đợt này)

- TASK-REF: sửa citation PRD1 §4.3 → §6.1 trong `Payroll_BRD_Tracker_Item.xlsx` (chỉ sửa tài liệu,
  không phải code) — chưa làm, chờ user xác nhận riêng.

## Đợt sửa lại 080926 (cùng ngày, sau khi đã merge lần đầu)

User xem lại file này và chốt lại: *"việc cấu hình các thông số tôi nghĩ sẽ không cần phải block mà
có thể thoải mái chọn giờ"* — tức range "1-3 lần/ngày"/"8h-18h giờ hành chính" chốt ban đầu (mục
"Quyết định" phía trên) là quá chặt cho một cấu hình nội bộ HR tự set. Hỏi lại qua
`AskUserQuestion` để rõ phạm vi (chỉ giờ, hay cả tần suất), user chọn **bỏ cả 2**:

- **Giờ gửi**: bỏ hẳn "giờ hành chính 8h-18h" — nhưng vẫn giữ kẹp **0-23** vì đó là biên KỸ THUẬT
  của khái niệm "1 giờ trong ngày" (không phải rule nghiệp vụ), tránh nhập được giá trị vô nghĩa
  như 25h hay -1h.
- **Tần suất/ngày**: bỏ hẳn giới hạn trên (không còn max=3) — chỉ còn chặn số nguyên dương (≥1),
  tránh 0 hoặc số âm/thập phân.

Đổi `NOTIFY_HOUR_RANGE` từ `{min:8,max:18,default:9}` → `{min:0,max:23,default:9}`; xoá hẳn
`NOTIFY_FREQUENCY_RANGE`, thay bằng hằng số `NOTIFY_FREQUENCY_DEFAULT=1` + validate inline
(`Number.isInteger && >= 1`, không còn max). Label UI "Số lần/ngày (1-3)" → "Số lần/ngày" (bỏ số
cứng); "Giờ gửi (8h-18h)" tự động đổi thành "Giờ gửi (0h-23h)" (dùng chung hằng số).

Nhánh `feat/notify-config-no-range-limit` (FE only, từ `develop_v1`), commit `985b9ae`.
`tsc`/`eslint`/`vitest` (239/0 — số tăng so 235 vì `develop_v1` đã nhận thêm test từ nhánh khác
merge vào cùng ngày, không phải do đợt này) sạch. Kiểm tay Playwright thật trên dev server local
(build binary BE mới + restart FE từ `develop_v1`): lưu tần suất=10/giờ=20h (trước đây bị chặn) →
thành công; giờ=24 (ngoài biên 0-23) → vẫn bị chặn đúng; tần suất=0 → vẫn bị chặn đúng. Đối chiếu
`system_config` qua `psql` xác nhận đã khôi phục default (1, 9) sau kiểm, script/ảnh tạm đã xoá.
Merge `--no-ff` vào `develop_v1`, push GitLab — xem dòng nhật ký CLAUDE.md cùng ngày cho SHA cụ thể.
