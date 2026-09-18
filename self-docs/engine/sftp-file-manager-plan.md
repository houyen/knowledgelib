---
type: plan
title: SFTP-File-Manager-PLAN
status: proposed
timestamp: 2026-09-10
branch: feature/sftp-file-manager-100926
id: self-docs/engine/sftp-file-manager-plan
canonical_question: 'Technical guide and specification: Kế hoạch Thi hành: Giám sát
  Máy chủ SFTP & Lịch sử Đẩy Phiếu Lương'
aliases:
- 'Kế hoạch Thi hành: Giám sát Máy chủ SFTP & Lịch sử Đẩy Phiếu Lương'
- 100926 SFTP File Manager PLAN
entity_type: how_to
domain: self-docs > engine
last_verified: 2026-09-17
---

# Kế hoạch Thi hành: Giám sát Máy chủ SFTP & Lịch sử Đẩy Phiếu Lương (Hợp nhất A + C)

**Goal:** Xây dựng tính năng kiểm tra trực tiếp danh sách file trên máy chủ SFTP (Workday) và xem lịch sử các lượt đẩy phiếu lương trong một Modal hợp nhất, mở bằng nút `[Kiểm tra SFTP]` độc lập trên Ribbon Bảng lương.
**Architecture:** 
- Backend Go: Bổ sung API `GET /api/v1/Core System/payslip-sftp/files?target=uat|prd` sử dụng thư viện `pkg/sftp` gọi `client.ReadDir()` đọc realtime từ SFTP server.
- Frontend Next.js: Nút `[Kiểm tra SFTP]` trên `HomeRibbon.tsx` mở `SFTPManagerModal.tsx` gồm 2 Tab: Tab 1 "File trên SFTP" (Realtime) và Tab 2 "Lịch sử đẩy" (DB `payslip_push_log`).
**Tech stack:** Golang, Chi Router, `pkg/sftp`, Next.js 14, React 18, Tailwind, Vitest, Playwright E2E.
**SPEC nguồn:** `self-docs/SFTP-Payslip-Integration-Analysis-100926.md`

---

## 1. Global Constraints & Nguyên tắc Bắt buộc
1. **Bảo mật (RBAC)**: Endpoint `/files` yêu cầu quyền `requireAdminOrCB` và `requireView`. Tuyệt đối không để lộ mật khẩu hay private key trong response.
2. **Khả năng chịu lỗi (Resilience & Timeout)**: Kết nối SFTP phải có timeout (tối đa 15s). Nếu SFTP server không thể kết nối hoặc sai thông tin xác thực, phải trả về lỗi JSON 502/504 thân thiện kèm thông báo tiếng Việt, không để goroutine treo hoặc crash process.
3. **Múi giờ**: Thời gian sửa đổi file (`ModTime`) phải hiển thị theo múi giờ Việt Nam (`GMT+7`).
4. **Không breaking change**: Giữ nguyên toàn bộ cơ chế đẩy phiếu lương hiện tại (`/push`, `/ws`, `/status`, `/history`).

---

## 2. File Structure

### Backend (`Core System-backend`)
- Sửa: `internal/service/payslip_sftp.go` — Thêm struct `SFTPRemoteFile` và method `ListFiles(ctx context.Context, targetEnv string) ([]SFTPRemoteFile, error)`.
- Sửa: `internal/handler/payslip_sftp_handler.go` — Thêm method `Files(w http.ResponseWriter, r *http.Request)`.
- Sửa: `internal/app/router.go` — Đăng ký route `GET /Core System/payslip-sftp/files`.
- Tạo mới: `internal/service/payslip_sftp_list_test.go` — Unit tests cho logic parse file, sort theo ModTime, và map DTO.

### Frontend (`Core System-frontend`)
- Sửa: `components-page/tinh-luong/payslip.ts` — Thêm interface `SFTPRemoteFile` và hàm `fetchSFTPFiles(target: "uat" | "prd")`.
- Tạo mới: `components-page/tinh-luong/SFTPManagerModal.tsx` — Modal hợp nhất 2 tab: Tab 1 Live SFTP Files, Tab 2 Database Push History.
- Sửa: `components-page/tinh-luong/HomeRibbon.tsx` — Thêm prop `onOpenSFTPManager` và nút `[Kiểm tra SFTP]` vào nhóm `grpPayslip`.
- Sửa: `components-page/tinh-luong/TinhLuongExcel.tsx` — Thêm state `sftpModalOpen`, xử lý callback mở modal và mount component `SFTPManagerModal`.
- Tạo mới: `e2e/sftp-manager-modal.spec.ts` — Bộ test Playwright tự động hoá toàn diện.

---

## 3. Danh sách Task Chi tiết

### Task 1: Backend — Thêm Service `ListFiles`, Handler `Files` và Route `GET /files`
- **Files**:
  - Sửa `internal/service/payslip_sftp.go`
  - Sửa `internal/handler/payslip_sftp_handler.go`
  - Sửa `internal/app/router.go`
  - Test: `internal/service/payslip_sftp_list_test.go`
- **Interfaces**:
  - `SFTPRemoteFile`: `{ Name: string, Size: int64, ModTime: time.Time, IsDir: bool }`
  - `ListFiles(ctx context.Context, targetEnv string) ([]SFTPRemoteFile, error)`
  - Endpoint: `GET /api/v1/Core System/payslip-sftp/files?target={uat|prd}`
- **Test Cases Unit Test (Go)**:
  - `TestSFTPRemoteFilesSortByModTime`: Kiểm tra danh sách file được sắp xếp đúng thứ tự thời gian mới nhất lên đầu.
  - `TestSFTPTargetResolution`: Kiểm tra chọn đúng thư mục UAT (`/workday/uat/...`) hoặc PRD (`/workday/prd/...`).
  - `TestSFTPFilesHandlerValidation`: Kiểm tra handler từ chối target không hợp lệ với HTTP 400.
- **Verification**: `cd Core System-backend && go test -v ./internal/service -run TestSFTP`

---

### Task 2: Frontend Client — API Helper & Type Definitions
- **Files**:
  - Sửa `components-page/tinh-luong/payslip.ts`
  - Test: `components-page/tinh-luong/payslip_sftp_files.test.ts`
- **Interfaces**:
  - `export interface SFTPRemoteFile { name: string; size: number; modTime: string; isDir: boolean; }`
  - `export async function fetchSFTPFiles(target: PayslipTarget = "uat"): Promise<SFTPRemoteFile[]>`
- **Test Cases Unit Test (Vitest)**:
  - `TestFormatBytes`: Format byte thành KB / MB chính xác.
  - `TestFormatModTimeVN`: Parse ISO string sang định dạng ngày giờ GMT+7.
  - `TestFetchSFTPFilesSuccess`: Gọi đúng URL và header JWT, nhận dữ liệu đúng schema.
- **Verification**: `cd Core System-frontend && pnpm test components-page/tinh-luong/payslip_sftp_files.test.ts`

---

### Task 3: Frontend UI — Modal `SFTPManagerModal.tsx` & Nút Ribbon `[Kiểm tra SFTP]`
- **Files**:
  - Tạo mới `components-page/tinh-luong/SFTPManagerModal.tsx`
  - Sửa `components-page/tinh-luong/HomeRibbon.tsx`
  - Sửa `components-page/tinh-luong/TinhLuongExcel.tsx`
- **Chi tiết giao diện**:
  - **Nút trên Ribbon**: Nằm cạnh nút "Đẩy phiếu lương đi", icon máy chủ / đám mây SFTP, nhãn "Kiểm tra SFTP", tooltip "Xem danh sách file thực tế trên máy chủ SFTP Workday và lịch sử các lượt đẩy".
  - **Modal**:
    - Header: Tiêu đề "Giám sát Máy chủ SFTP & Lịch sử Đẩy" kèm nút đóng `[✕]`.
    - Tab Bar: 
      - Tab 1: `File trên máy chủ SFTP (Live)` (Active mặc định).
      - Tab 2: `Lịch sử đẩy lương (Database Log)`.
    - Tab 1 Content:
      - Toolbar: Chọn môi trường (UAT/PRD) + Nút `[🔄 Làm mới]` + Text hiển thị đường dẫn SFTP hiện tại.
      - Loading skeleton khi đang fetch.
      - Error banner nếu không kết nối được SFTP (nêu rõ lý do).
      - Bảng file: Tên file, Dung lượng (KB/MB), Thời gian sửa đổi (`GMT+7`), Badge trạng thái (Vừa đẩy / Khớp kỳ YYYYMM).
      - Empty state: Hướng dẫn thân thiện khi thư mục rỗng.
    - Tab 2 Content:
      - Bảng lịch sử gọi từ `fetchPushHistory(50)`: Thời gian, Người thực hiện, Trạng thái (Done/Failed), Tên file, Dung lượng xác minh (`remote_bytes`).
- **Verification**: Typecheck `cd Core System-frontend && pnpm tsc --noEmit`

---

### Task 4: Tự động hóa Kiểm thử E2E Playwright
- **Files**:
  - Tạo mới `e2e/sftp-manager-modal.spec.ts`
- **Danh sách Test Cases E2E**:
  - **TASK-REF**: Nút `[Kiểm tra SFTP]` hiển thị trên HomeRibbon ở tab Bảng lương (không hiển thị ở tab Chấm công).
  - **TASK-REF**: Click nút `[Kiểm tra SFTP]` mở Modal thành công, mặc định active Tab 1 ("File trên máy chủ SFTP").
  - **TASK-REF**: Tab 1 hiển thị đầy đủ Toolbar (dropdown UAT/PRD, nút Làm mới, đường dẫn server).
  - **TASK-REF**: Bảng danh sách file hiển thị đúng cấu trúc cột (Tên file, Dung lượng, Cập nhật, Ghi chú).
  - **TASK-REF**: Bấm chuyển sang Tab 2 ("Lịch sử đẩy lương") hiển thị đúng danh sách các lần đẩy trong quá khứ.
  - **TASK-REF**: Chuyển đổi môi trường từ UAT sang PRD kích hoạt gọi API với `target=prd`.
  - **TASK-REF**: Đóng modal thành công bằng nút `[✕]` hoặc phím `Escape`.
- **Verification**: `cd Core System-frontend && npx playwright test e2e/sftp-manager-modal.spec.ts`

---
