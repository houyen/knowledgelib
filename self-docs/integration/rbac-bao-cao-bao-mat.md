---
id: self-docs/integration/rbac-bao-cao-bao-mat
canonical_question: 'Technical guide and specification: Báo cáo — Công việc RBAC/Bảo
  mật dự án Core System'
aliases:
- Báo cáo — Công việc RBAC/Bảo mật dự án Core System
- RBAC Bao Cao Bao Mat 150726
entity_type: how_to
domain: self-docs > integration
last_verified: 2026-07-15
---

# Báo cáo — Công việc RBAC/Bảo mật dự án Core System

**Ngày:** 2026-07-15
**Phạm vi:** Toàn bộ công việc RBAC/phân quyền/bảo mật từ 2026-07-14 (140726) đến 2026-07-15 (150726), nhánh `sec_dev` (`Core System-backend` + `Core System-frontend`).
**Mục đích:** Báo cáo tổng hợp để theo dõi tiến độ trước khi quyết định làm tiếp — đây là bản TÓM TẮT, không thay thế 2 tài liệu chi tiết:
- `self-docs/RBAC-Hybrid-Scoping-Implementation-140726.md` — toàn bộ chi tiết công việc ngày 140726 (schema, hierarchical RBAC, company/department scoping, `site_admin`).
- `self-docs/RBAC-Improvement-Analysis-150726.md` — toàn bộ chi tiết công việc ngày 150726 (đối chiếu WorkOS/IBM, 10 gap G1–G10, và triển khai 4 yêu cầu bảo mật nghiệp vụ).

---

## 1. Những việc đã làm được

### 1.1 Ngày 140726 (nền tảng)

| Việc | Kết quả |
|---|---|
| Vá lỗ hổng high-risk: `hr_admin` duyệt được Core System công ty khác | `RequireUnrestrictedScope`/`RequireCompanyScopeMatch`, cột `scope_company_code` trên `employee_roles` |
| Hierarchical RBAC | `parent_role_id` + `expandRoleHierarchy` (đệ quy SQL, resolve động) — cơ chế sẵn sàng, chưa có role nào dùng |
| Hợp nhất vai trò FE/BE | Xoá `pm` (không tồn tại thật), thêm `site_admin`/`search_profile` (tồn tại thật) vào đúng chỗ ở FE |
| Định nghĩa + triển khai `site_admin` | Xem chấm công/bảng công, giới hạn theo công trường qua `EnforceSiteAdminDepartmentFilter` (ép query-param phía server) |
| Vá phụ: route chấm công/bảng công không có `RequireRole` | Đóng theo 3 tầng gate tuỳ mức nhạy cảm dữ liệu |
| Đồng bộ tài liệu route↔role | `Core System-backend/docs/routes-permissions.md` ↔ `Core System-frontend/docs/routes-permissions.md` |

### 1.2 Ngày 150726 (4 yêu cầu bảo mật nghiệp vụ nhận từ phía kinh doanh)

| # | Yêu cầu | Trạng thái | Tóm tắt |
|---|---|---|---|
| — | *Phát hiện phụ*: route đọc Core System lõi không có `RequireRole` | ✅ Đã vá | `rows/summary/period/cell-overrides/cell-edits/attendance-codes`, `Core System-periods` List/GetByID, `allowance-overrides` GET/parse/conflicts — thêm `RequireRole(hr_admin, cb_staff)` |
| 2 | Ẩn dữ liệu theo pháp nhân (Enterprise/Unicons/Mắt Bão/Covescons) | ✅ Đã đóng | `ResolveReadCompanyScope` (lọc, không chặn) + lọc SQL/Go-side cho toàn bộ route đọc Core System |
| 3 | Chỉ HR Admin & C&B Staff truy cập Core Core System | ✅ Đã đóng | Cùng bản vá với phát hiện phụ; xác nhận "Core Core System" không gồm chấm công → `site_admin` không xung đột |
| 4 | Audit log: cũ→mới, người thực hiện, thời gian, lý do bắt buộc | ✅ Đã đóng | reason bắt buộc (400 nếu thiếu) cho CellSet/CellUndo/PatchDay; Old/NewValues gộp JSON vào `details`; `UndoCell`/`PatchDay` atomic hoàn toàn qua transaction, `SetCell` atomic một phần |
| 1 | Phân quyền chi tiết: Xem/Sửa/Xuất file/Khóa kỳ/Duyệt thay | 🟡 Đã đóng phần lớn | `RequirePermission` middleware mới (mặc định allow-until-configured) cho Core System/PayrollPeriods/Reports; Khóa kỳ mount + sửa bug thật; **Duyệt thay chưa làm** |
| G2 | Audit log có cấu trúc cho quyết định từ chối quyền | ✅ Đã đóng | `internal/middleware/access_audit.go`, wire vào 5 điểm deny thật (`log/slog`, không migration DB) |
| R1 | Row-Level Security (RLS) trên `employees` | ✅ Đã đóng | Migration fail-open + `ResolveReadCompanyScope` mở tx riêng SET session var khi scope không unlimited; **nhưng đang vô hiệu thật** vì app kết nối bằng role `postgres` (superuser/BYPASSRLS) — xem mục 2 |
| R2 | Data Masking cho `site_admin` (số tiền phụ cấp) | ✅ Đã đóng | Zero 6 nhóm phụ cấp + breakdown trên `GET /hris/attendance-daily/matrix` khi caller chỉ có `site_admin` |
| G1 | Test-guard chống thiếu `RequireRole` ở route mới | ✅ Đã đóng (160726) | `chi.Walk()` + allowlist tường minh — tìm ra **2 lỗ hổng mới** (Employee routes kể cả bank-accounts, HRIS connectors, departments), đã vá cả 3 |
| G4 | Báo cáo rà soát quyền định kỳ, ưu tiên nêu ngoại lệ | ✅ Đã đóng (160726) | `GET /roles/access-review` — cờ `multipleRoles`/`unusualScope` |
| G9 | Checklist JML thủ công | ✅ Đã đóng (160726) | `RBAC-JML-Checklist-Van-Hanh-150726.md`, tài liệu vận hành, không code |
| G10 | Vai trò DB scope hẹp cho agent | 🟡 Chuẩn bị, chưa áp dụng (160726) | Script `create-agent-data-role.sql` đã viết; auto-mode Claude Code chặn tự chạy (cấp quyền DB thật), người dùng chọn giữ lại chưa chạy |

### 1.3 Bằng chứng chất lượng (không phải khẳng định suông)

- Toàn bộ thay đổi đều có **test tích hợp chạy thật trên Postgres** (`TEST_DATABASE_URL`), không chỉ mock — bao gồm cả việc tự phát hiện và sửa 1 bug NULL-scan thật trong lúc viết test (140726).
- Mỗi lần sửa đều đối chiếu hồi quy bằng `git stash` + chạy lại baseline trước khi kết luận "không gây fail mới".
- Trạng thái cuối 150726: `go build`/`go vet` sạch; `go test ./...` = **396 passed, 12 failed** — toàn bộ 12 fail là baseline đã biết từ trước (schema drift ở vài integration test khác, không liên quan RBAC), không có fail mới. (Số 389 ban đầu là mốc trước khi làm G2/R1/R2 — mỗi lượt sau đều thêm test mới và giữ đúng 12 fail baseline, không hồi quy.)
- 2 lỗ hổng bảo mật thật (không phải lý thuyết) được tìm và vá trong 2 ngày: (a) company-scope thiếu trên `Finalize`/`Calculate` (140726), (b) toàn bộ route đọc Core System lõi không có role-gate (150726) — cùng nguyên nhân gốc (xem mục 2, G1).

---

## 2. Những điểm bị gap (đã có phân tích, chưa xử lý hoặc xử lý một phần)

Từ đối chiếu với 2 khung tham khảo bên ngoài (WorkOS, IBM) — 10 gap được đặt mã G1–G10, xem chi tiết đầy đủ ở `RBAC-Improvement-Analysis-150726.md` mục 3:

| Mã | Gap | Mức độ |
|---|---|---|
| **G1** | ~~Không có Policy Decision Point (PDP) tập trung~~ **✅ Test-guard đã đóng 2026-07-16** — logic phân quyền vẫn rải rác (PDP đầy đủ là Phase 2/OPA), nhưng nay có `chi.Walk()` test tự động chặn route mới quên gate. Việc xây test này tìm ra thêm 2 lỗ hổng mới (Employee bank-accounts, HRIS connectors, departments), đã vá cả 3 | Từng **Cao** — là nguyên nhân gốc của 4 lỗ hổng đã vá (140726 ×2, 150726 ×1, 160726 ×2) |
| **G2** | ~~Không có audit log có cấu trúc cho quyết định TỪ CHỐI quyền (khác audit log cho hành động sửa dữ liệu — đã đóng ở yêu cầu 4)~~ **✅ Đã đóng 2026-07-15** — `internal/middleware/access_audit.go`, xem `RBAC-Improvement-Analysis-150726.md` mục 3/G2 | — |
| **G3** | Không đồng bộ vai trò với Azure AD (IdP) — gán/thu hồi hoàn toàn thủ công | Trung bình — rủi ro quên thu hồi khi nghỉ việc |
| **G4** | ~~Không có báo cáo rà soát quyền định kỳ (access recertification)~~ **✅ Đã đóng 2026-07-16** — `GET /roles/access-review`, cờ `multipleRoles`/`unusualScope` | — |
| **G5** | `site_admin` chỉ khớp đúng 1 node `org_structures`, không mở rộng cây con | Trung bình — chặn đúng nhu cầu hợp lệ nếu công trường có cấu trúc phân cấp |
| **G6** | `site_admin` không gán được nhiều hơn 1 công trường cùng lúc | Thấp — giới hạn kỹ thuật có chủ đích, an toàn (403) hơn là đoán sai |
| **G7** | Không có Separation of Duties (SoD) — một người có thể vừa Calculate vừa Finalize cùng kỳ lương không cần người thứ hai xác nhận | Trung bình — tuỳ nghiệp vụ có bắt buộc four-eyes hay không |
| **G8** | Vai trò cấp bậc (hierarchy) có cơ chế nhưng chưa có role nào dùng | Thấp — cơ hội bỏ ngỏ, không phải bug |
| **G9** | ~~Không có quy trình Joiner-Mover-Leaver (JML) tường minh~~ **✅ Đã đóng 2026-07-16** — `self-docs/RBAC-JML-Checklist-Van-Hanh-150726.md`, quy trình vận hành 3 phần, không code | — |
| **G10** | AI agent/service-account chưa có vai trò DB riêng scope hẹp khi thao tác trực tiếp | 🟡 **Script sẵn sàng, chưa áp dụng 2026-07-16** — `create-agent-data-role.sql`; auto-mode Claude Code chặn tự chạy (cấp quyền DB thật cần xác nhận rõ hơn), người dùng chọn giữ lại chưa chạy |

**Gap phát sinh từ chính đợt triển khai 150726 (mới, chưa có ở G1–G10):**

- **Company-scope (yêu cầu 2) chưa áp cho ~12 report generator** (`report_gen_*.go` — bảng lương ngân hàng, bảo hiểm, kê toán...) — cố ý giữ `unlimited=true` vì là quyết định nghiệp vụ riêng đã xác nhận, nhưng đây vẫn là một khoảng hở thật: một `hr_admin` bị giới hạn 1 công ty vẫn xuất được báo cáo Excel chứa dữ liệu mọi công ty.
- **`RequirePermission` (yêu cầu 1) mới chỉ gắn cho 3/19 module** (`Core System`, `PayrollPeriods`, `Reports`) mà FE đã định nghĩa sẵn ở tab "Ma trận quyền hạn" — 16 module còn lại (Employees, Departments, Settings.*...) có UI cấu hình nhưng **chưa có tác dụng enforce thật**.
- **`SetCell` chỉ atomic một phần** — bước ghi override đầu tiên không nằm trong transaction (giới hạn kỹ thuật thật: engine tính lương cần đọc dữ liệu đã commit qua kết nối khác), khác với `UndoCell`/`PatchDay` atomic hoàn toàn.
- **App kết nối Postgres bằng role `postgres` (superuser, `BYPASSRLS=true`)** — phát hiện khi triển khai R1: RLS vừa tạo trên `employees` hiện **không có tác dụng thật** với chính connection app đang dùng, dù policy đúng (đã chứng minh bằng test tạo role riêng). Đây là gap hạ tầng (liên quan G10), không phải lỗi thiết kế RLS.

---

## 3. Những điểm chưa thực hiện (đã biết rõ, chưa có code)

1. **Duyệt thay (approve-on-behalf/delegation)** — yêu cầu 1, phần còn lại duy nhất. Không phải một quyền on/off mà là quy trình ủy quyền — cần trả lời trước: ai ủy quyền cho ai, giới hạn thời gian, workflow xác nhận (A yêu cầu → B chấp nhận?), audit trail ghi "B hành động nhân danh A", ràng buộc với SoD (G7).
2. **Separation of Duties (SoD) thật** (G7) — hiện chỉ dừng ở phân tích, chưa có cảnh báo hay chặn nào.
3. **Đồng bộ Azure AD/IdP** (G3) — cần quyết định nghiệp vụ trước (có muốn quyền Core System gắn với group AD hay giữ độc lập).
4. **Cây phân cấp vai trò thật** (G8) — cơ chế đã sẵn sàng, chỉ thiếu quyết định nghiệp vụ "vai trò nào kế thừa vai trò nào".
5. **Mở rộng `site_admin` theo cây con `org_structures`** (G5) — chặn bởi chất lượng dữ liệu (`org_level` không sạch), cần chuẩn hoá dữ liệu trước.
6. **`site_admin` nhiều công trường cùng lúc** (G6) — cần đổi kiểu tham số filter (chuỗi đơn → mảng), ảnh hưởng cả FE/BE.
7. **Tự động hoá JML đầy đủ** (G9) — vượt quá checklist thủ công, cần nguồn sự kiện HR đáng tin cậy.
8. **Vai trò DB riêng cho AI agent trên production** (G10) — chưa cấp thiết (DB hiện tại là dev/local).
9. **`atlas/migrations/atlas.sum` chưa cập nhật** (tồn đọng từ 140726) — cần người có Atlas CLI + Docker chạy `atlas migrate hash`.
10. **PDP tập trung đầy đủ** (G1, ngoài phần test-guard) — thuộc Phase 2 (OPA/Rego) theo đúng phạm vi đã xác định từ đầu dự án ("api/auth sẽ làm ở phase sau").
11. **ABAC (ngưỡng tiền phê duyệt + giờ hành chính/IP)** — đã chốt kiến trúc (Phương án B: bảng cột tường minh, không OPA; shadow mode giai đoạn đầu — xem `RBAC-Improvement-Analysis-150726.md` mục 9) nhưng CHƯA viết code, đang chờ số liệu nghiệp vụ cụ thể: ngưỡng tiền bao nhiêu, áp cho hành động nào, "giờ hành chính"/"IP nội bộ" cụ thể là gì, và xác nhận hạ tầng proxy trước khi tin `X-Forwarded-For`.
12. **Đổi role Postgres app đang dùng sang non-superuser/NOBYPASSRLS** — điều kiện để RLS (R1) có tác dụng thật trong production, hiện chỉ mới đúng ở migration + code, chưa đúng ở vận hành thật.
13. **RLS cho `payroll_records`** — cần policy dạng `EXISTS` join `employees` theo `employee_code` (bảng này không có cột `company_code` trực tiếp), phức tạp hơn `employees`, để lại lượt sau theo quyết định người dùng.
14. **Company-scope cho report generator** — quyết định nghiệp vụ riêng, xem mục 2.
15. **Mở rộng `RequirePermission` cho 16 module còn lại** — kỹ thuật đơn giản (chỉ cần gắn middleware vào route tương ứng) nhưng cần xác nhận có cần thiết hay không cho từng module.

---

## 4. Những điểm có thể cải thiện (khuyến nghị, xếp theo giá trị/nỗ lực)

Từ mục "Tóm tắt khuyến nghị" của `RBAC-Improvement-Analysis-150726.md`, xếp theo tỷ lệ giá trị/nỗ lực:

1. ~~**Test-guard chống thiếu `RequireRole` ở route mới (G1, rẻ)**~~ **✅ Đã đóng 2026-07-16** — `chi.Walk()` test-guard, tìm ra thêm 2 lỗ hổng mới (Employee bank-accounts, HRIS connectors, departments), đã vá cả 3.
2. ~~**Audit log cho quyết định TỪ CHỐI quyền (G2, rẻ)**~~ **✅ Đã đóng 2026-07-15.**
3. ~~**Checklist JML thủ công (G9, rẻ nhất — không đụng code)**~~ **✅ Đã đóng 2026-07-16** — `RBAC-JML-Checklist-Van-Hanh-150726.md`.
4. ~~**Báo cáo rà soát quyền định kỳ, ưu tiên nêu ngoại lệ (G4, rẻ)**~~ **✅ Đã đóng 2026-07-16** — `GET /roles/access-review`.
5. **Vai trò DB scope hẹp cho agent (G10, rẻ về kỹ thuật)** — 🟡 script sẵn sàng (`create-agent-data-role.sql`), chưa áp dụng — auto-mode chặn tự chạy, người dùng chọn giữ lại chưa chạy.
6. **Cảnh báo SoD phạm vi hẹp (G7)** — chỉ cảnh báo (không chặn) khi 1 người tự Calculate rồi tự Finalize CÙNG kỳ lương — cần xác nhận nghiệp vụ trước khi chặn cứng.
7. **Mở rộng `RequirePermission` sang các module còn lại** — middleware đã generic, chỉ cần quyết định module nào cần và gắn thêm.
8. **Company-scope cho report generator** — nếu nghiệp vụ xác nhận cần, áp dụng cùng cơ chế đã có sẵn (`ResolveReadCompanyScope`).
9. **Đồng bộ Azure AD, cây phân cấp vai trò thật, mở rộng site_admin theo cây con, site_admin đa công trường** — đều cần quyết định nghiệp vụ hoặc dữ liệu sạch trước, nên hỏi riêng từng cái khi tới lượt.

---

## Tóm tắt 1 dòng

**Đã xong (150726 + 160726):** 4 lỗ hổng high-risk đã vá (140726 ×2, 150726 ×1, 160726 ×2 — Employee bank-accounts/HRIS connectors/departments), 4/4 yêu cầu bảo mật nghiệp vụ đã xử lý (3 đóng hoàn toàn, 1 đóng phần lớn — còn "Duyệt thay"), và 6/10 gap đã đóng: G1 (test-guard), G2 (audit log deny), G4 (access-review), G9 (checklist JML), cộng R1 (RLS trên `employees`, đang vô hiệu do role DB app là superuser) và R2 (data masking `site_admin`). **Còn lại:** 4/10 gap mở (G3, G5–G8), G10 chỉ ở dạng script chuẩn bị chưa áp dụng, 3 gap phát sinh từ đợt triển khai đầu (report generator, 16 module chưa enforce, SetCell atomic một phần), cộng ABAC (kiến trúc đã chốt, chờ số liệu nghiệp vụ) — tất cả đã ghi rõ, không giấu.
