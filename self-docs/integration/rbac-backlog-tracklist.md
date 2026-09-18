---
id: self-docs/integration/rbac-backlog-tracklist
canonical_question: 'Technical guide and specification: Tracklist công việc RBAC/Bảo
  mật còn lại — Core System'
aliases:
- Tracklist công việc RBAC/Bảo mật còn lại — Core System
- RBAC Backlog Tracklist 160726
entity_type: how_to
domain: self-docs > integration
last_verified: 2026-07-16
---

# Tracklist công việc RBAC/Bảo mật còn lại — Core System

**Ngày:** 2026-07-16
**Phạm vi:** Tổng hợp toàn bộ hạng mục RBAC/company-scoping/bảo mật còn mở, tính đến hết ngày 160726, gom từ 4 tài liệu đã có (`RBAC-Hybrid-Scoping-Implementation-140726.md`, `RBAC-Improvement-Analysis-150726.md`, `RBAC-Improvement-Analysis-160726.md`, `RBAC-Workday-Golive-Impact-160726.md`) thành một danh sách việc-cần-làm duy nhất, xếp theo mức độ sẵn sàng triển khai — không lặp lại phân tích chi tiết đã có ở các file gốc, chỉ trích dẫn để tra cứu ngược. Đây là tài liệu canonical cho việc theo dõi tiến độ backlog; cập nhật liên tục khi có việc mới hoàn thành hoặc phát sinh.

Nguyên tắc phân nhóm: nhóm theo **cái gì đang chặn việc bắt đầu làm**, không theo mức độ nghiêm trọng — một gap "Trung bình" nhưng đã có quyết định rõ ràng thì đứng trước một gap "Cao" nhưng còn chờ nghiệp vụ trả lời.

## Nhóm A — Đã quyết định hướng xử lý, sẵn sàng triển khai ngay (không cần hỏi lại)

### A1. Chuyển khoá upsert nhân viên sang `hris_id` — ✅ Đã triển khai 2026-07-16

Nguồn: `RBAC-Workday-Golive-Impact-160726.md` mục 3. Đổi `ON CONFLICT` của upsert `employees` từ `(employee_code, company_code)` sang `hris_id`, để tránh `employee_roles` bị mồ côi khi Workday cấp lại mã nhân viên.

**Đã làm:** migration `atlas/migrations/20260716000000_employees_hris_id_identity_key.sql` (backfill `hris_id` NULL bằng `gen_random_uuid()`, `SET NOT NULL`, `SET DEFAULT gen_random_uuid()` — unique constraint đã có sẵn từ baseline). `internal/repository/employee_repo.go`: `Upsert()` đổi `ON CONFLICT` sang `hris_id`, thêm `resolveHRISIDForUpsert` (khớp dòng cũ theo `employee_code` khi hris_id đến từ Workday khác dòng hiện có — "thăng cấp" placeholder id thành id thật; tái sử dụng hris_id cũ khi nguồn không cung cấp), `employee_code = EXCLUDED.employee_code` thêm vào SET clause; `UpdateFromHRIS()` khớp theo `hris_id` khi có, fallback `employee_code`. Test: `employee_repo_hris_identity_test.go` (3 kịch bản: đổi mã NV giữ nguyên hris_id, nguồn thiếu hris_id tái sử dụng id cũ, nhân viên mới tinh). Migration đã áp dụng vào DB dev `payroll_engine` (xác nhận với người dùng trước khi chạy). `go test ./...`: 623 passed, 12 failed (baseline cũ không đổi).

### A2. Đưa company-scope về kiến trúc FK giống department-scope — ✅ Đã triển khai 2026-07-16

Nguồn: `RBAC-Workday-Golive-Impact-160726.md` mục 3b. Thêm `companies.hris_id`, đổi `employee_roles.scope_company_code` (string) → `scope_company_id` (uuid FK tới `companies.id`), sửa `internal/middleware/scope.go` để so khớp theo id. Đây là rủi ro có tác động rộng nhất trong toàn bộ backlog (một lần đổi mã công ty làm mất quyền của TOÀN BỘ nhân viên thuộc công ty đó).

**Đã làm:** migration `atlas/migrations/20260716010000_company_scope_fk.sql` (`companies.hris_id` uuid unique nullable; `employee_roles.scope_company_id` uuid FK `companies(id) ON DELETE SET NULL`; backfill từ `scope_company_code` hiện có qua `companies.code`). `ResolveCompanyScope` (`internal/middleware/scope.go`) đổi sang JOIN SỐNG `scope_company_id → companies.code` (giống hệt cách `ResolveDepartmentScope` JOIN sống sang `org_structures.name`) — nếu Workday đổi code công ty, lần resolve kế tiếp tự thấy code MỚI, không cần sửa code; vẫn đọc `scope_company_code` cũ làm fallback cho dòng chưa migrate. `SyncFromHRIS` (company_repo.go) được xem lại — không có bug thật cần sửa vì `NOT EXISTS` đã loại trừ đúng, và không có nguồn hris_id thật để dùng trong hàm bootstrap này (ghi chú lại, không đổi code). Test: `internal/middleware/company_scope_fk_integration_test.go` (3 kịch bản: JOIN sống bắt kịp đổi code, fallback dòng cũ, cả 2 cột NULL = unlimited). `go test ./...`: 623 passed, 12 failed (baseline cũ không đổi).

### A3. Chuyển app sang dùng DB role không phải superuser, để RLS trên `employees` có hiệu lực thật

**Đã làm (2026-08-06, dev local — theo brief `self-docs/files/prompt-L10-060826.md`):** tạo role
`payroll_app_role` (`LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS`), chuyển OWNER toàn bộ 106
bảng + 8 sequence trong schema `public` của `payroll_engine` sang role này, đổi
`Core System-backend/.env` (`DB_USER`/`DB_PASSWORD`, không commit — gitignored). Kiến trúc: **1
connection duy nhất** (không tách app-connection/agent-connection), dựa vào `FORCE ROW LEVEL SECURITY`
đã bật sẵn trên `employees` (`RLS` vẫn áp dụng cho cả owner khi có `FORCE`, chỉ superuser/`BYPASSRLS`
mới thoát được). Verify bằng `psql` tay với role mới: `company_scope_codes` không khớp → `0` dòng;
`company_scope_unlimited=true` → đủ `12044` dòng — RLS có tác dụng thật lần đầu tiên. Backend
(`RunMigrations()`, 106 `CREATE TABLE IF NOT EXISTS` + nhiều `ALTER TABLE ADD COLUMN IF NOT EXISTS`)
khởi động 2 lần liên tiếp không lỗi permission. Full suite (`TEST_DATABASE_URL` vẫn dùng `postgres`
theo đúng brief, không đổi): 891 passed/7 failed, khớp baseline tuyệt đối, 0 hồi quy. **Chưa làm ở
staging/production** — brief này chỉ định phạm vi dev local, việc nhân rộng lên môi trường khác là
quyết định vận hành riêng, chưa mở.

Nguồn: `RBAC-Bao-Cao-Bao-Mat-150726.md` mục 2 (gap phát sinh từ đợt 150726). Phát hiện quan trọng bị "chìm" trong các tài liệu cũ, cần nêu bật lại: RLS (R1, đã triển khai 150726) **hiện không có tác dụng thật** vì kết nối Postgres của chính ứng dụng dùng role `postgres` (`BYPASSRLS=true`) — toàn bộ lớp phòng thủ chiều sâu này đang chạy ở chế độ "tồn tại nhưng vô hiệu". Khác với G10 (vai trò DB scope hẹp cho AGENT/Claude Code thao tác trực tiếp — vẫn đang ở trạng thái chuẩn bị, xem A4), đây là việc đổi role kết nối của **chính ứng dụng khi chạy production**, một thay đổi hạ tầng/vận hành có rủi ro thật (đổi sai có thể làm app mất quyền DDL/quyền cần thiết) — cần lên kế hoạch cẩn thận, kiểm thử ở staging trước, không tự làm ẩn trong một đợt code bình thường. Đây là gap tồn tại lâu nhất và có ảnh hưởng tới toàn bộ tuyên bố "đã triển khai RLS" — nên ưu tiên cao dù kỹ thuật không phức tạp.

### A4. Áp dụng `create-agent-data-role.sql` (G10) — chờ xác nhận thời điểm, không phải xác nhận có làm hay không

Nguồn: `RBAC-Improvement-Analysis-160726.md` mục 4. Script đã viết xong và sẵn sàng, người dùng đã xác nhận hướng xử lý ("giữ lại chưa chạy" tại thời điểm 160726) — khi muốn áp dụng, chỉ cần chạy script vào DB dev/staging trước, xác nhận app vẫn hoạt động bình thường (đặc biệt là các luồng migration cần quyền DDL, vì role mới **không có quyền DDL**), rồi mới cân nhắc production.

## Nhóm B — Kỹ thuật đơn giản, nhưng cần xác nhận nghiệp vụ trước khi làm

### B1. Company-scope cho ~12 report generator (`report_gen_*.go`) — ✅ Đã triển khai 2026-07-16

Nguồn: `RBAC-Improvement-Analysis-150726.md` mục 7 (dòng 276), `RBAC-Bao-Cao-Bao-Mat-150726.md` mục 2. Hiện các báo cáo bảng lương ngân hàng/bảo hiểm/kế toán đọc dữ liệu không lọc theo company-scope (`unlimited=true` cố định) — một `hr_admin` bị giới hạn 1 công ty vẫn xuất được Excel chứa dữ liệu MỌI công ty. Người dùng xác nhận (2026-07-16): áp company-scope cho TẤT CẢ report generator, không có ngoại lệ nghiệp vụ.

**Đã làm:** `internal/service/report_export.go` (`ExportReport`, điểm dispatch trung tâm cho 17 report qua registry) — giới hạn danh sách công ty theo `middleware.CompanyReadScopeFromContext` TRƯỚC bước "rỗng = tất cả công ty active", để client không thể tự khai company ngoài phạm vi hoặc lách qua default "tất cả". `internal/service/report_registry.go` thêm `scopeForCompanyCode()` suy ra `(unlimited, allowedCompanies)` thật từ `companyCode` đã được giới hạn, áp vào 11 file `report_gen_*.go`/`report_raw.go` (trước đó tất cả hardcode `GetByPeriod(ctx, periodID, true, nil)` — luôn đọc DB không giới hạn dù có lọc hiển thị sau đó). 7 report còn lại (`report_gen_muc_luong.go` và tương tự) không gọi `GetByPeriod` trực tiếp nhưng đã tự lọc theo `companyCode` sẵn — được bảo vệ gián tiếp nhờ `companyCode` giờ luôn nằm trong phạm vi người gọi. `report_service.go` (`GeneratePayrollSummary`/`GenerateBankTransfer`, 2 route không qua registry) đổi signature nhận `(unlimited, allowedCompanies)` trực tiếp từ handler. `internal/transport/http/report/routes.go` gắn thêm `companyReadScope` middleware cho mọi route xuất file (không gắn `/catalog`). Test: `internal/service/report_export_scope_test.go` (request company ngoài phạm vi bị âm thầm loại, rỗng+PerCompany mặc định về đúng phạm vi thay vì toàn bộ công ty active). `go test ./...`: 623 passed, 12 failed (baseline cũ không đổi).

### B2. Mở rộng `RequirePermission` (View/Edit/Export/Lock/Approve chi tiết) cho 16/19 module còn lại — chưa triển khai, dời sang phiên sau

Nguồn: `RBAC-Bao-Cao-Bao-Mat-150726.md` mục 2. FE đã có sẵn UI "Ma trận quyền hạn" cho tất cả 19 module, nhưng BE mới enforce thật cho 3 module (`Core System`, `PayrollPeriods`, `Reports`) — 16 module còn lại (Employees, Departments, Settings.*...) cấu hình trên UI không có tác dụng thật. Người dùng xác nhận (2026-07-16): áp cho TẤT CẢ 16 module, không giới hạn phạm vi.

**Đánh giá quy mô (160726):** việc gắn middleware tự nó cơ học (lặp đúng mẫu 3 module đã có — `middleware.RequirePermission(db, "<Module>", "view"/"edit")`), nhưng khác B1 (1 điểm dispatch trung tâm `ExportReport` + 13 file cùng một khuôn mẫu), B2 trải trên ~16 route package RIÊNG BIỆT (mỗi module một `Register<X>Routes` function khác nhau, nhiều hàm chưa nhận tham số `db` nên cần thread thêm), mỗi route cần map đúng GET/POST/PUT/DELETE sang view/edit/delete/export theo đúng nghiệp vụ của module đó — không phải một mẫu lặp lại đơn giản như B1. Đã bắt đầu khảo sát (danh sách 19 module đối chiếu `Core System-frontend` `MODULES` const, map sơ bộ module → route registration function), nhưng **dừng lại trước khi triển khai** theo quyết định của người dùng — làm hết 16 module cùng lúc trong một phiên sẽ không đạt mức độ rà soát/test như A1, A2, B1 đã làm (mỗi cái đều có test tái hiện + xác nhận zero regression qua toàn bộ suite). Để phiên sau làm riêng, đủ thời gian test từng module.

### B3. G6 — `site_admin` được gán nhiều hơn 1 công trường cùng lúc

Nguồn: `RBAC-Improvement-Analysis-150726.md` mục G6. Giới hạn kỹ thuật hiện tại là chủ đích (an toàn — 403 thay vì đoán sai), nhưng nếu nghiệp vụ xác nhận có nhu cầu thật, cần đổi kiểu tham số filter (`orgName`/`dept`) từ chuỗi đơn sang mảng ở cả FE lẫn BE — một thay đổi API có thể ảnh hưởng ngược tới client hiện tại, nên chỉ làm khi có xác nhận nhu cầu thật.

### B4. Mở rộng phạm vi role `search_profile` (nếu cần)

Nguồn: `RBAC-Improvement-Analysis-160726.md` mục 6. Hiện `search_profile` chỉ có tác dụng cho List/GetByID hồ sơ nhân viên cơ bản (đã xác nhận với người dùng 160726) — nếu nghiệp vụ sau này muốn mở rộng sang các sub-resource khác (contracts/dependents/educations...), cần một quyết định riêng, không tự mở rộng.

## Nhóm C — Cần dọn dữ liệu/hạ tầng trước khi làm được (không chỉ chờ quyết định)

### C1. G5 — `site_admin` mở rộng theo cây con `org_structures`

Nguồn: `RBAC-Improvement-Analysis-150726.md` mục G5. `ResolveDepartmentScope` hiện chỉ khớp ĐÚNG một node được gán, không tự bao gồm các node con cháu trong cây `org_structures` (`parent_id`). Việc mở rộng theo cây là hợp lý về mặt kỹ thuật, nhưng bị chặn bởi CHẤT LƯỢNG DỮ LIỆU: cột `org_level` trong dữ liệu thật không đủ sạch (nhiều dòng trống/lỗi encoding) để suy luận an toàn "công trường" tương ứng cấp nào trong cây. Đoán sai gây hậu quả hai chiều (chặn nhầm hoặc lộ nhầm dữ liệu) — cần nghiệp vụ chuẩn hoá `org_level` trước, đây là việc của đội dữ liệu/vận hành, không phải việc thuần code RBAC.

### C2. `SetCell` atomic hoàn toàn (nợ kỹ thuật nhỏ)

Nguồn: `RBAC-Improvement-Analysis-150726.md` mục 4/7.4. Bước ghi override đầu tiên của `SetCell` không nằm trong transaction, khác với `UndoCell`/`PatchDay` đã atomic hoàn toàn — giới hạn kỹ thuật thật (engine tính lương cần đọc dữ liệu đã commit qua kết nối khác), cần thiết kế lại luồng đọc-ghi nếu muốn giải quyết dứt điểm, không phải một sửa nhỏ.

## Nhóm D — Quyết định nghiệp vụ thuần, có thể triển khai an toàn ở chế độ cảnh báo trước khi quyết chặn hẳn

### D1. G7 — Separation of Duties (four-eyes) cho Calculate/Finalize cùng kỳ lương

Nguồn: `RBAC-Improvement-Analysis-150726.md` mục G7, `RBAC-Bao-Cao-Bao-Mat-150726.md` mục 3. Có bắt buộc người tính lương khác người duyệt hay không là quyết định của tổ chức, không phải quyết định kỹ thuật — tài liệu gốc chỉ nêu gap. Có thể triển khai an toàn ở dạng **shadow-mode** (chỉ cảnh báo/audit log khi cùng một người Calculate rồi Finalize, không chặn) trong lúc chờ quyết định có cần chặn cứng hay không — không cần chờ quyết định nghiệp vụ mới bắt đầu được phần cảnh báo.

### D2. G8 — Kích hoạt Hierarchical RBAC cho một vai trò thật

Nguồn: `RBAC-Improvement-Analysis-150726.md` mục G8. Cơ chế `parent_role_id` + `expandRoleHierarchy` đã sẵn sàng từ 140726 nhưng chưa role nào dùng — cơ hội bỏ ngỏ, không phải bug. Nếu nghiệp vụ tương lai cần một vai trò như "hr_manager" tự động thừa hưởng quyền của `hr_admin` cộng thêm quyền riêng, chỉ cần một quyết định nghiệp vụ + một câu UPDATE gán `parent_role_id`, không cần code mới.

### D3. Thiết kế quy trình "Duyệt thay" (approve-on-behalf/delegation)

Nguồn: `RBAC-Bao-Cao-Bao-Mat-150726.md` mục 3, phần còn lại duy nhất của yêu cầu bảo mật nghiệp vụ #1 (phân quyền chi tiết theo hành động). Đây không phải một quyền on/off đơn giản mà là một quy trình ủy quyền cần thiết kế trước khi code: ai ủy quyền cho ai, có giới hạn thời gian không, luồng xác nhận (A yêu cầu → B chấp nhận, hay A tự set), audit trail phải ghi rõ "B hành động nhân danh A", và cách quy trình này tương tác với G7 (SoD) — người được uỷ quyền duyệt thay có tính vào ràng buộc four-eyes hay không. Cần một phiên thiết kế riêng với nghiệp vụ trước khi bắt tay viết code.

**Cập nhật 230726:** Approve/Reject CƠ BẢN cho `PayrollRecord` (người có quyền `approve` trực tiếp tự duyệt/từ chối bản ghi, KHÔNG có khái niệm uỷ quyền) đã triển khai — xem `llmwiki/wiki/sources/draft/230726-Core System-approve-reject-flow.md`. D3 (uỷ quyền/delegation, "B duyệt thay A") **vẫn còn mở**, không bị đóng bởi việc này — hai gap khác nhau về bản chất, chỉ trùng tên gọi bề mặt ("duyệt"/"approve").

### D4. G3 — Đồng bộ vai trò với Azure AD (IdP)

Nguồn: `RBAC-Improvement-Analysis-150726.md` mục G3. Rủi ro: nhân viên nghỉ việc bị vô hiệu hoá ở Azure AD nhưng `employee_roles` không tự động bị thu hồi. Khả thi kỹ thuật (Azure AD hỗ trợ group claims trong JWT hoặc Graph API để poll trạng thái), nhưng cần quyết định nghiệp vụ trước: có muốn quyền Core System gắn với group Azure AD hay giữ mô hình quản trị độc lập trong app như hiện tại? WorkOS (nguồn tham khảo gốc) cảnh báo việc này có nhiều biến chứng thực tế (IdP thường chỉ push chứ không cho poll, các IdP khác nhau xử lý deactivation khác nhau) — không nên đánh giá thấp độ phức tạp. Hiện đã có giải pháp tạm thời: `RBAC-JML-Checklist-Van-Hanh-150726.md` (quy trình thủ công) + `GET /roles/access-review` (phát hiện quyền bất thường định kỳ) — G3 là tự động hoá hoàn toàn quy trình đó, không phải lớp phòng thủ duy nhất.

## Nhóm E — Ngoài phạm vi RBAC thuần, cần phối hợp đội khác (đã bàn giao, không tự làm)

### E1. `hris_attendance_daily.org_structure_id`

Nguồn: `RBAC-Workday-Golive-Impact-160726.md` mục 4, đặc tả cột ở mục 7.2. Thuộc phạm vi đội data/adapter — đã có đặc tả cột đầy đủ (kiểu `uuid`, nguồn dữ liệu, ràng buộc) để bàn giao.

## Bảng tổng hợp theo mức ưu tiên đề xuất

| Ưu tiên đề xuất | Việc | Nhóm | Trạng thái |
|---|---|---|---|
| 1 | A3 — chuyển app sang DB role non-superuser | A | ✅ Đã triển khai 2026-08-06 **(dev local — CHỈ `payroll_engine` trên `localhost`, KHÔNG đụng staging/production)** |
| 2 | A2 — company-scope sang FK (`scope_company_id`) | A | ✅ Đã triển khai 2026-07-16 |
| 3 | A1 — employee upsert sang `hris_id` | A | ✅ Đã triển khai 2026-07-16 |
| 4 | B1 — company-scope cho report generator | B | ✅ Đã triển khai 2026-07-16 |
| 5 | D1 — SoD shadow-mode (chỉ cảnh báo) | D | Chưa làm |
| 6 | A4 — áp dụng agent_data_role ở dev/staging | A | Chưa làm |
| 7 | B2 — RequirePermission cho 16 module còn lại | B | Khảo sát xong, chưa triển khai — dời sang phiên sau (quyết định 2026-07-16, quy mô lớn hơn B1 đáng kể) |
| — | B3–B4, C1–C2, D2–D4 | B/C/D | Cần quyết định nghiệp vụ hoặc dọn dữ liệu trước |
| — | E1 | E | Đã bàn giao đội data/adapter |

**Cập nhật 2026-07-16 (sau phân tích ban đầu):** A1, A2, B1 đã triển khai đầy đủ (code + migration + test + xác nhận zero regression qua toàn bộ `go test ./...`, 623 passed/12 failed — 12 fail là baseline cũ có từ trước, không phải hồi quy mới). Migration đã áp dụng vào DB dev `payroll_engine`. B2 đã khảo sát sơ bộ nhưng dừng lại theo quyết định người dùng, dời sang phiên sau. A3, A4, D1 và các mục còn lại trong nhóm B/C/D/E vẫn giữ nguyên trạng thái "chưa làm" như phân tích ban đầu.
