---
id: self-docs/integration/rbac-jml-checklist-van-hanh
canonical_question: 'Technical guide and specification: Checklist vận hành Joiner-Mover-Leaver  —
  Core System'
aliases:
- Checklist vận hành Joiner-Mover-Leaver  — Core System
- RBAC JML Checklist Van Hanh 150726
entity_type: how_to
domain: self-docs > integration
last_verified: 2026-07-16
---

# Checklist vận hành Joiner-Mover-Leaver (JML) — Core System

**Ngày:** 2026-07-16
**Phạm vi:** G9 trong `RBAC-Improvement-Analysis-150726.md` — "Không có quy trình Joiner-Mover-Leaver (JML) tường minh". Đây là bước khả thi ngay theo phân tích ở mục 4.1 của tài liệu đó: một checklist vận hành thủ công, không cần tự động hoá, không cần tích hợp với hệ thống HR nguồn (đó là bước sau, nếu cần).

**Ai dùng file này:** người xử lý HR/IT khi có nhân viên mới vào, chuyển công ty/phòng ban/công trường, hoặc nghỉ việc — và cả `hr_admin` khi tự tay gán/sửa/xoá vai trò qua `/v1/settings/roles`.

---

## Vì sao cần checklist này

Hệ thống hiện tại không có cơ chế nào tự động dọn hoặc cập nhật bảng `employee_roles` khi một nhân viên đổi vai trò trong công ty hoặc nghỉ việc. Việc gán quyền mới thường được nhớ để làm, nhưng việc **thu hồi** quyền cũ thì dễ bị quên — và quyền thừa tích luỹ dần theo thời gian là đúng loại rủi ro mà kiểm toán nội bộ hay các khung RBAC chuẩn (NIST, IBM) luôn nhắc tới. Checklist dưới đây tồn tại để đảm bảo bước thu hồi không bị bỏ sót, không phải để thêm việc giấy tờ.

## Joiner — khi có nhân viên mới cần truy cập hệ thống Core System

1. Xác nhận nhân viên này thuộc nhóm nào trong 5 vai trò hiện có: `hr_admin`, `cb_staff`, `site_admin`, `search_profile`, hoặc không cần vai trò gì cả (nhân viên thường chỉ dùng ESS, không cần gán role trong `employee_roles`).
2. Nếu cần vai trò `hr_admin` hoặc `cb_staff`: xác định ngay từ đầu phạm vi công ty (`scope_company_code`) — để trống (NULL) nghĩa là không giới hạn, chỉ nên dùng cho người thực sự cần thấy toàn bộ pháp nhân. Nếu chỉ phụ trách một pháp nhân cụ thể, điền đúng mã công ty đó ngay từ lúc gán, không để mặc định rồi sửa sau.
3. Nếu là `site_admin`: xác định đúng công trường (`scope_department_id`) sẽ phụ trách trước khi gán — một `site_admin` được gán nhiều hơn một công trường cùng lúc sẽ bị hệ thống chặn (403) ở các route xem chấm công, vì cơ chế lọc hiện tại chỉ xử lý được một công trường một lần.
4. Gán vai trò qua `POST /roles/employees` (hoặc màn hình "Ma trận quyền hạn" ở `/v1/settings/roles`).
5. Xác nhận lại bằng cách gọi `GET /roles/access-review` (mới thêm — xem mục G4 cùng ngày) và tìm đúng dòng của nhân viên vừa gán để chắc chắn phạm vi đã ghi đúng như dự định.

## Mover — khi nhân viên chuyển phòng ban / công trường / pháp nhân, hoặc đổi vai trò

1. **Chuyển pháp nhân** (ví dụ từ Enterprise sang Unicons): nếu nhân viên này có vai trò `hr_admin`/`cb_staff` với `scope_company_code` cụ thể, phải cập nhật lại giá trị này cho khớp pháp nhân mới — nếu không, nhân viên sẽ tiếp tục nhìn thấy dữ liệu của pháp nhân CŨ (theo cơ chế company-scope ở `middleware/scope.go`) hoặc mất quyền xem pháp nhân MỚI.
2. **Chuyển công trường** (với `site_admin`): cập nhật `scope_department_id` sang công trường mới; xoá scope cũ khỏi dòng `employee_roles` đó thay vì thêm một dòng mới song song (tránh tình trạng một người có 2 dòng `site_admin` với 2 công trường khác nhau — hệ thống hiện tại không xử lý được trường hợp "nhiều công trường cùng lúc" một cách an toàn, xem gap G6).
3. **Đổi chức danh dẫn tới đổi vai trò trong hệ thống** (ví dụ từ `cb_staff` lên `hr_admin`, hoặc ngược lại khi thu hẹp trách nhiệm): xoá vai trò CŨ qua `DELETE /roles/employees` trước, rồi gán vai trò MỚI — không chỉ thêm vai trò mới mà quên xoá vai trò cũ, vì hệ thống cho phép nhiều vai trò cùng lúc (OR semantics) nên nếu không xoá, nhân viên vẫn giữ nguyên quyền hạn cũ chồng lên quyền mới.
4. Sau khi cập nhật, chạy lại `GET /roles/access-review` — nếu dòng của nhân viên này hiện cờ `multipleRoles=true` mà không phải chủ đích (ví dụ quên xoá vai trò cũ ở bước 3), xử lý lại ngay.

## Leaver — khi nhân viên nghỉ việc hoặc ngừng cần truy cập hệ thống Core System

1. Xoá TẤT CẢ dòng `employee_roles` của nhân viên này qua `DELETE /roles/employees` (lặp lại cho từng vai trò nếu có nhiều hơn một).
2. Nếu nhân viên nghỉ việc có vai trò `hr_admin` không giới hạn phạm vi (`scope_company_code IS NULL`), đây là trường hợp CẦN xử lý ưu tiên — một tài khoản `hr_admin` không giới hạn còn hoạt động sau khi người đó đã nghỉ là rủi ro cao nhất trong toàn bộ checklist này.
3. Việc xoá vai trò trong `employee_roles` **không tự động khoá được tài khoản Azure AD** — nếu JWT của người này còn hạn hoặc họ vẫn đăng nhập được qua Azure AD, họ sẽ rơi về vai trò `employee` mặc định (không có quyền `hr_admin`/`cb_staff`/`site_admin` nữa, nhưng vẫn đăng nhập được vào các route mở cho `employee`, ví dụ ESS xem thông tin cá nhân). Việc khoá tài khoản Azure AD hẳn là một bước RIÊNG, thuộc quy trình offboarding chung của công ty, không phải của riêng hệ thống Core System — checklist này chỉ đảm bảo phần `employee_roles`.
4. Nếu người này từng được thêm vào danh sách `super_admins` (bypass company-scope) hoặc `superAdminEmails` trong cấu hình middleware, phải xoá khỏi danh sách đó — hai chỗ này KHÔNG nằm trong `employee_roles` nên bước 1 không tự động dọn được, cần kiểm tra riêng.
5. Chạy lại `GET /roles/access-review` sau khi xoá, xác nhận không còn dòng nào của nhân viên này trong kết quả trả về.

## Tần suất kiểm tra định kỳ (bổ trợ, không thay thế 3 bước trên)

Checklist JML xử lý từng sự kiện riêng lẻ khi nó xảy ra — nhưng không bắt được trường hợp một sự kiện bị quên báo (ví dụ nhân viên đã chuyển phòng ban nhưng không ai báo cho người quản trị hệ thống). Vì vậy nên kết hợp với báo cáo rà soát quyền định kỳ (G4, `GET /roles/access-review`) theo lịch cố định — khuyến nghị mỗi quý một lần, do một `hr_admin` cấp cao xem lại toàn bộ các dòng có cờ `multipleRoles=true` hoặc `unusualScope=true`, xác nhận từng dòng còn hợp lý hay là dấu hiệu của một sự kiện Mover/Leaver bị bỏ sót.

## Giới hạn của checklist này (nói rõ, không giấu)

- Đây là quy trình **thủ công**, phụ thuộc vào việc người xử lý HR/IT nhớ và làm đúng — chưa có cơ chế nào ở tầng hệ thống bắt buộc phải hoàn thành checklist trước khi coi một nhân viên là "đã offboard xong". Tự động hoá đầy đủ (ví dụ trigger từ hệ thống HR nguồn khi trạng thái nhân viên đổi) là bước tiếp theo, cần một nguồn sự kiện HR đáng tin cậy mà hiện tại chưa xác nhận có hay không.
- Checklist này không bao gồm việc khoá tài khoản Azure AD hoặc thu hồi JWT đang hoạt động (xem mục Leaver, bước 3) — đó thuộc gap G3 (đồng bộ IdP) và nằm ngoài phạm vi có thể xử lý chỉ bằng quy trình vận hành thuần.
