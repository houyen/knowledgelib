---
id: self-docs/integration/task7-db-source-bangiao-doidb
canonical_question: 'Technical guide and specification: Bàn giao Task 7 — Nguồn dữ
  liệu DB cho báo cáo "Bảng chấm công CBNV"'
aliases:
- Bàn giao Task 7 — Nguồn dữ liệu DB cho báo cáo "Bảng chấm công CBNV"
- Task7 DB Source BanGiao DoiDB 310726
entity_type: specification
domain: self-docs > integration
last_verified: 2026-07-31
---

# Bàn giao Task 7 — Nguồn dữ liệu DB cho báo cáo "Bảng chấm công CBNV"

**Ngày:** 2026-07-31
**Trạng thái phần Excel:** đã xong và đã kiểm chứng (Task 0→6, 43 test xanh). Chỉ còn thiếu nguồn dữ liệu thật.

> **CẬP NHẬT cùng ngày, sau khi restore dump `payroll_adapter_dump_20260731_170100.sql`:** chúng tôi đã
> có DB thật trong tay và **phần lớn câu hỏi bên dưới đã tự trả lời được** — đặc biệt là mục V1. Bạn đã
> dựng sẵn **9 view** mà repo chưa có (`ts_attendance_daily_pivot`, `ts_time_off_plan_balances_pivot`,
> `ts_ot_reconciliation`, `ts_worker_job_change_log/_diff`, `ts_worker_organization_change_diff`,
> `ts_worker_compensation_change_log/_diff`, `ts_attendance_daily`) và chúng giải quyết gần hết phần
> nguồn dữ liệu. **Xin đọc mục 0 trước** — đó là danh sách rút gọn những gì còn thật sự cần bạn. Các mục
> V1–V4 phía sau giữ lại để bạn thấy bối cảnh, nhưng phần lớn đã có đáp án.

---

## 0. Bản rút gọn — chỉ còn 5 việc thật sự cần bạn

Sau khi restore DB và tự chạy các truy vấn, đây là phần còn lại:

**A. Quy tắc sinh mã chấm công (việc nghiệp vụ, vẫn chặn lưới 31 ngày).**
Chúng tôi đã lấy được 19 tag thật và đã thấy `ts_attendance_daily_pivot` — hình dạng dữ liệu hoàn hảo
cho lưới ngày. Điều còn thiếu **chỉ là quy tắc quy đổi**: từ một dòng pivot (nhân viên + ngày + các cột
tag) ra **chuỗi mã** mà báo cáo hiển thị. Mã trên báo cáo có dạng `x8-4`, `L-8`, `L-10`, `TASK-REF`,
`TASK-REF`, `TS/2-2`, `Fo/2-2`, `Ro-8`, `TASK-REF`, `TASK-REF`, `TASK-REF`.
Quan sát của chúng tôi, xin bạn/C&B xác nhận hoặc sửa:
- `calculated_quantity` trong DB tính bằng **NGÀY** (thực tế gần như chỉ `0.5` và `1.0`), còn hậu tố số
  trong mã (`-8`, `-4`, `-10`, `-16`, `-2`) trông như **GIỜ**. Có phải `1.0 ngày → 8`, `0.5 → 4`?
- Nếu vậy `L-10` (10 giờ) và `TASK-REF` (16 giờ) sinh ra từ đâu — có nguồn giờ riêng, hay là nhập tay?
- Tiền tố: `x` ← `actual_working_day`, `L` ← `paid_holiday`, `NB` ← `off_in_lieu_1x/2x`,
  `Ro` ← `unpaid_leave`, `OD` ← `sick_leave_gte_30_days`, `TS` ← `maternity_leave`,
  `CN` ← ngày chủ nhật đi làm (`sunday_meal`? hay `cash_*`?), `DT` ← ? , `ON` ← nghỉ ốm **dưới** 30 ngày
  (không thấy tag tương ứng trong pivot — có phải nằm ở `raas_absence_requests`?).
  Riêng `Uncompensated_Day` và `OFF` ứng với mã gì trên báo cáo?

**B. Độ phủ lưới ngày mới chỉ 6%.** `ts_attendance_daily_pivot` có 1.907 dòng / **227 nhân viên**
(`2026-05-21 → 2026-07-20`), trong khi `raas_monthly_attendance` có **3.768 nhân viên**. Nghĩa là 31 cột
chấm công sẽ trống cho ~94% người. Đây là do `wd_calculated_time_blocks` mới sync một phần, hay bản chất
chỉ một phần nhân viên có time block?

**C. Chỉ có một kỳ trong `raas_monthly_attendance`: `2026-06-21 → 2026-07-20`.** Chúng tôi sẽ nhắm kỳ
này. Có kế hoạch sync thêm kỳ cũ (05, 06) không, và cần gì để chạy?

**D. Xác nhận nhanh 19 ánh xạ ở mục V2 bên dưới** (đúng/sai từng dòng là đủ). Hai chỗ đáng chú ý:
`Sick_Leave___30_Days_` vs `Sick_Leave_____30_Days_` chỉ khác số dấu gạch dưới; và `LeaveDayNB`/
`LeaveDayRo` có phải cộng hai field không.

**E. 9 view chưa có trong repo.** Chúng chỉ tồn tại trong DB, không có migration nào tạo ra. Bạn có định
đưa chúng vào `internal/db/migrations/` không? Nếu không thì máy nào restore lại từ migration sẽ thiếu
view, và code của chúng tôi đọc view sẽ vỡ. Cùng câu hỏi cho 2 bảng `raas_ot_actual_blocks` và
`raas_ot_actual_block_tags`.

Chỉ cần **A** là chúng tôi code được phần khó nhất. **B, C, D, E** trả lời sau cũng được.

---

---

## 1. Bối cảnh trong một đoạn

Chúng tôi đang sinh lại file báo cáo `CTD_REPORT WORKDAY - ABSENCE & TIME TRACKING.xlsx`, sheet
`202603_Bang_Cong,_Phu_Cap_Repor` ("Bảng chấm công của CBNV") bằng Go trong repo `Core System-adapter`.
Toàn bộ phần khó về Excel đã làm xong: giữ nguyên 100% định dạng gốc (271 cột, 76 vùng gộp ô, header
hai tầng), nhân dòng theo số nhân viên, neo kỳ lương 21→20, và **toàn bộ công thức Excel vẫn sống** —
đổ số liệu vào các ô đầu vào thì các cột tổng tự tính ra đúng (đã kiểm chứng bằng hai engine độc lập:
excelize và LibreOffice, cùng ra một kết quả khớp số tính tay).

Việc còn lại duy nhất là **lấy số liệu thật từ DB `payroll_adapter` đổ vào**. Đó là lý do tài liệu này
gửi tới bạn. Chúng tôi cần bạn xác nhận nguồn dữ liệu và trả lời một số câu hỏi về DB — **không cần bạn
viết code Go, cũng không cần bạn biết gì về Excel**.

---

## 2. Ranh giới công việc — bạn chỉ cần quan tâm đúng một hợp đồng

Phần Excel và phần dữ liệu đã được tách hẳn bằng một interface. Toàn bộ những gì phần dữ liệu phải
làm là trả về một danh sách bản ghi, mỗi bản ghi là một map từ **mã field** sang giá trị:

```go
type Row map[string]any        // khoá = MÃ FIELD, không phải tên cột Excel

type Source interface {
    LoadRows(ctx context.Context, periodStart, periodEnd time.Time) ([]Row, error)
}
```

"Mã field" là các chuỗi như `EmployeeCode`, `StdWorkDay`, `LeaveDayF`, `Workdays1`… Chúng **nằm sẵn
trong chính file Excel** (dòng 7 của sheet, hàng ẩn) — người thiết kế file đã đặt tên field ở đó từ
trước, chúng tôi chỉ đọc lại. Có đúng **116 mã**.

Hệ quả thực tế cho bạn, và đây là điểm quan trọng nhất của thiết kế này:

- Bạn **không cần biết** mã field nào đi vào cột Excel nào. Việc ánh xạ mã → cột do code đọc từ file
  template, tự động.
- **Đổi cấu trúc bảng DB về sau chỉ ảnh hưởng đúng một file Go** (`source_db.go`). Chúng tôi đã kiểm:
  toàn bộ phần Excel không có một dòng nào tham chiếu tới DB — không `pgx`, không `database/sql`,
  không tên bảng, không câu SQL nào.
- Mã field nào **chưa có nguồn thì cứ không đặt key** — ô Excel sẽ để trống. Tuyệt đối **không điền 0**
  (xem cảnh báo ở mục 6).

---

## 3. Việc cần bạn làm, xếp theo mức chặn

### V1 — bảng quy đổi "tag chấm công Workday → mã hiển thị"

> **ĐÃ TỰ TRẢ LỜI PHẦN LỚN sau khi restore DB.** 3 truy vấn dưới đây chúng tôi đã tự chạy, kết quả:
> **19 tag** (`Actual_Working_Day` 675 block/117 NV, `OFF` 638/219, `Night_Meal` 321/85,
> `Uncompensated_Day` 304/48, `Paid_Holiday` 299/35, `Paid_Leave` 231/49, `Unpaid_Leave` 180/28,
> `Sick_Leave_(>=30_days)` 81/3, `Unpaid_Leave_(>=30_days)` 74/5, `Sunday_Meal` 70/36,
> `Off_in_Lieu_1x` 42/12, `OT_-_Actual_(Cash_&_Off_In_Lieu)` 35/9, `Cash_1x` 28/8, `Cash_2x` 14/8,
> `Off_in_Lieu_2x` 13/7, `OT_-_Actual_(Cash)` 9/5, `Maternity_Leave` 5/2, `Cash_3x` 5/4, `Pay_Back` 2/2);
> và `calculated_quantity` tính bằng **NGÀY** (gần như chỉ `0.5`/`1.0`). Hơn nữa view
> **`ts_attendance_daily_pivot`** của bạn đã cho đúng hình dạng cần cho lưới ngày.
> **Phần còn thiếu chỉ là quy tắc quy đổi ra chuỗi mã** — xem mục 0.A ở đầu tài liệu.
> Giữ lại phần dưới để bạn thấy chúng tôi đã tra những gì.

Đây là việc **dữ liệu + nghiệp vụ**, không phải việc code.

31 cột giữa của báo cáo (`Workdays1` … `Workdays31`) là ô chấm công từng ngày, giá trị là **chuỗi mã**
như `x8-4`, `L-8`, `L-10`, `TASK-REF`, `TASK-REF`, `TS/2-2`, `TASK-REF`, `TASK-REF`, `Fo/2-2`, `Ro-8`, `TASK-REF`, `TASK-REF`.
Chúng tôi biết chắc danh sách mã này vì công thức trong file so sánh trực tiếp với chúng (ba chuỗi `IF`
lồng nhau, 186 ô mỗi chuỗi, dịch mã thô sang mã hiển thị).

**Điều chưa ai định nghĩa là: tag nào của Workday sinh ra mã nào.** Không có tài liệu nào trong repo
nói điều đó, và chúng tôi không tự suy diễn — đoán sai ở đây là ra một bảng chấm công trông đúng mà
sai, nguy hiểm hơn là để trống.

Nguồn dữ liệu có sẵn: `wd_calculated_time_blocks` (có `calculated_date`, `employee_id`,
`calculated_quantity`) join `wd_calculated_time_block_tags` (có `time_calculation_tag_id`), và
`ts_tag_totals` (có `calculation_tag_descriptor` là tên người đọc được).

**Xin bạn chạy 3 truy vấn sau và gửi lại kết quả:**

```sql
-- (1) Danh sách tag thật đang có trong dữ liệu, kèm mức phổ biến
SELECT t.time_calculation_tag_id,
       COUNT(*)                        AS so_block,
       COUNT(DISTINCT b.employee_id)   AS so_nhan_vien,
       MIN(b.calculated_date)          AS tu_ngay,
       MAX(b.calculated_date)          AS den_ngay
FROM wd_calculated_time_block_tags t
JOIN wd_calculated_time_blocks b ON b.wid = t.block_wid
GROUP BY 1
ORDER BY 2 DESC;

-- (2) Tên người-đọc-được của từng tag (để đối chiếu với nghiệp vụ)
SELECT DISTINCT calculation_tag_wid, calculation_tag_descriptor
FROM ts_tag_totals
ORDER BY 2;

-- (3) QUAN TRỌNG NHẤT: tổ hợp (tag, số lượng giờ) — vì mã hiển thị có vẻ mã hoá
--     cả số giờ: "x8-4", "L-8", "TASK-REF", "TS/2-2"
SELECT t.time_calculation_tag_id,
       b.calculated_quantity,
       COUNT(*) AS so_lan
FROM wd_calculated_time_block_tags t
JOIN wd_calculated_time_blocks b ON b.wid = t.block_wid
GROUP BY 1, 2
ORDER BY 1, 2;
```

Truy vấn (3) là chìa khoá: nếu quy tắc thật là "tag `X` + số giờ `8` → mã `x8`" thì kết quả của nó sẽ
cho thấy ngay. Có nó rồi chúng ta mới chốt được bảng quy đổi cùng bên nghiệp vụ (C&B/HR).

Nếu bạn thấy có nguồn nào khác chính xác hơn cho ô chấm công từng ngày (ví dụ `wd_time_requests` hoặc
`raas_absence_requests` cho ngày nghỉ, và `wd_calculated_time_blocks` chỉ cho ngày đi làm), xin nói —
đó là thông tin chúng tôi không có.

### V2 — Xác nhận 19 mã field chúng tôi đã map (nhóm A)

Từ `raas_monthly_attendance`: bảng này có 3 cột số đã tách sẵn, và **35 field còn lại nằm trong cột
`raw` JSONB** với tên field gốc của Workday. Đây là các ánh xạ chúng tôi định dùng — xin bạn xác nhận
đúng/sai:

| Mã field | Nguồn dự kiến | Ghi chú |
|---|---|---|
| `EmployeeCode` | `employee_id` | |
| `EmployeeName` | `raw → Worker.@Descriptor` | dạng `"Bui Ngoc Kim (Bùi Ngọc Kim)"` — cần cắt phần nào? |
| `EmployeeTypeName` | `raw → Employee_Type.@Descriptor` | |
| `JobtileName` | `raw → Position` | |
| `EmployeeLevelName` | `raw → Management_Level.@Descriptor` | vd `L8` |
| `DateEmployment` | `hire_date` | **kiểu TEXT**, xem câu hỏi Q3 |
| `OrgStructureName` / `OrgStructureCode` | `supervisory_org_*` + join `wd_organizations` | |
| `StdWorkDay` | `standard_working_days` | |
| `RealWorkDay` | `actual_working_days` | |
| `LeaveDayL` | `paid_holidays` | |
| `LeaveDayF` | `raw → Annual_Leave` | |
| `LeaveDayFo` | `raw → Personal_Leave` | |
| `LeaveDayNB` | `raw → Off_in_Lieu_83246575` **+** `CF_SRI_Total_Off_in_Lieu_2x…` | dòng chú thích trong file ghi "off in lieu 1x + 2× of…" — xin xác nhận quy tắc cộng |
| `LeaveDayON` | `raw → Sick_Leave___30_Days_` | nghỉ ốm **dưới** 30 ngày |
| `LeaveDayOD` | `raw → Sick_Leave_____30_Days_` | nghỉ ốm **từ** 30 ngày — tên hai field này chỉ khác số dấu gạch dưới, xin xác nhận không lẫn |
| `LeaveDayTS` | `raw → Maternity_Leave` | |
| `LeaveDayTSN` | `raw → CF_SRI_Total_Paternity_Leave…` | thai sản nam |
| `LeaveDayRo` | `raw → Unpaid_Leave___30_Days_` **+** `Unpaid_Leave_____30_Days_` | xin xác nhận có cộng hai field |
| `CBSTT` | `raw → Pay_Back_Days` | công bổ sung tháng trước |

### V3 — Xác nhận hoặc bác bỏ ứng viên nguồn cho phần còn lại

Ban đầu chúng tôi đánh giá nhóm này là "chưa có nguồn". Sau khi đọc hết 29 migration của repo, chúng
tôi thấy **nhiều mã có ứng viên nguồn thật** — nhưng đây là phỏng đoán từ tên bảng/cột, cần bạn xác
nhận vì bạn biết dữ liệu thật:

| Mã field | Ý nghĩa trên báo cáo | Ứng viên nguồn (phỏng đoán) |
|---|---|---|
| `AmountTrip1..3` | mức phụ cấp nhiên liệu theo bộ phận | `raas_allowance_plans` (`employee_id`, `compensation_plan_id`, `amount`) |
| `AmountTrans1..3` | mức phụ cấp đi lại theo bộ phận | cùng bảng trên, khác `compensation_plan_id` |
| `AddIn`, `Used`, `UsedLastYear`, `Budget2` | quỹ phép năm / đã dùng / phép tồn | `wd_time_off_plan_balance_records` (`plan_id`, `balance`), `wd_override_balances`, `wd_carryover_overrides` |
| `AttendanceStatus` | trạng thái bảng công (`Approved`/`Rejected`) | `raas_absence_requests.status` hoặc `raas_all_worker_time_off` (`approved`/`pending`/`denied`) — công thức trong file tự dịch sang tiếng Việt, nên **xin gửi giá trị tiếng Anh thô** |
| `JobTitleName` | chức danh | `wd_job_profiles.job_title` |
| `GraduationName` | trình độ học vấn | `wd_workers.raw` (Get_Worker có phần education?) |
| `RootRegionName`, `RecProvinceName`, `PermanentProvince` | điểm gốc / nơi tuyển / hộ khẩu | `wd_workers.raw` (phần địa chỉ / personal data?) |
| `DateQuit` | ngày nghỉ việc | `wd_workers.raw` hoặc `wd_worker_transaction_logs` (transaction Termination) |
| `OrgStructure1..3` | tên bộ phận 1/2/3 **theo Job Change trong kỳ** | `wd_worker_transaction_logs` (job change) + `wd_organizations` — cần suy diễn theo khoảng thời gian |
| `UAllDays1..3`, `UAllDays1ST..3ST` | số ngày tính phụ cấp theo từng bộ phận | dẫn xuất từ `OrgStructure1..3` + ngày công; phụ thuộc mục trên |
| `Meal1..3` | số phần cơm CN + ca đêm **theo bộ phận** | `raas_monthly_attendance.raw → Sunday_Meal`, `Night_Meal` — nhưng Workday chỉ trả **một** con số, báo cáo cần **ba** ô. Chia theo quy tắc nào? |
| `CountMeal1..3`, `CountMealNumber1..3` | số bữa ăn và mức tiền/bữa theo bộ phận | chưa rõ — có thể là cấu hình của C&B, không phải dữ liệu Workday |
| `AddMeal` | bổ sung cơm tháng trước | chưa rõ |
| `SeniorWorking`, `Seniority1..12` | ngày/phép thâm niên theo tháng | chưa rõ — có thể dẫn xuất từ `hire_date` |

**Các mã KHÔNG thuộc phạm vi của bạn** (chính file Excel ghi chủ sở hữu ở dòng 4 là `Core System` hoặc
`Core System tính thực tế`): `MealUAll`, `PhoneUAll`, `TripUAll`, `TransUAll`, `RepUAll`. Hai cột `DO`, `DQ`
file gốc ghi thẳng là `??? Not available`. Chúng tôi sẽ để trống, không cần bạn xử lý.

### V4 — Sáu câu hỏi kỹ thuật về DB

**Q1 — Chiến lược ghi của `raas_monthly_attendance`.** Migration `0023` ghi rằng bảng này **xoá sạch
rồi ghi lại toàn bộ theo từng kỳ** (vì report không có WID ổn định cho từng dòng), khác hẳn cơ chế
upsert-theo-WID của các bảng `wd_*`. Nếu chúng tôi đọc bảng này đúng lúc `adapter sync` đang chạy thì
có thấy dữ liệu nửa vời không? Chúng tôi nên đọc trong transaction, hay lọc theo `computed_at`, hay có
cờ nào báo "kỳ này đã sync xong"?

**Q2 — Độ ổn định của key trong `raw` JSONB.** Vì adapter cố ý **không đổi tên** field Workday khi lưu
(`0001`: *"nothing is renamed or flattened"*), tên field trong `raw` chính là tên Workday. Có field nào
tên đang "bấp bênh" mà bạn biết sẽ đổi không? Đặc biệt: `Off_in_Lieu_83246575` và `Off_in_Lieu_4454655`
có số hậu tố trông như ID nội bộ — chúng có ổn định qua các lần đổi cấu hình Workday không?

**Q3 — `hire_date` đang là TEXT.** Migration `0023` giải thích: Workday trả dạng `"2003-01-25-08:00"`
(có offset múi giờ nhưng không có phần giờ), Postgres không parse trực tiếp được. Chúng tôi nên tự parse
ở tầng Go, hay bạn có dự định thêm một cột `date` đã chuẩn hoá?

**Q4 — Phạm vi kỳ.** Kỳ lương là cửa sổ **21 tháng trước → 20 tháng này**. `raas_monthly_attendance`
có `period_start`/`period_end` riêng. Chúng tôi truyền đúng cặp ngày đó vào để khớp một dòng, đúng
không? Nếu ai đó gọi report với cặp ngày chưa từng được sync thì bảng rỗng — chúng tôi nên báo lỗi rõ
hay trả file rỗng?

**Q5 — Phạm vi công ty.** Báo cáo có ghi chú "xuất report cho chọn NS chính thức, Mắt Bão, tất cả".
`raas_monthly_attendance` có `company_reference_id`. Chúng tôi có cần lọc theo công ty không, và nếu có
thì danh sách mã công ty hợp lệ lấy ở đâu?

**Q6 — Nhân viên nào được đưa vào báo cáo.** Lấy tất cả dòng có trong `raas_monthly_attendance` của kỳ,
hay còn điều kiện loại trừ (đã nghỉ việc trước đầu kỳ, thực tập sinh, người nước ngoài…)?

---

## 4. Hàng rào chúng tôi sẽ dựng — và vì sao nó liên quan tới bạn

Chúng tôi sẽ viết một test khai báo **tường minh danh sách mã field mà `source_db.go` cam kết cung
cấp**. Lý do rất cụ thể: nếu về sau một thay đổi cấu trúc DB làm rụng nguồn của một mã, thì **báo cáo
sẽ không báo lỗi** — ô đó chỉ để trống, và các cột tổng phía sau vẫn ra một con số. Test này biến tình
huống "sai im lặng" thành "test đỏ ngay".

Nghĩa là: **khi bạn đổi cấu trúc bảng hoặc đổi key JSONB, xin nói với chúng tôi** — không phải để chúng
tôi sửa nhiều (chỉ một file), mà để cập nhật danh sách cam kết đó cho khớp.

---

## 5. Đã làm xong, bạn không cần làm lại

Để bạn khỏi mất thời gian kiểm tra lại: phần Excel đã hoàn thành và có bằng chứng — nhúng template đã
làm sạch (đã xoá 5 dòng dữ liệu nhân sự thật để không đưa PII vào Git), nhân dòng theo số nhân viên,
neo kỳ vào một ô duy nhất, giữ nguyên toàn bộ định dạng gốc, và các cột tổng tự tính ra đúng số. 43
test đang xanh. Chúng tôi đã đối chiếu kết quả bằng hai công cụ độc lập với thư viện dùng để ghi file,
nên con số không phải "tự chấm điểm mình".

Hiện đang chạy được với dữ liệu giả (`FixtureSource`). Chỉ cần thay bằng nguồn DB thật là xong.

---

## 6. Một cảnh báo xin đọc trước khi trả lời

Có một điều chúng tôi phát hiện khi kiểm thử và nó ảnh hưởng tới cách bạn trả lời mục V3.

Chúng tôi có quy tắc "mã field chưa có nguồn thì để trống, không điền 0", vì điền 0 vào cột tiền sẽ
làm cột tổng ra một con số trông hợp lệ mà sai. Nhưng đo thật thì **để trống cũng ra đúng con số đó**:
Excel coi ô trống là 0 khi làm số học. Ví dụ cột "Chênh lệch ngày công" = `Số ngày được trả lương −
Công chuẩn`; nếu thiếu `StdWorkDay` thì nó ra `+22`, một con số vô nghĩa nhưng nhìn như thật. Tương tự,
vì cả nhóm phụ cấp chưa có nguồn nên cột "Thành tiền tất cả PC" hiện ra **0 cho mọi nhân viên** — đọc
như một câu trả lời, không đọc như "chưa có dữ liệu".

Vì vậy, khi trả lời mục V3, xin phân biệt rõ ba trường hợp cho mỗi mã:

1. **Có nguồn, dùng được ngay** — cho chúng tôi bảng/cột/JSONB path.
2. **Sẽ có, nhưng chưa** — cho chúng tôi mốc thời gian dự kiến, để chúng tôi quyết hiển thị tạm thế nào.
3. **Sẽ không bao giờ có từ phía Workday/adapter** — nói thẳng, để chúng tôi đưa lên bên Core System hoặc
   đề xuất ẩn/đánh dấu cột đó thay vì để nó hiện số 0 gây hiểu nhầm.

Trường hợp 3 quan trọng không kém trường hợp 1: biết một cột **vĩnh viễn** không có dữ liệu thì cách xử
lý đúng là ẩn hoặc đánh dấu nó, chứ không phải chờ.

---

## 7. Chúng tôi cần gì để bắt đầu code

Đủ để khởi động ngay: **kết quả 3 truy vấn ở V1**. Có chúng là chúng tôi bắt đầu được phần lưới ngày,
phần khó nhất.

Song song, phần nhóm A (V2) chỉ cần bạn xác nhận đúng/sai là chúng tôi code luôn. Nhóm V3 và V4 có thể
trả lời sau, không chặn.

Tài liệu kỹ thuật đầy đủ của phía Excel (nếu bạn muốn đọc): `self-docs/BangCong-Xlsx-Template-Golang-310726.md`,
đặc biệt mục 3 (bản đồ dữ liệu) và mục 12 (phân tích ảnh hưởng khi đổi cấu trúc DB).
