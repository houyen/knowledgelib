---
id: self-docs/integration/adapter-workday-implementation-and-local-test
canonical_question: 'Technical guide and specification: Thi hành + kiểm thử local
  — cầu nối `wd_change_log`'
aliases:
- Thi hành + kiểm thử local — cầu nối `wd_change_log`
- Adapter Workday Implementation And Local Test 180826
entity_type: how_to
domain: self-docs > integration
last_verified: 2026-08-06
---

# Thi hành + kiểm thử local — cầu nối `wd_change_log` (180826)

**Gửi:** đội phát triển `Core System-adapter`
**Đọc sau** `Adapter-Workday-Handover-180826.md` (thứ tự việc V0→V4) và **cùng lúc với**
`Adapter-Workday-ChangeLog-Mapping-Template-180826.md` (hợp đồng field).

File này trả lời: **sửa file nào, ở dòng nào, và làm sao kiểm trên máy mình khi KHÔNG có kết nối
Workday.**

---

## 0. Trước khi gõ dòng code đầu tiên

### 0.1 Nhánh gốc

Làm trên nhánh mới tách từ **`origin/develop`**, không phải `develop` local.

```bash
git fetch origin
git checkout -b feature/wd-change-log-transfer-events origin/develop
```

> Trên máy backend kiểm ngày 18/08, `develop` local đang **cũ 196 commit** so với `origin/develop`
> — toàn bộ code transfer event chỉ có ở bản remote. Kiểm nhánh của bạn trước khi kết luận "code
> không tồn tại":
> ```bash
> git rev-list --left-right --count develop...origin/develop
> ```

### 0.2 Những thứ ĐÃ CÓ SẴN, không phải viết lại

| Thứ | Ở đâu | Ghi chú |
|---|---|---|
| Vòng lặp chụp transfer event | `internal/sync/sync_transfer_events.go` → `Runner.SyncWorkerTransferEvents` | Đã chạy, gọi `store.InsertWorkerTransferEvent` ở **dòng 64** |
| Đường re-fetch | cùng file → `Runner.RefreshTransferEventsMissingScheduledHours` | Gọi `store.RefreshWorkerTransferEvent` ở **dòng 108** |
| Ba hàm store | `internal/store/worker_transfer_events.go` | `PendingTransferEvents`, `InsertWorkerTransferEvent`, `RefreshWorkerTransferEvent` |
| Hàm ghi change log | `internal/store/raw.go:1791` → `insertChangeLog(ctx, tx, syncRunID, entityType, wid, changeType, oldRaw, newRaw)` | **Mẫu để tái dùng** |
| Endpoint backend đọc | `internal/api/changes.go` → `GET /v1/changes` | **Không cần đổi gì** |
| Lịch chạy | `cmd/adapter/main.go` → `transactionLogJob`, cron `TRANSACTION_LOG_SYNC_CRON` (mặc định `0 3 * * *`) | `SyncWorkerTransferEvents` chạy ngay sau sync transaction log |

**Việc thiếu duy nhất: hai chỗ ghi `wd_change_log`.** Vòng lặp đã chụp dữ liệu vào
`wd_worker_transfer_events` nhưng không báo cho backend biết.

### 0.3 Một lưu ý về `insertChangeLog` sẵn có

Hàm ở `raw.go:1791` **bắt buộc có `syncRunID`**, mà vòng lặp transfer event **không có sync run**
(nó không bọc `StartSyncRun`/`FinishSyncRun`). Cột `wd_change_log.sync_run_id` **cho phép NULL**
(FK tới `wd_sync_runs`, không có `NOT NULL`) — nên viết một biến thể ghi `NULL` là được, **không
cần tạo sync run giả**.

---

## 1. V1 — đường ghi cơ bản

**Sửa:** `internal/store/worker_transfer_events.go`, hàm `InsertWorkerTransferEvent`.

Hiện tại nó chạy đúng **một** câu `INSERT ... ON CONFLICT (log_wid) DO NOTHING` bằng `s.pool.Exec`.
Cần đổi thành **một transaction** làm hai việc: giữ nguyên câu cũ, rồi ghi thêm dòng
`wd_change_log` — **chỉ khi câu đầu thật sự chèn được dòng** (`RowsAffected() > 0`). Đó chính là cơ
chế idempotent: gọi lại lần hai thì `DO NOTHING` không chèn gì, nên cũng không sinh change log thứ hai.

Nội dung dòng `wd_change_log` và JSON `new_raw`: **§4 của hợp đồng dữ liệu**. Ba điểm dễ sai nhất:

| | Đúng | Sai thường gặp |
|---|---|---|
| `entity_type` | `'worker_transfer_event'` | thiếu chữ `_event` |
| `wid` | **`log_wid`** | `worker_wid` — hỏng `hris_id` phía backend |
| `change_type` | `'insert'` | |

`new_raw` là JSON 4 khoá **camelCase**: `workerWid`, `effectiveDate`, `beforeRaw`, `afterRaw`.
`beforeRaw`/`afterRaw` là `json.RawMessage` — nếu `nil` thì marshal ra `null`, backend hiểu và bỏ
qua sự kiện đó (đúng ý đồ).

### Kiểm V1 trên local — KHÔNG cần Workday

Không cần gọi Workday: gọi thẳng hàm store bằng Go test với JSON tự chế.

**Bẫy phải biết:** `wd_worker_transfer_events.log_wid` có **khoá ngoại** trỏ
`wd_worker_transaction_logs(wid)`. Phải chèn dòng cha trước, nếu không test fail vì FK chứ không
phải vì code sai.

```go
// internal/store/worker_transfer_events_test.go
func TestInsertWorkerTransferEvent_WritesChangeLog(t *testing.T) {
    pool := testPool(t)                 // DATABASE_URL local
    s := New(pool)
    ctx := context.Background()

    logWID := "test-log-wid-001"
    workerWID := "test-worker-wid"
    effDate := time.Date(2026, 8, 1, 0, 0, 0, 0, time.UTC)
    before := json.RawMessage(`{"Worker_Data":{"Worker_ID":"999001","Employment_Data":{}}}`)
    after := json.RawMessage(`{"Worker_Data":{"Worker_ID":"999001","Employment_Data":` +
        `{"Worker_Job_Data":{"Position_Data":{"Business_Title":"Senior Engineer"}}}}}`)

    // BẮT BUỘC: dòng cha, vì log_wid có FK trỏ wd_worker_transaction_logs(wid)
    _, err := pool.Exec(ctx,
        `INSERT INTO wd_worker_transaction_logs (wid, worker_wid, raw) VALUES ($1,$2,'{}'::jsonb)`,
        logWID, workerWID)
    if err != nil { t.Fatalf("setup: %v", err) }

    t.Cleanup(func() {
        pool.Exec(ctx, `DELETE FROM wd_change_log WHERE wid=$1`, logWID)
        pool.Exec(ctx, `DELETE FROM wd_worker_transfer_events WHERE log_wid=$1`, logWID)
        pool.Exec(ctx, `DELETE FROM wd_worker_transaction_logs WHERE wid=$1`, logWID)
    })

    // lần 1 → phải có đúng 1 dòng change log, entity_type/new_raw đúng
    // lần 2 (cùng logWID) → VẪN đúng 1 dòng   ← đây là điều kiện idempotent
}
```

Chạy:
```bash
adapter migrate                       # dựng schema nếu DB local còn trống
go test ./internal/store/ -run TransferEvent -count=1 -v
```

Sau đó kiểm bằng SQL — **câu (1) và (4) ở §9** của hợp đồng dữ liệu.

---

## 2. V2 — múi giờ `effectiveDate`

**Sửa:** cùng chỗ vừa viết ở V1 (hàm dựng `new_raw`).

`wd_worker_transaction_logs.effective_moment` là **`timestamptz`**. Cột
`wd_worker_transfer_events.effective_date` là **`DATE`** — PostgreSQL quy đổi theo `TimeZone` của
session khi ghi. Còn chuỗi `effectiveDate` trong JSON thì do Go format, theo location của biến
`time.Time`. Hai đường này **có thể ra hai ngày khác nhau**.

```
2026-08-06 00:00+07  →  lưu 2026-08-05T17:00:00Z  →  Format() theo UTC ra "2026-08-05"   ✗ lệch 1 ngày
```

Quy đổi sang `Asia/Ho_Chi_Minh` trước khi format.

### Kiểm V2 — chọn đúng mốc dễ lộ lỗi

Lỗi này **chỉ lộ** với mốc rơi vào 17:00–23:59 UTC. Tìm sự kiện như vậy trong DB:

```sql
SELECT wid, effective_moment,
       (effective_moment AT TIME ZONE 'Asia/Ho_Chi_Minh')::date AS ngay_vn,
       (effective_moment AT TIME ZONE 'UTC')::date              AS ngay_utc
FROM wd_worker_transaction_logs
WHERE effective_moment IS NOT NULL
  AND EXTRACT(hour FROM effective_moment AT TIME ZONE 'UTC') >= 17
LIMIT 5;
```

Rồi khẳng định `new_raw->>'effectiveDate'` bằng cột `ngay_vn`, **không** bằng `ngay_utc`:

```sql
SELECT e.log_wid, e.effective_date AS cot_date,
       c.new_raw->>'effectiveDate' AS json_date,
       (e.effective_date::text = c.new_raw->>'effectiveDate') AS khop
FROM wd_worker_transfer_events e
JOIN wd_change_log c ON c.wid = e.log_wid AND c.entity_type='worker_transfer_event'
ORDER BY e.effective_date DESC LIMIT 20;   -- cột "khop" phải TRUE hết
```

Nếu DB local chưa có sự kiện thật nào rơi vào khung giờ đó, tự chèn một dòng
`wd_worker_transaction_logs` với `effective_moment = '2026-08-05 17:30:00+00'` rồi chạy lại — kỳ
vọng `effectiveDate` = `"2026-08-06"`.

---

## 3. V3 — đường refresh cũng sinh change log

**Sửa:** `internal/store/worker_transfer_events.go`, hàm `RefreshWorkerTransferEvent`
(gọi từ `internal/sync/sync_transfer_events.go:108`).

Hàm này đang chạy `UPDATE ... SET before_raw, after_raw, snapshotted_at` bằng `s.pool.Exec` và
không ghi change log. Đổi thành transaction: giữ câu `UPDATE`, rồi ghi thêm dòng `wd_change_log`
`change_type='update'` — tái dùng đúng hàm dựng `new_raw` của V1.

Khác V1 ở một điểm: ở đây **không** dựa vào `RowsAffected` để quyết định có ghi change log hay
không theo kiểu idempotent — refresh là hành động cố ý ghi đè, mỗi lần refresh thật sự cập nhật
dòng thì nên có một dòng `update` tương ứng để backend biết mà đọc lại. (Vẫn nên bỏ qua nếu
`UPDATE` khớp 0 dòng, vì khi đó chẳng có gì thay đổi.)

### Vì sao V3 không phải chi tiết nhỏ

Đúng những dòng cần refresh là dòng thiếu `Employment_Data` — snapshot chụp trước 06/08, trước khi
`Include_Employment_Information` được thêm vào `FetchWorkerOrgSnapshot`. Thiếu `Employment_Data`
nghĩa là thiếu `Position_Data.Business_Title`, **đúng trường duy nhất backend lấy**. Không có V3 thì
backend đã ghi work-history với `position_name`/`job_title_name` rỗng, và vì bản vá không bao giờ
được thông báo, nó **rỗng vĩnh viễn**. Hỏng im lặng, không có lỗi nào để lần ra.

### Kiểm V3 trên local

```sql
-- 1) tìm/dựng một dòng đã có nhưng thiếu Employment_Data
SELECT log_wid FROM wd_worker_transfer_events
WHERE after_raw IS NOT NULL
  AND after_raw->'Worker_Data'->'Employment_Data' IS NULL
LIMIT 5;
```

Gọi `RefreshWorkerTransferEvent` cho `log_wid` đó (test Go, hoặc chạy
`RefreshTransferEventsMissingScheduledHours` nếu môi trường có Workday), rồi:

```sql
SELECT change_type, new_raw->'afterRaw'->'Worker_Data'->'Employment_Data'
                          ->'Worker_Job_Data'->'Position_Data'->>'Business_Title' AS title
FROM wd_change_log
WHERE entity_type='worker_transfer_event' AND wid='<log_wid>'
ORDER BY id;
```
Kỳ vọng: có thêm dòng `update`, và `title` **khác NULL**.

---

## 4. V4 — backfill

Làm **sau cùng** — nó tái dùng hàm dựng `new_raw` của V1 và định dạng ngày của V2.

### Đếm trước (chính là V0, chạy trên **production**)

```sql
SELECT (SELECT count(*) FROM wd_worker_transfer_events)                       AS su_kien,
       (SELECT count(DISTINCT wid) FROM wd_change_log
         WHERE entity_type='worker_transfer_event')                           AS da_bao,
       (SELECT count(*) FROM wd_worker_transfer_events e
         WHERE NOT EXISTS (SELECT 1 FROM wd_change_log c
                            WHERE c.entity_type='worker_transfer_event' AND c.wid = e.log_wid))
                                                                              AS con_thieu;
```

### Cách làm

Một lệnh CLI dùng một lần (kiểu `adapter backfill-transfer-changelog`) hoặc script SQL — tuỳ bạn.
Yêu cầu:

- Duyệt các `log_wid` thuộc cột `con_thieu` ở trên, **theo `effective_date` tăng dần**.
- Dựng `new_raw` bằng **đúng hàm của V1** (không viết lại), lấy `beforeRaw`/`afterRaw` từ chính
  cột `before_raw`/`after_raw` đang có sẵn — **không gọi lại Workday**.
- `change_type='insert'`.
- Chạy lại lần hai phải **không** sinh thêm dòng nào (dùng cùng điều kiện `NOT EXISTS`).

**Về thứ tự `id`:** backend chạy theo con trỏ `wd_change_log.id` tăng dần. Chèn backfill với `id`
mới ở cuối bảng là **đúng** — backend sẽ đọc được. Đừng cố nhét `id` nhỏ để "đúng thứ tự lịch sử":
dòng nào có `id` nhỏ hơn con trỏ hiện tại của backend sẽ **không bao giờ được xử lý**.

### Kiểm V4

Chạy lại câu đếm ở trên — `con_thieu` phải bằng **0**, và `su_kien` = `da_bao`. Chạy script lần
thứ hai, hai số **không đổi**.

---

## 5. Kiểm end-to-end với backend (làm cùng đội backend)

Bốn việc trên kiểm được hoàn toàn bằng SQL ở phía bạn. Bước này để xác nhận backend đọc đúng.

```bash
# 1) adapter local
adapter migrate
API_ADDR=:8080 SYNC_API_TOKEN=devtoken adapter serve

# 2) backend local (đội backend chạy) — trỏ vào adapter của bạn
WD_ADAPTER_URL=http://localhost:8080 \
WD_ADAPTER_SECRET=devtoken \
go run ./cmd/Core System

# 3) kích một lượt kéo
curl -X POST -H "Authorization: Bearer dev" localhost:8080/api/v1/adapter-sync/pull
curl        -H "Authorization: Bearer dev" localhost:8080/api/v1/adapter-sync/state
```

`/pull` trả **mảng**, một phần tử mỗi `entity_type`. Đọc phần tử `worker_transfer_event`:
`applied` là số dòng work-history thật sự ghi được, `error` rỗng là không có lỗi.

Rồi kiểm phía DB backend:
```sql
SELECT employee_code, position_name, job_title_name, date_effective
FROM employee_work_histories WHERE source='workday'
ORDER BY updated_at DESC LIMIT 10;
```

**Điều dễ gây hiểu nhầm:** nếu `applied = 0` mà không có lỗi, phần lớn là do `Worker_ID` trong
`afterRaw` **không khớp `employees.employee_code` nào** ở DB backend — backend cố ý chỉ cập nhật
người đã có, không tạo mới. Khi test, lấy một `employee_code` có thật từ DB backend rồi đặt vào
`Worker_ID` của dữ liệu giả.

---

## 6. Checklist trước khi báo xong

| | Kiểm | Kỳ vọng |
|---|---|---|
| ☐ | §9 câu (1) | có `worker_transfer_event`, cả `insert` lẫn `update` |
| ☐ | §9 câu (2) / §4 câu đếm | `su_kien` = `da_bao`, `con_thieu` = 0 |
| ☐ | §9 câu (3) | 4 khoá camelCase đủ; `worker_id` và `business_title` khác `NULL` |
| ☐ | §9 câu (4) | **rỗng** (không `wid` nào trùng ở `change_type='insert'`) |
| ☐ | §2 câu so ngày | cột `khop` **TRUE** hết |
| ☐ | `go build ./... && go vet ./...` | rc=0 |
| ☐ | `go test ./internal/store/ -count=1` | pass, không để lại dòng rác |
| ☐ | Chạy backfill lần hai | số liệu **không đổi** |

Gửi kèm kết quả 5 câu SQL khi báo xong.

---

## 7. Ba điều KHÔNG được làm

1. **Đừng điền** `work_history_type`, `decision_no`, `decision_type`, `org_structure_id`,
   `job_grade` — backend cố ý để trống. Nhờ đúng những cột đó rỗng mà dòng do Workday sinh **không
   lọt vào các truy vấn tính lương**. Điền bừa là chạm thẳng vào kết quả tính lương.
2. **Đừng đổi tên khoá** camelCase, **đừng đổi `wid` sang `worker_wid`**. Cả hai làm backend bỏ qua
   dữ liệu **im lặng**, không báo lỗi.
3. **Đừng bỏ** `Include_Employee_Contract_Data` khỏi request `Get_Workers`, và đừng để
   `Employee_Contracts_Data` đổi vị trí trong payload. Nhánh hợp đồng của backend phụ thuộc vào nó.

Bảng đầy đủ "đổi X → backend hỏng Y": **§8** của hợp đồng dữ liệu.

---

## 8. Câu hỏi cần trả lời ngược lại backend

| # | Câu hỏi | Vì sao cần |
|---|---|---|
| 1 | Hai con số ở §4 (đếm trên **production**) | Biết V4 là việc thật hay chỉ là thủ tục |
| 2 | **`Contract_ID` của Workday có duy nhất toàn cục không?** | Backend sinh `employee_contracts.hris_id` bằng UUIDv5 từ nó. Nếu Workday tái dùng cùng `Contract_ID` cho hai hợp đồng khác nhau, hai hợp đồng sẽ **gộp thành một dòng, im lặng** |
| 3 | Báo khi xong V4 | Để hai bên cùng chạy một lượt sync thật và soi kết quả |

Về (3): nhánh `Business_Title` backend đã kiểm trên **8.427/8.429** payload `worker` thật (2 payload
còn lại có `Position_Data` nhưng thiếu khoá `Business_Title` — không phải lỗi, backend ghi
`position_name` rỗng và có test bao), nhưng nhánh `Employee_Contracts_Data` là **0/8.429** — chưa
có **một mẫu thật nào**. Lượt sync thật đó là
điều kiện để bật chạy định kỳ trên production.
