---
id: self-docs/engine/sftp-payslip-integration-analysis
canonical_question: 'Technical guide and specification: Báo cáo Phân tích Tích hợp
  SFTP & Phiếu Lương  — 100926'
aliases:
- Báo cáo Phân tích Tích hợp SFTP & Phiếu Lương  — 100926
- SFTP Payslip Integration Analysis 100926
entity_type: how_to
domain: self-docs > engine
last_verified: 2026-09-17
---

# Báo cáo Phân tích Tích hợp SFTP & Phiếu Lương (Payslip) — 100926

> **Mục đích**: Rà soát và tài liệu hóa toàn diện danh sách tính năng, màn hình giao diện, kiến trúc kỹ thuật của luồng đẩy file phiếu lương (payslip) lên máy chủ SFTP (Workday Ingestion), cũng như hiện trạng việc truy cập máy chủ SFTP để kiểm tra danh sách file thực tế.

---

## I. Tổng quan Tính năng (Feature List)

Hệ thống quản lý và đẩy phiếu lương lên Workday SFTP bao gồm các khối chức năng chính sau:

| STT | Tính năng | Mô tả chi tiết | Vị trí xử lý |
|---|---|---|---|
| 1 | **Tạo phiếu lương (PDF)** | Sinh file PDF phiếu lương A4 cho từng nhân viên từ dữ liệu bảng lương đã duyệt (`empToPayslipRow`). | Node.js Server (`/api/payslips/generate`) & Chromium headless / html2pdf |
| 2 | **Đóng gói & Mã hoá PGP** | Đóng gói tất cả file PDF thành `payslips.zip`, sinh file `payslip_Manifest_<kỳ>.csv`, và mã hoá bằng PGP Public Key của Workday thành 2 file: `payslips.zip.pgp` và `payslip_Manifest_<YYYYMM>.csv.pgp`. | Node.js Server (`/api/payslips/package`) qua OpenPGP |
| 3 | **Cổng kiểm soát duyệt lương (Push Gate)** | Chặn bấm nút nếu: chưa chọn kỳ, chưa chọn công ty (chỉ hỗ trợ `Enterprise`, `UNI`, `CVT`), hoặc còn dòng lương chưa duyệt (`evaluatePushGate`). | Frontend (`payslip.ts`) |
| 4 | **Đẩy SFTP đơn phiên (Single-flight Push)** | Sử dụng Mutex phía Backend Go để đảm bảo tại một thời điểm chỉ có DUY NHẤT 1 lượt đẩy lên SFTP. Nếu có người khác đang đẩy sẽ từ chối với mã `HTTP 409 Conflict`. | Backend Go (`PayslipSFTPService.StartPush`) |
| 5 | **Đẩy theo luồng & Dung lượng lớn** | Hỗ trợ 2 luồng đẩy: qua REST Multipart `POST /push` (lưu file tạm, dung lượng lên tới 2GB) và WebSocket Stream `GET /upload-ws` (stream binary trực tiếp lên SFTP tránh tốn RAM). | Backend Go (`payslip_sftp_handler.go`, `payslip_sftp_upload_ws.go`) |
| 6 | **Giám sát tiến độ thời gian thực (WebSocket)** | Backend phát trạng thái (Status, Percent %, Message, FileName) qua WebSocket `/Core System/payslip-sftp/ws`. Mọi trình duyệt đang mở đều nhận được tiến độ đồng nhất. | Backend Go (`payslip_sftp.go`) ↔ FE (`HomeRibbon.tsx`) |
| 7 | **Xác minh tự động sau khi đẩy (SFTP Stat Verification)** | Ngay sau khi upload xong, Backend tự động gọi `sftp.Stat()` đọc lại kích thước (`Size`) và thời gian cập nhật (`ModTime`) trên SFTP để xác nhận file tồn tại và không bị file cũ ghi đè. | Backend Go (`verifyRemoteFile` trong `payslip_sftp.go`) |
| 8 | **Lưu vết Lịch sử & Kiểm toán (Audit Push Log)** | Ghi nhận chi tiết từng lượt đẩy vào DB PostgreSQL (`payslip_push_log`): Người thực hiện (email Azure AD), thời điểm bắt đầu/kết thúc, trạng thái, danh sách file, dung lượng thực tế trên SFTP. | DB PostgreSQL (`payslip_push_log`) |
| 9 | **Bộ công cụ CLI độc lập (`pgp-to-sftp`)** | Bộ script Python chạy ngoài (`1_build_payload.py`, `2_push_sftp.py`) hỗ trợ đóng gói, mã hoá và đẩy SFTP qua Jump Host `.68` kèm lệnh in bằng chứng (`SFTP EVIDENCE`). | Script Python (`Core System-backend/pgp-to-sftp`) |

---

## II. Màn hình & Giao diện Người dùng (UI Screens)

Hiện tại trên giao diện Web (`Core System-frontend`), tính năng phiếu lương và SFTP tập trung tại màn hình:
**Đường dẫn**: `/Core System` -> **Tab Bảng lương** (không hiển thị ở tab Chấm công hay Bảng công phụ cấp).

### 1. Ribbon "Phiếu lương" (`HomeRibbon.tsx`)
Nằm ngay sau nhóm ribbon "Phê duyệt":
- **Nút "Xem phiếu"**: Xem trước PDF của các dòng đang chọn (hoặc tất cả dòng đã duyệt) trên drawer xem nhanh.
- **Nút "Đẩy phiếu lương đi"**:
  - **Trạng thái bình thường**: Icon tài liệu + mũi tên xanh, nhãn "Đẩy phiếu lương đi".
  - **Trạng thái bị khoá (Disabled)**: Mờ đi (opacity 0.55), con trỏ `not-allowed`. Tooltip hiển thị lý do cụ thể theo thứ tự ưu tiên (ví dụ: *"Kỳ này chưa có dòng lương nào được duyệt"*, *"Còn 5/100 dòng chưa được duyệt"*...).
  - **Trạng thái đang đẩy (`uploading`)**: Nhãn đổi thành "Đang đẩy...", hiển thị thanh tiến độ progress bar (xanh dương, 0% - 100%) ngay dưới nhãn nút.
  - **Cảnh báo mất kết nối**: Nếu đứt kết nối WebSocket tới server, nhãn phụ màu cam *"mất kết nối"* xuất hiện.
  - **Trạng thái lỗi (`failed`)**: Chữ nhãn chuyển màu đỏ báo thất bại.

*(Lưu ý: Các nút cũ "Thay thế bảng lương UAT/PRD" và "Tải lên SFTP UAT/PRD" đã được ẩn trên Ribbon giao diện để tinh giản luồng làm việc thành 1 cú click duy nhất).*

### 2. Panel Thông báo & Nhật ký Hành động (`actionLog` / Chuông thông báo)
- Khi mở trang, frontend gọi `GET /api/v1/Core System/payslip-sftp/history` để nạp danh sách 50 lượt đẩy gần nhất từ DB vào nhật ký.
- Khi một lượt đẩy hoàn tất, WebSocket gửi tín hiệu `done`/`failed` -> Popup thông báo Toast xanh/đỏ xuất hiện trên màn hình và tự động ghi thêm 1 dòng vào lịch sử hành động.

---

## III. Kiến trúc Kỹ thuật & Luồng Hoạt động (How It Works)

### 1. Sơ đồ Luồng Đẩy Phiếu Lương (Data Flow)

```
[Người dùng bấm "Đẩy phiếu lương đi"]
         │
         ▼
[Frontend: evaluatePushGate] ──(Không đạt)──> Báo lỗi qua Tooltip/Toast
         │ (Đạt: Đã duyệt đầy đủ)
         ▼
[Next.js Server: POST /api/payslips/package]
   ├─ 1. Đọc các PDF phiếu lương đã sinh từ ổ đĩa (/data/payslips/...)
   ├─ 2. Đóng gói ZIP: payslips.zip
   ├─ 3. Tạo CSV Manifest: payslip_Manifest_YYYYMM.csv (Chuẩn Workday: Pay_Group ID, Worker ID, ngày cuối tháng)
   └─ 4. Mã hoá OpenPGP (Public key Workday) ──> trả về 2 file .pgp (Base64)
         │
         ▼
[Frontend: startPushToSftp] ──(Kèm JWT Azure AD)──> [Backend Go: POST /api/v1/Core System/payslip-sftp/push]
         │
         ▼
[Backend Go: PayslipSFTPService]
   ├─ 1. Kiểm tra Mutex Lock (Đang có ai đẩy không? Nếu có: trả 409 Conflict)
   ├─ 2. Ghi nhận mở lượt vào DB `payslip_push_log` (status: uploading)
   ├─ 3. Trả về HTTP 202 Accepted ngay lập tức (Xử lý nền Goroutine)
   ├─ 4. Mở kết nối SSH/SFTP tới máy chủ SFTP (HostKeyCallback check)
   ├─ 5. Ghi từng byte lên SFTP (phát % tiến độ qua WebSocket /ws)
   ├─ 6. [XÁC MINH] Gọi sftp.Stat() kiểm tra Size và ModTime của file trên SFTP
   ├─ 7. Cập nhật kết quả vào DB `payslip_push_log` (status: done / failed)
   └─ 8. Phát tín hiệu hoàn tất qua WebSocket tới mọi client
```

### 2. Cấu hình Kết nối SFTP (Môi trường & Biến ENV)
Thông số kết nối máy chủ SFTP được cấu hình qua các biến môi trường tại `Core System-backend/.env`:
- `PAYSLIP_SFTP_HOST`: `sftp.Enterprise.vn`
- `PAYSLIP_SFTP_PORT`: `22`
- `PAYSLIP_SFTP_USER`: `payrollsftp`
- `PAYSLIP_SFTP_KEY_PATH`: Đường dẫn SSH Private Key (ưu tiên 1)
- `PAYSLIP_SFTP_PASSWORD`: Mật khẩu tài khoản `payrollsftp` (fallback ưu tiên 2)
- `PAYSLIP_SFTP_DIR`: Thư mục đích UAT (mặc định: `/workday/uat/Core System/payslips`)
- `PAYSLIP_SFTP_DIR_PRD`: Thư mục đích PRD (mặc định: `/workday/prd/Core System/payslips`)

---

## IV. Hiện trạng Truy cập SFTP để Kiểm tra File (Inspect / List Files)

### 1. Phân biệt: "Lịch sử trong DB" vs "File thực tế trên SFTP"
Cần làm rõ sự khác biệt quan trọng giữa 2 khái niệm này:
- **Lịch sử đẩy (`payslip_push_log`)**:
  - Lưu trong cơ sở dữ liệu PostgreSQL của hệ thống.
  - Phản ánh: Ai đẩy, lúc nào, trạng thái lúc đẩy ra sao, kích thước file lúc đẩy xong ghi nhận được.
  - **Hạn chế**: Nếu sau đó một kỹ sư xóa file trên SFTP, hoặc hệ thống Workday tự động quét (ingest) và di chuyển file sang thư mục archive/xóa đi, thì DB local **hoàn toàn không biết**.
- **File thực tế trên SFTP Server (`sftp.ReadDir`)**:
  - Phản ánh trực tiếp những gì đang tồn tại trên máy chủ `sftp.Enterprise.vn`.
  - Cho biết chính xác: Thư mục `/workday/uat/Core System/payslips` hiện có bao nhiêu file, tên gì, dung lượng bao nhiêu byte, thời gian cập nhật lần cuối lúc nào.

### 2. Hiện trạng mã nguồn hiện nay
- **Đã có**:
  - **Script Python (`Core System-backend/pgp-to-sftp/2_push_sftp.py`)**: Đã có hàm `sftp.listdir_attr(D)` liệt kê toàn bộ file và in ra bảng `+============ SFTP EVIDENCE (GMT+7) ============+`. Tuy nhiên đây là script chạy thủ công qua terminal/CLI từ máy dev, đi qua SSH Tunnel `.68`.
  - **Backend Go**: Đã có kết nối SFTP hoàn chỉnh bằng thư viện `github.com/pkg/sftp` và hàm `client.Stat()`, nhưng **chỉ dùng nội bộ** để xác minh 1 file cụ thể sau khi upload xong.
- **Chưa có**:
  - **Backend Go CHƯA có REST API** cho phép client gọi để lấy danh sách file đang có trên thư mục SFTP (ví dụ: `GET /api/v1/Core System/payslip-sftp/files`).
  - **Frontend CHƯA có giao diện (UI)** để người dùng/HR/Admin xem danh sách file thực tế trên SFTP, kiểm tra xem file đã được Workday lấy đi chưa, hoặc tải file/xóa file thủ công nếu cần.

---

## V. Đề xuất Hướng Xử lý & Các Phương án Kỹ thuật

Dựa trên yêu cầu kiểm tra và quản lý file trên SFTP, dưới đây là các phương án thiết kế để người dùng cân nhắc và quyết định:

### Phương án A: Bổ sung API Xem Danh Sách File SFTP & Màn hình Trực Quan trên Web (Khuyến nghị)
- **Backend**:
  - Thêm endpoint `GET /api/v1/Core System/payslip-sftp/files?target=uat|prd`:
    - Mở phiên SFTP tới thư mục cấu hình (`/workday/...`).
    - Dùng `client.ReadDir(dir)` để đọc danh sách file thực tế.
    - Trả về JSON: `[{ name, size, modTime, isDir }]`.
    - Phân quyền: `requireAdminOrCB` + `requireView`.
  - (Mở rộng tùy chọn): Thêm endpoint `DELETE /api/v1/Core System/payslip-sftp/files/{filename}` để dọn dẹp file cũ khi cần.
- **Frontend**:
  - Thêm 1 nút nhỏ hoặc menu phụ tại nhóm "Phiếu lương" trên Ribbon: **"Kiểm tra SFTP"** (hoặc tab phụ trong Modal Lịch sử).
  - Mở ra một Modal/Drawer dạng **"Trình quản lý File SFTP"**:
    - Hiển thị bảng: Tên file, Dung lượng (KB/MB), Thời gian sửa đổi (GMT+7), Trạng thái (vừa đẩy / file cũ / file rác).
    - Có nút "Làm mới (Refresh)" để kiểm tra tức thì xem Workday đã quét và lấy file đi hay chưa.

### Phương án B: Giữ nguyên cơ chế Backend, chỉ xây dựng Script / Tool CLI kiểm tra nhanh
- Không can thiệp vào Web UI.
- Viết thêm lệnh CLI hoặc tool Go/Python độc lập (ví dụ `go run cmd/sftp-tool/main.go list` hoặc cập nhật `pgp-to-sftp`) để kỹ thuật viên chạy khi cần đối soát file trên SFTP.

### Phương án C: Kết hợp Modal "Lịch sử & Bằng chứng SFTP" (Hợp nhất)
- Nâng cấp phần xem Lịch sử (`history`):
  - Khi người dùng bấm xem chi tiết 1 lượt đẩy trong lịch sử, giao diện sẽ có tab:
    1. **Nhật ký hệ thống** (Dữ liệu từ DB `payslip_push_log`).
    2. **Hiện trạng trên máy chủ SFTP** (Gọi API đọc trực tiếp từ SFTP server theo thời gian thực).
  - Giúp HR và Kỹ thuật viên đối chiếu 1-1 giữa những gì hệ thống đã đẩy và những gì Workday đang nhìn thấy trên SFTP.

---

## VI. Kết luận & Điểm cần Xác nhận từ Người dùng

1. Người dùng có muốn xây dựng giao diện xem danh sách file trên SFTP trực tiếp trên web app `/Core System` hay chỉ cần script/công cụ nội bộ?
2. Có cần hỗ trợ cả 2 môi trường `UAT` và `PRD` khi kiểm tra danh sách file trên SFTP hay chỉ tập trung vào `UAT`?
3. Có cần thêm tính năng tải xuống (Download) hoặc xóa (Delete) file trực tiếp từ SFTP trên giao diện web hay không?

---

## VII. Quyết định Chốt: Phương án Hợp nhất (A + C)

> **Xác nhận từ Người dùng (10/09/2026)**:
> - **Vị trí nút**: Theo **Phương án A** (Nút độc lập `[Kiểm tra SFTP]` đặt trên Ribbon nhóm Phiếu lương).
> - **Nội dung Modal**: Theo **Phương án C** (Modal Hợp nhất 2 Tab: Tab 1 là *File thực tế trên SFTP*, Tab 2 là *Lịch sử đẩy từ DB*).

### 1. Chi tiết Kiến trúc Giải pháp

```
Ribbon: [Xem phiếu]  [Đẩy phiếu lương đi]  [Kiểm tra SFTP] ◄── Nút mới (Luôn sáng cho CB/Admin)
                                                  │
                                                  ▼
                     ┌────────────────────────────────────────────────────────┐
                     │ Modal: Giám sát Máy chủ SFTP & Lịch sử Đẩy             │
                     ├────────────────────────────────────────────────────────┤
                     │  [Tab 1: File trên SFTP (Realtime)]  [Tab 2: Lịch sử]  │
                     ├────────────────────────────────────────────────────────┤
                     │  • Môi trường: [UAT ▼]       [🔄 Làm mới]              │
                     │  • Host: sftp.Enterprise.vn:22 (/workday/uat/...)       │
                     │  • Danh sách file thực tế đọc từ sftp.ReadDir()        │
                     │  • Size, ModTime (GMT+7), Tag nhận diện                │
                     └────────────────────────────────────────────────────────┘
```

### 2. Kế hoạch Triển khai Kỹ thuật (Implementation Plan)

#### Bước 1: Backend Go (`Core System-backend`)
- **Service (`internal/service/payslip_sftp.go`)**:
  - Struct `SFTPRemoteFile`: `Name string`, `Size int64`, `ModTime time.Time`, `IsDir bool`.
  - Hàm `ListFiles(ctx context.Context, targetEnv string) ([]SFTPRemoteFile, error)`:
    - Mở kết nối SSH/SFTP qua `target.authMethods()` và `knownHostsCallback()`.
    - Gọi `client.ReadDir(target.Dir)`.
    - Trả về danh sách file sắp xếp theo `ModTime` giảm dần (mới nhất trước).
- **Handler (`internal/handler/payslip_sftp_handler.go`)**:
  - Endpoint `GET /Core System/payslip-sftp/files`:
    - Đọc query param `target` (`uat` hoặc `prd`).
    - Gọi `svc.ListFiles`.
- **Router (`internal/app/router.go`)**:
  - Đăng ký route `r.With(requireAdminOrCB, requireView).Get("/files", handlers.PayslipSFTP.Files)` trong group `/Core System/payslip-sftp`.
- **Unit Test**: Viết test case kiểm tra format và quyền truy cập.

#### Bước 2: Frontend Next.js (`Core System-frontend`)
- **API Client (`components-page/tinh-luong/payslip.ts`)**:
  - Thêm constant `PUSH_FILES_URL = "/api/v1/Core System/payslip-sftp/files"`.
  - Thêm hàm `fetchSFTPFiles(target: "uat" | "prd"): Promise<SFTPRemoteFile[]>`.
- **Component Modal mới (`components-page/tinh-luong/SFTPManagerModal.tsx`)**:
  - Tab 1 `live`: Hiển thị danh sách file trực tiếp từ SFTP server (kèm dropdown UAT/PRD, nút Làm mới, empty state giải thích khi Workday đã quét đi).
  - Tab 2 `history`: Hiển thị bảng lịch sử 50 lượt đẩy từ DB `payslip_push_log` (kèm chi tiết ai đẩy, số byte, thời gian xác minh).
- **Ribbon (`components-page/tinh-luong/HomeRibbon.tsx`)**:
  - Thêm nút `[Kiểm tra SFTP]` vào nhóm `grpPayslip` (icon máy chủ / cloud SFTP).
- **Trang chính (`components-page/tinh-luong/TinhLuongExcel.tsx`)**:
  - Khai báo state `sftpModalOpen` và gắn trigger mở modal khi bấm nút.

---
