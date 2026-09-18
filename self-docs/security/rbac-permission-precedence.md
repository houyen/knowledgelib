---
id: self-docs/security/rbac-permission-precedence
canonical_question: 'Technical guide and specification: RBAC-Permission-Precedence-220726'
aliases:
- RBAC-Permission-Precedence-220726
- '[DOCS]RBAC Permission Precedence 220726'
entity_type: how_to
domain: self-docs > security
last_verified: 2026-07-22
---

# RBAC-Permission-Precedence-220726

**Ngày:** 2026-07-22
**Loại tài liệu:** đặc tả tường minh (specification), không phải báo cáo công việc theo ngày. Mục đích: trả lời chính xác câu hỏi "khi 2 quy tắc mâu thuẫn nhau, ai thắng?" cho hệ thống authorization hiện có — điểm còn thiếu mà cả 2 second opinion độc lập (Gemini, GPT) cùng nêu ra ở `self-docs/RBAC-Tri-Party-Comparison-210726.md` mục 4 (backlog P3, "quy tắc precedence chưa được viết ra thành văn bản tường minh"), sau khi đã xảy ra một bug thật đúng loại này (OR-semantics, sửa ở 200726 — xem `RBAC-Improvement-Analysis-200726.md`). Tài liệu này mô tả code **hiện có**, không đề xuất thay đổi hành vi.

Đọc file này khi: (a) sửa `internal/middleware/permission.go`/`scope.go`/`auth.go`, (b) điều tra một ca "vì sao user X được/không được phép làm Y", (c) thêm một module/action mới vào `RequirePermission` và cần biết dữ liệu `permissions` sẽ tương tác thế nào với role-hierarchy/priority đã có.

## 0. Bốn cơ chế độc lập — nhắc lại từ `RBAC-Architecture-Reassessment-200726.md` mục 1

| # | Cơ chế | File | Input | Ghi chú |
|---|---|---|---|---|
| 1 | Role + role-hierarchy | `internal/middleware/auth.go` (`getAppRoles`, `expandRoleHierarchy`) | `employee_roles`, `roles.parent_role_id` | Chạy ĐÚNG 1 LẦN ở `AuthJWT`, kết quả cache trong request context (`UserRolesKey`) — mọi middleware sau đọc lại danh sách này, không tự truy vấn lại. |
| 2 | Permission opt-out + priority | `internal/middleware/permission.go` (`resolveModuleActionPermission`) | `permissions`, `roles.priority` | Tự truy vấn DB riêng mỗi lần `RequirePermission` chạy — KHÔNG dùng chung cache với cơ chế 1 ngoài việc đọc lại `UserRolesKey`. |
| 3 | Company/department scope | `internal/middleware/scope.go` (`ResolveCompanyScope`, `ResolveDepartmentScope`) | `employee_roles.scope_company_id`/`scope_department_id` | Đọc TRỰC TIẾP cột scope trên `employee_roles`, **không dùng danh sách role đã mở rộng hierarchy** — cố ý, vì role tổ tiên kế thừa qua hierarchy không mang theo thông tin phạm vi công ty của role gốc. |
| 4 | Super-admin bypass | `internal/middleware/auth.go` (`isSuperAdmin`, `allRoleCodes`) | `super_admins` | Chạy TRƯỚC cơ chế 1, thay thế hoàn toàn kết quả của nó (xem mục 4 dưới). |

Không có hàm nào gộp cả 4 cơ chế thành một "quyết định" duy nhất — mỗi route tự chọn (qua `router.go`) sẽ áp cơ chế nào bằng cách xếp chồng middleware (`r.With(a, b, c...)`). Mục 1-4 dưới đây mô tả precedence **bên trong từng cơ chế**; mục 5 mô tả precedence **giữa các cơ chế xếp chồng trên cùng 1 route**.

## 1. Super-admin bypass (cơ chế 4) — chạy trước tiên, thay thế cơ chế 1 hoàn toàn

`getAppRoles(db, email)` (`auth.go`):

```
nếu email có trong super_admins:
    trả về TOÀN BỘ role code trong bảng roles (allRoleCodes) — không mở rộng hierarchy
    (không cần, vì đã có mọi code rồi)
    superAdminBypass = true
ngược lại:
    trả về role trực tiếp gán qua employee_roles, MỞ RỘNG qua expandRoleHierarchy
    superAdminBypass = false
```

**Precedence:** nếu `isSuperAdmin() == true`, nhánh "role trực tiếp + hierarchy" **không bao giờ chạy** — hai nguồn role không cộng dồn với nhau, một trong hai được chọn tuyệt đối.

**Điều super-admin bypass KHÔNG làm:** không tự động cấp `unlimited=true` cho company/department scope (cơ chế 3). Một tài khoản super-admin muốn vượt ranh giới công ty vẫn cần một dòng `employee_roles` thật với `scope_company_code IS NULL`, y hệt người dùng thường — quyết định có chủ đích, xem `RBAC-Hybrid-Scoping-Implementation-140726.md` mục T3. Nói cách khác: **super-admin bypass chỉ có hiệu lực ở cơ chế 1 (và do đó gián tiếp ở cơ chế 2, vì cơ chế 2 dùng lại danh sách role của cơ chế 1) — KHÔNG lan sang cơ chế 3.**

## 2. Role-hierarchy (cơ chế 1) — precedence bên trong `expandRoleHierarchy`

Không có khái niệm "role cha thắng role con" hay ngược lại — `expandRoleHierarchy` chỉ **cộng dồn** (union), không có mâu thuẫn nào có thể xảy ra ở tầng này: role con luôn có đủ role code của mọi tổ tiên nó, cộng thêm chính nó. `RequireRole(...)` sau đó chỉ là một phép kiểm tra membership (role cần có ∩ role đang giữ ≠ ∅) — không có precedence để nói, chỉ có OR phẳng: **có ít nhất 1 role khớp là đủ, role nào khớp trước trong 2 vòng lặp lồng nhau không quan trọng (không ưu tiên role nào hơn role nào).**

```go
// auth.go RequireRole — OR phẳng, dừng ở match đầu tiên tìm thấy (thứ tự duyệt
// không mang ý nghĩa ưu tiên, chỉ là tối ưu early-return)
for _, required := range roles {
    for _, has := range userRoles {
        if has == required { ALLOW }
    }
}
```

## 3. Permission opt-out + priority (cơ chế 2) — nơi có precedence THẬT SỰ phức tạp, đây là trọng tâm tài liệu

Đây là cơ chế duy nhất có khái niệm "role này thắng role kia" — mô tả chi tiết bằng pseudocode khớp `resolveModuleActionPermission` (`permission.go`):

```
input: roles[]  — TOÀN BỘ role user đang giữ (đã qua hierarchy/super-admin ở cơ chế 1)
       module, action

1. Tra permissions WHERE module=X AND action=Y AND role IN roles[]
   → nếu KHÔNG có dòng nào (0 dòng cho MỌI role đang giữ) → ALLOW ngay, dừng ở đây.
     (opt-out mặc định — chưa ai cấu hình gì cho module/action này cho bất kỳ role nào
     user đang giữ, xem mục 2 tài liệu gốc 200726 về rủi ro thế trận của lựa chọn này)

2. Nếu CÓ ít nhất 1 dòng cho ít nhất 1 role đang giữ:
   a. Tính maxPriority = giá trị priority CAO NHẤT trong số roles[] (tra roles.priority,
      mặc định 0 nếu role không có priority set riêng).
   b. CHỈ xét các role có priority == maxPriority — role priority THẤP HƠN bị loại
      hoàn toàn khỏi bước 3, KỂ CẢ KHI role đó có dòng permission tường minh
      granted=false. Dòng permission đó bị bỏ qua, không "bỏ phiếu" được nữa.
   c. Trong tập role priority cao nhất, MỖI role tự tính allow/deny RIÊNG:
      - có dòng permission tường minh cho module/action → dùng đúng giá trị đó
      - KHÔNG có dòng nào (dù CÓ role khác đang giữ có dòng) → role này tự mặc định
        ALLOW (opt-out tính TỪNG ROLE, không phải gộp chung toàn bộ tập role trước rồi
        mới xét mặc định 1 lần — đây chính là bug đã sửa ở 200726, xem bên dưới)
   d. OR toàn bộ kết quả bước c lại — CHỈ CẦN 1 role (dù granted=true tường minh, hay
      mặc định allow vì role đó chưa từng cấu hình) cho phép là ĐỦ → ALLOW.
      Không có role nào trong tầng cao nhất cho phép → DENY.
```

### 3.1. Bảng quyết định — user giữ 2 role, mọi tổ hợp có thể xảy ra

Giả định user giữ đúng 2 role A và B cho cùng module/action. `pri(A)`, `pri(B)` là `roles.priority` (mặc định 0 nếu chưa ai set).

| pri(A) so pri(B) | Dòng permission của A | Dòng permission của B | Kết quả | Vì sao |
|---|---|---|---|---|
| bằng nhau | không có dòng | không có dòng | **ALLOW** | Bước 1: 0 dòng cho MỌI role → opt-out ngay, không cần vào bước 2 |
| bằng nhau | không có dòng (mặc định allow) | `granted=false` | **ALLOW** | Cả A, B cùng tầng cao nhất → OR: A mặc định allow đã đủ, B deny không "kéo tụt" A |
| bằng nhau | `granted=true` | `granted=false` | **ALLOW** | OR: A=true đủ để allow, bất kể B nói gì |
| bằng nhau | `granted=false` | `granted=false` | **DENY** | Cả 2 role cùng tầng đều tường minh từ chối, không role nào allow |
| A > B | B có `granted=true`, A không có dòng nào | — | **ALLOW** | A ở tầng cao hơn → chỉ xét A; A không có dòng → mặc định allow. Dòng `granted=true` của B bị BỎ QUA hoàn toàn dù có vẻ "hào phóng hơn" |
| A > B | A có `granted=false` tường minh, B có `granted=true` | — | **DENY** | Chỉ xét A (tầng cao nhất) → A tường minh deny → DENY. B không được "cứu" dù cùng user đang giữ B |

**Bài học rút ra:** priority không phải "cộng thêm quyền" — nó là **cắt bớt tập role được xét**. Nâng priority cho 1 role không bao giờ làm user mất quyền do role khác gây ra (vì role priority thấp hơn bị loại khỏi phép OR hoàn toàn, không "bỏ phiếu deny" được nữa) — nhưng cũng có nghĩa role priority thấp hơn không còn "cứu" được user nếu role priority cao hơn tường minh deny.

### 3.2. Vì sao KHÔNG phải "gộp chung rồi mới xét mặc định" (bug 200726)

Thuật toán CŨ (trước 200726) gộp toàn bộ dòng permission của MỌI role user giữ vào 1 rổ, rồi hỏi "rổ rỗng hoàn toàn không?" — nếu rổ có bất kỳ dòng nào (kể cả của role không liên quan/yếu hơn), không còn coi là "chưa cấu hình" nữa, và logic OR chạy trên rổ đó. Hệ quả: user giữ `hr_admin` (0 dòng, lẽ ra mặc định allow) + `cb_staff` (có `granted=false`) → rổ = `[false]` → DENY, dù `hr_admin` "không hề bỏ phiếu gì". Thuật toán MỚI tính mặc định **cho từng role riêng biệt** (bước 2c ở trên) trước khi OR — nghĩa là role không có dòng cấu hình luôn tự coi mình allow, độc lập với việc role khác cùng tầng có dòng hay không.

## 4. Company/department scope (cơ chế 3) — OR theo assignment, không có priority

`ResolveCompanyScope`/`ResolveDepartmentScope` (`scope.go`) đọc trực tiếp `employee_roles.scope_company_id`/`scope_department_id` — **không tham chiếu `roles.priority`** (priority chỉ có ý nghĩa ở cơ chế 2). Precedence ở đây đơn giản hơn: OR phẳng theo từng dòng `employee_roles` khớp 1 trong các role yêu cầu:

```
unlimited = true nếu CÓ ÍT NHẤT 1 dòng employee_roles (khớp role yêu cầu) với CẢ
            scope_company_id VÀ scope_company_code đều NULL
allowed   = HỢP (union) company_code của mọi dòng còn lại (không unlimited)
```

Không có khái niệm "role nào thắng" — chỉ cần 1 trong các dòng gán role của user là "không giới hạn" thì toàn bộ kết quả là `unlimited=true`, bất kể các dòng khác giới hạn thế nào. Đây là OR đơn giản (không có tầng ưu tiên như cơ chế 2) — **cố ý khác** với cơ chế 2, vì bài toán khác nhau: cơ chế 2 trả lời "được làm hành động X không", cơ chế 3 trả lời "được làm ở PHẠM VI nào" — phạm vi rộng nhất trong các phạm vi user có luôn thắng, không có "phạm vi tường minh hẹp hơn phủ quyết phạm vi rộng của role khác".

## 5. Precedence GIỮA các cơ chế xếp chồng trên cùng 1 route — AND tuyệt đối, không merge

Một route thường xếp chồng NHIỀU middleware từ NHIỀU cơ chế khác nhau qua `r.With(a, b, c, ...)` (`router.go`). Ví dụ `POST /Core System/calculate/{periodId}`:

```go
r.With(requirePayrollCalculate, requireUnrestrictedCalculate, requireEdit).Post(...)
// requirePayrollCalculate      = RequireRole("hr_admin", "cb_staff")        — cơ chế 1
// requireUnrestrictedCalculate = RequireUnrestrictedScope(db, "hr_admin")   — cơ chế 3
// requireEdit                  = RequirePermission(db, "Core System", "edit")  — cơ chế 2
```

`chi.Router.With` bọc các middleware theo đúng thứ tự liệt kê — request đi qua `a` trước, chỉ tới `b` nếu `a` gọi `next.ServeHTTP`, tới `c` nếu `b` cũng gọi tiếp. **Đây là AND tuyệt đối giữa các cơ chế: CẢ BA phải cùng cho phép, không có khái niệm "cơ chế nào quan trọng hơn" hay "2/3 đồng ý là đủ".** Bất kỳ middleware nào trả 403 sẽ dừng chuỗi ngay tại đó — các middleware phía sau (kể cả khi bản thân chúng sẽ cho phép) không bao giờ chạy tới. Thứ tự liệt kê trong `r.With(...)` chỉ ảnh hưởng middleware nào chạy trước/dừng sớm hơn (tối ưu chi phí — đặt cơ chế rẻ/hay-chặn trước), **không ảnh hưởng kết quả cuối cùng** (AND có tính giao hoán).

Nói cách khác: 4 cơ chế ở mục 0 **không tranh chấp/ghi đè lẫn nhau bao giờ** — chúng chỉ có thể tranh chấp **BÊN TRONG cùng một cơ chế** (mục 1-4 ở trên), còn **GIỮA các cơ chế thì luôn là AND, không có precedence liên-cơ-chế nào để nói.**

## 6. Quy trình gỡ lỗi "vì sao request này bị/được phép" — dùng khi debug

Vì không có một điểm tổng hợp quyết định (xem `RBAC-Architecture-Reassessment-200726.md` mục 1, Ưu tiên #1 — vẫn đang hoãn hợp nhất lớn), tra theo thứ tự sau khi có một ca cụ thể:

1. Xem log `access_denied`/`access_allowed` (persist vào `audit_logs` từ 220726, xem `RBAC-Tri-Party-Comparison-210726.md` mục 5 P1#1) — field `check` cho biết ĐÚNG cơ chế nào (`RequireRole`/`RequirePermission`/`RequireUnrestrictedScope`/`RequireCompanyScopeMatch`/`EnforceSiteAdminDepartmentFilter`) đã quyết định, field `request_id` nối các dòng log cùng 1 request lại với nhau.
2. Nếu là `RequireRole` — tra `employee_roles` + `roles.parent_role_id` (mục 2), kiểm tra `super_admins` trước (mục 1).
3. Nếu là `RequirePermission` — tra `permissions` cho MỌI role user giữ (không chỉ role "chính") + `roles.priority` của từng role đó (mục 3, dùng bảng quyết định 3.1).
4. Nếu là `RequireCompanyScopeMatch`/`RequireUnrestrictedScope` — tra `employee_roles.scope_company_id`/`scope_company_code` cho MỌI role liên quan (mục 4).
5. Route đó xếp chồng bao nhiêu middleware (`router.go`) — nếu deny đến từ middleware KHÔNG PHẢI middleware cuối cùng liệt kê, các middleware sau nó chưa từng chạy tới (mục 5) — đừng debug nhầm sang cơ chế chưa từng được đánh giá.

## 7. Tham chiếu

- `RBAC-Architecture-Reassessment-200726.md` — mục 1 (4 cơ chế rời rạc), mục 2 (opt-out là quyết định thế trận), mục 3 (coverage lớp mịn).
- `RBAC-Tri-Party-Comparison-210726.md` — mục 4 điểm 1 (nguồn gốc yêu cầu viết tài liệu này, đề xuất từ GPT).
- `RBAC-Improvement-Analysis-200726.md` — bug OR-semantics gốc và cách sửa (Hướng A + Hướng C), dẫn tới thuật toán mô tả ở mục 3 tài liệu này.
- `internal/middleware/permission.go`, `internal/middleware/scope.go`, `internal/middleware/auth.go` — code nguồn, đối chiếu lại nếu tài liệu này lệch pha sau khi code thay đổi.
