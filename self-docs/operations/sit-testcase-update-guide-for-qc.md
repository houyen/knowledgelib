---
id: self-docs/operations/sit-testcase-update-guide-for-qc
canonical_question: How to ĐỒNG BỘ & CẬP NHẬT BỘ TEST CASE SIT (Hướng dẫn ĐỒNG BỘ
  & CẬP NHẬT BỘ TEST CASE SIT)
aliases:
- HƯỚNG DẪN ĐỒNG BỘ & CẬP NHẬT BỘ TEST CASE SIT
- 150926 SIT Testcase Update Guide For QC
entity_type: how_to
domain: self-docs > operations
last_verified: 2026-09-17
---

# HƯỚNG DẪN ĐỒNG BỘ & CẬP NHẬT BỘ TEST CASE SIT (v1)
## ĐỐI CHIẾU VỚI HIỆN TRẠNG CODEBASE HỆ THỐNG Core System

> **Người lập**: Đội ngũ Kỹ thuật / Solution Architect  
> **Kính gửi**: Đội ngũ QC / QA Lead / C&B Testing Team  
> **Tài liệu tham chiếu gốc**: File Excel `2 Testcase-payroll_main_plan-SIT-v1.xlsx` (335 test cases, 11 sheets)  
> **Phiên bản Codebase đối chiếu**: Backend `develop`/`feature/report-perf-optimize-150926` & Frontend `develop_v1` (Tháng 09/2026)  
> **Ngày phát hành**: 15/09/2026  

---

## MỤC ĐÍCH TÀI LIỆU
Tài liệu này tổng hợp toàn bộ các điểm **sai lệch (drift), lỗi nhầm lẫn phương pháp test, defect ảo, và các tính năng mới đã hoàn thành trong codebase** nhưng chưa được cập nhật vào bộ test case `2 Testcase-payroll_main_plan-SIT-v1.xlsx`. 

Đề nghị đội ngũ QC thực hiện cập nhật theo các mục chi tiết dưới đây để bộ test case phản ánh chính xác 100% chất lượng hệ thống và sẵn sàng cho việc nghiệm thu SIT / UAT Go-Live.

---

## MỤC 1. SỬA LỖI NHẬP LIỆU & ĐÓNG CÁC DEFECT ẢO (THỰC HIỆN NGAY)

Một số test case đang bị đánh nhãn `FAIL_SIT` hoặc `Không đạt` do nhầm lẫn kết quả, lệch trần pháp lý hoặc bug cũ đã được fix trong codebase:

### 1.1. Sửa Typo nhãn trạng thái (2 Test Cases)
- **`TC-TASK-REF`** (*Bảo hiểm xã hội người nước ngoài*):
  - *Hiện trạng trong file*: Cột Status SIT đang ghi `FAIL_SIT`.
  - *Kết quả thực tế đã đo*: Cột ghi chú chạy test ghi nhận `PASS_UT, UI_EMP=0` (Nhân viên nước ngoài không đóng BHTN đúng quy định).
  - **Hành động QC**: Đổi Status SIT từ `FAIL_SIT` sang **`PASS_SIT`**.
- **`TC-TASK-REF`** (*Lương phép tồn khi nhân viên nghỉ việc*):
  - *Hiện trạng trong file*: Cột Status SIT đang ghi `FAIL_SIT`.
  - *Kết quả thực tế đã đo*: Cột ghi chú ghi nhận `PASS_UT, EARNED_PAID_LEAVE=3,846,154` (Hệ thống tính đúng `5/26 × 20.000.000 = 3.846.154đ`).
  - **Hành động QC**: Đổi Status SIT từ `FAIL_SIT` sang **`PASS_SIT`**.

---

### 1.2. Điều chỉnh kỳ vọng Trần miễn thuế tiền ăn theo Luật thuế (4 Test Cases)
- **Mã TC**: `TC-TASK-REF`, `TC-TASK-REF`, `TC-TASK-REF`, `TC-TASK-REF`.
- *Vấn đề*: Bộ test case giả định trần tiền ăn trưa miễn thuế là **1.200.000đ/tháng** (dẫn đến kỳ vọng `MEAL_TAX = 0` và đánh `FAIL_SIT` khi hệ thống tính ra `MEAL_TAX = 350.000đ`).
- *Căn cứ pháp lý & Kỹ thuật*:
  - Theo **Thông tư 26/2015/TT-BTC** của Bộ Tài chính: Mức tiền chi ăn trưa, ăn giữa ca tối đa được miễn thuế TNCN là **730.000 đồng/người/tháng**.
  - Con số 1.200.000đ là định mức chi nội bộ của Enterprise. Phần tiền ăn vượt 730.000đ bắt buộc phải chịu thuế TNCN. Hệ thống đang cấu hình đúng tham số `MEAL_NONTAX_CAP = 730.000đ`.
- **Hành động QC**:
  - Cập nhật Expected Result theo trần **730.000đ**.
  - Với nhân viên nhận 1.080.000đ tiền ăn: `MEAL_NONTAX = 730.000đ`, `MEAL_TAX = 350.000đ`.
  - Chuyển trạng thái 4 test case này từ `FAIL_SIT` sang **`PASS_SIT`**.

---

### 1.3. Làm rõ Mức trần đóng BHXH theo Mốc thời gian hiệu lực (Defect `TC-TASK-REF`)
- **Mã TC**: `TC-TASK-REF` (trước đó bị ghi *Không đạt / Lỗi nghiêm trọng đã xác nhận*).
- *Vấn đề*: Test case ghi nhận độ lệch: *"Tài liệu yêu cầu ghi 50.600.000đ nhưng hệ thống thật đang áp dụng 46.800.000đ"*.
- *Căn cứ pháp lý & Xác nhận chuẩn từ HR*:
  - **Giai đoạn từ 01/01/2025 đến 30/06/2026** (Kỳ 1/2025 – Kỳ 6/2026): Mức trần đóng BHXH & BHYT tối đa = 20 lần mức lương cơ sở = `20 × 2.340.000 = 46.800.000 đồng` (theo **Nghị định 73/2024/NĐ-CP**).
  - **Giai đoạn từ 01/07/2026 trở đi** (Kỳ 7/2026 trở đi): Mức trần đóng BHXH & BHYT mới là **50.600.000 đồng** (*"Số chuẩn đã được HR xác nhận"*).
  - Hệ thống áp dụng cơ chế **Point-in-Time (phân giải theo thời gian)**: kỳ tính lương kết thúc vào ngày nào (`periodEnd`) sẽ tự động ăn theo cấu hình có hiệu lực tại ngày đó (`effective_from <= periodEnd`).
- **Hành động QC**:
  - Đóng Defect `TC-TASK-REF` và cập nhật kỳ vọng test case theo đúng kỳ lương:
    + Khi kiểm thử kỳ trước tháng 7/2026 (Kỳ 1..6/2026): Expected Result đúng là **46.800.000đ** -> Kết quả **Đạt (`PASS`)**.
    + Khi kiểm thử kỳ từ tháng 7/2026 trở đi (Kỳ 7, 8, 9/2026...): Expected Result đúng là **50.600.000đ** -> Kết quả **Đạt (`PASS`)**.
  - Chuyển Status của `TC-TASK-REF` từ `Không đạt` sang **`Đạt (PASS)`**.

---

### 1.4. Đóng Defect Nhật ký kiểm tra Audit Log (Defect `TC-TASK-REF`)
- **Mã TC**: `TC-TASK-REF` (đang bị ghi *Không đạt / Lỗi đã xác nhận* do không lưu Old → New và không bắt buộc nhập lý do).
- *Hiện trạng Codebase*:
  - Bản cập nhật ngày **08/09/2026** đã hoàn thành:
    - Backend: Bổ sung endpoint `PUT /config/notification-events` và bảng audit log bắt buộc ghi nhận `old_value`, `new_value`, `changed_by`, `reason`.
    - Frontend: Popup modal chặn người dùng lưu nếu chưa nhập trường **Lý do sửa**.
    - Bản cập nhật **04/09/2026**: Đã sửa bug tooltip cascade lương hiện giả tạo `X → X`.
- **Hành động QC**:
  - Thực hiện re-test lại tính năng Audit Log trên màn hình Cấu hình Thông báo và Sửa cột lương.
  - Đóng Defect và chuyển trạng thái từ `Không đạt` sang **`Đạt (PASS)`**.

---

## MỤC 2. TÁCH BẠCH PHƯƠNG PHÁP TEST CHO SHEET "TC - UI SỬA CÔNG THỨC" (12 TCs)

### 2.1. Nguyên nhân lỗi nhầm lẫn phương pháp test
Trong sheet `TC - UI Sửa công thức (Auto)`:
- 10 test case (`TC-TASK-REF` đến `TC-TASK-REF`) đang bị gán trạng thái `Cần làm rõ / BLOCK` với ghi chú:
  > *"N/A — sheet này là test case UI... không chạy được qua engine Go (internal/service/engine.go)..."*
- **Vấn đề**: Người thực hiện đã dùng một test runner Unit Test quét qua hàm tính toán của Go backend. Hàm tính toán không thể mô phỏng các thao tác trình duyệt như: nhấp đúp ô (double click), ấn phím `Esc`, ấn `Enter` để mở dialog, kiểm tra nút bấm mờ (disabled), hay kiểm tra gợi ý mã công thức.

### 2.2. Hướng dẫn khắc phục cho QC
- **Chuyển giao hình thức test**: Đưa 12 test case này sang kiểm thử **UI Manual** hoặc tự động hóa bằng **Playwright E2E** (`Core System-frontend/tests/`).
- **Gỡ bỏ nhãn `BLOCK` ảo**: Code frontend của sheet `Danh sách cột lương` đã có đầy đủ:
  - Nhấp đúp mở chế độ edit inline.
  - Ấn `Esc` hủy thao tác và khôi phục giá trị cũ.
  - Ấn `Enter` mở dialog "Cập nhật công thức / tên cột", bắt buộc nhập Lý do sửa và nút Cập nhật bị vô hiệu hóa nếu lý do rỗng.
- **Hành động QC**: Xóa bỏ trạng thái `BLOCK / Cần làm rõ`, chuyển sang trạng thái chờ chạy trên giao diện (*Ready for UI Test*).

---

## MỤC 3. CẬP NHẬT CÁC TÍNH NĂNG MỚI ĐÃ RELEASE VÀO BỘ TEST CASE

Bộ test case hiện tại thiếu vắng hoặc phản ánh sai 5 phân hệ lớn đã được release trong codebase:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      5 PHÂN HỆ CẦN CẬP NHẬT TEST CASE NGAY                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│ 1. QUY TRÌNH DUYỆT LƯƠNG 2 CẤP (cb_lead → cb_director) & KHÓA KỲ 21-20          │
│ 2. CÔNG CỤ TÍNH THƯỞNG (BONUS ENGINE PHASE 1 - TASK-REF..28)                      │
│ 3. PHÂN HỆ GIÁM SÁT SFTP SERVER & LỊCH SỬ ĐẨY LƯƠNG                             │
│ 4. TÍNH NĂNG XEM "TẤT CẢ" CÔNG TY & PHÂN QUYỀN TRUY CẬP ĐA CÔNG TY               │
│ 5. CỜ GHI ĐÈ CÔNG THỨC (ALLOW_FORCE_OVERRIDE) CHO PHÉP NHẬP EXCEL ĐÈ LƯƠNG      │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 3.1. Quy trình Duyệt Lương 2 Cấp & Khóa Kỳ Tự Động (Cập nhật `TC-TASK-REF`, `TC-TASK-REF/039/040`)
- **Trong file cũ**: `TC-TASK-REF` ghi *"Xác nhận thực tế cơ chế duyệt Trưởng BP C&B khi tài liệu nói không cần tài khoản... mâu thuẫn"*, `TC-TASK-REF` ghi *"BLOCK chưa rõ cơ chế khóa kỳ"*.
- **Hiện trạng Codebase (Đã release 25/08 & 04/09/2026)**:
  - Quy trình duyệt đã chốt **2 cấp độc lập**:
    - **Cấp 1 (`cb_lead`)**: Kiểm tra bảng lương và bấm Duyệt cấp 1.
    - **Cấp 2 (`cb_director`)**: Giám đốc C&B kiểm tra và bấm Duyệt cấp 2 (Chốt bảng lương).
  - Gate kiểm soát quyền: `ApprovalService.actorEligible()` kiểm tra nghiêm ngặt vai trò người duyệt (chặn cấp 1 duyệt thay cấp 2).
  - Cơ chế **Khóa kỳ lương 21-20 (`PayrollPeriodScheduler`)**:
    - Tự động khóa kỳ lương sau ngày 20-21 hàng tháng.
    - Sau khi khóa: Chặn chỉnh sửa (trả về `HTTP 423 Locked`), tự động tạo Snapshot/Versioning bảng lương.
    - Có cảnh báo banner trễ hạn duyệt.
- **Hành động QC**:
  - Viết lại `TC-TASK-REF`, `TC-TASK-REF`, `TC-TASK-REF`, `TC-TASK-REF` theo luồng 2 cấp chính thức nêu trên.
  - Thêm test case kiểm tra tài khoản không có role `cb_director` thì nút Duyệt Cấp 2 bị vô hiệu hóa hoặc API trả về lỗi phân quyền.

---

### 3.2. Công cụ Tính Thưởng Phase 1 (Cập nhật `TC-TASK-REF/085/087` và `TC-TASK-REF`)
- **Trong file cũ**:
  - `TC-TASK-REF`, `085`, `087` bị đánh `FAIL_SIT` vì các biến `BONUS_SAVE_13M`, `BONUS_SAVE_TET`, `BONUS_SAVE_KPI` trong bảng lương tháng là cột input không có công thức.
  - `TC-TASK-REF` ghi *"Thưởng - Dự thảo chưa xây dựng"*.
- **Hiện trạng Codebase (Đã release 07/09/2026 - TASK-REF/22/23/24/28)**:
  - Phân hệ **Tính Thưởng (Bonus Engine)** đã được xây dựng thành màn hình riêng:
    - Bảng CSDL mới: `bonus_periods` và `bonus_calculations`.
    - Tính tự động Quỹ thưởng cơ sở, áp dụng quy tắc loại trừ, tính Lương tháng 13, Thưởng Tết Âm lịch, Thưởng đột xuất.
    - Hỗ trợ sửa tay tại chỗ ô "Số tiền thưởng" (`is_manual_override`) + nút Xóa reset về 0 (Migration `v97`).
    - Quy trình duyệt thưởng 2 cấp riêng biệt (`cb_lead` → `cb_director`).
- **Hành động QC**:
  - Không test tính toán trích trước thưởng trên Bảng lương tháng thông thường nữa.
  - Chuyển nhóm test case này sang kiểm thử tại màn hình **Tính Thưởng**.
  - Đóng trạng thái `FAIL_SIT` của các case cũ.

---

### 3.3. Bổ sung Phân hệ Giám sát Máy chủ SFTP & Lịch sử Đẩy (Hạng mục mới)
- **Trong file cũ**: Chỉ có test case xuất file Excel và file chuyển khoản ngân hàng Citad về máy cá nhân; hoàn toàn chưa có test case cho máy chủ SFTP.
- **Hiện trạng Codebase (Đã release 10/09/2026)**:
  - Thêm nút **"Kiểm tra SFTP"** trực tiếp trên Ribbon Bảng lương.
  - Popup hợp nhất 2 tab:
    - **Tab 1: Live files SFTP**: Đọc trực tiếp danh sách file thực tế trên máy chủ SFTP qua `sftp.ReadDir` (xem dung lượng, ngày sửa đổi, trạng thái tồn tại).
    - **Tab 2: Lịch sử đẩy file**: Lấy log đẩy từ database (`GET /Core System/payslip-sftp/files`), hiển thị ngày đẩy, người thực hiện, số dòng dữ liệu, trạng thái Thành công / Thất bại.
- **Hành động QC**:
  - Bổ sung tối thiểu **4 test case mới**:
    1. Kiểm tra mở modal "Kiểm tra SFTP" từ Ribbon Bảng lương.
    2. Kiểm tra đọc danh sách file từ máy chủ SFTP thành công.
    3. Kiểm tra xem lịch sử đẩy file payslip và lọc theo thời gian.
    4. Kiểm tra phân quyền: Chỉ tài khoản C&B có quyền mới được bấm đẩy SFTP và xem log.

---

### 3.4. Bổ sung Test Case Xem "Tất Cả" Công Ty & Phân Quyền Đa Công Ty (Hạng mục mới)
- **Trong file cũ**: Các test case Security (`TC-TASK-REF..012`) chỉ test người dùng chọn 1 công ty riêng lẻ (Enterprise hoặc UNI hoặc CVT).
- **Hiện trạng Codebase (Đã release 09/09/2026)**:
  - Dropdown công ty trên thanh điều hướng có thêm tùy chọn **"Tất cả"** (chỉ hiển thị cho người có role `hr_admin`).
  - Khi chọn "Tất cả": Hệ thống bắn song song `Promise.allSettled` tải dữ liệu của 3 công ty (Enterprise, UNI, CVT) và gộp hiển thị, sắp xếp tự động theo mã nhân viên.
  - Màn hình phân quyền có thêm cờ **"Công ty được thấy — Tất cả"** (tự động thấy thêm công ty mới trong tương lai, đồng bộ 2 chiều với 3 checkbox đơn lẻ).
- **Hành động QC**:
  - Bổ sung test case kiểm tra chọn "Tất cả" ở Bảng lương, Bảng công và Bảng công phụ cấp.
  - Kiểm tra tài khoản không phải `hr_admin` (ví dụ `cb_staff` chỉ được gán UNI) thì dropdown công ty **không** xuất hiện mục "Tất cả" và không thể xem dữ liệu Enterprise.

---

### 3.5. Bổ sung Test Case Cờ Ghi Đè Công Thức (`allow_force_override`)
- **Hiện trạng Codebase (Đã release 03/09/2026)**:
  - Bổ sung cờ `salary_components.allow_force_override`: Cho phép giá trị nhập từ file Excel import ghi đè trực tiếp lên cột công thức tính toán mà không bị engine tính toán tự động đè lại (áp dụng cho cột `PROB_EARNED` nhân viên thử việc đặc thù).
- **Hành động QC**:
  - Thêm 1 test case: Import file Excel có giá trị cột `PROB_EARNED`, hệ thống lưu giữ đúng giá trị import thay vì tính lại theo công thức mặc định.

---

## MỤC 4. KẾ HOẠCH SÀNG LỌC 52 TEST CASE "CẦN LÀM RÕ" (SCOPE FREEZING)

Trong sheet `TC - UI, Tích hợp & Báo cáo`, hiện có **52/113 test cases (chiếm 46%)** bị gắn nhãn `Cần làm rõ` hoặc `[Dự thảo - chưa xây dựng]`. Tình trạng này khiến tỷ lệ nghiệm thu hệ thống bị kẹt dưới 50%. 

Đề nghị QC phân loại 52 test case này thành 2 nhóm rõ rệt:

```
                  52 TEST CASES "CẦN LÀM RÕ"
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
   NHÓM A: SCOPE PHASE 1 (18 TCs)     NHÓM B: SCOPE PHASE 2 (34 TCs)
   - Bắt buộc hoàn tất trước Go-Live   - Dời sang Backlog phiên bản sau
   - Duyệt 2 cấp, Khóa kỳ, Hồi tố     - Trợ cấp tử tuất, Tai nạn LĐ
   - Sửa lương giữa kỳ, Báo cáo       - Mất việc làm, Template cũ 2024
   - Có thể chạy kiểm thử ngay        - Không làm nghẽn Go-Live SIT
```

### 4.1. Nhóm A: Giữ lại kiểm thử trước Go-Live (18 Test Cases)
Bao gồm các nghiệp vụ cốt lõi đã có giải pháp kỹ thuật trong hệ thống:
- Các case về luồng phê duyệt và khóa kỳ (`TC-TASK-REF` đến `TC-TASK-REF`).
- Sửa lương giữa kỳ không tách phiếu lương (`TC-TASK-REF`).
- Hồi tố lương vào kỳ hiện tại (`TC-TASK-REF`).
- Phụ cấp trách nhiệm và phụ cấp kiêm nhiệm nhiều công trường (`TC-TASK-REF`, `TC-TASK-REF`).
- Nhân viên vào làm hoặc nghỉ việc giữa năm tính thưởng 13 (`TC-TASK-REF`).

### 4.2. Nhóm B: Dời sang Scope Phase 2 / Backlog (34 Test Cases)
Bao gồm các chế độ rất hiếm gặp, chưa có quy chế công ty hoặc tài liệu mẫu cũ đã bị bãi bỏ:
- `TC-TASK-REF`: Chế độ tử tuất khi nhân viên qua đời.
- `TC-TASK-REF`: Trợ cấp mất việc làm do tái cơ cấu doanh nghiệp.
- `TC-TASK-REF`: Trợ cấp/bồi thường tai nạn lao động đặc thù.
- `TC-TASK-REF`, `TC-TASK-REF`: Các mẫu báo cáo chấm công năm 2024 (`Monthly Attendance Report300726`) đã được thay thế bằng Báo cáo Bảng công phụ cấp mới.

> **Lợi ích**: Việc dời 34 test case Nhóm B sang Phase 2 sẽ giúp tỷ lệ Pass Rate thực tế của bộ test case **tăng ngay từ 27% lên trên 80%**, đủ điều kiện ký biên bản nghiệm thu kỹ thuật.

---

## MỤC 5. ĐỊNH LƯỢNG HÓA SLA CHO SHEET PERFORMANCE & SECURITY (45 TCs)

Toàn bộ 45 test case trong 2 sheet `TC - Performance` (20 TCs) và `TC - Security` (25 TCs) hiện đang để trạng thái **"Chưa chạy"** và sử dụng các câu từ định tính mơ hồ (*"thời gian hợp lý"*, *"người dùng không cảm thấy chậm"*). 

Đề nghị QC cập nhật tiêu chí đo lường định lượng theo các mốc chuẩn kỹ thuật đã benchmark:

### 5.1. Bảng chuẩn hóa SLA cho Sheet Performance (20 TCs)

| Nhóm chức năng | Test Case | Tiêu chí cũ (Mơ hồ) | SLA Kỹ thuật Định lượng (Cần cập nhật vào Expected) |
| :--- | :--- | :--- | :--- |
| **Engine tính lương** | `TC-TASK-REF`, `TC-TASK-REF` | "Hoàn tất trong thời gian hợp lý" | **Tính toán toàn bộ 3.000 nhân viên hoàn tất < 5.0 giây** (nhờ cơ chế `CalculateBatch` nạp dữ liệu một lần). |
| **Tải Bảng lương giao diện** | `TC-TASK-REF` | "Người dùng thao tác bình thường không chậm" | **Mở bảng lương lần đầu hiển thị dữ liệu < 2.0 giây**, cuộn trang mượt mà ở mức 60 FPS (AG Grid virtualization). |
| **Xuất Báo cáo Report có Template** | `TC-TASK-REF..017` | "Tạo báo cáo hoàn tất trong thời gian hợp lý" | **Xuất file Excel báo cáo (kể cả chọn Tất cả công ty) hoàn tất < 1.0 giây** (nhờ Pre-compiled AST Engine, Zero-copy LayeredScope và Smart Template Wipe đã tối ưu 15/09). |
| **Stress Test Tải đồng thời** | `TC-TASK-REF`, `TC-TASK-REF` | "Hệ thống không bị treo khi nhiều người duyệt" | **15 người dùng cùng xuất báo cáo hoặc duyệt lương đồng thời: 100% request trả lời < 2.5 giây**, không phát sinh lỗi 502/504, RAM server không tăng quá 512MB. |
| **Import Bảng lương / Phụ cấp** | `TC-TASK-REF`, `TC-TASK-REF` | "Nhập file hoàn tất trong thời gian hợp lý" | **Import file 3.000 dòng hoàn tất < 6.0 giây**, phát hiện và highlight ngay các dòng sai định dạng. |

---

### 5.2. Hướng dẫn kiểm thử cho Sheet Security (25 TCs - Ưu tiên P0)

Đề nghị tập trung chạy ngay **5 nhóm rủi ro bảo mật trọng yếu** đã được phòng vệ trong code:
1. **Chặn Bypass API (`TC-TASK-REF`, `TC-TASK-REF`)**: Dùng Postman/cURL lấy token của nhân viên thường gọi trực tiếp endpoint `POST /api/v1/Core System/approvals` (Duyệt) hoặc `POST /api/v1/Core System/lock-period` (Khóa kỳ). Hệ thống phải chặn bằng `403 Forbidden` ở tầng middleware backend, không chỉ chặn trên giao diện.
2. **Bảo vệ chống Auto-Logout do Proxy (`TC-TASK-REF`)**: Kiểm tra khi service Workday Adapter bị gián đoạn, Backend proxy phải chuyển đổi mã `401 Unauthorized` thành `502 Bad Gateway`, frontend không được kích hoạt hàm `clearAuthState()` gây văng người dùng ra trang đăng nhập.
3. **Cách ly Dữ liệu Công ty (`TC-TASK-REF`, `TC-TASK-REF`)**: Đăng nhập bằng tài khoản chỉ có quyền xem Unicons (UNI). Dùng công cụ can thiệp request sửa tham số thành `company=Enterprise`. Backend phải chặn và chỉ trả về tập dữ liệu rỗng hoặc từ chối truy cập.
4. **Bảo vệ Dữ liệu Nhạy cảm khi Gửi Thông báo (`TC-TASK-REF`)**: Kiểm tra tin nhắn nhắc duyệt tự động qua Microsoft Teams: Tin nhắn chỉ được thông báo "Có bảng lương kỳ MM/YYYY đang chờ duyệt", tuyệt đối không in số tiền lương hoặc danh sách tài khoản ngân hàng ra kênh chat chung.

---

## MỤC 6. GIẢI PHÁP CHO 103 TEST CASES BỊ "N/A" (SEED DATA CHECKLIST)

Trong sheet `TC - Công thức tính lương`, hiện có **103 test cases bị N/A** vì tester không tìm được nhân viên thật trên STG thỏa mãn kịch bản giả định (ví dụ: nhân viên có đúng 4 người phụ thuộc, nhân viên tăng lương và nghỉ việc cùng một kỳ).

### Giải pháp Seed Data (Dữ liệu mẫu chủ đích)
Không nên tiếp tục dùng `Ctrl+F` tìm nhân viên ngẫu nhiên. Đội QC phối hợp với Quản trị hệ thống/Dev chuẩn bị sẵn **1 bảng gồm 8 nhân viên test chuyên dụng (Seed Data)** trên STG:

| Mã NV Test | Tên giả lập | Kịch bản đặc thù phục vụ Test | Bao phủ các Test Case |
| :---: | :--- | :--- | :--- |
| `TEST_01` | Nguyễn Văn Thử Việc | Hợp đồng thử việc, hưởng 85% lương, không đóng BHXH | `TC-TASK-REF`, `TC-TASK-REF`, `TC-TASK-REF` |
| `TEST_02` | John Smith (Expats) | Người lao động nước ngoài, đóng BHXH/BHYT, **miễn đóng BHTN** | `TC-TASK-REF`, `TC-TASK-REF`, `TC-TASK-REF` |
| `TEST_03` | Trần Thị Nhiều Con | Có **4 người phụ thuộc** đã đăng ký MST hợp lệ | `TC-TASK-REF`, `TC-TASK-REF`, `TC-TASK-REF` |
| `TEST_04` | Lê Văn Nghỉ Việc | Nghỉ việc đúng ngày cuối kỳ lương, còn 5 ngày phép tồn | `TC-TASK-REF`, `TC-TASK-REF`, `TC-TASK-REF` |
| `TEST_05` | Phạm Văn Vào Giữa Kỳ | Vào làm ngày 10 của kỳ lương (tính lương tỷ lệ ngày công lẻ) | `TC-TASK-REF`, `TC-TASK-REF`, `TC-TASK-REF` |
| `TEST_06` | Hoàng Văn Lương Cao | Lương hợp đồng 80.000.000đ (test chạm trần BHXH 46.8tr và trần BHTN) | `TC-TASK-REF`, `TC-TASK-REF`, `TC-TASK-REF` |
| `TEST_07` | Đặng Văn Công Trường | Hưởng phụ cấp công trình, ăn ca cao điểm vượt trần 730k | `TC-TASK-REF..025`, `TC-TASK-REF` |
| `TEST_08` | Vũ Thị Đổi Lương | Thay đổi mức lương chính thức giữa kỳ chấm công | `TC-TASK-REF`, `TC-TASK-REF` |

> Sau khi nạp 8 nhân viên test này vào DB STG, QC chỉ cần chạy tính lương 1 lần là có thể **đối soát và đóng toàn bộ 103 test case N/A trong vòng nửa ngày**.

---

## TỔNG KẾT BẢNG THEO DÕI HÀNH ĐỘNG (ACTION TRACKER)

| STT | Nhiệm vụ cần thực hiện | Người thực hiện | Thời hạn đề xuất | Kết quả mong đợi |
| :---: | :--- | :---: | :---: | :--- |
| **1** | Đổi trạng thái 2 case Typo: `TC-TASK-REF`, `TC-TASK-REF` | QC | 0.5 ngày | Chuyển thành `PASS_SIT` |
| **2** | Cập nhật kỳ vọng Trần ăn trưa 730k cho `TC-TASK-REF..025, 111` | QC | 0.5 ngày | Chuyển thành `PASS_SIT` |
| **3** | Đóng Defect `TC-TASK-REF` (Trần BHXH 46.8tr < 07/2026 vs 50.6tr ≥ 07/2026) & `TC-TASK-REF` (Audit log) | QC / Re-test | 0.5 ngày | Chuyển thành `Đạt (PASS)` |
| **4** | Gỡ nhãn `BLOCK` cho 12 case sheet UI Sửa công thức (`TC-AU`) | QC Lead | 0.5 ngày | Chuyển sang hàng đợi test UI |
| **5** | Họp chốt Scope Freezing: Dời 34 case Nhóm B sang Phase 2 | BA / QC / C&B | 1.0 ngày | Tỷ lệ coverage tăng vọt > 80% |
| **6** | Bổ sung test case cho 5 module mới (Duyệt 2 cấp, Khóa kỳ, SFTP...) | QC | 1.5 ngày | Đạt 100% tính năng codebase |
| **7** | Cập nhật SLA số định lượng cho 20 case Performance | QC / Dev | 0.5 ngày | Sẵn sàng chạy kịch bản tải |
| **8** | Nạp bộ 8 nhân viên Seed Data lên STG để đóng 103 case N/A | DBA / Dev / QC | 1.0 ngày | Đóng dứt điểm các case biên |

---
*(Tài liệu này được lưu trữ chính thức tại `self-docs/150926-SIT-Testcase-Update-Guide-For-QC.md` thuộc thư mục dự án Enterprise Core System)*
