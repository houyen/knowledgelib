---
id: self-docs/integration/brd-38-notification-audit-log
canonical_question: 'Technical guide and specification: TASK-REF — Audit Log bắt buộc
  cho Cấu hình Thông báo'
aliases:
- TASK-REF — Audit Log bắt buộc cho Cấu hình Thông báo
- BRD 38 Notification Audit Log 080926
entity_type: how_to
domain: self-docs > integration
last_verified: 2026-09-17
---

# TASK-REF — Audit Log bắt buộc cho Cấu hình Thông báo (080926)

## Bối cảnh

Sau khi phân tích TASK-REF/39/40 (`self-docs/TASK-REF-Notification-Frequency-Config-080926.md` là tiền
đề — cùng nhóm "Thông báo"), chốt: chỉ 1 việc đủ điều kiện làm ngay không cần hỏi ai — **Audit Log
bắt buộc** cho sheet "Cấu hình Thông báo", đúng yêu cầu PRD1 §6.2: *"Audit Log: bắt buộc lưu lịch
sử: Giá trị cũ → Giá trị mới, Người thực hiện, Thời gian và Lý do bắt buộc."*

Phần còn lại của TASK-REF (gửi Teams thật, sync-back Workday, "Duyệt thay") và toàn bộ TASK-REF/40 bị
chặn bởi hạ tầng ngoài (Teams Bot registration, SMTP) hoặc business chưa chốt — xem danh sách câu
hỏi cần confirm ở cuối file `TASK-REF-...-080926.md`.

## Phát hiện lúc khảo sát code (quan trọng, làm thay đổi thiết kế)

1. `ConfigHandler.UpdateSystem` (route `/config/system` cũ) dùng **`userID := uuid.New()`** — sinh
   UUID ngẫu nhiên mỗi lần gọi, KHÔNG lấy actor thật đăng nhập. Route này dùng chung cho NHIỀU key
   config khác — sửa trực tiếp route này rủi ro đổi hành vi chỗ khác, nên **tách route mới riêng**
   `PUT /config/notification-events`, không đụng `/config/system`.
2. `system_config.updated_by` là cột **`uuid NOT NULL` THẬT** trên DB (kiểm bằng `psql \d`, KHÔNG
   suy từ `internal/db/schema.sql` — file này đang lệch DB thật, vấn đề đã tài liệu hoá ở
   `self-docs/DB-Cleanup-...-180826.md`) — không ghi thẳng `actorEmail` (chuỗi) vào đó được. Phải
   resolve `employeeRepo.GetIDByEmail(actorEmail)` (cùng khuôn `PayrollPeriodService.Lock`),
   fallback `uuid.Nil` nếu actor không có dòng `employees` (VD super-admin thuần AD).
3. Bảng `audit_logs` THẬT có cột `module/entity_type/entity_id/details` — **KHÔNG** có
   `resource/resource_id/old_values/new_values` như struct Go `models.AuditLog` gợi ý (xem comment
   có sẵn ở `AuditLogRepo.Create` — vấn đề này đã được vá từ trước, `Resource` map vào cả
   `module` lẫn `entity_type`, `OldValues`/`NewValues` gộp vào 1 cột `details` JSON
   `{"old":...,"new":...}`). Test viết theo đúng cấu trúc thật này (verify qua psql trước khi viết
   assertion, không suy từ tên field Go).

## Thi hành

Nhánh `feat/notify-config-audit-log` cả 2 repo, tách từ `develop_v1` mới nhất (không phải
`sec_dev` — không phải hạng mục RBAC/company-scoping, dù có chạm `audit_logs`).

**Backend** (`internal/service/config_service.go`, `internal/handler/config_handler.go`,
`internal/app/router.go`):
- `ConfigService.UpdateNotificationEvents(ctx, eventsJSON, reason, actorEmail)` — đọc giá trị cũ
  TRƯỚC khi ghi đè (OldValues thật, không suy từ payload FE), resolve actor→employee UUID, ghi
  `system_config` + `audit_logs` (Resource="notification_config", NewValues gồm cả `reason`).
- `ConfigHandler.UpdateNotificationEvents` — decode `{events, reason}`, 400 nếu `reason` rỗng hoặc
  `events` không phải mảng non-empty, actor qua `actorEmail(r)` (helper có sẵn).
- Route `PUT /config/notification-events` — cùng gate `requireSystemEdit` (Settings.System) như
  `/config/system`, đặt SONG SONG (không lồng vào group cũ).
- `ConfigService` thêm field `employeeRepo`, wire trong `service.go`.

**Frontend** (`TinhLuongExcel.tsx`, `lib/api/config.ts`):
- `api.updateNotificationEvents(events, reason)` — gọi route mới, thay `api.updateSystemConfig`.
- Modal "Sửa thông báo" thêm textarea "Lý do sửa (bắt buộc)" — chặn Lưu nếu rỗng (cùng khuôn các
  modal reason khác đã có: Kỳ lương, khoá kỳ...).

## Sự cố tự phát hiện + tự sửa khi viết test

Bản test đầu tiên dùng `t.Cleanup` để **`DELETE FROM system_config WHERE key = ...`** — nhưng
`notification.events` là **singleton toàn hệ thống** (đúng khoá thật sheet "Cấu hình Thông báo"
dùng ở DB dev, không phải dữ liệu scope theo tenant/test). Chạy test này đã **xoá mất cấu hình thật**
đang có trên DB dev (xác nhận bằng cách chạy Playwright kiểm tay ngay sau đó, thấy dòng audit đầu
tiên thiếu hẳn field `old` — vì `GetByKey` trả rỗng do dòng đã bị test trước đó xoá). Đây đúng loại
lỗi đã có tiền lệ ghi trong `self-docs/Super-Admin-Bootstrap-Runbook-120826.md` (bảng dùng chung
toàn cục phải snapshot/restore, không được xoá). Sửa: snapshot giá trị thật trước khi test, restore
đúng giá trị đó (không phải default cứng) trong `t.Cleanup`, cho cả 2 test integration. Xác nhận lại
bằng cách chạy lại test + `psql` đối chiếu — DB dev khôi phục đúng.

## Kết quả kiểm

- `go build`/`go vet`: sạch.
- 2 test integration mới (`config_service_notification_events_integration_test.go`) chạy trên DB
  dev thật (không mock): actor thật resolve đúng employee UUID, audit ghi đúng old/new/reason;
  actor không resolve được → fallback `uuid.Nil`, không lỗi/panic.
- `go test -p 1 ./internal/...`: baseline đo lại bằng `git stash -u` = 6 fail tiền tồn tại
  (`TestIntegrationAttendanceSummaryRepoGetAttendanceSummaries`,
  `TestIntegrationAttendanceTimesheetAllowanceRoutesEnforceFineGrainedPermission`,
  `TestIntegrationEmployeesRLSRestrictsWhenScoped`, `TestIntegrationFormulaApprovalAndRecalcE2E`
  — kèm 1 panic đã tiền tồn tại, `TestPipelineProtected{Run,Logs}RouteWithDevAuthReachesHandler`)
  → sau đổi vẫn đúng 6 fail đó (diff rỗng) — **0 hồi quy**.
- `tsc --noEmit`: 3 lỗi tiền tồn tại (`public/backup/payslip-lib.test.ts`, không liên quan) — sạch.
- `eslint`/`vitest` (235/0): sạch, khớp baseline.
- **Kiểm tay Playwright thật** trên dev server local (build binary mới từ nhánh, restart server):
  curl xác nhận `reason` rỗng → 400, `events` rỗng → 400; UI: chưa nhập lý do → toast lỗi chặn lưu;
  nhập đủ → lưu thành công; đối chiếu trực tiếp `audit_logs` qua `psql` — `user_email` = actor thật
  đăng nhập (`user@company.test`), `details.old`/`details.new`/`details.new.reason` đúng dữ liệu
  thật. Đã khôi phục `system_config` về default (1 lần/ngày, 9h) sau kiểm, xoá script/ảnh tạm.

## Trạng thái git

Commit `Core System-backend@d783d01`, `Core System-frontend@b2a5c1e` trên nhánh
`feat/notify-config-audit-log` (cả 2 repo), merge `--no-ff` vào `develop_v1` (0 conflict cả 2 —
FE auto-merge sạch với 3 commit khác vừa push lên `develop_v1` cùng lúc), đã push lên GitLab:
`Core System-backend@0e53e2f` (MR !34), `Core System-frontend@93f1013` (MR !61). Nhánh tạm đã xoá.
