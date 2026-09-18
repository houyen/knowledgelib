---
id: self-docs/integration/adapter-workday-handover
canonical_question: 'Technical guide and specification: Bàn giao đội Adapter — cầu
  nối Workday, làm gì và theo thứ tự nào'
aliases:
- Bàn giao đội Adapter — cầu nối Workday, làm gì và theo thứ tự nào
- Adapter Workday Handover 180826
entity_type: specification
domain: self-docs > integration
last_verified: 2026-09-17
---

# Bàn giao đội Adapter — cầu nối Workday, làm gì và theo thứ tự nào (180826)

**Gửi:** đội phát triển `Core System-adapter`
**Từ:** đội `Core System-backend`
**Đọc file này TRƯỚC**, rồi mới mở tài liệu hợp đồng dữ liệu.

---

## 0. Bạn nhận được đúng 2 tài liệu

| # | Tài liệu | Vai trò | Đọc khi nào |
|---|---|---|---|
| 1 | **File này** | Thứ tự công việc V0→V4, điều kiện xong từng bước, cách phối hợp. Không chứa chi tiết field. | đầu tiên |
| 2 | `Adapter-Workday-Implementation-And-Local-Test-180826.md` | **Sửa file nào, dòng nào, và kiểm thế nào trên máy mình khi KHÔNG có Workday.** Có sẵn test skeleton, câu SQL kiểm từng bước, cách test end-to-end với backend. | khi bắt tay làm |
| 3 | `Adapter-Workday-ChangeLog-Mapping-Template-180826.md` | **Hợp đồng dữ liệu** — bảng field, giới hạn độ dài từng cột, hình dạng JSON, 5 câu SQL tự kiểm. | tra cứu liên tục |

Tài liệu (3) có thêm hai dạng cùng nội dung, dễ đọc hơn bản markdown — dùng dạng nào cũng được:

- **File HTML rời:** `Adapter-Workday-ChangeLog-Mapping-Template-180826.html` — mở thẳng bằng trình
  duyệt, không cần cài gì. Có mục lục dính lề, bảng cuộn ngang được, tự theo giao diện sáng/tối của
  máy. Không có mạng vẫn đọc bình thường (chỉ đổi font sang font hệ thống).
- **Bản web:** https://claude.ai/code/artifact/f493bbe8-5c80-4dd0-8e1c-4dbf7638f1f7

Không cần file nào khác. Mọi tài liệu khác trong `self-docs/` là nội bộ backend.

Mỗi việc V0–V4 dưới đây đều có một mục tương ứng trong tài liệu (2) chỉ rõ **file/dòng cần sửa** và
**cách kiểm trên local**.

---

## 1. Bối cảnh trong một đoạn

Dữ liệu Workday đi **Workday → Core System-adapter → Core System-backend**. Backend không kết nối thẳng
database của adapter (quyết định kiến trúc 04/08), chỉ đọc `GET /v1/changes` — endpoint đã có sẵn và
**không cần đổi**. Việc của adapter là **ghi đúng dòng vào bảng `wd_change_log`**; backend tự đọc và
đổ vào `employees`, `employee_contracts`, `employee_work_histories`.

Phía backend **đã xong và đã đẩy lên GitLab**
(`Core System-backend@feature/workday-bridge-contracts-workhistories`, commit `1a7d43b`). Nó đang chờ dữ
liệu. Entity `worker` đã chạy thật từ 13/08 và **không cần bạn làm gì**. Việc còn thiếu là entity
mới `worker_transfer_event`.

---

## 2. Bốn việc, theo đúng thứ tự này

Thứ tự có lý do: V1 dựng hàm dựng JSON dùng chung, V2 sửa định dạng ngày trong chính hàm đó, V3 và
V4 tái dùng lại nó. Làm ngược thứ tự sẽ phải sửa lại chỗ đã làm.

| Việc | Nội dung | Mục trong hợp đồng dữ liệu | Phụ thuộc |
|---|---|---|---|
| **V0** | Đo quy mô backfill | §6-B | — |
| **V1** | Đường ghi cơ bản: mỗi transfer event mới → 1 dòng `wd_change_log` | §4, §5 | — |
| **V2** | `effectiveDate` theo giờ Việt Nam | §6-C | V1 |
| **V3** | Đường refresh cũng phải sinh change log | §6-A | V1 |
| **V4** | Backfill cho các `log_wid` đã tồn tại | §6-B | V0, V1, V2, V3 |

---

### V0 — Đo quy mô backfill  ·  ~5 phút  ·  làm ngay

Chạy hai câu này trên **database production** của adapter và **gửi số về cho backend**:

```sql
SELECT count(*) FROM wd_worker_transfer_events;
SELECT count(*) FROM wd_change_log WHERE entity_type = 'worker_transfer_event';
```

Vì sao cần: trên máy local của backend cả hai đều bằng **0**, nên chưa ai biết thực tế production có
bao nhiêu sự kiện lịch sử cần backfill ở V4. Nếu số thứ nhất lớn, V4 là việc thật chứ không phải
thủ tục.

**Xong khi:** đã gửi 2 con số cho backend.

---

### V1 — Đường ghi cơ bản

Mỗi khi có dòng mới trong `wd_worker_transfer_events`, ghi thêm **một** dòng `wd_change_log`.

Đọc **§4** của hợp đồng dữ liệu để lấy đúng: 6 cột của dòng `wd_change_log`, và 4 khoá camelCase của
`new_raw` (`workerWid` / `effectiveDate` / `beforeRaw` / `afterRaw`).

Ba điểm dễ sai nhất, đọc kỹ:

1. `wid` phải là **`log_wid`**, không phải `worker_wid`. Backend dùng nó sinh
   `employee_work_histories.hris_id` — ghi nhầm thì mỗi lượt sync tạo dòng mới thay vì cập nhật.
2. Ghi `wd_worker_transfer_events` và ghi `wd_change_log` phải nằm trong **cùng một transaction**.
3. **Idempotent:** cùng một `log_wid` xử lý nhiều lần chỉ được sinh **đúng 1** dòng
   `change_type='insert'`. Cách gọn nhất: chỉ ghi change log khi câu
   `INSERT ... ON CONFLICT (log_wid) DO NOTHING` thật sự chèn được dòng (`RowsAffected() > 0`).

`afterRaw` phải chứa `Worker_Data.Worker_ID` và
`Worker_Data.Employment_Data.Worker_Job_Data[].Position_Data.Business_Title` — xem bảng cuối §4.

**Xong khi:** câu SQL (1) và (4) ở §9 cho kết quả đúng — có dòng `worker_transfer_event`, và không
có `wid` nào trùng ở `change_type='insert'`.

---

### V2 — `effectiveDate` theo giờ Việt Nam

Làm ngay sau V1, trong cùng hàm dựng `new_raw`.

`wd_worker_transaction_logs.effective_moment` là **`timestamptz`**. Format ra `YYYY-MM-DD` theo UTC
sẽ **lệch 1 ngày** với mọi mốc rơi vào nửa đêm giờ Việt Nam:

```
2026-08-06 00:00+07  →  lưu 2026-08-05T17:00:00Z  →  format UTC ra "2026-08-05"   ✗
```

Quy đổi sang `Asia/Ho_Chi_Minh` trước khi format, và lấy **cùng một nguồn** với giá trị ghi vào cột
`wd_worker_transfer_events.effective_date` để hai bên không nói hai ngày khác nhau.

**Xong khi:** chọn vài sự kiện có `effective_moment` trong khoảng 17:00–23:59 UTC, xác nhận
`new_raw->>'effectiveDate'` bằng đúng cột `effective_date` của cùng dòng.

---

### V3 — Đường refresh cũng phải sinh change log

`RefreshWorkerTransferEvent` hiện ghi đè `before_raw`/`after_raw` của dòng đã có mà **không** sinh
`wd_change_log`. Phải sinh thêm 1 dòng với `change_type='update'`, cùng `wid = log_wid`, `new_raw`
theo đúng §4 (tái dùng hàm của V1).

Vì sao đây không phải chi tiết nhỏ: **đúng những dòng cần refresh là dòng thiếu `Employment_Data`**
— snapshot chụp trước 06/08, trước khi `Include_Employment_Information` được thêm — nên thiếu
`Position_Data.Business_Title`, **đúng trường duy nhất backend lấy**. Không làm V3 thì backend đã ghi
work-history với `position_name`/`job_title_name` rỗng, và vì bản vá không bao giờ được thông báo,
nó **rỗng vĩnh viễn**. Hỏng im lặng, không có lỗi nào để lần ra.

**Xong khi:** refresh một dòng đã tồn tại → xuất hiện thêm dòng `wd_change_log` `change_type='update'`
với `new_raw.afterRaw` đã có `Business_Title`.

---

### V4 — Backfill

Làm **sau cùng**, vì nó tái dùng hàm dựng `new_raw` của V1 và định dạng ngày của V2 — làm trước là
phải chạy lại.

Change log chỉ sinh cho dòng **mới**, nên mọi dòng `wd_worker_transfer_events` đã có sẵn từ trước
khi V1 bật sẽ **không bao giờ sang backend**. Viết script sinh change log cho phần chênh mà V0 đo
được, theo thứ tự `effective_date` tăng dần.

Lưu ý về thứ tự: backend giữ một con trỏ chạy theo `wd_change_log.id` tăng dần. Chèn backfill với
`id` mới (cuối bảng) là đúng — backend sẽ đọc được. Đừng cố chèn `id` nhỏ để "đúng thứ tự lịch sử":
dòng nào có `id` nhỏ hơn con trỏ hiện tại sẽ **không bao giờ được xử lý**.

**Xong khi:** câu SQL (2) ở §9 cho hai số **bằng nhau**.

---

## 3. Tự kiểm trước khi báo xong

Chạy đủ 5 câu SQL ở **§9** của hợp đồng dữ liệu và gửi kết quả kèm khi báo. Tóm tắt kỳ vọng:

| Câu | Kỳ vọng |
|---|---|
| (1) đếm theo entity/change_type | có `worker_transfer_event`, cả `insert` lẫn `update` |
| (2) backfill đủ chưa | hai số **bằng nhau** |
| (3) hình dạng `new_raw` | 4 khoá camelCase đủ, `worker_id` và `business_title` khác `NULL` |
| (4) idempotent | **rỗng** |
| (5) hợp đồng trong payload `worker` | `co_hop_dong` > 0 |

---

## 4. Ba điều KHÔNG được làm

1. **Đừng điền** `work_history_type`, `decision_no`, `decision_type`, `org_structure_id`,
   `job_grade`. Backend cố ý để trống — nhờ đúng những cột đó rỗng mà dòng do Workday sinh không lọt
   vào các truy vấn **tính lương**. Điền bừa là chạm thẳng vào kết quả tính lương.
2. **Đừng đổi tên khoá** trong `new_raw` (camelCase như §4) và **đừng đổi `wid` sang `worker_wid`**.
   Cả hai đều làm backend bỏ qua dữ liệu **im lặng**, không báo lỗi.
3. **Đừng bỏ** `Include_Employee_Contract_Data` khỏi request `Get_Workers`, và đừng để
   `Employee_Contracts_Data` đổi vị trí. Nhánh hợp đồng của backend phụ thuộc vào nó.

Bảng đầy đủ "đổi X → backend hỏng Y" ở **§8**.

---

## 5. Backend cần gì từ bạn

| # | Cần | Khi nào |
|---|---|---|
| 1 | Hai con số của V0 | ngay, ~5 phút |
| 2 | Xác nhận **`Contract_ID` duy nhất toàn cục** trong Workday | trước khi bật production |
| 3 | Báo khi xong V4 | để cùng chạy một lượt sync thật |

Về (2): backend sinh `employee_contracts.hris_id` bằng UUIDv5 từ `Contract_ID` (xem §7). Nếu Workday
tái sử dụng cùng một `Contract_ID` cho hai hợp đồng khác nhau — ví dụ ở hai công ty — hai hợp đồng
đó sẽ **gộp thành một dòng, im lặng**. Nếu bạn biết giả định này không đúng, **báo ngay**, backend
phải đổi cách sinh khoá.

---

## 6. Sau khi bạn xong — việc chung

Chạy **một lượt sync thật** trên môi trường có kết nối Workday, rồi hai bên cùng soi:

- 5–10 dòng `employee_contracts WHERE source='workday'` — kiểm `contract_no`, `sign_status`,
  `contract_type_name`, `date_start` có đúng hình dạng không, có bị cắt cụt không.
- `employee_work_histories WHERE source='workday'` — `position_name` phải khác rỗng. Rỗng hàng loạt
  nghĩa là V3 hoặc V4 chưa xong.
- Log backend, tìm dòng `[adapter-sync] bỏ qua hợp đồng` — nhiều là hình dạng JSON sai, dừng lại.

Vì sao bắt buộc bước này: nhánh `Business_Title` backend đã kiểm trên **8.427/8.429** payload
`worker` thật — 2 payload còn lại (`Worker_ID` 100206 và EE26000162) có `Position_Data` nhưng
KHÔNG có `Business_Title`, nên backend sẽ ghi `position_name` rỗng cho đúng 2 người đó (hành vi
đúng, có test bao). Nhánh `Employee_Contracts_Data` là **0/8.429** — chưa có **một mẫu thật nào**.
Đây là điều kiện để bật chạy định kỳ trên production.

---

## 7. Trạng thái phía backend

| | |
|---|---|
| Nhánh | `Core System-backend@feature/workday-bridge-contracts-workhistories` (`1a7d43b`, đã push GitLab) |
| Trạng thái | Sẵn sàng nhận. `go build`/`go vet` sạch, 939 test pass, 0 hồi quy so với `develop` |
| Chờ | Dữ liệu từ adapter (V1–V4) |
| Chưa bật | Scheduler chỉ chạy khi `WD_ADAPTER_URL` khác rỗng — hiện để trống ở mọi môi trường |

Code backend đọc dữ liệu của bạn, nếu cần đối chiếu:
`internal/service/adapter_sync_map.go` (ánh xạ JSON), `adapter_sync_contract.go` (hợp đồng),
`adapter_sync_workhistory.go` (work history).
