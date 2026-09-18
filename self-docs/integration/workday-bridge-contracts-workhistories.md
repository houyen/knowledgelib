---
id: self-docs/integration/workday-bridge-contracts-workhistories
canonical_question: 'Technical guide and specification: Cầu nối Workday → `employee_contracts`
  + `employee_work_histories`'
aliases:
- Cầu nối Workday → `employee_contracts` + `employee_work_histories`
- Workday Bridge Contracts WorkHistories 170826
entity_type: how_to
domain: self-docs > integration
last_verified: 2026-09-17
---

# Cầu nối Workday → `employee_contracts` + `employee_work_histories` (170826)

**Trạng thái:** Đã thi hành, chưa merge vào `develop`.
**Nhánh:** `Core System-backend@feature/workday-bridge-contracts-workhistories`,
`Core System-adapter@feature/workday-bridge-transfer-changelog` (cả 2 tạo mới từ `origin/develop`).
**Tài liệu nguồn:** `llmwiki/wiki/sources/draft/170826-workday-bridge-contracts-workhistories.md`
(SPEC) + `170826-workday-bridge-contracts-workhistories-PLAN.md` (PLAN thi hành).

## Bối cảnh

Hai lượt hỏi liên tiếp của user — "employee_contracts hiện tại đang được lấy dữ liệu vào thế nào"
rồi "tương tự cho employee_work_histories; dữ liệu đều có thể lấy từ workday về" — dẫn tới điều tra
sâu bằng đọc code thật (backend + adapter, nhánh `develop` đầy đủ nhất mỗi repo, không suy đoán),
phát hiện:

- **`employee_contracts`**: 25.865 dòng, toàn bộ `source='pipeline'`, ghi trong đúng 1 khung 13
  giây ngày 14/05/2026 — snapshot đóng băng, không có luồng ghi nào đang chạy trong code hiện tại.
- **`employee_work_histories`**: 3 nguồn (`pipeline` 52.627, `hris` 24.211, `manual` 18) — `hris`
  là luồng sync HRIS portal cũ (`sync_service.go`) không có UI nào gọi tới; `manual` là UI "Điều
  chuyển" (`transfers/page.tsx`) đang dùng thật hàng ngày.
- **`Core System-adapter`** đã có sẵn dữ liệu Workday tương đương cho cả 2 (`wd_workers` mang field
  hợp đồng từ 01/08/2026, `wd_worker_transfer_events` từ 05/08/2026) nhưng chưa có cầu nối sang
  `payroll_engine`.

User yêu cầu gộp cả 2 việc vào 1 SPEC/PLAN rồi thi hành trong 1 lượt.

## Kiến trúc — tái dùng nguyên xi `/v1/changes` đã có

`internal/service/adapter_sync.go` (quyết định 04/08/2026): backend gọi
`GET /v1/changes?after=<id>&entity=<type>&limit=<n>` của adapter, không bao giờ kết nối thẳng DB
`payroll_adapter`. Endpoint này đọc `wd_change_log`, đã tổng quát hoá theo `entity` từ trước.

**Phát hiện A (contracts) — không cần đổi adapter:** payload `entity_type='worker'` trong
`wd_change_log` đã mang sẵn field hợp đồng (cùng payload Get_Workers, `Include_Employee_Contract_Data`
thêm 01/08/2026) — chỉ cần backend parse thêm field từ payload đang nhận, dùng chung con trỏ
`worker` hiện có.

**Phát hiện B (work histories) — bắt buộc sửa adapter:** `wd_worker_transfer_events`
(migration `0047`, 05/08/2026) không hề ghi vào `wd_change_log` — thêm đúng 1 điểm ghi mới trong
`InsertWorkerTransferEvent`, entity type mới `worker_transfer_event`.

## Thi hành

1. **Task 1 (GATE):** baseline backend 918 passed/8 failed (đã biết trước), adapter 163 passed/0
   failed. Migration `atlas/migrations/20260817020000_adapter_sync_state_worker_transfer_event.sql`
   seed cursor mới. Đưa DB `payroll_adapter` cục bộ (đồng bộ Workday lần cuối 31/07, thiếu migration
   từ `0047` trở đi) lên hiện hành bằng chạy `db.Migrate` trực tiếp qua chương trình Go tạm — xác
   nhận bảng `wd_worker_transfer_events` tồn tại thật sau đó.
2. **Task 2 (adapter):** `InsertWorkerTransferEvent` bọc transaction, ghi thêm `wd_change_log`
   (`entity_type="worker_transfer_event"`, `new_raw` chứa `workerWid`/`effectiveDate`/`beforeRaw`/
   `afterRaw`) — chỉ khi dòng `wd_worker_transfer_events` thật sự mới (không bị `ON CONFLICT DO
   NOTHING` bỏ qua). Thêm `insertChangeLogNoSyncRun` (hàm riêng, không sửa `insertChangeLog` gốc —
   `sync_run_id` ghi NULL vì `SyncWorkerTransferEvents` không có `syncRunID` sẵn). Test integration
   thật trên DB cục bộ (cần seed 1 dòng `wd_worker_transaction_logs` trước — FK `log_wid`), xác nhận
   idempotent (gọi 2 lần không tạo 2 dòng `wd_change_log`).
3. **Task 3 (backend):** tổng quát hoá `AdapterSyncService` — `entitySync{entityType, apply}`,
   `entities()` liệt kê 2 entity (`worker`, `worker_transfer_event`), `State()`/`Run()` đổi từ trả
   1 struct sang slice (xác nhận không nơi nào khác gọi ngoài `AdapterSyncHandler`, không cần sửa
   handler vì `writeJSON` nhận `interface{}`). Một entity lỗi không chặn entity khác — lỗi lưu vào
   `AdapterSyncResult.Error` của đúng entity đó.
4. **Task 4 (backend):** `mapWorkerToContract` (parse `Worker_Data.Employee_Contracts_Data.
   Employee_Contract_Data[0]`, nhân bản `asList`/`idsByType` từ `xmltree` của adapter vì 2 module
   riêng không import chéo được), `upsertEmployeeContract` (hris_id sinh bằng `uuid.NewSHA1`,
   namespace cố định `uuid.NewSHA1(uuid.NameSpaceOID, []byte("Core System.workday.employee_contracts"))`
   — ổn định qua nhiều lần sync). Trả `ok=false` nếu thiếu `Contract_ID`/`Contract_Start_Date` —
   không bịa ngày cho cột NOT NULL.
5. **Task 5 (backend):** `mapWorkerTransferEvent` (diff lấy `Business_Title` từ `afterRaw` —
   phạm vi cố ý thu hẹp: chỉ position/job title, không trích department vì đòi traversal
   `Organization_Data` phức tạp hơn, để trống thay vì bịa), `upsertEmployeeWorkHistory`
   (`source='workday'`, `hris_id` sinh từ `log_wid` cùng kỹ thuật UUID namespace).
6. **Task 6 — verify không dùng dữ liệu Workday thật** (môi trường không có kết nối Workday sống):
   dry-run `mapWorkerToContract`-tương-đương trên toàn bộ 8429 dòng `wd_change_log` entity `worker`
   thật tại local — kết quả `total=8429 withContract=0 parseErr=0` (0 lỗi parse, khớp đúng phát
   hiện dữ liệu local đồng bộ trước 01/08 nên không có field hợp đồng). Test suite đầy đủ sau khi
   sửa: backend 918 passed/8 failed (khớp baseline tuyệt đối, `comm` đối chiếu tên fail cho kết quả
   rỗng), adapter 163 passed/0 failed (từ 163/0 baseline, không đổi). `go build`/`go vet` sạch cả
   2 repo.

## Giới hạn — chưa xác minh Workday thật

- **Chưa re-sync `wd_workers` với `Include_Employee_Contract_Data`** trong môi trường này — DB
  `payroll_adapter` cục bộ đồng bộ lần cuối 31/07/2026, trước ngày thêm tính năng (01/08). Cần môi
  trường có kết nối Workday thật để xác nhận `mapWorkerToContract` đọc đúng dữ liệu thật (không chỉ
  fixture giả lập).
- **Chưa chạy `SyncWorkerTransferEvents` thật** — bảng `wd_worker_transfer_events` vừa được tạo
  (migration `0047` áp dụng ở Task 1), chưa có dữ liệu Workday thật nào. Adapter code tự ghi chú
  `workday.FetchWorkerOrgSnapshot` (nguồn `before_raw`/`after_raw`) **chưa được xác minh với lệnh
  gọi Workday thật** trong bất kỳ môi trường nào — PLAN này không sửa việc đó, chỉ xây cầu nối giả
  định dữ liệu đúng hình dạng đã tài liệu hoá trong code.
- Việc kế tiếp cần làm ở môi trường có kết nối Workday thật: (1) chạy sync worker thật, xác nhận
  `employee_contracts` nhận đúng dữ liệu; (2) chạy `SyncWorkerTransferEvents` thật lần đầu, xác
  nhận `FetchWorkerOrgSnapshot` trả đúng hình dạng đã giả định, rồi xác nhận `employee_work_histories`
  nhận đúng dữ liệu.

## Commit

**`Core System-backend@feature/workday-bridge-contracts-workhistories`** (chưa push, chưa merge):
- `8321f37` — chore(db): thêm con trỏ đồng bộ worker_transfer_event (170826)
- `63fc5c0` — refactor(sync): tổng quát hoá AdapterSyncService theo danh sách entity type (170826)
- `3a69894` — feat(sync): map + upsert employee_contracts từ entity worker (170826)
- `319793d` — feat(sync): map + upsert employee_work_histories từ entity worker_transfer_event (170826)

**`Core System-adapter@feature/workday-bridge-transfer-changelog`** (chưa push, chưa merge):
- `a152d98` — feat(sync): ghi wd_change_log cho worker_transfer_event (170826)

## Việc KHÔNG làm (Non-goals, ghi trong SPEC)

- Không xác minh kết nối Workday thật (xem Giới hạn ở trên).
- Không sửa cảnh báo "unverified" của `FetchWorkerOrgSnapshot` — việc riêng của `Core System-adapter`.
- Không đồng bộ hoá 2 luồng ghi độc lập hiện có của `employee_work_histories` (`hris`/`manual`) với
  nguồn `workday` mới — chạy song song, không thay thế.
- Không tắt luồng `hris`/HRIS portal cũ.
- Không xây UI hiển thị riêng nguồn `workday`.
- Không merge 2 nhánh vào `develop` trong phạm vi này — để user quyết định thời điểm.
