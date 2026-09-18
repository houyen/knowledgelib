---
id: self-docs/security/rbac-technical-code-audit
canonical_question: 'Technical guide and specification: RBAC-Technical-Code-Audit-210726'
aliases:
- RBAC-Technical-Code-Audit-210726
- RBAC Technical Code Audit 210726
entity_type: how_to
domain: self-docs > security
last_verified: 2026-07-21
---

# RBAC-Technical-Code-Audit-210726

**Ngày:** 2026-07-21
**Loại tài liệu:** code review kỹ thuật (technical debt / bug thật trong code) — KHÁC hẳn mọi tài liệu RBAC trước đó.

## 0. Vì sao cần tài liệu này, khác gì với `RBAC-Tri-Party-Comparison-210726.md`

Toàn bộ phân tích trước — nội bộ (`RBAC-Architecture-Reassessment-200726.md`), Gemini, GPT, và bản so sánh 3 bên — đều nhìn ở tầng **logic nghiệp vụ/chính sách/kiến trúc** (default-allow đúng không, có nên chặn self-escalation không, 4 cơ chế có nên hợp nhất không...). Không tài liệu nào trong số đó thực sự **đọc từng dòng code** để hỏi câu hỏi khác: *code hiện tại viết đúng kỹ thuật không, hay có bug ẩn/nợ kỹ thuật mà chưa ai chạm tới?*

Tài liệu này trả lời đúng câu hỏi đó. Mọi finding dưới đây đã được **đọc trực tiếp từ code thật** trên nhánh `sec_dev` (không suy luận từ tài liệu), trích dòng cụ thể, xác nhận lại bằng `grep`/đọc file sau khi 1 agent audit ban đầu báo cáo — không đưa vào đây finding nào chưa tự tay xác nhận.

File đọc: `internal/middleware/auth.go`, `internal/middleware/permission.go`, `internal/middleware/scope.go`, `internal/middleware/access_audit.go`, `internal/handler/role_handler.go`, `internal/service/role_service.go`, `internal/service/audit_log_service.go`, `internal/repository/role_repo.go`, `internal/repository/scoped_executor.go`, `internal/repository/employee_repo.go`, `internal/service/payroll_scoped_resolver.go`, `internal/models/rbac.go`, migration `20260714000000_rbac_hierarchy_company_scope.sql`, `20260720000000_role_priority.sql`.

## 1. Findings — xếp theo mức nghiêm trọng

### 1.1. HIGH — `RoleRepo.Update` no-op thầm lặng trên system role, nhưng audit log vẫn ghi như đã đổi thành công — ✅ ĐÃ SỬA 2026-07-22

`internal/repository/role_repo.go:37-42`
```go
func (r *RoleRepo) Update(ctx context.Context, role *models.Role) error {
	_, err := r.db.ExecContext(ctx,
		`UPDATE roles SET name=$1, code=$2, description=$3, updated_at=NOW() WHERE id=$4 AND is_system=FALSE`,
		role.Name, role.Code, role.Description, role.ID)
	return err
}
```
Không kiểm `RowsAffected()`. Gọi `PUT /roles/{id}` với `id` của 1 role hệ thống (`is_system=TRUE`, ví dụ `hr_admin`/`config_admin`) → điều kiện `AND is_system=FALSE` khiến 0 dòng bị sửa, `err = nil` (Postgres không coi 0-row UPDATE là lỗi). Handler trả về 200 OK, và `RoleService.Update` (nối audit trail ở mục 13 tài liệu trước) vẫn ghi 1 dòng vào `audit_logs` với `NewValues` = giá trị người dùng GỬI LÊN — trong khi DB thật không đổi gì. Kết quả: admin tưởng đã đổi tên/description role hệ thống thành công (UI trả 200, audit log "xác nhận" đã đổi), nhưng lần load lại thấy y nguyên — và audit log lại đang **nói dối** về việc đã có thay đổi. Có thể tái hiện ngay hôm nay, không cần điều kiện đặc biệt.

**Cách sửa gợi ý:** dùng `sql.Result.RowsAffected()`, trả lỗi rõ (`ErrRoleNotEditable` hoặc tương đương) khi 0 rows, để handler trả 403/409 thay vì 200 giả.

**Đã triển khai 2026-07-22:** `RoleRepo.Update` (`internal/repository/role_repo.go`) giờ kiểm `RowsAffected()`, trả `ErrRoleUpdateNoRows` khi 0 dòng. `RoleService.Update` (`internal/service/role_service.go`) dùng kết quả `GetByID` đã gọi trước đó để phân biệt 2 lý do: role không tồn tại → `ErrRoleNotFound`, role hệ thống → `ErrRoleNotEditable` — cả 2 đều KHÔNG ghi audit log (audit chỉ ghi sau khi `repo.Update` trả `nil`, đúng thứ tự code sẵn có). `RoleHandler.Update` (`internal/handler/role_handler.go`) map 2 lỗi trên thành `404`/`409` thay vì `200` giả. Test mới: `internal/repository/role_integration_test.go` (3 test — system role no-op, role không tồn tại, role thường vẫn sửa được bình thường) + `internal/service/role_service_audit_integration_test.go` (xác nhận không ghi audit log giả + đúng sentinel error). `go build`/`go vet` sạch, `go test ./...` trên `payroll_engine`: 700 passed, 9 failed — đúng 9 fail baseline cũ (repository ×2, geo ×2, handler ×4, me ×1), không hồi quy.

### 1.2. HIGH — Role-hierarchy (kế thừa quyền) và priority-tier (phân tầng ưu tiên khi xung đột) vô tình dùng CHUNG một danh sách role, gây nhiễu ngữ nghĩa — ✅ ĐÃ SỬA 2026-07-22

`internal/middleware/auth.go:112` (`expandRoleHierarchy`) mở rộng danh sách role trực tiếp của user thêm mọi role TỔ TIÊN theo `parent_role_id`, ghi vào `UserRolesKey` trong context. `internal/middleware/permission.go:34` đọc lại CHÍNH danh sách đã mở rộng đó (`roles, _ := r.Context().Value(UserRolesKey).([]string)`), rồi dùng nó để tính `maxPriority` (`permission.go:118-126`) — tầng ưu tiên cao nhất trong số các role "user đang giữ".

Vấn đề: 2 tính năng được xây ở 2 ngày khác nhau (hierarchy ngày 140726, priority ngày 200726) chưa từng được đối chiếu chéo. `expandRoleHierarchy` tồn tại để PHỤC VỤ KẾ THỪA quyền (role cấp trên tự có quyền của role cấp dưới, không cần khai lại `permissions`) — nhưng vì nó ghi thẳng vào `UserRolesKey`, priority-tier lại coi luôn TỔ TIÊN suy ra được là role user "đang giữ trực tiếp" để tham gia phân tầng ưu tiên.

**Kịch bản lỗi cụ thể:** user được gán trực tiếp role X (`priority=0`). X có `parent_role_id` trỏ tới role Y (`priority=10`, do admin set tay qua "Ma trận theo Role" hoặc SQL trực tiếp — chưa có UI cho priority nhưng cột đã tồn tại và ghi được). `expandRoleHierarchy` cộng Y vào danh sách role của user (đúng thiết kế — để kế thừa quyền Y). Nhưng `resolveModuleActionPermission` sau đó tính `maxPriority=10` (của Y) và **loại bỏ hoàn toàn quyền deny tường minh mà X đã cấu hình** cho module đó — dù user chưa từng được ai GÁN role Y. Nói cách khác: cấu hình hierarchy cho mục đích kế thừa vô tình cho phép leo thang/mất quyền theo hướng không ai chủ động chọn.

Hiện tại CHƯA có UI đặt `priority>0` nên lỗi này đang **ngủ** (không role nào thật có priority khác 0 kèm hierarchy sâu 2+ tầng cùng lúc) — nhưng đây đúng là kịch bản "admin set bằng tay" mà comment code chính nó dự đoán sẽ xảy ra khi priority UI ra đời.

**Cách sửa gợi ý:** priority-tier nên tính trên danh sách role GÁN TRỰC TIẾP (`employee_roles`, trước khi mở rộng hierarchy), không phải danh sách đã mở rộng — 2 khái niệm (kế thừa quyền vs phân tầng xung đột) cần 2 danh sách role riêng, không dùng chung 1 context key.

**Phân tích sâu + phương án khắc phục + triển khai thật:** xem `self-docs/RBAC-Priority-Hierarchy-Collision-Fix-220726.md` — luồng dữ liệu đầy đủ, ràng buộc phải giữ, so sánh Phương án A/B, và mục 6 (triển khai thật 2026-07-22): `UserDirectRolesKey` mới (`auth.go`), `resolveModuleActionPermission` viết lại (role trực tiếp có dòng riêng → tuyệt đối, không tham khảo tổ tiên; chỉ fallback lên tổ tiên khi role trực tiếp im lặng hoàn toàn — phát hiện phụ khi viết test: thiết kế "gắn nhãn priority theo sponsor" ban đầu vẫn sai vì để tổ tiên đồng bỏ phiếu như sibling). 2 test mới `permission_priority_hierarchy_integration_test.go`. `go test ./...`: 703 passed, 9 failed (baseline cũ, không hồi quy). Chưa commit.

### 1.3. MEDIUM — Cycle-safety của recursive CTE `expandRoleHierarchy` là ngẫu nhiên, không phải chủ đích, không có tài liệu/ghi chú cảnh báo

`internal/middleware/auth.go:120-133`:
```go
func expandRoleHierarchy(db *sqlx.DB, codes []string) []string {
	...
	err := db.Select(&expanded, `
		WITH RECURSIVE anc AS (
			SELECT id, code, parent_role_id FROM roles WHERE code = ANY($1)
			UNION
			SELECT r.id, r.code, r.parent_role_id
			FROM roles r
			JOIN anc ON r.id = anc.parent_role_id
		)
		SELECT DISTINCT code FROM anc`, pq.Array(codes))
	...
}
```
Migration `20260714000000_rbac_hierarchy_company_scope.sql` chỉ thêm FK cho `roles.parent_role_id`, **không có CHECK/trigger nào chặn cycle** (A → parent B → parent A). Query hiện tại dùng `UNION` (không phải `UNION ALL`) — Postgres tự loại dòng trùng chính xác, nên với 1 cycle, recursion vẫn KẾT THÚC (không treo) vì các dòng lặp lại bị dedup. Đây là hành vi ĐÚNG hôm nay, nhưng **hoàn toàn ngẫu nhiên/không tài liệu hoá** — không có comment nào nói "phải giữ UNION vì lý do cycle-termination". Một dev sau này nhìn `UNION` + `SELECT DISTINCT` ở cuối sẽ thấy có vẻ dư thừa (dedup 2 lần) và có thể "tối ưu" đổi `UNION` → `UNION ALL` (nhìn hợp lý vì tưởng dòng không bao giờ trùng) — nếu khi đó tồn tại 1 cycle thật trong dữ liệu `roles.parent_role_id`, câu query sẽ **đệ quy vô hạn**, treo mọi request login của user chạm role đó, có thể làm cạn connection pool. Vì hierarchy hiện chỉ set được qua SQL tay (chưa có UI), khả năng tạo cycle do nhập nhầm là có thật và không có gì chặn ở tầng schema.

**Cách sửa gợi ý:** (a) thêm comment tường minh ngay tại câu SQL giải thích vì sao phải giữ `UNION` (không phải `UNION ALL`); (b) thêm 1 test cố ý tạo cycle 2 role trỏ vào nhau, xác nhận query không treo (hiện chưa có test này); (c) xem xét thêm 1 CHECK constraint hoặc validation ở tầng service khi set `parent_role_id` để chặn cycle từ gốc, không dựa vào tác dụng phụ của `UNION`.

### 1.4. MEDIUM — Lỗi DB trên đường đi auth bị nuốt hoàn toàn, không log, hạ quyền âm thầm — ✅ ĐÃ SỬA 2026-07-22

`internal/middleware/auth.go` — cả 3 hàm `isSuperAdmin` (dòng 61), `allRoleCodes` (dòng 73), và nhánh lấy role trực tiếp trong `getAppRoles` (dòng 88-113) đều theo mẫu `if err != nil { return <fallback thấp nhất> }` — không có bất kỳ lời gọi log nào (không `slog`, không `fmt.Printf`) khi query lỗi. Một lỗi DB tạm thời (mất kết nối, timeout, hoặc query vỡ sau khi đổi schema) khiến MỌI user bị coi như chỉ có role `"employee"` (thấp nhất) cho request đó — im lặng hoàn toàn. Khi người dùng report "tự nhiên bị mất quyền truy cập", không có gì để `grep` trong log phân biệt "đúng là user đó ít quyền" với "vừa có lỗi DB trong lúc resolve role" — đây đúng dạng sự cố khó chẩn đoán mà `access_audit.go` (mục 12, `logAuthzAllowed`/`logAuthzDenied`) được xây ra để giải quyết ở tầng quyết định cho phép/từ chối, nhưng KHÔNG che được tầng resolve-role bên dưới nó, nơi lỗi này nằm.

**Cách sửa gợi ý:** thêm `slog.Error`/`slog.Warn` (kèm `request_id` nếu có sẵn trong context tại điểm gọi) ở cả 3 điểm nuốt lỗi này, tối thiểu ở mức đủ để phân biệt "lỗi hạ tầng" với "user thật sự ít quyền" khi debug.

**Đã triển khai 2026-07-22:** cả 3 hàm (`isSuperAdmin`, `allRoleCodes`, nhánh query chính của `getAppRoles`) giờ gọi `slog.Error` khi gặp lỗi DB THẬT, còn giữ im lặng đúng như cũ khi đó là trạng thái hợp lệ (`sql.ErrNoRows` ở `isSuperAdmin` = "không phải super-admin", `len(codes)==0` ở `getAppRoles` = "nhân viên chưa có role nào") — fail-safe trả về (cho phép/từ chối) giữ nguyên 100%, chỉ thêm quan sát. Test mới (`internal/middleware/auth_integration_test.go`): `TestIntegrationIsSuperAdminSilentOnNoRowsLogsOnRealDBError`, `TestIntegrationAllRoleCodesLogsOnRealDBError`, `TestIntegrationGetAppRolesSilentWhenNoRolesAssignedLogsOnRealDBError` — mỗi test có 1 nhánh xác nhận IM LẶNG ở trạng thái hợp lệ và 1 nhánh xác nhận CÓ LOG khi lỗi DB thật (mô phỏng bằng đóng kết nối trước khi gọi).

### 1.5. LOW/MEDIUM — `AssignRole`/`RemoveRole` ghi audit log ngay cả khi câu lệnh ghi là no-op

`internal/repository/role_repo.go:54-66`:
```go
func (r *RoleRepo) AssignRole(ctx context.Context, employeeID, roleID uuid.UUID) error {
	_, err := r.db.ExecContext(ctx, `
		INSERT INTO employee_roles (employee_id, role_id)
		VALUES ($1, $2)
		ON CONFLICT (employee_id, role_id) DO NOTHING`, employeeID, roleID)
	return err
}

func (r *RoleRepo) RemoveRole(ctx context.Context, employeeID, roleID uuid.UUID) error {
	_, err := r.db.ExecContext(ctx, `
		DELETE FROM employee_roles WHERE employee_id = $1 AND role_id = $2`, employeeID, roleID)
	return err
}
```
`AssignRole` dùng `ON CONFLICT ... DO NOTHING` — gán lại 1 role user đã có sẵn → 0 dòng ảnh hưởng, `err=nil`. `RemoveRole` xoá 1 cặp (employee, role) không tồn tại → cũng 0 dòng, `err=nil`. Cả 2 trường hợp, `RoleService` (mục 13 tài liệu trước) vẫn ghi 1 dòng audit `assign_role`/`remove_role` như thể vừa có thay đổi thật xảy ra. Điều này làm nhiễu chính công cụ mà dự án đang dựa vào cho JML/access-review (`GET /roles/access-review` đọc từ `audit_logs`) — log có thể cho thấy nhiều "hành động" hơn số thay đổi thật đã xảy ra, gây khó khi soát lại lịch sử cấp quyền.

**Cách sửa gợi ý:** kiểm `RowsAffected()` ở cả 2 hàm, chỉ ghi audit khi thực sự có thay đổi (hoặc đổi nhãn audit thành "no-op attempt" riêng nếu vẫn muốn giữ lại tín hiệu "ai đó cố gán/xoá gì").

### 1.6. LOW — Log không nhất quán: `fmt.Printf` thô lộ PII, không qua `slog`, không gate theo level — ✅ ĐÃ SỬA 2026-07-22

`internal/middleware/auth.go:198,217`:
```go
fmt.Printf("[AuthJWT] token invalid: %v\n", err)
...
fmt.Printf("[AuthJWT] token valid — oid=%s email=%s\n", userID, email)
```
Chạy vô điều kiện ở MỌI lần xác thực thành công (dòng 217 in cả `email` — PII — ra stdout mỗi request), không qua `slog`, không có `request_id`, không tôn trọng `LOG_LEVEL` (biến môi trường mới thêm ở mục 12 tài liệu trước để làm "công tắc" log — 2 dòng `Printf` này nằm ngoài công tắc đó hoàn toàn). Thuần nợ kỹ thuật/nhất quán, không đổi hành vi cho phép/từ chối — nhưng là kiểu không nhất quán một reviewer sẽ vướng ngay, và về lâu dài lộ PII (email) ra stdout không kiểm soát được mức độ.

**Đã triển khai 2026-07-22:** `token invalid` → `slog.Warn("AuthJWT token invalid", ...)` kèm `error`/`method`/`path`/`request_id` — hiện ở mức log mặc định (đúng bản chất "1 lần từ chối hợp lệ", giống `access_denied`). `token valid` → `slog.Debug("AuthJWT token valid", "oid", ..., "email", ..., "request_id", ...)` — mặc định KHÔNG hiện, chỉ hiện khi vận hành bật `LOG_LEVEL=debug`, đúng cùng mức với `logAuthzAllowed` đã có. Test mới: `TestIntegrationAuthJWTInvalidTokenLogsStructuredWarnLine` (xác nhận dòng Warn thật, hiện ở mức mặc định, không cần bật debug). Chưa viết test riêng cho dòng Debug `token valid` — nhánh JWT thật cần JWKS/RSA-signing giả lập, hiện chưa có hạ tầng test nào trong repo dựng luồng JWT thật (chỉ có dev-bypass được test); đây là log-level/format thuần, không đổi logic quyết định, nên chấp nhận rủi ro thấp không test riêng — có thể bổ sung sau nếu hạ tầng test JWT thật được dựng cho mục đích khác.

## 2. Đã kiểm và xác nhận KHÔNG có vấn đề (để tránh nghi ngờ thừa)

- **SQL injection:** toàn bộ `permission.go`/`scope.go`/`role_repo.go` dùng parameterized query (`$1`, `pq.Array`) nhất quán — không có string-concat SQL nào.
- **`UpdatePermissions` (role_repo.go:68-85):** bọc đúng 1 transaction (`BeginTxx`/`defer Rollback`) cho toàn bộ batch upsert ma trận quyền — an toàn, đã đúng từ trước.
- **Tính atomic giữa ghi `employee_roles` và ghi `audit_logs`:** xác nhận đây là 2 lời gọi độc lập, KHÔNG chung transaction — nhưng đây khớp đúng quyết định "audit-only, fire-and-forget" đã ghi nhận ở tài liệu trước (không phải phát hiện mới, chỉ xác nhận cơ chế thật khớp mô tả). Hậu quả nếu crash giữa 2 lời gọi chỉ là thiếu 1 dòng audit, không gây sai lệch dữ liệu quyền thật.
- **`ScopedExecutorFromContext`/`ResolveReadCompanyScope` (scope.go) fail-open về pool không giới hạn khi lỗi set `tx`/`set_config`:** có chủ đích, có comment, khớp thiết kế "defense in depth, không phải bộ lọc chính" — không tính là bug.

## 3. Ưu tiên xử lý đề xuất

| # | Finding | Mức | Vì sao ưu tiên |
|---|---|---|---|
| 1 | `RoleRepo.Update` no-op trên system role, audit log nói dối | HIGH | Tái hiện được ngay hôm nay, không cần điều kiện gì đặc biệt, và làm audit trail (thứ vừa được nối thật ở mục 13 tài liệu trước) tự mất tin cậy |
| 2 | Hierarchy + priority dùng chung 1 danh sách role | HIGH | Đang "ngủ" vì chưa ai set priority>0 kèm hierarchy sâu, nhưng khi priority có UI (đã có groundwork, chưa có UI theo tài liệu trước) đây sẽ là lỗi bảo mật thật — leo thang/mất quyền ngoài ý muốn admin |
| 3 | Cycle-safety CTE ngẫu nhiên, không tài liệu hoá | MEDIUM | Rủi ro treo hệ thống (DoS nội bộ) nếu ai đó "tối ưu" `UNION`→`UNION ALL` mà không biết lý do — rẻ để phòng ngừa (1 comment + 1 test) |
| 4 | Lỗi DB trên auth path bị nuốt, không log | MEDIUM | Trực tiếp làm khó chẩn đoán các sự cố "mất quyền không rõ lý do" — đúng loại sự cố dự án đã tốn thời gian điều tra trước đây |
| 5 | Assign/RemoveRole audit log dù no-op | LOW/MEDIUM | Làm nhiễu chính audit trail dùng cho JML/access-review |
| 6 | `fmt.Printf` PII, không qua slog | LOW | Thuần nợ kỹ thuật, rẻ để dọn cùng lúc sửa mục 4 (cùng file, cùng chủ đề logging) |

Chưa triển khai sửa nào trong tài liệu này — đây là báo cáo audit, đúng vai trò tương tự các tài liệu "reassessment" trước, chờ người dùng chọn mục nào làm trước.

## 4. Tham chiếu

- `RBAC-Architecture-Reassessment-200726.md` — phân tích kiến trúc/chính sách (khác tầng với tài liệu này).
- `RBAC-Tri-Party-Comparison-210726.md` — so sánh 3 nguồn ở tầng chính sách/quy trình; tài liệu này bổ sung tầng CODE mà cả 3 nguồn đó đều chưa chạm tới.
- `RBAC-Backlog-Tracklist-160726.md` — backlog canonical; nên gộp bảng ưu tiên ở mục 3 vào đây khi bắt đầu sửa.
