---
id: self-docs/files/prompt-l10
canonical_question: 'Technical guide and specification: Brief thi hành — L10: chuyển
  app sang DB role non-superuser để RLS có hiệu lực thật'
aliases:
- 'Brief thi hành — L10: chuyển app sang DB role non-superuser để RLS có hiệu lực
  thật'
- prompt L10 060826
entity_type: how_to
domain: self-docs > files
last_verified: 2026-09-17
---

# Brief thi hành — L10: chuyển app sang DB role non-superuser để RLS có hiệu lực thật

**Đây là phiên THI HÀNH theo brief đã chốt, không phải phiên thiết kế.** Kiến trúc đã chốt (060826):
**1 connection duy nhất**, đổi OWNER của toàn bộ bảng sang role hạn chế, dựa vào
`FORCE ROW LEVEL SECURITY` đã bật sẵn trên `employees` để RLS áp dụng ngay cả với owner. KHÔNG tách 2
connection (phương án đó đã bị loại — đơn giản hơn được chọn thay).

## Bối cảnh — đo thật 060826

```
current_user=postgres, rolsuper=true, rolbypassrls=true  -- vai trò app đang dùng
employees: relrowsecurity=true, relforcerowsecurity=true  -- RLS đã bật + FORCE, nhưng vô hiệu vì bypass
1 policy trên employees: employees_company_scope (USING company_code khớp app.company_scope_codes
  hoặc app.company_scope_unlimited='true')
Core System-backend/.env: DB_USER=postgres, DB_PASSWORD=postgres, DB_HOST=localhost, DB_PORT=5432
internal/config/config.go:83  DatabaseConfig.DSN()  — build chuỗi kết nối từ 4 biến trên
internal/database/database.go:12  func Connect(cfg config.DatabaseConfig) (*sqlx.DB, error)  — 1 connection duy nhất dùng SUỐT đời backend (RunMigrations() VÀ mọi query sau đó qua CÙNG *sqlx.DB)
Schema public: 105 bảng, 8 sequence, 0 view — không có CREATE EXTENSION/lệnh cần superuser nào trong
  RunMigrations() (đã grep xác nhận). Extension đã cài sẵn: pgcrypto (gen_random_uuid()), plpgsql —
  cả hai EXECUTE mặc định cho PUBLIC, không cần quyền đặc biệt để gọi.
Tài liệu nguồn: self-docs/RBAC-Improvement-Analysis-150726.md mục G10 (đã có script nháp
  Core System-backend/scripts/create-agent-data-role.sql — vai trò đó dành cho AGENT thao tác psql tay,
  KHÁC MỤC ĐÍCH với role app kết nối liên tục trong brief này; không dùng chung 1 role cho cả hai).
```

Cơ chế Postgres đã xác nhận đúng: `FORCE ROW LEVEL SECURITY` khiến RLS áp dụng **kể cả với chủ sở
hữu bảng** (chỉ superuser hoặc role có `BYPASSRLS` mới thoát được) — nên đổi owner sang role
`NOSUPERUSER NOBYPASSRLS` là đủ, không cần giữ `postgres` làm owner riêng.

## Rủi ro cần biết trước khi làm

Đây là thay đổi hạ tầng ảnh hưởng MỌI truy vấn của backend — không phải sửa 1 dòng code. Làm sai =
backend không kết nối được DB (mất dịch vụ hoàn toàn), hoặc RunMigrations() lỗi giữa chừng (schema
dở dang). **Chỉ làm trên DB dev local (`payroll_engine` trên `localhost:5432`), không đụng
staging/production** — không có quyết định nào cho phép làm ở 2 môi trường đó trong brief này.

## Các bước

### Bước 0 — backup trạng thái hiện tại (an toàn, có thể rollback)

```bash
pg_dump "postgres://postgres@localhost:5432/payroll_engine?sslmode=disable" \
  --format=custom --file=/tmp/payroll_engine_before_L10_060826.dump
```
Xác nhận file tạo thành công (`ls -la /tmp/payroll_engine_before_L10_060826.dump`, kích thước > 0)
trước khi tiếp tục bước nào khác.

### Bước 1 — tạo role mới, KHÔNG đụng `agent_data_role` (khác mục đích)

```sql
-- Chạy với vai trò postgres (superuser) hiện tại, một lần
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'payroll_app_role') THEN
    CREATE ROLE payroll_app_role LOGIN PASSWORD '<mật khẩu mới, KHÔNG dùng lại "postgres">'
      NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS;
  END IF;
END $$;

GRANT CONNECT ON DATABASE payroll_engine TO payroll_app_role;
GRANT CREATE, USAGE ON SCHEMA public TO payroll_app_role;
```

`CREATE` trên schema là bắt buộc — nếu không, `RunMigrations()` sẽ lỗi ngay ở migration đầu tiên tạo
bảng mới trong tương lai (không phải các bảng hiện có, những bảng đó sẽ được xử lý ở Bước 2).

### Bước 2 — chuyển ownership toàn bộ 105 bảng + 8 sequence sang role mới

```sql
DO $$
DECLARE r RECORD;
BEGIN
  FOR r IN SELECT tablename FROM pg_tables WHERE schemaname = 'public' LOOP
    EXECUTE format('ALTER TABLE public.%I OWNER TO payroll_app_role', r.tablename);
  END LOOP;
  FOR r IN SELECT sequencename FROM pg_sequences WHERE schemaname = 'public' LOOP
    EXECUTE format('ALTER SEQUENCE public.%I OWNER TO payroll_app_role', r.sequencename);
  END LOOP;
END $$;
```

Xác nhận: `SELECT count(*) FROM pg_tables WHERE schemaname='public' AND tableowner != 'payroll_app_role';`
→ kỳ vọng `0`.

### Bước 3 — verify RLS thật, TRƯỚC khi đổi `.env` (dùng role mới qua `psql` tay)

```bash
PGPASSWORD='<mật khẩu Bước 1>' psql -h localhost -U payroll_app_role -d payroll_engine -c "
SET app.company_scope_unlimited = 'false';
SET app.company_scope_codes = 'MA_CONG_TY_KHONG_TON_TAI_060826';
SELECT count(*) FROM employees;"
```
Kỳ vọng: `0` (RLS chặn thật — trước đây với `postgres` sẽ luôn thấy toàn bộ, bất kể setting này).

Đối chứng cùng lệnh với `app.company_scope_unlimited='true'` → kỳ vọng thấy đủ dòng (không bị chặn
khi unlimited=true, đúng logic policy).

**Nếu bước này không ra đúng kỳ vọng — DỪNG, ĐỪNG đổi `.env`.** Rollback: `ALTER TABLE ... OWNER TO
postgres` lại từng bảng (dùng cùng khuôn vòng lặp Bước 2, đổi `payroll_app_role` → `postgres`), hoặc
restore từ dump Bước 0.

### Bước 4 — đổi kết nối của backend

Sửa `Core System-backend/.env`:
```
DB_USER=payroll_app_role
DB_PASSWORD=<mật khẩu Bước 1>
```

### Bước 5 — nghiệm thu backend thật

```bash
cd Core System-backend && AUTO_MIGRATE=true go run ./cmd/Core System
```
Kỳ vọng: log "Connected to database payroll_engine on localhost:5432" rồi "Database migrations
completed successfully" — KHÔNG có `migration N failed`. Đây là phép thử quan trọng nhất: xác nhận
`RunMigrations()` (105 bảng `CREATE TABLE IF NOT EXISTS`, nhiều `ALTER TABLE ADD COLUMN IF NOT
EXISTS`) chạy được với owner mới — nếu có bất kỳ migration nào fail, đọc thông báo lỗi cụ thể (thường
là "permission denied for table X" nếu Bước 2 bỏ sót bảng nào), sửa (chạy lại Bước 2 cho bảng đó),
không tự ý revert toàn bộ.

Dừng backend, chạy lại lần 2 (idempotent check) — xác nhận không lỗi.

### Bước 6 — chạy full test suite

```bash
TEST_DATABASE_URL="postgres://postgres@localhost:5432/payroll_engine?sslmode=disable" go test ./...
```
Lưu ý: `TEST_DATABASE_URL` (biến riêng cho test, hardcode `postgres://postgres@...`) KHÔNG đổi — test
tích hợp vẫn kết nối bằng `postgres` để có toàn quyền dựng/xoá fixture, độc lập với `.env` của app
thật. Kỳ vọng: đúng baseline đã biết (6 fail cố định: `TestG1AllProtectedRoutesRequireRoleGateExceptAllowlist`,
`TestPermissionGateCoverageReport`, `TestReportPayrollSummaryRouteRequiresPeriodID`,
`TestReportBankTransferRouteRequiresPeriodID`, `TestPipelineProtectedRunRouteWithDevAuthReachesHandler`,
`TestPipelineProtectedLogsRouteWithDevAuthReachesHandler`), không có fail MỚI.

### Bước 7 — dọn dẹp

Xoá dump backup nếu mọi thứ ổn (`rm /tmp/payroll_engine_before_L10_060826.dump`) — CHỈ xoá sau khi
Bước 5+6 đã pass, không xoá sớm.

## Ràng buộc tuyệt đối

- CHỈ làm trên DB dev local `payroll_engine`. KHÔNG đụng staging/production trong brief này.
- KHÔNG dùng chung `agent_data_role` cho việc này — role đó dành cho agent thao tác `psql` tay, mục
  đích khác (không cần chạy liên tục, không cần là owner bảng).
- KHÔNG commit mật khẩu thật vào `.env` nếu `.env` không nằm trong `.gitignore` (kiểm bằng `git
  check-ignore Core System-backend/.env` trước khi sửa — nếu không bị ignore, DỪNG và hỏi).
- KHÔNG xoá dump backup (Bước 0) trước khi Bước 5+6 xác nhận pass.

## DỪNG và hỏi khi

- Bước 3 (verify RLS bằng psql tay) không ra đúng kỳ vọng — nghĩa là hoặc policy có vấn đề, hoặc thứ
  gì đó khác đang cho phép bypass mà brief chưa biết.
- Bước 5 (`RunMigrations()` với role mới) fail vì lý do KHÁC "permission denied cho 1 bảng cụ thể" —
  có thể là giả định "không có lệnh cần superuser" đã sai, cần đọc lại toàn bộ `RunMigrations()` slice
  chứ không chỉ vá từng bảng.
- `.env` không bị gitignore.

## Định nghĩa xong

1. Dump backup đã tạo (Bước 0).
2. `payroll_app_role` tồn tại, sở hữu toàn bộ 105 bảng + 8 sequence.
3. Verify RLS bằng `psql` tay (Bước 3) — 0 dòng khi company_scope không khớp, đủ dòng khi unlimited.
4. `.env` đổi `DB_USER`/`DB_PASSWORD`, backend khởi động 2 lần liên tiếp không lỗi migration.
5. `go test ./...` — đúng 6 fail baseline, 0 fail mới.
6. Cập nhật `self-docs/RBAC-Backlog-Tracklist-160726.md` (xoá/đóng L10), `00-START-HERE.md` (xoá L10
   khỏi bảng lỗi mục 2), dòng nhật ký `CLAUDE.md`.
7. Commit — CHỈ commit `self-docs/`/`CLAUDE.md`/`00-START-HERE.md` (tài liệu), **KHÔNG commit
   `.env`** (chứa mật khẩu DB, phải nằm trong `.gitignore` — xác nhận trước khi commit bất cứ gì).
