---
id: self-docs/security/audit-log-compliance-plan
canonical_question: 'Technical guide and specification: Kế hoạch Thi hành: Nâng cấp
  Toàn diện Hệ thống Audit Log'
aliases:
- 'Kế hoạch Thi hành: Nâng cấp Toàn diện Hệ thống Audit Log'
- 160926 Audit Log Compliance PLAN
entity_type: how_to
domain: self-docs > security
last_verified: 2026-09-17
---

# Kế hoạch Thi hành: Nâng cấp Toàn diện Hệ thống Audit Log (160926)

**Goal:** Bổ sung cột "Lý do", Việt hóa cột "Hành động", hiển thị biến động "Cũ → Mới" tại cột "Chi tiết", và chuẩn hóa ghi nhận Audit Log đầy đủ ở cả Backend và Frontend theo đúng yêu cầu TASK-REF & kiểm toán tuân thủ.  
**Branch:** `feature/audit-log-compliance-160926` trên cả `Core System-backend` và `Core System-frontend`.  
**SPEC tham chiếu:** `self-docs/RBAC-Improvement-Analysis-160926.md`.

---

## 1. Danh sách các File Sửa đổi

### Backend (`Core System-backend`)
1. `internal/transport/http/auditlog/handler.go`:
   - Mở rộng `listItemOut` thêm `Reason *string` và `Summary *string`.
   - Bóc tách tự động `reason` và tạo `summary` thân thiện cho cả dữ liệu lịch sử.
2. `internal/repository/audit_log_repo.go`:
   - Cập nhật struct `AuditLogListItem` mang theo `Reason *string` và `Summary *string`.
3. `internal/service/approval_service.go`:
   - Lưu `comment` (lý do) vào audit log khi `Act` (Approve/Reject).
   - Bổ sung nạp thông tin nhân viên cho `payroll_record_version` trong `loadChangeDetail`.
4. `internal/service/payroll_service.go`:
   - Ghi kèm `empCode`, `componentCode`, `reason` trong audit log của `SetCell` và `UndoCell`.
5. `internal/service/payroll_bulk_cell_set.go`:
   - Ghi kèm `empCode`, `componentCode`, `reason` trong audit log của `BulkSetCells`.
6. `internal/service/sync_schedule.go`:
   - Ghi `NewValues` chứa tên tiếng Việt và mô tả tiến trình cho `LogAuditAction`.
7. `internal/service/role_service.go`:
   - Ghi kèm `RoleName` và `RoleCode` trong `logRoleAssignmentChange`.

### Frontend (`Core System-frontend`)
8. `lib/api/types.ts`:
   - Bổ sung `reason?: string; summary?: string;` vào interface `AuditLog`.
9. `lib/audit-log-summary.ts`:
   - Từ điển Việt hóa `ACTION_LABELS` và `MODULE_LABELS`.
   - Hàm `extractAuditReason` trích xuất lý do từ `details`.
   - Nâng cấp `summarizeAuditDetails` hiển thị dạng `[Cũ] → [Mới]`, đối tượng phân quyền, mô tả đồng bộ...
10. `lib/audit-log-summary.test.ts`:
    - Suite kiểm thử toàn diện cho các case định dạng, old/new, lý do, role assignment, cell edit.
11. `components-page/tinh-luong/TinhLuongExcel.tsx`:
    - Thêm cột `Lý do` (`_reason`) vào Grid "Nhật ký hệ thống".
    - Ánh xạ `action` sang tiếng Việt kèm badge hiển thị.
    - Cải tiến Modal "Chi tiết audit log" hiển thị bảng so sánh trực quan Cũ / Mới / Lý do.

---

## 2. Chi tiết Từng Bước Thi hành

- [ ] **Task 1: Backend - Tự động trích xuất Reason & Summary trong API `GET /audit-logs`**
  - Giúp toàn bộ dữ liệu lịch sử trong DB (kể cả trước đây) hiển thị được Lý do và Tóm tắt Cũ → Mới.
  - Viết helper hàm `extractAuditReasonAndSummary`.
  - Thêm unit test cho `handler.go`.

- [ ] **Task 2: Backend - Bổ sung đầy đủ thông tin khi ghi Audit Log tại các Services**
  - Cập nhật `ApprovalService.Act`: lưu `comment` vào `NewValues`.
  - Cập nhật `ApprovalService.Submit`: xử lý `payroll_record_version`.
  - Cập nhật `PayrollService.SetCell` / `UndoCell` / `BulkSetCells`: lưu `empCode`, `componentCode`, `reason`.
  - Cập nhật `SyncService.LogAuditAction`: lưu mô tả tiến trình đồng bộ tiếng Việt.
  - Cập nhật `RoleService.logRoleAssignmentChange`: lưu tên role tiếng Việt.

- [ ] **Task 3: Frontend - Nâng cấp Thư viện Tóm tắt `audit-log-summary.ts` & Unit Test**
  - Định nghĩa bảng map `ACTION_LABELS` và `MODULE_LABELS`.
  - Nâng cấp `summarizeAuditDetails` và `extractAuditReason`.
  - Bổ sung test cases trong `audit-log-summary.test.ts` (100% pass).

- [ ] **Task 4: Frontend - Thêm Cột Lý Do & Cải tiến Grid / Modal trong `TinhLuongExcel.tsx`**
  - Thêm cột `Lý do` (`_reason`) vào Grid cấu hình "Nhật ký hệ thống".
  - Hiển thị tên hành động tiếng Việt thân thiện.
  - Thiết kế lại Modal xem chi tiết có bảng Old vs New và ô Lý do nổi bật.

- [ ] **Task 5: Kiểm thử Toàn diện & Đối chiếu**
  - Chạy `go test ./...` trên backend.
  - Chạy `vitest run lib/audit-log-summary.test.ts` trên frontend.
  - Build test kiểm tra types: `tsc --noEmit` & `go build ./...`.
