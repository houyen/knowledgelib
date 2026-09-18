---
id: self-docs/files/payroll-engine-180826-readme
canonical_question: 'Technical guide and specification: Dump DB backend — `payroll_engine`,
  18/08/2026'
aliases:
- Dump DB backend — `payroll_engine`, 18/08/2026
- Core System engine 180826 README
entity_type: architecture_explainer
domain: self-docs > files
last_verified: 2026-09-17
---

# Dump DB backend — `payroll_engine`, 18/08/2026

Ảnh chụp database của `Core System-backend` trên máy dev, tức **trạng thái đích** sau đợt dọn dẹp DB
17–18/08 và cầu nối Workday.

| File | Nội dung | Kích thước |
|---|---|---|
| `payroll_engine-full-180826.dump` | **Schema + TOÀN BỘ DỮ LIỆU**, định dạng custom (nén) | 42 MB |
| `payroll_engine-schema-180826.sql` | **Chỉ schema**, SQL thuần, đọc được bằng mắt | 161 KB |

Nguồn: DB `payroll_engine`, PostgreSQL **14.18**. Sinh bằng `pg_dump --no-owner --no-privileges`.

---

## ⚠️ Bản `-full-` chứa DỮ LIỆU NHÂN SỰ THẬT

Không phải dữ liệu mẫu. Trong đó có:

| Bảng | Dòng | Gồm |
|---|---|---|
| `employees` | 12.044 | họ tên, email, số CCCD, ngày sinh, địa chỉ, lương cơ bản, lương bảo hiểm |
| `employee_work_histories` | 76.856 | lịch sử chức danh, phòng ban, lương theo thời gian |
| `employee_contracts` | 25.865 | số hợp đồng, loại, ngày hiệu lực |
| `employee_dependents` | 24.530 | người phụ thuộc — tên, quan hệ, giấy tờ |
| `employee_bank_accounts` | 10.700 | số tài khoản ngân hàng |
| `payroll_records` | 6.438 | kết quả tính lương từng kỳ |
| `employee_roles`, `super_admins` | 26, 3 | ai được cấp quyền gì |

**Xử lý như dữ liệu nội bộ:** đừng đưa lên kho công khai, đừng gửi ra ngoài công ty, đừng nạp vào
môi trường ai cũng vào được. Chỉ dùng nội bộ đội đã có sẵn quyền truy cập dữ liệu tương đương.

Cần đưa cho người **không** có quyền đó thì dùng `payroll_engine-schema-180826.sql` — bản đó
**0 dòng dữ liệu**, đã quét xác nhận 0 email và 0 token/khoá thật.

---

## Cấu trúc

| | |
|---|---|
| Bảng | **79** (+ `atlas_schema_revisions`, sổ ghi nội bộ của Atlas) |
| Index | 242 |
| Khoá ngoại | 63 |
| Function + trigger | 1 + 1 (`employee_roles_fill_email`) |
| Tổng số dòng | ~38.900 (thống kê `pg_stat_user_tables`) |

Bảng nhiều dòng nhất: `attendance_summary` 13.026 · `employees` 12.044 · `payroll_records` 6.438 ·
`audit_logs` 2.673 · `graduate_schools` 1.123 · `permissions` 1.008.

---

## Cách nạp

**Bản đầy đủ** — định dạng custom, phải dùng `pg_restore`:
```bash
createdb payroll_ref
pg_restore -d payroll_ref --no-owner --no-privileges payroll_engine-full-180826.dump
```
Thêm `-j4` cho nhanh. Cảnh báo về `atlas_schema_revisions` nếu có thì bỏ qua được.

**Bản schema-only** — SQL thuần:
```bash
createdb payroll_ref
psql -d payroll_ref -v ON_ERROR_STOP=1 -f payroll_engine-schema-180826.sql
```

---

## Bốn lưu ý khi đọc

1. **79 bảng là trạng thái SAU đợt dọn.** Production ngày 17/08 còn 146 bảng; sau khi merge
   `release/uat-180826` và apply 11 migration, nó về đúng 79 bảng và danh sách trùng khít bản dump
   này. Xem `self-docs/DB-Cleanup-Deploy-Runbook-180826.md`.
2. **Đây KHÔNG phải `internal/db/schema.sql` của repo.** File trong repo hiện thiếu 10 bảng và 10
   cột so với DB thật — drift có sẵn từ trước, đã ghi cảnh báo ở đầu chính file đó.
   **Hai bên lệch nhau thì tin bản dump này.**
3. PostgreSQL nguồn là **14.18**. Production chạy **16.x** — nạp lên 16 thì được, chiều ngược lại
   (dump từ 16 về 14) thì không.
4. Muốn xem nhanh dạng danh sách thay vì đọc SQL: `internal/db/tables_db.md` (ảnh chụp phía DB) và
   `internal/db/tables_code.md` (dẫn xuất từ `schema.sql` của repo).

## Liên quan

- `self-docs/DB-Cleanup-Deploy-Runbook-180826.md` — cách đưa production về đúng trạng thái này
- `self-docs/Review-DB-Cleanup-Workday-Bridge-180826.md` — vì sao 32 bảng + 28 cột bị xoá
- `llmwiki/wiki/sources/draft/180826-atlas-baseline-schema-truth-PLAN.md` — nợ hạ tầng schema chưa xử lý
