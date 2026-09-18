---
id: self-docs/files/payroll-adapter-190826-readme
canonical_question: 'Technical guide and specification: Dump DB adapter — `payroll_adapter`,
  19/08/2026'
aliases:
- Dump DB adapter — `payroll_adapter`, 19/08/2026
- Core System adapter 190826 README
entity_type: how_to
domain: self-docs > files
last_verified: 2026-09-17
---

# Dump DB adapter — `payroll_adapter`, 19/08/2026

Ảnh chụp database của `Core System-adapter` trên máy dev. Đây là **DB trung gian** giữa Workday và
`Core System-backend`: adapter kéo dữ liệu từ Workday vào đây, backend đọc lại qua `GET /v1/changes`.

| File | Nội dung | Kích thước |
|---|---|---|
| `payroll_adapter-full-190826.dump` | **Schema + TOÀN BỘ DỮ LIỆU**, định dạng custom (nén) | **81 MB** |
| `payroll_adapter-schema-190826.sql` | **Chỉ schema**, SQL thuần, đọc được bằng mắt | 116 KB |

Nguồn: DB `payroll_adapter`, PostgreSQL **14.18**, 511 MB trên đĩa, **55 bảng**, ~208.500 dòng.
Sinh bằng `pg_dump --no-owner --no-privileges`. Chỉ có schema `public`.

---

## ⚠️ Bản `-full-` chứa DỮ LIỆU WORKDAY THẬT

Payload SOAP nguyên bản của Workday, trong đó có họ tên, ngày sinh, email, lương, phụ cấp, nghỉ phép
của người thật.

| Bảng | Dòng | Dung lượng | Là gì |
|---|---|---|---|
| `wd_change_log` | 47.508 | 258 MB | nhật ký thay đổi + payload `new_raw` nguyên bản — **kênh backend đọc** |
| `wd_workers` | 4.211 | 72 MB | worker Workday, payload đầy đủ |
| `attendancecalc_precomputed` | 19.216 | 56 MB | cache tính chấm công |
| `raas_all_worker_time_off` | 12.294 | 24 MB | nghỉ phép theo worker |
| `wd_organization_links` | 38.011 | 13 MB | liên kết cây tổ chức |
| `wd_worker_transaction_logs` | 5.700 | 8,5 MB | log giao dịch (nguồn của transfer event) |

**KHÔNG chứa credential.** Đã quét xác nhận: không cột nào tên
`password`/`secret`/`token`/`credential`/`api_key`/`auth`, không bảng config nào, và 0 dòng
`wd_change_log` có chuỗi kiểu `"password"`/`"secret"`/`Bearer `. Thông tin đăng nhập Workday (ISU)
chỉ nằm trong `.env`, không vào DB.

**Xử lý như dữ liệu nội bộ:** đừng đưa lên kho công khai, đừng gửi ra ngoài công ty. Ai không có
quyền truy cập dữ liệu này thì đưa bản `payroll_adapter-schema-190826.sql` — bản đó **0 dòng dữ liệu**.

---

## Vì sao bản này hữu ích cho đội adapter

Ba con số trong tài liệu bàn giao (`Adapter-Workday-Handover-180826.md`) **đo trên chính DB này** —
nạp dump về là tự kiểm lại được, không phải tin lời:

```sql
-- 1) wd_change_log theo entity_type (20 loại, tổng 47.508)
SELECT entity_type, count(*) FROM wd_change_log GROUP BY 1 ORDER BY count(*) DESC;

-- 2) Nhánh Business_Title: 8.427 / 8.429  ← đã kiểm, có căn cứ dữ liệu thật
SELECT count(*) FILTER (WHERE new_raw->'Worker_Data'->'Employment_Data'->'Worker_Job_Data'
                             ->'Position_Data'->>'Business_Title' IS NOT NULL) || ' / ' || count(*)
FROM wd_change_log WHERE entity_type='worker';

-- 3) Nhánh hợp đồng: 0 / 8.429  ← CHƯA có một mẫu thật nào
SELECT count(*) FILTER (WHERE new_raw->'Worker_Data'->'Employee_Contracts_Data' IS NOT NULL)
       || ' / ' || count(*)
FROM wd_change_log WHERE entity_type='worker';

-- 4) Việc V0 trong tài liệu bàn giao: cả hai đều 0 trên DB local này
SELECT (SELECT count(*) FROM wd_worker_transfer_events)                      AS su_kien,
       (SELECT count(*) FROM wd_change_log
         WHERE entity_type='worker_transfer_event')                          AS da_bao;
```

Kết quả thật trên DB này: (2) = **8427 / 8429** · (3) = **0 / 8429** · (4) = **0 và 0**.

**Về 2 payload thiếu `Business_Title`:** `Worker_ID` = **100206** và **EE26000162**. Cả hai CÓ
`Position_Data` với 12 khoá (`Position_ID`, `Position_Reference`, `Scheduled_Weekly_Hours`,
`Working_FTE`…) nhưng **không có khoá `Business_Title`**. Đã kiểm cả 8.429 payload đều có
`Worker_Job_Data` kiểu `object`, không có dạng mảng nào. Backend sẽ ghi `position_name` rỗng cho
đúng 2 người đó — hành vi đúng, đã có test bao.

**Về (4):** DB local này **chưa có transfer event nào**, nên nó KHÔNG dùng để đo quy mô backfill
được. Việc V0 phải đếm trên **production của adapter**.

---

## Cách nạp

```bash
createdb payroll_adapter_ref
pg_restore -d payroll_adapter_ref --no-owner --no-privileges payroll_adapter-full-190826.dump
# hoặc chỉ schema:
psql -d payroll_adapter_ref -v ON_ERROR_STOP=1 -f payroll_adapter-schema-190826.sql
```
Thêm `-j4` cho nhanh. Nguồn PostgreSQL **14.18** — nạp lên 16 thì được, chiều ngược lại thì không.

---

## Liên quan

- `self-docs/files/payroll_engine-180826-README.md` — dump DB **backend** (`payroll_engine`, 79 bảng),
  phía bên kia của cùng đường dữ liệu
- `self-docs/Adapter-Workday-Handover-180826.md` — đội adapter đọc file này TRƯỚC (thứ tự việc V0→V4)
- `self-docs/Adapter-Workday-ChangeLog-Mapping-Template-180826.md` — hợp đồng dữ liệu `wd_change_log`
- `self-docs/Adapter-Workday-Implementation-And-Local-Test-180826.md` — sửa file nào, test local thế nào
