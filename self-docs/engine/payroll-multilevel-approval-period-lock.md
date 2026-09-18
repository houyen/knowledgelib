---
id: self-docs/engine/payroll-multilevel-approval-period-lock
canonical_question: 'Technical guide and specification: Core System Multilevel Approval
  + Period Lock — 250826'
aliases:
- Core System Multilevel Approval + Period Lock — 250826
- Core System Multilevel Approval Period Lock 250826
entity_type: how_to
domain: self-docs > engine
last_verified: 2026-09-17
---

# Core System Multilevel Approval + Period Lock — 250826

**Canonical.** Tài liệu duy nhất cho hạng mục "luồng phê duyệt tính lương nhiều cấp + hạn chót
từng bước + hợp nhất khoá kỳ + version sau chốt", bắt đầu 2026-08-25. SPEC/PLAN gốc:
`llmwiki/wiki/sources/draft/250826-Core System-multilevel-approval-period-lock.md` (+ `-PLAN.md`).

## Yêu cầu gốc (4 việc)

1. Quy trình phê duyệt tính lương 2 cấp: C&B Staff tính lương → Trưởng bộ phận C&B kiểm tra
   (hạn 1 ngày) → C&B Head/Director phê duyệt cuối (hạn chậm nhất ngày 25 hàng tháng).
2. Khi Trưởng bộ phận chọn "Không duyệt" → trả về bước tính lương để sửa lại — tách bạch rõ
   với 2 nút Duyệt/Từ chối đơn cấp hiện có.
3. Cấu hình hạn chót theo từng bước + cảnh báo khi trễ hạn (popup đơn giản, chưa cần hệ thống
   notification).
4. Khoá/mở khoá kỳ: HR khoá kỳ thủ công → dừng đồng bộ Workday + chặn mọi thay đổi sau khi
   khoá. Không override — sửa sai đi qua truy thu kỳ sau + tạo 1 "version" Core System đã chỉnh
   sửa (đi qua lại đúng 2 cấp duyệt).

## 4 quyết định thiết kế đã chốt (AskUserQuestion, 2026-08-25)

- **Reject giữa chừng:** đóng request cũ (rejected) + tạo request MỚI khi trình duyệt lại —
  KHÔNG sửa semantics reject của `approval_service.Act` (vẫn terminate như thiết kế gốc).
- **Hạn ngày 25:** tính theo `period.end_date + N ngày` (không phải ngày 25 dương lịch cố
  định) — tự trượt nếu đổi lịch kỳ.
- **Version sau khoá:** đi qua lại đúng quy trình duyệt 2 cấp (không phải HR/Admin sửa tay +
  audit log đơn thuần).
- **Hợp nhất khoá kỳ:** `period.IsLocked` (khoá thủ công HR) phải chặn được cả
  approve/reject/calculate + đồng bộ Workday — hợp nhất với auto-lock lịch 21-20.

## 3 phát hiện làm tinh chỉnh cách thi hành (không phải SPEC sai)

Phát hiện lúc viết PLAN (đọc code thật, không suy đoán):

1. **`/Core System/approve/{id}` đã multiplex submit+act** qua `SubmitOrAct` — khi company đã có
   rule, actor không đủ quyền act ngay thì lỗi bị nuốt, trả 200 (thực chất chỉ SUBMIT). Đây
   đúng là vấn đề "detach" SPEC nêu.
2. **`/approvals/{id}/act` + trang `/v1/approvals` đã là bộ hành động đa cấp thật** — giảm khối
   lượng cần làm, chỉ cần thêm "Trình duyệt"/"Trình duyệt lại" tường minh.
3. **`AdapterSyncService` không ghi dữ liệu nào có `period_id`** (chỉ `employees`/
   `employee_work_histories`) — không có gì để "chặn theo từng kỳ". Diễn giải lại đúng ý gốc
   yêu cầu #4 ("dừng đồng bộ API"): **tạm dừng toàn bộ vòng đồng bộ** khi có bất kỳ kỳ nào
   đang khoá (kỳ lương là khái niệm toàn hệ thống, không theo công ty).

Phát hiện thêm khi viết code Task 5 (đọc `TinhLuongExcel.tsx` thật): cột "Trạng thái duyệt" đã
hiện đúng cấp/tổng cấp (`approvalLevel`/`approvalTotalLevels`, có từ 240726) — không có 2 bộ nút
tách biệt trong FE hiện tại để "detach", chỉ có 1 bộ nút dùng chung cho cả đường đơn cấp lẫn đa
cấp (thiết kế cố ý từ 240726). Lỗ hổng thật duy nhất: sau khi bị "Không duyệt", `showActions` cũ
(điều kiện `approval==="pending"`) tắt hẳn — **không có cách nào trình duyệt lại** từ ô đó. Đã
vá bằng nút "Trình duyệt lại" riêng.

## Đã triển khai (12 task, cả 2 repo, nhánh `sec_dev`)

**Backend (`Core System-backend`):**
- Task 1: migration cột `approval_rules.deadline_days_after_period_end`,
  `approval_steps.due_at` (cả atlas file lẫn Go-const idempotent trong `RunMigrations` — backend
  không tự chạy atlas apply, phải khai kép để đảm bảo áp dụng ở mọi môi trường) + 2 role mới
  `cb_lead`/`cb_director`.
- Task 2: seed `approval_rules` global (company/org_structure NULL) cho `payroll_record`, level
  1→`cb_lead` N=1, level 2→`cb_director` N=5. Dùng `NOT EXISTS` thay `ON CONFLICT` (NULL không bị
  unique constraint bắt trùng).
- Task 3: `resolveDueDate` trong `approval_service.go` — tính `due_at` khi tạo step (Submit),
  không đổi `Act`.
- Task 4: `GET /approvals/inbox` trả thêm `dueAt`/`isOverdue` (additive).
- Task 5: BE thêm `POST /approvals/submit` ("Trình duyệt" tường minh, không qua `SubmitOrAct`);
  FE thêm nút "Trình duyệt lại" khi `approval==="rejected"`.
- Task 6: FE banner + nhãn "Quá hạn" trên trang `/v1/approvals` (chỉ cảnh báo, không chặn).
- Task 7: hợp nhất khoá kỳ — `service.IsAnyPeriodLocked` OR thêm vào `checkLock()` của
  `PayrollHandler`/`AttendanceSummaryHandler`; vá lỗ hổng có sẵn (route Reject trước đây KHÔNG
  gọi `checkLock()` ở bất kỳ hình thức nào).
- Task 8: `AdapterSyncService.Run()` tạm dừng toàn bộ khi có kỳ đang khoá (xem phát hiện 3).
- Task 9: bảng `payroll_record_versions` + entity_type mới `payroll_record_version` tái dùng
  NGUYÊN chain rule của `payroll_record` trong `Resolve()` (không seed rule riêng).
- Task 10: route `POST/GET /Core System/{id}/versions` (tạo snapshot + tự động trình duyệt 2 cấp
  trong 1 request); FE nút "Tạo bản sửa" chỉ hiện khi `period.isLocked`.
- Task 11: `docs/routes-permissions.md` (2 repo) cập nhật.

## Test & trạng thái git

- `go test ./internal/...`: **1053 passed / 6 failed** — 6 fail xác nhận **tiền tồn tại** qua
  `git stash` trước mỗi lần commit (RLS permission-denied cục bộ, pipeline 502 do adapter ngoài
  không chạy local, 2 template-enforce edge-case, 1 seed test flaky theo thứ tự chạy) — **0 hồi
  quy** từ toàn bộ 10 task + 1 bugfix.
- `Core System-frontend`: `tsc --noEmit` 0 lỗi mới (3 lỗi pre-existing ở `public/backup/`), `eslint`
  sạch, `vitest` **109 passed / 2 failed** — 2 fail xác nhận tiền tồn tại (`payrollTemplateExport`,
  không liên quan).
- **Đã kiểm bằng Playwright click-through thật trên trình duyệt** (dev-login bypass qua
  `Authorization: Bearer dev`, gán tạm role `cb_lead`/`cb_director` cho tài khoản dev để test —
  đã xoá sau khi xong), chạy `go run ./cmd/Core System` + `npm run dev` local:
  - Luồng duyệt 2 cấp thật: submit → hiện "Cấp 1/2" + banner/nhãn "Quá hạn" đúng (Task 4/6) →
    click "Duyệt" thật (role `cb_lead`) → tiến "Cấp 2/2" → click "Duyệt" (role `cb_director`) →
    `payroll_records.approved_at` được set đúng (Task 1-4).
  - Nút "Trình duyệt lại" sau khi bị "Không duyệt" — hiện đúng, click gọi đúng
    `POST /approvals/submit` (201), dòng chuyển "Chờ duyệt (cấp 1/2)" (Task 5).
  - **Phát hiện + sửa 1 bug thật khi reload trang sau resubmit:** `payroll_records.rejected_reason`
    không được xoá khi trình duyệt lại → tải lại trang thì `deriveApproval()` ở FE (dựa vào
    `approvedAt`/`rejectedReason`/`status`, không biết gì về `approval_requests`) vẫn hiện "Từ
    chối" dù đã có request mới đang "pending". Sửa: xoá `rejected_reason` trong cùng transaction
    với `CreateRequestTx` khi `Submit` cho `entityType=payroll_record`. Thêm test
    `TestIntegrationResubmitClearsRejectedReason`, xác nhận lại bằng reload trình duyệt thật sau
    khi vá.
  - Khoá kỳ thủ công (`UPDATE payroll_periods SET is_locked=true`) → cả `POST /Core System/approve/{id}`
    VÀ `POST /Core System/reject/{id}` trả đúng `423 {"error":"locked_manual"}` — xác nhận qua `curl`
    VÀ qua click nút Duyệt/Từ chối thật trên UI (Promise.allSettled bắt lỗi per-row, không âm
    thầm coi là thành công, dòng giữ nguyên trạng thái).
  - Nút "Tạo bản sửa" — chỉ hiện khi kỳ khoá, click gọi đúng `POST /Core System/{id}/versions` (201),
    version + approval request 2 cấp tạo đúng, hiện đúng trên `/v1/approvals` với nhãn "Bản sửa
    bảng lương (sau khoá kỳ)" (Task 9/10).
  - Toàn bộ dữ liệu test (period/record/version/role tạm) đã dọn sạch khỏi DB dev sau khi kiểm —
    xác nhận bằng query đếm = 0.
- Nhánh: `sec_dev` cả 2 repo (BE tách từ `feature/Core System-period-schedule-gate` — giữ 7 commit
  của công việc 240826 mà PLAN này phụ thuộc trực tiếp; FE tách từ `develop`). **Chưa push, chưa
  merge.**
- Migration DB: đã áp lên DB dev local qua `psql` trực tiếp (theo lựa chọn user, không dùng
  `atlas migrate apply`) — cần áp lại đúng cách khi lên UAT/prod theo runbook chuẩn của dự án.

## Non-goals (đã chốt, không làm ở đợt này)

- Không tự động áp giá trị "version chính thức" vào kỳ lương kế tiếp — truy thu kỳ sau vẫn là
  thao tác tay của C&B Staff.
- Không có hệ thống notification/email/push cho cảnh báo trễ hạn.
- Không cho override trực tiếp payroll_record của kỳ đã khoá dưới bất kỳ hình thức nào.
- Không đổi cơ chế auto-lock theo lịch 21-20 đã có (chỉ hợp nhất điều kiện chặn).

## Việc kế tiếp

1. Kiểm tay UI trên trình duyệt thật (chưa có Playwright trong phiên này).
2. Viết tài liệu hướng dẫn sử dụng cuối-người-dùng (Task 12) — xem
   `self-docs/Huong-Dan-Su-Dung-Duyet-Luong-Khoa-Ky-250826.md`.
3. Xác nhận với user trước khi push/merge lên `develop`/UAT (chưa làm trong phiên này).
