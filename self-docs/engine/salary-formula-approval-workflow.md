---
id: self-docs/engine/salary-formula-approval-workflow
canonical_question: 'Technical guide and specification: Luồng duyệt công thức cột
  lương  — 26/08/2026'
aliases:
- Luồng duyệt công thức cột lương  — 26/08/2026
- Salary Formula Approval Workflow 260826
entity_type: how_to
domain: self-docs > engine
last_verified: 2026-09-17
---

# Luồng duyệt công thức cột lương (SPEC + PLAN + kết quả triển khai) — 26/08/2026

## Bối cảnh — vì sao cần

Khảo sát 25/08 phát hiện: FE (`UpdateFormulaDialog.tsx`, `TinhLuongExcel.tsx`) đã viết sẵn UI đầy đủ cho
luồng "duyệt công thức cột lương" (cột "Trạng thái duyệt", nút Duyệt/Từ chối, `isApprovalRequest()`),
NHƯNG BE (`SalaryComponentHandler.Update`) luôn ghi trực tiếp vào `salary_components` (bảng LIVE mà
engine tính lương đọc), không có nhánh tạo `ApprovalRequest`. Kết quả thật: mọi sửa công thức áp dụng
ngay lập tức, cột "Trạng thái duyệt" luôn hiện "Đã duyệt" (vì field nguồn `approvalStatus` không tồn
tại ở model Go, luôn rơi về default FE).

## Quyết định thiết kế (đã trình bày phương án, người yêu cầu chốt tiếp bằng "viết spec, plan và triển khai")

Tái dùng nguyên `internal/service/approval_service.go` (engine chung: `approval_rules` → `Resolve` →
`Submit` → `Act` → `applyFinal`) — KHÔNG viết engine duyệt mới, chỉ thêm 1 entity_type mới +
bảng "đề xuất chờ duyệt" tách khỏi bảng live.

Giả định mặc định (chưa được xác nhận từng điểm riêng — ghi rõ ở đây để dễ soát lại):
1. `salary_components` không có company/site riêng → rule cấu hình với `company_id=NULL,
   org_structure_id=NULL` (áp dụng toàn hệ thống). Form admin (company/site) vẫn giữ nguyên, chỉ
   không có ý nghĩa thực tế cho entity_type này — không chặn admin nếu họ vẫn muốn set.
2. Phạm vi CHỈ áp dụng cho **Update công thức/tên** (khớp đúng dialog đã có ở FE). Create/Delete/
   Reorder/ToggleVisible KHÔNG qua duyệt — giữ nguyên hành vi cũ.
3. CHƯA cấu hình `approval_rules` cho entity_type này → áp dụng NGAY (an toàn ngược, khớp convention
   opt-out-allow dùng khắp repo — `RequirePermission`, Core System approve/reject...).
4. Trạng thái "đang chờ duyệt" hiện cho MỌI người xem "Danh sách cột lương" (không ẩn) — khớp cách
   Core System approve/reject đang hiển thị.

## Thiết kế

### Bảng mới: `salary_component_pending_changes`
```sql
CREATE TABLE salary_component_pending_changes (
    id                 uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    component_id       uuid NOT NULL REFERENCES salary_components(id) ON DELETE CASCADE,
    component_code     varchar(50) NOT NULL,
    old_formula        text NOT NULL,
    new_formula        text NOT NULL,
    old_name           varchar(255) NOT NULL,
    new_name           varchar(255) NOT NULL,
    reason             text NOT NULL DEFAULT '',
    requested_by       varchar(255) NOT NULL,
    status             varchar(20) NOT NULL DEFAULT 'pending'
                          CHECK (status IN ('pending','approved','rejected')),
    approval_request_id uuid REFERENCES approval_requests(id) ON DELETE SET NULL,
    created_at         timestamptz NOT NULL DEFAULT now(),
    updated_at         timestamptz NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX uq_salary_component_pending_active
  ON salary_component_pending_changes (component_id) WHERE status = 'pending';
```
Không sửa `salary_components` cho tới khi duyệt xong cấp cuối — công thức cũ vẫn LIVE suốt thời gian chờ.

### entity_type mới: `salary_component_formula`
`applyFinal` thêm case: approved → gọi lại `SalaryComponentService.Update()` (hàm có sẵn, không viết
lại) với `new_formula/new_name` của pending change, rồi đánh dấu pending change `approved`; rejected →
chỉ đánh dấu pending change `rejected`, KHÔNG đụng `salary_components`.

### Luồng ghi (`PUT /config/salary-components/{id}`)
```
Resolve("salary_component_formula", nil, nil) → 0 cấp  → Update() trực tiếp như cũ
                                               → ≥1 cấp → tạo pending_change(pending)
                                                          → Submit(...) → trả ApprovalRequest
```
Response giữ đúng shape cũ (`SalaryComponent | ApprovalRequest`) — **0 thay đổi hợp đồng API**, FE đã
sẵn code nhận đúng 2 nhánh này từ 250727.

### `GET /config/salary-components` — thêm field hiển thị
LEFT JOIN pending change đang `pending` theo `component_id` → set `ApprovalStatus="pending"` cho đúng
dòng; các dòng khác để trống (FE tự fallback "approved" như hiện tại — 0 thay đổi FE cho phần này).

### FE — bổ sung theo yêu cầu #1: chọn entity_type trên giao diện Cấu Hình Duyệt
`app/(app)/v1/settings/approval-rules/page.tsx` đang hardcode `ENTITY_TYPE = "payroll_record"` (comment
gốc 240726 đã tự ghi "khung backend tổng quát sẵn... chỉ cần thêm rule + applier, không cần đổi trang
này" — nay cần đổi vì có entity_type thứ 2 thật). Đổi hằng số thành state + dropdown chọn loại đối
tượng (Bảng lương / Công thức cột lương), refetch rules theo entity_type đang chọn.

## Việc KHÔNG làm trong đợt này (ghi rõ, tránh hiểu lầm là đã xong)
- "Duyệt của tôi" (inbox chung, `app/(app)/v1/approvals/page.tsx`) — CHƯA thêm hiển thị chi tiết
  old/new formula cho entity_type mới; người duyệt tạm thấy dạng chung (entityType/entityId) như các
  entity khác chưa có UI riêng.
- Create/Delete/Reorder/ToggleVisible salary component — KHÔNG qua duyệt.

## Kết quả triển khai + test

### BE (`Core System-backend`, nhánh `feature/salary-formula-approval-workflow` từ `develop_v1`)

File sửa/thêm:
- `atlas/migrations/20260826000000_salary_component_pending_changes.sql` (mới) — bảng đề xuất
  chờ duyệt, đã apply tay lên DB dev (khớp tiền lệ `20260724000000_approval_engine.sql` — atlas
  migrate apply không dùng được ở môi trường nào, phải apply tay).
- `internal/models/Core System.go` — thêm `SalaryComponent.ApprovalStatus` (runtime, `db:"-"`, khớp
  pattern `Maskable`/`Role` có sẵn) + struct `SalaryComponentPendingChange`.
- `internal/repository/salary_component_repo.go` — `CreatePendingChange`, `GetPendingChangeByID`,
  `SetPendingChangeApprovalRequestID`, `SetPendingChangeStatus`, `DeletePendingChange`,
  `ListPendingComponentIDs`.
- `internal/service/approval_service.go` — const `EntityTypeSalaryComponentFormula`, field +
  setter `salaryComponentSvc`/`SetSalaryComponentService`, case mới trong `applyFinal`.
- `internal/service/salary_component_service.go` — field + setter `approvalSvc`/
  `SetApprovalService`, hàm `RequestUpdate` (entry point mới cho handler) + `ApplyPendingChange`
  (applier), sentinel `ErrPendingChangeExists`.
- `internal/service/service.go` — wiring 2 chiều (`SetSalaryComponentService`/`SetApprovalService`).
- `internal/handler/salary_component_handler.go` — `Update` gọi `RequestUpdate` thay `Update`
  trực tiếp; dịch `ErrPendingChangeExists` → 409 rõ nghĩa.

**Test tự động:** `go build ./...`/`go vet ./...` sạch. `go test ./...`: **824 passed / 0 failed**
(baseline `develop_v1` trước đợt này: 800/0 — không có test nào failed thêm, số tăng do file mới
chưa có unit test riêng cho phần này — CHƯA viết unit test, chỉ verify bằng test thật dưới đây).

**Test thật trên DB dev** (tạo rule → sửa → duyệt/từ chối → dọn dữ liệu, không để lại gì):
1. Tạo rule cấp 1, role `hr_admin`, entity_type `salary_component_formula`, company/site = NULL
   (toàn hệ thống) — qua `POST /admin/approval-rules`.
2. `PUT /config/salary-components/{id}` sửa formula `TRANSPORT_TAX` → trả về `ApprovalRequest`
   (status "pending"), **`salary_components.formula` KHÔNG đổi** — xác nhận đúng bằng SQL trực tiếp.
3. `GET /config/salary-components` → `approvalStatus: "pending"` đúng cho cột đang sửa.
4. `GET /approvals/inbox` (role hr_admin) → thấy đúng request pending, đúng role cần duyệt.
5. `POST /approvals/{id}/act {action:"approve"}` → **formula ÁP DỤNG THẬT** vào
   `salary_components` + ghi `salary_component_history` đúng (`ChangedBy` = người đề xuất).
6. Tạo đề xuất thứ 2, **Từ chối** → formula giữ nguyên bản đã duyệt ở bước 5 (không rơi về bản đề
   xuất bị từ chối, không đổi gì).
7. Bắt được bug thật khi test: gọi `PUT` lần 2 trong lúc đề xuất trước còn "pending" → lỗi generic
   `500 "failed to update component"` (đúng chặn bởi UNIQUE index, nhưng thông báo không rõ) — đã
   sửa: bắt `pq.Error` code `23505` → sentinel `ErrPendingChangeExists` → handler trả `409` kèm câu
   rõ nghĩa "cột này đang có 1 đề xuất sửa công thức khác chờ duyệt...". Verify lại: đúng 409 + đúng
   câu.

### FE (`Core System-frontend`, nhánh `feature/salary-formula-approval-workflow` từ `develop_v1`)

File sửa: `app/(app)/v1/settings/approval-rules/page.tsx` — đổi hằng số cố định `ENTITY_TYPE`/
`ENTITY_TYPE_LABEL` thành danh sách `ENTITY_TYPES` (payroll_record/salary_component_formula) +
dropdown "Loại đối tượng cần duyệt" (`Select` có sẵn, không thêm component mới), `useApi` refetch
theo `entityType` đang chọn.

**Không cần sửa gì thêm ở FE** cho phần Danh sách cột lương/dialog phê duyệt — `UpdateFormulaDialog.tsx`/
`TinhLuongExcel.tsx` đã viết đúng từ 250727, chỉ chờ BE trả đúng shape (nay đã đúng).

**Test:** `tsc --noEmit`/`eslint` sạch trên file sửa. Playwright thật (dev login, vào
`/v1/settings/approval-rules`, đổi dropdown): xác nhận gọi lại đúng
`GET /admin/approval-rules?entityType=salary_component_formula`, heading đổi đúng
"Cấu Hình Duyệt — Công thức cột lương". Script test tạm đã xoá sau khi kiểm.

### Việc CHƯA làm (đúng như đã ghi ở mục "KHÔNG làm trong đợt này" — nhắc lại cho rõ)
- "Duyệt của tôi" chưa có UI riêng hiển thị old/new formula cho entity_type mới (test bằng API xác
  nhận request LÊN ĐÚNG inbox, chỉ chưa đẹp khi hiển thị).
- Chưa viết unit test Go riêng cho `RequestUpdate`/`ApplyPendingChange` (chỉ verify bằng test thật
  qua API + SQL trực tiếp).
- Create/Delete/Reorder/ToggleVisible salary component vẫn áp dụng thẳng, không qua duyệt (đúng
  phạm vi đã chốt).

### Đã commit + push
- BE: `Core System-backend@bf6d90b` (tính năng), `Core System-backend@4c6930c` (fix bổ sung dưới đây).
- FE: `Core System-frontend@c6b15e0` (dropdown lọc trang), `Core System-frontend@dbc5416` (sửa entity_type
  của 1 rule qua modal Sửa).

## Bổ sung sau khi user hỏi lại "ý #1 đâu" — điểm còn thiếu thật

Dropdown cấp TRANG (đợt đầu) chỉ lọc "đang xem/tạo rule theo loại nào" — **không** cho sửa loại
đối tượng của 1 rule ĐÃ CÓ qua modal "Sửa" (không có field entityType trong `RuleFormState`).
Đây đúng là thiếu sót so với ý "bổ sung sửa type của rule trên giao diện" ban đầu.

**Đã bổ sung:**
- FE: thêm field `entityType` vào `RuleFormState` + `<Select>` trong modal, mặc định từ entityType
  trang khi Tạo mới, từ `rule.entityType` khi Sửa.
- **Phát hiện thêm 1 bug BE khi verify:** `ApprovalRuleRepo.Update()` (`approval_rule_repo.go`)
  câu `UPDATE approval_rules SET ...` **thiếu cột `entity_type`** — dù FE gửi đúng, BE âm thầm bỏ
  qua, rule giữ nguyên type cũ. Đã thêm `entity_type = $2` vào SET.

**Sự cố khi tự test (đã tự phát hiện + tự sửa ngay, ghi lại làm bài học):** Playwright test đầu
bấm "Sửa" vào dòng ĐẦU BẢNG (sort theo level) để verify — nhưng dòng đó là **1 rule THẬT đã có sẵn
từ trước** (2 dòng `payroll_record` level 1/2, tạo 25/08, không phải do tôi tạo), không phải rule
test mới tạo — đã lỡ đổi `entity_type` của rule thật đó thành `salary_component_formula`. Phát
hiện ngay khi xem `SELECT` sau test (thấy 3 dòng lạ thay vì 2 dòng cũ), **revert lại đúng giá trị
gốc** (`UPDATE ... SET entity_type='payroll_record' WHERE id=...`) + xoá 2 dòng rác do 2 lần chạy
test tạo ra, xác nhận lại đúng 2 dòng gốc còn nguyên. Verify lại phần entity_type-update bằng 1 rule
test **tách biệt hoàn toàn** (tạo bằng API, lấy đúng ID trả về, sửa đúng ID đó, xoá sau khi xong) —
không còn động vào dữ liệu có sẵn nữa.

**Bài học:** khi test trên UI có bảng liệt kê dữ liệu thật (không phải bảng trống mới dựng), PHẢI
tạo dữ liệu test có gắn danh tính riêng biệt (id trả về từ API, hoặc field dễ nhận diện) rồi thao
tác ĐÚNG bằng định danh đó — không dựa vào "dòng đầu tiên trong bảng" hay thứ tự hiển thị, vì bảng
có thể đã có dữ liệu thật từ trước sắp xen giữa.

## Sửa lại lần 2 — ý #1 thật ra là gì (đã hỏi lại `AskUserQuestion` để chốt, không đoán tiếp)

2 lần sửa trên (dropdown lọc trang + field entityType trong modal Sửa rule) đều nhắm vào
`approval_rules.entity_type` — VẪN SAI Ý. Người dùng gửi ảnh màn "Danh sách cột lương" và xác nhận:
"type của rule" = **`componentType`** (input/config/formula/system/manual) của CHÍNH 1 cột lương —
"rule lương" là cách gọi cột lương/công thức, không phải `approval_rules`.

**Vấn đề thật:** `componentType` chỉ chọn được lúc TẠO MỚI (`SalaryComponentModal` mode="add") —
sau khi tạo, không có đường nào mở lại modal ở mode="edit" để đổi lại (nút "Sửa" riêng đã bị bỏ từ
250727, lý do lúc đó: sửa-tại-chỗ ở ô Công thức/Tên đã đủ — nhưng bỏ sót rằng componentType không
nằm trong 2 ô sửa-tại-chỗ đó).

**Đã sửa** (`Core System-frontend@1294522`): thêm 1 nút "Sửa" nhỏ cạnh dòng "Loại" trong panel "Giải
thích công thức" (đúng chỗ trong ảnh người dùng gửi) — mở `SalaryComponentModal` ở mode="edit" (state
đã hỗ trợ sẵn variant này, chỉ thiếu nút gọi). Không thêm cột hành động thứ 2 cho bảng (cơ chế
`rowActions`/`actionKind` hiện chỉ hỗ trợ 1 hành động/sheet).

Verify Playwright thật: chọn `DIFF_DAYS` (đã kiểm `is_system=false` trước — rút kinh nghiệm từ lỗi
lần 1, KHÔNG chọn mù theo vị trí), bấm Sửa, đổi componentType `input`→`manual`, điền Lý do, Lưu →
PUT gửi đúng `componentType`, DB đổi đúng → **revert lại `input` ngay sau khi verify**, không có dữ
liệu thật nào bị thay đổi lâu dài.

Ghi nhận phụ (không sửa, ngoài phạm vi): đổi RIÊNG `componentType` (không kèm đổi formula/tên)
không được ghi vào `salary_component_history`/`salary_component_versions` — điều kiện ghi history
hiện chỉ check `old.Formula != comp.Formula || old.Name != comp.Name`. Nếu cần audit đổi loại cột,
đây là điểm cần bổ sung riêng sau.

## Bổ sung lần 3 — "Create cũng phải qua duyệt" (đã hỏi lại, user chọn CÓ)

Đã hỏi lại rõ (`AskUserQuestion`): Create (Thêm cột lương mới) có cần qua duyệt giống Update không
— trước đó chỉ là giả định của tôi, chưa xác nhận. User chọn CÓ.

**Thiết kế mở rộng** (`Core System-backend`, migration `20260826010000_...create.sql`):
- `salary_component_pending_changes.component_id` đổi thành nullable + thêm cột `action`
  (`create`|`update`) + `new_component_data` (jsonb, toàn bộ định nghĩa cột đề xuất tạo, chỉ dùng
  cho `action='create'`).
- `SalaryComponentService.RequestCreate` (entry point mới cho handler `Create`): 0 cấp duyệt cấu
  hình → `Create()` thẳng như cũ; ≥1 cấp → lưu `new_component_data` + `Submit()`, KHÔNG insert vào
  `salary_components`.
- `ApplyPendingChange` thêm nhánh `action="create"`: approved → gọi lại `Create()` thật (sinh ID
  MỚI tại lúc áp dụng, không sinh trước); rejected → không tạo gì.
- Hạn chế đã biết, ghi rõ trong code: 2 đề xuất `create` CÙNG mã cùng "pending" không bị chặn ở mức
  này (UNIQUE index chỉ chặn theo `component_id`, luôn NULL cho `create`) — an toàn vì UNIQUE(code)
  thật của `salary_components` sẽ chặn lúc apply, chỉ chưa báo sớm cho người duyệt thứ 2.

**Verify bằng test thật trên DB dev** (tạo/xoá sạch): Create khi có rule → trả `ApprovalRequest`,
component CHƯA tồn tại trong `salary_components` → duyệt → tạo thật đúng dữ liệu; đề xuất khác bị
Từ chối → không tạo gì. `go test ./...`: 836 passed / 0 failed (sau rebase, số tăng do các commit
khác của người khác đã merge vào `develop_v1` trong lúc này, không liên quan).

**Sự cố git khi commit (đã tự phát hiện + tự sửa):** nhánh feature cũ đã bị xoá sau khi MR trước
được merge (GitLab tự xoá source branch) — tôi commit nhầm trực tiếp lên `develop_v1` local mà
không nhận ra, và tại thời điểm đó `origin/develop_v1` đã tiến xa hơn local (có thêm việc của
người khác: "update/fix sync attendance summary"). Phát hiện ngay khi `git push` báo lỗi refspec
không khớp. Đã sửa: tách commit ra nhánh mới `feature/salary-formula-approval-workflow-create`,
`git reset --hard origin/develop_v1` để đưa `develop_v1` local về khớp đúng remote (không mất gì —
commit lạc chưa từng được push), rebase nhánh mới lên đúng `origin/develop_v1` hiện tại, build/test
lại sạch rồi mới push. Đã push: `Core System-backend@3be0ef4` trên nhánh
`feature/salary-formula-approval-workflow-create`.
