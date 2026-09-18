---
id: self-docs/security/rbac-phase1a-test-plan
canonical_question: 'Technical guide and specification: RBAC-Phase1A-Test-Plan-200726'
aliases:
- RBAC-Phase1A-Test-Plan-200726
- RBAC Phase1A Test Plan 200726
entity_type: how_to
domain: self-docs > security
last_verified: 2026-07-20
---

# RBAC-Phase1A-Test-Plan-200726

**Ngày:** 2026-07-20
**Vai trò tài liệu:** đối chiếu 2 file kế hoạch do phiên bản Claude web tạo ra (`self-docs/files/RBAC-Phase1-Improvement-TestStrategy.md`, `self-docs/files/RBAC-Test-Templates-and-Samples.md`) với tình trạng thật của codebase, rồi đề xuất một kế hoạch Phase 1A đã được điều chỉnh để khớp với code thật thay vì code mẫu tưởng tượng. Đây là artefact tham khảo, không thay thế báo cáo ngày canonical `self-docs/RBAC-Improvement-Analysis-200726.md`.

## Vì sao cần đối chiếu lại

Hai file kế hoạch được viết bởi một phiên Claude chạy trên web, không có quyền đọc mã nguồn thật của hai repo. Bản kế hoạch đó nắm đúng các sự kiện đã được tôi tóm tắt lại cho người dùng (2 bug đã sửa, mô hình opt-out, cơ chế priority, super-admin), nhưng phần thiết kế test cụ thể — tên hàm, kiểu dữ liệu, thư viện, cấu trúc thư mục — được suy đoán theo khuôn mẫu Go/React phổ biến chứ không phải từ code thật, nên phần lớn code mẫu trong file thứ hai (`RBAC-Test-Templates-and-Samples.md`) sẽ không biên dịch được nếu copy-paste thẳng vào repo. Mục đích của tài liệu này là chỉ ra chính xác chỗ nào sai khác và đề xuất cách làm khớp với code thật.

## Bảng đối chiếu: giả định trong kế hoạch vs thực tế codebase

| Chủ đề | Kế hoạch giả định | Thực tế trong codebase | Hệ quả nếu copy nguyên |
|---|---|---|---|
| Driver DB (Go) | `github.com/jackc/pgx/v5`, `pgxpool.Pool` | `github.com/jmoiron/sqlx` + `github.com/lib/pq` (`go.mod`, dùng `*sqlx.DB` khắp `internal/repository/`, `internal/middleware/`) | Không biên dịch được — hai thư viện có API hoàn toàn khác nhau. |
| Thư viện assertion test (Go) | `github.com/stretchr/testify` (`assert.True`, `require.NoError`) | Không có testify trong `go.mod` — mọi test hiện tại (`internal/middleware/*_test.go`, `internal/repository/*_test.go`) dùng thẳng `testing` chuẩn với `t.Fatalf` | Thêm testify là thêm 1 dependency mới không nhất quán với 100% test hiện có trong repo — nên tránh trừ khi có quyết định đổi convention rõ ràng. |
| Kiểu khoá chính role/employee | Số nguyên (`role_id=10`, `user_id="user100"` dạng string tuỳ ý) | `roles.id` và `employee_roles.employee_id`/`role_id` đều là `uuid` thật (`internal/db/schema.sql`, `internal/models/rbac.go`) | Test insert sai kiểu cột → lỗi SQL ngay khi chạy, không phải lỗi logic. |
| Tên cột liên kết nhân viên | `employee_roles.user_id` | Cột thật tên là `employee_id` (khớp bảng `employees.id`, đã xác minh lại ở phiên trước — không phải `employee_code`/`hris_id`) | Toàn bộ câu SQL insert trong template sai tên cột, sẽ lỗi "column does not exist". |
| Tầng gọi permission | `service.NewPermissionService(db)`, `svc.ResolvePermission(...)`, `models.User{Roles: []int{...}}` | Không có `PermissionService` hay `models.User` nào trong repo. Logic nằm thẳng trong hàm gói-nội-bộ `resolveModuleActionPermission(db *sqlx.DB, module, action string, roles []string)` (`internal/middleware/permission.go`), được gọi trực tiếp bởi middleware `RequirePermission` — role là slice string (mã role), không phải object User. | Test viết theo mẫu sẽ gọi vào các type/hàm không tồn tại — lỗi biên dịch ngay từ bước import. |
| Cấu trúc thư mục test (Go) | `Core System-backend/tests/unit/`, `tests/integration/`, `tests/fixtures/*.json` — một cây thư mục test tách biệt khỏi `internal/` | Convention Go tiêu chuẩn của repo: file `_test.go` nằm CÙNG package với code nó test (`internal/middleware/permission_integration_test.go` cạnh `permission.go`), không có cây `tests/` riêng, không có fixture JSON — mỗi test tự seed dữ liệu tối thiểu bằng SQL trực tiếp trong hàm test (`seedPermissionTestRole`/`cleanupPermissionTestRole`) rồi tự dọn bằng `t.Cleanup`. | Tạo thêm 1 convention cấu trúc thư mục song song, gây lệch chuẩn, khó bảo trì lâu dài — nên đi theo convention có sẵn thay vì nhập convention mới từ ngoài vào. |
| Test DB setup | `docker-compose.test.yml` mới, `pgxpool.New`, tự chạy migration trong `SetupTestDB` | Không có `docker-compose*.yml` nào trong `Core System-backend` (chỉ có `Dockerfile` cho image app). Convention có sẵn: `internal/testutil/dbtest.Open(t)` đọc biến môi trường `TEST_DATABASE_URL`, tự `t.Skip(...)` nếu chưa set — không tự chạy migration, kỳ vọng DB test đã có sẵn schema từ trước (migrate bằng tay hoặc trỏ vào 1 DB dev đã migrate). | Không sai về ý tưởng (có DB test cô lập là tốt), nhưng nên tái dùng `dbtest.Open` có sẵn thay vì viết lại bộ khởi tạo mới; và cần quyết định nguồn DB (xem phần quyết định bên dưới). |
| CI | `.github/workflows/test.yml` (GitHub Actions) | Remote của cả 2 repo là **GitLab** (`code.vsol.vn`), không phải GitHub — 1 workflow GitHub Actions đặt trong repo sẽ **không bao giờ tự chạy**. Hiện tại **không có `.gitlab-ci.yml`** ở cả 2 repo — chưa có CI nào gate test/coverage thật. (`Core System-backend` có 1 thư mục `.github/` nhưng đang **untracked**, không phải phần đã commit; `Core System-frontend` có `.github/workflows/harness.yml` nhưng chỉ là lint tài liệu markdown nội bộ, không liên quan gì tới test app.) | Nếu copy nguyên, file YAML sẽ nằm im trong repo không tác dụng gì — gây ảo giác "đã có CI gate" trong khi thực tế chưa có gì chạy. |
| Test framework FE | Jest + React Testing Library, import `roleMatrixChecked` như 1 hàm export độc lập từ `TinhLuongExcel.tsx`, gọi trực tiếp `roleMatrixChecked('employee', 'reports', 'view', dbPermissions)` | `Core System-frontend` **chưa có bất kỳ hạ tầng test nào** (không jest/vitest/RTL trong `package.json`, không file config, không thư mục `__tests__/`). Quan trọng hơn: `roleMatrixChecked` thật (`components-page/tinh-luong/TinhLuongExcel.tsx`) là 1 **closure định nghĩa bên trong thân component** `TinhLuongExcel`, đọc `state.roleMatrix` qua closure — **không phải hàm thuần nhận tham số** như mẫu giả định. Không thể import và gọi trực tiếp như trong template. | Test mẫu sẽ không compile được — sai cả về hạ tầng (chưa cài gì) lẫn về hình dạng hàm (không phải pure function nhận tham số). |
| Endpoint lưu ma trận quyền | `POST /api/permissions` với body `{ role_id, changes: [...] }` (diff tăng dần) | Endpoint thật là `PUT /api/v1/roles/{id}/permissions` (`internal/app/router.go:273`), nhận **mảng đầy đủ** `[{module, action, granted}]` không có `roleId` trong body (roleId nằm trên URL), và ghi kiểu **upsert** (`ON CONFLICT ... DO UPDATE`) chứ không xoá các dòng bị bỏ khỏi mảng — không phải mô hình "diff các ô đã đổi". | Test integration end-to-end viết theo endpoint/format sai sẽ không bao giờ gọi đúng API thật. |

## Đề xuất Phase 1A đã điều chỉnh

Giữ nguyên đúng MỤC TIÊU của Phase 1A trong kế hoạch gốc (test infra + coverage cho logic permission + test tái hiện 2 bug + seed/migration verification), chỉ thay cách làm cho khớp code thật:

### Backend (`Core System-backend`)

1. **Không tạo cây `tests/` mới.** Tiếp tục viết thêm test ngay trong `internal/middleware/permission_integration_test.go` (đã có 6 test ở đó sau phiên trước — 3 test gốc từ 150726 + 3 test mới 200726 tái hiện đúng 2 bug và cơ chế priority). Việc "viết test unit cho `resolveModuleActionPermission`" mà Phase 1A yêu cầu — **phần lớn đã làm xong**, chỉ còn thiếu bằng chứng chạy xanh thật trên Postgres (xem mục seed/DB bên dưới).
2. **Bổ sung thật sự còn thiếu:** test kết hợp priority + company/department scope (ý tưởng IT-TASK-REF trong kế hoạch gốc là đúng hướng, nhưng cần viết lại đúng chữ ký thật — `middleware.ResolveCompanyScope`/`ResolveDepartmentScope`, cột `scope_company_id`/`scope_department_id` là `uuid`, không phải `scope_company_id="comp_a"` dạng string tuỳ ý). Chưa có test nào kiểm chứng "priority + scope cùng lúc" — đây là khoảng trống thật, không phải đã làm.
3. **`scripts/verify-migration.sh`** — không cần viết mới hoàn toàn: `Core System-backend/scripts/atlas-check.sh` đã làm gần hết việc này (kiểm `atlas migrate validate`/`lint`, fail-open khi thiếu `atlas` CLI, fail cứng khi `--ci`). Việc cần làm chỉ là **gọi nó** từ một bước CI/pre-commit thật (xem mục CI bên dưới), không phải viết lại logic kiểm tra.
4. **Seed script** — `Core System-backend/internal/database/database.go` (hàm `RunMigrations`/`migrationSeedRoles`) đã là "seed script" thật, tự chạy mỗi lần khởi động app, idempotent. Việc thêm 1 file `scripts/seed-rbac.sql` riêng chỉ nên làm nếu muốn 1 kịch bản dữ liệu MẪU cho việc test thủ công (nhân viên giả, gán role giả) — khác mục đích với seed role hệ thống đã có, nên đặt tên rõ ràng để tránh nhầm hai việc.

### Frontend (`Core System-frontend`)

1. **Cần dựng hạ tầng test từ 0** — đúng như kế hoạch gốc nói, đây là việc thật chưa tồn tại. Đề xuất **Vitest** thay vì Jest: cấu hình cho dự án Next.js 14 + TypeScript đơn giản hơn (không cần babel transform riêng), khởi động nhanh hơn cho vòng lặp test thuần logic — phù hợp với mục tiêu tối thiểu của Phase 1A (test 1 hàm logic, không phải dựng toàn bộ pipeline render).
2. **Bắt buộc phải tách `roleMatrixChecked` ra khỏi closure trước khi viết được unit test** — đây là điểm khác biệt lớn nhất so với kế hoạch gốc. Cách làm: trích xuất phần tính toán thuần (nhận `permMap`, `localChanges`, `module`, `action` làm tham số, trả về boolean — không đọc `state` qua closure nữa) thành 1 hàm export riêng, có thể đặt cạnh `MODULES`/`ACTION_LABELS` trong `lib/rbac-constants.ts` hoặc 1 file mới `lib/permission-resolve.ts`. Đây là 1 khúc refactor nhỏ, thuần tách hàm, KHÔNG đổi hành vi — nhưng là điều kiện tiên quyết bắt buộc, không có cách nào unit-test đúng nghĩa "hàm thuần" nếu không tách trước.
3. **Không nên làm "full-flow.test.tsx" (mount toàn bộ `TinhLuongExcel`) trong Phase 1A.** Component này phụ thuộc `ag-grid`, `exceljs` (dynamic import), context xác thực MSAL, toast — dựng được môi trường jsdom mount đúng tất cả sẽ tốn công sức lớn, dễ vỡ, và không phải mục tiêu "foundation" của Phase 1A. Đề xuất dời loại test này sang giai đoạn sau, khi cần thì làm bằng Playwright chạy thật trên dev server (kiểm tra hành vi UI thật) thay vì cố mock toàn bộ trong Jest/Vitest.

### CI

Hiện KHÔNG có CI thật nào gate test/coverage ở cả 2 repo. Có 2 lựa chọn độc lập nhau, không nhất thiết chọn 1:
- Thêm `.gitlab-ci.yml` (đúng nền tảng, thay vì GitHub Actions vô dụng trong kế hoạch gốc) chạy `go test ./...` + (khi có) `npm run test` mỗi merge request.
- Hoặc trước mắt chỉ dựa vào `verify-before-commit` cục bộ (đã có sẵn theo README harness của dự án) — không cần CI tập trung ngay nếu đội còn nhỏ.

### Test DB cho backend

`dbtest.Open` cần 1 Postgres thật qua `TEST_DATABASE_URL`. Có 2 hướng, cần người dùng chọn (xem câu hỏi bên dưới):
- Trỏ vào DB dev cục bộ đã có sẵn (`postgresql://postgres:postgres@localhost:5433/payroll_dev`, theo `Makefile`'s `REF_DB` mặc định) — nhanh, không cần hạ tầng mới, an toàn vì mọi test đều tự tạo role có mã tiền tố `test_*` rồi tự dọn bằng `t.Cleanup`.
- Dựng `docker-compose.test.yml` riêng (Postgres cô lập, tự migrate từ `atlas/migrations/*.sql`) — sạch hơn, không phụ thuộc máy có sẵn DB dev, nhưng tốn công dựng + bảo trì thêm 1 hạ tầng.

## Việc KHÔNG đưa vào Phase 1A (dời sang 1B/1C như kế hoạch gốc đã đúng)

Giữ nguyên đề xuất gốc: Role Priority Configuration UI, Permission Matrix Backup/Restore tool, RBAC Audit Log bảng riêng (`rbac_audit_log`) — lưu ý bảng audit riêng này **khác** với audit log DENY-decision đã có sẵn từ 150726 (`internal/middleware/access_audit.go`, ghi lại quyết định TỪ CHỐI quyền qua `log/slog`) — cái mới đề xuất ở đây là ghi lại THAY ĐỔI CẤU HÌNH (ai sửa ma trận, sửa role), một việc khác, cross-reference chứ không trùng lặp. ADR/Developer Guide/Runbook (Phase 1C) vẫn hợp lý, chưa cần làm ngay.
