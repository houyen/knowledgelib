---
id: self-docs/security/rbac-priority-hierarchy-collision-fix
canonical_question: 'Technical guide and specification: RBAC-Priority-Hierarchy-Collision-Fix-220726'
aliases:
- RBAC-Priority-Hierarchy-Collision-Fix-220726
- RBAC Priority Hierarchy Collision Fix 220726
entity_type: troubleshooting
domain: self-docs > security
last_verified: 2026-07-22
---

# RBAC-Priority-Hierarchy-Collision-Fix-220726

**Ngày:** 2026-07-22
**Loại tài liệu:** phân tích sâu + phương án khắc phục chi tiết cho 1 finding cụ thể — mở rộng mục 1.2 của `self-docs/RBAC-Technical-Code-Audit-210726.md` (HIGH #2: role-hierarchy và priority-tier vô tình dùng chung 1 danh sách role).

**✅ ĐÃ TRIỂN KHAI Phương án A, 2026-07-22 — xem mục 6.**

## 1. Bối cảnh — vì sao bug này tồn tại

Hệ thống RBAC có 2 tính năng xây ở 2 thời điểm khác nhau, vô tình đọc chung một danh sách role trong request context (`UserRolesKey`), dù mục đích thiết kế khác nhau:

| Tính năng | Xây khi nào | Mục đích | Cách hoạt động |
|---|---|---|---|
| **Role hierarchy** (`roles.parent_role_id`) | 140726 | Role cấp dưới tự động kế thừa quyền của role tổ tiên mà không cần khai lại trong `permissions` | `expandRoleHierarchy` (`internal/middleware/auth.go:120-133`) cộng thêm mã của MỌI tổ tiên vào danh sách role user đang giữ |
| **Priority tier** (`roles.priority`) | 200726 | Khi user giữ nhiều role trực tiếp xung đột nhau (1 role deny, 1 role allow cho cùng module/action), role có priority cao hơn thắng | `resolveModuleActionPermission` (`internal/middleware/permission.go:118-126`) tính `maxPriority` trên đúng danh sách role đọc từ context, chỉ role ở tầng cao nhất được "bỏ phiếu" |

Luồng dữ liệu thật (đã đọc code, không suy luận):

```
AuthJWT
  └─ getAppRoles(db, email)                             // auth.go:88
       └─ codes := [role trực tiếp từ employee_roles]   // auth.go:103-109
       └─ expandRoleHierarchy(db, codes)                // auth.go:112
            └─ CỘNG THÊM mã mọi tổ tiên (parent_role_id) // auth.go:125-133
       └─ return DANH SÁCH ĐÃ TRỘN (trực tiếp + tổ tiên)
  └─ ctx = context.WithValue(ctx, UserRolesKey, roles)   // auth.go:166, 227 — CHỈ 1 danh sách, đã trộn

RequireRole                      ← đọc UserRolesKey, MEMBERSHIP CHECK (đúng — tổ tiên NÊN được coi là "có role")
EnforceSiteAdminDepartmentFilter ← đọc UserRolesKey, MEMBERSHIP CHECK (đúng — tương tự)
RequirePermission                ← đọc UserRolesKey, dùng cho CẢ 2 việc khác nhau:
    (a) tra dòng permission theo từng code         ← ĐÚNG, đây chính là cơ chế kế thừa 140726 phải làm
    (b) tính maxPriority theo rolePriority[code]   ← SAI, vì code ở đây có thể là TỔ TIÊN user
                                                       chưa từng được GÁN, nhưng cột roles.priority
                                                       của tổ tiên đó vẫn được tính vào cuộc
                                                       "tranh chấp ưu tiên"
```

Đã xác nhận qua `grep`: `RequireRole` (`auth.go:239`) và `EnforceSiteAdminDepartmentFilter` (`scope.go:345`) chỉ làm membership check (role tổ tiên NÊN tham gia — đúng thiết kế, KHÔNG cần sửa 2 chỗ này). Chỉ `resolveModuleActionPermission` là nơi duy nhất lấy `rolePriority[code]` của TỪNG code trong danh sách đã trộn để so sánh — đây là chỗ 2 tính năng "đấu" nhau.

## 2. Kịch bản lỗi cụ thể

- Nhân viên được **gán trực tiếp** role `X` (`priority = 0`, mặc định).
- `X.parent_role_id = Y` (role tổ tiên — nhân viên **chưa từng được gán** role này).
- Sau đó ai đó set `Y.priority = 10` bằng SQL tay (chưa có UI, nhưng cột đã ghi được) — với mục đích hoàn toàn khác: để `Y` thắng tranh chấp với 1 role KHÁC ở 1 nơi khác trong tổ chức.
- `expandRoleHierarchy(["X"])` → trả về `["X", "Y"]` — `Y` lọt vào context của nhân viên này chỉ vì tình cờ là tổ tiên của `X`, không phải vì admin chủ ý gán `Y` cho họ.
- `resolveModuleActionPermission` tính `maxPriority = max(rolePriority["X"]=0, rolePriority["Y"]=10) = 10` → chỉ code có priority=10 (`Y`) được xét ở vòng OR cuối; dòng permission tường minh mà admin đã cấu hình cho `X` (ví dụ `granted=false` — chủ ý cấm nhân viên này) **bị loại khỏi tầng thắng, không được xét tới**.
- Kết quả: quyết định cho phép/từ chối module đó phụ thuộc vào cấu hình của `Y` (role không ai gán cho nhân viên) thay vì cấu hình thật của `X` (role họ đang giữ) — leo thang hoặc mất quyền hoàn toàn ngoài chủ ý của người cấu hình `X`.

**Vì sao đang "ngủ":** mọi role hiện có `priority=0` mặc định, chưa có UI để set khác 0, và test `permission_priority_scope_integration_test.go` hiện tại chỉ test 2 role **cùng được gán trực tiếp** (không hierarchy) — không có test nào phối hợp cả 2 trục cùng lúc. Bug chỉ kích hoạt khi priority UI ra đời VÀ có ít nhất 1 cặp role hierarchy tồn tại đồng thời — cả 2 điều kiện đều đã có sẵn hạ tầng, chỉ chưa ai bật cùng lúc.

## 3. Ràng buộc phải giữ khi sửa (đã kiểm, không được phá)

1. `RequireRole`/`EnforceSiteAdminDepartmentFilter` PHẢI tiếp tục coi tổ tiên là "có role" — không đổi gì ở 2 nơi này.
2. Cơ chế kế thừa permission-row (140726: dòng cấu hình của tổ tiên áp dụng cho con cháu chưa có dòng riêng) PHẢI giữ nguyên — đây là tính năng, không phải bug.
3. Test `TestIntegrationPriorityAndCompanyScopeAreIndependentAxes` (2 role **trực tiếp** khác priority, không hierarchy) phải tiếp tục pass.
4. Test `TestIntegrationGetAppRolesInheritsParentRole` (hierarchy, không priority) phải tiếp tục pass.

## 4. Phương án khắc phục

Nguyên tắc sửa: **priority phải đại diện cho role user THỰC SỰ ĐƯỢC GÁN, không phải role suy ra qua hierarchy.** Việc kế thừa dòng permission của tổ tiên vẫn giữ, nhưng dòng đó phải được xét ở đúng tầng ưu tiên của role trực tiếp đang kế thừa nó — không phải ở tầng ưu tiên riêng của chính tổ tiên.

### Phương án A — tách riêng "role trực tiếp" khỏi "role đã mở rộng hierarchy" qua context key mới (khuyến nghị)

- Thêm 1 context key mới `UserDirectRolesKey` — set song song với `UserRolesKey` ngay trong `AuthJWT`, giá trị là `codes` (danh sách role gán trực tiếp, TRƯỚC khi gọi `expandRoleHierarchy`). Với nhánh super-admin, direct = expanded = toàn bộ role hệ thống (không đổi, vì super-admin đã bypass hoàn toàn).
- `getAppRoles` đổi chữ ký trả thêm `directRoles []string` (3 call site đã kiểm: dev-bypass `auth.go:163`, JWT thật `auth.go:220`, 1 test gọi trực tiếp `auth_integration_test.go:39`).
- `resolveModuleActionPermission` đổi chữ ký nhận `directRoles []string` thay cho `roles []string` hiện tại. Bên trong: với mỗi role trực tiếp, tự gọi `expandRoleHierarchy` cho riêng role đó để lấy đúng chuỗi tổ tiên của NÓ, gắn nhãn mọi code trong chuỗi đó (kể cả chính role trực tiếp) bằng priority của role trực tiếp — không phải priority riêng của tổ tiên. `maxPriority` chỉ tính trên priority của các role TRỰC TIẾP. Tầng thắng gồm: role trực tiếp ở tầng đó + tổ tiên của riêng nó (giữ đúng cơ chế kế thừa 140726). Nếu 1 tổ tiên được kế thừa qua nhiều role trực tiếp khác priority (hiếm, chưa gặp trong dữ liệu thật), lấy MAX priority trong số các role trực tiếp "bảo trợ" nó.
- `RequirePermission` (`permission.go:34`) đọc `UserDirectRolesKey` thay cho `UserRolesKey` khi gọi `resolveModuleActionPermission`.

**Cái giá phải trả (đã kiểm thật):** `internal/middleware/permission_integration_test.go` có ~6 nơi tự tay set `UserRolesKey` vào context để giả lập request (không đi qua `AuthJWT`) — nếu đổi `RequirePermission` sang đọc key mới, phải sửa cả 6 nơi đó thêm 1 dòng set `UserDirectRolesKey` (dùng đúng cùng danh sách, vì trong các test đó role đang test đều là role trực tiếp, không có hierarchy). Đây là sửa cơ học, an toàn, nhưng là diff thật cần review, không chỉ sửa 2 file production (`auth.go`, `permission.go`).

### Phương án B — không thêm context key, tự truy vấn lại trong `resolveModuleActionPermission`

- Giữ `UserRolesKey`/`RequirePermission` gọi hàm với đúng 1 tham số như hiện tại — không đổi `auth.go`, không đổi context key, không phải sửa test giả lập nào.
- Nhược điểm: hàm KHÔNG còn cách nào tự phân biệt "code nào trực tiếp, code nào tổ tiên" nếu chỉ nhận 1 danh sách đã trộn sẵn — phải truy vấn lại `employee_roles` (cần thêm `email`/`employeeID` làm tham số) để tự xác định lại tập trực tiếp, tức là **query trùng lặp với việc `getAppRoles` đã làm** — đúng kiểu vấn đề mà `RBAC-Architecture-Reassessment-200726.md` mục 1 đã nêu (nhiều nơi tự query rời rạc, không nơi nào là 1 nguồn sự thật). Không khuyến nghị, chỉ nêu để so sánh.

### So sánh nhanh

| | Phương án A | Phương án B |
|---|---|---|
| Đúng kiến trúc (tránh query trùng) | Có | Không |
| Số file production phải sửa | `auth.go`, `permission.go` | chỉ `permission.go` (nhưng thêm tham số email/employeeID mới) |
| Test phải sửa theo | ~6 chỗ trong `permission_integration_test.go` (thêm 1 dòng/chỗ) | Không cần sửa test cũ |
| Rủi ro | Thấp — chỉ mở rộng chữ ký, logic cũ (`RequireRole`, `EnforceSiteAdminDepartmentFilter`, kế thừa permission-row) giữ nguyên 100% | Trung bình — thêm query mới vào đường auth core, nguy cơ lệch dữ liệu với `getAppRoles` nếu 2 nơi tính hierarchy khác cách |

**Khuyến nghị: Phương án A.** Rẻ hơn về rủi ro kiến trúc, dù test phải sửa nhiều điểm hơn — nhưng đó là sửa cơ học, không phải logic.

## 5. Kế hoạch test cần thêm (bất kể chọn phương án nào)

Chưa có test nào phối hợp cả 2 trục — cần thêm tối thiểu 2 test tích hợp mới:

1. Role trực tiếp `X` (priority 0, deny tường minh cho module/action) có tổ tiên `Y` (priority CAO, không có dòng permission nào) → kỳ vọng **DENY thắng** (đúng cấu hình của `X`, `Y` không được phép ghi đè dù priority cao hơn).
2. Role trực tiếp `X` (priority 0, KHÔNG có dòng permission nào) có tổ tiên `Y` (priority bất kỳ, có dòng deny tường minh) → kỳ vọng **kế thừa dòng deny của `Y` vẫn hoạt động đúng** (không phá tính năng 140726).

## 6. Triển khai thật (2026-07-22)

Đã làm đúng Phương án A, cộng 1 phát hiện phụ trong lúc viết test khiến thiết kế phải chỉnh lại so với mục 4 (ghi lại đầy đủ để lần sau không lặp lại):

### Đã làm

- `internal/middleware/auth.go`: thêm `UserDirectRolesKey`; `getAppRoles` trả thêm `directRoles []string` (role gán trực tiếp, trước `expandRoleHierarchy`); cả 2 điểm gọi trong `AuthJWT` (dev-bypass, JWT thật) lưu `directRoles` vào context; thêm `GetUserDirectRoles(ctx)` song song `GetUserRoles`.
- `internal/middleware/permission.go`: `RequirePermission` đọc `UserDirectRolesKey` để gọi `resolveModuleActionPermission` (giữ `UserRolesKey` chỉ để log `expanded_roles` cho đầy đủ ngữ cảnh). `resolveModuleActionPermission` đổi chữ ký nhận `directRoles` — viết lại thuật toán, xem mục dưới.
- `internal/middleware/auth_integration_test.go`, `internal/middleware/permission_integration_test.go` (helper `requestWithRoles`): cập nhật theo chữ ký/context key mới.
- Test mới: `internal/middleware/permission_priority_hierarchy_integration_test.go` (2 test, xem mục 5).

### Phát hiện phụ khi viết test — thiết kế mục 4 (Phương án A) phải chỉnh lại

Bản thiết kế gốc ở mục 4 (gắn nhãn priority theo "sponsor" rồi vẫn OR flat qua mọi code trong `expandedAll`) **tự nó vẫn có lỗi**: viết test xong chạy đỏ, vì tổ tiên KHÔNG có dòng permission riêng vẫn được coi là 1 "người bỏ phiếu" độc lập trong vòng OR (mặc định opt-out ALLOW cho chính nó) — dòng deny tường minh của role trực tiếp vẫn bị vô hiệu, chỉ đổi từ "sai vì tầng priority" sang "sai vì tổ tiên đồng bỏ phiếu như role ngang hàng". Đây không phải lỗi hierarchy/priority nữa mà là nhầm lẫn giữa 2 khái niệm: "role trực tiếp SIBLING nhau thì OR" (200726, đúng) vs "tổ tiên chỉ là FALLBACK cho role trực tiếp đang kế thừa nó, không phải 1 voter độc lập" (140726, bị vi phạm).

**Sửa lại đúng như sau (đã code, đã test xanh):** với mỗi role trực tiếp ở tầng priority thắng — nếu nó có dòng permission riêng, dòng đó **tuyệt đối**, không tham khảo tổ tiên gì cả; chỉ khi nó KHÔNG có dòng riêng mới tham khảo tổ tiên của ĐÚNG NÓ làm fallback. OR chỉ áp dụng giữa các role TRỰC TIẾP trong tầng thắng (sibling), không áp dụng giữa 1 role trực tiếp và tổ tiên của chính nó.

### Bằng chứng

`go build`/`go vet` sạch. `go test ./internal/middleware/...`: 49 passed (0 fail, gồm 2 test mới). `go test ./...` trên `payroll_engine`: **703 passed, 9 failed** — đúng 9 fail baseline cũ (repository ×2, geo ×2, handler ×4, me ×1), không hồi quy. Không đổi bất kỳ HTTP status/route/contract nào — `RequireRole`, `EnforceSiteAdminDepartmentFilter`, mọi test cũ của `RequirePermission` (opt-out default-allow, OR sibling, priority thắng) đều xanh nguyên.

## 7. Tham chiếu

- `RBAC-Technical-Code-Audit-210726.md` mục 1.2 — finding gốc, đã trỏ ngược lại file này.
- `RBAC-Architecture-Reassessment-200726.md` mục 1 — vấn đề "4 cơ chế quyết định rời rạc" cùng họ nguyên nhân (nhiều nơi tự query/tự quyết không hợp nhất).
