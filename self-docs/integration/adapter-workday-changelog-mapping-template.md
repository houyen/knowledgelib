---
id: self-docs/integration/adapter-workday-changelog-mapping-template
canonical_question: 'Technical guide and specification: Template mapping `wd_change_log`
  — hợp đồng dữ liệu Adapter → Backend'
aliases:
- Template mapping `wd_change_log` — hợp đồng dữ liệu Adapter → Backend
- Adapter Workday ChangeLog Mapping Template 180826
entity_type: how_to
domain: self-docs > integration
last_verified: 2026-08-06
---

# Template mapping `wd_change_log` — hợp đồng dữ liệu Adapter → Backend (180826)

**Đối tượng đọc:** đội phát triển `Core System-adapter`.
**Người phát hành:** đội `Core System-backend`.
**Trạng thái:** phía Backend ĐÃ sẵn sàng nhận (nhánh `feature/workday-bridge-contracts-workhistories`).
Phía Adapter còn **3 việc bắt buộc** ở §6 — chưa làm thì tính năng chỉ chạy được một nửa.

> **Đọc `self-docs/Adapter-Workday-Handover-180826.md` TRƯỚC file này.** Đó là bản hướng dẫn thứ tự
> công việc (V0→V4) và điều kiện xong từng bước. File này là tài liệu **tra cứu field**, không phải
> tài liệu chỉ thứ tự làm.

---

## 1. Ranh giới và kênh duy nhất

Dòng dữ liệu: **Workday → `Core System-adapter` → `Core System-backend`**.

Backend **không bao giờ** kết nối thẳng vào database của adapter (quyết định kiến trúc 04/08/2026:
nối thẳng sẽ buộc backend phụ thuộc vào 53 bảng mà adapter tự do đổi bằng runner migration riêng).
Toàn bộ trao đổi đi qua đúng một endpoint đọc:

```
GET /v1/changes?after=<id>&entity=<entity_type>&limit=<n>
Authorization: Bearer <SYNC_API_TOKEN>

→ {"changes":[{id, entityType, wid, changeType, newRaw, changedAt}], "lastId":<id>, "hasMore":bool}
```

Endpoint này **đã tồn tại và không cần đổi**. Nó đọc thẳng bảng `wd_change_log`, lọc theo
`entity_type`, sắp theo `id`. Việc của Adapter chỉ là **ghi đúng dòng vào `wd_change_log`**.

## 2. Giao thức con trỏ (Backend tự lo, ghi ở đây để hiểu ràng buộc)

Backend giữ **một con trỏ cho mỗi `entity_type`** trong bảng `adapter_sync_state.last_change_id`,
hỏi `?after=<con trỏ>` rồi tiến con trỏ trong cùng transaction với lần ghi dữ liệu.

Ràng buộc suy ra cho Adapter — **`wd_change_log.id` phải tăng đơn điệu theo thứ tự thay đổi thực
tế** (hiện là `BIGSERIAL`, đúng). Nếu có dòng nào được chèn với `id` NHỎ HƠN một dòng backend đã
đọc qua, dòng đó sẽ không bao giờ được xử lý — con trỏ đã vượt qua nó rồi.

## 3. entity `worker` — ĐANG CHẠY, không đổi gì

Đã hoạt động từ 13/08. `new_raw` là **nguyên đối tượng worker** (`{"Worker_Data": {...}}`) —
chính là `json.Marshal(worker)` trong `internal/workday/get_workers.go`.

Backend đọc đúng những nhánh sau. Nhánh nào vắng thì backend **giữ nguyên giá trị HRIS đang có**
(`COALESCE(NULLIF(...))`), không ghi đè bằng rỗng.

| Đường dẫn JSON trong `new_raw` | Cột đích `employees` | Kiểu / giới hạn | Bắt buộc |
|---|---|---|---|
| `Worker_Data.Worker_ID` | `employee_code` (khoá khớp) | VARCHAR(50) | **Có** — thiếu là bỏ qua cả bản ghi |
| `Worker_Data.Personal_Data.Name_Data.Legal_Name_Data.Name_Detail_Data.@Formatted_Name` | `full_name` | — | Không |
| ↳ hoặc `First_Name` / `Middle_Name` / `Last_Name` (ghép Họ-Đệm-Tên) | `full_name` | — | Không |
| `Worker_Data.Personal_Data.Gender_Reference.@Descriptor` | `gender` | — | Không |
| `Worker_Data.Personal_Data.Birth_Date` | `date_of_birth` | `YYYY-MM-DD` hoặc RFC3339 | Không |
| `Worker_Data.Personal_Data.Citizenship_Reference.@Descriptor` | `nationality` | — | Không |
| `Worker_Data.Personal_Data.Contact_Data.Email_Address_Data[].Email_Address` | `email` | lấy phần tử đầu không rỗng | Không |

**Lưu ý về `@Formatted_Name`:** Workday trả dạng `"Nguyen Van Vinh (Nguyễn Văn Vinh)"`. Backend tự
tách lấy phần trong ngoặc khi phần đó có ký tự ngoài ASCII. Adapter **không cần xử lý gì thêm**.

### 3b. Hợp đồng — đi kèm CÙNG payload `worker`, không cần entity riêng

Từ 01/08/2026 request đã bật `<wd:Include_Employee_Contract_Data>1</...>` nên `new_raw` mang sẵn
nhánh hợp đồng. Backend lấy **phần tử ĐẦU TIÊN** của danh sách (khớp `workerEmployeeContract`).

Gốc: `Worker_Data.Employee_Contracts_Data.Employee_Contract_Data[0]` — là con TRỰC TIẾP của
`Worker_Data`, **không** lồng dưới `Employment_Data`.

| Trường | Cột đích `employee_contracts` | Kiểu / giới hạn | Bắt buộc |
|---|---|---|---|
| `Contract_ID` | `contract_no` | **VARCHAR(100)** | **Có** — thiếu là bỏ qua hợp đồng |
| `Contract_Start_Date` | `date_start` | DATE **NOT NULL**, `YYYY-MM-DD` | **Có** — thiếu là bỏ qua hợp đồng |
| `Contract_Status_Reference` → ID có `@type="Employee_Contract_Status_ID"` | `sign_status` | **VARCHAR(50)** | Không |
| `Contract_Type_Reference` → ID có `@type="Employee_Contract_Type_ID"` | `contract_type_name` | **VARCHAR(255)** | Không |

`Contract_ID` còn được dùng để sinh `employee_contracts.hris_id` (UUIDv5, namespace cố định) —
xem §7.

Reference object có dạng `{"ID": [{"@type": "...", "#text": "..."}]}`, và có thể là **object đơn
hoặc mảng** tuỳ số phần tử; backend xử lý cả hai.

## 4. entity `worker_transfer_event` — **MỚI, Adapter phải làm**

Nguồn: bảng `wd_worker_transfer_events` (đã có từ 05/08). Việc còn thiếu là **ghi thêm một dòng
`wd_change_log`** mỗi khi bảng đó có dòng mới hoặc được cập nhật.

### Dòng `wd_change_log` phải có

| Cột | Giá trị |
|---|---|
| `entity_type` | `'worker_transfer_event'` (đúng chuỗi này) |
| `wid` | **`log_wid`** — KHÔNG phải `worker_wid`. Backend dùng nó sinh `employee_work_histories.hris_id`. |
| `change_type` | `'insert'` cho dòng mới, `'update'` cho lần refresh (§6-A) |
| `old_raw` | `NULL` |
| `new_raw` | JSON ở dưới |
| `sync_run_id` | `NULL` được phép (cột nullable) — vòng lặp theo-sự-kiện không có sync run |

### Hình dạng `new_raw` — đúng 4 khoá, **camelCase**

```json
{
  "workerWid":     "<wd_worker_transfer_events.worker_wid>",
  "effectiveDate": "2026-08-06",
  "beforeRaw":     { "Worker_Data": { ... } },
  "afterRaw":      { "Worker_Data": { ... } }
}
```

| Khoá | Kiểu | Backend dùng làm gì |
|---|---|---|
| `workerWid` | string | Hiện chưa dùng (dự phòng đối chiếu) |
| `effectiveDate` | string `YYYY-MM-DD` | `employee_work_histories.date_effective` — xem §6-C |
| `beforeRaw` | object hoặc `null` | Hiện chưa dùng |
| `afterRaw` | object hoặc `null` | **Nguồn của mọi giá trị.** `null` ⇒ backend bỏ qua sự kiện |

`afterRaw` **bắt buộc chứa** (cùng hình dạng `{"Worker_Data": ...}` như entity `worker`):

| Đường dẫn trong `afterRaw` | Cột đích `employee_work_histories` | Giới hạn | Bắt buộc |
|---|---|---|---|
| `Worker_Data.Worker_ID` | `employee_code` (khoá khớp nhân viên) | VARCHAR(50) | **Có** — thiếu là bỏ qua sự kiện |
| `Worker_Data.Employment_Data.Worker_Job_Data[].Position_Data.Business_Title` | `position_name` **và** `job_title_name` | VARCHAR(255) | Không, nhưng thiếu thì bản ghi vô nghĩa (xem §6-A) |

`Worker_Job_Data` có thể là object đơn hoặc mảng (`Include_Additional_Jobs`); backend lấy phần tử
đầu tiên có `Position_Data`. Đây **đúng bằng** traversal của `workerPositionData` trong
`internal/workday/get_workers.go` — cố ý nhân bản để không lệch.

Cột **không** lấy từ Workday, backend để trống có chủ ý: `work_history_type`, `decision_no`,
`decision_type`, `org_structure_id`, `job_grade`. Nhờ đúng những cột này rỗng mà dòng do Workday
sinh **không lọt vào các truy vấn tính lương** (`ResolveLevelAsOf`, `ResolveDepartmentAsOf`, phát
hiện đổi level giữa kỳ, `RecordEmployeeChanges` — tất cả đều lọc `job_grade` khác rỗng /
`org_structure_id IS NOT NULL` / `decision_type IN (...)`). **Đừng điền bừa các cột đó** — điền
vào là chạm thẳng vào kết quả tính lương.

## 5. Tính idempotent (bắt buộc)

- Cùng một `log_wid` xử lý nhiều lần chỉ được sinh **đúng 1** dòng `wd_change_log` `insert`.
- Ghi `wd_worker_transfer_events` và ghi `wd_change_log` phải nằm trong **CÙNG một transaction** —
  không được có dòng này mà thiếu dòng kia theo bất kỳ chiều nào.
- Backend đã idempotent ở phía nó (upsert theo `hris_id`), nhưng change log trùng sẽ làm số liệu
  báo cáo sai và tốn công xử lý lại.

## 6. BA VIỆC BẮT BUỘC phía Adapter — Backend không tự khắc phục được

### A. Đường "re-fetch and replace" phải sinh change log `update`

`RefreshWorkerTransferEvent` ghi đè `before_raw`/`after_raw` của dòng đã có nhưng **không sinh
`wd_change_log`**. Đây không phải chi tiết nhỏ: đúng những dòng cần refresh là dòng thiếu
`Employment_Data` (snapshot chụp trước 06/08, trước khi `Include_Employment_Information` được thêm)
⇒ thiếu `Position_Data.Business_Title` ⇒ **đúng trường duy nhất Backend lấy**.

Hậu quả nếu không làm: Backend ghi work-history với `position_name`/`job_title_name` **rỗng**, và
vì bản vá không bao giờ được thông báo, nó **rỗng vĩnh viễn**.

Việc cần làm: sau khi `UPDATE wd_worker_transfer_events`, chèn thêm 1 dòng `wd_change_log` với
`change_type='update'`, cùng `wid = log_wid`, `new_raw` theo đúng §4.

### B. Backfill change log cho các `log_wid` đã tồn tại

Change log chỉ nên được ghi khi có dòng mới (`ON CONFLICT DO NOTHING` → `RowsAffected() > 0`).
Nghĩa là **mọi dòng `wd_worker_transfer_events` đã có sẵn từ trước khi tính năng này bật sẽ không
bao giờ sang Backend**.

Đếm trước khi làm gì khác:
```sql
SELECT count(*) FROM wd_worker_transfer_events;
SELECT count(*) FROM wd_change_log WHERE entity_type = 'worker_transfer_event';
```
Nếu số thứ nhất lớn hơn số thứ hai ⇒ cần script backfill sinh change log cho phần chênh, theo thứ
tự `effective_date` tăng dần. (Trên DB `payroll_adapter` cục bộ ngày 18/08 cả hai đều bằng 0 nên
không đo được thực tế prod — phải tự đếm trên prod.)

### C. `effectiveDate` phải theo giờ Việt Nam, không phải UTC

Nguồn `wd_worker_transaction_logs.effective_moment` là **`timestamptz`**. Định dạng nó ra chuỗi
`YYYY-MM-DD` theo UTC sẽ **lệch 1 ngày** với mọi mốc rơi vào nửa đêm giờ VN: `2026-08-06 00:00+07`
lưu thành `2026-08-05T17:00:00Z`, format UTC ra `"2026-08-05"`.

Việc cần làm: quy đổi sang `Asia/Ho_Chi_Minh` trước khi format, và lấy **cùng một nguồn** với giá
trị ghi vào cột `wd_worker_transfer_events.effective_date` (cột `DATE`, PostgreSQL quy đổi theo
`TimeZone` của session) để hai bên không nói hai ngày khác nhau.

## 7. `hris_id` sinh phía Backend (chỉ để hiểu ràng buộc)

Backend sinh `hris_id` (kiểu `uuid`) từ chuỗi Workday bằng **UUIDv5** (`uuid.NewSHA1`) với namespace
cố định riêng cho từng bảng:

- `employee_contracts.hris_id` ← `Contract_ID`
- `employee_work_histories.hris_id` ← `log_wid`

Cùng đầu vào luôn cho cùng UUID ⇒ upsert đúng qua nhiều lượt sync. **Ràng buộc suy ra:**
`Contract_ID` và `log_wid` phải **duy nhất toàn cục**. Nếu Workday tái sử dụng cùng một
`Contract_ID` cho hai hợp đồng khác nhau (ví dụ ở hai công ty), hai hợp đồng đó sẽ **gộp thành một
dòng, im lặng**. Nếu biết giả định này không đúng, báo lại đội Backend ngay.

## 8. Adapter đổi X → Backend hỏng Y

| Adapter đổi | Backend hỏng |
|---|---|
| Đổi tên khoá camelCase trong `new_raw` (`afterRaw` → `after_raw`…) | Bỏ qua toàn bộ sự kiện, im lặng, không lỗi |
| Ghi `wid = worker_wid` thay vì `log_wid` | `hris_id` sai ⇒ mỗi lượt sync tạo dòng work-history mới thay vì cập nhật |
| Bỏ `Include_Employee_Contract_Data` khỏi request | Ngừng sinh hợp đồng, không báo lỗi |
| `Employee_Contracts_Data` chuyển xuống dưới `Employment_Data` | Ngừng sinh hợp đồng, không báo lỗi |
| Đổi `Business_Title` sang trường khác | `position_name`/`job_title_name` rỗng |
| `effectiveDate` không phải `YYYY-MM-DD` | Bỏ qua sự kiện (không parse được) |
| Chèn dòng `wd_change_log` với `id` nhỏ hơn con trỏ hiện tại | Dòng đó không bao giờ được xử lý |
| Giá trị dài quá giới hạn cột | Backend **cắt** cho vừa (không lỗi), nhưng dữ liệu mất phần đuôi |

## 9. Cách tự kiểm trước khi báo xong

```sql
-- 1) có sinh change log không, bao nhiêu
SELECT entity_type, change_type, count(*)
FROM wd_change_log GROUP BY 1,2 ORDER BY 1,2;

-- 2) backfill đã đủ chưa (2 số phải bằng nhau)
SELECT (SELECT count(*) FROM wd_worker_transfer_events) AS su_kien,
       (SELECT count(DISTINCT wid) FROM wd_change_log
         WHERE entity_type='worker_transfer_event')     AS da_bao;

-- 3) hình dạng new_raw có đúng 4 khoá camelCase và afterRaw có đủ 2 trường bắt buộc không
SELECT wid,
       new_raw ? 'workerWid'      AS co_workerwid,
       new_raw ? 'effectiveDate'  AS co_effectivedate,
       new_raw ? 'afterRaw'       AS co_afterraw,
       new_raw->>'effectiveDate'  AS ngay,
       new_raw->'afterRaw'->'Worker_Data'->>'Worker_ID' AS worker_id,
       new_raw->'afterRaw'->'Worker_Data'->'Employment_Data'->'Worker_Job_Data'
              ->'Position_Data'->>'Business_Title'      AS business_title
FROM wd_change_log
WHERE entity_type='worker_transfer_event'
ORDER BY id DESC LIMIT 5;

-- 4) idempotent: không được có wid trùng cho change_type='insert'
SELECT wid, count(*) FROM wd_change_log
WHERE entity_type='worker_transfer_event' AND change_type='insert'
GROUP BY wid HAVING count(*) > 1;   -- phải rỗng

-- 5) hợp đồng đã có trong payload worker chưa
SELECT count(*) FILTER (WHERE new_raw->'Worker_Data'->'Employee_Contracts_Data' IS NOT NULL)
         AS co_hop_dong,
       count(*) AS tong
FROM wd_change_log WHERE entity_type='worker';
```

Kỳ vọng ở (3): `Worker_Job_Data` có thể là mảng — nếu câu trên trả `NULL` mà dữ liệu vẫn đúng thì
kiểm lại bằng `jsonb_array_elements`. Backend xử lý được cả hai dạng.

## 10. Trạng thái phía Backend

Đã sẵn sàng nhận, trên nhánh `Core System-backend@feature/workday-bridge-contracts-workhistories`:

- `internal/service/adapter_sync.go` — vòng lặp đa-entity, con trỏ riêng mỗi `entity_type`, một
  entity lỗi không chặn entity khác.
- `internal/service/adapter_sync_map.go` — ánh xạ JSON, cắt độ dài theo rune cho vừa cột đích.
- `internal/service/adapter_sync_contract.go` — upsert `employee_contracts`, có SAVEPOINT nên một
  hợp đồng hỏng không làm kẹt đồng bộ nhân viên.
- `internal/service/adapter_sync_workhistory.go` — upsert `employee_work_histories`.
- `atlas/migrations/20260817020000_adapter_sync_state_worker_transfer_event.sql` — con trỏ mới.

**Chưa có xác minh Workday thật cho nhánh hợp đồng.** Đường `Business_Title` đã kiểm trên
**8.427/8.429** payload `worker` thật trong `wd_change_log` — 2 payload còn lại (`Worker_ID`
100206 và EE26000162) có `Position_Data` nhưng thiếu hẳn khoá `Business_Title`, backend sẽ ghi
`position_name` rỗng cho đúng 2 người đó. Đường `Employee_Contracts_Data` là **0/8.429** — chưa
có một mẫu thật nào. Sau khi Adapter làm xong §6, cần chạy một lượt sync thật
rồi cùng soi 5–10 dòng `employee_contracts WHERE source='workday'` trước khi bật chạy định kỳ trên
production.

## 11. Liên quan

- `self-docs/Review-DB-Cleanup-Workday-Bridge-180826.md` — review độc lập, nguồn của §6.
- `self-docs/Workday-Bridge-Contracts-WorkHistories-170826.md` — thiết kế gốc phía Backend.
- `Core System-backend/docs/routes-permissions.md` §Cầu nối Workday — role gate + mã trạng thái.
