---
id: self-docs/integration/attendance-export-all-fix
canonical_question: 'Technical guide and specification: Kế hoạch xử lý: Sửa lỗi không
  xuất được file khi chọn ALL Bảng công — 090926'
aliases:
- 'Kế hoạch xử lý: Sửa lỗi không xuất được file khi chọn ALL Bảng công — 090926'
- Attendance Export All Fix 090926
entity_type: troubleshooting
domain: self-docs > integration
last_verified: 2026-09-17
---

# Kế hoạch xử lý: Sửa lỗi không xuất được file khi chọn ALL Bảng công — 090926

**File canonical**: `self-docs/Attendance-Export-All-Fix-090926.md`  
**Ngày lập**: 09/09/2026  
**Nhánh làm việc**: `feature/attendance-export-all-fix-090926` (`Core System-frontend`), `feature/attendance-export-cached-xlsx-090926` (`Core System-adapter`)

---

## 1. Tóm tắt vấn đề & Nguyên nhân gốc rễ

### A. Hiện tượng:
- Khi mở modal **"Chọn công ty/phòng ban để xuất Excel"** tại Sheet Bảng công ("Monthly Attendance 09/2026"), chọn 1 công ty (`Enterprise`) và chọn **ALL 307 phòng ban**:
- Bấm nút **"Xuất Excel"**: Nút chuyển sang *"Đang xuất..."*, sau một khoảng thời gian thì quay trở về *"Xuất Excel"*. Modal không đóng, không có file Excel nào được tải về, và không có thông báo lỗi nào trên giao diện.

### B. Nguyên nhân kỹ thuật:
1. **Định tuyến gọi Adapter gốc**: `exportRoute.ts` coi việc chọn toàn bộ 307/307 phòng ban là "không lọc phòng ban", định tuyến sang `route.adapter = true` để lấy file gốc chuẩn Workday từ adapter thay vì dựng lại trên client.
2. **Server-side Timeout (504) / Render Busy (503) / OOM (502)**:
   - Adapter khi nhận `format=xlsx` bị ép chạy truy vấn LIVE 20+ bảng DB cho ~3,000 nhân viên (tốn 40s+), sau đó Excelize tạo 500,000 cell tuần tự tốn ~1.2GB RAM.
   - Nginx / Ingress trên STG có timeout 60s -> Ngắt kết nối trả về `504 Gateway Timeout`.
   - Adapter có khóa đơn luồng `maxConcurrentRenders = 1` -> Trả về `503 Service Unavailable` nếu đang có request khác chạy.
3. **Frontend nuốt lỗi im lặng (Silent Error Swallowing)**:
   - Trong `TinhLuongExcel.tsx`, hàm `confirmExportCompanyModal` gọi `api.downloadAdapterAttendance` trong khối `try { ... } finally { ... }` mà **hoàn toàn không có khối `catch (err)`**.
   - Khi API ném lỗi (504/503/502), exception bị unhandled: modal không đóng, không có toast báo lỗi, nút bấm chỉ bị reset về trạng thái ban đầu trong `finally`.

---

## 2. Kế hoạch thi hành (Action Plan)

### Task 1: Bổ sung Bắt lỗi & Fallback thông minh ở Frontend (`Core System-frontend`)
*Mục tiêu: Đảm bảo người dùng luôn biết chuyện gì xảy ra và LUÔN NHẬN ĐƯỢC FILE EXCEL dù server có bị timeout.*

1. **Bổ sung `try...catch` trong `confirmExportCompanyModal`**:
   - Bắt mọi lỗi ngoại lệ khi gọi `downloadAdapterAttendance` / `downloadAdapterTimesheet`.
   - Phân loại lỗi:
     - Nếu lỗi 504 (Timeout) hoặc 503 (Máy chủ bận): Báo thông báo rõ ràng cho người dùng.
2. **Cơ chế Fallback tự động xuất từ dữ liệu màn hình (Client-side Rebuild)**:
   - Nếu gọi file gốc từ Adapter thất bại do Timeout (504) hoặc Máy chủ bận (503) hoặc Lỗi mạng:
     - Tự động chuyển tiếp sang nhánh xuất client-side bằng `exceljs` từ dữ liệu grid (`view` / `data.adapterAttendance`) đã nạp sẵn trên trình duyệt.
     - Hiển thị Toast thông báo:
       *"Máy chủ tạo file gốc quá thời gian chờ (Timeout). Đã tự động xuất bản xem trước từ dữ liệu màn hình ({written} dòng)!"*
     - Tải file về máy cho người dùng và đóng modal thành công.
3. **Thêm tùy chọn "Xuất nhanh từ màn hình" trên Modal khi chọn ALL**:
   - Khi chọn số lượng phòng ban lớn (hoặc chọn ALL): Cảnh báo rõ ràng và cho phép người dùng chủ động chọn xuất nhanh từ màn hình hoặc xuất file gốc.

### Task 2: Tối ưu hoá phía Adapter (`Core System-adapter`)
*Mục tiêu: Giảm thời gian query từ ~40s xuống ~0.2s khi xuất file Excel từ Adapter.*

1. **Cho phép `isXLSX` sử dụng dữ liệu Precomputed (`LoadCached`)**:
   - Tại `Core System-adapter/internal/api/attendance.go` và `timesheet.go`:
   - Hiện tại: Khi `isXLSX = true`, code bỏ qua `LoadCached` và ép chạy `Load` LIVE.
   - Sửa lại: Nếu không truyền `cached=false`, ưu tiên gọi `monthlyattendance.LoadCached(...)`. Nếu kỳ đó đã precomputed, dữ liệu được trả về trong ~0.2 giây, tránh hoàn toàn 20+ câu query live nặng nề.
   - Nếu chưa có precompute, `LoadCached` tự động rơi về `Load` an toàn như cũ.

### Task 3: Kiểm chứng & Đo đạc (Verification)
1. Kiểm tra unit test và build trên cả `Core System-frontend` và `Core System-adapter`:
   - `vitest run` trên frontend.
   - `go test` trên adapter.
2. Kiểm thử kịch bản:
   - Kịch bản 1: Giả lập adapter timeout -> Frontend tự động bắt lỗi và fallback xuất file client-side thành công, người dùng nhận được file.
   - Kịch bản 2: Khi adapter hoạt động bình thường với cache -> tải file gốc thành công nhanh chóng.

---

## 3. Kết quả triển khai & Kiểm chứng thực tế

### A. Chi tiết thay đổi code:
1. **`Core System-frontend/components-page/tinh-luong/TinhLuongExcel.tsx`**:
   - Bổ sung khối `try ... catch (adapterErr)` lồng bên trong nhánh `if (route.adapter)`. Nếu adapter thất bại (504 Timeout, 503 Render Busy, 502 Bad Gateway hoặc ngắt mạng):
     - Log warning chi tiết vào console.
     - Hiện `toast.warning`: thông báo máy chủ quá hạn chờ hoặc đang bận và hệ thống đang tự động xuất bản từ dữ liệu màn hình.
     - Tự động tiếp tục chạy xuống khối `exceljs` để xuất file từ `view` thay vì abort.
   - Thêm khối `catch (outerErr)` bao quát bên ngoài để đảm bảo mọi ngoại lệ không bị nuốt im lặng, luôn bắn `toast.error`.
   - Bổ sung thông điệp hướng dẫn màu xanh thân thiện trong modal khi chọn toàn bộ phòng ban: *"Đang chọn toàn bộ {N} phòng ban: Hệ thống ưu tiên tải file chuẩn Workday từ máy chủ; nếu máy chủ quá thời gian chờ (timeout), hệ thống sẽ tự động xuất bản từ dữ liệu màn hình để bạn luôn nhận được file."*
2. **`Core System-adapter/internal/api/attendance.go`**:
   - Sửa hàm `attendanceHandler`: Cho phép `format=xlsx` tận dụng `monthlyattendance.LoadCached(ctx, pool, ...)` khi không truyền `cached=false` (mặc định), thay vì ép chạy live query 20+ bảng. Khi kỳ đã precomputed, tốc độ nạp dữ liệu giảm từ ~40 giây xuống dưới 1 giây.

### B. Kết quả kiểm chứng:
- **`Core System-frontend` Vitest**: `vitest run` pass **278/278 tests (35 test files)**. `tsc --noEmit` không phát sinh lỗi mới.
- **`Core System-adapter` Go test**: `go test ./...` pass toàn bộ các packages (`internal/api`, `internal/report/...`).
- **`Core System-frontend` Playwright E2E (`e2e/attendance-export-fallback.spec.ts`)**: Pass **4/4 tests (11.5s)**:
  1. `✓ 1. Mở modal xuất Excel tại sheet Monthly Attendance và thấy thông tin đầy đủ kèm ghi chú >50 phòng ban (1.2s)`: Kiểm tra giao diện modal hiển thị đủ danh sách công ty, 55 phòng ban, và banner cảnh báo thông minh màu xanh.
  2. `✓ 2. Tự động Graceful Fallback sang xuất màn hình khi Adapter bị lỗi 504 Gateway Timeout (4.1s)`: Giả lập 504 Timeout khi gọi adapter, hệ thống bắt lỗi, bắn toast cảnh báo và tự động fallback sang client-side rebuild, người dùng nhận được file `.xlsx`, modal tự đóng.
  3. `✓ 3. Tự động Graceful Fallback khi Adapter bị lỗi 503 Service Unavailable (Render Busy) (3.5s)`: Giả lập 503 Busy từ adapter, hệ thống tự động fallback sang xuất dữ liệu màn hình, tải file thành công, modal tự đóng.
  4. `✓ 4. Xuất file gốc từ Adapter thành công khi Adapter phản hồi 200 OK (2.4s)`: Giả lập adapter trả về 200 OK kèm file chuẩn, tải đúng file `attendance_2026-09.xlsx`, bắn toast xác nhận file gốc từ adapter.
