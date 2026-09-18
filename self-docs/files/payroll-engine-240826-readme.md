---
id: self-docs/files/payroll-engine-240826-readme
canonical_question: 'Technical guide and specification: payroll_engine — dump 24/08/2026'
aliases:
- payroll_engine — dump 24/08/2026
- Core System engine 240826 README
entity_type: architecture_explainer
domain: self-docs > files
last_verified: 2026-09-17
---

# payroll_engine — dump 24/08/2026 (DB dev, đã sửa `employees.company_code`)

## File
- `payroll_engine-full-240826.dump` — 32.5 MB, `pg_dump -Fc` (custom format, restore bằng `pg_restore`), schema `atlas_schema_revisions` bị loại (role dump không có quyền đọc, không ảnh hưởng dữ liệu nghiệp vụ).
- Nguồn: DB dev local `payroll_engine` (PostgreSQL 14.18), **có dữ liệu nhân viên thật** (tên/email/CCCD/lương/tài khoản ngân hàng...) — **giữ nguyên, KHÔNG mask** theo yêu cầu.

⚠️ **Cảnh báo dữ liệu thật:** file này chứa PII thật của nhân viên Enterprise/Unicons (họ tên, số CCCD, số tài khoản ngân hàng, lương...). Chỉ gửi cho người có quyền xử lý dữ liệu nhân sự thật. Không đăng công khai.

## Bối cảnh — khác gì so với DB gốc

Đây **không phải** dump nguyên trạng từ prod. Trong phiên làm việc 24/08/2026 đã chỉnh sửa trực tiếp trên DB dev này để dựng **bộ data mẫu 3 công ty** phục vụ test RBAC company-scoping + lên kế hoạch sync company từ Workday adapter:

1. **Xoá 7.344 nhân viên đã nghỉ việc không có lịch sử lương/công** (`date_quit IS NOT NULL` và không có `payroll_records`/`payroll_manual_inputs`/`attendance_records`) — giữ lại 671 người đã nghỉ nhưng có lịch sử lương (không xoá được vì FK), và toàn bộ người đang làm.
2. **Đồng bộ lại `employees.status`** theo `date_quit` (`date_quit IS NULL` → `active`, ngược lại → `inactive`) — trước đó `status` bị lệch (đã có 2.624 dòng `status='active'` nhưng thực tế đã nghỉ, do chưa từng được sync qua HRIS sau khi tạo).
3. **Rà + gán lại `employees.company_code`** theo quy tắc: mã nhân viên bắt đầu bằng số `0` → `Enterprise` (Enterprise), bắt đầu bằng số `1` → `UNI` (Unicons) — 0 dòng cần đổi vì đã đúng sẵn với mã số; mã có prefix chữ (I/S/A/E/T/M/`-`, 660 dòng) giữ nguyên `company_code` cũ theo quyết định của người yêu cầu (không áp quy tắc cho mã chữ).
4. **Xoá công ty `CTC`** — 1 dòng trùng tên "Enterprise" với `Enterprise` trong bảng `companies`, không còn nhân viên/dữ liệu nào tham chiếu tới.

## Số liệu sau khi sửa

| | Số dòng |
|---|---|
| `employees` tổng | 4.701 |
| `employees` company_code=Enterprise, status=active | 3.162 |
| `employees` company_code=Enterprise, status=inactive | 671 |
| `employees` company_code=UNI, status=active | 868 |
| `payroll_records` | 6.459 (100% thuộc Enterprise — UNI/CVT hiện chưa có payroll_records nào) |
| `employee_roles` | 27 (26 dòng gán quyền thật + 1 dòng `user@company.test` / role `cb_staff` / scope Enterprise, dùng để test RBAC company-scoping, có thể xoá nếu không cần) |

**`companies`** — 3 dòng (đã xoá `CTC`):

| code | name | hris_id |
|---|---|---|
| Enterprise | Công ty Cổ phần Xây dựng Enterprise | (trống) |
| UNI | Công ty Cổ phần Unicons | (trống) |
| CVT | Công ty Cổ phần Covestcons | (trống) |

`hris_id` cả 3 dòng đang **trống** — đây là cột cần điền `Organization_Reference_ID` (Workday) khi triển khai sync company tự động (xem prompt kế hoạch đã gửi kèm riêng).

## Gap còn tồn (chưa sửa trong bản dump này, để tham khảo khi lên kế hoạch)

- **Covestcons (CVT): 0 dữ liệu tuyệt đối** — 0 employees, 0 payroll_records, 0 attendance.
- **UNI không có `org_structures` (phòng ban) nào** — 868 NV UNI chỉ có `department`/`department_code` dạng text tự do, chưa map sang bảng `org_structures`.
- **`org_structures.company_id`** — NULL 100% (883/883 dòng), chưa có đường sync nào ghi cột này.
- **`employee_dependents.company_code`** — cột denormalize, còn lệch với `company_code` của nhân viên cha cho ~3.045 dòng thuộc NV UNI (vẫn ghi Enterprise).
- **`approval_rules`/`approval_requests`** — 0 dòng, tính năng có sẵn trong schema nhưng chưa từng seed data.

## Restore

```bash
createdb payroll_engine_restore_240826
pg_restore -d payroll_engine_restore_240826 --no-owner --no-privileges payroll_engine-full-240826.dump
```
