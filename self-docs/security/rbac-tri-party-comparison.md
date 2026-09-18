---
id: self-docs/security/rbac-tri-party-comparison
canonical_question: 'Technical guide and specification: RBAC-Tri-Party-Comparison-210726'
aliases:
- RBAC-Tri-Party-Comparison-210726
- RBAC Tri Party Comparison 210726
entity_type: how_to
domain: self-docs > security
last_verified: 2026-07-21
---

# RBAC-Tri-Party-Comparison-210726

**Ngày:** 2026-07-21
**Loại tài liệu:** so sánh 3 nguồn phân tích độc lập — không phải implementation plan, không phải báo cáo công việc ngày.

## 0. Ba nguồn

1. **Nội bộ** — `RBAC-Architecture-Reassessment-200726.md` (mục 1-14), do phiên Claude Code trước viết, có quyền đọc code thật.
2. **Gemini** — `RBAC_Architecture_Assessment_From_Gemini.md`, second opinion độc lập, nhận input là context prompt (không đọc code thật).
3. **GPT** — `RBAC_Second_Opinion_Analysis_From_GPT.md`, second opinion độc lập, cùng context prompt (không đọc code thật).

Cả 2 bên ngoài đều nhận đúng 1 context prompt (`self-docs/RBAC-Architecture-Reassessment-200726.md` tóm tắt + câu hỏi phản biện) — không đọc code, nên đánh giá của họ có giá trị ở góc **nguyên tắc/độ ưu tiên**, không có giá trị ở góc **chi tiết implementation thật** (ví dụ Gemini/GPT không biết `137/184` đã tăng từ `19/184`, không biết audit trail RBAC đã được nối thật ở mục 13-14 nội bộ).

## 1. Ma trận đồng thuận theo từng rủi ro

| # | Rủi ro | Nội bộ (200726) | Gemini | GPT | Đồng thuận |
|---|---|---|---|---|---|
| 1 | 4 cơ chế quyết định rời rạc | Option A (log+request_id) đã làm; Option B (resolve 1 lần) đánh giá lợi ích nhỏ hơn ước lượng, hoãn | Đề xuất **Single Gateway Middleware Pattern** — hợp nhất NGAY qua 1 middleware wrapper | Đây là vấn đề **observability**, không phải lỗ hổng thật; giữ Option A, **hoãn** unified `AuthDecision` tới khi có refactor router lớn hơn | **2/3 (Nội bộ + GPT) đồng ý hoãn hợp nhất lớn; Gemini là ngoại lệ đề xuất làm ngay** — xem mục 3 |
| 2 | Default-allow (opt-out) | Rủi ro thế trận đã ghi nhận, chưa đề xuất sửa cụ thể, chờ quyết định nghiệp vụ | **"Indefensible"** cho hệ thống lương — đề xuất CI/CD guardrail bắt buộc seed row + metric `AuthzDefaultAllowFallbackTriggered` + deadline flip sang deny | **Critical** trong bảng ưu tiên nhưng phần thân: "không nên là chính sách vĩnh viễn", đề xuất CI test seed row + shadow-mode so sánh trước khi flip | **3/3 đồng thuận: không được giữ vĩnh viễn.** Khác biệt là TỐC ĐỘ — Gemini muốn deadline cứng ngay, GPT/nội bộ nghiêng về đo trước (shadow-mode) |
| 3 | Handler self-filter (ESS/read-only/dashboard, đặc biệt 3 route `X-HRIS-Cookie`) | Đã phát hiện, gọi là "rủi ro thiết kế cần quyết định", **chưa sửa** | **Critical/P0** — gọi đích danh là "IDOR / Path Traversal", đề xuất kiến trúc cụ thể: bỏ header client-supplied, thêm middleware `RequireSelfScope` so khớp `employee_id` với JWT subject | Coverage test chỉ "phát hiện triệu chứng", cần chuyển ownership-check thành middleware/helper dùng lại được, không để từng handler tự làm | **3/3 đồng thuận đây là rủi ro thật cần xử lý** — Gemini/GPT đều đề xuất chuyển kiểm tra sở hữu ra khỏi handler thành middleware tái dùng được. Đây là điểm có **hành động cụ thể nhất, ít mơ hồ nhất** trong toàn bộ so sánh |
| 4 | SoD tự cấu hình RBAC (self-grant) | Đã chọn audit-only trước (dựa trên dữ liệu 12 `hr_admin`) — **đã triển khai** | Cho rằng audit-only "tạo vector leo thang vĩnh viễn nếu không chặn" — đề xuất hard-block self-escalation + maker-checker cho role mạnh | Với 12 `hr_admin`, "có khả năng chặn được mà không quá rủi ro" — audit-first hợp lý làm bước tạm, nhưng **prevention nên là mục tiêu dài hạn** | **3/3 đồng thuận hướng cuối cùng là phải chặn (prevention), không chỉ audit.** Nội bộ đã làm bước 1 (audit), cả 2 bên ngoài đều coi đây là bước TẠM, chưa phải điểm dừng |
| 5 | RLS vô hiệu do BYPASSRLS | Đã biết, đã ghi nhận từ trước (150726), chưa hành động | **P0** trong action matrix | **High priority** | **3/3 đồng thuận mức độ nghiêm trọng — đây là gap tồn tại lâu nhất (từ 150726) mà cả 3 bên đều xếp hạng cao nhất hoặc gần cao nhất** |
| 6 | Audit log deny chỉ ghi stdout, không persist | Đã ghi nhận (mục 5), chưa sửa | High severity — đề xuất kết nối vào bảng DB hoặc buffer persist | Medium priority — đồng ý cần persist | **3/3 đồng thuận cần persist**, khác nhau ở mức ưu tiên tương đối (Gemini xếp cao hơn GPT) |
| 7 | Frontend stale role/permission mid-session | Ghi nhận là rủi ro nhận thức (UX), không phải bypass bảo mật thật (backend vẫn chặn đúng) | Đề xuất role/permission version hashing qua Redis hoặc DB cho request thay đổi trạng thái | **Low priority** | **3/3 đồng thuận đây là rủi ro thấp nhất trong danh sách** — chỉ khác về giải pháp cụ thể (Gemini đề xuất hạ tầng mới, Redis) |

## 2. Điểm đồng thuận mạnh nhất — nên đưa vào backlog ngay, không cần tranh luận thêm

Xếp theo thứ tự cả 3 nguồn cùng xếp hạng cao:

1. **RLS vô hiệu (BYPASSRLS)** — biết từ 150726, 3/3 xác nhận mức độ nghiêm trọng, chưa có lý do kỹ thuật nào để tiếp tục trì hoãn ngoài việc chưa quyết định vận hành đổi DB role. Đây là gap có tuổi đời dài nhất trong toàn bộ RBAC work.
2. **3 route ESS đọc `X-HRIS-Cookie`/`filePath` từ client không đối chiếu JWT** — nội bộ gọi là "rủi ro thiết kế", cả Gemini và GPT gọi đích danh là lỗ hổng (IDOR-shaped) và đều đề xuất giải pháp CÙNG HƯỚNG: middleware tái dùng được thay cho tự-lọc trong handler. Đây là hạng mục có mức đồng thuận + mức cụ thể giải pháp cao nhất trong toàn bộ so sánh — ưu tiên phân tích/triển khai sớm.
3. **SoD self-configuration: chuyển từ audit-only sang có chặn (ít nhất chặn self-escalation lên role mạnh hơn)** — nội bộ đã làm bước audit đúng theo lựa chọn "đo trước khi khoá" nhất quán của dự án, nhưng cả 2 bên ngoài đều coi đây là bước tạm, không phải điểm dừng cuối.
4. **Default-allow không được là chính sách vĩnh viễn** — 3/3 đồng thuận hướng đi (default-deny cuối cùng), khác nhau ở tốc độ. Hành động tối thiểu 3/3 đều gợi ý: **CI/CD test bắt buộc mọi module/action mới phải có permission row tường minh trước khi merge** — đây là việc RẺ, có thể làm ngay mà không cần quyết định flip default ngay.
5. **Audit log deny cần persist DB**, không chỉ ghi `stdout`.

## 3. Điểm bất đồng cần người dùng quyết định

### 3.1. Hợp nhất 4 cơ chế quyết định — làm ngay hay hoãn?

- Nội bộ + GPT: hoãn, gộp vào một đợt refactor router lớn hơn trong tương lai (lợi ích thực tế nhỏ, rủi ro đụng code lõi auth).
- Gemini: đề xuất **Single Gateway Middleware Pattern** ngay — một middleware wrapper gọi 1 policy evaluator interface thống nhất.
- Nhận xét khách quan: Gemini không có quyền truy cập code thật nên có thể đang đánh giá thấp độ phức tạp thật của việc đổi tất cả route để đi qua 1 gateway (đây chính là điều nội bộ đã đo — mục 9 tài liệu gốc, ước lượng Phương án B 2-4 ngày kèm rủi ro đụng auth core). Khuyến nghị: **giữ quyết định hoãn đã có**, nhưng ghi nhận ý tưởng "gateway middleware" của Gemini làm hình dạng đích khi thực sự làm refactor lớn.

### 3.2. Tốc độ flip default-allow → default-deny

- Gemini muốn deadline cứng ("Mandatory Deprecation Timeline").
- Nội bộ + GPT nghiêng shadow-mode, đo trước khi khoá (nhất quán với cách dự án đã làm mọi quyết định opt-out khác — SoD, RLS bổ sung...).
- Khuyến nghị: giữ nguyên triết lý "đo trước khi khoá" đã dùng xuyên suốt dự án, nhưng lấy gợi ý CI-gate của Gemini/GPT làm việc-làm-ngay (mục 2.4 ở trên) để KHÔNG cần chờ quyết định flip mới có hành động.

## 4. Rủi ro/hạng mục mới mà 2 bên ngoài nêu ra, nội bộ chưa ghi thành mục riêng

Những điểm này KHÔNG mâu thuẫn nội bộ, chỉ là góc nhìn bổ sung — nên xem xét đưa vào backlog kế tiếp:

1. **Quy tắc precedence permission chưa được viết ra thành văn bản tường minh** (GPT, mục "Permission semantics"): allow vs deny, multi-role, multi-parent-role, priority tương tác với nhau ra sao khi 2+ quy tắc mâu thuẫn. Hệ thống ĐÃ có logic thật (OR theo role + priority tie-breaker, sửa ở 200726) nhưng chưa có tài liệu đặc tả riêng — rủi ro là bug tương tự OR-semantics 200726 lặp lại vì không ai có bảng quy tắc để đối chiếu khi sửa.
2. **Route coverage ≠ authorization coverage** (GPT): `chi.Walk()` coverage test (G1, mở rộng 200726) chỉ xác nhận route CÓ gắn middleware nào, không xác nhận middleware đó áp đúng logic nghiệp vụ (ví dụ 3 route ESS ở mục 3 — có "allowlist" nhưng logic bên trong sai). Cần một lớp test khác: "semantic integration test" theo từng route thay vì chỉ đếm middleware.
3. **Route classification taxonomy tường minh** (GPT): đề xuất mọi route phải khai báo rõ 1 trong 6 nhóm (Public/Authenticated/Self/Role/Permission/Internal), không có "chưa phân loại". Hệ thống hiện đã có tương đương một phần (test coverage 200726 phân 3 nhóm: fine-gated/role-only/allowlist), có thể mở rộng thêm nhãn Self/Public/Internal để rõ hơn.
4. **CI/CD guardrail cụ thể cho seed permission row** (Gemini): chưa có trong backlog nội bộ nào — là việc rẻ, cụ thể, có thể làm độc lập không cần quyết định lớn.
5. **Metric quan sát `AuthzDefaultAllowFallbackTriggered`** (Gemini): ý tưởng đo tần suất thực tế default-allow đang "cứu" ai — dữ liệu này sẽ trực tiếp trả lời câu hỏi mục 3.2 (có nên flip ngay hay không) bằng số liệu thay vì ước lượng.
6. **JWT lifecycle chưa có tài liệu** (GPT): hành vi refresh/revoke role chưa viết thành văn bản riêng (có liên quan tới mục 6 nội bộ — frontend stale role — nhưng góc nhìn GPT là thiếu tài liệu, không chỉ thiếu tính năng).

## 5. Backlog tổng hợp đề xuất (chưa triển khai, chờ người dùng chọn thứ tự)

Ưu tiên theo mức đồng thuận (mục 2) trước, sau đó mới tới nhóm cần quyết định (mục 3) và nhóm bổ sung (mục 4):

| Ưu tiên | Việc | Vì sao | Nguồn đồng thuận | Trạng thái |
|---|---|---|---|---|
| P0 | Đổi DB role chạy app sang non-superuser (bỏ `BYPASSRLS`) | RLS đang vô hiệu hoàn toàn, biết từ 150726 | Nội bộ + Gemini + GPT | ⬜ Chưa làm |
| P0 | Sửa 3 route ESS (`leave-details`/`timesheet-raw`/`attendance-calendar`) — bỏ tin client-supplied cookie/filePath, đối chiếu JWT | IDOR-shaped, đã có giải pháp cụ thể từ cả 2 bên ngoài | Nội bộ (đã phát hiện) + Gemini + GPT (đã đề xuất fix) | ✅ Xong (2026-07-22) — xem mục 7 |
| P1 | Audit log deny: persist vào DB thay vì chỉ `stdout` | Mất toàn bộ forensic khi restart | Nội bộ + Gemini + GPT | ✅ Xong (2026-07-22) — xem mục 7 |
| P1 | CI test bắt buộc permission row tường minh cho module/action mới | Rẻ, chặn được silent privilege creep mà không cần flip default ngay | Gemini + GPT | ⬜ Chưa làm |
| P2 | Chặn self-escalation (actor == target hoặc actor đang giữ role bị sửa) cho role mạnh, giữ audit cho phần còn lại | 12 hr_admin → rủi ro khoá nhầm thấp, 3/3 đồng thuận hướng cuối là phải chặn | Nội bộ (đã làm audit) + Gemini + GPT | ⬜ Chưa làm |
| P3 | Viết tài liệu precedence permission (allow/deny/multi-role/priority) | Ngăn lặp lại bug kiểu OR-semantics 200726 | GPT (mới) | ✅ Xong (2026-07-22) — `RBAC-Permission-Precedence-220726.md` |
| P3 | Metric `AuthzDefaultAllowFallbackTriggered` hoặc tương đương | Cho số liệu thật để quyết định tốc độ flip default-deny | Gemini (mới) | ⬜ Chưa làm |
| Hoãn (đã quyết) | Unified `AuthDecision` / Single Gateway Middleware | Lợi ích nhỏ hơn ước lượng, rủi ro đụng auth core — giữ nguyên quyết định hoãn của nội bộ+GPT | Nội bộ + GPT (Gemini bất đồng, xem mục 3.1) | Hoãn |

## 7. Cập nhật 2026-07-22 — triển khai P0 #2, P1 #1, P3 #1

### P0 #2 — 3 route ESS (IDOR-shaped filePath/cookie)

Trace lại toàn bộ luồng trước khi sửa, phát hiện thực tế khác với mô tả ban đầu: frontend (`Core System-frontend/lib/api/ess.ts`) **hiện không hề gửi header `X-HRIS-Cookie`**; `filePath` cho `attendance-calendar` đang **hardcode 1 giá trị demo** (`app/(app)/v1/ess/page.tsx:12`, mã nhân viên `001590` dùng chung cho mọi người dùng) — tính năng chưa hoàn thiện, chưa thật sự expose cho người dùng thật hôm nay, nhưng backend vẫn ở tư thế tin bất kỳ input nào một khi frontend nối dây thật.

Không có bảng ánh xạ `employee_code` (Workday, đang/sẽ đổi mã) sang mã nhân viên số của cổng HRIS legacy ASP.NET (nêu ra với người dùng, xác nhận mã Workday sẽ khác `001590`) — chọn hướng **trust-on-first-use (TOFU)**: cột mới `employees.hris_portal_employee_code` (migration `20260722000000_hris_portal_employee_code.sql`, nullable, đã áp dụng vào `payroll_engine`), lần gọi hợp lệ đầu tiên của mỗi nhân viên tự ghi nhận mã quan sát được trong `filePath`, các lần sau bắt buộc khớp — lệch → 403 (`ESSService.AuthorizeAttendanceFilePath`, `EmployeeRepo.CheckAndLinkHRISPortalCode`). Đồng thời enforce định dạng `filePath` bằng regex chặt (`attendanceFilePathRe`) — chặn luôn path traversal.

`leave-details`/`timesheet-raw` (chỉ có cookie, không có filePath — không có tham số định danh nào để đối chiếu) — không thể verify ownership tương tự (cookie là chuỗi ASP.NET session opaque, không tự chứa định danh nào backend giải mã được). Residual risk ghi rõ trong code (`logHRISPortalProxyAccess`): thêm audit log mỗi lần proxy (email JWT + request_id), CHƯA chặn được — cần thiết kế lại luồng đăng nhập HRIS (session do backend quản lý thay vì trình duyệt) để đóng triệt để, ngoài phạm vi lượt sửa này.

Test: `internal/service/ess_hris_portal_selfscope_integration_test.go` (4 case: lần đầu tự ghi nhận, lần sau khớp không chặn, mã khác bị chặn, path traversal bị chặn).

### P1 #1 — Audit log deny persist DB

`logAccessDenied` (`internal/middleware/access_audit.go`) trước đây chỉ `slog.Warn` (stdout/stderr) — giờ ghi thêm 1 dòng vào bảng `audit_logs` có sẵn (tái dùng hạ tầng, không thêm bảng mới), action=`access_denied`, module=tên middleware (`RequireRole`/`RequirePermission`/...), details=JSON gộp reason/method/path/request_id + các field riêng từng middleware (required_roles, target_company...).

`RequireRole` không nhận `db` (khác 4 middleware còn lại) và có ~100+ điểm gọi trong `router.go` — thay vì đổi chữ ký tất cả, `AuthJWT` (middleware ngoài cùng, bọc mọi route, đã nhận `db`) stash `db` vào request context (`auditDBKey`, `internal/middleware/auth.go`); `persistAccessDenied` đọc lại từ context, no-op nếu không có (giữ nguyên hành vi test cũ không set context này). Chạy trong goroutine riêng, best-effort, timeout 5s — lỗi persist không được phép chặn/làm chậm quyết định 403 chính nó, chỉ `slog.Error` để vận hành biết audit trail có lỗ hổng.

Test: `internal/middleware/access_audit_persist_integration_test.go` — xác nhận có DB trong context thì ghi đúng 1 dòng, và các test cũ (không set context) vẫn im lặng đúng như trước (không hồi quy `TestRequireRoleAllowDoesNotLogDenial`).

### P3 #1 — Tài liệu precedence permission

`self-docs/RBAC-Permission-Precedence-220726.md` — đặc tả tường minh cách 4 cơ chế (role-hierarchy, permission opt-out+priority, company/department scope, super-admin bypass) quyết định khi có mâu thuẫn: bảng quyết định đầy đủ cho permission opt-out+priority (cơ chế duy nhất có precedence thật sự phức tạp), giải thích tại sao AND tuyệt đối giữa các cơ chế xếp chồng trên 1 route (không merge/không ưu tiên cơ chế nào), và quy trình gỡ lỗi theo thứ tự tra cứu khi có ca cụ thể.

### Bằng chứng

`go build`/`go vet` sạch. `go test ./...` trên `payroll_engine`: **695 passed, 9 failed** — đúng 9 fail baseline cũ (repository ×2, geo ×2, handler ×4, me ×1), không hồi quy.

## 6. Tham chiếu

- `RBAC-Architecture-Reassessment-200726.md` — nguồn nội bộ, có quyền đọc code thật, canonical cho mọi số liệu coverage/implementation.
- `RBAC_Architecture_Assessment_From_Gemini.md`, `RBAC_Second_Opinion_Analysis_From_GPT.md` — 2 second opinion độc lập, không đọc code thật, giá trị ở góc nguyên tắc/ưu tiên.
- `RBAC-Backlog-Tracklist-160726.md` — backlog canonical hiện có; nên gộp các mục P0-P3 ở mục 5 vào đây khi bắt đầu triển khai (không tạo backlog thứ 2 song song).
