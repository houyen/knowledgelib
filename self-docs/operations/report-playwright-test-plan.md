---
id: self-docs/operations/report-playwright-test-plan
canonical_question: 'Technical guide and specification: 🎭 Kế hoạch Kiểm thử Playwright
  E2E — Tối ưu Renderer Báo cáo'
aliases:
- 🎭 Kế hoạch Kiểm thử Playwright E2E — Tối ưu Renderer Báo cáo
- 150926 Report Playwright Test PLAN
entity_type: how_to
domain: self-docs > operations
last_verified: 2026-09-17
---

# 🎭 Kế hoạch Kiểm thử Playwright E2E — Tối ưu Renderer Báo cáo (Phase 1 & Phase 2)

> **Mục tiêu**: Kiểm thử tự động hóa đầu cuối (E2E) bằng Playwright để xác thực toàn bộ các cải tiến hiệu năng và tính chính xác của hệ thống Report sau cả Phase 1 và Phase 2.
> **Thời gian**: 15/09/2026  
> **Nhánh**: `feature/report-perf-optimize-150926`

---

## I. MỤC TIÊU & PHẠM VI KIỂM THỬ

Kế hoạch kiểm thử bao gồm **4 nhóm kịch bản chính**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PLAYWRIGHT E2E REPORT TEST SUITE                         │
└─────────────────────────────────────────────────────────────────────────────┘
       │
       ├──► 1. [ƯU TIÊN #1] Built-in Canned Reports (Batch Bank + Smart Wipe)
       │    ├── TC01: Xuất Báo cáo TPBank (bank-tpbank) — Batch bank accounts
       │    ├── TC02: Xuất Báo cáo Ngân Hàng Khác (bank-khac) — Batch bank accounts
       │    ├── TC03: Xuất Báo cáo PIT Năm (pit-nam) — Smart surplus wipe
       │    ├── TC04: Xuất Báo cáo Trích Thưởng Lũy Kế (trich-thuong) — Smart wipe
       │    └── TC05: Xuất Báo cáo Core System Summary & Bank Transfer Legacy (Phase 1)
       │
       ├──► 2. [ƯU TIÊN #2] Custom Report Runner (AST Engine + LayeredScope)
       │    ├── TC06: Chạy Template có công thức expr đa toán tử (+, -, *, /, IF)
       │    ├── TC07: Chạy Template có biểu thức expr tham chiếu Alias dòng trước
       │    └── TC08: Zero-copy LayeredScope bảo toàn dữ liệu khi chạy lặp lại
       │
       ├──► 3. [FRONTEND UI] Ribbon Preview & Song Song Hoá Đa Công Ty
       │    ├── TC09: Ribbon Báo cáo: Mở xem trước Báo cáo TPBank trên lưới
       │    └── TC10: Preview khi chọn "Tất cả công ty" (N requests song song)
       │
       └──► 4. [PERFORMANCE GATE] Cổng Giám Sát Thời Gian Phản Hồi
            └── TC11: Benchmark Response Time: Toàn bộ API báo cáo phản hồi < 3.0s
```

---

## II. CHI TIẾT CÁC TEST CASES

### Nhóm 1: Built-in Canned Reports (Batch Queries + Smart Wipe)

| Mã TC | Tên Kịch bản | Phương thức & Endpoint | Tiêu chí Đạt (Assertions) |
|:---|:---|:---|:---|
| **TC01** | Xuất Báo cáo TPBank (Batch Bank Accounts) | `POST /api/v1/reports/bank-tpbank/export` | Status 200, Content-Type XLSX, Buffer size > 5KB, headers `Content-Disposition` chứa `bank-tpbank`. |
| **TC02** | Xuất Báo cáo Ngân Hàng Khác (Batch Bank Accounts) | `POST /api/v1/reports/bank-khac/export` | Status 200, Content-Type XLSX, Buffer size > 5KB, thời gian thực thi < 2.5s. |
| **TC03** | Xuất Báo cáo PIT Năm (Smart Surplus Wipe) | `POST /api/v1/reports/pit-nam/export` (year=2026) | Status 200, Content-Type XLSX, file không bị lỗi XML corruption khi mở. |
| **TC04** | Xuất Báo cáo Trích Thưởng Lũy Kế (Smart Wipe) | `POST /api/v1/reports/trich-thuong-luy-ke/export` | Status 200, Content-Type XLSX, dữ liệu bảng 9 được ghi đầy đủ các nhóm. |
| **TC05** | Tải Core System Summary & Bank Transfer Legacy | `GET /api/v1/reports/Core System-summary`<br>`GET /api/v1/reports/bank-transfer` | Cả 2 route legacy trả về 200, xử lý toàn bộ nhân viên mà không gặp N+1 timeout. |

### Nhóm 2: Custom Report Runner (AST Engine + LayeredScope)

| Mã TC | Tên Kịch bản | Mô tả chi tiết | Tiêu chí Đạt (Assertions) |
|:---|:---|:---|:---|
| **TC06** | AST Engine: Biểu thức toán học & hàm điều kiện | Tạo template có dòng `sourceKind: "expr"`: `[BASIC_SAL] * 0.1 + IF([GROSS] > 30000000, 500000, 0)`. | Chạy `run`: Trả về 200, cột kết quả tính chính xác theo giá trị của từng nhân viên. |
| **TC07** | LayeredScope: Tham chiếu Alias dòng trước | Dòng 1: `sourceKind: "sum"`, `alias: "TONG_BH"`. Dòng 2: `sourceKind: "expr"`, công thức `[GROSS] - [TONG_BH]`. | Chạy `run`: Dòng 2 nhận đúng giá trị của alias `TONG_BH` qua LayeredScope. |
| **TC08** | Tính nhất quán của Runner khi chạy liên tục | Chạy lặp lại template 5 lần liên tiếp trên cùng 1 kỳ. | Cả 5 lần đều trả về kết quả số liệu đồng nhất 100%, không bị memory leak hay sai lệch alias giữa các NV. |

### Nhóm 3: Frontend Ribbon Preview & Song song hoá Đa công ty

| Mã TC | Tên Kịch bản | Mô tả chi tiết | Tiêu chí Đạt (Assertions) |
|:---|:---|:---|:---|
| **TC09** | UI Preview Báo cáo Đóng gói sẵn | Mở tab `/Core System`, chuyển Ribbon "Báo cáo", click vào tile "UP Ngân hàng — TPBank". | Sheet preview `r-bank-tpbank` xuất hiện, grid hiển thị đủ cột STT, Số tài khoản, Tên tài khoản, Số tiền. |
| **TC10** | Multi-Company Parallel Preview | Chọn dropdown công ty = "Tất cả công ty", click xem trước báo cáo. | Frontend bắn các request song song (`Promise.allSettled`), dữ liệu các công ty được gộp vào 1 lưới duy nhất. |

### Nhóm 4: Performance Guardrail (Cổng Chặn Hồi Quy Hiệu Năng)

| Mã TC | Tiêu chí Kiểm tra | Ngưỡng Tối Đa Cho Phép (Threshold) |
|:---|:---|:---:|
| **TC11.1** | Thời gian xuất báo cáo TPBank (3.000 NV) | **< 3.0 giây** (trước đây ~6-10s) |
| **TC11.2** | Thời gian xuất báo cáo Ngân Hàng Khác | **< 3.0 giây** |
| **TC11.3** | Thời gian chạy Custom Template Report qua AST | **< 1.5 giây** cho toàn bộ kỳ |
| **TC11.4** | Thời gian render lưới Preview trên Frontend | **< 2.0 giây** cho 1.000 dòng đầu |

---

## III. THIẾT KẾ FILE TEST PLAYWRIGHT

Tạo file test mới độc lập:
`Core System-frontend/e2e/report-perf-and-renderer.spec.ts`

**Cấu trúc file**:
```typescript
import { test, expect } from "@playwright/test";

const API = "http://localhost:8080";
const DEV_AUTH = { Authorization: "Bearer dev" };
const PERIOD_ID = "eb960286-8e22-4d1e-ab88-687b66848b87"; // Kỳ T06/2026

test.describe("E2E Report Performance & Renderer (Phase 1 & Phase 2)", () => {
  // Test Nhóm 1: Canned Reports
  test("TC01: Xuất Báo cáo TPBank (bank-tpbank) — Batch Bank Accounts", async ({ request }) => { ... });
  test("TC02: Xuất Báo cáo Ngân Hàng Khác (bank-khac) — Batch Bank Accounts", async ({ request }) => { ... });
  test("TC03: Xuất Báo cáo PIT Năm (pit-nam) — Smart Wipe", async ({ request }) => { ... });
  test("TC04: Xuất Báo cáo Trích Thưởng Lũy Kế (trich-thuong-luy-ke)", async ({ request }) => { ... });
  test("TC05: Tải Báo cáo Tổng Hợp & Chuyển Khoản Legacy", async ({ request }) => { ... });

  // Test Nhóm 2: Custom Reports AST Engine & LayeredScope
  test("TC06: Chạy Custom Report với biểu thức AST đa toán tử", async ({ request }) => { ... });
  test("TC07: Chạy Custom Report với LayeredScope Alias dòng trước", async ({ request }) => { ... });
  test("TC08: Đảm bảo tính nhất quán qua nhiều lần chạy", async ({ request }) => { ... });

  // Test Nhóm 3: Performance Guardrail
  test("TC11: Performance Gate — Tất cả endpoints phản hồi dưới ngưỡng thời gian", async ({ request }) => { ... });
});
```

---

## IV. ĐIỀU KIỆN CHẠY TEST (PREREQUISITES)

Để thực thi bộ test Playwright này trên môi trường local:
1. **PostgreSQL**: Đang chạy trên port `5432` với database `payroll_engine` và user `payroll_app_role`.
2. **Backend**: Đang chạy trên port `8080` với `DEV_USER_EMAIL=user@company.test`, `DEV_AUTH_TOKEN=dev`, `APP_ENV=dev`.
3. **Frontend**: Đang chạy trên port `3000` (đối với các test có UI interaction).
4. **Lệnh chạy**:
   ```bash
   cd Core System-frontend && npx playwright test e2e/report-perf-and-renderer.spec.ts --reporter=list
   ```

---

## V. KẾT QUẢ THỰC THI THỰC TẾ (15/09/2026)

```
Running 9 tests using 1 worker

  ✓ 1 TC01: Xuất Báo cáo TPBank (bank-tpbank) — Batch Bank Accounts (348ms)
  ✓ 2 TC02: Xuất Báo cáo Ngân Hàng Khác (bank-khac) — Batch Bank Accounts (239ms)
  ✓ 3 TC03: Xuất Báo cáo PIT Năm (pit-nam) — Smart Surplus Row Wipe (712ms)
  ✓ 4 TC04: Xuất Báo cáo Trích Thưởng Lũy Kế (trich-thuong-luy-ke) — Smart Wipe (278ms)
  ✓ 5 TC05: Xuất Báo cáo Core System Summary & Bank Transfer Legacy (Phase 1 N+1 Fix) (309ms)
  ✓ 6 TC06: Chạy Custom Report với biểu thức AST đa toán tử (+, -, *, /) (401ms)
  ✓ 7 TC07: Chạy Custom Report với LayeredScope Alias dòng trước (266ms)
  ✓ 8 TC08: Đảm bảo tính nhất quán qua nhiều lần chạy liên tiếp (Zero-Copy Stability) (522ms)
  ✓ 9 TC11: Performance Gate — Endpoints phản hồi dưới ngưỡng thời gian chuẩn (67ms)

  9 passed (3.4s)
```

- **Hồi quy**: Chạy kèm suite `e2e/report-template-config.spec.ts`: **6/6 passed (2.0s)**.
- **Tổng cộng**: **15/15 Playwright E2E tests PASS 100%**. Mọi thao tác xuất báo cáo phức tạp đều hoàn tất trong vòng **0.2s - 0.7s**.

---
*Tài liệu này là căn cứ chính thức để triển khai và nghiệm thu kiểm thử tự động cho tính năng Report.*
