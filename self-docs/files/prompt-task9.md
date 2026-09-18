---
id: self-docs/files/prompt-task9
canonical_question: 'Technical guide and specification: Brief thi hành — Task 9  —
  Tài liệu tổng kết'
aliases:
- Brief thi hành — Task 9  — Tài liệu tổng kết
- prompt Task9 060826
entity_type: how_to
domain: self-docs > files
last_verified: 2026-09-17
---

# Brief thi hành — Task 9 (PLAN 040826-Core System-template-on-giatbh-engine) — Tài liệu tổng kết

**Đây là phiên THI HÀNH theo brief đã chốt, không phải phiên thiết kế.** Task cuối cùng của PLAN —
Task 0-8 đều đã xong. Không có code nào để sửa, chỉ cập nhật tài liệu — nhưng vẫn phải xác minh từng
điều viết ra khớp code thật (grep/psql), không chép từ trí nhớ.

## Bối cảnh

PLAN: `llmwiki/wiki/sources/draft/040826-Core System-template-on-giatbh-engine-PLAN.md`, mục "### Task 9
— Tài liệu" (đọc nguyên văn 5 bước + lệnh kiểm cuối mục — brief này chỉ ra CHÍNH XÁC những chỗ đã lỗi
thời, đã grep xác nhận 060826, không suy đoán).

## Các lỗ tài liệu đã xác nhận cụ thể (060826)

### 1. `Core System-backend/docs/routes-permissions.md:196` — route SAI, vẫn ghi GET dù đã đổi POST từ Task 4

```
Dòng 196 hiện ghi: | `GET /Core System/template-impact/{periodId}` | ...
```
Route THẬT (xác nhận `grep -n "template-impact" internal/app/router.go`):
```
POST /api/v1/Core System/template-impact/{periodId}
```
Đây đúng là điều PLAN Task 9 bước 2 cảnh báo trước ("đổi GET→POST `template-impact` nếu làm Task 4")
— chưa ai sửa dòng tài liệu này dù Task 4 đã đổi route từ lâu. Sửa `GET` → `POST` tại dòng 196.

### 2. `Core System-backend/docs/routes-permissions.md` — thiếu HOÀN TOÀN 3 route mới của Task 7

Grep `internal/app/router.go` xác nhận các route sau chưa có dòng nào trong tài liệu:
```
POST   /api/v1/config/employee-Core System-templates/bulk       (Task 7, gate: requireSalaryComponentsCreate)
```
Thêm 1 dòng vào bảng route hiện có, cùng khuôn các dòng `/config/employee-Core System-templates/*` khác
đã có trong file (nếu bảng đó tồn tại — grep `employee-Core System-templates` trong file để tìm đúng vị
trí chèn; nếu bảng route cho nhóm này chưa từng có dòng nào, tạo mới theo khuôn của các nhóm route
khác trong cùng file).

### 3. `Core System-frontend/docs/routes-permissions.md` — 0 dòng nào cho toàn bộ nhóm `Core System-templates`

Grep xác nhận file này **không có một dòng nào** nhắc tới `Core System-templates`/`template-impact`/
`employee-Core System-templates` — file song sinh với backend nhưng chưa từng đồng bộ nhóm route này.
Copy toàn bộ nhóm route từ `Core System-backend/docs/routes-permissions.md` (sau khi đã sửa mục 1+2 ở
trên) sang file frontend, theo đúng khuôn/format các nhóm route khác đã có trong file frontend đó.

### 4. `Core System-backend/docs/database-schema.md` — thiếu bảng mới của Task 8 + Task 1

Grep xác nhận file có `payroll_templates`/`template_components` (dòng 471, 476, quan hệ dòng
567-568) nhưng **KHÔNG có**:
- `employee_payroll_templates` (Task 1, tồn tại thật trong DB — `\d employee_payroll_templates`)
- `template_component_versions` (Task 8, mốc BZ — `\d template_component_versions`)

Thêm 2 khối ERD/bảng cho 2 bảng này, theo đúng khuôn `template_components` đã có (dòng 476), lấy
schema thật bằng `psql ... -c "\d employee_payroll_templates"` và `\d template_component_versions`
— KHÔNG chép từ PLAN (PLAN có thể lệch cột thật nếu code đã tinh chỉnh khi thi hành).

### 5. `self-docs/Salary-Structure-Template-Analysis-260726.md` mục 13 — HOLD chưa đánh dấu kết thúc

Mục 13 hiện tên là "Quyết định HOLD toàn bộ tính năng...". Thêm 1 đoạn ngay đầu mục 13 (không xoá nội
dung cũ — đó là lịch sử quyết định HOLD, vẫn có giá trị): "**Cập nhật 060826: HOLD đã kết thúc.**
Toàn bộ PLAN `040826-Core System-template-on-giatbh-engine-PLAN.md` (Task 0-8) đã hoàn tất — xem PLAN mục
'Tiến độ' để có tóm tắt đầy đủ + commit hash từng task. Tính năng hiện ĐANG BẬT ở dev local
(`PAYROLL_TEMPLATE_ENFORCE=on`)."

### 6. Đính chính "3 lớp bảo vệ" — kiểm xem còn tồn tại không

PLAN Task 9 bước 1 nhắc "đính chính những chỗ mục 7/9 nói mask có 3 lớp bảo vệ (đã sai — xem 14.6
(1))". Grep `self-docs/Salary-Structure-Template-Analysis-260726.md` tìm cụm "3 lớp" ở mục 7 và mục
9 — nếu đã có đính chính từ phiên trước (kiểm mục 16.6 xem đã ghi chưa) thì bỏ qua bước này, không
lặp lại. Nếu CHƯA đính chính, thêm 1 câu ở đúng vị trí mục 7/9 trỏ sang mục 16.6 (đã đính chính đúng
thật là gì).

## Các bước

1. Đọc PLAN mục "### Task 9 — Tài liệu" (5 bước gốc) — brief này bổ sung, không thay thế.
2. Sửa 5 lỗ đã liệt kê ở trên, theo đúng thứ tự.
3. Kiểm bằng đúng 2 lệnh PLAN đã cho sẵn ở cuối mục Task 9:
```bash
grep -n "template-impact\|template-enforce-status" Core System-backend/internal/app/router.go
grep -n "template-impact\|template-enforce-status" Core System-backend/docs/routes-permissions.md \
     Core System-frontend/docs/routes-permissions.md
```
Đối chiếu 2 output — route trong tài liệu PHẢI khớp route thật (method + path), không chỉ có mặt.
4. Cập nhật `self-docs/document-map.md`: thêm dòng cho 2 SPEC/PLAN mới nếu chưa có
   (`060826-report-template-config-v1.md`, `060826-report-template-config-v1-PLAN.md` — kiểm bằng
   `grep -n "060826-report-template" self-docs/document-map.md`, nếu đã có thì bỏ qua).
5. Thêm 1 dòng nhật ký `CLAUDE.md` (mới nhất lên đầu mục "Nhật ký công việc theo ngày"), tóm tắt:
   toàn bộ PLAN template (Task 0-8) đã hoàn tất, trỏ tới PLAN mục "Tiến độ" để không lặp chi tiết đã
   ghi ở đó, kèm commit hash BE/FE của Task 5-9.

## Ràng buộc tuyệt đối

- KHÔNG xoá nội dung lịch sử ở mục 13 (HOLD) — chỉ THÊM đoạn cập nhật, giữ nguyên phần cũ làm bằng
  chứng lịch sử quyết định.
- Schema ghi vào `database-schema.md` PHẢI lấy từ `psql \d <table>` thật, không chép từ PLAN hay
  brief này (có thể đã lệch nếu code tinh chỉnh khi thi hành Task 8).
- KHÔNG sửa lại nội dung Task 0-8 trong bảng "Tiến độ" của PLAN — nó đã đúng và đầy đủ (đã cập nhật
  060826), Task 9 chỉ thêm tài liệu MỚI, không viết lại lịch sử đã ghi.

## DỪNG và hỏi khi

- Route thật (`grep router.go`) khác những gì brief này liệt kê — nghĩa là có thay đổi giữa lúc viết
  brief và lúc thi hành, báo lại route thật trước khi ghi tài liệu.
- Không tìm thấy bảng route nào cho nhóm `/config/Core System-templates`/`/config/employee-Core System-templates`
  trong `Core System-frontend/docs/routes-permissions.md` để biết chèn theo khuôn nào — hỏi thay vì tự
  bịa format mới.

## Định nghĩa xong

1. `routes-permissions.md` (2 repo) khớp tuyệt đối route thật — xác nhận bằng 2 lệnh grep ở Bước 3.
2. `database-schema.md` có đủ `employee_payroll_templates` + `template_component_versions`, lấy từ
   `psql` thật.
3. Mục 13 của `Salary-Structure-Template-Analysis-260726.md` đã đánh dấu HOLD kết thúc.
4. `document-map.md` không thiếu entry nào cho SPEC/PLAN 060826.
5. 1 dòng nhật ký `CLAUDE.md` mới, đúng format, đúng vị trí (đầu mục, không phải cuối).
6. Commit (có thể gộp cả 2 repo tài liệu vào 1 lần commit mỗi repo nếu cả BE/FE docs đều sửa) — hỏi
   xác nhận trước khi commit, không tự push.
