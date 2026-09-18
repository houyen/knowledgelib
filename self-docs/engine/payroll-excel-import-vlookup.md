---
id: self-docs/engine/payroll-excel-import-vlookup
canonical_question: 'Technical guide and specification: Core System Excel Import —
  VLOOKUP theo mã nhân viên'
aliases:
- Core System Excel Import — VLOOKUP theo mã nhân viên
- Core System Excel Import VLookup 110826
entity_type: how_to
domain: self-docs > engine
last_verified: 2026-09-17
---

# Core System Excel Import — VLOOKUP theo mã nhân viên (110826)

## Hiện trạng trước khi làm

Mục "Nhập Excel" trong menu Tệp (`Core System-frontend/components-page/tinh-luong`) trước đây chỉ đọc file Excel bằng `exceljs` (thật, chạy được) và hiện preview tên file/sheet/số dòng/danh sách tối đa 12 header. Toàn bộ phần ghi dữ liệu là stub cố ý (pattern "build-now-adapt-later" — comment đầu `fileActions.ts` tự ghi rõ), nằm sau cờ `VERSION_API_READY = false`: `applyImportedRows` luôn trả `{ok:false, message:"Import API chưa sẵn sàng..."}`. Không có validate cột mã nhân viên bắt buộc, không mapping header→cột lưới, không tra cứu theo mã NV, không xử lý nhân viên lạ — bấm "Nhập" chỉ hiện toast lỗi.

Cơ chế ghi 1 ô lương hiện có (`cell-set`) cũng không đủ cho nhu cầu này: mỗi sửa 1 ô gọi `POST /Core System/cell-set/{periodId}` — 1 ô/1 request, bắt buộc lý do, tính lại lương ngay. Không có endpoint bulk nào cho ô lương trước 110826.

## Quyết định đã chốt (qua `AskUserQuestion`)

1. **Đối chiếu header cột:** khớp cả mã kỹ thuật (`col.key`, ví dụ `BASIC_SAL`) lẫn tên hiển thị (`col.label`, tiếng Việt, đã chuẩn hoá bỏ dấu/khoảng trắng/hoa-thường) — thử `key` trước, `label` sau.
2. **Nhân viên trong Excel không có trong kỳ đang mở:** bỏ qua dòng đó, liệt kê cảnh báo trong preview — không chặn toàn bộ import (không all-or-nothing).
3. **Ô Excel để trống tại 1 cột đã khớp:** giữ nguyên giá trị cũ trên lưới, không ghi đè thành 0/rỗng.
4. **Phạm vi:** làm đầy đủ cả Backend (API bulk mới) lẫn Frontend trong cùng đợt, vì API `cell-set` 1-ô-1-lần không đủ cho ghi hàng loạt.

Hai điểm nhỏ tự quyết theo tiền lệ code có sẵn (không cần hỏi vì đã có quy ước rõ): chỉ ghi vào cột `editable` (`componentType` là `input`/`manual`, khớp comment sẵn có ở `data.ts:141`); có màn hình xem trước đầy đủ trước khi ghi thật.

## Kiến trúc đã chọn

**Approach A (đã chọn):** đối chiếu VLOOKUP 100% ở Frontend (tái dùng `emps`/`cols` đã có sẵn trong state, không cần round-trip API để xem trước). Backend chỉ nhận danh sách `{empCode, componentCode, value}` đã đối chiếu xong, **không tin mù** — tự re-validate toàn bộ (company-scope, tồn tại nhân viên trong kỳ, cột có phải `input`/`manual`).

Hai phương án khác đã cân nhắc và không chọn: (B) gửi cả file Excel lên Backend để tự đọc/đối chiếu (chi phí cao hơn, phải viết lại logic matching bằng Go, round-trip API cho preview) — không chọn vì repo đã có sẵn `exceljs` client-side chạy tốt; (C) lặp gọi `cell-set` cũ nhiều lần từ FE — không chọn vì hàng nghìn request tuần tự, mỗi request bắt buộc lý do riêng, không transaction, `CalculateOne` bị gọi lặp nhiều lần cho cùng 1 NV.

Chi tiết đầy đủ (Context, Global constraints, Non-goals, 3 phương án, FR/SC): `llmwiki/wiki/sources/draft/110826-Core System-excel-import-vlookup.md`. PLAN thi hành chi tiết: `llmwiki/wiki/sources/draft/110826-Core System-excel-import-vlookup-PLAN.md`.

## Triển khai

**Backend (`Core System-backend`):**
- Tách `writeOverrideCell` (resolve component, validate period/finalized/blocklist, đọc oldVal, ghi/xoá override) khỏi `SetCell` — dùng chung cho cả `SetCell` (không đổi hành vi, đã xác nhận bằng test `TestPayrollCellSetRequiresReason` vẫn PASS) và `BulkSetCells` mới.
- `BulkSetCells` (`internal/service/payroll_bulk_cell_set.go`): ghi override cho từng ô (lỗi cục bộ nếu cột không tồn tại/không phải input-manual/NV không tồn tại trong kỳ), rồi `CalculateOne` **đúng 1 lần** cho mỗi nhân viên có ít nhất 1 ô ghi thành công (không phải 1 lần/ô), rồi ghi `payroll_cell_edits` + `audit_logs` theo batch trong 1 transaction.
- Middleware mới `RequireBulkEmpCompanyScope` (`internal/middleware/scope.go`): bản nhiều-mã của `RequireCompanyScopeMatch` — đọc toàn bộ `items[].empCode` trong body, kiểm TỪNG mã, 403 toàn bộ request nếu bất kỳ mã nào ngoài phạm vi công ty người gọi (fail-closed, kể cả mã không tra được company).
- Route mới: `POST /Core System/cells/bulk-set/{periodId}`, gate `requirePayrollCalculate + requireBulkEmpCompanyScope + requireEdit (Core System.edit)` — cùng tầng gate với `cell-set`, không mở quyền rộng hơn.
- Không có migration DB — tái dùng nguyên bảng `salary_component_overrides`, `payroll_cell_edits`, `audit_logs`.

**Frontend (`Core System-frontend`):**
- `matchImportToGrid` (hàm thuần, `fileActions.ts`) — đối chiếu cột mã NV, đối chiếu header còn lại theo key/label đã chuẩn hoá (`normalizeForMatch`, kỹ thuật NFD giống `toCode()` ở `PayrollPage.helpers.ts` nhưng viết riêng vì mục đích khác), tra `emps` theo mã, gộp trùng lấy dòng sau, trả về danh sách item + các danh sách cảnh báo (NV lạ, cột không nhận diện, cột tính toán bị bỏ qua).
- `applyImportedRows` (thay stub cũ) gọi `api.bulkSetPayrollCells` thật.
- `TinhLuongExcel.tsx`: dialog "Nhập Excel" hiện đầy đủ số ô sẽ ghi/số NV bị ảnh hưởng/3 loại cảnh báo trước khi cho bấm "Nhập"; sau khi ghi thành công gọi `data.refetchRows()` để làm mới lưới từ dữ liệu thật (không chỉ set state cục bộ).

## Kết quả test

**Backend:** baseline trước khi sửa (đo bằng `go test ./... -p 1` trên `payroll_engine` qua role `postgres`): 915 passed / 7 failed. Sau khi thêm: **922 passed / 7 failed** — đúng 7 fail baseline (không liên quan: `TestPermissionGateCoverageReport`, gate thiếu ở route dev seed-test-data, 4 test `RequireRole`/403 ở `internal/handler`), 0 hồi quy. 2 test tích hợp mới cho `BulkSetCells` (ghi nhiều NV/nhiều ô, tính đúng 1 lần/NV; cột không tồn tại chỉ lỗi cục bộ) + 4 test tích hợp mới (1 cha + 3 sub) cho `RequireBulkEmpCompanyScope` (trong phạm vi/ngoài phạm vi/mã không tra được → fail-closed). `go build`/`go vet` sạch. `gofmt` không chạy `-w` trên `payroll_service.go` vì file có quirk pre-existing không liên quan (comment cũ có smart-quote, alignment map ở xa vùng sửa — đã xác nhận bằng `gofmt -d` không đụng khối 1180-1330 mình sửa).

**Frontend:** 3 test vitest mới cho `matchImportToGrid`/`normalizeForMatch` — PASS. Toàn bộ suite vitest: 54 PASS/0 FAIL (không hồi quy). `tsc --noEmit` và `eslint` sạch cho mọi file đã sửa.

**Kiểm chứng end-to-end bằng dữ liệu dev thật (curl, dev-bypass `Authorization: Bearer dev`):** gọi `POST /Core System/cells/bulk-set/{periodId}` đổi `PHONE_ALLOW` của nhân viên thật `000061` (kỳ Tháng 06/2026, draft) từ 600.000 → 650.000 — xác nhận `GROSS` tự tính lại đúng (47.482.727), `payroll_cell_edits` ghi đúng `old_value`/`new_value`/`reason = "Nhập từ Excel: test-import-110826.xlsx"`. Sau đó khôi phục lại giá trị 600.000 qua 1 lượt bulk-set khác — xác nhận đọc lại đúng 600.000, không để lại dữ liệu test sai lệch trên DB dev.

## Việc còn nợ

**Chưa click-through giao diện thật trong trình duyệt** — phiên này không có công cụ điều khiển trình duyệt (Playwright/computer-use). Đã chuẩn bị sẵn file mẫu `/tmp/test-import-110826.xlsx` (cột "Mã nhân viên" + "Phụ cấp điện thoại", 1 dòng khớp NV `000061`, 1 dòng mã lạ `MA_LA_110826` để test nhánh cảnh báo) và đã chạy `go run ./cmd/Core System` (`:8080`) + `npm run dev` (`:3000`) ở nền để bạn tự kiểm nếu muốn — 3 việc cần xác nhận bằng mắt: (1) preview hiện đúng số ô/cảnh báo trước khi bấm Nhập, (2) sau khi Nhập lưới tự cập nhật không cần F5, (3) F5 lại giá trị vẫn còn (đã xác nhận đúng ở tầng API/DB qua curl, chỉ chưa xác nhận qua chính UI).

## Trạng thái git

- `Core System-backend@9d53e6a` trên `feature_v2` — chưa push.
- `Core System-frontend@4d34e6b` trên `feature_v2` — chưa push.
