---
id: self-docs/integration/super-admin-bootstrap-runbook
canonical_question: 'Technical guide and specification: Runbook: Bootstrap & thu hồi
  Super-Admin'
aliases:
- 'Runbook: Bootstrap & thu hồi Super-Admin'
- Super Admin Bootstrap Runbook 120826
entity_type: runbook
domain: self-docs > integration
last_verified: 2026-09-17
---

# Runbook: Bootstrap & thu hồi Super-Admin (120826)

## Bối cảnh

Trước 120826, `EnsureSuperAdmins` (`Core System-backend/internal/database/database.go`) seed cứng email `user@company.test` làm super-admin gốc, chạy mỗi lần backend khởi động ở mọi môi trường kể cả production — rủi ro bảo mật kiểu TASK-REF (danh tính đặc quyền hardcode trong source code đã commit git). Từ commit `f0dc6f3` (nhánh `fix/admin-bootstrap-security`, dựa trên `origin/develop`), cơ chế đổi sang: chỉ seed từ biến môi trường `INITIAL_SUPER_ADMIN_EMAIL` khi bảng `super_admins` đang **rỗng**. Xem đầy đủ phân tích + quyết định: `llmwiki/wiki/sources/draft/120826-super-admin-bootstrap-security.md` + `-PLAN.md`.

Bảng `super_admins` (`email PRIMARY KEY`, `note`, `created_at`) — bất kỳ email nào trong bảng này được cấp **toàn bộ role code hệ thống** (qua `isSuperAdmin`/`allRoleCodes` trong `internal/middleware/auth.go`), không cần dòng `employee_roles` nào. Không có UI/API quản lý bảng này — mọi thay đổi (ngoài lúc bootstrap lần đầu) làm bằng SQL trực tiếp.

## 1. Dựng môi trường mới lần đầu (staging/prod)

Trước khi khởi động backend lần đầu trên 1 môi trường MỚI (DB `super_admins` chưa có dòng nào — bảng có thể chưa tồn tại, `EnsureSuperAdmins` sẽ tự tạo):

1. Set biến môi trường `INITIAL_SUPER_ADMIN_EMAIL=<email người phụ trách vận hành ban đầu>` (ví dụ: `INITIAL_SUPER_ADMIN_EMAIL=user@company.test`) trong cấu hình deploy của môi trường đó (secret/env của CI-CD hoặc container orchestration — **KHÔNG commit giá trị thật vào git**).
2. Khởi động backend. Kiểm log khởi động có dòng `"bootstrap super-admin lần đầu"` kèm đúng email — nếu thay vào đó thấy `"bảng super_admins đang rỗng và INITIAL_SUPER_ADMIN_EMAIL chưa được set"`, nghĩa là biến chưa set đúng; sửa lại rồi khởi động lại.
3. Người có email đó đăng nhập qua Azure AD thật — có toàn quyền hệ thống ngay, không cần thao tác SQL nào thêm.

**Lưu ý:** nếu bảng `super_admins` đã có ít nhất 1 dòng từ trước (ví dụ môi trường đã từng chạy code cũ, đã có `user@company.test`), việc set `INITIAL_SUPER_ADMIN_EMAIL` ở lần khởi động sau **sẽ không có tác dụng gì** (đúng thiết kế — tránh cấp thêm quyền ngoài ý muốn). Dòng cũ vẫn giữ nguyên.

## 2. Thu hồi email bootstrap sau khi đã gán quyền thật

Sau khi go-live ổn định và đã gán `hr_admin` (hoặc role phù hợp) thật cho (các) người phụ trách qua `employee_roles`/UI quản trị:

1. **Xác nhận còn ÍT NHẤT 1 tài khoản khác** (không phải email bootstrap sắp xoá) có quyền quản trị đủ để tiếp tục vận hành `super_admins`/`employee_roles` — nếu không, **KHÔNG xoá**, sẽ tự khoá mình ra khỏi hệ thống (không có đường khôi phục nào khác ngoài truy cập DB trực tiếp).
2. Chạy SQL (qua kết nối trực tiếp DB, không qua API — không có endpoint nào cho việc này):

```sql
DELETE FROM super_admins WHERE email = LOWER('<email-bootstrap>');
```

3. Xác nhận lại bằng `SELECT * FROM super_admins;` rằng danh sách còn lại đúng như mong đợi.

## 3. Thêm/xoá super-admin thủ công (ngoài lúc bootstrap)

Không có UI/API quản lý `super_admins` — mọi thay đổi làm trực tiếp bằng SQL:

```sql
-- Thêm
INSERT INTO super_admins (email, note) VALUES (LOWER('<email>'), '<lý do, ví dụ: "on-call incident YYYY-MM-DD">') ON CONFLICT (email) DO NOTHING;

-- Xoá
DELETE FROM super_admins WHERE email = LOWER('<email>');

-- Xem danh sách hiện tại
SELECT email, note, created_at FROM super_admins ORDER BY created_at;
```

## Việc đã bỏ qua khỏi phạm vi (Task 2 của PLAN)

`Core System-backend` không có file `.env.example` nào ở thời điểm thi hành (đã kiểm bằng `find`, không có file `.env*` mẫu nào trong repo) — không tạo mới file này chỉ để thêm 1 dòng, vì tạo `.env.example` cho toàn dự án là quyết định phạm vi lớn hơn thay đổi này. Người vận hành set `INITIAL_SUPER_ADMIN_EMAIL` trực tiếp theo hướng dẫn mục 1 ở trên, không có file mẫu tham chiếu.

## Tham chiếu

- SPEC: `llmwiki/wiki/sources/draft/120826-super-admin-bootstrap-security.md`
- PLAN: `llmwiki/wiki/sources/draft/120826-super-admin-bootstrap-security-PLAN.md`
- Code: `Core System-backend/internal/database/database.go` (`EnsureSuperAdmins`), `Core System-backend/internal/config/config.go` (`ServerConfig.InitialSuperAdminEmail`)
- Test: `Core System-backend/internal/database/ensure_super_admins_integration_test.go`
- Commit: `Core System-backend@f0dc6f3` trên nhánh `fix/admin-bootstrap-security` (dựa trên `origin/develop`)
