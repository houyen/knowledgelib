---
id: self-docs/security/rbac-architecture-reassessment
canonical_question: Architecture and technical specifications for RBAC-Architecture-Reassessment-200726
aliases:
- RBAC-Architecture-Reassessment-200726
- RBAC Architecture Reassessment 200726
entity_type: architecture_explainer
domain: self-docs > security
last_verified: 2026-07-20
---

# RBAC-Architecture-Reassessment-200726

**Ngày:** 2026-07-20
**Loại tài liệu:** context / nghiên cứu (study) — không phải báo cáo công việc đã hoàn tất theo ngày, mà là tài liệu tham khảo được cập nhật liên tục mỗi khi có phân tích mới về cùng chủ đề kiến trúc phân quyền.

**Vai trò tài liệu:** đánh giá tổng quan lại toàn bộ hệ thống permission/role, chủ động đứng ở một góc nhìn KHÁC với cách làm suốt các phiên trước (sửa từng lỗi cụ thể khi nó xuất hiện — 150726, 160726, 200726 đều là mô hình "phát hiện sự cố → phân tích → sửa điểm đó"). Tài liệu này không đề xuất sửa gì ngay — mục đích là lùi lại một bước, nhìn tổng thể kiến trúc đã hình thành sau nhiều lần vá liên tiếp, và chỉ ra những rủi ro mang tính CẤU TRÚC mà cách làm "vá từng điểm" không thể tự lộ ra được, vì mỗi lần vá chỉ nhìn đúng phạm vi sự cố đang xử lý.

## 0. Vì sao cần một góc nhìn khác

Nhìn lại lịch sử: 140726 xây company/department scoping, 150726 xây audit log + fine-grained permission + RLS, 160726 xử lý rủi ro Workday (chuyển key sang `hris_id`/FK), 200726 sửa bug OR-semantics + thêm priority tier. Mỗi lần đều là phản ứng đúng đắn với một triệu chứng cụ thể, và mỗi lần đều làm đúng phần việc được giao. Nhưng nhìn tổng thể, hệ thống authorization hiện tại không phải một thiết kế thống nhất — nó là **4 cơ chế quyết định độc lập, chưa từng được thiết kế cùng nhau, mỗi cơ chế được truy vấn riêng trên cùng một request**: (1) role + role-hierarchy (`roles.parent_role_id`), (2) permission opt-out + priority-tier (`permissions` + `roles.priority`), (3) company/department scope (thuộc tính trên từng dòng `employee_roles`, kiểu ABAC), (4) danh sách bypass theo identity (`super_admins`). Không có bất kỳ hàm/struct nào tổng hợp cả 4 cơ chế thành MỘT quyết định có lý do đầy đủ — mỗi middleware tự gọi DB, tự quyết, tự ghi log riêng (nếu có).

Đây chính là điều cách làm "vá từng điểm" không thể tự lộ ra: từng lần vá đều đúng trong phạm vi của nó, nhưng không ai từng đặt câu hỏi "bốn cơ chế này có nên là một hay không, và việc chúng tách rời có gây rủi ro gì mà từng lần vá riêng lẻ không thấy được".

## 1. Không có một "authorization decision" thống nhất — rủi ro cấu trúc lớn nhất

Với một request bất kỳ đi qua `/api/v1`, tối thiểu 3 lượt truy vấn DB độc lập chỉ để dựng danh sách role của người gọi (`isSuperAdmin`, join `employee_roles`, và CTE đệ quy `expandRoleHierarchy` cho role-hierarchy — `internal/middleware/auth.go`), sau đó `RequirePermission` lại tự truy vấn `permissions` + `roles.priority` riêng (`internal/middleware/permission.go`), và các route có company/department-scope lại tự truy vấn `employee_roles` một lần NỮA theo một hướng khác (`internal/middleware/scope.go`, đọc trực tiếp cột scope, không dùng danh sách role đã resolve ở bước đầu — có chủ đích, xem mục 4). Bốn lượt đọc riêng biệt, bốn nguồn sự thật riêng biệt, không hàm nào biết về quyết định của hàm khác.

Hệ quả thực tế: khi một request bị từ chối, không có nơi nào trả lời được câu "vì sao" một cách đầy đủ — chỉ có 4 log dòng rời rạc (nếu middleware nào đó gọi `logAccessDenied`) không liên kết với nhau bằng một request-id hay một decision-trace chung. Khi debug một ca "user X không truy cập được Y", người xử lý phải tự lần qua 4 cơ chế bằng tay — đúng như những gì đã xảy ra ở NHIỀU sự cố trước đây trong chính dự án này (đổi role không thấy hiệu lực → hoá ra là bug OR-semantics; đổi role không ẩn ribbon → hoá ra là super-admin bypass). Cả hai sự cố đó tốn thời gian điều tra chính vì không có một nơi tổng hợp lý do quyết định — nếu có, câu trả lời đã hiện ra ngay ở bước đầu tiên thay vì phải đọc code dò từng tầng.

Về lâu dài, mỗi tính năng RBAC mới (ví dụ ABAC theo giờ/IP ở Phase 2 roadmap) sẽ có xu hướng trở thành CƠ CHẾ ĐỘC LẬP THỨ 5, vì đó là cách duy nhất khớp với hình dạng hiện tại của codebase. Không nhất thiết phải là OPA/Rego (đã cân nhắc và đúng là quá nặng cho quy mô hiện tại, theo `Structure-Security-001.md`) — nhưng một hàm/struct Go đơn giản kiểu `ResolveAuthorizationContext(db, email, request) → AuthDecision{Roles, EffectivePermissions, CompanyScope, DepartmentScope, IsSuperAdmin, Reasons[]}` gọi một lần đầu request, cache trong context, và mọi middleware phía sau chỉ ĐỌC từ struct đó — sẽ giảm số lượt truy vấn DB, và quan trọng hơn, tạo ra ĐÚNG MỘT chỗ để ghi log quyết định đầy đủ lý do.

### Từ khoá để tự đọc thêm

Policy Decision Point / Policy Enforcement Point (PDP/PEP) — thuật ngữ XACML, đúng khái niệm "tách nơi quyết định ra khỏi nơi thực thi", dùng để hiểu vì sao gộp thành 1 điểm quyết định là một pattern chuẩn.
Request-scoped authorization context / auth context object (Go middleware pattern)
Structured audit logging for authorization decisions (hoặc "authz decision trace / correlation id")
Google Zanzibar — hệ thống authorization hợp nhất quy mô lớn của Google, đọc để hiểu triết lý "một nguồn sự thật cho mọi quyết định" (không cần áp dụng nguyên bản, chỉ để hiểu hướng thiết kế).
NIST RBAC (ANSI INCITS 359) — mô hình RBAC phân cấp chính thức, liên quan trực tiếp vì roles.parent_role_id đã là một dạng hierarchy RBAC.

## 2. Mô hình mặc định-cho-phép (opt-out) — một lựa chọn thế trận bảo mật, không chỉ là chi tiết kỹ thuật

Toàn bộ các lần sửa `resolveModuleActionPermission` (150726, 200726) đều giữ nguyên tiền đề: KHÔNG có dòng permission nào → mặc định ALLOW. Lý do ban đầu (150726) là thực tế: 4/5 role có 0 dòng permission, nếu đổi sang mặc định DENY sẽ khoá cứng toàn bộ hệ thống ngay lập tức. Đó là một quyết định vận hành đúng đắn ở thời điểm đó — nhưng nó đã trở thành CHÍNH SÁCH VĨNH VIỄN chỉ vì chưa ai từng đặt lại câu hỏi.

Nhìn từ góc độ nguyên tắc "least privilege" (đặc biệt quan trọng với một hệ thống lương — dữ liệu lương/PII là loại dữ liệu nhạy cảm cao), mặc định-cho-phép là ngược hướng với thông lệ bảo mật chuẩn (fail-safe = mặc định từ chối, chỉ mở khi được cấu hình tường minh). Hệ quả cụ thể của việc giữ mặc định-cho-phép: **mọi module/action MỚI được thêm vào hệ thống trong tương lai sẽ tự động ĐƯỢC PHÉP cho MỌI role**, cho tới khi có ai đó nhớ ra phải vào "Ma trận theo Role" tắt nó đi. Đây là một dạng "quyền mở rộng ngầm" (silent privilege creep) — không ai chủ động cấp quyền đó, nó chỉ đơn giản là hệ quả của việc không cấu hình. Bằng chứng cho việc này đã thực sự xảy ra trong chính dự án: mục coverage ở phần 3 dưới đây cho thấy phần lớn module (Config/*, Employees, Departments, Companies, HRIS, Attendance...) chưa từng có một dòng permission nào, tức đang mặc định mở cho MỌI role đang giữ được (qua `RequireRole`) — kể cả những role lẽ ra chỉ nên có quyền hạn chế.

Đây không phải đề xuất "đổi ngay sang mặc định deny" — việc đó cần một lộ trình migrate dữ liệu (chạy shadow-mode, xem trước khi khoá thật, đúng như hướng ABAC B đã bàn ở 150726) và một quyết định nghiệp vụ rõ ràng của người dùng. Điểm cần nêu ra ở đây là: đây là một QUYẾT ĐỊNH THẾ TRẬN BẢO MẬT đang được mặc nhiên giữ nguyên qua nhiều lần vá, chưa từng được đặt lại thành một câu hỏi tường minh cho người có quyền quyết.

## 3. Lớp "phân quyền mịn" chỉ che được một phần rất nhỏ hệ thống — công sức đã dồn vào đúng phần nhỏ đó

`RequirePermission` (lớp mịn, có opt-out + priority-tier) chỉ được gắn vào **5 điểm route** trong toàn bộ `router.go`: `Reports/export`, `PayrollPeriods/view`, `PayrollPeriods/edit`, `Core System/view`, `Core System/edit`. Toàn bộ phần còn lại — Employees, Departments, Companies, Config/* (khoảng 30 route: ot-multipliers, insurance, transport-allowances, leave-types, public-holidays, period-config, system, salary-components, pit-brackets...), Roles/*, Attendance*, Timesheets, AllowanceOverrides, HRIS Connector, Sync, Pipeline — chỉ có lớp thô `RequireRole`, không có bất kỳ kiểm soát View/Edit/Export riêng biệt nào, dù yêu cầu nghiệp vụ gốc (150726, yêu cầu 1) là "phân quyền chi tiết theo action" cho toàn hệ thống, không riêng 3 module.

Điều đáng chú ý ở góc nhìn này: toàn bộ công sức của phiên hôm nay (viết test priority+scope, sửa thuật toán OR, thêm cột priority) đều dồn vào làm cho ĐÚNG cái cơ chế chỉ đang che được 5/~137+ điểm route. Đây không phải sai — thuật toán sai thì phải sửa trước khi mở rộng phạm vi — nhưng nhìn từ góc độ ưu tiên tổng thể, việc "mở rộng `RequirePermission` ra thêm các module còn thiếu" (đã từng được nêu là B2 trong backlog 160726, rồi bị deferred vì quy mô lớn hơn B1) vẫn đang là món nợ lớn nhất về DIỆN TÍCH bao phủ, còn công việc hôm nay chỉ giải quyết được ĐỘ CHÍNH XÁC của phần diện tích nhỏ đã có.

Nghiêm trọng hơn: ba nhóm route hoàn toàn KHÔNG có `RequireRole` — `RegisterESSRoutes` (tự nhân viên xem hồ sơ/phiếu lương/chấm công của mình), `RegisterReadOnlyAPIRoutes` (ref/geo/me/lookup), `RegisterDashboardRoutes` — dựa hoàn toàn vào việc mỗi handler tự lọc theo email trong context (ví dụ `internal/handler/ess_handler.go`). Đây đúng là mô hình đã từng gây ra 2 lỗ hổng thật ở G1 (150726: Employee bank-accounts, HRIS connectors thiếu role gate) — "tự lọc trong từng handler" là một pattern DỄ QUÊN, vì không có gì ở tầng router bắt lỗi nếu một handler mới quên tự lọc. `RegisterESSRoutes`/`RegisterReadOnlyAPIRoutes` chưa bị phát hiện có handler nào quên lọc, nhưng đây chính xác là DẠNG rủi ro mà G1 (`chi.Walk()` test-guard) được viết ra để bắt — và test đó chỉ bắt được "thiếu RequireRole ở tầng route", không bắt được "handler tự lọc nhưng lọc sai/thiếu điều kiện" bên trong 3 nhóm route này.

### Từ khoá để tự đọc thêm

Principle of complete mediation — nguyên tắc bảo mật "mọi truy cập phải được kiểm tra, không có đường tắt" — đúng tên gọi cho lỗ hổng nhóm ESS/read-only/dashboard.
Declarative route authorization / API endpoint permission manifest
Defense in depth (authorization layers) — khái niệm cho việc có nhiều lớp gate (role + permission + scope) chồng lên nhau có chủ đích.
Fail-safe defaults (nguyên tắc Saltzer & Schroeder) — liên quan cả ưu tiên #2 (mặc định-cho-phép) lẫn #3 (route không gate).
chi router middleware testing golang — để tự tìm cách viết/mở rộng kiểu test chi.Walk() đã dùng ở G1.

## 4. Không ai kiểm tra ai — bề mặt cấu hình RBAC chính nó không có kiểm soát nội bộ

Đây là phát hiện đáng chú ý nhất của lần rà soát này, vì nó chưa từng được đặt ra ở bất kỳ phiên trước: `AssignRole`/`RemoveRole`/`UpdatePermissions` (`internal/handler/role_handler.go`) — tức chính các API dùng để CẤU HÌNH quyền — không có bất kỳ kiểm tra nào so sánh người đang thực hiện hành động với đối tượng bị tác động. Một `hr_admin` hoặc `config_admin` có thể:
- Tự gán thêm bất kỳ role nào (kể cả role mạnh hơn) cho chính tài khoản của mình.
- Tự sửa ma trận quyền của role mà chính mình đang giữ, mở rộng quyền cho bản thân.
- Không có bước phê duyệt thứ hai (maker-checker) cho bất kỳ thay đổi nào ở bề mặt này.

`AccessReview` (`GET /roles/access-review`) là công cụ DUY NHẤT liên quan, nhưng đây là kiểm soát PHÁT HIỆN SAU (detective), không phải NGĂN CHẶN TRƯỚC (preventive) — nó được thiết kế để một `hr_admin` cấp cao xem lại định kỳ (theo comment trong code là hàng quý), không chặn gì tại thời điểm ghi. Nói cách khác: hệ thống có "ai xem lại", nhưng không có "ai duyệt trước" cho chính bề mặt cấu hình quyền hạn.

Đây là một khoảng trống SoD (separation of duties) khác — và nghiêm trọng hơn — G7 (SoD trong quy trình duyệt lương, đã có trong backlog 160726, dạng shadow-mode) mà dự án đã biết và đang chờ triển khai: G7 là SoD cho NGHIỆP VỤ (ai duyệt lương của ai), còn phát hiện này là SoD cho CHÍNH VIỆC CẤU HÌNH RBAC (ai được sửa quyền của ai) — "ai gác cổng cho người gác cổng". Chưa từng được liệt kê thành một mục riêng trong bất kỳ backlog trước đó.

## 5. Audit trail cho thay đổi cấu hình RBAC không tồn tại — và có dấu hiệu "tưởng đã có" (dead code)

`RoleService` (`internal/service/role_service.go`) có một field `audit *AuditLogService` — khai báo sẵn, không được dùng ở bất kỳ method nào (`Create`, `Update`, `UpdatePermissions` đều không gọi `s.audit`). Bảng `audit_logs` (khác `attendance_audit_logs`) đã tồn tại thật trong schema, có repo `Create`/`CreateTx` hoàn chỉnh — nhưng chỉ được dùng cho audit chỉnh sửa DỮ LIỆU LƯƠNG (override, cell edit), không có lời gọi nào liên quan tới role/permission.

Điểm đáng lưu ý ở góc nhìn này: đây không đơn thuần là "chưa làm" — mà là "đã dựng một phần hạ tầng (field `audit`, bảng `audit_logs`, repo) rồi KHÔNG kết nối", một dạng nợ kỹ thuật dễ gây hiểu lầm — một người đọc code thấy field `audit` trên `RoleService` có thể lầm tưởng rằng thay đổi role/quyền đã được ghi log, trong khi thực tế không có gì được ghi. Không có cách nào trả lời câu "ai vừa sửa ma trận quyền của role X, lúc nào, giá trị cũ là gì" — kể cả khi hậu quả nghiêm trọng (như bug 200726 — lưu ma trận `cb_staff` ghi nhầm hàng loạt deny) xảy ra, không có bản ghi nào để tra lại NGOÀI việc người dùng tự nhớ và tự báo cáo, đúng như đã xảy ra thật trong phiên làm việc này.

Đồng thời, audit log TỪ CHỐI quyền (150726, G2, `access_audit.go`) — thứ ĐÃ được xây và ĐÃ được coi là "đã đóng gói yêu cầu audit log" trong báo cáo 150726 — thực chất chỉ ghi ra `log/slog` (stdout mặc định), KHÔNG có bất kỳ persist nào vào DB hay file. Nếu không có log-shipper/log-aggregator nào scrape stdout của tiến trình backend (chưa xác nhận được có hay không trong hạ tầng vận hành thật), toàn bộ audit trail TỪ CHỐI quyền biến mất mỗi khi container/process restart. Yêu cầu nghiệp vụ gốc "audit log old→new + reason bắt buộc" (150726) chỉ thật sự được thoả cho phần DỮ LIỆU LƯƠNG (`audit_logs` table, có old/new value + reason) — phần RBAC/permission hoàn toàn chưa có gì tương đương.

## 6. Độ trễ đồng bộ frontend không phải là "trường hợp super-admin" — nó là hành vi mặc định cho MỌI người dùng

Sự cố "đổi role sang C&B nhưng ribbon không ẩn" (200726) được kết luận đúng là do tài khoản test là super-admin — nhưng việc điều tra sự cố đó vô tình lộ ra một sự thật rộng hơn, chưa từng được nêu thành vấn đề riêng: `Core System-frontend/lib/auth.tsx` chỉ gọi `/api/v1/me` (đồng bộ role) MỘT LẦN duy nhất, tại thời điểm `AuthProvider` mount — không có interval, không có lắng nghe `focus`/`visibilitychange`, timer refresh token silent (`scheduleRefresh`) cũng không gọi lại đồng bộ role.

Điều này có nghĩa: với BẤT KỲ người dùng nào — không riêng super-admin — nếu quyền của họ bị thu hẹp giữa lúc đang mở tab (ví dụ hr_admin vừa tắt một quyền của họ trong "Ma trận theo Role"), giao diện của người đó vẫn hiển thị y hệt như trước cho tới khi họ tự tải lại trang hoặc mở tab mới. Backend vẫn đúng — request kế tiếp tới API sẽ bị chặn đúng theo mục 1 (roles được resolve live) — nhưng người dùng sẽ thấy một trải nghiệm khó hiểu: menu vẫn còn đó, bấm vào thì nhận lỗi 403. Đây là một khoảng trống UX-bảo mật (không phải lỗ hổng bảo mật thật, vì backend vẫn chặn đúng) nhưng đáng được nhìn nhận như một RỦI RO NHẬN THỨC — người dùng có thể tưởng mình vẫn có quyền, thao tác nhiều lần, nhận nhiều lỗi, và có thể báo nhầm thành "hệ thống lỗi" thay vì hiểu đúng là quyền đã bị thu hẹp.

## 7. Kết luận — điều gì khác với cách nhìn "vá từng điểm" trước đây

Nếu tiếp tục cách làm cũ ("chờ sự cố tiếp theo xuất hiện rồi phân tích + sửa đúng điểm đó"), các mục 1 (thiếu decision hợp nhất), 4 (thiếu SoD cho bề mặt cấu hình RBAC), và 5 (audit trail nửa vời) sẽ tiếp tục KHÔNG được phát hiện — vì chúng không tự biểu hiện thành một "lỗi" cụ thể như OR-semantics hay ribbon không ẩn. Chúng là những khoảng trống mang tính CẤU TRÚC, chỉ hiện ra khi có ai chủ động hỏi "hệ thống này có coherent không" thay vì "tính năng này có đúng không".

Không có đề xuất sửa cụ thể nào trong tài liệu này — đây là một bản đánh giá, không phải một implementation plan. Việc có triển khai mục nào (và theo lộ trình/quy mô nào) là quyết định của người dùng, sau khi đã thấy toàn cảnh.

## 9. Bổ sung cùng ngày — độ phức tạp triển khai 2 phương án cho ưu tiên #1

Theo yêu cầu người dùng, phân tích độ phức tạp thật của 2 phương án đã đề xuất cho ưu tiên #1 (hợp nhất 4 cơ chế quyết định phân quyền), TRƯỚC KHI làm bất kỳ phương án nào — mục này thuần phân tích, chưa code.

### Phương án A — trace hợp nhất, chưa đổi kiến trúc

**Độ phức tạp: THẤP.** Chỉ thêm log có cấu trúc tại từng điểm quyết định đã có sẵn (`getAppRoles`/`isSuperAdmin` trong `auth.go`, `resolveModuleActionPermission` trong `permission.go`, `ResolveCompanyScope`/`ResolveDepartmentScope` trong `scope.go`) — không đổi kiểu dữ liệu, không đổi control-flow, không đổi hành vi cho phép/từ chối. Rủi ro gần như bằng 0 vì log là side-effect thuần, không ảnh hưởng giá trị trả về. Cần thêm: xác nhận `go-chi/chi` đã có middleware `RequestID` tích hợp sẵn (rất có thể có, vì đây là tính năng chuẩn của chi) để nối các dòng log rời rạc theo cùng một request — nếu chưa có, thêm cũng rẻ. Ước lượng: vài giờ tới 1 ngày làm việc, không cần test mới bắt buộc (có thể thêm 1 test smoke xác nhận log được ghi, không bắt buộc).

Nếu muốn đi xa hơn thành MỘT dòng log duy nhất/request (gộp qua context accumulator thay vì 4 dòng rời rạc) thì độ phức tạp lên mức TRUNG BÌNH: cần thêm 1 context key mới, một middleware "chốt" ở đầu chain để flush sau khi response ghi xong, và sửa từng điểm quyết định để ghi vào accumulator thay vì gọi thẳng `logAccessDenied`. Ước lượng: 2-3 ngày kể cả viết test tích hợp xác nhận trace gộp đúng qua nhiều middleware liên tiếp.

### Phương án B — resolve 1 lần, cache trong request context

**Cần đính chính một điểm quan trọng phát hiện khi phân tích kỹ hơn:** vai trò (role list) THỰC RA đã được cache trong context từ `AuthJWT` (`UserRolesKey`, `auth.go:209-213`) — cả `RequireRole` lẫn `RequirePermission` đều đọc lại từ context này (`permission.go`: `roles, _ := r.Context().Value(UserRolesKey).([]string)`), KHÔNG tự truy vấn DB lại. Nghĩa là phần "trùng lặp giữa các tầng middleware" nhỏ hơn nhiều so với mô tả ban đầu ở mục 1 — cái thật sự lặp lại là **3 query TUẦN TỰ NẰM BÊN TRONG một lần gọi `getAppRoles`** (isSuperAdmin, join `employee_roles`, CTE hierarchy `expandRoleHierarchy`), tức một vấn đề LATENCY của một hàm, không phải một vấn đề kiến trúc "4 tầng tự ý query riêng". Company/department-scope (`ResolveCompanyScope`/`ResolveDepartmentScope`) VẪN phải tự truy vấn riêng dù làm phương án B, vì nó phục vụ dữ liệu khác (cột scope) theo tham số `roles []string` khác nhau tuỳ route yêu cầu — không gộp được vào cùng 1 lần resolve đầu request.

**Độ phức tạp: TRUNG BÌNH đến CAO, và lợi ích thực tế nhỏ hơn ước lượng ban đầu.** Nếu vẫn làm: gộp 3 query bên trong `getAppRoles` thành 1 câu SQL (UNION hoặc CASE WHEN kiểm tra super-admin ngay trong câu JOIN chính) — đây là code lõi của TOÀN BỘ auth, mọi request đều đi qua, sai một chỗ ảnh hưởng ngay lập tức toàn hệ thống. Cần test kỹ: tái dùng test kiểu G1 (`chi.Walk()`) để đảm bảo không phá gate nào, cộng test riêng cho hàm gộp mới ở đủ 3 nhánh (super-admin, role thường, role có hierarchy nhiều tầng). Ước lượng: 2-4 ngày kể cả test.

**Đã triển khai Phương án A (bản tối thiểu) trong ngày — xem mục 12.**

**Khuyến nghị:** làm Phương án A (bản tối thiểu) trước — rẻ, đúng vào đúng nỗi đau đã xảy ra thật (khó chẩn đoán khi debug, không phải do truy vấn trùng lặp). Phương án B nên hoãn lại, không làm riêng lẻ ngay — vì lợi ích thực tế (giảm latency 1 hàm) không đủ lớn để một mình biện minh cho rủi ro đụng vào code lõi auth; nếu làm, nên gộp chung với một đợt refactor lớn hơn có nhiều lý do cùng lúc (ví dụ làm cùng lúc với việc mở rộng `RequirePermission` ở ưu tiên #3 bước 3, khi nào đó cả router.go đã được cấu trúc lại).

## 10. Bổ sung cùng ngày — triển khai ưu tiên #3, Bước 1 và Bước 2

Theo yêu cầu người dùng, đã triển khai (không chỉ lên kế hoạch) Bước 1 và Bước 2 đã đề xuất cho ưu tiên #3.

### Bước 1 — báo cáo coverage tự động (`internal/app/permission_gate_coverage_test.go`)

Mở rộng đúng cơ chế G1 (`chi.Walk()`) đã có — không tạo cơ chế mới. Test mới phân loại MỌI route đã đăng ký thành 3 nhóm bằng cách đọc tên hàm runtime của từng middleware qua `reflect`/`runtime.FuncForPC` (kỹ thuật giới hạn trong phạm vi test, không đụng code sản phẩm) để phân biệt `RequireRole` (thô) và `RequirePermission` (mịn) mà không cần đổi kiểu dữ liệu của 2 hàm đó. Kết quả chạy thật trên toàn bộ router:

- **Fine-gated (RequireRole + RequirePermission): 19/184 route (10%)** — đúng 19 route thuộc 3 module Reports/PayrollPeriods/Core System đã biết từ trước.
- **Role-gate only (chỉ RequireRole, chưa có RequirePermission): 149/184 route (81%)** — bao gồm toàn bộ Employees, Departments, Companies, Config/* (~30 route), Roles/*, Attendance*, Timesheets, AllowanceOverrides, HRIS Connector, Sync, Pipeline.
- **Allowlist tự-lọc trong handler (không có RequireRole ở tầng router): 16/184 route (9%)** — ESS, read-only (ref/geo/me/lookup), dashboard, pipeline health.
- **0 route "unknown"** — nghĩa là mọi route hiện tại đã được phân loại rõ; assert duy nhất của test là giữ nguyên bất biến này (0 unknown) — route MỚI trong tương lai rơi vào "unknown" sẽ tự làm test đỏ, buộc người viết phải chủ động phân loại nó thay vì để lọt.

Con số 10%/81%/9% giờ là một bằng chứng CHẠY ĐƯỢC mỗi lần `go test`, không còn là ước lượng thủ công từ lần rà soát trước.

### Bước 2 — xác nhận thật claim "tự-lọc theo email" của allowlist ESS, và một phát hiện mới

Viết test tích hợp thật trên Postgres (`internal/handler/ess_self_scope_integration_test.go`, dùng `payroll_engine`): seed 2 nhân viên thật, gọi `GET /ess/profile` với JWT dev resolve về email nhân viên A, xác nhận response CHỈ chứa dữ liệu A — kể cả khi request cố tình gắn `?employeeCode=B&email=B` vào query string. Cả 2 test con đều xanh — xác nhận đúng claim của allowlist cho `GetProfile`/`UpdateProfile`/`GetPayslip`.

**Phát hiện mới khi rà kỹ 7 route ESS thay vì tin theo đúng 1 dòng comment chung cho cả nhóm:** 3 route (`GET /ess/leave-details`, `GET /ess/timesheet-raw`, `GET /ess/attendance-calendar`) **KHÔNG hề tự lọc theo email JWT** như comment gốc của allowlist từng khẳng định cho toàn bộ nhóm ESS. Cả 3 đọc trực tiếp một cookie session HRIS do CLIENT tự gửi qua header `X-HRIS-Cookie` (`attendance-calendar` còn nhận thêm `filePath` từ query string, cũng do client tự gửi), không có bước nào đối chiếu cookie/filePath đó với danh tính JWT của người gọi (`internal/handler/ess_handler.go` — `GetLeaveDetails`, `GetTimesheetRaw`, `GetAttendanceCalendar`). Trong luồng hợp lệ hiện tại, hành vi vẫn đúng vì frontend luôn tự gắn đúng cookie theo phiên HRIS của chính người dùng và dùng `filePath` là hằng số cố định (`Core System-frontend/lib/api/ess.ts`) — nhưng bản thân BACKEND không hề enforce ranh giới này, chỉ đang dựa vào việc frontend luôn gửi đúng. Đây KHÔNG PHẢI một hồi quy mới (hành vi này đã như vậy từ trước, chưa từng bị phát hiện vì allowlist gốc mô tả gộp chung cả 7 route bằng 1 câu). Đã sửa comment của allowlist (`internal/app/router_role_gate_test.go`) để phản ánh đúng 3 nhóm hành vi thật thay vì 1 câu chung sai một phần, và trỏ rõ tới test mới. **Chưa sửa hành vi** — việc có nên ràng buộc cookie/filePath theo JWT của người gọi hay không là một quyết định thiết kế cần hỏi trước (ảnh hưởng tới luồng tích hợp HRIS ngoài đang chạy thật), không tự ý đổi.

Bằng chứng: `go build ./...`, `go vet ./...` sạch; `go test ./...` với `TEST_DATABASE_URL` trỏ `payroll_engine`: 648 passed, 9 failed — đúng 9 fail baseline cũ (không đổi so với lần chạy trước khi thêm 2 test mới này), không hồi quy.

## 12. Bổ sung cùng ngày — triển khai ưu tiên #1, Phương án A (bản tối thiểu)

Theo yêu cầu người dùng, đã triển khai thật (không chỉ phân tích) Phương án A cho ưu tiên #1.

### Những gì đã làm

- **`internal/middleware/access_audit.go`**: thêm `logAuthzAllowed(r, check, reason, extra...)` — đối xứng với `logAccessDenied` đã có, nhưng ghi ở mức **`slog.Debug`** (không phải Info/Warn) để KHÔNG đổi hành vi log mặc định hiện có — test cũ `TestRequireRoleAllowDoesNotLogDenial` (khẳng định "không log gì khi cho phép" ở mức mặc định) vẫn xanh nguyên vì handler mặc định lọc ở mức Info, tự động bỏ qua Debug. Cả `logAccessDenied` lẫn `logAuthzAllowed` giờ đều gắn thêm `request_id` (đọc qua `chimw.GetReqID`, dùng đúng middleware `RequestID` của `go-chi` đã được bật sẵn toàn cục ở `cmd/Core System/main.go` từ trước, không cần thêm middleware mới) — cho phép nối các dòng log rời rạc của 4 cơ chế về cùng một request khi debug.
- Thêm riêng `logSuperAdminBypass(r, email, roleCount)` ghi ở mức **Info** (không phải Debug) — đóng đúng khoảng trống nêu ở mục 5 ("không có bản ghi nào tied tới hành động super-admin"): sự kiện này hiếm (chỉ vài tài khoản), có ý nghĩa audit/governance thật, nên luôn hiện ra ở mức log mặc định thay vì ẩn sau cờ debug.
- **`internal/middleware/auth.go`**: `getAppRoles` đổi chữ ký trả thêm `superAdminBypass bool` (tránh phải query lại `isSuperAdmin` lần 2 chỉ để log) — gọi `logSuperAdminBypass` ở cả 2 nhánh của `AuthJWT` (dev-bypass và JWT thật) khi bypass kích hoạt. `RequireRole` ghi `logAuthzAllowed` ở nhánh cho phép.
- **`internal/middleware/permission.go`**: `RequirePermission` ghi `logAuthzAllowed` ở nhánh cho phép, phân biệt rõ lý do (mặc định opt-out vì chưa role nào cấu hình, hay có role tường minh grant=true).
- **`internal/middleware/scope.go`**: `RequireUnrestrictedScope` và `requireCompanyScopeMatchWithScope` ghi `logAuthzAllowed` ở các nhánh cho phép (unlimited scope, hoặc company khớp phạm vi).
- **`cmd/Core System/main.go`**: thêm `LOG_LEVEL` (env var, giá trị `debug`/`info`/`warn`/`error`, mặc định `info` — giữ nguyên hành vi hiện có khi chưa set) qua `slog.SetDefault` — đây là "công tắc" thật để vận hành bật/tắt toàn bộ trace quyết định phân quyền khi cần chẩn đoán, không cần build lại binary.

### Bằng chứng

- 2 test mới: `TestParseLogLevel` (`cmd/Core System/main_test.go`, xác nhận map giá trị env var → level đúng) và `TestRequireRoleAllowLogsDebugTraceWhenLogLevelDebugEnabled` (`internal/middleware/access_audit_test.go`, xác nhận log THẬT SỰ phát ra kèm `request_id` khi mức Debug được bật — đối xứng với test cũ chỉ xác nhận im lặng ở mức mặc định).
- `go build ./...`, `go vet ./...` sạch. `go test ./internal/middleware/...`: 44/44 passed (bao gồm mọi test cũ, không hồi quy — đặc biệt `TestRequireRoleAllowDoesNotLogDenial` và `TestRequireCompanyScopeMatchDenyLogsStructuredAuditLine` vẫn xanh nguyên). `go test ./...` toàn repo trên `payroll_engine`: 650 passed, 9 failed — đúng 9 fail baseline cũ (không đổi so với lần chạy trước khi thêm các thay đổi này), không hồi quy.

### Chưa làm (nằm ngoài phạm vi "bản tối thiểu")

Không gộp 4 dòng log rời rạc/request thành 1 dòng duy nhất qua context accumulator (bản "đi xa hơn" của Phương án A, mục 9 đã ước lượng 2-3 ngày) — bản tối thiểu này đã đủ để nối các dòng log qua `request_id` khi cần, không cần thêm độ phức tạp của accumulator ngay bây giờ. Có thể làm sau nếu 4 dòng rời rạc (dù đã nối được qua request_id) vẫn chưa đủ tiện khi debug thật.

## 13. Bổ sung 2026-07-21 — triển khai mục 4 (SoD bề mặt cấu hình RBAC), hướng audit-only

Người dùng chọn hướng "audit-only trước" (không chặn tự-phục-vụ ngay) sau khi được trình bày 3 phương án: audit-only / chặn cứng self-grant leo thang / cả hai. Dữ liệu thật kiểm tra trước khi hỏi cho thấy có **12 tài khoản `hr_admin`** (không phải trường hợp chỉ có 1 admin duy nhất) — nên rủi ro khoá nhầm của phương án "chặn cứng" thực ra thấp, nhưng người dùng vẫn chọn audit-only làm bước đầu, đúng tinh thần "đo trước khi khoá" đã dùng nhất quán trong toàn bộ RBAC work (shadow-mode, opt-out).

### Đã làm

- **Nối audit trail THẬT cho mọi thay đổi RBAC** — trước đây `RoleService.audit` là dead code (field khai báo, không method nào gọi). Giờ `Create`, `Update`, `UpdatePermissions`, `AssignRole` (mới), `RemoveRole` (mới) đều ghi 1 dòng vào `audit_logs` qua `AuditLogService` có sẵn — action/resource/resourceId/old→new value đầy đủ, theo đúng cấu trúc `models.AuditLog` đã có từ 150726.
- **`AssignRole`/`RemoveRole` chuyển từ SQL viết tay trong `role_handler.go` sang `RoleRepo`/`RoleService`** (`internal/repository/role_repo.go`, `internal/service/role_service.go`) — cùng một chỗ với mọi thao tác ghi khác của role, để bọc audit log quanh chúng nhất quán; câu SQL giữ nguyên, chỉ đổi chỗ nó nằm.
- **Cờ `selfReferential`** trong `NewValues` JSON của mỗi dòng audit — `AssignRole`/`RemoveRole` so khớp `actorEmail` (qua `EmployeeRepo.GetIDByEmail`) với nhân viên bị tác động; `UpdatePermissions` so khớp mã role đang giữ của actor (`actorRoleCodes`, đọc qua `middleware.GetUserRoles`) với role đang bị sửa. Không chặn gì — chỉ đánh dấu để một admin cấp cao lọc ra khi soát lại (bổ sung tự nhiên cho `AccessReview` đã có từ G4, 150726 — cùng triết lý "ưu tiên nêu ngoại lệ").
- **`UpdatePermissions` ghi cả `old` lẫn `new`** — bắt buộc phải là TOÀN BỘ ma trận trước đó (không phải diff), vì `UpdatePermissions` ghi đè toàn bộ mảng gửi lên (đúng như bug 200726 đã phân tích) — nên "cũ" phải phản ánh đúng trạng thái trước khi ghi đè để trả lời được "trước khi sửa, ma trận trông thế nào".
- **Actor identity truyền tường minh qua tham số** (`actorEmail string`, không phải service tự đọc `middleware.GetUserEmail` từ context) — khớp đúng quy ước đã có sẵn ở `PayrollPeriodService.Lock`/`SalaryComponentService`, giữ layering nhất quán (service không phụ thuộc `net/http`/context của tầng transport).

### Phát hiện phụ (không sửa, ghi lại)

`AuditLogRepo.List` (dùng bởi `GET /audit-logs/`) hiện KHÔNG select cột `details` (nơi chứa old/new JSON) — nghĩa là dữ liệu old/new đã ghi ĐÚNG vào DB (xác nhận bằng test tích hợp, xem dưới) nhưng API đọc audit log hiện tại chưa trả nó ra cho client. Đây là giới hạn tiền tồn tại của toàn bộ audit log (ảnh hưởng cả audit dữ liệu lương từ 150726, không riêng RBAC), ngoài phạm vi quyết định "audit-only" hôm nay — cần một quyết định riêng nếu muốn hiển thị old/new trên UI audit log.

### Bằng chứng

Test mới: `internal/service/role_service_audit_integration_test.go` (5 test con) — xác nhận `AssignRole`/`RemoveRole` ghi đúng dòng audit kèm `selfReferential` đúng cả 2 chiều (actor là chính mình / actor là người khác), và `UpdatePermissions` ghi đúng cả `old` lẫn `new`. `go build`/`go vet` sạch. `go test ./...` trên `payroll_engine`: **655 passed, 9 failed** — đúng 9 fail baseline cũ (không đổi so với lần chạy trước khi thêm các thay đổi này), không hồi quy.

## 14. Bổ sung 2026-07-21 — sửa `AuditLogRepo.List` + bắt đầu Ưu tiên #3 mục 3 (Employees)

### `AuditLogRepo.List` không trả `details` (old/new) — đã sửa

Phát hiện phụ ở mục 13 (`AuditLogRepo.List` không select cột `details`) đã sửa: `internal/repository/audit_log_repo.go` giờ select thêm `details`, tách JSON `{"old":...,"new":...}` thành `OldValues`/`NewValues` trên từng dòng trả về. Test mới: `internal/repository/audit_log_repo_integration_test.go`, xác nhận `List()` trả đúng giá trị `Create()` đã ghi (trước đây luôn rỗng dù DB có dữ liệu thật).

### Ưu tiên #3 mục 3 — bắt đầu Phương án A, module Employees

Đã chọn thứ tự triển khai (xem `self-docs/RBAC-Priority3-Module-Rollout-Tasklist-210726.md` — file task-list riêng, cập nhật liên tục, không lặp lại chi tiết ở đây): Employees → Roles/\* → Departments/Companies → Config/\* → Attendance/Timesheets/AllowanceOverrides → HRIS Connector/Sync/Pipeline.

Trước khi wire, phát hiện module "Employees" đã tồn tại sẵn trong danh sách `MODULES` của UI "Ma trận theo Role" (`Core System-frontend/lib/rbac-constants.ts`) — bảng `permissions` **đã có dữ liệu thật** (`cb_staff`: view/create/edit/export=true, delete/approve=false; `config_admin`: chỉ view=true) dù chưa từng có tác dụng vì backend chưa enforce. Xác nhận với người dùng: giữ nguyên dữ liệu, cho enforce ngay — `cb_staff` sẽ mất quyền xóa work-history/dependent/education/experience/language kể từ khi triển khai, đúng ý định đã cấu hình từ trước, không phải hồi quy ngoài ý muốn.

Đã wire `RequirePermission(db, "Employees", action)` vào toàn bộ 30 route của `RegisterEmployeeRoutes` (`internal/app/router.go`), ánh xạ GET→view, POST tạo mới→create, PUT/PATCH→edit, DELETE→delete. Test mới `internal/app/employee_routes_permission_integration_test.go` — dùng 1 role test riêng có priority CAO HƠN `cb_staff` (theo Hướng C) để cô lập kết quả khỏi dữ liệu `cb_staff` thật, xác nhận delete=false chặn đúng 403 trong khi view/create/edit=true không bị chặn.

Coverage report (`permission_gate_coverage_test.go`) tăng từ 19/184 (10%) lên **49/184 (27%)**.

Bằng chứng: `go build`/`go vet` sạch, `go test ./...` trên `payroll_engine`: **660 passed, 9 failed** — đúng 9 fail baseline cũ, không hồi quy.

## 15. Bổ sung 2026-07-21 — Ưu tiên #3 mục 3, module thứ 2: Roles/\*

Kiểm tra dữ liệu `permissions` cho module "Settings.Roles" trước khi wire (đúng quy trình đã rút ra từ Employees): `config_admin` có TẤT CẢ action = `true` (đã full quyền từ trước), `hr_admin` có 0 dòng (mặc định allow-all). `cb_staff`/`employee` có dữ liệu (toàn `false`) nhưng KHÔNG liên quan — cả hai không nằm trong `RequireRole("hr_admin","config_admin")` của nhóm route `/roles/*`, chưa từng qua được lớp thô để chạm lớp mịn. Kết luận: **wire module này không đổi hành vi thật nào ngay lập tức** cho bất kỳ role nào đang thực sự dùng được các route này — khác hẳn Employees (không cần hỏi lại người dùng vì không có rủi ro thay đổi hành vi).

Đã wire `RequirePermission(db, "Settings.Roles", action)` vào 9 route của `RegisterRoleRoutes` (`internal/app/router.go`): List/GetPermissions/ListEmployeeRoles/AccessReview → `view`; Create/AssignRole → `create` (AssignRole tạo 1 dòng gán quyền mới, không phải sửa); Update/UpdatePermissions → `edit`; RemoveRole → `delete`. Test mới `internal/app/roles_routes_permission_integration_test.go` — cùng kỹ thuật cô lập bằng role priority cao hơn `hr_admin` (vì `hr_admin` có 0 dòng, nếu không nâng priority thì OR-semantics sẽ luôn ALLOW bất kể role test nói gì).

Coverage report tăng từ 49/184 (27%) lên **58/184 (32%)**.

Bằng chứng: `go build`/`go vet` sạch, `go test ./...` trên `payroll_engine`: **665 passed, 9 failed** — đúng 9 fail baseline cũ, không hồi quy.

## 16. Bổ sung 2026-07-21 — Ưu tiên #3 mục 3, module thứ 3: Departments / Companies

**Departments** đã có dữ liệu `permissions` cấu hình sẵn (`cb_staff`, `config_admin`, `employee`) nhưng chỉ `hr_admin` nằm trong `RequireRole` của nhóm route này (`hr_admin`-only từ trước), và `hr_admin` có 0 dòng permission cho module này (mặc định allow-all) — wire không đổi hành vi thật nào, giống Roles/\*.

**Companies** CHƯA từng tồn tại trong danh sách `MODULES` của UI "Ma trận theo Role" (`Core System-frontend/lib/rbac-constants.ts`) — 0 dòng permission nào trong DB (không ai cấu hình được vì UI chưa có chỗ). Đã thêm `"Companies"` vào `MODULES`/`MODULE_LABELS` TRƯỚC khi wire backend (đúng lưu ý đã rút ra ở task-list — nếu không, backend enforce nhưng admin không có màn hình để bật/tắt).

Đã wire `RequirePermission(db, "Departments", action)` (4 route: List→view; Sync/UpdatePolicy/UploadOrgStructure→edit) và `RequirePermission(db, "Companies", action)` (5 route: List→view; Create→create; SyncFromHRIS/Update→edit; Delete→delete) — cả hai module vào `internal/app/router.go` (`RegisterDepartmentRoutes`/`RegisterCompanyRoutes`), truyền middleware xuống qua `internal/transport/http/department/routes.go`/`internal/transport/http/company/routes.go` (đổi chữ ký `RegisterRoutes` để nhận thêm các middleware mới — 1 test cũ `department_route_test.go` cần cập nhật theo, dùng `noopMiddleware` passthrough vì test đó chỉ quan tâm lớp `RequireRole`, không cần DB thật cho lớp mịn).

Test mới `internal/app/departments_companies_routes_permission_integration_test.go` — cùng kỹ thuật cô lập bằng role priority cao hơn `hr_admin`.

Coverage report tăng từ 58/184 (32%) lên **67/184 (36%)**.

Bằng chứng: `go build`/`go vet` sạch, `go test ./...` trên `payroll_engine`: **671 passed, 9 failed** — đúng 9 fail baseline cũ, không hồi quy.

## 17. Bổ sung 2026-07-21 — Ưu tiên #3 mục 3, module thứ 4 và 5: Config/\* và Attendance/Timesheets/AllowanceOverrides

Trước khi làm, đã phân tích rõ và xin xác nhận người dùng 3 điểm rẽ nhánh thiết kế (không tự quyết vì ảnh hưởng hành vi UI thật): (1) tách Config/\* thành 5 module con mới hay gộp 1 module chung — người dùng chọn **tách riêng**, nhất quán với cách Insurance/LeaveTypes/PublicHolidays đã tách trước đó; (2) AttendanceSummary/AttendanceComputed tách module riêng hay gộp vào AttendanceDaily — người dùng chọn **tách riêng**, khớp 2 nhóm route độc lập trong router.go; (3) route `/attendance/items`,`/attendance/records` (stub rỗng, tính năng đã gỡ theo comment code cũ) có wire không — người dùng chọn **bỏ qua, không wire**.

### Config/\* (module thứ 4)

Kiểm tra dữ liệu `permissions` trước khi wire: route `/config` chỉ `RequireRole("hr_admin")` (không cb_staff/config_admin), và `hr_admin` có **0 dòng** cấu hình cho MỌI module `Settings.*` hiện có (Insurance/LeaveTypes/PublicHolidays/System/Overtime) — mặc định allow-all, wire **không đổi hành vi thật nào**, giống Roles/\*/Departments/Companies (khác Employees).

Thêm 5 module mới vào `Core System-frontend/lib/rbac-constants.ts`: `Settings.SalaryComponents`, `Settings.PITBrackets`, `Settings.TransportAllowances`, `Settings.PeriodConfig`, `Settings.EmployeeLevels`. `ot-multipliers`/`overtime-types` dùng chung module `Settings.Overtime` có sẵn (không tạo module mới, vì cùng khái niệm nghiệp vụ "tăng ca").

Đã wire `RequirePermission(db, "Settings.<SubModule>", action)` cho toàn bộ ~14 sub-route trong `RegisterConfigRoutes` (`internal/app/router.go`), ánh xạ GET→view, POST tạo mới→create, PUT/PATCH→edit, DELETE→delete (kể cả `/salary-components/{id}/overrides` — dùng chung module `Settings.SalaryComponents`, không tách module riêng vì đây là sub-resource của cùng 1 khái niệm). Test mới `internal/app/config_routes_permission_integration_test.go` — spot-check 4/10 sub-module đại diện đủ dạng action (view/create/edit/delete), không test hết cả 10 vì cơ chế wire giống hệt nhau (đã chứng minh đủ ở test trước đó).

### Attendance/Timesheets/AllowanceOverrides (module thứ 5)

`AttendanceDaily`/`Timesheets` đã có dữ liệu `permissions` cấu hình sẵn cho `cb_staff` (AttendanceDaily: view/create/edit/export=true, delete/approve=false; Timesheets: view/create/edit/export=true, delete/approve=false) nhưng đối chiếu với action THẬT SỰ được route dùng: AttendanceDaily chỉ dùng view/edit/export (không có route map create/delete/approve) — cb_staff đã `true` cho cả 3; Timesheets chỉ dùng view/edit (List/GetByEmployee là view, Sync là edit) — cb_staff đã `true` cho cả 2. Kết luận: **wire không đổi hành vi thật nào**, giống Roles/\*/Departments/Companies. `config_admin`/`employee` có dữ liệu `false` nhưng không nằm trong `RequireRole` của 2 nhóm route này nên không liên quan.

`AttendanceSummary`, `AttendanceComputed` là module hoàn toàn mới (0 dòng permission, an toàn tuyệt đối) — tách riêng theo quyết định người dùng. `AllowanceOverrides` cũng module hoàn toàn mới. Cả 4 module mới (`AttendanceSummary`, `AttendanceComputed`, `AllowanceOverrides` — `Timesheets`/`AttendanceDaily` đã có sẵn từ trước) đã thêm vào `rbac-constants.ts`.

Đã wire `RequirePermission` vào `RegisterAttendanceDailyRoutes`, `RegisterAttendanceSummaryRoutes`, `RegisterAttendanceComputedRoutes`, `RegisterAllowanceOverrideRoutes` (`internal/app/router.go`) và `internal/transport/http/timesheet/routes.go` (đổi chữ ký `RegisterRoutes` để nhận thêm `requireView`/`requireEdit` — 1 test cũ `internal/handler/timesheet_route_test.go` cập nhật theo, dùng `noopMiddleware` passthrough giống mẫu `department_route_test.go`). Route `/attendance/items`,`/attendance/records` (`RegisterAttendanceRoutes`, stub rỗng) **giữ nguyên, không wire** theo quyết định người dùng — đã có `RequireRole` che, không phải lỗ hổng, wire thêm cho code chết là phí công.

Test mới `internal/app/attendance_timesheet_allowance_permission_integration_test.go` — cùng kỹ thuật cô lập bằng role priority cao hơn (gán cùng `hr_admin` để qua lớp thô, vì mọi route trong nhóm này đều có `hr_admin` trong `RequireRole`).

### Coverage & bằng chứng

Coverage report (`permission_gate_coverage_test.go`) tăng từ 67/184 (36%) lên **137/184 (74%)**, 0 route "unknown" (assert vẫn pass).

`go build`/`go vet` sạch, `go test ./...` trên `payroll_engine`: **689 passed, 9 failed** — đúng 9 fail baseline cũ (repository ×2, geo ×2, handler ×4, me ×1), không hồi quy.

Còn lại theo task-list (`RBAC-Priority3-Module-Rollout-Tasklist-210726.md`): module thứ 6 — HRIS Connector/Sync/Pipeline (chưa làm, cần bổ sung tên module trước).

## 11. Tham chiếu

- Nền tảng đã xây: `RBAC-Hybrid-Scoping-Implementation-140726.md`, `RBAC-Improvement-Analysis-150726.md`, `RBAC-Improvement-Analysis-160726.md`, `RBAC-Improvement-Analysis-200726.md`, `RBAC-Phase1A-Test-Plan-200726.md`.
- Backlog liên quan (đã biết từ trước, không phải phát hiện mới của tài liệu này): `RBAC-Backlog-Tracklist-160726.md` (G7 — SoD nghiệp vụ Core System, khác với mục 4 ở đây — SoD cho bề mặt cấu hình RBAC).
- Roadmap gốc (Phase 2, chưa triển khai, có bàn tới OPA/Rego cho policy engine hợp nhất — liên quan trực tiếp tới mục 1): `Core System-Architecture-Roadmap.md`, `Structure-Security-001.md`.
