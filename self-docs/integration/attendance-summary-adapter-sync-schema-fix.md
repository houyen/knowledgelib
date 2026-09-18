---
id: self-docs/integration/attendance-summary-adapter-sync-schema-fix
canonical_question: 'Technical guide and specification: Sửa thiếu cột schema chặn
  `cmd/summary-sync --write` — 260826'
aliases:
- Sửa thiếu cột schema chặn `cmd/summary-sync --write` — 260826
- Attendance Summary Adapter Sync Schema Fix 260826
entity_type: how_to
domain: self-docs > integration
last_verified: 2026-09-17
---

# Sửa thiếu cột schema chặn `cmd/summary-sync --write` — 260826

**Bối cảnh:** cùng ngày, nhánh `develop_v1` của `Core System-backend` đang có 1 luồng rewrite
đang chạy dở (tác giả `ThaiDT <user@company.test>`, các commit `7749289`/`5036ca4`/`224f34b`/
`bf1f399`): thay đường sync `attendance_summary` cũ (Workday time block → `hris_attendance_daily`
→ gộp theo org) bằng đường mới đọc trực tiếp `GET /v1/attendance` của `Core System-adapter`
(`internal/service/adapter_summary_sync.go` + CLI mới `cmd/summary-sync`). Route HTTP cũ
`POST /hris/attendance-summary/generate-from-daily` đã bị **tắt hẳn** (trả lỗi hướng dẫn dùng
CLI mới), không phụ thuộc `ATTENDANCE_SOURCE` nữa.

Commit `bf1f399` (16:12 hôm nay) đã ghi rõ nguyên nhân gốc: 1 migration "v59" đã thêm 17 cột
trên máy gốc của tác giả (Phạm Bằng) **nhưng chưa từng được commit vào cây migration** —
`v60_attendance_summary_adapter_shape.sql` dọn lại phần đó (xoá 7 cột rác, thêm 1 số cột) nhưng
không đủ, và `bf1f399` đã vá tiếp `segment_no`/`department_code` cho v61/v62.

**Việc đã làm (tiếp nối đúng khuôn `bf1f399`):** chạy thử `cmd/summary-sync --write` lần đầu
tiên end-to-end trên máy này (sau khi restore DB `payroll_adapter` + dựng adapter service :8081,
xem `self-docs/` các file DB-restore/adapter-serve cùng ngày) — lộ ra **thêm 2 lớp lỗi schema**
mà `bf1f399` chưa bắt hết, vì khi đó có thể chưa từng chạy `--write` thật với dữ liệu adapter đầy đủ:

1. **Thiếu cột** (cùng loại lỗi migration "v59" mất — không phải lỗi migration KHÔNG áp được,
   mà cột CHƯA TỪNG được tạo ở đâu trong cây migration đã commit):
   - `v64_attendance_summary_start_end_date.sql` — thêm `start_date`/`end_date` (nullable, `date`)
     — dùng cho ngày bắt đầu/kết thúc của từng đoạn `departments[i]`.
   - `v65_attendance_summary_ot_meal_units.sql` — thêm 6 cột: `night_meal_units`,
     `sunday_meal_units`, `ot_weekday_normal_units`, `ot_weekend_normal_units`,
     `ot_holiday_normal_units`, `ot_off_in_lieu_units` (nullable, `numeric(10,2)`).
   - Cách tìm: `diff` toàn bộ `summaryUpsertCols` (Go, `attendance_summary_upsert_repo.go`)
     với cột thật trong DB (`information_schema.columns`) — tìm HẾT 1 lần thay vì sửa từng cột
     theo từng lỗi runtime lộ ra tuần tự (Postgres chỉ báo cột thiếu ĐẦU TIÊN gặp trong câu SQL).
2. **Cột quá hẹp** (lỗi khác hẳn — không phải cột thiếu):
   - `v66_attendance_summary_department_code_width.sql` — nới `department_code` từ
     `varchar(50)` → `varchar(500)`. Đo thật: `org_structure_code` (API adapter) thực chất là
     TÊN phòng ban có dấu/gạch dưới, không phải mã ngắn — mẫu dài nhất đo được (kỳ 8/2026,
     3.785 NV): `"Bộ_phận_Giải_pháp_Xây_dựng_Thông_minh_(Smart_Construction)"` (58 ký tự).
     Bảng này đã có tiền lệ y hệt: `org_structure_name` đặt sẵn `varchar(500)` đúng vì lý do
     này — áp cùng độ rộng, không tự đặt số khác.

**Không sửa `v59`/`v60`/`v61`/`v62`/`v63`** — cùng lý do `bf1f399` đã nêu: các file đó đã được
`schema_migrations` đánh dấu "applied" trên máy này, sửa vào đó không có tác dụng lại.

## Kiểm chứng

- Sau `v64`+`v65`: `comm -23` giữa danh sách cột code kỳ vọng và cột DB thật → **rỗng** (đủ hết).
- Chạy `go run ./cmd/summary-sync --month M --year 2026 --write` cho **cả 8 kỳ có trong
  `payroll_periods`** (01→08/2026): tất cả pass kiểm bất biến (Σ theo đoạn = Σ cấp nhân viên
  cho `standard_working_days`/`real_work_day`/`total_paid_days`/`night_meal`), ghi thành công,
  0 lỗi. Kết quả cuối `attendance_summary` theo kỳ: 01=3265, 02=3938 (2867 dòng cũ giữ vì đã
  chốt công), 03=3846, 04=4013, 05=3971, 06=3734, 07=3945, 08=3810 dòng.
- `go run ./cmd/Core System` (AUTO_MIGRATE=true) áp cả 3 migration mới sạch, healthy.

## Trạng thái git

`Core System-backend@develop_v1`: 3 file migration mới (`v64`/`v65`/`v66`), **chưa commit**
(nhánh đang có người khác/chính tác giả các commit `bf1f399` trở về trước làm việc dở —
để họ tự quyết commit theo đúng luồng rewrite đang chạy, không tự commit thay).
