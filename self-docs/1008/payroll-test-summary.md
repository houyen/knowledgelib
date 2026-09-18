---
type: draft
status: proposed
tags:
- docs-site-macos
- output-report
- testing
- playwright
- rbac
proposed: 2026-08-10
id: self-docs/1008/payroll-test-summary
canonical_question: 'Technical guide and specification: 100826-Core System-test-summary'
aliases:
- 100826-Core System-test-summary
- 100826 Core System test summary
entity_type: how_to
domain: self-docs > 1008
last_verified: 2026-09-17
---

# 100826-Core System-test-summary

## What
Thiết kế 74 kịch bản test cho 7 phân hệ Core System (Formula Engine, Core System Template, Salary Override, Core System Period Flow, RBAC, Bảng chấm công, Report Template Config) + xuất mỗi phân hệ 2 file Excel (Blind/Answer), dựng lại hạ tầng Playwright e2e cho máy local, và viết 6 spec Playwright mới (33 test tự động PASS).

## Output
- 74 kịch bản test grounded trên code thật (`Core System-backend`, `Core System-adapter`), mỗi phân hệ 2 file Excel tại `self-docs/files/`.
- Sửa hạ tầng e2e: bỏ phụ thuộc Docker trong `psql()` helper, vá fixture DB thiếu (period + attendance FAKE cho Tháng 06/2026), tắt `trace: "retain-on-failure"` (nguyên nhân thật của timeout giả 30s+, không phải "dev-mode nguội" như nghi ban đầu), sửa fixture `contract_type`/`is_foreigner` (ưu tiên cột mới hơn `emp_status` từ 040826).
- 6 spec Playwright mới: `Core System-template.spec.ts` (3), `Core System-override.spec.ts` (5), `Core System-period-flow.spec.ts` (5), `Core System-rbac.spec.ts` (3, cần quy trình restart backend đặc biệt), `report-template-config.spec.ts` (6) — cộng `Core System-formula.spec.ts` (10) + `smoke.spec.ts` (1) đã sửa. Tổng 33 test, chạy chung không đụng nhau, dọn dữ liệu sạch (xác nhận bằng truy vấn DB sau mỗi lần chạy).
- 4 phát hiện lệch giữa giả định ban đầu và code thật: (1) `SalaryComponentOverridesPanel` không có đường vào từ UI chính (mode "edit" chưa được dispatch); (2) lệch mã lỗi 400 (CellSet) vs 500 (CalculateOne) cho cùng loại lỗi nghiệp vụ; (3) `ReportTemplateConfig` TC04 chặn alias trùng mã thật ở bước CHẠY báo cáo, không phải bước LƯU — đã tự sửa lại Excel gốc; (4) `Core System-adapter` (Bảng chấm công) không có UI/HTTP endpoint ở nhánh hiện tại, dùng bộ Go test có sẵn (58 case) làm test tự động thay vì ép viết Playwright.
- Quy trình RBAC đặc biệt: dev-bypass gắn cố định 1 email qua `DEV_USER_EMAIL`, và `EnsureSuperAdmins` tự seed lại email đó vào `super_admins` mỗi lần khởi động — phải xoá tay dòng auto-seed để test đúng identity hạn chế. Đã khôi phục sạch `.env` + xoá dữ liệu test + restart backend về trạng thái ban đầu, xác nhận lại bằng smoke test.

## Files
| File | Action |
|------|--------|
| `self-docs/files/PayrollFormula-TestCase-{Blind,Answer}-100826.xlsx` | created |
| `self-docs/files/PayrollTemplate-TestCase-{Blind,Answer}-100826.xlsx` | created |
| `self-docs/files/SalaryOverride-TestCase-{Blind,Answer}-100826.xlsx` | created |
| `self-docs/files/PayrollPeriodFlow-TestCase-{Blind,Answer}-100826.xlsx` | created |
| `self-docs/files/RBAC-TestCase-{Blind,Answer}-100826.xlsx` | created |
| `self-docs/files/BangChamCong-TestCase-{Blind,Answer}-100826.xlsx` | created |
| `self-docs/files/ReportTemplateConfig-TestCase-{Blind,Answer}-100826.xlsx` | created (regenerated sau khi sửa TC04) |
| `Core System-frontend/e2e/Core System-template.spec.ts` | created |
| `Core System-frontend/e2e/Core System-override.spec.ts` | created |
| `Core System-frontend/e2e/Core System-period-flow.spec.ts` | created |
| `Core System-frontend/e2e/Core System-rbac.spec.ts` | created |
| `Core System-frontend/e2e/report-template-config.spec.ts` | created |
| `Core System-frontend/e2e/Core System-formula.spec.ts` | modified (psql local, contract_type fixture, timeout) |
| `Core System-frontend/e2e/smoke.spec.ts` | modified (timeout comment corrected) |
| `Core System-frontend/playwright.config.ts` | modified (trace off) |
| `llmwiki/html/100826-Core System-test-summary.html` | created |

## Notes
- Invoked via: `/docs-site-macos` skill
- Preview: `http://localhost:8765/llmwiki/html/100826-Core System-test-summary.html`

## Origin
- **Draft:** `wiki/sources/draft/100826-Core System-test-summary.md`
- **Commit:** _(filled by verify-before-commit)_
- **Date promoted:** _(filled by verify-before-commit)_
