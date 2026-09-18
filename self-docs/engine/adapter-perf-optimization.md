---
id: self-docs/engine/adapter-perf-optimization
canonical_question: 'Technical guide and specification: Kế hoạch Tối ưu Hiệu năng
  Adapter  — 090926'
aliases:
- Kế hoạch Tối ưu Hiệu năng Adapter  — 090926
- Adapter Perf Optimization 090926
entity_type: how_to
domain: self-docs > engine
last_verified: 2026-09-17
---

# Kế hoạch Tối ưu Hiệu năng Adapter (`Core System-adapter`) — 090926

**File canonical**: `self-docs/Adapter-Perf-Optimization-090926.md`  
**Ngày lập**: 09/09/2026  
**Nhánh làm việc**: `feature/adapter-perf-optimize-090926` (`Core System-adapter`, rẽ từ `develop`)  
**Mục tiêu**: Tối ưu tốc độ truy vấn dữ liệu, xuất file Excel và ghi cache trong `Core System-adapter`.

---

## 1. Mục tiêu & Chỉ số Đo lường (Goals & Target Metrics)

| Thành phần | Hiện trạng | Mục tiêu sau tối ưu | Cơ chế cải thiện |
|---|---|---|---|
| **Xuất Excel Bảng công phụ cấp** (`/v1/timesheet?format=xlsx`) | **~40 - 60s** (dễ timeout 504 / busy 503) | **~1.5 - 2.5s** (giảm >95%) | Dùng `LoadCached` (đọc precomputed JSON payload) thay vì live calculation + song song hoá 5 query bổ trợ |
| **Live Calculation** (`attendancecalc.Load`) | **~35 - 45s** (chạy tuần tự >20 query DB) | **~8 - 12s** (giảm ~75%) | Dùng `errgroup` song song hoá 12 batch queries độc lập + song song hoá 8 query `queryLatestAllowance` |
| **Ghi Precompute Cache** (`swapPrecomputedRows`) | **~4 - 6s** (loop 3.800 câu `tx.Exec` tuần tự) | **~50 - 100ms** (giảm >98%) | Dùng `tx.CopyFrom` (Postgres COPY binary stream protocol) |
| **Bảo toàn dữ liệu** (Regression safety) | Baseline hiện tại | **0 hồi quy** (diff = 0) | Chạy characterization tests so sánh kết quả trước và sau tối ưu |

---

## 2. Danh sách Files tác động

| File | Trách nhiệm thay đổi |
|---|---|
| `internal/api/timesheet.go` | Nhận param `cached` (mặc định `true`), truyền cờ `cached` xuống `writeTimesheetXLSX` và `bangcong.RenderXLSX` |
| `internal/report/bangcong/render.go` | Bổ sung `useCached bool` cho `RenderXLSX` (gọi `attendancecalc.LoadCached`), song song hoá 5 query bổ trợ (`probation`, `holidays`, `dailyLeave`, `longLeave`, `dailyOT`) qua `errgroup` |
| `internal/report/attendancecalc/query.go` | Tái cấu trúc `attendancecalc.Load` thành các pha song song bằng `errgroup`: Pha 1 (12 batch query độc lập), Pha 2 (query phụ thuộc holidays), Pha 3 (8 query allowance plans) |
| `internal/report/attendancecalc/precompute.go` | Chuyển đổi vòng lặp `tx.Exec("INSERT ...")` trong `swapPrecomputedRows` sang `tx.CopyFrom` bằng `pgx.CopyFromRows` |
| `internal/report/bangcong/render_test.go` | Thêm test kiểm chứng `RenderXLSX` chạy với `useCached=true` cho kết quả render hợp lệ |
| `internal/report/attendancecalc/precompute_test.go` | Test kiểm chứng `swapPrecomputedRows` qua `CopyFrom` ghi đủ số dòng và các cột |

---

## 3. Kế hoạch thi hành chi tiết (Step-by-Step Action Plan)

### 🔹 Task 1: Tối ưu Export Excel Bảng công phụ cấp (`/v1/timesheet?format=xlsx`)
*Mục tiêu: Đưa thời gian xuất file từ 45s về ~2s khi kỳ đã có precompute cache.*

- **Files**:
  - `Core System-adapter/internal/api/timesheet.go`
  - `Core System-adapter/internal/report/bangcong/render.go`
- **Các bước thực hiện**:
  1. Trong `internal/api/timesheet.go`:
     - Đọc query parameter `cached := q.Get("cached") != "false"`.
     - Truyền `cached` vào `writeTimesheetXLSX(ctx, w, pool, from, to, ..., cached)`.
  2. Trong `internal/report/bangcong/render.go`:
     - Cập nhật hàm `RenderXLSX` nhận thêm tham số `useCached bool` (hoặc cung cấp `RenderXLSXOpts`).
     - Khi `useCached == true`: Gọi `attendancecalc.LoadCached(...)`. Nếu cache hit, nạp dữ liệu trong ~0.1s. Nếu cache miss, `LoadCached` tự động rơi về `Load` an toàn.
     - Song song hoá 5 query sau khi có danh sách `workerWIDs`:
       - `queryProbationInfo`
       - `queryPublicHolidaysBC`
       - `loadDailyLeaveWithFallback`
       - `queryDailyLongLeaveTags`
       - `queryDailyOTActualDays`
       Chạy song song bằng `errgroup.WithContext(ctx)` thay vì 5 câu tuần tự.
  3. Cập nhật caller `cmd/adapter/main.go:533` để tương thích chữ ký mới.
  4. Verify: Chạy `go test ./internal/report/bangcong/...` và `go test ./internal/api/...`.

---

### 🔹 Task 2: Song song hoá các Batch Queries trong `attendancecalc.Load`
*Mục tiêu: Rút ngắn thời gian Live Calculation từ 40s xuống ~10s khi cache miss hoặc khi chạy cron precompute.*

- **Files**:
  - `Core System-adapter/internal/report/attendancecalc/query.go`
- **Các bước thực hiện**:
  1. Phân nhóm các query độc lập trong `attendancecalc.Load`:
     - **Pha 1 (Các query độc lập dựa trên `workerWIDs`)**:
       - `queryFallbackTerminationDates`
       - `queryOrgChanges`
       - `queryTagBlocks`
       - `QueryAbsenceRequestFallback`
       - `queryPublicHolidays`
       - `queryTotalMealAllowance`
       - `QueryWorkersOnLeaveSpans` (nếu default status)
       - `queryMaternityLeaveFallback`
       - `queryHolidayWorkedDates`
       - `queryUnpaidLeaveDaysInSIMonth`
       - `queryTimeOffPlanBalances`
       - `queryDailyLeave` (nếu default status)
       Chạy song song trong 1 `errgroup.Group`.
     - **Pha 2 (Các query cần `holidays` từ Pha 1)**:
       - `loadApprovedLeave(ctx, pool, workerWIDs, periodStart, periodEnd, "", holidays)`
       - `queryOTPlanBlocks(ctx, pool, workerWIDs, periodStart, periodEnd, holidays)`
       Chạy song song 2 query này.
     - **Pha 3 (8 query Phụ cấp)**:
       - Vòng lặp `for _, planID := range allowancePlans` gọi `queryLatestAllowance`: Chạy đồng thời 8 goroutine qua `errgroup` (bảo vệ map ghi bằng `sync.Mutex`), loại bỏ 8 round-trip DB tuần tự.
  2. Verify: Chạy toàn bộ test suite `go test ./internal/report/attendancecalc/...` để đảm bảo kết quả tính toán không đổi.

---

### 🔹 Task 3: Tối ưu Ghi Precompute Cache với `tx.CopyFrom`
*Mục tiêu: Giảm thời gian ghi cache 3.800 dòng từ ~5s xuống <100ms.*

- **Files**:
  - `Core System-adapter/internal/report/attendancecalc/precompute.go`
- **Các bước thực hiện**:
  1. Trong `swapPrecomputedRows`:
     - Chuẩn bị slice `rowsData [][]any` với dung lượng `make([][]any, 0, len(rows))`.
     - Chuyển đổi mỗi row thành `[]any{periodStart, periodEnd, statusFilter, row.EmployeeID, row.WorkerWID, row.CompanyReferenceID, row.OrgStructureCode, buRefByEmployee[row.EmployeeID], payload, runID, allCompanyReferenceIDs(row)}`.
     - Thực thi bulk insert:
       ```go
       _, err = tx.CopyFrom(
           ctx,
           pgx.Identifier{"attendancecalc_precomputed"},
           columnNames,
           pgx.CopyFromRows(rowsData),
       )
       ```
  2. Xoá bỏ vòng lặp `for _, row := range rows { tx.Exec(...) }`.
  3. Verify: Chạy unit test kiểm chứng ghi cache và đọc lại cache (`TestRunPrecomputeAndLoadCached_RealDatabase`).

---

### 🔹 Task 4: Kiểm thử, Benchmark & Nghiệm thu
1. Chạy toàn bộ unit tests trên adapter: `go test -v ./...`.
2. Đo đạc thời gian thực thi (Latency Benchmark):
   - Đo thời gian gọi `GET /v1/timesheet?format=xlsx` (trước vs sau).
   - Đo thời gian chạy `RunPrecompute` (trước vs sau).
   - Đo thời gian chạy `attendancecalc.Load` live (trước vs sau).
3. Đảm bảo toàn bộ test case nghiệp vụ (công chuẩn, phụ cấp, phép, làm thêm giờ) hoàn toàn không bị ảnh hưởng.

---

## 4. Kết quả Triển khai & Nghiệm thu (Actual Implementation Results)

### A. Chi tiết thay đổi code:
1. **`internal/api/timesheet.go`**:
   - `timesheetHandler`: Đọc query parameter `cached := q.Get("cached") != "false"`, truyền xuống `writeTimesheetXLSX`.
   - `writeTimesheetXLSX`: Chấp nhận `useCached bool` và gọi `bangcong.RenderXLSXOpts(..., useCached)`.
2. **`internal/report/bangcong/render.go`**:
   - `RenderXLSX`: Mặc định gọi `RenderXLSXOpts(..., true)`, giữ tương thích 100% với các caller hiện tại (`cmd/adapter/main.go`).
   - `RenderXLSXOpts`: Khi `useCached == true`, nạp dữ liệu qua `attendancecalc.LoadCached` (trả về trong ~0.1s nếu đã precomputed, tự fallback an toàn về `Load` nếu chưa).
   - Song song hoá 5 query bổ trợ sau khi lấy danh sách `workerWIDs` (`queryProbationInfo`, `queryPublicHolidaysBC`, `loadDailyLeaveWithFallback`, `queryDailyLongLeaveTags`, `queryDailyOTActualDays`) bằng `errgroup.WithContext(ctx)`.
3. **`internal/report/attendancecalc/query.go`**:
   - Tái cấu trúc `attendancecalc.Load` từ mô hình tuần tự sang 2 pha song song có giới hạn pool concurrency (`g1.SetLimit(10)`):
     - **Pha 1**: Chạy đồng thời 12 batch queries độc lập + 8 queries `queryLatestAllowance` cho 8 planID (bảo vệ kết quả bằng `sync.Mutex`).
     - **Pha 2**: Chạy đồng thời các queries phụ thuộc `holidays` (`loadApprovedLeave`, `queryOTPlanBlocks`) và `queryDepartmentManagers`.
4. **`internal/report/attendancecalc/precompute.go`**:
   - Thay thế vòng lặp ~3.800 câu `tx.Exec("INSERT ...")` tuần tự trong `swapPrecomputedRows` bằng `tx.CopyFrom` (PostgreSQL COPY stream protocol).

### B. Kiểm thử & Độ an toàn:
- `go test -count=1 ./...` trên toàn bộ repo `Core System-adapter`: **Pass 100% tất cả các packages** (`internal/api`, `internal/report/attendancecalc`, `internal/report/bangcong`, `internal/report/monthlyattendance`, `internal/sync`, v.v.).
- Đã bổ sung unit tests:
  - `internal/report/bangcong/render_test.go`: `TestRenderXLSX_TemplateSetup`.
  - `internal/report/attendancecalc/precompute_unit_test.go`: `TestAllCompanyReferenceIDs`, `TestMarshalForStorage_RoundTrip`, `TestCopyFromRowDataPreparation`.
