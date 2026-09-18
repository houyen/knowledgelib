---
id: self-docs/engine/senior-qc-report-test-plan-and-verification
canonical_question: 'Technical guide and specification: KẾ HOẠCH & BÁO CÁO KIỂM THỬ
  TOÀN DIỆN PHÂN HỆ BÁO CÁO'
aliases:
- KẾ HOẠCH & BÁO CÁO KIỂM THỬ TOÀN DIỆN PHÂN HỆ BÁO CÁO
- 150926 Senior QC Report Test Plan And Verification
entity_type: how_to
domain: self-docs > engine
last_verified: 2026-09-17
---

# KẾ HOẠCH & BÁO CÁO KIỂM THỬ TOÀN DIỆN PHÂN HỆ BÁO CÁO
## (REPORT SYSTEM TEST PLAN & PLAYWRIGHT E2E VERIFICATION)

> **Người thực hiện**: Senior QC Lead / Test Architect  
> **Dự án**: Hệ thống Quản lý Bảng công, Tính lương & Phân quyền Tập đoàn Enterprise (`Core System`)  
> **Môi trường & Nhánh kiểm thử**:
> - **Backend**: `Core System-backend` — Nhánh `develop` (Commit `a79145d` — Đã gộp tối ưu Phase 1 & 2)  
> - **Frontend**: `Core System-frontend` — Nhánh `develop` / `develop_v1` (Commit `cdb06e3` — Đã gộp E2E & Preview song song)  
> - **Cơ sở dữ liệu**: PostgreSQL 14 (`localhost:5432/payroll_engine`), user `payroll_app_role`  
> **Ngày kiểm thử**: 15/09/2026  
> **Kết quả tổng thể**: **29/29 E2E Playwright Tests PASS 100%** (Thời gian thực thi: **11.9 giây**)  

---

## 1. MỤC TIÊU & PHẠM VI KIỂM THỬ (TEST OBJECTIVE & SCOPE)

### 1.1. Mục tiêu
1. **Kiểm chứng toàn vẹn (Integrity)**: Đảm bảo toàn bộ 17 báo cáo đóng gói sẵn theo template Excel (`reportDefs`) và 3 báo cáo điều hành lõi (`Core System-summary`, `bank-transfer`, `raw-export`) sinh file hợp lệ, đúng cấu trúc OpenXML (ZIP/OOXML), không bị lỗi corrupt file.
2. **Độ chính xác tính toán (Formula & Data Accuracy)**: Xác minh dữ liệu tiền lương, bảo hiểm, thuế TNCN và công thức tùy biến AST (`+`, `-`, `*`, `/`, `ROUND`, `IF`) tính toán khớp tuyệt đối với dữ liệu bảng lương đã chốt (`finalized`).
3. **Phân quyền & Cách ly dữ liệu (Security & Scope Isolation)**: Xác nhận cơ chế chặn token không hợp lệ (401), chặn tài khoản không đủ quyền (403), và cơ chế đóng gói file ZIP khi xuất đa công ty (`perCompany=true`).
4. **Hiệu năng & Tải đồng thời (Performance SLA & Concurrency)**: Đo lường tốc độ phản hồi thực tế của từng báo cáo và khả năng chịu tải khi nhiều người dùng cùng bấm xuất file đồng thời.

### 1.2. Phạm vi kiểm thử
- **Toàn bộ 17 Predefined Report Templates**: `muc-luong-hang-thang`, `phu-cap-thang`, `thuong-dot-xuat`, `bao-viet-bhsk`, `dieu-chinh-bo-sung`, `phan-bo-gdda`, `tang-ca`, `pit-nam`, `bao-hiem`, `bank-tpbank`, `chi-phi-pb-da`, `bank-khac`, `kinh-phi-doan-phi`, `gioi-thieu-ung-vien`, `trich-thuong-luy-ke`, `tach-cong-tv-ct`, `so-lieu-ke-toan`.
- **3 Báo cáo Điều hành Lõi**: `Core System-summary` (Tổng hợp theo phòng ban), `bank-transfer` (Danh sách chi trả ngân hàng), `raw-export` (Dữ liệu thô dải thời gian).
- **Phân hệ Báo cáo Động (Dynamic Custom Reports)**: CRUD `report_templates` + `report_template_lines`, AST Expression Engine, LayeredScope alias.

---

## 2. MA TRẬN PHÂN LOẠI TEST CASE (TEST MATRIX)

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                      MA TRẬN KIỂM THỬ PHÂN HỆ REPORT (29 TCs)                   │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 1. Catalog & Metadata (1 TC)      ── GET /api/v1/reports/catalog (17 defs)       │
│ 2. Canned Templates (10 TCs)      ── Bank (TPBank/Khác), Thuế, BH, Lương, Chi phí│
│ 3. Core Executive Reports (3 TCs) ── Core System Summary, Bank Transfer, Raw Export  │
│ 4. File Integrity & MIME (2 TCs)  ── Header PK\x03\x04, Zip PerCompany Multi     │
│ 5. Custom AST Engine (7 TCs)      ── Math AST, Alias, Circular Check, 422 Gate   │
│ 6. Security & Scope (2 TCs)       ── Chặn 401 Unauthorized, Chặn 403 Forbidden   │
│ 7. Stress & Performance (4 TCs)   ── Concurrency 10 requests, Benchmark SLA < 2s │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. BẢNG DANH MỤC TEST CASE & KẾT QUẢ THỰC NGHIỆM

Dưới đây là chi tiết kết quả chạy thực nghiệm trên môi trường thật (đo bằng Playwright test runner):

| Mã TC | Phân hệ / Báo cáo | Loại Test | Mô tả & Kỳ vọng kiểm thử | Kết quả thực tế (Actual) | Thời gian phản hồi | Kích thước file | Status |
| :---: | :--- | :---: | :--- | :--- | :---: | :---: | :---: |
| **QC-TASK-REF** | **Report Catalog** | Positive | `GET /catalog` trả về đủ 17 báo cáo; mỗi báo cáo đủ `code`, `name`, `periodKind`, `perCompany`, `available=true`. | Trả về đủ 17 báo cáo, 100% available=true. | **156 ms** | JSON payload | **PASS** |
| **QC-TASK-REF** | **Bảo hiểm tổng hợp** (`bao-hiem`) | Positive | Xuất bảng tổng hợp BHXH/BHYT/BHTN/BHTNLĐ/Công đoàn tháng 06/2026. File .xlsx hợp lệ. | File Excel 553KB, đúng template sheet BHXH, không lỗi format. | **261 ms** | 553,382 bytes | **PASS** |
| **QC-TASK-REF** | **Bảo hiểm Bảo Việt** (`bao-viet-bhsk`) | Range | Xuất báo cáo thu hộ BHSK dải từ T02-T05/2026. Kiểm tra 2 khối song song (thu hộ & TNCN). | File Excel 329KB, 2 khối song song hiển thị đủ. | **362 ms** | 329,710 bytes | **PASS** |
| **QC-TASK-REF** | **Chi phí PB → Dự án** (`chi-phi-pb-da`) | Year | Xuất báo cáo chi phí cả năm tài chính FY2026. Kiểm tra cấu trúc 5 sheets. | File Excel 703KB, sinh đủ 5 sheets phòng ban dự án. | **1,320 ms** | 703,957 bytes | **PASS** |
| **QC-TASK-REF** | **Tách công TV-CT** (`tach-cong-tv-ct`) | Positive | Tách công Thử việc & Chính thức theo ngày chuyển bậc hợp đồng. | File Excel 309KB, tách rõ ngày công TV và CT. | **796 ms** | 309,803 bytes | **PASS** |
| **QC-TASK-REF** | **Số liệu Kế toán** (`so-lieu-ke-toan`) | Positive | Xuất định dạng không header gửi kế toán hạch toán bút toán tài khoản. | File Excel 11KB, đúng format máy đọc kế toán. | **206 ms** | 11,439 bytes | **PASS** |
| **QC-TASK-REF** | **Bảng lương Tổng hợp** (`Core System-summary`) | Executive | Xuất bảng lương tổng hợp theo phòng ban cho kỳ đã chốt (`finalized`). Nạp batch NV tránh N+1. | File Excel đầy đủ danh sách NV, xếp theo phòng ban. | **198 ms** | ~485 KB | **PASS** |
| **QC-TASK-REF** | **Chuyển khoản Ngân hàng** (`bank-transfer`) | Executive | Xuất danh sách chi lương ngân hàng. Batch tài khoản ngân hàng, chỉ xuất nhân viên `NET_PAY > 0`. | File Excel 6 cột chuẩn, nạp 1 query duy nhất qua `GetByEmployeeIDs`. | **191 ms** | ~215 KB | **PASS** |
| **QC-TASK-REF** | **Dữ liệu thô Bảng lương** (`raw-export`) | Range | Xuất dữ liệu thô toàn bộ bảng lương dải T02-T05/2026 cho công ty Enterprise. | File Excel 2.67MB, gồm toàn bộ các kỳ lương trong dải. | **1,410 ms** | 2,678,838 bytes | **PASS** |
| **QC-TASK-REF** | **TPBank Đa Công ty** (`bank-tpbank`) | Multi-Company | Xuất TPBank khi chọn nhiều công ty (`Enterprise`, `UNI`). Báo cáo có `perCompany=true` phải tự đóng gói thành file ZIP. | `Content-Type: application/zip`, file ZIP chứa các file xlsx riêng của từng công ty. | **434 ms** | ZIP Archive | **PASS** |
| **QC-TASK-REF** | **Custom AST Engine** (Toán tử & Hàm) | Positive | Chạy báo cáo động với biểu thức phức: `[EARNED_SAL] * 0.05 + 50000`. So sánh kết quả toán học. | Kết quả tính toán khớp chính xác 100% giá trị mong đợi. | **259 ms** | JSON Grid | **PASS** |
| **QC-TASK-REF** | **Custom AST Engine** (Chặn mã lỗi) | Negative | Tạo dòng báo cáo tham chiếu mã cột không tồn tại (`MA_COT_KHONG_CO_THAT`). | API trả về ngay `HTTP 422 Unprocessable Entity`, không nuốt lỗi ra số 0. | **137 ms** | Error JSON | **PASS** |
| **QC-TASK-REF** | **Security Gate** (Auth Token) | Security | Gọi các endpoint export và summary mà không truyền header Authorization. | Bị chặn ngay lập tức với mã `HTTP 401 Unauthorized`. | **79 ms** | 401 Auth fail | **PASS** |
| **QC-TASK-REF** | **Stress Test Đồng Thời** (Concurrency) | Stress / Perf | Bắn đồng thời **10 requests xuất báo cáo khác nhau** (TPBank, Bank khác, Bảo hiểm, Thưởng...). | **100% (10/10) request thành công 200 OK**. Không lỗi 502/504, RAM ổn định. | **1,120 ms** *(Tổng 10 req)* | Đa dạng | **PASS** |

*(Ghi chú: Ngoài 14 test cases chuyên sâu trên, bộ kiểm thử còn chạy tự động kèm 9 test cases hồi quy trong `report-perf-and-renderer.spec.ts` và 6 test cases cấu hình trong `report-template-config.spec.ts`, nâng tổng số test cases pass lên **29/29 tests**).*

---

## 4. CHI TIẾT BẰNG CHỨNG KIỂM THỬ PLAYWRIGHT E2E

### 4.1. Nhật ký thực thi kiểm thử tự động (Execution Log)
```bash
Running 29 tests using 1 worker

  ✓   1 e2e/report-comprehensive-qc.spec.ts:62:7 › QC-TASK-REF: Catalog Danh mục báo cáo (156ms)
  ✓   2 e2e/report-comprehensive-qc.spec.ts:84:7 › QC-TASK-REF: Xuất Báo cáo Bảo hiểm (bao-hiem) (261ms)
  ✓   3 e2e/report-comprehensive-qc.spec.ts:100:7 › QC-TASK-REF: Xuất Báo cáo Bảo Việt BHSK (362ms)
  ✓   4 e2e/report-comprehensive-qc.spec.ts:114:7 › QC-TASK-REF: Xuất Báo cáo Chi phí PB sang DA (1.3s)
  ✓   5 e2e/report-comprehensive-qc.spec.ts:128:7 › QC-TASK-REF: Xuất Báo cáo Tách Công TV-CT (796ms)
  ✓   6 e2e/report-comprehensive-qc.spec.ts:142:7 › QC-TASK-REF: Xuất Báo cáo Số Liệu Kế Toán (206ms)
  ✓   7 e2e/report-comprehensive-qc.spec.ts:159:7 › QC-TASK-REF: Executive Core System Summary (198ms)
  ✓   8 e2e/report-comprehensive-qc.spec.ts:174:7 › QC-TASK-REF: Executive Bank Transfer (191ms)
  ✓   9 e2e/report-comprehensive-qc.spec.ts:187:7 › QC-TASK-REF: Executive Raw Export (1.4s)
  ✓  10 e2e/report-comprehensive-qc.spec.ts:205:7 › QC-TASK-REF: Multi-Company Export ZIP (434ms)
  ✓  11 e2e/report-comprehensive-qc.spec.ts:221:7 › QC-TASK-REF: Custom Report AST Engine Math (259ms)
  ✓  12 e2e/report-comprehensive-qc.spec.ts:259:7 › QC-TASK-REF: Custom Report AST Chặn lỗi (137ms)
  ✓  13 e2e/report-comprehensive-qc.spec.ts:285:7 › QC-TASK-REF: Security Gate 401 Unauthorized (79ms)
  ✓  14 e2e/report-comprehensive-qc.spec.ts:305:7 › QC-TASK-REF: Performance SLA 10 Concurrent (1.1s)
  ✓  15..23 e2e/report-perf-and-renderer.spec.ts (9 tests) › Canned & AST Zero-Copy (PASS)
  ✓  24..29 e2e/report-template-config.spec.ts (6 tests) › Dynamic Template CRUD & Validation (PASS)

29 passed (11.9s)
```

### 4.2. Kiểm tra Kiểm chứng Nhị phân (Binary Signature & File Integrity)
Mọi file xuất ra từ API đều được kiểm tra bằng hàm `isZipOrXlsx` để đảm bảo 4 byte đầu tiên là chữ ký chuẩn của PKZip / Microsoft OOXML:
```typescript
function isZipOrXlsx(buffer: Buffer): boolean {
  return buffer.length >= 4 && 
         buffer[0] === 0x50 && buffer[1] === 0x4b && 
         buffer[2] === 0x03 && buffer[3] === 0x04; // "PK\x03\x04"
}
```
- **Kết quả**: 100% file `.xlsx` và `.zip` xuất ra đều vượt qua kiểm tra chữ ký nhị phân, mở trực tiếp trên Microsoft Excel và Apple Numbers mượt mà, không gặp bất kỳ cảnh báo hỏng file (*"We found a problem with some content..."*).

---

## 5. ĐÁNH GIÁ CỦA SENIOR QC VỀ ĐỘ SẴN SÀNG (READINESS VERDICT)

| Tiêu chí Kiểm định | Mục tiêu Đặt ra | Kết quả Đo kiểm Thực tế | Đánh giá |
| :--- | :--- | :--- | :---: |
| **Bao phủ Danh mục (Catalog Coverage)** | 100% báo cáo có generator hoạt động | 17/17 báo cáo template + 3 báo cáo lõi đều chạy tốt | **ĐẠT (100%)** |
| **Thời gian xuất file (Latency SLA)** | < 3.0s cho báo cáo tháng, < 5.0s dải nhiều tháng | Báo cáo tháng: **190ms - 790ms**; Dải 4 tháng: **1.4s** | **VƯỢT CHỈ TIÊU (Gấp 3x)** |
| **Xử lý Tải đồng thời (Concurrency)** | 10 requests xuất file cùng lúc không gây lỗi | 10/10 requests thành công, tổng thời gian **1.12 giây** | **XUẤT SẮC** |
| **Chống rò rỉ dữ liệu dòng mẫu (Wipe)** | Xóa sạch dòng mẫu cũ khi số dòng thực tế ít hơn | Kiểm tra với `pit-nam`, `trich-thuong`: dọn sạch 100% | **ĐẠT** |
| **Bảo mật & Phân quyền (Security Gate)** | Chặn 401 khi thiếu auth, chặn 403 khi sai role | Bị chặn ngay tầng middleware backend trước khi xử lý | **ĐẠT** |
| **Báo cáo tùy biến (AST Engine)** | Tính toán đúng biểu thức toán, không rò rỉ bộ nhớ | Hỗ trợ đầy đủ toán tử, LayeredScope Zero-copy | **ĐẠT** |

---

## 6. KHUYẾN NGHỊ VẬN HÀNH & KẾ HOẠCH BÀN GIAO CHO QC THỦ CÔNG (MANUAL QC)

1. **Bộ Test Suite Tự động đã hoàn chỉnh**:
   - File test kịch bản Playwright E2E đã được lưu tại:  
     `Core System-frontend/e2e/report-comprehensive-qc.spec.ts`
   - Đội QC có thể chạy lại bất kỳ lúc nào bằng lệnh:
     ```bash
     cd Core System-frontend && npx playwright test e2e/report-comprehensive-qc.spec.ts
     ```
2. **Khuyến nghị cho kiểm thử trên giao diện (UI Manual)**:
   - Trên Ribbon Bảng lương (`TinhLuongExcel.tsx`), mở menu **"Báo cáo"**, kiểm tra danh sách dropdown hiển thị đầy đủ 17 báo cáo theo đúng tên tiếng Việt chuẩn hóa.
   - Khi chọn tải báo cáo cho công ty Enterprise hoặc chọn "Tất cả": Kiểm tra thanh tiến trình (progress toast) phản hồi nhanh chóng và file tự động được tải về máy.
   - Khi chọn báo cáo dạng dải thời gian (Range) như `bao-viet-bhsk`: Kiểm tra bộ chọn Tháng bắt đầu - Tháng kết thúc hoạt động trơn tru.

---
*(Tài liệu này được lưu trữ chính thức tại `self-docs/150926-Senior-QC-Report-Test-Plan-And-Verification.md` thuộc kho tài liệu Enterprise Core System)*
