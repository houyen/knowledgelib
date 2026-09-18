---
id: self-docs/engine/payroll-import-template-toolbar-export
canonical_question: 'Technical guide and specification: Core System Import Template
  Toolbar Export — 030926'
aliases:
- Core System Import Template Toolbar Export — 030926
- Core System Import Template Toolbar Export 030926
entity_type: how_to
domain: self-docs > engine
last_verified: 2026-09-03
---

# Core System Import Template Toolbar Export — 030926

**Canonical duy nhất cho hạng mục này.** Cập nhật liên tục, không tạo file mới cùng chủ đề.

## Bối cảnh

User yêu cầu 2 việc trên `Core System-frontend`, màn `TinhLuongExcel` (bảng lương):

1. Icon "download" đầu tiên trên tab-strip (trước đây chỉ tải file tĩnh `/backup/Core System-template-verified-30.xlsx`, phục vụ mục đích backup-plan/tham chiếu Workday cũ, không còn dùng) → đổi thành export file Excel làm **template nhập bảng lương**: 3 cột (`employeeCode`/`BASIC_SAL`/`PROB_EARNED`), dòng 1 = diễn giải tiếng Việt, dòng 2 = mã kỹ thuật, data từ dòng 3.
2. Luồng "Nhập Excel" (`matchImportToGrid`) trước đây cứng "dòng 1 luôn là header, data từ dòng 2" → sửa để tự nhận diện dòng nào là header, hỗ trợ cả file cũ (1 dòng header) lẫn template mới (2 dòng header).

## Quyết định đã chốt qua `AskUserQuestion` (2026-09-03)

- Nguồn data cho template mới: y hệt icon export thứ 2 (`emps`/`cols` đang mở ở sheet lương hiện tại), không phải toàn bộ NV công ty.
- Import: auto-detect dòng header, không ép chỉ hỗ trợ 1 định dạng.
- Cột trong template mới: cố định 2 cột lương (`BASIC_SAL`, `PROB_EARNED`), không làm UI chọn cột.
- File tĩnh cũ `/backup/Core System-template-verified-30.xlsx`: bỏ hẳn đường tải trong code (giữ nguyên file vật lý trên đĩa — không có runtime nào khác đọc nó, các tham chiếu còn lại trong codebase chỉ là comment lịch sử về nguồn gốc schema `payrollImportMapping.ts`/`detectPayrollTemplateMatch`, không phải fetch thật).

## Quy trình

`/propose` → SPEC `llmwiki/wiki/sources/draft/030926-Core System-import-template-toolbar-export.md` (+ HTML companion tối thiểu qua cổng R7) → duyệt → `/plan` → PLAN `llmwiki/wiki/sources/draft/030926-Core System-import-template-toolbar-export-PLAN.md` → thi hành theo TDD.

**1 phát hiện sửa lúc viết PLAN (fact, không phải quyết định thiết kế):** SPEC ghi mặc định "nhánh mới từ `feature_v2`". Kiểm tra thật (`git branch -a --sort=-committerdate`, `git log origin/develop_v1 -1`) cho thấy `origin/feature_v2` đã bị xoá trên remote ("gone"); `develop_v1` mới là nhánh đang checkout, khớp `origin/develop_v1` (cùng ngày 2026-09-03). → Nhánh làm việc thật: `feature/Core System-import-template-toolbar-export`, tách từ `develop_v1`.

## Thi hành

**Task 1 — `Core System-frontend@91454ad`:**
- Thêm `buildPayrollImportTemplateExport(input: { emps, periodLabel? })` trong `payrollTemplateExport.ts` (cuối file) — hàm ĐỘC LẬP với `buildPayrollTemplateExport` đã có (không đọc `TEMPLATE_URL`, dựng workbook mới hoàn toàn). 2 dòng header ghi cứng (`IMPORT_TEMPLATE_COLUMNS`), data ghi từ dòng 3 theo đúng thứ tự `emps`, ô không có giá trị lương để `null` (không ép về 0).
- Đổi import + `onClick` icon 1 trong `TinhLuongExcel.tsx` — cùng nguồn `emps`/`cols`/`data.periods`/`data.periodId` với `runPayrollSummaryExport()` (icon 2 kế bên), cùng pattern `toast`/`logAction`/`downloadBlob` đã dùng trong file.
- Test mới: `payrollTemplateExport.test.ts` — 2 case (đủ 2 dòng header + data đúng vị trí/giá trị; ô trống giữ `null`).

**Task 2 — `Core System-frontend@755b225`:**
- Thêm `detectHeaderRowIndex(rows, cols): number` trong `fileActions.ts` (ngay trước `matchImportToGrid`) — đếm số ô ở `rows[0]`/`rows[1]` khớp `EMP_CODE_HEADER_CANDIDATES` hoặc `col.key` đã chuẩn hoá (`normalizeForMatch`); `rows[1]` thắng chỉ khi khớp NHIỀU HƠN `rows[0]` — hoà hoặc thua thì mặc định `rows[0]` (an toàn ngược file cũ).
- Sửa 2 dòng đầu `matchImportToGrid` dùng `headerRowIndex` thay vì hardcode `rows[0]`/`rows.slice(1)` — chữ ký hàm công khai không đổi, không ảnh hưởng call site (`TinhLuongExcel.tsx` gọi qua `fileActions.matchImportToGrid`).
- Test mới: `fileActions.match.test.ts` — 3 case `detectHeaderRowIndex` (file cũ, template mới, hoà) + 1 case end-to-end `matchImportToGrid` với file 2-dòng-header + thêm cột `PROB_EARNED` vào fixture `cols` dùng chung.

## Kết quả kiểm

- `tsc --noEmit`: 3 lỗi — xác nhận **tiền tồn tại** bằng `git stash` (file `public/backup/payslip-lib.test.ts`, không liên quan 2 file đã sửa) — 0 lỗi mới.
- `eslint` trên đúng các file đã sửa (`TinhLuongExcel.tsx`, `payrollTemplateExport.ts`, `payrollTemplateExport.test.ts`, `fileActions.ts`, `fileActions.match.test.ts`): sạch.
- `vitest run` toàn bộ suite: baseline 184 pass/0 fail → sau 190 pass/0 fail (+6 test mới) — 0 hồi quy.

## Trạng thái git

Nhánh `Core System-frontend@feature/Core System-import-template-toolbar-export` (tách từ `develop_v1`), 2 commit (`91454ad`, `755b225`). **Chưa push, chưa merge.**

## Khuyến nghị trước khi merge

Dự án không có hạ tầng test component (xem log 240826) — khuyến nghị kiểm tay bằng dev server thật: bấm icon 1 → tải file → dùng chính file đó bấm "Nhập Excel" ngay → xác nhận preview đúng NV + đúng giá trị 2 cột, không lệch dòng (khớp TASK-REF/TASK-REF của SPEC); và thử lại 1 file cũ (1-dòng-header) đã từng nhập thành công trước đây để xác nhận TASK-REF (không hồi quy).
