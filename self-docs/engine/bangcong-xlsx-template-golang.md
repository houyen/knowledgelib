---
id: self-docs/engine/bangcong-xlsx-template-golang
canonical_question: 'Technical guide and specification: PLAN — Build template Excel
  "Bảng chấm công CBNV" bằng Go + excelize'
aliases:
- PLAN — Build template Excel "Bảng chấm công CBNV" bằng Go + excelize
- BangCong Xlsx Template Golang 310726
entity_type: how_to
domain: self-docs > engine
last_verified: 2003-01-25
---

# PLAN — Build template Excel "Bảng chấm công CBNV" bằng Go + excelize (2026-07-31)

**Loại tài liệu:** PLAN thi hành (canonical cho hạng mục này). Đặt ở `self-docs/` chứ không ở
`llmwiki/wiki/sources/draft/` theo đúng tiền lệ `Salary-Column-Sync-Impact-280726.md` — quy ước máy
local cấm tạo file `.html` đi kèm mà rule R7 lại đòi companion HTML cho file trong `sources/draft/`.

**Trạng thái:** chưa code dòng nào. Toàn bộ số liệu dưới đây đo trực tiếp từ file thật bằng openpyxl
và từ code/migration thật của `Core System-adapter`, không suy đoán.

---

## 0. Bốn quyết định đã chốt với người dùng

| Điểm | Lựa chọn | Hệ quả chính |
|---|---|---|
| Sheet | `202603_Bang_Cong,_Phu_Cap_Repor` (tab **nhìn thấy** thứ 2) | 271 cột, 76 merge, header 2 tầng, lưới 31 ngày |
| Phạm vi | Khung **+ đổ dữ liệu từ DB** | Phải làm cả tầng truy vấn và bản đồ cột↔nguồn |
| Công thức | **Giữ công thức sống** (`SetCellFormula`) | Không phải port 51 dạng công thức sang Go |
| Repo | **`Core System-adapter`** | Thêm dep `excelize` (hiện repo chỉ có 3 dep) |

**Đính chính con số tôi đưa ra lúc hỏi:** tôi nói "~60 công thức" — sai. Đo thật: **1.081 ô công
thức**, thuộc **51 dạng khác nhau**, trong đó **123 công thức trên mỗi dòng nhân viên**. Con số này
làm quyết định "giữ công thức sống" càng đúng: port 51 dạng đó sang Go là một dự án riêng.

---

## 1. Sự thật đã đo được từ file gốc

Nguồn: `document/CTD_REPORT WORKDAY - ABSENCE & TIME TRACKING.xlsx`, sheet
`202603_Bang_Cong,_Phu_Cap_Repor`.

### 1.1 Kích thước và bố cục dòng

| Dòng | Vai trò | Ghi chú |
|---|---|---|
| 1 | Ghi chú "Confirm: start date - end date of this report" | |
| 2 | Tiêu đề `="BẢNG CHẤM CÔNG CỦA CBNV THÁNG "&MONTH(J6)&"/"&YEAR(J6)` | merge `A2:K2`, Times New Roman 24pt bold, cao 63.75 |
| 3 | Trống, cao 30 | |
| 4 | **Dòng CHỦ SỞ HỮU dữ liệu** — `WD` / `Core System` / `Added by RA` / `??? Not available` | xem §1.5 |
| 6, 7 | **Ẩn.** Dòng 6 = chuỗi ngày (`=DATE(YEAR(J6),MONTH(J6)-1,21)` rồi `=M6+1`...); dòng 7 = `WEEKDAY` + **mã field API** | |
| 8, 9 | Header 2 tầng (merge dọc `X8:X9` cho cột đơn, merge ngang cho nhóm) | cao 25.5 / 72 |
| 10 | Hướng dẫn nguồn dữ liệu (`Paid_Holiday`, `Off_in_Lieu_1x`...) | cao 159 |
| 11 | Mô tả quy tắc nghiệp vụ, chữ đỏ `FFFF0000` | cao 395.25 |
| **12** | **DÒNG MẦM (seed row)** — có đủ **123 công thức**, không có dữ liệu nhân viên | mấu chốt của phương án, xem §2 |
| 13–17 | **5 nhân viên thật** (Vũ Ngọc Quyền, Phạm Văn Đảm...) — dữ liệu mẫu | phải xoá, xem §4 |
| 18 | Dòng tổng `SUBTOTAL` (14 công thức) | |
| 20 | Rác: `C20 = '` | |
| 26–44 | Khối dán rác không liên quan (cột DG..EA, tên dự án + số tiền) | không thuộc báo cáo |

### 1.2 Bốn dải 31 cột — phát hiện quan trọng nhất

Lưới ngày công không phải một dải mà là **bốn dải 31 cột nối tiếp nhau bằng công thức**:

| Dải | Cột | Vai trò | Nguồn |
|---|---|---|---|
| Dải 4 (hiển thị) | `M`–`AQ` | Ô người dùng nhìn thấy | công thức `IF` lồng, đọc từ dải 3 |
| Dải 1 (đầu vào) | `EU`–`FY` | Mã `Workdays1`…`Workdays31` | **DỮ LIỆU THẬT ĐỔ VÀO ĐÂY** |
| Dải 2 | `FZ`–`HD` | Chuẩn hoá bước 1 | công thức, đọc dải 1 |
| Dải 3 | `HE`–`II` | Chuẩn hoá bước 2 | công thức, đọc dải 2 |

Ba chuỗi `IF` khổng lồ (186 ô mỗi chuỗi, ở `M12`, `FZ12`, `HE12`) làm việc dịch mã chấm công thô
sang mã hiển thị: `"L-10"→"L-8"`, `"TS/2-2"→"TS/2"`, `"x8-4"→"x8"`, `"TASK-REF"→""`, `"TASK-REF"→"DT"`…

**Hệ quả cho việc code:** trong 124 cột của lưới ngày, chỉ cần đổ dữ liệu vào **31 cột `EU`–`FY`**.
93 cột còn lại tự chạy. Đây là lý do chọn "giữ công thức sống" tiết kiệm cực lớn.

### 1.3 Phân loại 271 cột

| Nhóm | Số cột | Ý nghĩa |
|---|---|---|
| Có công thức ở dòng mầm (dòng 12) | **123** | Go không cần tính, chỉ nhân bản công thức |
| Có dữ liệu literal ở dòng 13 (cột cần đổ) | **85** | Go phải điền |
| Trống hoàn toàn | 63 | chưa dùng / để dành |
| Có **mã field API** ở dòng 7 | **116** | khoá ánh xạ, xem §3 |

### 1.4 Census định dạng (cần cho quyết định kiến trúc)

- **1.081 ô công thức / 51 dạng**; hàm dùng: `IF` (668), `DAY` (80), `WEEKDAY` (31), `SUBTOTAL` (26),
  `INDIRECT` (23), `MONTH` (32), `YEAR` (20), `COUNTIF` (2), `IFERROR` (6), `ROUNDUP`, `SUM`, `OR`, `AND`, `LEN`.
- **13 định dạng số** khác nhau, gồm accounting `_(* #,##0.0_);_(* \(#,##0.0\);_(* "-"??_);_(@_)`
  (248 ô), `0;\-0;;@` (139), `#,##0` (127), `ddd` (124), `mm-dd-yy` (36), `[$-1010000]d/m/yyyy;@` (4).
- **22 tổ hợp nền (fill)** — trong đó **15 tổ hợp dùng màu THEME + tint** (`theme0 tint -0.0499`,
  `theme6 tint 0.7999`…), chỉ 7 là RGB thẳng. Điểm này quyết định kiến trúc: tái tạo màu theme +
  tint bằng tay trong excelize là việc dễ sai và không có cách kiểm tự động rẻ.
- **6 tổ hợp font**: chủ đạo Times New Roman 11 (2.108 ô), tiêu đề 24pt, lẫn Aptos Narrow 11 (401 ô —
  font mặc định của ô chưa định dạng), 1 ô Arial 9.
- Không có: conditional formatting, data validation, defined name, sheet protection, page setup, freeze pane.

### 1.5 Ai sở hữu cột nào (đọc từ dòng 4 của chính file)

| Nhãn dòng 4 | Số cột | Nghĩa |
|---|---|---|
| `WD` | **103** | Workday cấp → `Core System-adapter` lấy được |
| (trống) | 154 | không ghi chủ sở hữu (phần lớn là cột công thức và dải phụ) |
| `Core System` | 6 | `BG`, `BI`, `BJ`, `BX`, `CW`, `DR` — hệ Core System tính |
| `Core System tính thực tế` | 4 | `CX`, `DF`, `DK`, `DP` |
| `??? Not available` | 2 | `DO`, `DQ` — **chính file gốc thừa nhận chưa có nguồn** |
| `Core System?` | 1 | `CB` (còn dấu hỏi) |
| `Added by RA` | 1 | `CH` |

### 1.6 Lỗi có sẵn trong file gốc (phải quyết giữ hay bỏ)

1. **10 ô `#REF!`**: `E13:E17` (`=IF(#REF!>0,"","")`) và `DS13:DS17` (`=#REF!`). Đều nằm ở **5 dòng
   mẫu sẽ bị xoá**; dòng mầm 12 sạch. Nếu vô tình nhân bản từ dòng 13 thay vì dòng 12 thì lỗi này
   nhân ra toàn bảng.
2. **Mã field bị hỏng bởi find/replace**: `FC:Workdays{r}`, `FM:Workdays1{r}`, `FW:Workdays2{r}`,
   `IR:Seniority{r}` — chuỗi `{r}` đứng chỗ chữ số `9`. Tức là đúng ra phải là `Workdays9`,
   `Workdays19`, `Workdays29`, `Seniority9`. Trình ánh xạ theo mã field sẽ **trượt đúng 4 cột** nếu
   không xử lý.
3. **File chứa dữ liệu nhân sự thật** (5 họ tên + mã NV + ngày vào làm). Xem ràng buộc G4 ở §5.

---

## 2. Kiến trúc chọn: nhúng template + nhân bản dòng mầm

### 2.1 Quyết định

Nhúng **chính file .xlsx (đã làm sạch)** vào binary bằng `go:embed`, mở bằng
`excelize.OpenReader`, rồi **nhân bản dòng mầm 12** thành N dòng nhân viên và chỉ điền dữ liệu vào
~85 cột cần điền. Không dựng lại style/merge/định dạng bằng code.

### 2.2 Vì sao không dựng từ đầu bằng code

Phương án "code dựng 100% từ spec" phải tái tạo bằng tay: 76 vùng merge, 22 tổ hợp fill **trong đó
15 là theme+tint** (excelize không có API màu theme — phải tự giải ra hex, và sai lệch màu sẽ không
test tự động nào bắt được), 13 định dạng số, 6 tổ hợp font, độ rộng/ẩn của 10 cột, chiều cao 8 dòng,
và **1.081 công thức**. Chi phí lớn, rủi ro sai cao, mà lợi ích duy nhất là "không phụ thuộc file
nhị phân trong repo" — không đáng đổi.

### 2.3 Vì sao nhân bản dòng mầm, không dùng `InsertRows`/`DuplicateRow` của excelize

Dòng 12 **đã sẵn là một dòng mầm hoàn chỉnh**: đủ 123 công thức, không có dữ liệu nhân viên, không
dính `#REF!`. Người làm file thiết kế đúng như vậy.

Nhưng **không dựa vào `excelize.DuplicateRow`/`InsertRows` để tự dịch tham chiếu công thức** — hành
vi dịch tham chiếu tương đối của excelize khi chèn dòng là thứ phải kiểm chứng chứ không được tin,
và nếu nó dịch sai thì sai lặng lẽ trên cả nghìn ô. Thay vào đó **tự viết bộ dịch tham chiếu**: đọc
chuỗi công thức của dòng 12, dịch mọi số dòng **không có `$`** đi một khoảng `delta`, giữ nguyên số
dòng có `$`. Đây là ~40 dòng Go, tất định, và **test được bằng bảng case** — khác hẳn việc tin vào
hành vi nội bộ của thư viện.

Quy tắc dịch (phải viết thành test trước khi dùng):

| Đầu vào (ở dòng 12) | delta | Kết quả mong đợi |
|---|---|---|
| `=IF(HE12="L-10","L-8",...)` | +3 | `=IF(HE15="L-10","L-8",...)` |
| `=SUBTOTAL(3,$G$13:G12)` | +3 | `=SUBTOTAL(3,$G$13:G15)` (`$G$13` giữ nguyên) |
| `=IF(G12="","",IFERROR(B11+1,1))` | +3 | `=IF(G15="","",IFERROR(B14+1,1))` |
| `=IF(JA18="","",SUBTOTAL(9,INDIRECT("CU"&ROW()+1&...)))` | — | dòng 18 là footer, dịch riêng |
| `=COUNTIF(JC:JC,F11)` | +3 | `=COUNTIF(JC:JC,F14)` (`JC:JC` cả cột — không có số dòng, giữ nguyên) |

Cạm bẫy đã thấy trong dữ liệu thật, phải có case test riêng: chuỗi **`"L-10"`, `"x8-4"`, `"TS/2-2"`,
`"TASK-REF"` nằm TRONG dấu nháy kép** — regex dịch số dòng mà quét mù cả chuỗi literal sẽ biến `"L-10"`
thành `"L-13"` và làm hỏng toàn bộ logic dịch mã chấm công. **Bộ dịch bắt buộc phải bỏ qua nội dung
trong nháy kép.** Đây là rủi ro số một của cả plan.

---

## 3. Bản đồ dữ liệu: mã field (dòng 7) → nguồn trong `Core System-adapter`

Khoá ánh xạ là **mã ở dòng 7**, không phải chữ cái cột — cột có thể xê dịch, mã thì không.

### 3.1 Nhóm A — có nguồn trực tiếp, làm được ngay

Từ `raas_monthly_attendance` (bảng đã có, migration `0023_raas_reports.sql`; 3 cột số đã tách +
**cột `raw` JSONB chứa 38 field**, xác nhận bằng `Get_Monthly_Attendance_Report_API_Response.txt`):

| Mã dòng 7 | Cột | Field Workday trong `raw` |
|---|---|---|
| `StdWorkDay` | AR | `Standard_Working_Days` (đã có cột riêng `standard_working_days`) |
| `RealWorkDay` | AV | `Actual_Working_Days` (cột riêng `actual_working_days`) |
| `LeaveDayL` | AW | `Paid_Holidays` (cột riêng `paid_holidays`) |
| `LeaveDayF` | AZ | `Annual_Leave` |
| `LeaveDayFo` | BA | `Personal_Leave` |
| `LeaveDayNB` | AX | `Off_in_Lieu_83246575` + `CF_SRI_Total_Off_in_Lieu_2x__Base_on_Start_Date___End_Date_` (dòng 10 của file ghi rõ "lấy off in lieu 1x + 2× of…") |
| `LeaveDayON` | BB | `Sick_Leave___30_Days_` (< 30 ngày) |
| `LeaveDayOD` | BC | `Sick_Leave_____30_Days_` (≥ 30 ngày) |
| `LeaveDayTS` / `LeaveDayTSN` | BD / BE | `Maternity_Leave` / `CF_SRI_Total_Paternity_Leave…` |
| `LeaveDayRo` | BH | `Unpaid_Leave___30_Days_` + `Unpaid_Leave_____30_Days_` |
| `CBSTT` | BK | `Pay_Back_Days` |
| `Meal1`…`Meal3` | CS–CU | `Sunday_Meal`, `Night_Meal` (cần quy tắc chia theo bộ phận — chưa rõ) |
| `EmployeeCode` | G | `Employee_ID` |
| `EmployeeName` | H | `Worker@Descriptor` |
| `JobtileName` | I | `Position` |
| `EmployeeLevelName` | J | `Management_Level@Descriptor` |
| `DateEmployment` | K | `Hire_Date` (kiểu TEXT `"2003-01-25-08:00"` — Postgres không parse thẳng được, migration đã ghi chú) |
| `EmployeeTypeName` | C | `Employee_Type@Descriptor` |
| `OrgStructureName` / `OrgStructureCode` | F / D | `Supervisory_Organization` + join `wd_organizations` |

### 3.2 Nhóm B — phải tính, nguồn có nhưng chưa ở dạng dùng được

- **`Workdays1`…`Workdays31` (EU–FY)** — ô chấm công từng ngày, giá trị dạng chuỗi mã (`x8-4`,
  `L-10`, `TASK-REF`, `TS/2-2`, `TASK-REF`…). Nguồn: `wd_calculated_time_blocks` (có `calculated_date`,
  `employee_id`, `calculated_quantity`) + `wd_calculated_time_block_tags`
  (`time_calculation_tag_id`). **Chưa có ở đâu quy tắc tag → mã hiển thị**; phải đối chiếu dữ liệu
  thật rồi chốt bảng quy đổi. Đây là hạng mục lớn thứ hai sau bộ dịch công thức.
- **`AttendanceStatus` (BY)** — công thức `CA12` dịch `Approved/Rejected` → `Đã Duyệt/Từ Chối/Yêu Cầu`,
  nên Go chỉ cần đổ giá trị tiếng Anh thô. Nguồn khả dĩ: `raas_absence_requests` /
  `raas_all_worker_time_off` (`approved`/`pending`/`denied`).
- **`PayrollMonth` (JB)**, `LeaveDayx0`/`x1`/`DT` (IY–JA) — dẫn xuất từ kỳ và từ chính lưới ngày.

### 3.3 Nhóm C — CHƯA CÓ NGUỒN trong adapter (phải để trống, không được bịa)

`CountMeal1..3`, `CountMealNumber1..3` (định mức bữa/mức tiền), `AmountTrip1..3`, `AmountTrans1..3`
(mức phụ cấp), `UAllDays1..3` + `UAllDays1ST..3ST`, `RootRegionName`, `RecProvinceName`,
`PermanentProvince`, `GraduationName`, `SeniorWorking`, `Seniority1..12`, `Budget2`, `AddIn`, `Used`,
`UsedLastYear`, `SeniorityRate`, `OrderNumberJobTitle`, `OrgStructure1..3`, `AddMeal`, `MealUAll`,
`PhoneUAll`, `TripUAll`, `TransUAll`, `RepUAll`, `DateQuit`, `JobTitleName`.

Ba lý do khác nhau, đừng gộp: (a) là **dữ liệu Core System** chứ không phải Workday (dòng 4 ghi `Core System`
/ `Core System tính thực tế`); (b) là **cấu hình định mức** của C&B, không nằm ở adapter; (c) chính file
gốc ghi `??? Not available` (`DO`, `DQ`) hoặc `Core System?` (`CB`).

**Ràng buộc:** cột nhóm C để **trống**, không điền 0. Điền 0 vào cột tiền/định mức là nói dối có hệ
thống — công thức tổng phía sau (`DR`, `EG`, `EK`, `EO`) sẽ cho ra một con số trông hợp lệ mà sai.

---

## 4. Task breakdown

Thứ tự cố ý: rủi ro cao nhất (bộ dịch công thức) đứng trước, để nếu phải đổi hướng thì đổi sớm.

### Mốc M1 — "dựng xong template, chưa ráp công thức, chưa nối DB" = Task 0 + Task 1 (+ mẩu nhỏ Task 7)

Ghi lại vì câu hỏi này chắc chắn sẽ được hỏi lại: **không tách được mốc "template không có công
thức"**. Kiến trúc là nhúng file gốc (§2.2), nên 1.081 công thức nằm sẵn trong dòng 1–12 và 18 của
template — chúng không phải thứ được "ráp thêm vào" ở bước sau. Ở mốc này chúng vô hại: chưa có dòng
dữ liệu nào nên dòng mầm 12 trả `""` hết, dòng 18 `SUBTOTAL` ra 0. Cố tình xoá chúng đi rồi Task 2/3
nhét lại là việc vứt đi — **đừng làm**.

Thứ thật sự chưa có ở M1 là: **chưa nhân dòng và chưa có dữ liệu**.

| M1 CÓ | M1 CHƯA CÓ |
|---|---|
| File `.xlsx` mở được, tiêu đề 24pt, 76 merge, header 2 tầng, 13 định dạng số, 22 tổ hợp nền (gồm 15 theme+tint), 10 cột ẩn, 8 chiều cao dòng | Chỉ **1 dòng mầm** (dòng 12), chưa nhân ra N dòng → Task 3 |
| Template sạch: hết 10 ô `#REF!`, hết PII 5 nhân viên, hết rác dòng 20 + khối 26–44, chỉ còn 1 sheet | Lưới 31 ngày hiện **sai tháng** vì chưa neo kỳ vào ô `J6` → Task 4 |
| **Bằng chứng excelize không phá file** — giá trị lớn nhất của mốc, chính là cổng Task 0 | Không có dữ liệu → Task 5, 6 |

Mẩu Task 7 cần kéo lên sớm: chỉ đúng phần ghi file ra đĩa (`f.SaveAs`) để M1 kiểm chứng được bằng
mắt, chưa cần route HTTP.

Rủi ro của mốc: excelize làm lệch màu theme → **dừng, xét lại kiến trúc**. Biết điều này trước khi
bỏ công vào Task 2–6 chính là lý do M1 tồn tại.

### Task 0 — Spike: excelize có giữ nguyên được template không (GATE)

- **Files:** `internal/report/bangcong/spike_test.go` (mới, giữ lại làm test hồi quy),
  `tools/xlsx_inspect.py` (mới — **công cụ KIỂM, chỉ đọc**).
- **Steps:**
  1. `go get github.com/xuri/excelize/v2@v2.10.0` (pin đúng version `Core System-backend` đang chạy production, tránh 2 repo lệch nhau — xem G7).
  2. `excelize.OpenFile` file gốc → `SaveAs` ra file mới, **không sửa một ô nào ở giữa**. Round-trip thuần.
  3. `tools/xlsx_inspect.py` (openpyxl, máy đã có 3.1.5) nhận đường dẫn + tên sheet, in JSON: số merge
     và danh sách merge đã sort, số ô công thức, số dạng công thức, số công thức dòng 12, tập định dạng
     số kèm tần suất, tập fill **ghi rõ theme+tint hay rgb** kèm tần suất, tập font, độ rộng/ẩn theo
     cột, chiều cao theo dòng.
  4. Chạy script trên file gốc và file đã qua excelize, `diff` hai JSON.
- **Mốc kiểm:** 76 merge · 1.081 ô công thức · 51 dạng · 123 công thức ở dòng 12 · 22 tổ hợp fill
  (**15 theme+tint**) · 13 định dạng số · 10 cột khai độ rộng/ẩn · 8 dòng khai chiều cao.
- **Kỳ vọng:** `diff` rỗng.
- **Verify:**
  ```
  go test ./internal/report/bangcong/ -run TestSpikeRoundTrip -v
  python3 tools/xlsx_inspect.py "<gốc>"  "202603_Bang_Cong,_Phu_Cap_Repor" > /tmp/before.json
  python3 tools/xlsx_inspect.py "<sau>"  "202603_Bang_Cong,_Phu_Cap_Repor" > /tmp/after.json
  diff /tmp/before.json /tmp/after.json
  ```
- **CỔNG:** `diff` không rỗng → **dừng, báo cáo chính xác trường nào lệch**. Không nới lỏng assertion,
  không "chấp nhận sai số nhỏ", không đổi thư viện. Lệch ở **màu theme** là lệch nghiêm trọng: cả
  kiến trúc §2 phải xét lại.

### Task 1 — Làm sạch template và nhúng vào binary (chỉ khi Task 0 xanh)

- **Files:** `internal/report/bangcong/template/bangcong.xlsx` (mới — artefact),
  `internal/report/bangcong/tools/sanitize.go` (mới, `//go:build ignore`, chạy tay 1 lần),
  `internal/report/bangcong/embed.go` (mới), `internal/report/bangcong/template_test.go` (mới).
- **Steps:**
  1. `sanitize.go` dùng **chính excelize** tạo template sạch (xem G9 — vì sao không dùng openpyxl):
     xoá 6 sheet còn lại (giữ đúng sheet cần) · xoá khối dòng 26–44 (dán rác) · xoá dòng 20 (rác
     backtick ở `C20`) · xoá dòng 13–17 (5 nhân viên thật — PII, xem G4) · **giữ nguyên dòng 1–12 và
     dòng 18**. **Xoá từ dưới lên trên** để chỉ số dòng không trượt giữa chừng.
  2. `embed.go`: `//go:embed template/bangcong.xlsx` → `[]byte` + `Open()` trả `*excelize.File` qua
     `excelize.OpenReader`.
  3. `template_test.go` khẳng định trên template đã sạch: đúng 1 sheet · **0 ô chứa `#REF!`** · dòng
     mầm 12 vẫn đúng **123 ô công thức** · **dòng footer `SUBTOTAL` còn nguyên và công thức trỏ đúng
     dải sau khi các dòng phía trên bị xoá** · không còn họ tên/mã NV mẫu.
- **Điểm phải kiểm kỹ:** excelize **tự dịch tham chiếu công thức khi xoá dòng**. Ở đây đó là hành vi
  mong muốn (footer phải bám theo), nhưng nó phải được **xác nhận bằng test**, không được tin — cùng
  một lý do như §2.3 với `DuplicateRow`.
- **Verify:**
  ```
  go build ./... && go vet ./...
  go test ./internal/report/bangcong/... -v
  unzip -p internal/report/bangcong/template/bangcong.xlsx xl/worksheets/sheet1.xml | grep -c "REF!"   # = 0
  python3 tools/xlsx_inspect.py internal/report/bangcong/template/bangcong.xlsx "202603_Bang_Cong,_Phu_Cap_Repor"
  # đối chiếu phần dòng 1–12 + 18 với /tmp/before.json của Task 0
  ```

### Task 2 — Bộ dịch tham chiếu công thức (phần rủi ro nhất)

- **Files:** `internal/report/bangcong/formula.go`, `formula_test.go`.
- **Interfaces:** `func ShiftRows(formula string, delta int) string`.
- **Steps:** viết **test trước**, tối thiểu 8 case: 5 case ở bảng §2.3, cộng 3 case cạm bẫy —
  `"L-10"` trong nháy kép **không được đổi**, `$G$13` **không được đổi**, `JC:JC` (cả cột)
  **không được đổi**. Rồi mới viết hàm: quét ký tự, bật/tắt cờ "đang trong chuỗi", chỉ dịch số dòng
  của tham chiếu ô hợp lệ không có `$`.
- **Verify:** `go test ./internal/report/bangcong/ -run TestShiftRows -v` — xanh toàn bộ trước khi sang Task 3.

### Task 3 — Nhân bản dòng mầm

- **Files:** `internal/report/bangcong/builder.go`.
- **Interfaces:** `func (b *Builder) ExpandRows(n int) error`.
- **BỐ CỤC ĐÍCH — chép đúng bố cục file gốc, đừng tự sáng tạo:** dòng 12 **VẪN LÀ DÒNG MẦM, giữ
  nguyên tại chỗ, không mang dữ liệu**; n dòng nhân viên nằm ở **dòng 13 … 12+n**; footer đẩy xuống
  **dòng 13+n**. Đây chính xác là bố cục của file gốc (mầm 12, nhân viên 13–17, footer 18) và là điều
  làm cho tham chiếu `G$13` trong `A12` đúng — xem §8.
- **Steps:** đọc toàn bộ ô có giá trị/công thức/style của dòng 12; với mỗi dòng đích 13…12+n, chép
  **style index** (`GetCellStyle`/`SetCellStyle` — không dựng style mới) và công thức đã qua
  `ShiftRows` với `delta = dòngĐích − 12`.
- **MỘT Ô PHẢI XỬ RIÊNG, KHÔNG ĐƯỢC DỊCH CỨNG:** `JB<footer>` = `SUBTOTAL(3,JB2:JB12)` — phạm vi phải
  **GIÃN** theo n thành `JB2:JB<12+n>`, không phải dịch nguyên khối. Ô này là **số đếm dòng** mà 11
  công thức `SUBTOTAL(9,INDIRECT(...))` còn lại của footer đọc qua `JA<footer>`; sai đây là sai cả
  hàng footer. (`A12` **không** thuộc nhóm này — nó đã được `sanitize.go` vá về đúng bản gốc
  `$G12:G$13` ở Task 1, và bản gốc đó đúng sẵn với bố cục trên.)
- **Không dùng `GetSheetDimension`** để suy ra biên dòng/cột — Task 1 đã đo thấy nó **stale** sau
  `RemoveRow` (vẫn báo `A1:JK44` khi sheet chỉ còn 13 dòng). Dùng `GetRows`/`GetCols`.
- **Verify:** sinh file 3 dòng, mở lại đếm: mỗi dòng 13/14/15 đúng 123 công thức, style index của
  `M13`/`M14`/`M15` bằng `M12`, footer nằm ở dòng 16 và `JB16 = SUBTOTAL(3,JB2:JB15)`, và **STT ra
  1/2/3** (không phải 0 hay lỗi) sau khi tính lại.

### Task 4 — Neo kỳ báo cáo

- **Files:** `internal/report/bangcong/period.go`.
- **Steps:** cả lưới ngày và tiêu đề đều dẫn xuất từ **một ô duy nhất**. ⚠️ **ĐÍNH CHÍNH (thi hành
  2026-07-31):** bản đầu của PLAN này ghi ô neo là `J6` — **SAI**. Chuỗi thật là
  `J6 = K6` → `K6 = JB6` → `JB6 = JB12`, và **`JB12` (trong dòng mầm) mới là ô literal ghi được**.
  `SetPeriod` ghi vào **`JB12`**. Ghi đúng ô đó thì 31 cột ngày + `WEEKDAY` + tiêu đề
  `"BẢNG CHẤM CÔNG… THÁNG m/yyyy"` tự đúng. Tái dùng `internal/payperiod` đã có sẵn trong repo cho
  quy tắc cửa sổ 21→20.
- **Verify:** sinh 3 file cho 3 kỳ khác nhau (tháng 28 ngày / 30 / 31), mở bằng LibreOffice headless
  tính lại (`soffice --convert-to xlsx`), đọc giá trị đã tính của `M9`…`AQ9`.
  ⚠️ **ĐÍNH CHÍNH (kiểm chứng 2026-07-31):** bản đầu của PLAN này viết "kỳ tháng 2 phải cho ô ngày
  thừa ra chuỗi rỗng vì `AQ9` đã có nhánh `IF(DAY(AQ6)=21,"",…)`" — **giả định đó SAI**. Nhánh đó chỉ
  làm trống khi ngày tràn đúng bằng 21, tức **chỉ đúng cho tháng 30 ngày**. Với tháng 2 thì tràn 3 cột
  và **không cột nào bị làm trống**. Xem §11.8. Tiêu chí verify đúng phải là: kiểm số cột hiển thị
  ngày **thuộc kỳ** khớp số ngày thật của kỳ, và ghi nhận các cột tràn.

### Task 4.5 (MỚI) — Làm cho ô công thức RA SỐ THẬT

Đây là task trả lời trực tiếp yêu cầu "ô nào là input thì nhận dữ liệu, ô nào là formula thì cũng
phải thực hiện được". excelize ghi công thức **không kèm giá trị cache**, nên nếu bỏ qua task này thì
file mở bằng Excel vẫn ra số (Excel tự tính) nhưng **mọi thứ đọc file bằng code sẽ thấy rỗng** —
openpyxl `data_only=True`, pandas, và cả script kiểm của chính chúng ta.

- **Files:** `internal/report/bangcong/recalc.go`, `calc_support_test.go`.
- **Steps:**
  1. Bật cờ tính lại khi mở: `f.SetCalcProps(excelize.CalcPropsOptions{FullCalcOnLoad: &tru})` — để
     Excel/LibreOffice luôn tính lại, không tin cache cũ.
  2. Tính sẵn và ghi giá trị cache bằng `f.CalcCellValue(sheet, cell)` cho toàn bộ ô công thức, theo
     đúng thứ tự phụ thuộc của file (dải ngày: `EU–FY` → `FZ–HD` → `HE–II` → `M–AQ`; rồi các cột
     tổng; footer sau cùng).
  3. `calc_support_test.go` khoá bất biến: **21 hàm** mà template dùng đều được `CalcCellValue`
     hỗ trợ (đã đo, xem §9.3) — nếu nâng version excelize làm rụng hàm nào thì test đỏ ngay.
- **Verify:** đối chiếu chéo hai đường tính, phải khớp: (a) giá trị `CalcCellValue` của Go;
  (b) giá trị sau khi LibreOffice tính lại `soffice --headless --convert-to xlsx`, đọc bằng openpyxl
  `data_only=True`. Hai engine độc lập cho cùng số thì mới tin được.

### Task 5 — Nguồn dữ liệu qua interface + fixture (KHÔNG cần DB)

Cố ý tách khỏi Task 7: chuỗi `input → formula → số` phải chứng minh được **trước** và **độc lập** với
việc DB adapter đã có đủ dữ liệu hay chưa. Hiện DB còn thiếu nhiều (§3.3) và container Postgres
thậm chí đang không chạy — để nó chặn thì không bao giờ biết phần Excel đã đúng chưa.

- **Files:** `internal/report/bangcong/source.go`, `fixture.go`, `builder_test.go`.
- **Interfaces:**
  ```go
  type Row map[string]any            // khoá = MÃ FIELD ở dòng 7, không phải chữ cái cột
  type Source interface {
      LoadRows(ctx context.Context, periodStart, periodEnd time.Time) ([]Row, error)
  }
  ```
- **Steps:** viết `FixtureSource` trả 3 dòng cứng, đủ để kích hoạt mọi nhánh công thức đáng kiểm:
  1 người đủ dữ liệu, 1 người thiếu vài cột (kiểm nhánh `IF(...="","",...)`), 1 người có ngày công
  đặc biệt (`L-8`, `TASK-REF`, `TS/2`). Nhóm C **không xuất hiện trong `Row`** — vắng key = để trống ô.
- **Verify:** sinh file từ fixture, chạy Task 4.5, khẳng định **số cụ thể** ở ô tổng — ví dụ dòng có
  `AV=20`, `AW=1`, `AX=0`… thì `AS` (`=AV+SUM(AW:BF)+BH`) phải ra đúng tổng tính tay. Đây là lúc
  chứng minh "formula chạy được", không phải lúc lo DB.

### Task 7 — Nối DB adapter thật (phần "chưa đầy đủ")

- **Files:** `internal/report/bangcong/source_db.go`, `source_db_integration_test.go`.
- **Interfaces:** `type DBSource struct{...}` — **cùng interface `Source`** với fixture, thay được 1:1.
- **Steps:** truy vấn `raas_monthly_attendance` (nhóm A, §3.1, 19 mã đã map sẵn) join
  `wd_workers`/`wd_organizations`; dựng lưới ngày từ `wd_calculated_time_blocks` +
  `wd_calculated_time_block_tags` (nhóm B). **Mã nào chưa có nguồn thì KHÔNG đặt key** (G2).
- **Điều kiện tiên quyết:** (a) `docker compose up -d postgres` — hiện daemon Docker **đang không
  chạy**, cổng 5434 từ chối kết nối; (b) DB phải có dữ liệu đã sync thật, nếu rỗng thì chạy
  `adapter sync` trước; (c) **bảng quy đổi tag → mã ô chấm công phải được chốt** (§7 câu 1) — không
  có nó thì 31 cột `Workdays*` không thể đúng, và đây là việc nghiệp vụ, không phải việc code.
- **Verify:** test tích hợp trên DB thật, khẳng định số dòng và vài giá trị cụ thể; xác nhận key
  nhóm C **không tồn tại** trong map; đối chiếu 1 nhân viên với chính response RaaS thô.

### Task 6 — Ánh xạ mã field → cột và điền

- **Files:** `internal/report/bangcong/mapping.go`, `mapping_test.go`.
- **Steps:** đọc **dòng 7 của chính template** lúc khởi tạo để dựng `map[mã]cột` — **không hardcode
  chữ cái cột**. Xử lý riêng 4 mã hỏng `{r}` (§1.6.2): chuẩn hoá `Workdays{r}`→`Workdays9`,
  `Workdays1{r}`→`Workdays19`, `Workdays2{r}`→`Workdays29`, `Seniority{r}`→`Seniority9`, kèm comment
  giải thích vì sao.
- **Verify:** test khẳng định bản đồ có đúng **116** mã, và `Workdays1`…`Workdays31` ánh xạ đúng vào
  `EU`…`FY` liên tục không đứt (chính là chỗ 4 mã hỏng sẽ làm trượt nếu quên xử lý).

### Task 8 — Điểm vào (CLI + HTTP)

- **Files:** `cmd/adapter/main.go` (thêm `case "report"`), `internal/api/report.go` (mới).
- **Steps:** thêm lệnh `adapter report --period 2026-03 --out bangcong.xlsx`, và route
  `GET /reports/bangcong?period=YYYY-MM` trả về stream. Dùng `f.Write(w)`, không ghi file tạm.
- **Verify:** chạy CLI thật sinh file, mở được bằng Excel/LibreOffice không cảnh báo hỏng file.

### Task 9 — Golden test

- **Files:** `internal/report/bangcong/golden_test.go`, `testdata/`.
- **Steps:** sinh file từ 3 dòng fixture (Task 5), so **cấu trúc + giá trị đã tính** với bản vàng
  (merge, số công thức mỗi dòng, style index của các ô mốc, giá trị của ô dữ liệu và ô tổng) —
  **không so byte** (excelize không đảm bảo byte ổn định giữa các version).
- **Verify:** `go test ./internal/report/bangcong/...`.

### Task 10 — Tài liệu

Cập nhật chính file này (mục "Kết quả thi hành"), `self-docs/document-map.md`, và nhật ký `CLAUDE.md`.

---

## 5. Ràng buộc bao trùm (chép nguyên văn vào brief của mọi task)

- **G1 — Không hardcode chữ cái cột.** Mọi ánh xạ đi qua mã field ở dòng 7 của template.
- **G2 — Không điền 0 cho cột nhóm C.** Ô không có nguồn thì để trống. Điền 0 vào cột tiền/định mức
  làm công thức tổng ra số sai mà trông hợp lệ.
- **G3 — Không dựng lại style bằng code.** Chỉ chép style index từ dòng mầm. Nếu thấy mình đang gọi
  `NewStyle` cho ô dữ liệu là đã đi sai hướng.
- **G4 — Không commit dữ liệu nhân sự thật.** File gốc có 5 họ tên + mã NV + ngày vào làm; template
  nhúng vào repo phải sạch (Task 1). Kiểm trước khi commit.
- **G5 — Nhân bản từ dòng 12, KHÔNG từ dòng 13.** Dòng 13–17 dính 10 ô `#REF!`.
- **G6 — Bộ dịch công thức phải bỏ qua nội dung trong nháy kép.** `"L-10"`, `"x8-4"`, `"TASK-REF"`,
  `"TS/2-2"` là dữ liệu, không phải tham chiếu ô.
- **G7 — Pin `excelize v2.10.0`** đúng version `Core System-backend` đang chạy, để hai repo không lệch hành vi.
- **G8 — Không đụng Dockerfile.** excelize là Go thuần, `CGO_ENABLED=0` và image distroless giữ nguyên.
- **G9 — Một công cụ GHI, một công cụ KIỂM, không đảo vai.** Mọi thao tác **sửa/ghi** file `.xlsx`
  (kể cả bước làm sạch template) làm bằng **excelize (Go)**. Python/openpyxl **chỉ đọc** — dùng để
  đo và đối chiếu. Hai lý do: (a) openpyxl lưu lại file cũng có thể làm rơi định dạng, nếu dùng nó
  sửa template thì Task 0 kiểm chứng excelize xong cũng vô nghĩa; (b) kiểm bằng thư viện **khác** thư
  viện đã ghi file là điểm mạnh của phép kiểm — để excelize tự chấm điểm mình thì không còn giá trị.
  Ngoài ra Python **không tồn tại trong runtime image** của adapter (distroless static, không
  shell/libc/python), nên bất cứ thứ gì Python làm đều phải là bước offline chạy tay, không được lọt
  vào đường chạy thật.

---

## 6. Rủi ro và cách chặn

| Rủi ro | Mức | Chặn bằng |
|---|---|---|
| Bộ dịch công thức phá chuỗi literal (`"L-10"`→`"L-13"`) | **Cao** | Task 2 viết test trước, 3 case cạm bẫy bắt buộc |
| excelize làm hỏng màu theme+tint khi lưu lại | **Cao** | Task 0 là cổng, chạy trước mọi thứ |
| Bảng quy đổi tag → mã chấm công (`x8-4`, `L-10`…) chưa ai định nghĩa | **Cao** | Task 5 phải đối chiếu dữ liệu thật rồi chốt; không đoán |
| 4 mã field hỏng `{r}` làm trượt cột | Trung bình | Task 6 test khẳng định `Workdays1..31` liên tục |
| Excel không tự tính lại khi mở (công thức sống nhưng không có giá trị cache) | Trung bình | Đặt `CalcChain`/full recalc on load; verify bằng LibreOffice headless ở Task 4 |
| File 271 cột × N nghìn dòng → bộ nhớ | Thấp–TB | Nếu chậm, chuyển `StreamWriter`; nhưng StreamWriter **không** chép style/merge sẵn có → phải đo trước khi đổi |
| Hai repo cùng sinh Excel, logic trôi khỏi nhau | Thấp | Đã pin cùng version; ghi rõ trong tài liệu rằng đây là báo cáo của adapter, khác nhóm 13 report của backend |
| Xoá dòng 13–17 làm lệch tham chiếu của footer `SUBTOTAL` (dòng 18) | Trung bình | Task 1 có test riêng khẳng định footer trỏ đúng dải sau khi xoá — không tin hành vi dịch tham chiếu của excelize |

### 6.1 Sửa brief giữa đường — vì sao Task 0/1 đổi từ Python sang Go

Bản đầu của PLAN này viết bước làm sạch template bằng script Python (`sanitize.py`). Khi soạn brief
giao việc mới thấy chỗ đó **tự phá phép kiểm của chính mình**: Task 0 tồn tại để chứng minh *excelize*
không làm hỏng file, nhưng nếu template lại do *openpyxl* ghi ra thì bản đã kiểm và bản thật là hai
file do hai thư viện khác nhau tạo — chứng minh xong cũng không nói được gì về file thật. Đã sửa
thành: excelize ghi, openpyxl chỉ đọc (ràng buộc **G9**).

Ghi lại để người đọc sau không tưởng "Python là lựa chọn sai từ đầu" — nó sai ở **vai**, không sai ở
công cụ. openpyxl vẫn là thứ đã đo ra toàn bộ số liệu ở §1 và vẫn là công cụ kiểm chính thức.

---

## 7. Câu hỏi còn mở (không chặn khởi động, nhưng chặn hoàn thành)

1. **Quy tắc tag → mã ô chấm công.** Cần bảng chốt: tag Workday nào ra `x8`, `x8-4`, `L-8`, `TASK-REF`,
   `TS/2`, `DT`… Không có bảng này thì lưới 31 ngày không thể đúng.
2. **Cột nhóm C**: để trống vĩnh viễn, hay giai đoạn sau adapter sẽ gọi sang Core System lấy? Ảnh hưởng
   thiết kế `Row` (map thưa vs struct đầy đủ).
3. **`Sunday_Meal`/`Night_Meal` chia về 3 bộ phận (`Meal1..3`) theo quy tắc nào?** Workday trả 1 con
   số, file cần 3 ô.
4. **Có giữ dòng 10 và dòng 11** (hướng dẫn nguồn + mô tả quy tắc, cao 159 và 395 px) trong file
   xuất cho người dùng cuối không? Chúng là chú thích cho người làm mapping, không phải nội dung báo cáo.
5. **Đặt ở adapter có đúng chỗ không** — adapter hiện là CLI `migrate|sync|engine|serve`, chưa có
   route xuất file nào; còn `Core System-backend` đã có sẵn 13 generator + RBAC + company scope. Đã chốt
   adapter, ghi lại đây để người đọc sau biết đây là lựa chọn có ý thức, không phải mặc định.

---

## 8. Kết quả thi hành Task 0 + Task 1 (2026-07-31)

**Task 0 (GATE) — XANH.** `go get github.com/xuri/excelize/v2@v2.10.0` (pin đúng, không lấy
latest). `internal/report/bangcong/spike_test.go`: `excelize.OpenFile` → `SaveAs` không sửa ô nào.
`tools/xlsx_inspect.py` (mới, openpyxl — công cụ KHÁC excelize để tự chấm điểm) đo fingerprint
trước/sau: `diff /tmp/before.json /tmp/after.json` **rỗng tuyệt đối** — 76 merge, 1081 công thức,
123 công thức dòng 12, 22 fill combo (15 theme+tint) đều khớp 100%. Kết luận: excelize v2.10.0
round-trip an toàn cho file này, kiến trúc "nhúng template + excelize" ở §2 đứng vững.

**Mâu thuẫn brief vs PLAN (đã hỏi, user chọn):** PLAN gốc ghi Task 1 dùng `tools/sanitize.py`
(Python/openpyxl). Brief thi hành đưa ra sau đó đổi sang `tools/sanitize.go` dùng CHÍNH excelize,
lý do: Task 0 chỉ mới kiểm chứng excelize ghi an toàn, chưa có bằng chứng gì cho openpyxl ghi
(không đảo vai công cụ ghi/kiểm). User xác nhận qua `AskUserQuestion`: **theo brief — sanitize.go**.
File PLAN này giữ nguyên chưa sửa mục Task 1 (chỉ ghi chú lệch ở đây).

**Task 1 — Làm sạch template.** `internal/report/bangcong/tools/sanitize.go` (build tag `ignore`,
`go run` 1 lần): xoá 6 sheet còn lại, xoá dòng 44→26 (khối rác), 20 (backtick rác), 17→13 (5 nhân
viên thật + 10 ô `#REF!`) — **thứ tự dòng số cao trước** để index không trượt. Output:
`internal/report/bangcong/template/bangcong.xlsx` (144.9KB), nhúng qua `embed.go`
(`//go:embed template/bangcong.xlsx`, hàm `Open()` trả `*excelize.File`).

**Phát hiện quan trọng — excelize tự "vá" tham chiếu công thức khi `RemoveRow`, và vá SAI 1 chỗ
trong chính dòng mầm (dòng 12, đáng lẽ bất khả xâm phạm):**
- `A12` (cột STT) gốc là `=SUBTOTAL(3,$G12:G$13)`. Sau khi xoá dòng 13-17, excelize tự động co
  `$13` (giờ trỏ vào dòng đã xoá) xuống thành `$12` → `=SUBTOTAL(3,$G12:G$12)` (range suy biến 1 ô).
- Xác minh bằng cách đọc `A13..A17` **trong file nguồn, trước khi bị xoá** (dữ liệu này giờ chỉ
  còn tồn tại ở file nguồn, không còn trong template): `A13=SUBTOTAL(3,$G$13:G13)` (cache=1),
  `A14=...G14` (cache=2), ... `A17=...G17` (cache=5) — một dãy sạch, neo cố định ở dòng 13 (dòng
  nhân viên đầu tiên), lớn dần theo dòng hiện tại. Điều này chứng minh `G$13` trong công thức A12
  là tham chiếu **CỐ Ý hướng tới tương lai** — "dòng đầu tiên của danh sách nhân viên" — không phải
  tham chiếu tới thứ đã biến mất. Sau khi Task 3 nhân dòng mầm, dòng 13 **sẽ lại là** dòng nhân
  viên đầu tiên, giống hệt file gốc — nên `G$13` vẫn đúng, còn `G$12` (kết quả excelize tự vá) sai:
  nó trỏ vào chính dòng mầm (luôn rỗng), không phải điểm neo danh sách nhân viên.
- Quét toàn bộ dòng 1-12 + 18 bằng regex bỏ qua chuỗi trong nháy kép (tránh bẫy `"TASK-REF"`, `"TASK-REF"`
  bị nhận nhầm là tham chiếu ô — đúng cảnh báo G6 của PLAN): chỉ **2 ô** có tham chiếu chữ tới dòng
  13-17: `A12` (sai, cần vá) và `JB18` footer `=SUBTOTAL(3,JB2:JB17)` (excelize tự co đúng thành
  `JB2:JB12` — đã kiểm chứng đúng, không cần sửa).
- **Đã vá:** `sanitize.go` bước 3, sau vòng `RemoveRow`, gọi `SetCellFormula(sheet,"A12",
  "SUBTOTAL(3,$G12:G$13)")` ghi đè lại giá trị gốc, kèm comment giải thích đầy đủ lý do trong code.
  Đối chiếu lại toàn bộ 3252 ô dòng 1-12 (nguồn vs template): **0 sai khác** sau khi vá (trước khi
  vá: đúng 1 sai khác, chính là `A12`).

**Phát hiện phụ — `f.GetSheetDimension()` bị stale sau `RemoveRow`:** vẫn báo `A1:JK44` dù sheet
thật chỉ còn 13 dòng (kiểm bằng `f.GetRows()`/`f.GetCols()` đếm thật: 13 dòng, 271 cột — khớp).
Code Task 3 sau này **không được** dựa vào `GetSheetDimension` để suy ra biên dòng/cột.

**Test:** `internal/report/bangcong/template_test.go` — 6 test (1 sheet, 0 `#REF!`, dòng 12 đúng
123 công thức, footer `JB13=SUBTOTAL(3,JB2:JB12)`, `A12` khớp đúng công thức gốc đã vá, không còn
PII — needle PII đọc ĐỘNG từ file nguồn lúc chạy test, không hardcode tên/mã NV vào source code, an
toàn với G4). Cộng `spike_test.go` (Task 0) = **7/7 pass**. `go build`, `go vet` sạch.

**Trạng thái git:** chưa commit (đúng yêu cầu). File mới: `internal/report/bangcong/{spike_test.go,
embed.go, template_test.go, tools/sanitize.go, template/bangcong.xlsx}`, `tools/xlsx_inspect.py`.
`go.mod`/`go.sum` đổi (thêm `excelize v2.10.0` + transitive deps).

**Còn nợ:** chưa mở file bằng Excel/LibreOffice thật bằng mắt. Task 2 (bộ dịch `ShiftRows`) phải
biết: excelize tự vá tham chiếu khi xoá dòng KHÔNG đáng tin cho pattern "tham chiếu hướng tới tương
lai" như `A12` — nhưng đây là vấn đề của `RemoveRow` (Task 1), không phải của `DuplicateRow`/
`InsertRows` (rủi ro Task 2 đã lường trước ở §2.3). Hai việc khác nhau, đừng nhầm.

### 8.1 Kiểm chứng lại lần hai, độc lập (2026-07-31, phiên chủ)

Không tin báo cáo, tự chạy lại `openpyxl` trên template đã sinh: 1 sheet · 76 merge · 22 tổ hợp fill
(**15 theme+tint**) · 13 định dạng số · 7 cột ẩn · dòng ẩn {6,7} · 10 mục `column_dimensions` giống
từng giá trị · **466 ô công thức = 1081 − 5×123** · dòng mầm 12 đúng 123 công thức và giống nguyên
văn ở các ô mẫu (`A12`, `B12`, `M12`, `AS12`, `BI12`, `CF12`, `EG12`, `EK12`) · **0 ô `#REF!`** ·
**0 PII**. Footer ở dòng 13 với 14 công thức, tham chiếu đã dịch đúng (`JA18→JA13`, `F18→F13`).
Kết luận: mốc M1 đạt thật.

**Đính chính một nhận định sai của phiên chủ giữa chừng:** tôi từng kết luận `A12` "đang trỏ vào
footer nên Task 3 phải neo lại về `G$12`" — **sai**. Báo cáo Task 1 đúng: `G$13` là điểm neo *"dòng
nhân viên đầu tiên"* hướng tới tương lai (chứng minh bằng dãy `A13..A17` của file gốc), và vì Task 3
giữ dòng 12 làm mầm rồi đổ dữ liệu **từ dòng 13**, dòng 13 lại đúng là nhân viên đầu tiên. Giữ
`$G12:G$13`, không sửa. Sai của tôi đến từ việc đọc template sau khi xoá mà quên bố cục đích của
Task 3 — đã ghi rõ bố cục đó vào Task 3 để không ai vấp lại.

### 8.2 Đo năng lực `CalcCellValue` — 21/21 hàm được hỗ trợ

Chạy thật trên `excelize v2.10.0`, mọi hàm template dùng đều tính được, kể cả các ca khó nhất:

| Ca kiểm | Công thức đã chạy | Kết quả |
|---|---|---|
| `SUBTOTAL` sum/count | `=SUBTOTAL(9,A1:A3)` / `=SUBTOTAL(3,A1:A3)` | `20` / `3` |
| `INDIRECT` lồng trong `SUBTOTAL` | `=SUBTOTAL(9,INDIRECT("A"&1&":A"&3))` | `20` |
| **Đúng dạng footer thật** | `=IF(A1="","",SUBTOTAL(9,INDIRECT("A"&ROW()-20&":A"&ROW()-18)))` | `20` |
| `IF` so chuỗi mã chấm công | `=IF(C1="x8-4","x8","other")` | `x8` |
| `WEEKDAY` `DAY` `MONTH` `YEAR` `DATE` | | OK |
| `OR` `AND` `LEN` `SUM` `COUNTIF` `IFERROR` `ROUNDUP` `ROW` | | OK |

**Hệ quả:** không phải chọn giữa "công thức sống" và "có sẵn số" — làm được **cả hai**, đó là Task 4.5.

---

## 9. Kết quả thi hành Task 2, 3, 4, 4.5 (2026-07-31, phiên thứ 2)

Thi hành bởi phiên độc lập (không phải phiên viết Task 0/1), theo brief tự chứa dispatch riêng.
Task 0/1 không làm lại — đã kiểm chứng độc lập trước khi bắt đầu (đọc file thật, không tin báo cáo
cũ). Toàn bộ code mới: `formula.go`+`formula_test.go` (Task 2), `builder.go`+`builder_test.go`
(Task 3), `period.go` (Task 4), `recalc.go`+`calc_support_test.go`+`recalc_test.go` (Task 4.5),
`acceptance_test.go` (nghiệm thu end-to-end). **20 test case / 12 hàm test, tất cả xanh** (`go test
./internal/report/bangcong/... -v`), `go build`/`go vet` sạch toàn repo, `gofmt` sạch.

### 9.1 Task 2 — ShiftRows (CỔNG) — XANH

`ShiftRows(formula string, delta int) string`: quét ký tự tuần tự, cờ "đang trong chuỗi nháy kép",
chỉ dịch số dòng của tham chiếu ô hợp lệ không có `$`. 13 test case bảng (8 tối thiểu theo brief +
5 thêm, gồm cả bẫy `"x8-4"`, `"TS/2-2"`, `"TASK-REF"` trong nháy kép và tên hàm không bị nhầm tham
chiếu ô) + 1 test quét **toàn bộ 123 công thức thật của dòng mầm**, xác nhận không có literal nào
(`"L-10"`, `"TASK-REF"`...) bị đếm lệch trước/sau khi dịch. `go test -run TestShiftRows -v`: xanh
toàn bộ. **CỔNG XANH — đã sang Task 3.**

### 9.2 Task 3 — ExpandRows

`Builder.ExpandRows(n int) error`: nhân dòng mầm (12) thành dòng 13…12+n, đẩy footer xuống
13+n. Không dùng `GetSheetDimension` (stale) — dùng `GetCols`/`GetRows`.

**Phát hiện 1 — cell literal trong dòng mầm phải chép verbatim, không qua ShiftRows:** dòng mầm có
2 ô KHÔNG phải công thức (`JB12` = ngày `PayrollMonth`, `BU12` = `Used`=0). Xác nhận bằng cách đọc
`JB13..JB17`/`BU13..BU17` **trong file NGUỒN trước khi Task 1 xoá** — file gốc chép y nguyên các
giá trị này sang mọi dòng nhân viên (không dịch). `ExpandRows` chép các ô literal này verbatim
(không qua `ShiftRows`, `ShiftRows` chỉ áp cho công thức).

**Phát hiện 2 — footer KHÔNG "bất biến" như brief mô tả, phải qua `ShiftRows` như mọi công thức
khác (trừ `JB`):** thử đầu tiên copy verbatim toàn bộ 13 công thức còn lại của footer (theo brief:
"ROW()-relative... copy unchanged") — **test `TestBuilder_ExpandRows` bắt được sai ngay**:
`JA<footer>` = `IF(F<footer>="","",COUNTIF(JC:JC,F<footer>))` có tham chiếu **CÙNG DÒNG** (`F13`)
không qua `ROW()` — nếu không dịch, `F13` mãi mãi trỏ dòng 13 dù footer đã chuyển xuống dòng 16.
Sửa: áp `ShiftRows(formula, n)` cho **mọi** công thức footer (kể cả các công thức lồng `ROW()`, vì
`ShiftRows` không đụng token `ROW()` — không có số dòng để dịch — nên vô hại), **trừ** cột `JB`
(range tĩnh `JB2:JB12`, không thể dịch bằng `ShiftRows` vì sẽ dịch luôn đầu `JB2` cố định — phải
"giãn" riêng bằng `widenFooterRowCountRange`).

**Verify (n=3):** dòng 13/14/15 mỗi dòng đúng 123 công thức; style index `M13=M14=M15=M12`; footer
dòng 16, `JB16=SUBTOTAL(3,JB2:JB15)`; `A12` không đổi (vẫn giá trị Task 1 đã vá); `JB13/14/15` và
`BU13/14/15` khớp verbatim với `JB12`/`BU12`.

### 9.3 Task 4 — Neo kỳ báo cáo

**Brief/PLAN ghi SAI ô neo:** cả 2 tài liệu đều nói neo ở `J6`. Đọc công thức thật:
`J6=K6`, `K6=JB6`, `JB6=JB12` — **`JB12` mới là ô literal thật (trong dòng mầm)**; `J6/K6/JB6` đều
là công thức, ghi vào đó vô nghĩa (sẽ bị đè lại khi tính). `A6=DATE(YEAR(J6),MONTH(J6)-1,21)` và
tiêu đề chỉ đọc `YEAR()`/`MONTH()` của `J6`, **không đọc `DAY()`** — nên phần ngày của `JB12` không
quan trọng; theo đúng quy ước "PayrollMonth" (file gốc để ngày 1), `SetPeriod` ghi ngày 1 của tháng
kết thúc kỳ.

`SetPeriod(f, t) (start, end, key, err)` tái dùng `internal/payperiod.Current(t)`.

**Phát hiện — ghi `time.Time` trực tiếp làm ĐỔI STYLE:** `f.SetCellValue(sheet,"JB12", time.Time{})`
đổi style index từ 190 → 232 (excelize tự gán style ngày mặc định, ghi đè style gốc của ô) — xác
nhận bằng đo trực tiếp trước/sau. Sửa: tự tính serial number Excel (`t.Sub(epoch).Hours()/24`,
epoch `1899-12-30`) rồi `SetCellValue` bằng `float64` thuần — style giữ nguyên 190, giá trị hiển thị
vẫn đúng (đối chiếu `GetCellValue` định dạng = `01/07/2026`).

**Thứ tự bắt buộc: `SetPeriod` PHẢI gọi TRƯỚC `ExpandRows`** — `ExpandRows` chụp ảnh dòng mầm (gồm
`JB12`) rồi nhân bản; gọi sau sẽ để lại các dòng nhân viên mang kỳ cũ.

### 9.4 Task 4.5 — RecalcAll (2 lỗi excelize nghiêm trọng, cả 2 tự tìm + tự sửa)

**Lỗi 1 (đã biết trước, brief có nhắc sơ): excelize không có API công khai "ghi giá trị cache mà
giữ công thức".** Mọi hàm ghi giá trị (`SetCellValue`, `SetCellFloat`, `SetCellStr`,
`SetCellDefault`) đều gọi `removeFormula` ở cuối — xác nhận bằng đọc thẳng source `cell.go`. Thứ tự
sống sót qua save/reopen (xác nhận bằng test round-trip + đọc raw XML độc lập): `SetCellValue`
(ghi giá trị) **TRƯỚC**, `SetCellFormula` (ghi lại công thức) **SAU** — `SetCellFormula` chỉ đụng
`c.F`, không đụng `c.V`.

**Lỗi 2 (tự phát hiện, KHÔNG có trong brief, nghiêm trọng hơn nhiều): rò rỉ INDEX bảng shared-string
ra làm giá trị cache, khi giá trị cache là CHUỖI.** `SetCellFormula` gán cứng `c.T="str"` **vô điều
kiện** (đọc source, dòng `c.T, c.IS = "str", nil`). Với giá trị SỐ (`SetCellFloat`) không sao (số ghi
thẳng vào `<v>`, không qua bảng shared-string). Với giá trị CHUỖI (`SetCellValue(string)` →
`SetCellStr` → ghi **INDEX** vào bảng shared-string, gắn `t="s"` để báo "hãy tra bảng") — nhưng
`SetCellFormula` gọi ngay sau đó ghi đè `t="str"` ("đọc `<v>` làm chuỗi nghĩa đen") mà **không đổi
`<v>`** → độc giả thấy đúng con số INDEX, không phải giá trị thật. Bắt được nhờ chính hiện tượng lạ:
công thức tính ra `22` lại hiện `684` sau khi cache ~684 chuỗi khác trước đó trong cùng sheet — 684
khớp chính xác với "chuỗi thứ 684 được thêm vào bảng". Xác nhận bằng regression test tối giản
(`TestRecalcAll_DoesNotLeakSharedStringIndex`, không cần template thật, tạo 100 chuỗi đệm rồi kiểm
tra 1 ô số bị lệch hay không). **Sửa:** chỉ cache kết quả SỐ (`strconv.ParseFloat` được) qua
`SetCellFloat`; kết quả CHUỖI/rỗng (mã chấm công `M-AQ`, các nhánh `""`) **không cache được** —
đây là khoảng trống thật so với mục tiêu brief ("mọi ô ra số thật"), chỉ đóng được cho cột SỐ, chưa
đóng được cho cột hiển thị mã chấm công dạng text.

**Lỗi 3 (đã lường trước một phần, nhưng phạm vi rộng hơn brief nghĩ): `IF()` lồng có nhánh chia cho
0 làm rò `#DIV/0!` dù giá trị trả về đúng.** `EK`/`EO` (2 công thức mỗi dòng) có dạng
`IF(G="","",IF(...,ROUNDUP((EH/AR)*...,-3),...))` — khi `G` rỗng, `IF` NGOÀI đúng ra chọn nhánh `""`
mà không cần tính nhánh trong, nhưng `CalcCellValue` VẪN trả `err=#DIV/0!` kèm `result=""` **đúng**
— xác nhận bằng test tối giản độc lập với template. Brief chỉ tiên liệu cho dòng mầm (cố định rỗng
mãi mãi) — **tự phát hiện thêm: bất kỳ dòng nhân viên thật nào thiếu input (đặc biệt `AR`=0/rỗng)
cũng dính y hệt**, không riêng dòng mầm. `RecalcAll` bỏ qua dòng mầm (`seedRow`, không bao giờ có
dữ liệu thật); với dòng nhân viên thật, theo đúng nguyên tắc brief đã nêu cho lỗi `""`
("đừng vá công thức, điền đủ input") — test acceptance đã điền đủ `AR` cho mọi dòng nên không dính.

**Verify:** `TestCalcSupport_HardCases` xác nhận lại độc lập cả 3 case khó brief nêu (đều đúng như
brief nói). `TestCalcSupport_TemplateFunctions`: `CalcCellValue` chạy được trên 351/351 công thức
thật (bỏ dòng mầm). `TestRecalcAll_OnRealTemplate` + `TestRecalcAll_DoesNotLeakSharedStringIndex`:
xanh, kể cả sau save/reopen thật.

### 9.5 Nghiệm thu end-to-end (input → formula → số thật, 2 engine độc lập)

Chuỗi 2 tầng thật: `AS12=AV12+SUM(AW12:BF12)+BH12`, `BI12=AV12+AW12+AX12+AY12+AZ12+BA12+IY12+IZ12+JA12`,
`BJ12=BI12-AR12` (đọc từ template thật trước khi viết test). 3 dòng input tay (dòng 14 cố ý cho
`BJ=-1`, kiểm cả dấu âm). Giá trị tính tay: dòng13 `AS=22,BI=22,BJ=0`; dòng14 `AS=21,BI=21,BJ=-1`;
dòng15 `AS=22,BI=22,BJ=0`.

**Kiểm chéo 2 engine độc lập, cả 2 khớp tuyệt đối:**
- (a) Go/excelize (`CalcCellValue` + `RecalcAll` cache) — khớp cả 9 giá trị.
- (b) `soffice --headless --convert-to xlsx` (LibreOffice có sẵn ở `/opt/homebrew/bin/soffice`,
  tính lại thật) → đọc bằng `openpyxl data_only=True` (công cụ thứ 3, độc lập cả Go lẫn LibreOffice)
  — khớp cả 9 giá trị.

`go test -run TestAcceptance_InputToFormulaToRealNumber -v`: xanh, 9.7s (bao gồm gọi `soffice` thật).

### 9.6 Việc còn nợ / chuyển cho Task 5-8

- **Cache giá trị cho cột TEXT (mã chấm công M-AQ) vẫn chưa làm được** — Lỗi 2 ở trên chỉ đóng được
  cho cột số. Cần quyết định trước Task 6: chấp nhận cột hiển thị luôn "rỗng" với code-reader (chỉ
  đúng khi mở bằng Excel/LibreOffice thật), hay tìm cách khác (vd. để LibreOffice headless convert
  làm bước hậu xử lý cuối cùng trước khi trả file — nhưng distroless/CGO_ENABLED=0 không thể bundle
  LibreOffice vào adapter).
- Chưa mở file bằng Excel thật bằng mắt (chỉ kiểm bằng code + LibreOffice headless).
- Task 5 (Source/Fixture), Task 6 (mapping mã field→cột), Task 7 (DB), Task 8 (CLI/HTTP) chưa làm,
  đúng phạm vi dispatch.

---

## 10. Kiểm chứng độc lập Task 2+3+4+4.5, phát hiện D1/D2 (2026-07-31, phiên chủ)

Đây là báo cáo kiểm chứng độc lập (không phải của tác giả mục 9) — nguồn gốc của D1/D2 được sửa ở
mục 11. Giữ nguyên văn, không sửa nội dung, chỉ đánh lại số mục cho khỏi trùng với mục 9.

Artefact để lại (chưa commit): `internal/report/bangcong/{formula.go, formula_test.go, builder.go,
builder_test.go, period.go, recalc.go, recalc_test.go, calc_support_test.go, acceptance_test.go}`.
`go build`, `go vet` sạch. **31 test pass.**

### 10.1 Đạt — kiểm chứng độc lập bởi phiên chủ

| Task | Bằng chứng tự chạy lại |
|---|---|
| 2 `ShiftRows` | 13 case, gồm 3 bẫy nháy kép (`x8-4`, `TS/2-2`, `TASK-REF`+`TASK-REF` trong `OR()`), thêm 1 test quét **toàn bộ 123 công thức dòng mầm** |
| 3 `ExpandRows(3)` | mầm 12 giữ nguyên · dòng 13/14/15 mỗi dòng đúng 123 công thức · footer sang dòng 16 · `JB16 = SUBTOTAL(3,JB2:JB15)` **giãn** đúng · 76 merge còn nguyên · 1 sheet |
| 4 `SetPeriod` | kỳ `2026-02-21 → 2026-03-20` (đúng cửa sổ 21→20), tiêu đề tính ra `"BẢNG CHẤM CÔNG CỦA CBNV THÁNG  3/2026"` |
| Nghiệm thu | **Hai engine độc lập khớp nhau**: excelize và LibreOffice thật (`soffice` có ở `/opt/homebrew/bin`, đã chạy, KHÔNG bị skip) cùng ra `AS/BI/BJ` đúng số tính tay, gồm ca âm `BJ14 = −1` |
| Cơ chế cache | XML thô: `<c r="AS13" t="str"><f>AV13+SUM(AW13:BF13)+BH13</f><v>22</v></c>` — công thức **còn**, cache **có** |
| STT | Ra đúng **1/2/3** ở dòng 13/14/15 khi cột `G` (mã NV) có dữ liệu — xác nhận `$G12:G$13` mà Task 1 vá là ĐÚNG |

**Lưu ý về STT:** acceptance test không điền cột `G`, nên `A13..A15` ra `0` trong file nó sinh —
`SUBTOTAL(3,...)` là `COUNTA`, không có mã NV thì đếm 0. Không phải lỗi code; nhưng nghĩa là tiêu chí
verify "STT ra 1/2/3" của Task 3 **chưa được test nào phủ**. Phiên chủ tự điền `G`/`F` rồi kiểm lại
mới xác nhận được.

### 10.2 D1 (NẶNG, CHƯA SỬA) — `RecalcAll` phá 295 ô công thức ở dòng 6,7,8,9

**Nguyên nhân gốc:** **416 / 464 công thức trong template là SHARED FORMULA**
(`<f t="shared" ref="N6:AQ6" si="0">M6+1</f>` ở ô chủ, ô thành viên là `<f t="shared" si="0"></f>`
thân rỗng). `RecalcAll` gọi `SetCellFloat` lên ô **chủ** → excelize xoá **cả nhóm shared**; khi vòng
lặp tới ô thành viên thì `GetCellFormula` trả `""` → nhánh `if formula == "" { continue }` bỏ qua →
ô đó **mất công thức vĩnh viễn**.

| Dòng | Công thức trước | Sau `RecalcAll` | Mất |
|---|---|---|---|
| 6 (chuỗi ngày) | 35 | 6 | 29 |
| 7 (`WEEKDAY`) | 31 | 2 | 29 |
| 8 (header ngày) | 124 | 8 | 116 |
| 9 (`DAY`) | 124 | 3 | 121 |
| **shared tag toàn sheet** | **416** | **111** | |

Ví dụ cụ thể: `O9` từ `=DAY(O6)` còn `<c r="O9" s="88"><v>23</v></c>`.

**Hệ quả thật:** lưới ngày bị **đóng băng**. File đúng cho kỳ đã sinh, nhưng người dùng đổi ô neo kỳ
trong Excel thì header ngày không cập nhật — `FullCalcOnLoad` cũng không cứu được vì **không còn công
thức để tính**. Đây là phá đúng hai cam kết: "neo 1 ô, cả lưới tự đúng" (Task 4) và "giữ công thức
sống" (§0).

Dòng 13–15 **không bị** vì `ExpandRows` ghi chúng thành công thức thường, không shared. Dòng 12 không
bị vì `RecalcAll` cố tình bỏ qua.

**Hướng sửa:** `RecalcAll` chạy **hai lượt** — lượt 1 đọc TOÀN BỘ công thức vào memory *trước khi*
mutate ô nào; lượt 2 mới ghi value + formula. Nhóm shared bị xoá không còn làm lượt đọc trả rỗng.
Cách khác (rẻ hơn, mất cache ở header): bỏ qua dòng 1–11 vì `FullCalcOnLoad` sẽ lo.

### 10.3 D2 (TRUNG BÌNH, CHƯA SỬA) — giá trị cache bị đánh kiểu chuỗi

`SetCellFormula` ép `c.T = "str"` vô điều kiện, nên ô cache mang `t="str"`: đọc lại `AR13` (input
thường) ra `22` **kiểu số**, còn `AS13` (formula có cache) ra `'22'` **kiểu chuỗi**. Báo cáo Task 4.5
đã phát hiện cơ chế này (và dùng nó để giải thích vì sao phải đi qua `SetCellFloat`) nhưng **chưa nêu
hệ quả**: mọi giá trị cache đều là text, làm giảm chính cái lợi mà Task 4.5 nhắm tới. Excel mở thì
`FullCalcOnLoad` tính lại và trả về đúng kiểu; chỉ công cụ đọc bằng code bị ảnh hưởng.

### 10.4 Hạn chế đã biết, có chủ đích

- **102/123 công thức mỗi dòng dữ liệu không có cache.** Cố ý: công thức trả text hoặc `""` không
  cache được vì `SetCellStr` + `SetCellFormula` gây **rò chỉ số shared-string** — báo cáo Task 4.5 tái
  hiện được: cache giá trị `"22"` hiện ra `684`, đúng bằng index bảng chuỗi tại thời điểm đó. Hệ quả:
  **cột lưới ngày `M–AQ` (mã chấm công `x8`, `L-8`, `TS/2`) sẽ không bao giờ có cache** — Excel mở thì
  đúng, code đọc thì rỗng. Cần biết trước khi Task 5/6 đổ mã chấm công thật vào.
- **Dòng mầm 12 bị bỏ qua khi recalc**, do quirk excelize: `EK12`/`EO12` (`IF(G12="","",IF(...,
  ROUNDUP((EH12/AR12)*...)))`) trả đồng thời `result=""` (đúng) và `err=#DIV/0!` (sai) khi `G12` rỗng —
  nhánh false không được chọn vẫn bị đánh giá. Hợp lý vì dòng 12 không bao giờ mang dữ liệu, nhưng
  cache của nó là số cũ (`AS12 = 0`).
- **`acceptance_test.go` tự huỷ artefact:** LibreOffice `--convert-to xlsx --outdir` ghi **cùng đường
  dẫn** với input → file excelize gốc bị ghi đè. Phép kiểm vẫn hợp lệ (LibreOffice có tính lại thật),
  nhưng không còn bản excelize để soi. Chính chỗ này làm phiên chủ **kết luận sai một lượt** rằng
  LibreOffice phá công thức — thực ra là D1. Nên convert sang `--outdir` khác.

### 10.5 Bốn sự thật kỹ thuật phát sinh khi thi hành — ảnh hưởng trực tiếp Task 5/6

Ghi tách riêng vì cả bốn đều là thứ mà brief/PLAN ghi sai hoặc chưa lường tới, và cả bốn đều sẽ làm
Task 5/6 vấp nếu không biết trước.

**(1) Ô neo kỳ là `JB12`, không phải `J6`.** Xem đính chính ở Task 4.

**(2) `#DIV/0!` kèm giá trị ĐÚNG xảy ra ở BẤT KỲ dòng thiếu input, không riêng dòng mầm.**
`CalcCellValue` của excelize v2.10.0 trả **đồng thời** `result` đúng và `err = #DIV/0!` khi nhánh
`false` không được chọn vẫn bị đánh giá ngầm. Bản đầu của `recalc.go` xử bằng cách **skip dòng 12** —
chỉ đúng cho dòng mầm. Đo lại trên dòng mầm, **có đúng 4 ô chứa phép chia thật** (đã lọc bỏ dấu `/`
nằm trong chuỗi như `"TS/2-2"`):

| Ô | Công thức | Mẫu số | Rủi ro |
|---|---|---|---|
| `BM` | `=BL12/8` | hằng số 8 | an toàn |
| `BO` | `=BN12/8` | hằng số 8 | an toàn |
| `EK` | `…ROUNDUP((EH12/AR12)*CZ12+…)` | **`AR` = `StdWorkDay`** | `#DIV/0!` khi thiếu `StdWorkDay` |
| `EO` | `…ROUNDUP(((EL12/AR12)*CZ12)+…)` | **`AR` = `StdWorkDay`** | `#DIV/0!` khi thiếu `StdWorkDay` |

**Hệ quả cho Task 5:** fixture cố ý có một dòng "thiếu vài mã" — nếu dòng đó thiếu `StdWorkDay` thì
`RecalcAll` (hiện `return err` ngay khi `CalcCellValue` báo lỗi) sẽ làm **`Render` fail hoàn toàn**.
Phải xử trước, và xử theo nguyên tắc chứ không skip theo số dòng.

**(3) Dòng mầm có đúng 2 ô LITERAL (không phải công thức), `ExpandRows` nhân cả hai ra mọi dòng:**

| Ô | Giá trị | Mã dòng 7 | Vai trò |
|---|---|---|---|
| `JB12` | `2026-03-01` | `PayrollMonth` | ô neo kỳ (mục 1) |
| `BU12` | `0` | `Used` | mặc định của template, được `BW12 = BU12+BV12` tiêu thụ |

`BU = 0` nghĩa là **mọi dòng nhân viên sẽ hiện `Đã dùng phép năm = 0`** dù `Source` không có key
`Used`. Đây là **mặc định của chính template**, KHÔNG phải vi phạm G2 do ta tạo ra — và **không được
"dọn" thành trống**, vì nó tồn tại để `BW` có số cộng. Ghi lại để không ai nhầm hai chuyện đó.

**(4) `JA<footer>` phải qua `ShiftRows`, không chép nguyên.** Bản đầu của Task 3 mô tả footer là
"ROW()-relative, chép nguyên" — sai với `JA<footer>` = `IF(F<footer>="","",COUNTIF(JC:JC,F<footer>))`,
vốn tham chiếu **cùng dòng** nên phải dịch. Đã xử ở Task 3, ghi lại để không ai "sửa lại cho đúng brief".

### 10.6 Trạng thái tổng thể

| Task | Trạng thái |
|---|---|
| 0, 1, 2, 3, 4 | ✅ xong, đã kiểm chứng độc lập |
| 4.5 | ⚠️ **một phần** — cơ chế đúng cho cột số, nhưng D1 + D2 phải sửa |
| 5 (Source + fixture) | ⬜ chưa |
| 6 (ánh xạ mã field) | ⬜ chưa |
| 7 (DB thật) | ⬜ chưa — **chặn bởi**: Docker daemon không chạy, và **bảng quy đổi tag → mã chấm công chưa ai định nghĩa** (§7 câu 1) |
| 8 (CLI + HTTP) | ⬜ chưa |
| 9 (golden test) | ⬜ chưa |
| 10 (tài liệu) | 🔄 chính mục này |

**Việc kế tiếp nên làm, theo thứ tự:** sửa D1 (hai lượt) → sửa hoặc chấp nhận có ghi chú D2 → Task 5
→ Task 6. Task 7 chờ quyết định nghiệp vụ, không chặn 5/6.

---

## 11. Sửa D1/D2 + Task 5 + Task 6 (2026-07-31, phiên thứ 3)

Thi hành đúng thứ tự A→B→C→D theo brief (D1 là CỔNG, đã sửa + có test hồi quy trước khi sang Task 5).
Không làm lại Task 0-4 (đã kiểm chứng độc lập ở mục 10). Artefact mới:
`internal/report/bangcong/{source.go, fixture.go, render.go, render_test.go, mapping.go,
mapping_test.go}`; sửa `recalc.go` (chữ ký đổi), `recalc_test.go` (4 test mới), `acceptance_test.go`
(cập nhật theo chữ ký mới); `tools/xlsx_inspect.py` thêm `formula_count_by_row`. **43 test case / 27
hàm test — 0 fail** (từ 31 lên 43, không giảm). `go build`/`go vet`/`gofmt` sạch toàn repo.

### 11.1 (A) Sửa D1 — XÁC NHẬN bằng công cụ KIỂM (openpyxl), không tự chấm điểm bằng excelize

Đối chiếu baseline TRƯỚC khi sửa (đo bằng `xlsx_inspect.py` đã bổ sung `formula_count_by_row`):
dòng 6=35, dòng 7=31, dòng 8=124, dòng 9=124 — khớp đúng số mục 10.2 đã đo.

**Nguyên nhân xác nhận lại:** `RecalcAll` cũ đọc-rồi-ghi trong CÙNG một lượt quét; ghi `SetCellFloat`
lên ô CHỦ của một nhóm shared formula làm excelize xoá NGAY LẬP TỨC toàn bộ `GetCellFormula` của các ô
THÀNH VIÊN còn lại trong nhóm (xác nhận: không cần save/reopen, thấy ngay trong cùng lần chạy) — vòng
lặp tới các ô đó thì `GetCellFormula` trả `""`, nhánh bỏ qua, mất công thức vĩnh viễn.

**Sửa:** `RecalcAll` giờ 2 lượt tách biệt — Lượt 1 đọc TOÀN BỘ ô có công thức vào slice trong memory
(không mutate ô nào); Lượt 2 mới `CalcCellValue`+ghi từ slice đã chụp. Việc nhóm shared bị xoá ở Lượt
2 không còn ảnh hưởng vì Lượt 1 đã đọc xong hết trước đó.

**Verify bằng openpyxl (KHÔNG dùng excelize tự đọc lại — G9), sinh file thật rồi soi:**
```
python3 tools/xlsx_inspect.py /tmp/d1_verify.xlsx "202603_Bang_Cong,_Phu_Cap_Repor"
  row 6 : 35   row 7 : 31   row 8 : 124   row 9 : 124   (KHỚP baseline, không mất ô nào)
  row 12: 123  row 13: 123  row 14: 123   row 15: 123   row 16: 14
  total formula_cell_count: 835
```
Số lượng shared-formula tag (`t="shared"`) đổi từ 416 → 101 — **đây là thay đổi CHỦ ĐÍCH, không phải
lỗi**: mỗi ô được cache số qua `SetCellFloat`+`SetCellFormula` sẽ mất trạng thái "shared" (ghi lại
thành công thức thường), đúng như cách `ExpandRows` (Task 3) đã làm cho dòng 13-15 từ đầu. Số công
thức và NỘI DUNG công thức mới là bất biến cần giữ — đã giữ, số shared-tag không phải bất biến.

**Test hồi quy (khoá đúng điều D1 mô tả):** `TestRecalcAll_PreservesSharedFormulaGroups` — đếm công
thức mỗi dòng trước/sau `RecalcAll` trên CÙNG file, khẳng định KHÔNG dòng nào giảm; assert cứng dòng
6/7/8/9 = 35/31/124/124; assert `O9` vẫn còn công thức chứa `"DAY"`.

### 11.2 (A2) — RecalcAll không còn hard-fail khi CalcCellValue lỗi nhưng giá trị đúng

Đổi chữ ký: `func RecalcAll(f *excelize.File) (Diagnostics, error)`. Quy tắc đúng theo brief: lỗi hạ
tầng (`GetCols`/`SetCellFloat`/...) vẫn hard-fail; `CalcCellValue` lỗi nhưng parse được số → TIN giá
trị, cache, ghi vào `Diagnostics`; lỗi và không phải số → không cache, ghi `Diagnostics`; không lỗi →
hành vi cũ, không ghi diagnostic. **Bỏ nhánh `if row == seedRow { continue }`** — quy tắc trên đã bao
trùm: dòng 12 giờ LUÔN tạo đúng 2 diagnostic (`EK12`,`EO12`) mỗi lần chạy (vì `G12` mãi mãi rỗng), đây
là steady-state bình thường chứ không phải lỗi.

**Test hồi quy:** `TestRecalcAll_IncompleteRowDoesNotAbortRun` — dòng thiếu `AR` (StdWorkDay) →
`RecalcAll` KHÔNG lỗi, `Diagnostics` có đúng `EK<row>`/`EO<row>`, cột không liên quan (`AS`,`BI`) vẫn
đúng số.

### 11.3 (B) Quyết D2 — chọn NHÁNH 2 (chấp nhận), time-box ~20 phút

Đọc lại `cell.go`: `SetCellFloat`/`SetCellStr`/`SetCellDefault`/`SetCellBool` đều gọi `removeFormula`
ở cuối (xoá `c.F`); `SetCellFormula` là hàm DUY NHẤT không đụng `c.F` của cell khác nhưng lại gán cứng
`c.T="str"` KHÔNG ĐIỀU KIỆN, không có option nào trong `FormulaOpts` (chỉ có `Type`/`Ref`, dùng cho
formula ARRAY/SHARED/DATATABLE, không liên quan `c.T` giá trị) để đổi lại. **Không có đường nào qua
API công khai vừa giữ `<f>` vừa đúng kiểu số `t="n"`.** Xác nhận thêm: `excelize.GetCellType` báo
`CellTypeFormula` (nhìn `c.F != nil`, không nhìn `c.T`) — tức BẢN THÂN excelize không "thấy" lỗi gắn
nhãn này, chỉ độc giả ngoài (openpyxl, tôn trọng `t=` XML thô) mới bị ảnh hưởng.

**Chọn nhánh 2 — chấp nhận:** đã ghi rõ hệ quả vào doc comment của `RecalcAll` (giá trị ĐÚNG, kiểu
KHÔNG đúng — người gọi phải tự parse). Khoá bằng `TestRecalcAll_CachedNumericValueIsTypedAsText`:
verify NỬA giá trị đúng (`22`) VÀ nửa kiểu sai (`GetCellType`→`CellTypeFormula` phía excelize; XML thô
`t="str"` phía ngoài — đọc trực tiếp qua `archive/zip` thay vì tin cách excelize tự báo cáo). Nếu bản
excelize sau này đổi hành vi, test này đỏ ngay, không lặng lẽ dựa vào giả định cũ.

### 11.4 (C) Task 5 — Source + FixtureSource + Render

`Row map[string]any` (khoá = mã field dòng 7), `Source` interface, `FixtureSource` (3 dòng cứng theo
đúng mô tả đã sửa: dòng 1 đủ dữ liệu, dòng 2 thiếu vài mã (có `StdWorkDay`), dòng 3 THIẾU HẲN
`StdWorkDay`). `Render(ctx, src, period)` đúng thứ tự: `Open` → `SetPeriod` (TRƯỚC `ExpandRows`) →
`ExpandRows(len(rows))` → ghi từng dòng qua `FieldMap` (Task 6) → `EnableFullCalcOnLoad` →
`RecalcAll`.

**3 dòng fixture:**
```
row 1: {EmployeeCode: NV001, EmployeeName: Nguyen Van A, OrgStructureName: Phong Ke Toan,
        StdWorkDay: 22, RealWorkDay: 20, LeaveDayL: 1, LeaveDayF: 1}
row 2: {EmployeeCode: NV002, OrgStructureName: Phong Ke Toan, StdWorkDay: 22, RealWorkDay: 18}
row 3: {EmployeeCode: NV003, OrgStructureName: Phong Ke Toan, RealWorkDay: 22}   ← thiếu StdWorkDay
```

**Tính tay (đọc công thức thật trước khi viết test, KHÔNG lấy từ output chương trình):**

| Dòng | AS = AV+SUM(AW:BF)+BH | BI = AV+AW+AX+AY+AZ+BA+IY+IZ+JA | BJ = BI−AR | STT (A) |
|---|---|---|---|---|
| 13 (NV001) | 20+2+0=**22** | 20+1+0+0+1+0+0+0+0=**22** | 22−22=**0** | COUNTA(G13:G13)=**1** |
| 14 (NV002) | 18+0+0=**18** | 18+0+...=**18** | 18−22=**−4** | COUNTA(G13:G14)=**2** |
| 15 (NV003) | 22+0+0=**22** | 22+0+...=**22** | 22−(rỗng=0)=**22** | COUNTA(G13:G15)=**3** |

**Kiểm chéo 2 engine, khớp tuyệt đối cả 12 giá trị (kể cả STT — LẦN ĐẦU được test thật với dữ liệu
có cột `G`, trước đây `acceptance_test.go` không điền `G` nên STT luôn ra 0, chưa test được tiêu chí
Task 3):**
- Go/excelize (`cachedFloat`): `A13=1 AS13=22 BI13=22 BJ13=0`, `A14=2 AS14=18 BI14=18 BJ14=-4`,
  `A15=3 AS15=22 BI15=22 BJ15=22`.
- LibreOffice headless (`soffice`, `--outdir` KHÁC thư mục input — sửa đúng lỗi mục 10.4 đã nêu, xác
  nhận file input còn tồn tại sau khi convert) đọc lại bằng openpyxl: khớp cả 12/12.

`go test -run TestRender_ProducesCorrectValues -v`: PASS (~10s, gồm gọi `soffice` thật).

### 11.5 (D) Task 6 — ReadFieldMap

Đọc dòng 7 CỦA CHÍNH TEMPLATE lúc khởi tạo, không hardcode chữ cái cột. **Phát hiện khi đo:** dòng 7
làm HAI VAI TUỲ CỘT — ở lưới ngày (`M..AQ`) dòng 7 là công thức `WEEKDAY(...)` (không phải mã field);
ở mọi cột khác là chuỗi mã field literal. `ReadFieldMap` bỏ qua cột có CÔNG THỨC ở dòng 7 (không phải
"không có mã" — là một loại ô khác hẳn). Bỏ qua sai chỗ này lúc đầu ra 147 mã (gồm lẫn 31 công thức
`WEEKDAY`) — sửa lại đúng **116**.

4 mã hỏng chuẩn hoá đúng: `Workdays{r}→Workdays9` (FC), `Workdays1{r}→Workdays19` (FM),
`Workdays2{r}→Workdays29` (FW), `Seniority{r}→Seniority9` (IR). Bất biến "0 overlap mã field × công
thức dòng mầm" đo được **0** — khớp đúng brief. Bẫy `SeniorityRate` (cột `EP`) xác nhận KHÔNG lẫn vào
`Seniority1..12` (khớp bằng chuỗi chính xác qua map key, không qua prefix).

**Verify:** 116 mã đúng, 0 trùng, `Workdays1..31` liên tục `EU..FY`, `Seniority1..12` liên tục
`IJ..IU`, `SeniorityRate` (EP) tách biệt, 0 overlap với công thức dòng mầm — 7 test, tất cả xanh.

### 11.6 Brief ghi sai/thiếu so với thật

- Mục ④ báo cáo brief gọi mã "2b" nhưng đánh số trùng với mã có sẵn — đã diễn giải là "mục báo cáo bổ
  sung", không phải lỗi kỹ thuật.
- Không phát hiện chỗ nào brief sai về mặt KỸ THUẬT lần này (4 sự thật đã xác lập ở mục 10.5 đều đúng
  và đã dùng làm nền); brief này chủ yếu SỬA CHỮA hai lỗi mục 10 đã nêu đúng, không tự giới thiệu lỗi
  mới cần đính chính.

### 11.7 Còn nợ

- Cache giá trị cho cột TEXT (mã chấm công `M-AQ`) vẫn chưa làm được (D2 không giải quyết vấn đề
  riêng này — đó là lỗi rò shared-string index, khác D2 là lỗi gắn nhãn kiểu). Cần quyết định trước
  khi đổ dữ liệu Workday thật vào lưới ngày.
- Task 7 (DBSource) chờ: Docker daemon chưa chạy, bảng quy đổi tag Workday→mã chấm công chưa ai chốt.
- Task 8 (CLI/HTTP), Task 9 (golden test) chưa làm — đúng phạm vi dispatch.
- Chưa mở file bằng Excel/LibreOffice thật bằng mắt (chỉ kiểm bằng code + LibreOffice headless).
- Chưa commit.

---

### 11.8 Kiểm chứng độc lập phiên 3 (phiên chủ) — D1 ĐẠT, cộng 2 phát hiện mới

**Chạy lại thật:** `go build` + `go vet` + `gofmt` sạch, **43 test pass** (đúng như báo cáo).

**D1 — đạt, và tôi kiểm mạnh hơn test của phiên 3.** Test `TestRecalcAll_PreservesSharedFormulaGroups`
chỉ khẳng định *số lượng* công thức và *`O9` còn chứa `DAY`*. Điều đó **chưa loại trừ rủi ro thật sự
đáng lo**: khi excelize giãn shared formula thành công thức thường, nếu nó chép nguyên văn thân của ô
**chủ** sang ô **thành viên** thì `O9` sẽ thành `DAY(M6)` — vẫn "chứa DAY", vẫn đủ số lượng, nhưng sai
lệch 2 ngày. Nên tôi **so nội dung từng ô** của 4 dòng lưới ngày, template vs output:

```
đã so 314 ô, lệch 0
M9=DAY(M6)  N9=DAY(N6)  O9=DAY(O6)  P9=DAY(P6)   ← offset đúng từng ô
N6=M6+1     O6=N6+1     AQ6=AP6+1
AQ9 = IF(DAY(AQ6)=21,"",DAY(AQ6))                ← giữ nguyên nhánh guard
```

Kết luận: D1 sửa đúng. Việc `shared 416 → 101` là **hệ quả chủ đích** và lập luận của phiên 3 đúng —
bất biến cần giữ là *nội dung công thức*, không phải trạng thái `shared`. Bằng chứng là 0 lệch trên
314 ô, mạnh hơn cả claim ban đầu.

**F1 (MỚI) — kỳ tháng 2 rò 2 cột hiển thị ngày NGOÀI kỳ; và Task 4 verify chưa từng chạy.**

Kỳ `2026-02-21 → 2026-03-20` dài **28 ngày**, nhưng lưới có **31 cột** `M`–`AQ`:

| Cột | Ngày thật (dòng 6) | Hiện ở dòng 9 | Ẩn? | |
|---|---|---|---|---|
| `AN` | 2026-03-20 | `20` | không | ngày cuối kỳ ✓ |
| `AO` | 2026-03-21 | `21` | **ẩn** | ngoài kỳ, may là cột ẩn |
| `AP` | 2026-03-22 | `22` | không | **ngoài kỳ, ĐANG HIỆN** |
| `AQ` | 2026-03-23 | `23` | không | **ngoài kỳ, ĐANG HIỆN** |

Nguyên nhân: kỳ 21→20 dài đúng bằng số ngày của tháng đầu, nên tháng 31 ngày vừa khít 31 cột; tháng
30 ngày tràn 1 cột và nhánh `IF(DAY(AQ6)=21,…)` xử đúng ca đó; **tháng 2 tràn 3 cột và nhánh guard
không bắt** (`DAY(AQ6)=23 ≠ 21`). Đây là **hạn chế của template gốc**, không phải do code Go — nhưng
báo cáo cho người dùng cuối vẫn sai, nên phải quyết.

Kèm theo: **không có `period_test.go`, và mọi test đều dùng đúng một kỳ `time.Date(2026, 3, …)`** →
tiêu chí verify "3 kỳ 28/30/31 ngày" của Task 4 **chưa từng được chạy**. Không phải phiên 3 bỏ sót
đơn thuần: tiêu chí đó do PLAN ghi và **PLAN ghi sai giả định** (xem đính chính ở Task 4).

**F2 (MỚI, quan trọng cho cam kết sản phẩm) — G2 KHÔNG bảo vệ được cột DẪN XUẤT.**

Ràng buộc G2 nói "mã chưa có nguồn thì để trống, cấm điền 0, vì điền 0 làm công thức tổng ra một con
số trông hợp lệ mà sai". Đo thật cho thấy **để trống cũng ra đúng con số đó**, vì Excel coerce ô trống
thành 0 trong phép số học:

| Dòng fixture | `AR` (StdWorkDay) | `BJ` = `BI − AR` | Ý nghĩa hiển thị |
|---|---|---|---|
| row13 (đủ) | 22 | `0` | đúng |
| row14 (thiếu vài mã) | 22 | `-4` | đúng |
| row15 (**thiếu `StdWorkDay`**) | *trống* | **`22`** | "Chênh lệch ngày công = +22" — **vô nghĩa nhưng trông hợp lệ** |

Và với toàn bộ **nhóm C** (không có nguồn nào): `BW`, `CF`, `DR`, `EG`, `EK` đều ra **`0`** cho **mọi**
dòng. Tức là báo cáo hiện tại nói "Thành tiền tất cả PC = 0" cho tất cả nhân viên — đọc như một câu
trả lời thật, không đọc như "chưa có dữ liệu".

**Kết luận về G2:** nó bảo vệ *ô đầu vào* (ô trống là trung thực) nhưng **không** bảo vệ *ô dẫn xuất*.
Đây là quyết định thiết kế còn mở, thuộc người dùng: (a) chấp nhận cho UAT kèm chú thích/legend rõ
"cột chưa có nguồn"; (b) làm trống luôn cột tổng khi đầu vào của nó vắng; (c) hiện dấu hiệu trực quan.
Không tự quyết trong plan này.

### 11.9 Trạng thái tổng thể (cập nhật sau kiểm chứng phiên 3)

| Task | Trạng thái |
|---|---|
| 0, 1, 2, 3 | ✅ xong, đã kiểm chứng độc lập |
| 4 (neo kỳ) | ⚠️ **gần xong** — `SetPeriod` đúng (ghi `JB12`), nhưng **verify 3 kỳ chưa chạy** và có F1 (tràn cột tháng 2) |
| 4.5 + D1 + D2 + A2 | ✅ xong — D1 sửa (0/314 ô lệch), D2 chấp nhận có test khoá, A2 có `Diagnostics` |
| 5 (Source + fixture) | ✅ xong — `Render` + `FixtureSource`, STT ra 1/2/3, kiểm chéo 12/12 khớp |
| 6 (ánh xạ mã field) | ✅ xong — 116 mã, 4 mã hỏng chuẩn hoá, 0 clash |
| 7 (DB thật) | ⬜ chưa — chặn bởi Docker + **bảng quy đổi tag chưa định nghĩa** |
| 8 (CLI + HTTP) | ⬜ chưa |
| 9 (golden test) | ⬜ chưa |
| 10 (tài liệu) | 🔄 mục này |

**Nợ kỹ thuật đã biết, xếp theo mức:** F2 (cột dẫn xuất ra 0 trông như thật) → cần **quyết định của
người dùng**, không phải việc code. F1 (tràn cột tháng 2) → sửa được ở tầng Go (làm trống cột ngoài
kỳ) nhưng phải xác nhận vì nó đụng hiển thị. Cache cột TEXT (`M`–`AQ`) → chấp nhận, đã ghi rõ. Chưa mở
Excel thật bằng mắt. Chưa commit.

---

## 12. Đổi cấu trúc DB thì ảnh hưởng tới đâu (phân tích 2026-07-31)

Câu hỏi của người dùng: "nếu thay đổi cấu trúc bảng dưới DB thì hàm chúng ta có ảnh hưởng nặng
không". Trả lời bằng bằng chứng, không phỏng đoán.

### 12.1 Hiện trạng: package KHÔNG có một dòng nào biết DB tồn tại

Kiểm import từng file không phải test của `internal/report/bangcong/`: chỉ `github.com/xuri/excelize/v2`,
stdlib (`fmt`, `strconv`, `strings`, `bytes`, `embed`, `context`, `time`), và `Core System-adapter/internal/payperiod`.
**Không** `pgx`, **không** `database/sql`, **không** `internal/db`, **không** `internal/store`, **không**
chuỗi SQL hay tên bảng nào.

| Tầng | File | DB đổi thì sao |
|---|---|---|
| Excel/template | `formula.go`, `builder.go`, `period.go`, `recalc.go`, `embed.go` | **miễn nhiễm** |
| Ánh xạ | `mapping.go` — đọc dòng 7 template, khoá theo mã field | **miễn nhiễm** |
| Biên (seam) | `source.go` — `Row map[string]any` + `Source` interface | **miễn nhiễm** (hợp đồng theo mã field, không theo cột DB) |
| Nguồn dữ liệu | `source_db.go` — **Task 7, chưa viết** | **chỗ duy nhất phải sửa** |

Đây đúng là lý do Task 5 (fixture) được tách khỏi Task 7 (DB) và cả hai dùng chung `Source` — không
phải để đẹp kiến trúc mà để chịu được đúng tình huống này.

### 12.2 Năm loại "đổi cấu trúc DB", mức ảnh hưởng khác nhau

| Loại | Ảnh hưởng | Mức |
|---|---|---|
| (a) Đổi tên cột / bảng / kiểu dữ liệu | chỉ SQL trong `DBSource` | nhẹ, 1 file |
| (b) **Đổi key trong `raw` JSONB** | chỉ JSONB path trong `DBSource` | nhẹ, 1 file — **loại phổ biến nhất ở repo này** |
| (c) Thêm nguồn cho một mã field MỚI | phải sửa **template Excel** (mã phải có ở dòng 7), không phải sửa code | nặng hơn, nhưng không do DB gây ra |
| (d) **MẤT nguồn của một mã đang dùng** | `DBSource` không đặt key → ô trống → **cột dẫn xuất âm thầm ra 0** (§11.8 F2) | **nguy hiểm nhất: sai số liệu, không lỗi, không test đỏ** |
| (e) Đổi chiến lược ghi | `raas_monthly_attendance` hiện **delete + reinsert toàn bộ theo kỳ** (migration `0023`: report không có wid ổn định) → đọc trúng lúc sync thấy dữ liệu nửa vời | cùng họ rủi ro, cần đọc có kiểm `computed_at` hoặc trong transaction |

Về (b): adapter **cố ý** lưu `raw JSONB` với tên field gốc của Workday, không rename — comment
migration `0001` ghi thẳng *"nothing is renamed or flattened"*; `raas_monthly_attendance` chỉ flatten
**3 cột số** (`standard_working_days`, `actual_working_days`, `paid_holidays`), **35 field còn lại nằm
trong `raw`**. Nên phần lớn "đổi cấu trúc" ở đây **không phải DDL** mà là Workday đổi tên field.

### 12.3 Hàng rào đang thiếu — việc phải làm trong Task 7

Hiện có test khoá **phía template** (116 mã, 0 clash, `Workdays1..31` liên tục `EU`–`FY`). **Không có**
hàng rào nào phía DB khẳng định *"mã field nào `DBSource` hứa cung cấp thì thật sự có nguồn"*.

**Yêu cầu bắt buộc cho Task 7:** một test liệt kê **tập mã field `DBSource` bao phủ**, đối chiếu với
một danh sách khai báo tường minh trong code. DB đổi làm rụng một mã → **test đỏ ngay**, thay vì báo
cáo âm thầm ra `0`. Đây là thứ biến loại (d) từ "sai im lặng" thành "sai ồn ào".

**Kết luận:** nhẹ về code (một file chưa tồn tại), **nhưng nặng về đúng/sai số liệu** nếu không đóng
F2 (§11.8) và không có hàng rào coverage nói trên. Chỗ đáng lo không phải sửa code — là báo cáo vẫn
ra số khi dữ liệu đã mất.

---

## 13. Bàn giao Task 7 cho đội DB — và đính chính nhóm C

Đã viết tài liệu bàn giao riêng cho người phụ trách DB:
**`self-docs/Task7-DB-Source-BanGiao-DoiDB-310726.md`** (viết cho NGƯỜI đọc, văn xuôi đầy đủ, không
phải brief cho agent). Nội dung: ranh giới hợp đồng `Source`, 19 mã nhóm A cần xác nhận, 3 truy vấn SQL
sẵn để lấy danh sách tag chấm công thật, 6 câu hỏi kỹ thuật về DB, và cảnh báo F2.

**ĐÍNH CHÍNH quan trọng cho mục 3.3 ("nhóm C — chưa có nguồn"):** đánh giá ban đầu là quá bi quan. Sau
khi đọc hết **29 migration** của `Core System-adapter` (trước đó chỉ đọc `0001`, `0004`, `0023`), nhiều mã
nhóm C **có ứng viên nguồn thật** trong DB hiện tại:

| Mã field nhóm C | Ứng viên nguồn mới tìm thấy |
|---|---|
| `AmountTrip1..3`, `AmountTrans1..3` | `raas_allowance_plans` (`employee_id`, `compensation_plan_id`, `amount`) — migration `0028` |
| `AddIn`, `Used`, `UsedLastYear`, `Budget2` | `wd_time_off_plan_balance_records` (`0008`), `wd_override_balances` (`0014`), `wd_carryover_overrides` (`0016`) |
| `AttendanceStatus` | `raas_absence_requests.status` (`0029`) hoặc `raas_all_worker_time_off` (`0023`) |
| `JobTitleName` | `wd_job_profiles.job_title` (`0024`) |
| `GraduationName`, `RootRegionName`, `RecProvinceName`, `PermanentProvince` | `wd_workers.raw` (Get_Worker) |
| `DateQuit` | `wd_workers.raw` hoặc `wd_worker_transaction_logs` (`0020`, transaction Termination) |
| `OrgStructure1..3` | `wd_worker_transaction_logs` (job change) + `wd_organizations` — cần suy diễn theo khoảng thời gian |

Chưa xác nhận, đều là phỏng đoán từ tên bảng/cột — chờ người phụ trách DB trả lời. Nhưng nghĩa là
**phạm vi thật của Task 7 rộng hơn dự kiến ban đầu**, và điều đó tốt: nhiều cột tưởng phải để trống
vĩnh viễn thì thực ra có đường lấy dữ liệu.

Vẫn giữ nguyên: `MealUAll`, `PhoneUAll`, `TripUAll`, `TransUAll`, `RepUAll` thuộc **Core System** (dòng 4
của file ghi rõ), và `DO`/`DQ` chính file gốc ghi `??? Not available` — không thuộc phạm vi đội DB.

---

## 14. Restore dump DB thật (2026-07-31) — Task 7 gần như được mở khoá

### 14.1 Việc đã làm

Restore `document/payroll_adapter_dump_20260731_170100.sql` (953 MB, 192.428 dòng, plain SQL, dump từ
PostgreSQL **16.14**) vào DB đích.

**Đích thật là `localhost:5432/payroll_adapter`** — đọc từ `Core System-adapter/.env`
(`DATABASE_URL=postgres://localhost:5432/payroll_adapter`), **không phải** cổng 5434 của
`docker-compose.yml`; Docker daemon lúc đó cũng đang tắt. Server local là PostgreSQL **14.18**
(Postgres.app).

**Bốn vấn đề phát hiện TRƯỚC khi chạy, đã trình bày rồi mới xin quyết định:**

1. **DB đích không rỗng** — 33 bảng, 216 MB dữ liệu thật (4.186 `wd_workers`, 22.997 `wd_change_log`…).
   Dump có `CREATE TABLE` nhưng **không có `DROP`** nào và không có `CREATE DATABASE` → nếu chạy đè sẽ
   lỗi "already exists" và `COPY` có thể nhân đôi/vi phạm PK.
2. **Role `adapter` không tồn tại** trên server local (chỉ có `postgres`, `thaidt`), dump có **72 lệnh
   `OWNER TO adapter`**.
3. **Lệch phiên bản 16.14 → 14.18.** Đã quét trước: **không có syntax riêng của 15/16**
   (không `COMPRESSION`, không `NULLS NOT DISTINCT`, không `CREATE EXTENSION`, không
   `SET SESSION AUTHORIZATION`). Chỉ 2 dòng `\restrict`/`\unrestrict` là meta-command psql mới → xử
   bằng cách lọc qua `sed` khi stream, không tạo file tạm 953 MB.
4. Docker tắt nên không dùng được `postgres:16` của compose (vốn khớp phiên bản hơn).

**Quyết định của người dùng** (qua `AskUserQuestion`, có nêu rõ phương án backup ngay bên cạnh):
**drop + tạo lại `payroll_adapter`, KHÔNG backup**; role `adapter` **bỏ qua**, để owner là `postgres`.
216 MB dữ liệu cũ đã mất, không phục hồi được — ghi lại đây vì đó là lựa chọn có ý thức, không phải sơ suất.

**Kết quả:** restore **15 giây**, exit 0. 72 dòng lỗi — phân loại lại thì **72/72 đều là
`role "adapter" does not exist`**, không lẫn một lỗi thật nào.

| Chỉ số sau restore | Giá trị |
|---|---|
| Bảng (`BASE TABLE`) | **46** |
| **View** | **9** ← xem §14.2 |
| Index / constraint | 128 / 87 |
| Dung lượng | 429 MB |

### 14.2 Phát hiện lớn nhất: 9 VIEW không nằm trong migration nào của repo

Repo `Core System-adapter` có 29 migration tạo ra ~35 bảng. DB thật có **46 bảng + 9 view**. Ba bảng mới
(`raas_ot_actual_blocks`, `raas_ot_actual_block_tags`, `schema_migrations`) và **toàn bộ 9 view** là thứ
đội DB đã dựng thêm mà repo chưa có. Chúng trả lời gần hết những gì tài liệu bàn giao đang định hỏi:

| View | Cột | Giải quyết mã field nào |
|---|---|---|
| **`ts_attendance_daily_pivot`** | `worker_wid`, `employee_id`, `calculated_date`, `full_name`, `business_title`, `supervisory_org_name`, rồi **một cột numeric cho MỖI tag**: `off`, `actual_working_day`, `paid_holiday`, `night_meal`, `uncompensated_day`, `paid_leave`, `unpaid_leave`, `unpaid_leave_gte_30_days`, `sick_leave_gte_30_days`, `sunday_meal`, `off_in_lieu_1x`, `off_in_lieu_2x`, `ot_actual_cash`, `ot_actual_cash_and_off_in_lieu`, `cash_1x`, `cash_2x`, `cash_3x`, `maternity_leave`, `pay_back` | **`Workdays1`…`Workdays31`** — đúng hình dạng cần cho lưới 31 ngày: một dòng mỗi (nhân viên, ngày) |
| `ts_attendance_daily` | dạng dài: `calculation_tag_descriptor`, `total_quantity`, `source_block_count` + `full_name`, `business_title`, `position_id`, `supervisory_org_name` | bản chi tiết của view trên |
| `ts_time_off_plan_balances_pivot` | `annual_leave_balance`, `sick_leave_balance`, `off_in_lieu_balance` | `AddIn`, `Used`, `UsedLastYear`, `Budget2`, `BP` (phép tồn) |
| `ts_ot_reconciliation` | `date`, `requested_hours`, `submitted_hours`, `denied_hours`, `actual_hours`, `variance_hours` | `OT_CN`, `OT_Ho` (**tính bằng GIỜ**) |
| `ts_worker_job_change_log` / `_diff` | log/diff đổi vị trí theo `effective_moment` | `OrgStructure1..3` (bộ phận theo Job Change trong kỳ) |
| `ts_worker_organization_change_diff` | đổi tổ chức | `OrgStructure1..3` |
| `ts_worker_compensation_change_log` / `_diff` | đổi lương/phụ cấp | `AmountTrip*`, `AmountTrans*` |

### 14.3 Danh sách 19 tag chấm công thật — V1 gần như đã tự trả lời

Chạy đúng 3 truy vấn đã soạn cho đội DB, trên dữ liệu thật:

| Tag | Số block | Số NV | Tag | Số block | Số NV |
|---|---|---|---|---|---|
| `Actual_Working_Day` | 675 | 117 | `Sunday_Meal` | 70 | 36 |
| `OFF` | 638 | 219 | `Off_in_Lieu_1x` | 42 | 12 |
| `Night_Meal` | 321 | 85 | `OT_-_Actual_(Cash_&_Off_In_Lieu)` | 35 | 9 |
| `Uncompensated_Day` | 304 | 48 | `Cash_1x` | 28 | 8 |
| `Paid_Holiday` | 299 | 35 | `Cash_2x` | 14 | 8 |
| `Paid_Leave` | 231 | 49 | `Off_in_Lieu_2x` | 13 | 7 |
| `Unpaid_Leave` | 180 | 28 | `OT_-_Actual_(Cash)` | 9 | 5 |
| `Sick_Leave_(>=30_days)` | 81 | 3 | `Maternity_Leave` | 5 | 2 |
| `Unpaid_Leave_(>=30_days)` | 74 | 5 | `Cash_3x` | 5 | 4 |
| | | | `Pay_Back` | 2 | 2 |

**`calculated_quantity` tính bằng NGÀY, không phải giờ** — phân bố thực tế gần như chỉ có `0.5` và
`1.0` (vài ngoại lệ `2.0`, `4.0`, `8.0`, và `Night_Meal` có `30`/`31` = số bữa cả tháng).

Điều này **thu hẹp mạnh** câu hỏi V1 nhưng **chưa đóng nó**: mã hiển thị trên báo cáo có hậu tố số
(`L-8`, `L-10`, `TASK-REF`, `TASK-REF`, `x8-4`, `TS/2-2`) trông như **giờ**, mà chuỗi `IF` trong template lại
làm việc **cắt hậu tố** (`"x8-4"→"x8"`, `"TASK-REF"→"TS"`) — trừ một ca không nhất quán `"L-10"→"L-8"`.
Quy tắc sinh ra hậu tố đó vẫn là **quyết định nghiệp vụ**, không suy diễn.

### 14.4 Hai ràng buộc dữ liệu thật, ảnh hưởng ngay tới Task 7 và tới test

**(1) Chỉ có ĐÚNG MỘT kỳ trong `raas_monthly_attendance`: `2026-06-21 → 2026-07-20`** (kỳ 07/2026),
**3.768 nhân viên**. Toàn bộ test hiện tại đang dùng kỳ `2026-03` (theo tên sheet gốc `202603_…`) —
**Task 7 phải chuyển sang kỳ 07/2026**, nếu không sẽ đọc ra 0 dòng.

**(2) Lưới ngày chỉ phủ 227 / 3.768 nhân viên (~6%).** `ts_attendance_daily_pivot` có 1.907 dòng /
**227 nhân viên**, khoảng ngày `2026-05-21 → 2026-07-20`. Nghĩa là với dữ liệu hiện tại, **31 cột chấm
công sẽ trống cho ~94% nhân viên** trong khi các cột tổng từ `raas_monthly_attendance` thì có đủ. Đây
là câu hỏi cho đội DB: `wd_calculated_time_blocks` mới sync một phần, hay bản chất chỉ một phần nhân
viên có time block?

### 14.5 Task 7 giờ chặn bởi gì

| Trước restore | Sau restore |
|---|---|
| Docker không chạy, DB rỗng | ✅ DB có dữ liệu thật, 46 bảng + 9 view |
| Không biết tag chấm công nào tồn tại | ✅ 19 tag, có số lượng, có view pivot sẵn |
| Không rõ nguồn cho nhóm C | ✅ 9 view trả lời phần lớn |
| Bảng quy đổi tag → mã hiển thị | ⬜ **vẫn chờ nghiệp vụ** — nhưng phạm vi nhỏ hơn nhiều |
| — | ⬜ **mới:** độ phủ lưới ngày chỉ 6%; và chỉ có 1 kỳ (07/2026) |

---

## 15. Đội DB trả lời V4 — phân tích + thiết kế Task 7 (2026-07-31)

### 15.1 Bốn câu dùng được ngay

**Q1 — chiến lược ghi `raas_monthly_attendance`:** *"Phần này không implement vì Workday có cơ chế
unique được log rồi."* → **`DBSource` đọc thẳng, không cần transaction, không cần cờ "sync xong"**. Rủi
ro còn lại (đọc trúng lúc sync) được chấp nhận có ý thức; ghi lại ở đây để sau này không ai tưởng là sơ suất.

**Q2 (phần tên field) — ổn định:** *"tên trong xml không thay đổi"*, và
`wd_calculated_time_blocks.calculation_tag_reference` là cố định. → An tâm dùng JSONB path theo tên
Workday. (Phần còn lại của Q2 có vấn đề, xem §15.2.)

**Q3 — `hire_date`:** *"Trong lúc sync cũng nên flat field này ra cho postgres"* → đội DB sẽ thêm cột
`date` chuẩn hoá. Trong lúc chờ, `DBSource` **tự parse ở Go** nhưng phải viết sao cho **tự động dùng cột
`date` nếu cột đó xuất hiện** — tránh phải sửa lại khi họ làm xong.

**Q5 — danh sách công ty:** lấy từ `wd_organizations`. Đã tra đường dẫn thật:
`raw->'Organization_Data'->>'Name'`, join với `raas_monthly_attendance.company_reference_id`. Dữ liệu
thật của kỳ 07/2026:

| `company_reference_id` | Số NV | Tên |
|---|---|---|
| `CTDGROUP_0001` | 3.231 | Enterprise Construction Joint Stock Company |
| `CTDGROUP_0002` | 515 | (tra `wd_organizations`) |
| `TASK-TASK-REF` | 17 | |
| *(rỗng)* | 3 | **3 dòng không có `company_reference_id`** — cần quyết đưa vào hay bỏ |
| `TASK-TASK-REF` / `TASK-TASK-REF` | 1 / 1 | |

**Q6 — nhân viên nào vào báo cáo:** *"Lấy tất cả nhân viên trừ những người đã nghỉ trước đầu kỳ (nếu có
payback ở kỳ này cũng sẽ phải lấy ra)"* → điều kiện: `KHÔNG (ngày nghỉ việc < period_start)` **HOẶC** có
`Pay_Back` trong kỳ. Nguồn ngày nghỉ việc: `wd_workers.raw` hoặc `wd_worker_transaction_logs`; nguồn
payback: tag `Pay_Back` (2 block/2 NV) hoặc `raas_monthly_attendance.raw->Pay_Back_Days`.

### 15.2 Hai điểm cần phản hồi lại đội DB

**(A) Phản đối việc gộp `wd_calculated_time_block_tags` vào `wd_calculated_time_blocks`.**

Đội DB đề xuất: *"Anh nghĩ bảng này không cần thiết — nếu chỉ để lấy `tag_id`/`time_calculation_tag_id`
thì ghi thẳng vào `wd_calculated_time_blocks` luôn cũng được."*

Đo trên DB vừa restore: **36 / 2.990 block có ĐÚNG 2 tag** (2.954 block có 1 tag). Và tổ hợp có **nghĩa
nghiệp vụ thật**, không phải nhiễu:

| Ví dụ thật | Tổ hợp tag | Nghĩa |
|---|---|---|
| `EE26000008`, 2026-06-07, qty 1.0 | `Cash_1x` + `Off_in_Lieu_1x` | tăng ca trả **một phần tiền, một phần nghỉ bù** |
| `004351`, 2026-06-19, qty 1.0 | `Cash_1x` + `Off_in_Lieu_2x` | cùng loại, hệ số khác |

Gộp thành **một cột đơn** sẽ **mất im lặng** một trong hai tag — đúng loại dữ liệu ảnh hưởng tới tiền.
Chính migration `0004` đã ghi lý do này từ trước: *"34 of 1,882 real synced blocks carry more than one
tag (verified), so a single column would silently drop data for those rows."* Con số nay là 36/2.990 —
hiện tượng vẫn còn.

**Đề nghị:** giữ bảng con. Nếu vẫn muốn gộp để đỡ join, dùng **cột mảng `text[]`**, không dùng cột đơn.

**(B) Q4 — ba nguồn nói ba cửa sổ kỳ KHÁC NHAU. Đây là điểm chặn thật.**

| Nguồn | Cửa sổ |
|---|---|
| **Template Excel** (hardcode trong ô `A6`: `=DATE(YEAR(J6),MONTH(J6)-1,21)`) | **21 → 20** |
| **DB thật** (`raas_monthly_attendance.period_start/period_end`) | **2026-06-21 → 2026-07-20** = **21 → 20** |
| **Đội DB trả lời** | *"nên lấy **18 tháng trước → 17 tháng này**"* |

Và dữ liệu **CÓ** cho các ngày 18, 19, 20 tháng 7 (29, 60, 34 block) — nên câu *"thực tế chỉ lấy được
từ 21 tháng trước đến 17 tháng này"* là ràng buộc **VẬN HÀNH** (lúc chạy lương thì 18–20 chưa chốt),
**không phải** ràng buộc dữ liệu trong dump này.

**Hệ quả nếu chốt 18→17:** phải **sửa công thức `A6` của template**, tức đụng toàn bộ 31 cột ngày + ô
tiêu đề + cả quy tắc trong `internal/payperiod`. Đây là thay đổi hiển thị, **không tự quyết** — chờ
người dùng chốt. Trong lúc chờ, `DBSource` **đọc đúng `period_start`/`period_end` có trong DB** (21→20),
tức không phụ thuộc quyết định này.

#### ✅ ĐÃ CHỐT (người dùng, 2026-07-31): cửa sổ kỳ lương là **21 → 20**

Đề xuất 18→17 của đội DB **không áp dụng**. Hệ quả: **không sửa dòng code nào** — cả ba nguồn đã khớp,
đã xác nhận lại từng chỗ:

| Nguồn | Cửa sổ |
|---|---|
| Template, ô `A6` = `DATE(YEAR(J6),MONTH(J6)-1,21)` | 21 → 20 |
| `internal/payperiod.periodEndFor` — `t.Day() <= 20` → ngày 20 tháng này, ngược lại ngày 20 tháng sau | 21 → 20 |
| DB `raas_monthly_attendance.period_start/period_end` | `2026-06-21 → 2026-07-20` |

**Nhưng mối lo THẬT phía sau đề xuất 18→17 vẫn còn, chỉ là nó không phải chuyện cửa sổ kỳ.** Đội DB nói
*"thực tế mình chỉ lấy được khoảng từ 21 tháng trước đến 17 tháng này"* — đó là ràng buộc **thời điểm
chạy**: nếu chạy báo cáo vào ngày 18 thì dữ liệu ngày 18–20 chưa chốt. Cách xử đúng là ở **quy trình vận
hành**, không phải thu hẹp cửa sổ:

- chạy báo cáo **sau ngày 20** (dữ liệu đủ kỳ), hoặc
- nếu buộc phải chạy sớm thì **nói rõ trên báo cáo** là 3 ngày cuối chưa chốt — chứ không âm thầm cắt
  cửa sổ, vì cắt cửa sổ làm `Công chuẩn` sai theo (kỳ 18→17 có số ngày khác kỳ 21→20).

Đây là câu cần hỏi lại đội DB/C&B: **quy trình dự kiến chạy báo cáo vào ngày nào trong tháng?**

### 15.3 Thiết kế Task 7 theo DB thật — đọc VIEW, không đọc bảng thô

Điểm khác lớn nhất so với bản PLAN gốc: **không truy vấn `wd_calculated_time_blocks` +
`wd_calculated_time_block_tags` trực tiếp** mà dùng các view đội DB đã dựng (§14.2). Vừa đơn giản hơn,
vừa tránh đúng tranh chấp ở §15.2(A).

| Nguồn | Cung cấp |
|---|---|
| `raas_monthly_attendance` (3 cột số + `raw` JSONB) | 19 mã nhóm A (§3.1) |
| `wd_organizations` | `OrgStructureName`/`OrgStructureCode`, tên công ty |
| `ts_attendance_daily_pivot` | nguyên liệu cho `Workdays1..31` — **nhưng xem §15.4** |
| `ts_time_off_plan_balances_pivot` | `AddIn`, `Used`, `UsedLastYear`, `Budget2` |
| `ts_ot_reconciliation` | `OT_CN`, `OT_Ho` (**giờ**) |
| `wd_job_profiles` | `JobTitleName` |
| `wd_worker_transaction_logs` | ngày nghỉ việc (Q6), `OrgStructure1..3` (sau) |

### 15.4 `Workdays1..31` vẫn CHƯA làm được — và vì sao không nên đoán

`ts_attendance_daily_pivot` cho đúng hình dạng cần, nhưng **quy tắc quy đổi từ dòng pivot ra chuỗi mã**
(`x8-4`, `L-8`, `L-10`, `TASK-REF`, `TASK-REF`, `TS/2-2`…) vẫn chờ nghiệp vụ. Hai điểm chưa khớp:

- `calculated_quantity` tính bằng **NGÀY** (gần như chỉ `0.5`/`1.0`), còn hậu tố mã trông như **GIỜ**
  (`-8`, `-4`, `-10`, `-16`, `-2`). Nếu `1.0 ngày → 8` thì `L-10` và `TASK-REF` sinh từ đâu?
- Không có tag nào ứng với `ON` (nghỉ ốm **dưới** 30 ngày) trong pivot; và chưa rõ `Uncompensated_Day`,
  `OFF`, `DT` ứng với mã nào.

**Quyết định: Task 7 KHÔNG điền `Workdays1..31`.** Đổi lại, các cột tổng (từ
`raas_monthly_attendance`) đều có số thật, nên báo cáo vẫn dùng được để đối chiếu. Phần lưới ngày tách
thành **Task 7b**, chặn bởi câu trả lời nghiệp vụ. Đoán ở đây là tạo ra một bảng chấm công **trông đúng
mà sai** — tệ hơn để trống.

---

## 16b. Thi hành Task 7 — DBSource đọc DB thật (2026-07-31, phiên thứ 4)

Files mới: `internal/report/bangcong/{source_db.go, source_db_integration_test.go}`. Sửa nhỏ
`period.go` (thêm `ExcelSerialDate` xuất công khai, tái dùng cho `DateEmployment` — tránh lặp lại
kỹ thuật serial-number đã có ở `SetPeriod`). **45 test case / 29 hàm test — 0 fail** (từ 43 lên 45).

### 16b.1 CỔNG khác thường: bắt được vi phạm G7 không do phiên này gây ra

Trước khi chạm vào Task 7, chạy lại toàn bộ 43 test cũ để xác nhận baseline — **3 test đỏ**
(`TestRecalcAll_OnRealTemplate`, `TestRecalcAll_IncompleteRowDoesNotAbortRun`,
`TestRender_MissingStdWorkDayIsDiagnosed`), tất cả cùng triệu chứng: **Diagnostics thiếu `EK`/`EO`**
— cơ chế bắt lỗi `#DIV/0!`-dù-giá-trị-đúng (D1/A2, mục 11) không còn kích hoạt.

Truy nguyên (không đoán, không sửa test cho qua): `go.mod` đang ghi `github.com/xuri/excelize/v2
v2.11.0` — **vi phạm G7** ("giữ v2.10.0, không nâng version"). Không phải do phiên này — commit
`0bdd5de` (đồng nghiệp khác, "update api & dsoc") nằm giữa base cũ và nhánh `feature_v1` sau khi
nhánh được rebase lên `develop` mới; đâu đó trong quá trình đó `excelize` cùng 7 dependency gián
tiếp khác (`mscfb`, `msoleps`, `go-deepcopy`, `x/crypto`, `x/net`, `x/sync`, `x/text`) bị nâng version.
Excelize v2.11.0 rõ ràng đã **sửa** đúng quirk evaluator (nested `IF` short-circuit vẫn eager-eval
nhánh không chọn) mà `recalc.go` đã xây cơ chế `Diagnostics` để sống chung — hành vi tốt hơn nhưng
phá đúng bất biến 3 test đang khoá.

**Sửa:** `go get github.com/xuri/excelize/v2@v2.10.0` rồi `go mod tidy` — excelize về đúng v2.10.0,
7 dependency gián tiếp khác giữ nguyên bản mới (không quan hệ tới quirk này, không thấy ảnh hưởng
sau khi chạy lại toàn bộ suite). Xác nhận bằng thực nghiệm: xoá cache (`go clean -cache -testcache`),
build lại, **cả 3 test đỏ trở lại xanh ngay**, không đụng dòng test nào. Đây đúng tinh thần G7: một
dependency lệch version có thể âm thầm đổi hành vi runtime mà không đổi dòng code nào của mình.

### 16b.2 Task 7.1 — DBSource, 1 dòng thật (đã che tên)

Query JOIN `raas_monthly_attendance` + `wd_workers` (lấy `hire_date`/`termination_date` đã chuẩn
hoá kiểu `date`, KHÔNG cần tự parse text ở Go — xem 16b.3) + LEFT JOIN `wd_organizations` qua
**`supervisory_org_wid = wid`** (khoá có FK, không phải `supervisory_org_reference_id` như brief
mô tả — đo thật cả 2 cách đều khớp 3768/3768 dòng, chọn cách có ràng buộc khoá ngoại vì an toàn hơn).
Cột `wd_organizations.name` đã có sẵn dạng phẳng, khớp 100% với `raw->'Organization_Data'->>'Name'`
(đối chiếu toàn bộ mẫu) — dùng thẳng cột phẳng, không cần JSONB path.

**Phát hiện lớn nhất:** phần lớn field brief bảo lấy qua `raw->>'...'` (JSONB) **đã có sẵn dạng
cột phẳng đã tách kiểu `numeric(18,6)`** ngay trên `raas_monthly_attendance` (`standard_working_days`,
`actual_working_days`, `paid_holidays`, `annual_leave`, `personal_leave`,
`sick_leave_under_30_days`, `sick_leave_over_30_days`, `maternity_leave`, `paternity_leave`,
`unpaid_leave_under_30_days`, `unpaid_leave_over_30_days`, `pay_back_days`) — đối chiếu giá trị
JSONB vs cột phẳng khớp 100% trên toàn bộ mẫu kiểm. Dùng cột phẳng (an toàn kiểu, khỏi cast text→số
trong SQL); chỉ 2 mã thật sự cần JSONB: `LeaveDayNB` (`Off_in_Lieu_83246575` +
`CF_SRI_Total_Off_in_Lieu_2x...`, không có cột phẳng tương ứng).

1 dòng thật (kỳ 2026-06-21→2026-07-20, tên đã che):
```
EmployeeCode: 000023          EmployeeName: <che>              EmployeeTypeName: Regular
JobtileName: Managing Director, MEP        EmployeeLevelName: L8
DateEmployment: 37646 (serial Excel)  →  xác nhận = 2003-01-25 (khớp ĐÚNG ví dụ PLAN §3.1 đã nêu)
OrgStructureName: GLOBAL_US    OrgStructureCode: GLOBAL_US
StdWorkDay: 23   RealWorkDay: 0   LeaveDayL/F/Fo/NB/ON/OD/TS/TSN/Ro: 0   CBSTT: 0
```
20/20 mã có key (đếm theo `CoveredFieldCodes`). **Sai số đếm của brief:** brief ghi "19 mã" nhưng
liệt kê đúng 20 mã (đếm tay lại từ danh sách brief đưa) — không tự sửa số, chỉ implement đúng 20 mã
đã liệt kê.

### 16b.3 Task 7.1b — nhánh cột date chuẩn hoá

Đo thật: `raas_monthly_attendance.hire_date` **vẫn là TEXT** (`"2003-01-25-08:00"`, chưa có cột mới
như Q3 hứa) — nhưng `wd_workers.hire_date` **đã sẵn là `date`** (không liên quan gì tới lời hứa Q3,
tồn tại độc lập từ trước, migration cũ hơn). Đối chiếu: giá trị khớp nhau 1-1 (chỉ khác đuôi
`-08:00`), 0/3768 dòng NULL ở cả hai phía. Quyết định: JOIN sang `wd_workers` lấy `hire_date` kiểu
`date` thật, KHÔNG tự parse chuỗi text ở Go — vừa đơn giản, vừa đúng tinh thần "tự động dùng cột
`date` nếu có" mà brief yêu cầu (chỉ khác: cột đó nằm ở `wd_workers`, không phải
`raas_monthly_attendance` như brief giả định).

### 16b.4 Task 7.2 — kỳ, lọc Q6, company rỗng, nguồn ngày nghỉ việc

- **Kỳ có trong DB:** đúng 1, `2026-06-21 → 2026-07-20`, 3768 NV — khớp PLAN §14.4.
- **Q6 (trước/sau lọc):** đo thật trên TOÀN BỘ 3768 dòng: **0 người nghỉ việc trước đầu kỳ** (23
  người có `termination_date`, tất cả đều `>= period_start`) → lọc Q6 hiện **không loại ai** cho kỳ
  này (3768 trước = 3768 sau). Quy tắc vẫn cài đúng (loại khi `termination_date < period_start` VÀ
  `pay_back_days <= 0`) — chỉ là dữ liệu kỳ này không kích hoạt nhánh loại trừ, không phải quy tắc
  vô dụng.
- **`company_reference_id` rỗng (3 dòng):** KHÔNG lọc theo company — Q6 không nhắc company là tiêu
  chí. Soi tay: 2/3 dòng trông như dữ liệu test/sandbox Workday (`SITEE0016`, org tên "Dummy SIT...
  (Test)"), 1/3 (`EE26000061`) trông như NV thật (org "BU2_BAI DAT DO..."). Không tự loại theo suy
  đoán — cả 3 vẫn được đưa vào báo cáo, `OrgStructureName` vẫn join đúng qua `supervisory_org_wid`
  (không phụ thuộc `company_reference_id`).
- **Nguồn ngày nghỉ việc:** `wd_workers.termination_date` (đã sẵn kiểu `date`), KHÔNG cần
  `wd_worker_transaction_logs` như brief gợi ý — cột có sẵn, đơn giản hơn, cùng bảng đã JOIN cho
  7.1b.

### 16b.5 Task 7.3 — mức chắc chắn của từng mã

Cả 20/20 mã trong bảng brief đưa đều map được CHẮC CHẮN (đối chiếu giá trị JSONB vs cột phẳng, vs
mẫu thật — khớp 100%, không phát hiện mã nào mơ hồ trong phạm vi 20 mã này). Không mã nào bị BỎ.
`Meal1..3` (có trong PLAN §3.1 nhưng KHÔNG có trong bảng 20 mã của brief này) — không implement,
đúng phạm vi brief đưa, không tự thêm.

### 16b.6 Task 7.4 — CoveredFieldCodes

**Brief bị cắt/hỏng ở đúng đoạn mô tả Task 7.4** (nội dung dán vào bị đứt giữa chừng, nhảy thẳng
sang Task 7.5) — chỉ còn lại 1 câu cuối: *"Rụng nguồn → test đỏ ngay thay vì báo cáo âm thầm ra 0."*
Đã tự suy ra thiết kế từ câu này + tinh thần G2 xuyên suốt PLAN, KHÔNG bịa thêm ngoài đó: biến xuất
`CoveredFieldCodes []string` liệt kê đúng 20 mã `DBSource` phủ, dùng trong
`TestDBSource_RealDatabase` để đếm coverage thật trên dữ liệu trả về — 4 mã cốt lõi
(`EmployeeCode/EmployeeName/OrgStructureName/StdWorkDay`) bắt buộc 100% (3768/3768), các mã còn lại
chỉ cần >0 (một số NV thật thiếu `EmployeeLevelName`/`EmployeeTypeName` do JSONB gốc rỗng — hợp lệ,
không phải lỗi). Nếu nguồn rụng (JOIN gãy, đổi tên cột) mà mọi dòng chỉ còn `EmployeeCode` thì test
này đỏ ngay thay vì "0 lỗi, có dòng trả về" trông như thành công. **Đây là phần brief mô tả không
đầy đủ nhất — nếu ý định thật khác, cần nói rõ để sửa lại.**

### 16b.7 Task 7.5 — kiểm tồn tại view: phát hiện tiền đề đã LỖI THỜI

**Đính chính PLAN §14.2/§14.5:** hai mục đó (viết cùng ngày, trước Task 7 vài giờ) khẳng định "9
view + 2 bảng chỉ tồn tại trong dump, không migration nào trong repo tạo ra". Đọc lại
`internal/db/migrations/` ngay trước khi code: **SAI, đã lỗi thời** — cả 9 view lẫn 2 bảng đều ĐÃ có
migration thật (`0007`,`0017`,`0018`,`0020`,`0022`,`0030`,`0031`,`0035`), nằm trên `develop`, commit
`a49095b`. Đối chiếu `schema_migrations` của DB thật: đúng 36/36 file khớp tên — một máy dựng DB từ
migration bây giờ SẼ có đủ 9 view, không còn thiếu như PLAN mô tả. Ai đó đã đóng gap này giữa lúc
viết §14 và lúc thi hành Task 7 (không phải do phiên này).

Vẫn cài cơ chế `requiredViews` + kiểm `to_regclass` trong `NewDBSource` đúng như brief yêu cầu —
NHƯNG danh sách hiện **rỗng**, vì 20 mã Task 7.1 KHÔNG đụng view nào (chỉ dùng
`raas_monthly_attendance`/`wd_workers`/`wd_organizations`, cả ba đều có migration từ lâu). Cơ chế
để sẵn cho Task 7b (sẽ cần `ts_attendance_daily_pivot`) — hiện là phòng thủ thêm, không phải vá một
lỗ hổng đang mở.

### 16b.8 Việc còn nợ

- Task 7b (`Workdays1..31`) vẫn chặn bởi quyết định nghiệp vụ chưa ai chốt (PLAN §15.4) — không
  đụng, đúng phạm vi.
- Cửa sổ kỳ 21→20 vs 18→17 (PLAN §15.2B) vẫn chờ người dùng chốt — `DBSource` đọc đúng
  `period_start`/`period_end` có trong DB (21→20), không phụ thuộc quyết định này.
- **7 dependency gián tiếp khác vẫn ở bản mới** sau khi hạ `excelize` về v2.10.0 (`mscfb`, `msoleps`,
  `go-deepcopy`, `x/crypto`, `x/net`, `x/sync`, `x/text`) — không thấy ảnh hưởng sau khi chạy lại
  toàn bộ 45 test, nhưng chưa hạ về đúng bản gốc vì `go mod tidy` không tự làm vậy (do phần khác của
  repo/`go.sum` đã khoá phiên bản mới hơn cho các gói này qua đường phụ thuộc khác) — cần đội phụ
  trách repo xem lại nếu muốn khôi phục nguyên trạng go.sum hoàn toàn.
- Task 7.4 (`CoveredFieldCodes`) triển khai dựa trên suy luận từ 1 câu brief còn sót lại — cần xác
  nhận lại ý định thật.
- Chưa mở file bằng Excel/LibreOffice thật bằng mắt với dữ liệu DB thật.
- Chưa commit.

---

## 16c. Kiểm chứng độc lập Task 7 (phiên chủ, 2026-07-31)

`go build`, `go vet`, `gofmt` sạch. Đã tự chạy lại mọi con số dưới đây.

### 16c.1 Ba chỗ báo cáo thi hành ghi khác thực tế

**1. "45/45 pass" chỉ đúng khi có `DATABASE_URL`.** Hai test `TestDBSource_RealDatabase` và
`TestDBSource_ViewCheckFailsLoudly` **gate bằng `os.Getenv("DATABASE_URL")` + `t.Skip`** → `go test ./...`
bình thường **bỏ qua im lặng**; tôi đo được **43**, không phải 45 (chạy lại với `DATABASE_URL` thì 2 test
đó pass thật). Hệ quả đáng lo: **hàng rào coverage mã field của Task 7.4 — dựng riêng để bắt DB đổi cấu
trúc — KHÔNG chạy trong lần test mặc định.** Gate integration test theo env là hợp lệ, nhưng cần (a) CI
set `DATABASE_URL`, hoặc (b) thêm một test **không cần DB** khẳng định `CoveredFieldCodes` ⊆ `FieldMap`
đọc từ template.

**2. Số người có `termination_date`: 18, không phải 23.** Kết luận cuối vẫn đúng (**0 người bị loại** —
không ai có `termination_date < period_start`), chỉ con số trung gian sai.

**3. `period.go` bị sửa mà báo cáo không nhắc.** Diff +11/−1: tách `ExcelSerialDate(t)` thành hàm công
khai, kèm lý do đo được — *truyền `time.Time` vào `SetCellValue` sẽ âm thầm ghi đè style của ô bằng style
ngày mặc định của excelize*. **Thay đổi ĐÚNG**, và chính là lý do `DateEmployment` ghi serial `37646` chứ
không ghi date: để giữ format `mm-dd-yy` của template. Chỉ thiếu trong báo cáo.

### 16c.2 Ba chỗ phiên thi hành ĐÚNG mà brief của tôi SAI

- **"19 mã" → thật là 20.** Brief tôi ghi 19 nhưng liệt kê 20 dòng (`OrgStructureName` và
  `OrgStructureCode` bị gộp một dòng trong tài liệu bàn giao). Đúng là **20**.
- **Tiền đề "9 view chưa có migration" (§14.2/§14.5) ĐÃ LỖI THỜI.** Lúc tôi khảo sát repo có 29 migration
  (tới `0029`); nay đã có tới **`0036`** — gồm `0030_attendance_daily_pivot.sql`,
  `0035_worker_organization_change_diff.sql`, `0036_monthly_attendance_flatten.sql`. Rủi ro "máy khác
  restore từ migration sẽ thiếu view" **không còn**. §14.2/§14.5 giữ làm lịch sử, đọc kèm đính chính này.
- **Nguồn ngày vào làm / nghỉ việc:** brief tôi chỉ sang `wd_worker_transaction_logs`; thật ra `wd_workers`
  **đã có `hire_date date` và `termination_date date`** — đơn giản hơn, cùng bảng đã JOIN. Chọn đúng.

### 16c.3 `0036_monthly_attendance_flatten.sql` xử luôn cạm bẫy tôi cảnh báo

`0036` đã **flatten toàn bộ field JSONB thành cột thật** (`raas_monthly_attendance` nay **42 cột**):
`annual_leave`, `personal_leave`, `sick_leave_under_30_days`, `sick_leave_over_30_days`,
`unpaid_leave_under_30_days`, `unpaid_leave_over_30_days`, `maternity_leave`, `paternity_leave`,
`pay_back_days`, `sunday_meal`, `night_meal`, `cash_1x/2x/3x`, `total_paid_days`… và **DB đã restore CÓ
đủ**. Nghĩa là cạm bẫy `Sick_Leave___30_Days_` vs `Sick_Leave_____30_Days_` (khác số dấu gạch dưới) **đã
được xử ở tầng DB** — nay tên rõ ràng `_under_30_days` / `_over_30_days`.

`OrgStructureName` trả `GLOBAL_US` **không phải join lỗi**: join phủ **3768/3768**, và
`wd_organizations.raw->'Organization_Data'->>'Name'` của org đó **đúng là chuỗi `"GLOBAL_US"`**.

### 16c.4 PHÁT HIỆN NẶNG NHẤT — dữ liệu chấm công gần như trống, không ai nêu

Kỳ `2026-06-21 → 2026-07-20`:

| Chỉ số | Số dòng | % |
|---|---|---|
| Tổng dòng trong kỳ | 3.768 | 100% |
| `standard_working_days > 0` | 3.713 | 98,5% |
| **`actual_working_days > 0`** | **26** | **0,7%** |
| `total_paid_days > 0` | 88 | 2,3% |

Theo công ty: `CTDGROUP_0001` 22/3.231 · `CTDGROUP_0002` 4/515 · ba công ty còn lại **0**. Cả **26 người
đó đều nằm trong `ts_attendance_daily_pivot`** — tập 227 NV của pivot bao trùm đúng nhóm có dữ liệu thật.

**Kết luận: bản thân report Workday `raas_monthly_attendance` cũng gần như KHÔNG có dữ liệu chấm công** —
không chỉ riêng lưới ngày như §14.4 tưởng. Đây có vẻ là **sync thử nghiệm trên nhóm nhỏ**.

**Hậu quả nếu xuất báo cáo bây giờ:** ~3.742/3.768 nhân viên hiện **"Công chuẩn 24, Ngày công 0"**, và
**mọi cột tổng dẫn xuất (`AS`, `BI`, `BJ`…) tính từ những số 0 đó rồi ra con số trông hợp lệ** — đúng **F2**
(§11.8) nhưng ở quy mô **toàn bộ báo cáo**. Câu hỏi này phải gửi lại đội DB, và nó **quan trọng hơn** câu
"vì sao pivot chỉ phủ 6%".

### 16c.5 excelize — G7 cần xét lại, không pin lại máy móc

`go.mod` ở **HEAD (`93c066a`)** là **v2.11.0** (commit trước `0bdd5de` đã có v2.11.0 dạng `// indirect`),
do nhánh rebase lên `develop` mới. Phiên thi hành hạ về **v2.10.0** theo **G7** — nhưng **chỉ trong working
tree, chưa commit**, nên **ai build từ HEAD vẫn nhận v2.11.0**.

Quan trọng hơn: theo báo cáo, **v2.11.0 đã sửa đúng quirk `#DIV/0!`-kèm-giá-trị-đúng** mà `Diagnostics`
(§11.2) được xây để sống chung. Hạ version để giữ workaround cho một bug đã sửa là đi ngược. Ba dữ kiện
xung đột: `Core System-backend` production **v2.10.0** (lý do gốc của G7) · adapter HEAD **v2.11.0** · v2.11.0
**sửa** quirk mà 3 test đang encode.

**Cần quyết định, không tự chọn:** (a) nâng adapter lên v2.11.0, sửa 3 test + xem lại `Diagnostics`;
(b) giữ v2.10.0 nhưng **commit** go.mod để HEAD khớp; (c) nâng cả hai repo.

### 16c.5b PHÁT HIỆN MỚI — `ts_attendance_daily_pivot` cộng trùng, lệch với cột tổng ở 6/26 NV

Đo thêm khi rà việc còn lại. Đối chiếu `sum(pivot.actual_working_day)` trong kỳ với
`raas_monthly_attendance.actual_working_days` cho **26 nhân viên có dữ liệu thật**: **20 khớp, 6 lệch**.

Ví dụ lệch:

| `employee_id` | `raas.actual_working_days` | `sum(pivot.actual_working_day)` |
|---|---|---|
| `002551` | 1,0 | **4,5** |
| `004351` | 8,5 | **31,5** |

Nguyên nhân: **`wd_calculated_time_blocks` có nhiều block cho cùng một (nhân viên, ngày)** —
**520 / 1.907 cặp (27%)** có hơn 1 block, cao nhất **32 block** cho một cặp; tổng 1.603 / 2.990 block
nằm trong các cặp trùng. Ví dụ cụ thể đã thấy: `004351` ngày `2026-06-19` có **3 block khác WID nhưng
giống hệt nhau** (cùng `calculated_quantity = 1.0`, cùng tổ hợp tag `Cash_1x + Off_in_Lieu_2x`).

`ts_attendance_daily_pivot` **cộng dồn** các block đó, nên với 27% ô ngày thì con số nó cho **không khớp**
số tổng mà Workday tự tính. Chưa kết luận được là **sync trùng** hay **Workday cấp nhiều block hợp lệ** —
cần đội DB xác nhận.

**Hệ quả cho Task 7b:** đây là việc phải làm **TRƯỚC** khi dựng lưới ngày. Nếu lấy pivot làm nguồn mà
không xử trùng thì lưới 31 ngày sai ngay từ gốc — và sai theo kiểu **cộng thừa**, tức ô có giá trị trông
hợp lệ. Nó cũng làm câu hỏi "quy tắc quy đổi tag → mã" khó trả lời hơn: không rõ 3 block giống nhau
trong một ngày nên ra một mã hay ba.

### 16c.5c A1 — ĐIỀU TRA block trùng: ĐÃ KẾT LUẬN, có bằng chứng, KHÔNG phải "cần đội DB" (2026-08-01)

**Kết luận: KHÔNG phải trùng, KHÔNG phải cộng sai cách — là chưa lọc bản ghi Workday tự đánh dấu đã
xoá.** Mỗi block mang sẵn `raw->'Calculated_Time_Block_Data'->>'Is_Deleted'` (`"0"` hoặc `"1"`,
Workday tự gắn khi gửi bản sửa/thay thế một block cũ). Lọc `Is_Deleted <> '1'` rồi `SUM
calculated_quantity` theo tag `Actual_Working_Day` khớp **26/26** nhân viên có dữ liệu thật với
`raas_monthly_attendance.actual_working_days` — **tuyệt đối, không sai số nào**. Bằng chứng cụ thể
(002551, 2026-06-24): 3 block cùng tag `Actual_Working_Day`, 1 block `Is_Deleted="0"`
(`Status_Reference=APPROVED`, `Worker_Time_Block_ID=WORKER_TIME_BLOCK-6-5638`), 2 block
`Is_Deleted="1"` (`Status_Reference=NEVER_SUBMITTED`) — 3 `Worker_Time_Block_Reference` KHÁC NHAU
(không phải cùng 1 block chèn lặp), tức Workday gửi 3 phiên bản lịch sử của cùng 1 ngày công, chỉ 1
phiên bản còn hiệu lực.

| Giả thuyết | Kết luận | Bằng chứng |
|---|---|---|
| H1 — sync trùng | **Đúng một phần, chính xác hơn brief mô tả** — không phải "chèn lặp bản ghi giống hệt", mà là **giữ lại các bản ghi lịch sử đã bị Workday đánh dấu `Is_Deleted="1"`** thay vì lọc bỏ | 120/290 block `Actual_Working_Day` trong kỳ có `Is_Deleted="1"`; các bản ghi khác `Worker_Time_Block_ID`/`Status_Reference`, không phải bản sao byte-for-byte |
| H2 — Workday cấp nhiều block hợp lệ | **Bác bỏ** — nếu đúng thì SUM tất cả (kể cả `Is_Deleted="1"`) đã phải khớp `raas`, nhưng chỉ khớp khi LOẠI `Is_Deleted="1"` | so khớp 26/26 chỉ đạt sau khi lọc |
| H3 — cộng sai cách (nên COUNT(DISTINCT date) thay vì SUM) | **Bác bỏ dứt khoát** — `SUM` thô (không lọc) đã khớp nhiều hơn `COUNT(DISTINCT date)` (20/26 so với 19/26); và `COUNT` không bao giờ khớp được các giá trị lẻ 0.5 (vd `003964`=20,5). `SUM` **có lọc `Is_Deleted`** khớp 26/26 — đúng là `SUM`, chỉ thiếu điều kiện lọc | bảng so sánh 3 cách tính trên 26 NV, xem file test/query đã chạy |
| H4 — 6 NV lệch = 6 NV có cặp trùng | **Không chính xác như phát biểu** — nhiều NV khác cũng có cặp trùng (`005769` 32 cặp, `006636` 24 cặp…) nhưng SUM vẫn khớp, vì trùng của họ rơi vào tag KHÁC `Actual_Working_Day`. Ngược lại `007337`/`101699` lệch nhưng KHÔNG hề có block trùng cho `Actual_Working_Day` — lệch của 2 NV này chỉ biến mất khi lọc `Is_Deleted`, chứng tỏ cả 2 NV này VẪN có block `Is_Deleted="1"` lẫn trong dữ liệu dù không "trùng cặp ngày" theo nghĩa >1 dòng cùng ngày ở mọi tag | đối chiếu tập "NV lệch SUM thô" vs tập "NV có cặp (NV,ngày) trùng bất kỳ tag" — không trùng khớp tập hợp |

**Đề xuất gửi đội DB:** thêm điều kiện `WHERE (raw->'Calculated_Time_Block_Data'->>'Is_Deleted')
IS DISTINCT FROM '1'` vào định nghĩa `ts_attendance_daily`/`ts_attendance_daily_pivot` (và bất kỳ
truy vấn Task 7b nào đọc thẳng `wd_calculated_time_blocks`). Đây là sửa ở tầng VIEW/query, không
phải sửa dữ liệu đã sync — dữ liệu lịch sử (`Is_Deleted="1"`) vẫn nên giữ lại trong bảng gốc (có thể
hữu ích cho audit), chỉ cần loại khi TỔNG HỢP.

**Ảnh hưởng Task 7 (đã code, đã commit):** KHÔNG cần sửa gì. `DBSource` (source_db.go) không đọc
`wd_calculated_time_blocks`/`wd_calculated_time_block_tags`/`ts_attendance_daily_pivot` ở bất kỳ đâu
— toàn bộ dữ liệu Task 7.1 lấy thẳng từ cột đã có sẵn trên `raas_monthly_attendance` (nguồn ĐÃ đúng,
độc lập với lỗi `Is_Deleted` này). Phát hiện này chỉ ảnh hưởng Task 7b (chưa code).

### 16c.6 Việc còn lại

| Hạng mục | Trạng thái |
|---|---|
| Task 7.1–7.5 | ✅ xong |
| **Task 7b** — `Workdays1..31` | ⬜ chặn bởi quy tắc quy đổi tag → mã (nghiệp vụ) |
| Cửa sổ kỳ | ✅ **CHỐT 21→20** (2026-07-31) — không sửa code, ba nguồn đã khớp; xem §15.2 B |
| **Dữ liệu chấm công chỉ 0,7%** | ⬜ **mới — chờ đội DB giải thích (§16c.4)** |
| Hàng rào coverage không chạy mặc định | ⬜ CI set `DATABASE_URL`, hoặc thêm test không cần DB |
| excelize v2.10.0 vs v2.11.0 | ⬜ chờ quyết (§16c.5); go.mod chưa commit |
| Ngoại lệ payback của Q6 | ⚠️ **chưa được dữ liệu kiểm** — `pay_back_days > 0` có **0 dòng** trong kỳ |
| `EmployeeLevelName` / `EmployeeTypeName` | ⚠️ thiếu ở 5 / 12 dòng (thực tế dữ liệu, không phải lỗi code) |
| Task 8, 9 | ⬜ chưa |
| Mở Excel thật bằng mắt | ⬜ chưa bao giờ làm |
| **Trạng thái git** | Task 0–6 **ĐÃ COMMIT** (`93c066a`) trên nhánh **`feature_v1`** (không phải `develop` như brief ghi); Task 7 chưa commit |

---

## 17. Kế hoạch việc còn đọng làm được ở local — A1 → A2 → A3 → A5 (2026-07-31)

Thứ tự cố ý: **A1 trước** vì nó là thứ duy nhất đang âm thầm làm sai một task chưa bắt đầu; **A2** thứ
hai vì rẻ và là món nợ duy nhất chưa ai từng trả (mọi bằng chứng đến giờ là số từ script, **chưa ai
NHÌN file**); **A3** thứ ba vì hàng rào không chạy thì coi như không có; **A5** cuối vì nó là tính năng,
không phải rủi ro.

### A1 — Điều tra block trùng theo (nhân viên, ngày) — ĐIỀU TRA, KHÔNG SỬA

Dữ kiện đã đo (§16c.5b): **520/1.907 cặp (NV, ngày) có >1 block** (27%), cao nhất **32 block** một cặp;
`sum(pivot.actual_working_day)` lệch `raas.actual_working_days` ở **6/26** nhân viên có dữ liệu thật.

Đây là **điều tra**, sản phẩm là **kết luận + bằng chứng**, không phải code. Tuyệt đối không tự cài quy
tắc chống trùng rồi coi như xong — chọn sai quy tắc là sai tiền, và chưa biết trùng là lỗi sync hay là
dữ liệu hợp lệ.

Bốn giả thuyết cần bác/xác nhận, mỗi cái có phép kiểm riêng:

| Giả thuyết | Cách kiểm |
|---|---|
| H1 — **sync trùng**: các block giống nhau hoàn toàn trừ `wid` | so `raw` (bỏ `wid`) giữa các block cùng (NV, ngày); xem `first_synced_at`/`last_synced_at` có lệch |
| H2 — **Workday cấp nhiều block hợp lệ** (vd sáng/chiều, nhiều tag) | xem các block cùng cặp có khác `calculated_quantity` hoặc khác tổ hợp tag không |
| H3 — **cách cộng đúng không phải `SUM`** mà là `COUNT(DISTINCT date)` hoặc `MAX` | với 26 NV có dữ liệu, thử cả 3 cách cộng rồi so với `raas.actual_working_days`, xem cách nào khớp 26/26 |
| H4 — 6 NV lệch **chính là** nhóm có cặp trùng | giao tập "NV lệch" với tập "NV có cặp trùng" |

H3 là giả thuyết đáng thử nhất: nếu `COUNT(DISTINCT calculated_date)` khớp 26/26 thì bài toán không phải
"chống trùng" mà là "cộng sai cách", và pivot của đội DB cần sửa chứ không phải ta.

**Sản phẩm:** một mục mới trong file này, gồm bảng kết quả từng giả thuyết, kết luận, và **đề xuất gửi
đội DB**. Nếu không kết luận được thì nói rõ "không kết luận được, cần đội DB" — đó cũng là kết quả hợp lệ.

### A2 — Mở file thật bằng mắt (nợ từ Task 1)

Đến giờ **chưa ai nhìn file** — toàn bộ bằng chứng là số do script đọc ra. Layout vỡ, chữ tràn, cột dồn,
merge lệch đều là loại lỗi mà script không thấy.

Các bước: sinh file từ `DBSource` trên DB thật (kỳ `2026-06-21 → 2026-07-20`), **giới hạn ~20 dòng** cho
dễ xem và tránh vấn đề hiệu năng ở A5; rồi render ra ảnh để đọc được:

```
soffice --headless --convert-to pdf --outdir <dir> <file>.xlsx
```

rồi xem PDF. Kiểm bằng mắt tối thiểu 8 điểm: tiêu đề `"BẢNG CHẤM CÔNG CỦA CBNV THÁNG 7/2026"` ·
header 2 tầng dòng 8–9 không lệch merge · lưới 31 ngày đúng 21/06→20/07 · cột ẩn vẫn ẩn · định dạng
tiền/ngày đúng · chiều cao dòng 10–11 không cắt chữ · `STT` chạy 1..n · dòng footer `SUBTOTAL` ở đúng chỗ.

**Cũng ghi lại điều đã biết trước** để không bị bất ngờ: `Ngày công = 0` cho gần hết nhân viên (§16c.4)
và 31 cột chấm công trống (Task 7b chưa làm). Hai điều đó **không phải lỗi layout**.

Lưu ý: người dùng vẫn nên tự mở bằng Excel thật — LibreOffice không phải Excel, và một số khác biệt
render chỉ Excel mới lộ.

### A3 — Đóng lỗ hàng rào coverage

Vấn đề (§16c.1): hai test tích hợp gate bằng `os.Getenv("DATABASE_URL")` + `t.Skip`, nên
`go test ./...` **bỏ qua im lặng** — hàng rào coverage mã field, thứ dựng riêng để bắt DB đổi cấu trúc,
không chạy trong lần test mặc định.

Hai việc:
1. Thêm test **không cần DB**: `CoveredFieldCodes` phải là tập con của `FieldMap` đọc từ template, có
   **đúng 20** phần tử, không rỗng, không trùng. Test này chạy mọi lúc.
2. Ghi rõ ở `TESTING.md` (hoặc README của package) rằng test tích hợp cần `DATABASE_URL`, và CI phải set
   nó — nếu không thì nói thẳng là CI hiện không phủ nhóm test đó.

### A5 — Task 8: CLI + route HTTP

`adapter report --period 2026-07 --out bangcong.xlsx` và `GET /reports/bangcong?period=YYYY-MM`.

**Cổng hiệu năng — phải đo trước khi coi là xong.** `RecalcAll` hiện mất ~5 giây cho **3 dòng** dữ liệu
(`TestRecalcAll_OnRealTemplate` 5,30s; acceptance 9,45s). Kỳ thật có **3.768 dòng**. Nếu chi phí tuyến
tính thì đã là hàng giờ; nếu siêu tuyến tính thì không chạy nổi. Phải đo ở 20 / 200 / 1.000 dòng, vẽ ra
xu hướng, rồi quyết:
- nếu chấp nhận được: giữ nguyên;
- nếu không: thêm `--limit`, hoặc **bỏ `RecalcAll` cho file lớn** và chỉ dựa `FullCalcOnLoad` (Excel tự
  tính khi mở) — đánh đổi: công cụ đọc bằng code sẽ thấy ô công thức rỗng (§11.8/D2).

**Không tự chọn** đánh đổi này — đo, báo số, rồi hỏi.

---

## 18. Thi hành A1 → A2 (2026-08-01, phiên thứ 5)

Trước khi bắt đầu: xác nhận `Task 7b` **CHƯA có dòng code nào** (`grep Workdays` chỉ ra 4 dòng ở
`mapping.go` — chuẩn hoá mã hỏng, thuộc Task 6 — và 2 dòng comment ở `source_db.go` nói rõ CHƯA làm).
Vậy A1 không có code Task 7b nào để "phân tích kĩ trước khi thay đổi" — điều tra ở dưới không đụng
gì tới `DBSource` (đã commit, `555840c`).

### 19.1 A1 — Điều tra block trùng: KẾT LUẬN DỨT KHOÁT (không phải "cần đội DB"), 26/26

**Kết luận: không phải trùng, không phải cộng sai cách — là CHƯA LỌC bản ghi Workday tự đánh dấu
`Is_Deleted="1"`.** Mỗi block Workday mang `raw->'Calculated_Time_Block_Data'->>'Is_Deleted'`
(`"0"`=còn hiệu lực, `"1"`=đã bị thay thế bởi bản sửa mới hơn). Lọc `Is_Deleted <> '1'` rồi
`SUM(calculated_quantity)` theo tag `Actual_Working_Day` khớp **26/26** nhân viên có dữ liệu thật
với `raas_monthly_attendance.actual_working_days` — **tuyệt đối, 0 sai số**.

Bằng chứng cụ thể (`002551`, `2026-06-24`): 3 block cùng tag `Actual_Working_Day`, 3
`Worker_Time_Block_Reference` KHÁC NHAU (không phải chèn lặp cùng 1 bản ghi) — 1 block
`Is_Deleted="0"` (`Status_Reference=APPROVED`), 2 block `Is_Deleted="1"`
(`Status_Reference=NEVER_SUBMITTED`). Tức Workday gửi 3 phiên bản lịch sử của cùng một ngày công,
chỉ 1 phiên bản còn hiệu lực — sync giữ lại cả 3.

| Giả thuyết | Kết luận |
|---|---|
| H1 sync trùng | Đúng một phần, chính xác hơn mô tả — không phải chèn lặp bản ghi giống hệt, mà giữ lại các bản ghi lịch sử `Is_Deleted="1"` thay vì lọc bỏ |
| H2 Workday cấp nhiều block hợp lệ | Bác bỏ — SUM không lọc gì cũng không khớp `raas`; chỉ khớp khi loại `Is_Deleted="1"` |
| H3 cộng sai cách (nên `COUNT(DISTINCT date)`) | Bác bỏ dứt khoát — `SUM` thô đã khớp NHIỀU HƠN `COUNT` (20/26 so với 19/26); `COUNT` không bao giờ khớp giá trị lẻ 0,5 (vd `003964`=20,5). `SUM` có lọc `Is_Deleted` khớp 26/26 |
| H4 6 NV lệch = 6 NV có cặp trùng | Không chính xác như phát biểu — nhiều NV khác cũng có cặp trùng (`005769` 32 cặp) nhưng SUM vẫn khớp (trùng rơi vào tag khác); ngược lại `007337`/`101699` lệch dù không có block trùng cho `Actual_Working_Day` — vẫn dính `Is_Deleted="1"` |

**Đề xuất gửi đội DB:** thêm `WHERE (raw->'Calculated_Time_Block_Data'->>'Is_Deleted') IS DISTINCT
FROM '1'` vào định nghĩa `ts_attendance_daily`/`ts_attendance_daily_pivot`. Sửa ở tầng VIEW, không
sửa dữ liệu đã sync. Chi tiết đầy đủ + bảng SQL đã chạy: mục 16c.5c.

**Ảnh hưởng Task 7 đã code:** không cần sửa gì — `DBSource` không đọc `wd_calculated_time_blocks`.

### 19.2 A2 — Mở file thật bằng mắt: PHÁT HIỆN NẶNG, KHÔNG PHẢI CHUYỆN NHỎ

File sinh: `DBSource`, kỳ `2026-06-21→2026-07-20`, giới hạn 20 dòng. Giữ lại cả 2 file (đường dẫn ở
cuối mục này).

| # | Điểm kiểm | Kết quả | Mô tả |
|---|---|---|---|
| 1 | Tiêu đề | ❌ **LỆCH NẶNG** | `A2` hiện `"BẢNG CHẤM CÔNG CỦA CBNV THÁNG  3/2026"` — SAI, phải là `THÁNG 7/2026`. Xem §19.3 — cùng gốc với #3 |
| 2 | Header 2 tầng dòng 8-9 (cột định danh) | ✅ ĐẠT | Merge đúng, không lệch, xem trang 1 PDF |
| 3 | Lưới 31 ngày | ❌ **LỆCH NẶNG** | Dòng 6 (ẩn) và dòng 8 (hiện, hiển thị số thứ tự ngày) đúng ở 2 cột đầu (`M`,`N`) rồi **NHẢY VỀ dữ liệu cache CŨ của kỳ 03/2026** từ cột `O` trở đi — dòng 8 hiện `1,2,9,10,11,12,13,14…` thay vì `1,2,3,4,5,6,7,8…`. Xem §19.3 |
| 4 | Cột ẩn (`AO,BL,BN,BU,BY,DG,DS`) | ✅ ĐẠT | Kiểm bằng script (`openpyxl`, không chỉ nhìn PDF — cột ẩn thì PDF vốn không in ra): cả 7 cột `hidden=True` |
| 5 | Định dạng tiền/ngày | ❌ **LỆCH** | `DateEmployment` (cột K) đúng kiểu `date` (`dd/mm/yyyy`), giá trị đúng (`2003-01-25` khớp NV mẫu đã biết) — nhưng **cột K không có độ rộng riêng** (`width=None`, dùng mặc định), không đủ chỗ hiển thị `dd/mm/yyyy` → Excel/LibreOffice hiện `###` thay vì ngày. Thấy trực tiếp trên PDF (cột toàn `###`) |
| 6 | Chiều cao dòng 10-11 | ✅ ĐẠT | Chữ hướng dẫn (dòng 11, chữ đỏ) hiện đầy đủ, không bị cắt |
| 7 | STT chạy 1..n | ⚠️ **QUAN SÁT** | STT nhân viên thật chạy đúng `1..20`. NHƯNG dòng mầm (12) — vẫn hiện diện, giữ nguyên tại chỗ theo đúng thiết kế G5 — hiện `STT=1` giống hệt dòng nhân viên đầu tiên ngay bên dưới (cũng `=1`). Nhìn như 2 dòng trùng STT. Đây là hệ quả TẤT YẾU của quyết định "giữ dòng mầm tại chỗ", không phải lỗi mới, nhưng CHỈ THẤY ĐƯỢC KHI NHÌN FILE THẬT |
| 8 | Footer SUBTOTAL đúng chỗ | ✅ ĐẠT | Dòng 33 (=12+20+1), `JB33=SUBTOTAL(3,JB2:JB32)` có giá trị cache thật (`25`) |

**Đã biết trước, không phải lỗi (đúng như brief lường):** ngày công = 0 cho ~19/20 dòng mẫu (dữ liệu
Workday thật gần như trống, xem 16c.4); 31 cột chấm công trống (Task 7b chưa làm).

### 19.3 NGUYÊN NHÂN #1 và #3 — lỗi MỚI trong `RecalcAll`, SÂU HƠN D1, D1's test KHÔNG bắt được

**Đây là phát hiện quan trọng nhất của A2.** Không phải lỗi hiển thị/layout đơn thuần — là lỗi
ĐÚNG giá trị công thức bị hỏng do `RecalcAll` (Task 7 era, `recalc.go`), và **bài test hồi quy của D1
(`TestRecalcAll_PreservesSharedFormulaGroups`) không bắt được** vì nó chỉ đếm SỐ LƯỢNG công thức mỗi
dòng, không kiểm GIÁ TRỊ.

**Cơ chế (đã truy đến gốc, xác nhận bằng đọc giá trị thật, không đoán):**

1. `RecalcAll` hiện chạy 2 lượt: Lượt 1 đọc TOÀN BỘ công thức vào bộ nhớ; Lượt 2, VỚI TỪNG Ô, gọi
   `CalcCellValue` (đọc CÔNG THỨC SỐNG hiện tại của sheet — KHÔNG dùng chuỗi đã chụp ở lượt 1) rồi
   `SetCellFloat` + `SetCellFormula` NGAY LẬP TỨC cho ô đó, trước khi sang ô tiếp theo.
2. Dòng 6 có nhóm shared formula: ô CHỦ `N6` (công thức `M6+1`), thành viên `O6..AQ6` (31 ô, "" thân
   rỗng, dựa vào chủ). Khi Lượt 2 xử `N6`: `CalcCellValue(N6)` ĐÚNG (46195) — nhưng `SetCellFloat(N6,
   ...)` xoá NGAY bộ nhớ trong của excelize cho CẢ NHÓM (đã ghi nhận hiện tượng này ở finding (3) của
   `recalc.go`, nhưng CHỈ nghĩ tới việc mất CÔNG THỨC — chưa nghĩ tới việc này làm SAI GIÁ TRỊ).
3. Lượt 2 sang `O6`: `CalcCellValue(O6)` gọi vào lúc `O6` **đã mất công thức** (bị xoá ở bước 2) →
   rơi vào nhánh `cellResolver` (đọc VALUE THÔ, không tính công thức) → trả về **giá trị cache CŨ
   của chính template gốc** (kỳ 03/2026 khi file còn tên `202603_...`) — SAI, nhưng KHÔNG lỗi (không
   throw). `SetCellFloat(O6, <giá trị sai>)` ghi số sai vào cache; `SetCellFormula(O6, "N6+1")` (lấy
   từ snapshot Lượt 1) khôi phục ĐÚNG công thức — nên **đếm công thức vẫn đúng, giá trị thì sai**.
4. Dòng 9 (`=DAY(M6)`, `=DAY(N6)`...) được xử SAU dòng 6 trong vòng lặp (Lượt 2 đi theo thứ tự dòng
   1→lastRow) — lúc `CalcCellValue(O9)` chạy, `O6` ĐÃ được khôi phục công thức (bước 3) nên
   `DAY(O6)` tính lại ĐÚNG từ đầu — giải thích vì sao dòng 9 (hiện `21,22,23...`) đúng trong khi dòng
   6 và dòng 8 (cùng nhóm bị đầu độc, xử TRƯỚC dòng 9) sai.

**Kiểm chứng bằng số liệu thật (không suy diễn):** giá trị sai của `O6` là serial `46076` = **đúng
2026-02-23** — không phải số ngẫu nhiên, mà là NGÀY CACHE GỐC của chính template khi còn là báo cáo
tháng 03/2026 (dải kỳ 23/02→23/03 xấp xỉ đúng cửa sổ 21→20 của tháng 3). Xác nhận: lỗi này là
"đọc lại cache cũ chưa từng được làm mới", không phải một phép tính mới sai.

**Vì sao test D1 không bắt:** `TestRecalcAll_PreservesSharedFormulaGroups` chỉ khẳng định SỐ Ô CÔNG
THỨC không giảm — đúng, không giảm (đã khôi phục ở bước 3). Nó không hề đọc GIÁ TRỊ đã cache của
`O6`/`M8`, nên bug này tồn tại xuyên suốt Task 7 mà chưa ai thấy cho tới khi A2 (bắt buộc nhìn file
thật) lộ ra — đúng như lý do §17 xếp A2 là "món nợ chưa ai trả".

**Phạm vi ảnh hưởng đã xác nhận:** dòng 6 (ẩn, chuỗi ngày) và dòng 8 (hiện, mã minh hoạ cho lưới
ngày) — cả hai đều là nhóm shared-formula "chủ + nhiều thành viên rỗng", đều bị. Dòng 9 (DAY) và các
dòng nhân viên (13+, do `ExpandRows` ghi bằng `SetCellFormula` RIÊNG LẺ — không đánh dấu shared) —
KHÔNG bị, đã xác nhận bằng giá trị đúng ở acceptance test + A2. Chưa quét toàn bộ 271 cột × 11 dòng
header để liệt kê hết mọi nhóm shared bị ảnh hưởng — phạm vi chính xác cần một lượt quét riêng.

**CHƯA SỬA — ngoài phạm vi A1/A2 của dispatch này** (A2 là "mở file bằng mắt", không phải "sửa
`recalc.go`). Hướng sửa khả dĩ (ghi lại để làm sau, chưa áp dụng): tách Lượt 2 thành hai lượt con —
2a tính TOÀN BỘ giá trị (gọi `CalcCellValue` cho mọi ô, KHÔNG ghi gì) trong khi sheet còn nguyên vẹn
100% (chưa ô nào bị mutate) — lúc này mọi nhóm shared còn sống nên mọi phép tính đều đúng; 2b MỚI ghi
`SetCellFloat`+`SetCellFormula` từ kết quả đã tính sẵn ở 2a (lúc này phá nhóm shared không còn hại gì
vì không cần tính lại nữa). Đây là RecalcAll ba lượt thay vì hai — chưa code, chỉ ghi hướng.

Artefact giữ lại (đường dẫn tuyệt đối, tự mở bằng Excel thật — LibreOffice không phải Excel):
- `.xlsx`: `/private/tmp/claude-501/-Users-thaidt-Documents-Core System-Enterprise/733fd79c-076c-4ab3-9b9b-863e900c024f/scratchpad/a2_visual/bangcong_2026-07_20rows.xlsx`
- `.pdf` (LibreOffice headless, 23 trang): cùng thư mục, `bangcong_2026-07_20rows.pdf`

### 19.1 A3 — Đóng lỗ hàng rào coverage

Thêm `TestCoveredFieldCodes_ExistsAndIsSubsetOfTemplate` (`mapping_test.go`) — KHÔNG cần DB, chạy mọi
lúc: khẳng định `CoveredFieldCodes` đúng 20 phần tử, không trùng, và mỗi mã đều khớp một field code
thật đọc từ dòng 7 template (`ReadFieldMap`). Đây KHÔNG thay thế `TestDBSource_RealDatabase` — nó chỉ
xác nhận DANH SÁCH khai báo đúng hình dạng, không chứng minh `DBSource` trả giá trị thật (chỉ có test
cần DB mới chứng minh được điều đó).

Viết `internal/report/bangcong/TESTING.md`. **Kiểm CI thật thay vì đoán:** repo **KHÔNG có
`.gitlab-ci.yml`/`Jenkinsfile`/workflow nào chạy `go test`** — file duy nhất trong `.github/workflows/`
(`harness.yml`) chỉ lint file Markdown thay đổi theo policy nội bộ, không đụng Go toolchain. Nghĩa là:
**không chỉ 2 test cần `DATABASE_URL` không chạy trong CI — TOÀN BỘ package hiện không có CI nào chạy
`go test` cả**, dù có `DATABASE_URL` hay không. Đã ghi thẳng điều này vào `TESTING.md`, không viết như
thể CI đã phủ.

### 19.2 A5 — Task 8 (CLI + HTTP) — đã xong, kèm CỔNG HIỆU NĂNG

`cmd/adapter/main.go` thêm `case "report"` (`adapter report --period YYYY-MM --out path.xlsx`).
`internal/api/report.go` (mới) thêm `GET /reports/bangcong?period=YYYY-MM`, stream qua `f.Write(w)`,
không file tạm — đăng ký ở `NewMux`. Cả 2 dùng chung 1 hàm `bangcong.CheckPeriodAvailable` (mới,
`periods.go`) để báo lỗi kỳ không có dữ liệu kèm DANH SÁCH kỳ đang có — brief nói "DBSource đã có sẵn
cơ chế này" là **SAI**, cơ chế đó KHÔNG tồn tại trước dispatch này, phải tự viết mới (`AvailablePeriods`
+ `CheckPeriodAvailable`).

Test tay đầy đủ cả 2 đường: CLI thiếu `--period` / sai định dạng / kỳ không có dữ liệu đều báo lỗi rõ
ràng đúng như thiết kế; HTTP route (qua `httptest`, không cần dựng server thật) cho 3 case y hệt, cùng
message với CLI (dùng chung hàm). Route thật `GET /reports/bangcong?period=2026-03` trả `404` với
body `"no data for period 2026-03 (2026-02-21..2026-03-20); periods with data: 2026-06-21..2026-07-20"`.

**CỔNG HIỆU NĂNG — đo thật trước khi coi Task 8 xong, KHÔNG tự chọn hướng xử lý:**

Đo `Open→SetPeriod→ExpandRows→ghi dữ liệu→EnableFullCalcOnLoad→RecalcAll` với dữ liệu THẬT từ
`DBSource` (không phải fixture giả), cắt đúng N dòng đầu của kỳ 2026-07 (3.768 dòng sẵn có):

| N dòng | Tổng thời gian | `ExpandRows` | Ghi dữ liệu | `RecalcAll` | Diagnostics |
|---|---|---|---|---|---|
| 20 | 7,95 s | 0,46 s | 0,15 ms | **7,01 s** | 2 |
| 200 | 33,90 s | 0,51 s | 1,52 ms | **32,90 s** | 2 |
| 1.000 | 2 phút 19,30 s | 0,73 s | 8,13 ms | **2 phút 18,07 s (138,07 s)** | 2 |

`ExpandRows` và bước ghi dữ liệu KHÔNG phải vấn đề (dưới 1 giây, gần như không đổi theo N) —
**toàn bộ chi phí nằm ở `RecalcAll`**.

**Xu hướng: XẤP XỈ TUYẾN TÍNH** (đo thật ở 3 điểm, không chỉ suy từ 2 điểm) — độ dốc đoạn 20→200
(0,1438 s/dòng) và đoạn 200→1.000 (0,1315 s/dòng) gần bằng nhau, KHÔNG tăng tốc theo N (nếu siêu
tuyến tính thì độ dốc đoạn sau phải lớn hơn đoạn trước rõ rệt — không xảy ra). Hồi quy tuyến tính
trên cả 3 điểm: `RecalcAll(N) ≈ 4,34s + N × 0,134s`. Ngoại suy N=3.768 (TOÀN BỘ kỳ 2026-07 thật) →
**≈509s ≈ 8,5 phút**. Khớp quan sát thực tế: chạy CLI thật với TOÀN BỘ kỳ (không cắt) qua
`adapter report --period 2026-07` **KHÔNG xong trong 2 phút** (bị hủy) — đúng hướng mô hình dự đoán.

Tin tốt duy nhất trong cổng này: KHÔNG phải tăng trưởng siêu tuyến tính (không có dấu hiệu O(N²) hay
tệ hơn) — nhưng hệ số góc 0,134s/dòng tự nó đã đủ lớn để 8,5 phút cho kỳ đầy đủ là con số thật, không
phải trường hợp xấu bất thường.

**Đề xuất (đo xong, trình bày, KHÔNG tự áp dụng):**
- **(a) chấp nhận được** — CHỈ đúng nếu dùng CLI, chạy nền/theo lịch, không ai chờ trực tiếp (~9 phút
  cho kỳ đầy đủ vẫn hoàn thành, không phải "không chạy nổi"). **KHÔNG chấp nhận được cho route HTTP**
  ở quy mô đầy đủ — mọi timeout HTTP/proxy/load-balancer hợp lý (30-60s) đều nổ trước khi xong.
- **(b) thêm `--limit`** — dễ làm, hữu ích để debug/xem trước, nhưng KHÔNG giải quyết được nhu cầu
  thật (báo cáo phải bao phủ toàn bộ 3.768 NV, không phải bản rút gọn).
- **(c) bỏ `RecalcAll` cho file lớn** — giải quyết đúng cổ chai (9 phút chủ yếu để cache SỐ cho công
  cụ đọc bằng code — xem D2/§11.8), nhưng đánh đổi: Excel/LibreOffice mở vẫn đúng (`FullCalcOnLoad`
  lo phần đó), còn `xlsx_inspect.py`/`pandas`/bất kỳ code nào đọc file mà KHÔNG mở qua Excel thật sẽ
  thấy toàn bộ ô công thức RỖNG.

**Đề xuất cá nhân (không tự áp dụng):** (c) cho route HTTP (hoặc giới hạn route HTTP chỉ chấp nhận kỳ
+ ngưỡng N nhỏ, CLI mới cho phép chạy full), giữ CLI chạy `RecalcAll` đầy đủ vì CLI vốn đã là tác vụ
nền chấp nhận chờ vài phút. Đây là ĐỀ XUẤT, chưa code, chờ quyết.

**Còn nợ riêng A5:** phát hiện phụ khi test CLI — `config.Load()` đòi `WD_USERNAME`/`WD_PASSWORD`
KHÔNG ĐIỀU KIỆN cho MỌI subcommand (kể cả `report`, không hề gọi Workday) — phải set giá trị giả để
test được. Không sửa (ngoài phạm vi A5, đây là hành vi `main()` có từ trước), chỉ ghi lại.

---

## 20. Sửa D3 + D4 (cache cũ trong RecalcAll) + đo lại hiệu năng (2026-08-01, phiên thứ 6)

### 20.1 D3 — cơ chế đã chẩn đoán đúng ở §18, sửa bằng pass MATERIALIZE

Xác nhận lại nguyên nhân bằng đọc trực tiếp source excelize v2.10.0 (`cell.go`), không suy đoán:
`removeFormula` (gọi bởi MỌI value-setter, gồm `SetCellFloat`) kiểm `c.F.T == "shared" && c.F.Ref != ""`
— nếu đúng, nó xoá `<f>` của **TOÀN BỘ** ô cùng `Si` (không chỉ ô đang ghi). `RecalcAll` (2-pass cũ) snapshot
công thức xong (Pass 1) rồi COMPUTE+GHI luôn trong 1 vòng lặp (Pass 2 cũ) theo thứ tự dòng/cột — khi vòng
lặp chạm ô MASTER (`N6`, sở hữu `ref="N6:AQ6"`), `SetCellFloat(N6,...)` xoá `<f>` của cả nhóm (gồm `O6`
chưa tới lượt); khi tới lượt `O6`, `CalcCellValue("O6")` gặp ô KHÔNG CÒN công thức → rơi về `<v>` cũ
(cache 202603) thay vì tính lại — ĐÚNG NHƯ BRIEF MÔ TẢ.

**Brief đề xuất chỉ thêm 1 pass MATERIALIZE (`SetCellFormula` không kèm `FormulaOpts`) giữa Pass 1 và Pass
2 cũ. Đã KIỂM BẰNG THỰC NGHIỆM (không tin theo brief) và phát hiện đề xuất đó KHÔNG ĐỦ:** gọi
`SetCellFormula(cell, formula)` KHÔNG kèm `opts` chỉ ghi `c.F.Content`, KHÔNG đổi `c.F.T` (đọc trực tiếp
`cell.go:788-833` — nhánh đổi `c.F.T` chỉ chạy bên trong `for _, opt := range opts`, bỏ qua hoàn toàn nếu
không truyền `opts`). Nghĩa là sau "materialize" kiểu brief, `N6` VẪN mang `c.F.T=="shared"` và `Ref!=""`
— đến lượt Pass 2 cũ gọi `SetCellFloat(N6,...)`, `removeFormula` VẪN kích hoạt nhánh xoá cả nhóm, xoá luôn
công thức vừa "materialize" cho `O6..AQ6` nếu chúng CHƯA tới lượt trong CÙNG vòng lặp đó — **D3 tái diễn
y hệt, chỉ là muộn hơn 1 bước.** Đã tự viết test thực nghiệm tối giản (3 ô `N1`/`O1`/`P1`, xoá sau khi
xác nhận) tái hiện đúng: sau "materialize kiểu brief" + gọi `SetCellFloat` trên `N1` (ô từng là master),
`O1`/`P1` MẤT công thức — xác nhận đề xuất gốc của brief sai, không chỉ lý thuyết.

**Sửa thật: materialize phải TRUYỀN `FormulaOpts{Type: &excelize.STCellFormulaTypeNormal, Ref: &""}`** cho
MỌI entry, không chỉ gọi `SetCellFormula` trơn. Đọc `cell.go`: khi có `opts`, dòng `c.F.T = *opt.Type` chạy
TRƯỚC dòng kiểm `if c.F.T == "shared"` — nên truyền `Type=normal` khiến điều kiện đó luôn SAI ngay từ lúc
materialize, "tháo ngòi" nhóm shared-formula VĨNH VIỄN cho mọi ô, TRƯỚC khi Pass 2 cũ (nay là Pass 3) kịp
gọi bất kỳ `SetCellFloat` nào. Test thực nghiệm xác nhận: sau materialize kiểu này, `SetCellFloat` trên ô
từng-là-master KHÔNG còn xoá anh em cùng nhóm — `O1`/`P1` sống sót nguyên vẹn qua bước này.

**`xlsxF.Si` (chỉ số nhóm shared) không có API công khai nào xoá được** — vẫn còn sót lại trên XML sau
khi sửa (`<f t="normal" si="0">...</f>`), chấp nhận vì vô hại: `t="normal"` khiến mọi trình đọc bỏ qua
`si`. **Đã kiểm bằng thực nghiệm round-trip qua LibreOffice thật** (không chỉ excelize tự chấm): lưu
file → `soffice --convert-to xlsx` → đọc lại bằng openpyxl — `O1=12`, `P1=13` đúng tuyệt đối, `soffice`
không báo lỗi/sửa chữa gì. Kết luận: `si` sót lại KHÔNG gây corrupt.

### 20.2 D4 — UpdateLinkedValue: kiểm thực nghiệm ra sao, XOÁ được `<v>` hay KHÔNG

**Kiểm bằng thực nghiệm TRƯỚC khi dựa vào** (đúng yêu cầu brief), không chỉ đọc source. Dựng 1 ô công
thức chuỗi (`A1 = ="hello"`) mang cache cũ (`t="str"`, `<v>` là chỉ số shared-string rò rỉ — tái hiện đúng
D2), rồi gọi `f.UpdateLinkedValue()`, dán XML thô trước/sau:

```
trước: <c r="A1" t="str"><f>="hello"</f><v>0</v></c>
sau:   <c r="A1"><f>="hello"</f></c>
```

**XOÁ ĐƯỢC** — cả `<v>` và thuộc tính `t` đều biến mất, `<f>` giữ nguyên. Đúng như brief kỳ vọng (dù tên
hàm "linked value" gợi ý tham chiếu NGOÀI file — không phải, nó xoá cache của MỌI ô có công thức, bất kể
liên kết ngoài hay không — xác nhận bằng đọc `excelize.go:500-525`: điều kiện chỉ là `col.F != nil &&
col.V != ""`, không phân biệt loại công thức).

**Phát hiện phụ, brief CÓ cảnh báo nhưng chưa đo**: gọi hàm này cũng **xoá sạch `wb.CalcPr` về `nil`**
(`wb.CalcPr = nil` ngay dòng đầu hàm) — xác nhận bằng `GetCalcProps()` sau khi gọi, mọi field đều `nil`.
Vì `Render` gọi `EnableFullCalcOnLoad` TRƯỚC `RecalcAll`, nếu `RecalcAll` gọi `UpdateLinkedValue` mà không
tự phục hồi cờ đó, `FullCalcOnLoad` sẽ bị xoá âm thầm. **Đã tự gọi lại `EnableFullCalcOnLoad` ngay sau
`UpdateLinkedValue`, bên TRONG `RecalcAll`** — để hành vi hàm này không phụ thuộc thứ tự gọi của caller.

### 20.3 Cache thật sau khi sửa

Render lại cho kỳ 2026-07 (khác kỳ 2026-03 mà MỌI test cũ trong repo dùng — lý do chính test cũ không
bắt được D3/D4: cache cũ của template TRÙNG với kỳ test dùng nên "sai" và "đúng" là cùng 1 con số):

| Ô | Trước sửa | Sau sửa |
|---|---|---|
| A2 (tiêu đề) | `"BẢNG CHẤM CÔNG CỦA CBNV THÁNG  3/2026"` | **rỗng** (công thức chuỗi không cache — đúng thiết kế D2, không còn cache CŨ SAI) |
| O6 | `46076` (= 23/02/2026, cache kỳ 202603) | **A6+2** (đúng theo kỳ đang render) |
| số thẻ `t="shared"` còn lại trong `entries` đã materialize | 101 (từ §16c) | **0** — toàn bộ chuyển `t="normal"` |

Text đọc từ PDF (LibreOffice → PDF → `pdftotext`, tầng NGƯỜI DÙNG THẤY, assert quan trọng nhất theo yêu
cầu brief):

```
BẢNG CHẤM CÔNG CỦA CBNV THÁNG 7/2026
```

Không còn "THÁNG 3/2026" ở đâu trong text PDF. Test mới `TestRecalcAll_DoesNotLeakStalePeriodCache`
(`recalc_stale_cache_test.go`) khoá cả 5 assert brief yêu cầu (a-e): title không chứa "3/2026", O6 =
A6+2 (không phải 46076), quét toàn bộ 31 cột M6:AQ6 không ô nào có cache ngoài cửa sổ [A6,A6+31], text
PDF không chứa "THÁNG 3/2026", và mọi test cũ (cấu trúc/số lượng) vẫn xanh nguyên — render CHO KỲ KHÁC
với mọi test cũ (2026-07 thay vì 2026-03) để bug không thể trốn sau lần này.

### 20.4 Hiệu năng SAU khi sửa — bảng so sánh trước/sau

Đo lại đúng 3 mốc 20/200/1.000 dòng dữ liệu DB thật, cùng phương pháp §18 (Task 8):

| N | RecalcAll TRƯỚC | RecalcAll SAU | Chênh lệch tuyệt đối | Chênh lệch % |
|---|---|---|---|---|
| 20 | 7,01 s | 10,70 s | +3,68 s | +52,5% |
| 200 | 32,90 s | 41,57 s | +8,67 s | +26,4% |
| 1.000 | 138,07 s | 142,73 s | +4,66 s | +3,4% |

**Chênh lệch % GIẢM DẦN khi N tăng** — đúng như dự đoán từ thiết kế: `UpdateLinkedValue` quét 1 lần cho
cả sheet + pass materialize thêm đúng 1 lệnh `SetCellFormula` mỗi entry là chi phí gần như CỐ ĐỊNH,
không tăng theo N nhanh bằng phần biến đổi (`CalcCellValue` vẫn là chi phí chính, không đổi bản chất).
Ở N nhỏ, chi phí cố định chiếm tỉ trọng lớn (rõ nhất ở N=20: +52%); ở N=1.000 (gần quy mô thật), chi phí
cố định gần như biến mất trong tổng (+3,4%).

Hồi quy tuyến tính lại (bình phương nhỏ nhất, cả 3 điểm): `RecalcAll(N) ≈ 11,22s + N × 0,1322s` — hệ số
góc gần NHƯ Y HỆT trước khi sửa (0,134s/dòng), chỉ phần bù cố định tăng (4,34s → 11,22s). Ngoại suy
N=3.768 (kỳ đầy đủ): **≈509s ≈ 8,5 phút** — **THỰC TẾ KHÔNG ĐỔI so với trước khi sửa** (509s cả hai
lần, sai khác nằm trong nhiễu đo). Kết luận quan trọng nhất của phần đo lại: **sửa đúng D3/D4 không
làm xấu đi cổng hiệu năng ở quy mô THẬT sự cần** — chi phí thêm chỉ đáng kể ở quy mô nhỏ (debug/test),
biến mất ở quy mô sản xuất. Ba lựa chọn A5 ở §18 (Task 8) **giữ nguyên không đổi**, kể cả sau khi sửa
D3/D4.

### 20.5 Cổng hiệu năng A5 — chốt phương án (d), không phải (a)/(b)/(c) (2026-08-02)

Người dùng giao "sửa A5 theo ý của bạn". Ba lựa chọn §19.2 đều xuất phát từ một giả định **sai** mà
chính phép đo D4 vừa bác bỏ: rằng phải cache số thì Excel/LibreOffice mới hiển thị đúng. Bằng chứng
ngược nằm ngay trong §20.3 — tiêu đề hiện đúng "THÁNG 7/2026" trong PDF **dù `A2` không có cache nào**.
LibreOffice (và Excel) **tự tính công thức không có cache**; nó chỉ bỏ qua việc tính lại khi cache
**đã tồn tại**. Nghĩa là §18.4 viết "LibreOffice phớt lờ `fullCalcOnLoad`" là **kết luận sai của
chính tôi** — thứ bị phớt lờ chưa bao giờ là cái cờ, mà là do cache cũ chắn đường.

Hệ quả: 8,5 phút của `RecalcAll` được trả để phục vụ **một nhóm người đọc không tồn tại trong repo
này** — công cụ đọc `.xlsx` bằng code mà không mở qua ứng dụng bảng tính. Cache **vắng** thì vô hại;
cache **sai** mới hại. Vậy việc đúng là **xoá cache, đừng tính lại**:

- Tách `ClearStaleCache(f)` khỏi `RecalcAll` (`recalc.go`) — chỉ `UpdateLinkedValue` + phục hồi
  `EnableFullCalcOnLoad`. `Render` **luôn** gọi nó (template mang cache kỳ 202603, không xoá là sai).
- `Render` **mặc định KHÔNG** gọi `RecalcAll` nữa. Bật lại bằng `WithRecalc()` /
  `adapter report --recalc` / `GET /reports/bangcong?period=…&recalc=1`, dành đúng cho trường hợp
  duy nhất cần: có thứ gì đó đọc file **không qua** Excel/LibreOffice (openpyxl `data_only=True`,
  pandas). Hiện **không pipeline nào trong repo làm vậy**.

**Đo end-to-end qua CLI thật, toàn bộ kỳ 2026-07 (3.768 nhân viên):**

| | Thời gian | Kết quả |
|---|---|---|
| Trước (mặc định `RecalcAll`) | ~8,5 phút ngoại suy — **chạy thật thì timeout** | — |
| Sau (mặc định chỉ `ClearStaleCache`) | **5,18 giây** | 3.781 dòng, 463.928 công thức, **0 ô công thức còn cache** |

Test khoá bất biến: `TestRender_DefaultPathCachesNothing` (`render_default_path_test.go`) — đọc
**XML thô** (excelize là thứ đang bị kiểm, để nó tự mô tả đầu ra thì không chứng minh được gì): không
ô công thức nào còn `<v>`, `A2` rỗng, `fullCalcOnLoad` còn nguyên (xoá cache mà mất cờ này thì mọi ô
hiện trắng). Hai test cũ khẳng định giá trị cache nay truyền `WithRecalc()` tường minh — cũng là cách
nói rõ mỗi test đang nói về đường nào.

**Trạng thái git:** commit `e91ed3c`, **đã push** lên `origin/feature_v1` cùng `1473409` (A3+A5) —
`555840c` (Task 7) đã có sẵn trên remote từ trước, không phải phiên này đẩy. Nhánh remote của
`Core System-adapter` là **`feature_v1`**, KHÔNG có nhánh `feature_1` (đó là quy ước của
`Core System-backend`/`Core System-frontend`).

---

## 21. Tài liệu liên quan

- `Core System-adapter/internal/db/migrations/0023_raas_reports.sql` — bảng `raas_monthly_attendance`.
- `Core System-adapter/internal/db/migrations/0001_raw_workday.sql`, `0004_calculated_time_block_columns.sql` — nguồn lưới ngày.
- `Core System-adapter/Get_Monthly_Attendance_Report_API_Response.txt` — 38 field thật của RaaS.
- `Core System-adapter/WORKDAY_FETCH_API_REQUESTS.md` — cách gọi RaaS.
- `Core System-backend/internal/service/report_gen_*.go` — 13 mẫu dùng excelize đã chạy production.

---

## 22. Bảng đối chiếu mã field ↔ nguồn DB, xuất ra Excel (2026-08-03)

Sản phẩm: **`document/BangCong-Template-FieldMap-TASK-REF.xlsx`** — 116 mã field, mỗi mã một dòng.

**Cách dựng — không gõ tay dòng nào.** Mã field đọc thẳng từ **dòng 7 của template đã nhúng** qua
`ReadFieldMap` (đúng G1, gồm cả 4 mã hỏng `{r}` đã chuẩn hoá); tên hiển thị lấy từ **dòng 8**; cột
"nguồn theo template" lấy từ **dòng 4** (chính file gốc tự khai `WD` / `Core System` / để trống); phần
map DB lấy nguyên văn biểu thức SQL từ `source_db.go`. Nghĩa là file này **không thể lệch khỏi code**
theo kiểu tài liệu chép tay bị cũ đi — nó là ảnh chụp của template thật + truy vấn thật tại thời điểm
xuất.

Công cụ là một `cmd/tmp-fieldmap` **dùng một lần, đã xoá sau khi chạy** (`go build ./...` sạch, working
tree sạch). Ghi bằng excelize, kiểm lại bằng openpyxl **và** round-trip LibreOffice → PDF — đúng G9,
không để excelize tự chấm điểm mình.

| Trạng thái | Số mã |
|---|---|
| **ĐÃ map** (DBSource điền thật) | **20** |
| CHƯA map — Task 7b (lưới ngày `Workdays1..31`) | 31 |
| CHƯA map (còn lại) | 65 |
| — trong đó có **nguồn ứng viên** đã xác minh tồn tại trong DB | 23 |

**Cột I "Nguồn ỨNG VIÊN" là gợi ý, KHÔNG phải mapping.** View và cột đã kiểm tồn tại thật bằng `\d`
trên DB đã restore (`ts_ot_reconciliation`, `ts_time_off_plan_balances_pivot` — xác nhận đủ cột), nhưng
**chưa viết truy vấn nào và chưa đối chiếu một giá trị nào**. Tách hẳn ra cột riêng để không ai đọc
"view có tồn tại" thành "cột đã chạy".

**Phát hiện đáng giá nhất khi dựng bảng:** `DateQuit` (cột L, "Ngày nghỉ việc") có nguồn **đã nằm sẵn
trong truy vấn hiện tại** — `wd_workers.termination_date`, đang được đọc ở mệnh đề `WHERE` để lọc người
nghỉ trước kỳ (436/4.211 NV có giá trị), chỉ là không được xuất ra `Row`. Đây là mã dễ nối nhất trong
toàn bộ 65 mã còn lại: không cần JOIN mới, không cần quyết định nghiệp vụ, không chờ ai.

Hai cảnh báo đã ghi thẳng vào sheet "Truy vấn gốc" để người đọc file không cần quay lại PLAN này:
quy tắc ô trống (G2 — NULL thì để trống, không bao giờ điền 0) và **F2** (ô trống ở cột đầu vào vẫn
làm cột tổng dẫn xuất ra `0`, một con số trông hợp lệ mà vô nghĩa).
