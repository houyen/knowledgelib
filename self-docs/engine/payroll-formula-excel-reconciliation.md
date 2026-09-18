---
id: self-docs/engine/payroll-formula-excel-reconciliation
canonical_question: 'Technical guide and specification: Đối chiếu công thức lương:
  Excel HR  vs DB `payroll_engine`'
aliases:
- 'Đối chiếu công thức lương: Excel HR  vs DB `payroll_engine`'
- Core System Formula Excel Reconciliation 190826
entity_type: architecture_explainer
domain: self-docs > engine
last_verified: 2026-09-17
---

# Đối chiếu công thức lương: Excel HR (`Payroll_BRD_Tracker_Item.xlsx`) vs DB `payroll_engine`

**Ngày:** 19/08/2026 · **Loại việc:** CHỈ ĐỌC — không sửa code/DB/config. Mọi sai lệch dưới đây chỉ được ghi nhận, chưa xử lý.

**Cập nhật 19/08/2026 (cùng ngày, sau khi báo cáo này được dùng để lên `/propose` — xem `llmwiki/wiki/sources/draft/190826-Core System-formula-rules-update.md`):** user đã trả lời trực tiếp 3 câu hỏi mở của mục 3.3, 3.9, 3.10 dưới đây. Kết quả:
- **Mục 3.3** (lương phép tồn chỉ trả NV chính thức) — **XÁC NHẬN GIỮ NGUYÊN**, không sửa DB. Đây là hành vi cố ý, không phải bug.
- **Mục 3.10** (trần phí công đoàn 234k vs 253k) — **XÁC NHẬN GIỮ 253.000đ**, không sửa DB. Số 234k trong Excel là số cũ.
- **Mục 3.9** (điều kiện nghỉ ≥14 ngày không đóng BHXH) — **CHUYỂN SANG GIAI ĐOẠN 2, CHỜ DỮ LIỆU ĐỘI ADAPTER**. User xác nhận backend/DB hiện chưa có nguồn dữ liệu đúng nghĩa "số ngày nghỉ liên tục trong tháng"; sẽ phối hợp đội adapter tạo ra số liệu này rồi bắn sang backend. Không tự tạo formula tham chiếu field chưa tồn tại.

Kết luận: sau vòng xác nhận này, **không còn mục nào trong báo cáo cần sửa DB ngay** — 2/3 nghi vấn "Giai đoạn 1" hoá ra đúng theo chủ ý nghiệp vụ, 1/3 chờ dữ liệu nguồn mới. Các mục 3.2, 3.4–3.8, 3.12 vẫn giữ nguyên trạng thái "cần thiết kế thêm" như báo cáo gốc, chưa xử lý.

## Phụ lục — Danh sách TẤT CẢ câu hỏi mở còn treo của Giai đoạn 2 (gom 1 lượt theo yêu cầu user, 19/08)

Mục đích: user đi hỏi HR/kế toán/Workday functional team **một lần** thay vì rải rác theo từng cụm `/propose`. Mỗi câu ghi rõ mục báo cáo liên quan + câu tương ứng (nếu có) trong Excel `Questions-draft` (BRD Tracker) để không hỏi trùng nội dung đã có sẵn trong đó.

### A. Cụm OT (mục 3.7) — SPEC `190826-Core System-ot-engine.md`
Đã chốt: **Core System tự tính** (Phương án A), không dùng số Workday đẩy sẵn. **Khảo sát kỹ thuật thêm (19/08) đã phát hiện phần lớn hạ tầng đã có sẵn — xem mục ĐÍNH CHÍNH đầu SPEC** — nên câu hỏi bên dưới đã cập nhật, không còn là "thiết kế từ đầu":
1. `cash_1x/cash_2x/cash_3x` trong report Workday `"Enterprise - Monthly Attendance Report"` (bảng `raas_monthly_attendance`, đã có 3.768 dòng dữ liệu thật) có đúng là 3 mốc OT ngày thường/nghỉ/lễ đã bucket sẵn không? Đơn vị là ngày hay giờ? Phần ca đêm (3 mốc còn lại) lấy nguồn nào — có nằm trong report `"Enterprise - OT Plan & OT Actual"` (qua `Calculation_Tags`) không? *(đang tạm treo, user sẽ khảo sát/quyết định sau)*
2. Cách tách `OT_TAX`/`OT_NONTAX` đúng luật thuế TNCN — **lưu ý:** DB hiện code cứng `OT_TAX` luôn = 0 (coi toàn bộ OT miễn thuế), giả định này có thể sai theo luật (chỉ miễn phần trả thêm so với đơn giá ngày thường), cần kế toán xác nhận lại.
3. Hệ số trong `ot_multiplier_configs` (1.50/2.00/2.00/2.70/3.00/3.70, hiệu lực từ 2020-01-01) có đúng mức công ty đang áp dụng thật không, hay là số cũ/thử nghiệm lúc setup ban đầu?
4. **(mới)** Migration `migrationSalaryComponentsV3` từng xoá chủ ý 8 component OT đầy đủ với comment "chưa cần tính" — cần hỏi tác giả (có thể đồng nghiệp nhánh `origin/giatbh`) lý do cụ thể đã tắt, trước khi coi đây là "xây mới từ đầu".

### B. Cụm bổ nhiệm 2 mức lương giữa kỳ (mục 3.2) — *(trùng câu hỏi số 17 đã có sẵn trong `Questions-draft`)*
4. Khi nhân viên được bổ nhiệm/tăng lương giữa kỳ lương (có 2 mức lương khác nhau trong cùng 1 kỳ): Core System tự tách 2 giai đoạn theo ngày hiệu lực quyết định, hay Workday đẩy sẵn 2 dòng lương riêng?
5. Rule tách 2 giai đoạn này có áp dụng luôn cho phụ cấp trách nhiệm khi phụ cấp thay đổi giữa kỳ không?

### C. Cụm PC cơm theo địa điểm (mục 3.4) — *(trùng câu hỏi số 1, 2, 14 đã có sẵn trong `Questions-draft`)*
6. Số bữa cơm/ngày theo địa điểm (VP 1 bữa, site <30km 2 bữa, site ≥30km 3 bữa) do Workday tính sẵn rồi đẩy sang, hay Core System phải tự tính?
7. Nếu Core System tự tính: dữ liệu "khoảng cách công trường" lấy từ đâu, ai cập nhật/duy trì?
8. Khi nhân viên đi làm đúng ngày lễ hoặc ngày nghỉ (không phải Chủ nhật): có tính thêm bữa cơm không, tính theo cách nào?

### D. Cụm PC điện thoại/đi lại/xăng theo level + prorate <14 ngày (mục 3.5, 3.6) — *(trùng câu hỏi số 3, 13, 14 đã có sẵn trong `Questions-draft`)*
9. PC điện thoại "theo level" (Excel `AS10`) — bảng tra level → mức trần cụ thể là gì? (DB hiện dùng trần cố định 400.000đ cho mọi level, không đúng theo Excel).
10. Ngưỡng "dưới 14 ngày đi làm thực tế thì phụ cấp tính theo tỷ lệ" — tính trên loại ngày nào: chỉ ngày đi làm thực tế, hay gồm cả ngày nghỉ hưởng lương?
11. Công thức chia tỷ lệ chính xác: chia cho ngày công chuẩn (`STD_DAYS`) hay chia cho 14?
12. Rule <14 ngày này áp dụng cho đúng 4 khoản phụ cấp (điện thoại, đi lại chịu/không chịu thuế, xăng) hay cả 7 loại phụ cấp?
13. Nhân sự điều động (chuyển giữa VP/công trường hoặc giữa 2 công trường trong cùng kỳ lương) — phụ cấp tính theo nơi làm việc cuối kỳ, hay chia tỷ lệ theo số ngày ở từng nơi?

### E. Cụm thưởng bình quân 12 tháng (mục 3.8) — *(trùng câu hỏi số 21 đã có sẵn trong `Questions-draft`)*
14. Lương bình quân 12 tháng liền kề (dùng để tính Thưởng Tết Âm lịch, tối đa 15 triệu, và Lương tháng 13) — Core System tự lưu lịch sử lương để tính, hay Workday cung cấp sẵn con số bình quân?
15. "Thời gian tính thưởng" (dùng trong công thức `= thời gian tính thưởng/365 × định mức`) đếm từ ngày nào đến ngày nào — từ ngày vào làm, hay từ đầu năm tài chính?

### F. Cụm BHXH nghỉ ≥14 ngày (mục 3.9) — đã có hướng riêng
16. *(Không phải câu hỏi — ghi nhớ)* User sẽ phối hợp đội adapter tạo dữ liệu "số ngày nghỉ liên tục trong tháng" rồi bắn sang backend; không cần hỏi HR thêm ở đây, chỉ cần xác nhận tên field/format khi đội adapter có kết quả.

### G. Cụm thuế TNCN thử việc (mục 3.12) — *(trùng câu hỏi số 3, 25, 26 đã có sẵn trong `Questions-draft`, có hệ quả pháp lý/tài chính — KHÔNG tự chọn)*
17. Nhân viên thử việc (không phải thực tập, người Việt) tính thuế TNCN theo biểu luỹ tiến giống nhân viên chính thức (như DB đang làm), hay 10% cố định trên tổng thu nhập (như Excel gốc `CH11` ghi)?
18. Hợp đồng vãng lai/dưới 3 tháng có cần thêm 1 nhánh riêng tính 10% cố định theo quy định thuế hiện hành không (DB hiện chưa có nhánh này)?
19. Cơ sở tính thuế cho các nhánh 10%/20% là "tổng thu nhập" (GROSS, chưa trừ gì) như Excel ghi, hay "thu nhập tính thuế" (`TAXABLE_INC`, đã trừ bảo hiểm/giảm trừ) như DB hiện đang dùng?

## Cập nhật 21/08/2026 — Phân tích câu trả lời (`self-docs/list_ques_main-answer.md`) + xác nhận cơ chế 2 loại input

### Xác nhận cơ chế input (câu hỏi riêng của user, đã kiểm bằng đọc code, không suy đoán)

`salary_components.component_type="input"` có **đúng 2 nguồn giá trị**, phân biệt bằng cột `source_field`:
- `source_field = ''` → **HR nhập tay**, qua bảng `payroll_manual_inputs`.
- `source_field = 'attendance_summary.<col>'` → **input hệ thống**, đọc từ bảng `attendance_summary` — cơ chế đọc tại `internal/service/payroll_service.go:524-531` (`resolveSourceField`).

**Dữ liệu từ đội adapter dùng được ngay theo đường "input hệ thống"** — không cần cơ chế mới: thêm cột mới vào `attendance_summary` (ví dụ `ot_weekday_normal_hours`, `meal_count`, `phone_cap_by_level`...) + nối 1 đường sync ghi vào cột đó (tương tự các cột đã có `transport_allowance`, `phone_allowance`, `meals`, `leave_l`...), rồi tạo/sửa component trong `salary_components` với `source_field` trỏ đúng cột mới. Đây là pattern có sẵn, không phải thiết kế từ đầu.

### Phân tích trả lời — khớp mong đợi chưa

Phần lớn câu trả lời **cụ thể và dùng được** (đặc biệt cụm B/C/D — có công thức/nguồn dữ liệu rõ), nhưng vẫn còn lỗ hổng:
- **Q2** (cách tách OT_TAX/OT_NONTAX theo luật thuế) — chưa trả lời (để trống).
- **Q7** (nguồn "khoảng cách công trường") — trả lời mơ hồ: *"Lấy số liệu khoảng cách để HR đối chiếu"* — không rõ đây là xác nhận "khoảng cách không cần vào công thức vì đã gói trong định mức cơm của Q6" hay "vẫn cần lấy khoảng cách, chỉ để HR đối chiếu thủ công song song". **Cần hỏi lại làm rõ trước khi code.**
- **Q3** trả lời xác nhận `Cash_1x/Cash_2x/Cash_3x` (nguồn: Workday API `Time_Tracking > Get_Calculated_Time_Blocks > ... > Time_Calculation_Tag_ID`, đơn vị "unit", nhân với `Calculated_Quantity`) đúng là 3 mốc ngày thường/nghỉ/lễ — nhưng **không thấy đề cập phần ca đêm** (3 mốc còn lại trong `ot_multiplier_configs`: `OT_WD_NIGHT`/`OT_WE_NIGHT`/`OT_HLD_NIGHT`) — vẫn còn thiếu, cần hỏi tiếp.
- **Q12, Q14, Q15, Q17, Q18, Q19** — vẫn "chưa confirm", chưa có câu trả lời.

### Danh sách A — việc thuộc BACKEND (lên PLAN xử lý sau khi đủ dữ liệu từ adapter)

1. **[3.2]** Logic tách lương theo bộ phận khi bổ nhiệm/tăng lương giữa kỳ: WD chỉ cung cấp định mức tại từng bộ phận theo thời điểm hiệu lực — BE phải tự tính lại theo tỷ lệ ngày ở từng bộ phận (Q5). Áp dụng luôn cho phụ cấp trách nhiệm.
2. **[3.4]** Công thức PC cơm: `(định mức cơm bộ phận / 45.000) = số bữa/ngày tại bộ phận đó`, cộng dồn theo từng ngày dựa vào schedule/bộ phận của ngày đó (Q6); cộng thêm bữa khi đi làm ngày lễ/nghỉ theo tag Cash_1x/2x/3x quy đổi phức hợp (Q8 — 1 ngày có thể mang nhiều tag, ví dụ lễ Cash_2x ⇒ quy đổi Cash_1x + Off_In_Lieu_1x = 1).
3. **[3.5]** Giữ đúng CẤU TRÚC công thức `PHONE_TAX`/`PHONE_NONTAX` hiện tại (`MAX(0, allow-cap)` / `MIN(allow,cap)`) — chỉ đổi nguồn `cap` từ hằng số 400.000 sang tra theo level (Q9, cấu trúc thuế đã được xác nhận đúng, chỉ còn thiếu giá trị cap thật theo level).
4. **[3.6]** Công thức prorate <14 ngày: ngưỡng = (tổng công đi làm 21→20) + (tổng nghỉ hưởng lương cột BA→BE); tỷ lệ áp = (tổng công đi làm + nghỉ lễ); chia cho **công chuẩn CÓ THỂ LÀM FULL tại bộ phận đó trong kỳ** (không phải 14, không phải STD_DAYS toàn kỳ) (Q10, Q11); nhân sự điều động chia theo tỷ lệ công chuẩn từng bộ phận (Q13) — cùng cơ chế với việc B.
5. **[3.7 — OT]** Công thức nhân giờ/đơn vị OT theo tag (`Cash_1x/2x/3x` × `Calculated_Quantity`) với hệ số trong `ot_multiplier_configs` — chờ dữ liệu ca đêm từ adapter trước khi hoàn thiện đủ 6 nhánh.

### Danh sách B — việc thuộc ĐỘI ADAPTER (gửi riêng để họ xử lý phía Workday)

1. **[OT]** Lấy dữ liệu OT theo tag `Time_Calculation_Tag_ID` (`Cash_1x/2x/3x`, `Off_In_Lieu_1x`...) qua Workday API `Time_Tracking > Get_Calculated_Time_Blocks` (chỉ lấy block đã `APPROVED`), kèm `Calculated_Quantity` — đồng bộ vào `attendance_summary` (cột mới) để BE đọc qua "input hệ thống" (Q1, Q3).
2. **[Bổ nhiệm]** Đồng bộ 2 report Workday: `"Enterprise - Compensation Changes Report"` (định mức lương/phụ cấp thay đổi theo bộ phận + ngày hiệu lực) và `"Enterprise - List Detail of Work History"` (đối chiếu lịch sử công tác) — cần cho cả cụm 3.2 và 3.4 (định mức cơm theo bộ phận) (Q4, Q6).
3. **[PC điện thoại theo level]** Đồng bộ bảng tra level → mức trần PC điện thoại từ Workday (Q9 — "Tất cả số liệu theo WD").
4. **[Bình quân 12 tháng]** Tìm đúng report/API Workday cho lương bình quân 12 tháng liền kề — **user tự nhận chưa kiểm tra, cần đội adapter phụ giúp tìm** (Q14, trả lời nguyên văn "Chưa kiểm tra trong WD, cần phụ giúp để tìm đúng report hoặc API").
5. **[Ca đêm OT]** — chưa có trong câu trả lời hiện tại, cần hỏi bổ sung: dữ liệu ca đêm (3 mốc `*_NIGHT` trong `ot_multiplier_configs`) lấy từ tag nào trong `Get_Calculated_Time_Blocks`, hay cần API/report khác.

## Cập nhật 21/08/2026 (tiếp) — Đọc thêm file `CTD_REPORT WORKDAY - ABSENCE & TIME TRACKING.xlsx`

File này (`~/Downloads/CTD_REPORT WORKDAY - ABSENCE & TIME TRACKING.xlsx`, sheet chính **`Monthly Attendance Report300726`**) là **tài liệu field-mapping chi tiết đã có sẵn** (khả năng do RA/Workday functional lập) — mỗi cột có: dòng 5 = report/API nguồn, dòng 6 = ghi chú tag/status, dòng 7 = cách tính, dòng 9 = **XPath/query WD thật**. Đây trả lời cụ thể hơn nhiều câu hỏi đang treo:

- **Xác nhận Q1/Q3 (OT)**: nguồn xác nhận là `Time_Tracking → Get_Calculated_Time_Blocks`, lọc `Status_Reference = APPROVED`, theo tag `Time_Calculation_Tag_ID` — danh sách tag đầy đủ tìm được: `Actual_Working_Day`, `Paid_Holiday`, `Cash_1x`, `Cash_2x`, `Cash_3x`, `Off_in_Lieu_1x`, `Off_in_Lieu_2x`, `Pay_Back`, `Sunday_Meal`, `Night_Meal`. Công thức tổng hợp mẫu: `Cash_1x*1 + Cash_2x*2 + Cash_3x*3` (dùng để ra "tổng ngày hưởng lương", KHÔNG phải trực tiếp ra tiền OT).
- **XÁC NHẬN GAP MỚI, quan trọng**: quét toàn bộ file cho "night"/"đêm" chỉ ra **`Night_Meal`** (phụ cấp cơm ca đêm) — **không có tag nào cho hệ số OT ca đêm** (3 mốc `OT_WD_NIGHT`/`OT_WE_NIGHT`/`OT_HLD_NIGHT` trong `ot_multiplier_configs`). Tức phần ca đêm của OT **chưa có nguồn dữ liệu Workday nào được xác nhận** — nặng hơn nhận định ban đầu, cần hỏi thẳng RA/Workday: có tag nào khác cho ca đêm không, hay công ty hiện không tách lương OT ca đêm riêng.
- **XÁC NHẬN GAP MỚI**: quét "12 tháng"/"bình quân" ra **0 kết quả** trong file này — khớp với câu trả lời của HR ở Q14 ("chưa kiểm tra trong WD") — xác nhận đây thật sự là khoảng trống, không phải do tôi tra thiếu.
- **Xác nhận công thức rule <14 ngày (Q10/Q11, cụ thể hơn câu trả lời trước)**: ô `BO7`/`DO7` — *"Nếu Total paid days - allowances < 14, thì tính Paid working days BP1 + Holiday BP1, còn lại tính tỉ lệ bình thường — Allowance_-_Telephone"*. Công thức tỷ lệ đầy đủ (ô `EU7`...`FS7`, lặp cho 4 "Bộ phận"/segment do điều động giữa kỳ): `= Số ngày hưởng phụ cấp / ngày công chuẩn BỘ_PHẬN_ĐÓ * Định mức phụ cấp` — áp dụng đều cho **6 loại phụ cấp**: điện thoại, ô tô, nhiên liệu, đi lại, duyệt riêng, đặc biệt (trả lời luôn 1 phần Q12 — không phải chỉ 4 loại như câu hỏi cũ giả định, nhưng vẫn cần xác nhận lại có đúng 6 hay 7 loại).
- **Xác nhận công thức PC cơm theo bộ phận (Q6/Q8)**: `ET7`...`FN7`: `= Tổng bữa ăn bộ phận N * 45.000`; nguồn "Số ngày tính bữa ăn" có quy tắc riêng theo VP/CT (`O7`: VP nghỉ thứ 7 không tính cơm — 5 ngày/tuần; CT thứ 7 vẫn tính — 6 ngày/tuần; luôn bỏ ngày nghỉ lễ).
- **Xác nhận nguồn dữ liệu tách theo bộ phận khi điều động (cụm 3.2)**: cột `AW9`/`AX9` — `ts_worker_organization_change_diff → Departments[1]` + tính trong code đoạn ngày `21/n → 20/n+1` cho từng segment — nghĩa là **adapter cần tính sẵn các "segment" theo ngày đổi bộ phận**, không chỉ đẩy raw event.
- **Cấu trúc dữ liệu quan trọng cho thiết kế contract BE**: file này thiết kế sẵn cho **tối đa 4 "Bộ phận"/segment trong 1 kỳ lương** (nhân viên đổi bộ phận tới 3 lần/kỳ) — mỗi bộ phận có đầy đủ 1 bộ cột riêng (ngày công, bữa ăn, phụ cấp...). Đây là gợi ý mạnh cho việc quyết định "contract" ở câu hỏi build-now-adapt-later: **nên là 1 bảng con theo (nhân viên, kỳ, segment/bộ phận)**, không phải chỉ thêm cột scalar vào `attendance_summary` (1 dòng/kỳ) như suy nghĩ ban đầu.

### Danh sách C — vẫn "chưa confirm", CHƯA gửi ai xử lý (cần hỏi lại HR/kế toán, không phải BE hay adapter)

- Q2 — cách tách OT_TAX/OT_NONTAX theo luật thuế TNCN.
- Q7 — làm rõ lại ý nghĩa câu trả lời (khoảng cách công trường có cần vào công thức không).
- Q12 — rule <14 ngày áp dụng 4 hay 7 loại phụ cấp.
- Q15 — cách đếm "thời gian tính thưởng" (bình quân 12 tháng).
- Q17, Q18, Q19 — toàn bộ cụm thuế TNCN thử việc (có hệ quả pháp lý, vẫn treo hoàn toàn).

## 0. Phạm vi & phương pháp

- **Nguồn Excel:** `~/Downloads/Payroll_BRD_Tracker_Item.xlsx`, đọc bằng `openpyxl` (`data_only=False` để lấy formula text gốc, không phải giá trị cache). 4 sheet: `Questions-draft`, `Core System template`, `Plan`, `obsoleted -Core System-origin (dev)`.
- **Nguồn DB:** đọc trực tiếp `psql -h localhost -d payroll_engine` (không qua UPDATE/INSERT/DELETE). Không gọi được API `GET /api/v1/config/salary-components` — backend tại `:8080` yêu cầu JWT/dev-bypass thực sự (không chỉ header thường), không cố thêm cơ chế xác thực để tránh động vào state đang chạy song song; đọc thẳng DB thay thế là đủ vì đây là cùng một nguồn dữ liệu.
- **Phát hiện quan trọng về nguồn DB — có 2 bảng, chỉ 1 bảng đang sống:**
  - `salary_components` (148 dòng) — **bảng đang được engine đọc thật** (dùng trong `salary_component_repo.go` và nhiều repo/handler khác). Đây là "cây công thức" (Formula tree) thật sự vận hành.
  - `salary_formula_configs` (18 dòng, `scope_type=company, scope_id=CTC`) — **bảng mồ côi**: chỉ được `internal/database/database.go` tạo + seed lúc boot, **không có bất kỳ repo/handler nào SELECT từ bảng này** (grep toàn repo `Core System-backend` chỉ thấy 3 lần xuất hiện, cả 3 đều nằm trong đúng khối tạo/seed ở `database.go`). Bảng này dùng bộ mã hoàn toàn khác (`SAL_BASE`, `GROSS_PAY`, `STANDARD_DAYS`=26 cố định...) và **số liệu luật cũ/khác hẳn** (giảm trừ bản thân 11.000.000đ + NPT 4.400.000đ/người, trần BHXH 36.000.000đ) — không khớp cả Excel HR lẫn `salary_components`. Vì không repo nào đọc bảng này nên nó **không ảnh hưởng hành vi tính lương thật**, nhưng nếu ai vô tình tra cứu/báo cáo dựa vào `salary_formula_configs` sẽ ra kết luận sai hoàn toàn. → Đối chiếu dưới đây chỉ dùng `salary_components` làm "cấu hình hệ thống".
- **Nguồn công thức HR trong Excel:** sheet `obsoleted -Core System-origin (dev)` (mã cột dòng 7, công thức/rule text nằm rải rác dòng 8/10/11/12/14 — HR không viết công thức liền một chỗ mà tách "công thức chính" ở dòng 10 và "ghi chú/điều kiện áp dụng" ở các dòng 11/12/14 bên dưới). Sheet `Core System template` chỉ có nhãn cột (không có công thức). Sheet `Questions-draft` là **báo cáo gap-analysis đã có sẵn từ trước** (do phân tích viên khác lập, so "Formula tree" — tức đúng bảng `salary_components` — với sheet `obsoleted -Core System-origin (dev)`), 31 câu hỏi kèm trích dẫn ô nguồn. Tôi dùng nó làm **danh sách khoanh vùng**, nhưng **tự đọc lại từng ô Excel gốc + từng dòng DB thật** để xác nhận độc lập, không copy nguyên kết luận cũ (một điểm ở mục 3.7 cho thấy DB đã thay đổi so với thời điểm Questions-draft viết).

---

## 1. Bảng liệt kê công thức HR trích nguyên văn (Excel)

Trích các ô có công thức/rule text trong `obsoleted -Core System-origin (dev)` (mã cột lấy từ dòng 7):

| Cột | Nhãn (dòng 7) | Ô + nội dung nguyên văn |
|---|---|---|
| R | Mức lương đóng BHXH, BHYT | `R10`: `'Mức trần 50,600,000'` |
| S | Mức lương đóng BHTN | `S10`: `'Mức trần 106,200,000'` |
| AG | Lương Thử việc | `AG10`: `'.= ngày thử việc* lương thử việc(bao gồm ngày đi làm + ngày nghỉ hưởng lương của Tgian thử việc)'` |
| AH | Lương chính thức | `AH10`: `'= ngày chính thức* lương chính thức (bao gồm ngày đi làm + ngày nghỉ hưởng lương của Tgian CThuc)'`; `AH11`: `'Bổ nhiệm: nếu có 2 mức lương khác nhau trong kỳ lương thì tính theo 2 gdoan'` |
| AI | Phụ cấp Trách nhiệm | `AI10`: `'=ngày hưởng phụ cấp * Định Mức phụ cấp/ngày công chuẩn'` |
| AJ | Lương phép tồn | `AJ10`: `'=ngày phép tồn/ngày công chuẩn * Mức lương'` (không nêu điều kiện loại HĐ) |
| AK | Tổng lương thực tế trong tháng | `AK10`: `'=lương thử việc+lương chính thức+phụ cấp trách nhiệm+lương phép tồn'` |
| AL | PC cơm (Taxable) | `AL10`: `'sau khi tính phụ cấp cơm theo rule:'`; `AL11`: `'vp: 1b/ngày, site <30km: 2b/ngày, site >=30km: 3b/ngày'`; `AL12`: `'--> Phụ cấp cơm còn lại sau khi trừ mức miễn 730k'` |
| AN | PC NL/Xăng (Taxable) | `AN10`: `'VP: up duyệt riêng theo tờ trình'`; `AN11`/`AN12`: `'-- lưu ý nhân sự điều động'` |
| AO | PC đi lại (Taxable) | `AO10`: `'Theo quy định, lưu ý số ngày đi làm thực tế dưới 14 (mười bốn) ngày, phụ cấp được tính theo tỷ lệ ngày làm việc thực tế và ngày nghỉ lễ trong tháng'`; `AO11`: `'-- lưu ý nhân sự điều động'` |
| AQ | PC Khác (Taxable) | `AQ10`: `'Phụ cấp duyệt riêng theo tờ trình'` |
| AR | PC cơm (Non-tax) | `AR10`: `'sau khi tính phụ cấp cơm theo rule:'`; `AR11`: `'vp: 1b/ngày, site <30km: 2b/ngày, site >=30km: 3b/ngày'`; `AR12`: `'--> Phụ cấp cơm <=730k, lấy pc cơm thực tế, ngược lại 730k'`; `AR14`: `'-- lưu ý nhân sự điều động'` |
| AS | PC điện thoại (Non-tax) | `AS10`: `'Theo level, lưu ý số ngày đi làm thực tế dưới 14 (mười bốn) ngày, phụ cấp được tính theo tỷ lệ ngày làm việc thực tế và ngày nghỉ lễ trong tháng'`; `AS11`: `'-- lưu ý nhân sự điều động'` |
| AU | PC đi lại (Non-tax) | `AU10`: `'Tính theo quy định, lưu ý số ngày đi làm thực tế dưới 14 (mười bốn) ngày, phụ cấp được tính theo tỷ lệ ngày làm việc thực tế và ngày nghỉ lễ trong tháng'`; `AU11`: `'-- lưu ý nhân sự điều động'` |
| AY | OT Non-tax | `AY10`: `'chủ nhật 200%'`; `AY11`: `'Ngày nghỉ Lễ, Tết theo quy định của pháp luật: theo list DS: trả thêm 100% tiền lương và ghi nhận 2 ngày nghỉ bù cho mỗi ngày đi làm'`; `AY12`: `'Ngày truyền thống, bổ sung, bù: = và ghi nhận nghỉ bù cho mỗi ngày đi làm'` |
| AZ | TẾT ÂM LỊCH | `AZ10`: `'Lương bình quân 12 tháng liền kề, ko quá 15 triệu'`; `AZ11`: `'Mức hưởng = thời gian tính thưởng/365 * định mức'` |
| BE | LƯƠNG THÁNG 13 | `BE10`: `'Lương bình quân 12 tháng liền kề'`; `BE11`: `'Mức hưởng = thời gian tính thưởng/365 * định mức'` |
| BT | TỔNG THU NHẬP TRONG THÁNG | `BT10`: `'cộng hết thu nhập'` |
| BU | TỔNG THU NHẬP CHỊU THUẾ | `BU10`: `'cộng hết thu nhập chịu thuế'` |
| BV | BHXH (NLĐ) | `BV10`: `'=8%* lương bhxh'`; `BV11`: `'--NS chính thức'`; `BV12`: `'số ngày thử việc, ko lương, thai sản ...>=14 ngày tính từ 1- cuối tháng --ko đóng bhxh'` |
| BY | BHYT (NLĐ) | `BY10`: `'=1.5%* lương bhxh'`; `BY11`: `'--NS chính thức'` |
| BZ | BHTN (NLĐ) | `BZ10`: `'=1%* lương BHTN'`; `BZ11`: `'--NS chính thức'` |
| CE | GIẢM TRỪ GIA CẢNH | `CE10`: `'Bản thân: 15.5 tr'`; `CE11`: `'NPT: 6.2 tr/người'` |
| CH | THUẾ TNCN | `CH10`: `'Thử việc:'` (bỏ dở, không có công thức); `CH11`: `'VN 10% * tổng TN'`; `CH12`: `'NNN 20% * tổng TN'`; `CH14`: `'Chính thức: theo thu nhập chịu thuế * biểu lũy tiến'` |
| CQ | PHÍ CÔNG ĐOÀN 0.5% | `CQ10`: `'=0.5%* lương bhxh, tối đa 234k'`; `CQ11`: `'--NS chính thức'` |
| DA | BHXH (Cty) | `DA10`: `'=17%* lương bhxh'`; `DA11`: `'--NS chính thức'` |
| DC | BHTNLĐ-BNN (Cty) | `DC10`: `'=0.5%* lương bhxh'`; `DC11`: `'--NS chính thức'` |
| DE | **nhãn cột ghi "BHYT"** (Cty) | `DE10`: `'=1%* lương BHTN'` ← **công thức ghi trong ô không khớp nhãn cột "BHYT"** |
| DF | **nhãn cột ghi "Đ/C BHYT"** | `DF10`: `'=3%* lương bhxh'` ← đây mới đúng công thức BHYT 3% |
| DG | **nhãn cột ghi "BHTN"** (Cty) | `DG10`: `'=1%* lương BHTN'` |
| DJ | 2% KPCĐ | `DJ10`: `'=2%* lương bhxh'`; `DJ11`: `'--NS chính thức'` |
| DP | Trích Du lịch | `DP10`: `'Ngày hưởng lương>0, 6tr : 12'` |
| DT | Trích thưởng KPIs | `DT10`: `'Ngày hưởng lương>0, lương HĐLD/Lương TV * 3 : 12'` |
| DU | Trích Lương tháng 13 | `DU10`: `'Ngày hưởng lương>0, lương HĐLD/Lương TV : 12'` |
| DV | Trích thưởng Âm lịch | `DV10`: `'Ngày hưởng lương>0, nếu lương HĐLD/Lương TV>15tr, 15tr: 12, lương HĐLD/Lương TV :12'` |

---

## 2. Cấu hình hệ thống hiện tại (`salary_components`, 148 dòng — trích các code liên quan mục 1)

Trích nguyên văn cột `formula` từ `salary_components` (bảng đang được engine đọc thật):

```
INS_SAL_BH        = IF(AND([CONTRACT_TYPE]=="Chính thức", [HAS_SECOND_CONTRACT]==0), MIN([CONTRACT_TOTAL], 50600000), 0)
INS_SAL_UI        = IF(AND([CONTRACT_TYPE]=="Chính thức", [IS_FOREIGNER]==0, [HAS_SECOND_CONTRACT]==0), MIN([CONTRACT_TOTAL], 106200000), 0)
PROB_EARNED       = [PROB_DAYS] * [BASIC_SAL] * 0.85 / [STD_DAYS]
OFFICIAL_EARNED   = ([PAID_DAYS] - [PROB_DAYS]) * [BASIC_SAL] / [STD_DAYS]
RESP_EARNED       = [PAID_DAYS] * [RESP_SAL] / [STD_DAYS]
EARNED_PAID_LEAVE = IF([CONTRACT_TYPE]=="Chính thức", [PAID_LEAVE_BALANCE_DAYS] / [STD_DAYS] * [BASIC_SAL], 0)
EARNED_SAL        = [PROB_EARNED] + [OFFICIAL_EARNED] + [RESP_EARNED] + [EARNED_PAID_LEAVE]
MEAL_ALLOW        = [MEALS_TOTAL] * 45000
MEAL_NONTAX       = MIN([MEAL_ALLOW], 730000)
MEAL_TAX          = MAX(0, [MEAL_ALLOW] - 730000)
FUEL_ALLOW        = (input, không có formula)
TRANSPORT_TAX     = [TRANSPORT_ALLOW] + [TRIP_OVERRIDE]
TRANSPORT_NONTAX  = (input, không có formula)
OTHER_ALLOW_TAX   = (input, không có formula)
PHONE_NONTAX      = MIN([PHONE_ALLOW], 400000)
PHONE_TAX         = MAX(0, [PHONE_ALLOW] - 400000)
OT_TAX            = 0                              ← formula literally = hằng số 0
OT_NONTAX         = (input, không có formula)
BONUS_TET / BONUS_13M / BONUS_SAVE_TRAVEL / BONUS_SAVE_KPI / BONUS_SAVE_13M / BONUS_SAVE_TET
                  = (đều là input, không có formula/công thức nào)
GROSS             = [EARNED_SAL] + [MEAL_TAX] + [MEAL_NONTAX] + [PHONE_TAX] + [PHONE_NONTAX] + [FUEL_ALLOW] + [FUEL_NONTAX]
                    + [TRANSPORT_TAX] + [TRANSPORT_NONTAX] + [LIVING_ALLOW] + [LIVING_NONTAX] + [OTHER_ALLOW_TAX]
                    + [OTHER_ALLOW_NONTAX] + [OT_TAX] + [OT_NONTAX] + [BONUS_TOTAL] + [TOTAL_SUPPORT] + [ADJ_PLUS] - [ADJ_MINUS]
TAXABLE_GROSS     = [GROSS] - [MEAL_NONTAX] - [PHONE_NONTAX] - [FUEL_NONTAX] - [TRANSPORT_NONTAX] - [LIVING_NONTAX]
                    - [OTHER_ALLOW_NONTAX] - [OT_NONTAX] - [SEVER_ALLOW] - [SI_BENEFIT] - [BONUS_TRAVEL] - [HEALTH_INS]
SI_EMP            = [INS_SAL_BH] * 0.08
HI_EMP            = [INS_SAL_BH] * 0.015
UI_EMP            = [INS_SAL_UI] * 0.01
PERSONAL_DED      = 15500000                        (hằng số)
DEPENDENT_DED     = [DEPENDENT_CNT] * 6200000
PIT               = IF([EMP_TYPE]=="Intern", IF([HAS_TAX_COMMITMENT]==1, 0, IF([TAXABLE_INC]>5000000, 0.1*[TAXABLE_INC], 0)),
                       IF(AND([CONTRACT_TYPE]=="Thử việc", [IS_FOREIGNER]==1), 0.2*[TAXABLE_INC],
                          ROUND(MAX(0.05*[TAXABLE_INC], 0.10*[TAXABLE_INC]-500000, 0.20*[TAXABLE_INC]-3500000,
                                    0.30*[TAXABLE_INC]-9500000, 0.35*[TAXABLE_INC]-14500000), 0)))
UNION_FEE         = MIN([INS_SAL_BH] * 0.005, 253000)
SI_CTY            = [INS_SAL_BH] * 0.17
TNLD_CTY          = [INS_SAL_BH] * 0.005
HI_CTY            = [INS_SAL_BH] * 0.03
UI_CTY            = [INS_SAL_UI] * 0.01
KPCD_CTY          = [INS_SAL_BH] * 0.02
```

---

## 3. Đối chiếu chi tiết

Ký hiệu: ✅ Khớp · ⚠️ Lệch công thức/số · 🕳️ Thiếu điều kiện/rule trong hệ thống · ➕ Hệ thống thêm điều kiện không có trong Excel gốc · 📝 Chỉ là lỗi nhãn cột trong Excel, không phải lỗi hệ thống

### 3.1 ✅ Mức trần bảo hiểm (khớp)
- Excel `R10`: `'Mức trần 50,600,000'` ↔ DB `INS_SAL_BH`: `MIN([CONTRACT_TOTAL], 50600000)` — khớp.
- Excel `S10`: `'Mức trần 106,200,000'` ↔ DB `INS_SAL_UI`: `MIN([CONTRACT_TOTAL], 106200000)` — khớp.

### 3.2 🕳️ `AH11` — Bổ nhiệm/tăng lương giữa kỳ: hệ thống THIẾU
- Excel `AH11`: `'Bổ nhiệm: nếu có 2 mức lương khác nhau trong kỳ lương thì tính theo 2 gdoan'`.
- DB `OFFICIAL_EARNED = ([PAID_DAYS] - [PROB_DAYS]) * [BASIC_SAL] / [STD_DAYS]` — dùng **đúng một** giá trị `BASIC_SAL` duy nhất cho cả kỳ, không có cơ chế tách 2 giai đoạn theo ngày hiệu lực quyết định. Nhân viên được bổ nhiệm/tăng lương giữa kỳ sẽ bị tính sai (dùng 1 trong 2 mức lương cho toàn bộ số ngày, thay vì chia theo từng giai đoạn).

### 3.3 ➕ `AJ10` — Lương phép tồn: hệ thống thêm điều kiện Excel không có
- Excel `AJ10`: `'=ngày phép tồn/ngày công chuẩn * Mức lương'` — không nêu điều kiện loại hợp đồng.
- DB `EARNED_PAID_LEAVE = IF([CONTRACT_TYPE]=="Chính thức", [PAID_LEAVE_BALANCE_DAYS] / [STD_DAYS] * [BASIC_SAL], 0)` — **chỉ trả cho nhân viên "Chính thức"**, nhân viên thử việc luôn = 0 dù công thức Excel không loại trừ trường hợp này.

### 3.4 🕳️ `AL`/`AR` — Phụ cấp cơm theo địa điểm: hệ thống THIẾU
- Excel `AL11`/`AR11`: `'vp: 1b/ngày, site <30km: 2b/ngày, site >=30km: 3b/ngày'`.
- DB: `MEAL_ALLOW = [MEALS_TOTAL] * 45000` — `MEALS_TOTAL` là trường **nhập tay** (input), không có công thức nào tự tính số bữa theo địa điểm (VP/site <30km/site ≥30km). Phần trừ mức miễn 730k thì khớp đúng (`MEAL_NONTAX = MIN(MEAL_ALLOW,730000)`, `MEAL_TAX = MAX(0, MEAL_ALLOW-730000)` — khớp `AL12`/`AR12`).

### 3.5 ⚠️🕳️ `AS10` — PC điện thoại (không chịu thuế): lệch CẢ công thức lẫn điều kiện
- Excel `AS10`: `'Theo level, lưu ý số ngày đi làm thực tế dưới 14 (mười bốn) ngày, phụ cấp được tính theo tỷ lệ ngày làm việc thực tế và ngày nghỉ lễ trong tháng'` — mức miễn thuế phải **theo cấp bậc (level)** nhân viên, và **chia tỷ lệ nếu đi làm <14 ngày**.
- DB `PHONE_NONTAX = MIN([PHONE_ALLOW], 400000)` — dùng **một mức trần cố định 400.000đ cho mọi level**, và **không có** phép chia tỷ lệ theo ngày công <14. Cả 2 điều kiện Excel yêu cầu đều không có trong công thức.

### 3.6 🕳️ `AO10`/`AU10` — PC đi lại (chịu thuế & không chịu thuế): thiếu rule <14 ngày
- Excel `AO10`/`AU10`: cùng câu `'... lưu ý số ngày đi làm thực tế dưới 14 (mười bốn) ngày, phụ cấp được tính theo tỷ lệ ngày làm việc thực tế và ngày nghỉ lễ trong tháng'`.
- DB: `TRANSPORT_TAX = [TRANSPORT_ALLOW] + [TRIP_OVERRIDE]` (cộng thẳng, không chia tỷ lệ ngày công); `TRANSPORT_NONTAX` là input tay, không có công thức. → Rule "trùm" này (áp cho cả PC điện thoại, đi lại, NL/xăng theo `AN`/`AO`/`AS`/`AU`) chưa xuất hiện ở bất kỳ công thức nào trong `salary_components`.

### 3.7 ⚠️ `AY10`/`AY11` — Tăng ca: `OT_TAX` bị khoá cứng = 0
- Excel `AY10`: `'chủ nhật 200%'`; `AY11`: `'... trả thêm 100% tiền lương ...'` — có hệ số OT theo loại ngày.
- DB `OT_TAX`: type = `formula`, cột `formula` = literal `"0"` — **luôn trả về 0 bất kể số giờ tăng ca**, không có bất kỳ hệ số 200%/100% nào. `OT_NONTAX` là input tay (không công thức). Đây là khoảng trống nặng nhất trong nhóm tăng ca — không chỉ "chưa có hệ số", mà bản thân `OT_TAX` bị chặn cứng về 0.

### 3.8 🕳️ `AZ10`/`BE10` — Thưởng Tết Âm lịch & Lương tháng 13: hệ thống THIẾU công thức bình quân
- Excel `AZ10`: `'Lương bình quân 12 tháng liền kề, ko quá 15 triệu'`; `AZ11`/`BE11`: `'Mức hưởng = thời gian tính thưởng/365 * định mức'`.
- DB: `BONUS_TET`, `BONUS_13M` đều là **input** (không có `formula`), và `AVG_SALARY_12M` (lương bình quân 12 tháng) tuy có tồn tại như một component riêng nhưng **cũng là input** — không có công thức nào tự tính bình quân 12 tháng liền kề hay chia theo 365 ngày. Hai khoản này hiện hoàn toàn phụ thuộc nhập tay.

### 3.9 🕳️ `BV12` — Điều kiện nghỉ ≥14 ngày không đóng BHXH: hệ thống THIẾU
- Excel `BV12`: `'số ngày thử việc, ko lương, thai sản ...>=14 ngày tính từ 1- cuối tháng --ko đóng bhxh'` — theo luật BHXH, nhân viên **chính thức** nhưng nghỉ không lương/thai sản/... **≥14 ngày trong tháng** thì tháng đó không đóng BHXH.
- DB `INS_SAL_BH = IF(AND([CONTRACT_TYPE]=="Chính thức", [HAS_SECOND_CONTRACT]==0), MIN([CONTRACT_TOTAL], 50600000), 0)` — chỉ xét loại hợp đồng + có hợp đồng thứ 2 hay không, **không xét số ngày nghỉ trong tháng**. Nhân viên chính thức nghỉ không lương/thai sản cả tháng vẫn bị tính đóng BHXH như bình thường theo công thức hiện tại.

### 3.10 ⚠️ `CQ10` — Phí công đoàn: lệch mức trần (số cụ thể)
- Excel `CQ10`: `'=0.5%* lương bhxh, tối đa 234k'`.
- DB `UNION_FEE = MIN([INS_SAL_BH] * 0.005, 253000)` — trần **253.000đ**, khác **234.000đ** ghi trong Excel. (253.000đ khớp mức trần đoàn phí hiện hành theo lương cơ sở mới — số Excel 234k nhiều khả năng là số cũ; đây chỉ là ghi nhận sai lệch, KHÔNG kết luận số nào đúng — cần HR xác nhận theo đúng yêu cầu chỉ-đọc).

### 3.11 📝 `DE10`/`DF10`/`DG10` — Nhãn cột BHYT/BHTN doanh nghiệp trong Excel bị lệch, DB đúng
- Excel: cột có nhãn **"BHYT"** (`DE`) lại ghi công thức `DE10='=1%* lương BHTN'`; cột có nhãn **"Đ/C BHYT"** (`DF`) mới ghi đúng công thức BHYT `DF10='=3%* lương bhxh'`.
- DB: `HI_CTY` (BHYT Cty 3%) `= [INS_SAL_BH] * 0.03`; `UI_CTY` (BHTN Cty 1%) `= [INS_SAL_UI] * 0.01` — **DB đúng theo tỷ lệ luật định (BHYT DN 3%, BHTN DN 1%)**, độ lệch nằm ở việc Excel gốc đặt nhãn cột nhầm chỗ (đã biết từ trước, không phải lỗi hệ thống). Ghi nhận để không map nhầm cột nếu đối chiếu lại sau này.

### 3.12 ⚠️ `CH11`/`CH12` — Thuế TNCN thử việc: khác cơ sở tính + khác nhánh áp dụng
- Excel: `CH10` bỏ dở (`'Thử việc:'` không có công thức theo sau); `CH11`: `'VN 10% * tổng TN'` (thử việc người Việt: 10% × **tổng thu nhập**); `CH12`: `'NNN 20% * tổng TN'` (thử việc người nước ngoài: 20% × **tổng thu nhập**); `CH14`: `'Chính thức: theo thu nhập chịu thuế * biểu lũy tiến'`.
- DB `PIT`: nhánh thử việc + là người nước ngoài (`IS_FOREIGNER==1`) → `0.2*[TAXABLE_INC]`; **thử việc người Việt không nằm trong nhánh riêng nào** — rơi thẳng vào nhánh `else` (biểu luỹ tiến 5 bậc, giống nhân viên chính thức), **không phải 10% như Excel `CH11` ghi**. Ngoài ra cả 2 nhánh 20%/luỹ tiến trong DB đều dùng `TAXABLE_INC` (thu nhập **tính thuế**, đã trừ bảo hiểm/giảm trừ), trong khi Excel ghi rõ là `× tổng TN` (thu nhập **chưa trừ** gì) — khác cơ sở tính, không chỉ khác tỷ lệ.

### 3.13 ✅ Giảm trừ gia cảnh (khớp chính xác)
- Excel `CE10`: `'Bản thân: 15.5 tr'` ↔ DB `PERSONAL_DED = 15500000` — khớp.
- Excel `CE11`: `'NPT: 6.2 tr/người'` ↔ DB `DEPENDENT_DED = [DEPENDENT_CNT] * 6200000` — khớp.

### 3.14 ✅ Bảo hiểm NLĐ + DN theo tỷ lệ (khớp)
`BV10` 8%↔`SI_EMP`; `BY10` 1.5%↔`HI_EMP`; `BZ10` 1%↔`UI_EMP`; `DA10` 17%↔`SI_CTY`; `DC10` 0.5%↔`TNLD_CTY`; `DJ10` 2%↔`KPCD_CTY` — tất cả khớp đúng tỷ lệ %, và điều kiện `'--NS chính thức'` (chỉ áp cho nhân viên chính thức) đã được đảm bảo gián tiếp vì `INS_SAL_BH`/`INS_SAL_UI` = 0 khi không phải "Chính thức".

### 3.15 🕳️ `DP10`/`DT10`/`DU10`/`DV10` — Khoản trích trước thưởng: không có công thức trong DB để đối chiếu số
- Excel ghi rõ định mức + điều kiện: `DP10` (Du lịch, 6tr/12, điều kiện ngày hưởng lương>0), `DT10`/`DU10`/`DV10` tương tự cho KPIs/Lương 13/Tết.
- DB: `BONUS_SAVE_TRAVEL`, `BONUS_SAVE_KPI`, `BONUS_SAVE_13M`, `BONUS_SAVE_TET` đều là **input**, không có `formula` — bảng `salary_components`/`salary_formula_configs` **không lưu bất kỳ hằng số định mức (6tr/năm, hệ số ×3...) hay điều kiện nào** cho các khoản này. → Không thể kết luận khớp/lệch số tại tầng DB; nếu định mức này nằm trong code Go (không phải DB) thì nằm ngoài phạm vi đối chiếu DB của lần rà soát này.

### 3.16 (không kết luận được) `BT10`/`BU10` — "cộng hết thu nhập" / Điều chỉnh trừ lương
- Excel `BT10`/`BU10` chỉ ghi vắn tắt `'cộng hết thu nhập'` / `'cộng hết thu nhập chịu thuế'`, không liệt kê chi tiết từng khoản — không đủ cơ sở để đối chiếu từng số hạng trong công thức `GROSS`/`TAXABLE_GROSS` của DB.
- Riêng một điểm có thể xác minh: công thức `GROSS` hiện tại trong DB là `... + [ADJ_PLUS] - [ADJ_MINUS]` — tức **trừ** đúng khoản `ADJ_MINUS` (Điều chỉnh trừ lương), không phải cộng. Đây là ghi nhận thời điểm 19/08/2026 — nếu có tài liệu nào khác (ví dụ báo cáo `Questions-draft` trong file này, mục câu hỏi số 24) từng ghi nhận việc này đang bị "cộng nhầm", thì tại DB hiện tại **không thấy hiện tượng đó** nữa; không rõ đã được sửa từ trước hay câu hỏi đó ám chỉ một bản "cây tính lương" khác không có trong DB này. Cần hỏi lại HR/đội kỹ thuật để biết chắc, không tự kết luận.

---

## 4. Tổng kết theo loại sai lệch

| Loại | Số mục | Danh sách |
|---|---|---|
| ✅ Khớp | 6 nhóm | Trần BHXH/BHTN (3.1), PC cơm phần trừ 730k (3.4 phần sau), Giảm trừ gia cảnh (3.13), 6 khoản bảo hiểm theo % (3.14), nhãn BHYT/BHTN DN đúng bản chất dù Excel ghi nhãn sai (3.11) |
| 🕳️ DB thiếu rule Excel có | 6 mục | Bổ nhiệm 2 giai đoạn (3.2), PC cơm theo địa điểm (3.4), <14 ngày cho PC đi lại (3.6), hệ số OT theo loại ngày (3.7), công thức bình quân 12 tháng cho 2 khoản thưởng (3.8), điều kiện nghỉ ≥14 ngày không đóng BHXH (3.9) |
| ⚠️ Lệch công thức/số | 4 mục | PC điện thoại không chịu thuế — theo level vs trần cố định 400k (3.5), OT_TAX khoá cứng = 0 (3.7 — vừa thiếu vừa lệch), trần phí công đoàn 234k vs 253k (3.10), cơ sở/nhánh tính thuế TNCN thử việc (3.12) |
| ➕ DB thêm điều kiện Excel không có | 1 mục | Lương phép tồn chỉ trả nhân viên chính thức (3.3) |
| 📝 Lỗi nhãn cột trong Excel (không phải lỗi DB) | 1 mục | Cột "BHYT"/"Đ/C BHYT"/"BHTN" doanh nghiệp bị đặt nhãn lệch với công thức ghi trong ô (3.11) |
| Không đủ dữ liệu để kết luận | 2 mục | Định mức trích trước thưởng (3.15 — số liệu không nằm trong DB), danh sách chi tiết "cộng hết thu nhập" (3.16) |
| Phát hiện cấu trúc (không phải 1 công thức cụ thể) | 1 mục | Bảng `salary_formula_configs` là bảng mồ côi, không repo nào đọc, chứa số liệu luật cũ/khác — xem mục 0 |

---

## 5. Việc CHƯA làm / giới hạn của báo cáo này

- Không gọi được `GET /api/v1/config/salary-components` qua HTTP thật (thiếu cơ chế đăng nhập hợp lệ trong phiên đọc-only này) — đã dùng DB trực tiếp thay thế, cùng nguồn dữ liệu nên kết luận không đổi.
- Chưa đối chiếu hết 148/148 component — chỉ đối chiếu các cột có công thức/rule text tường minh trong Excel (mục 1). Nhiều component còn lại trong DB (ví dụ `SEVER_ALLOW`, `SI_REGIME`, `OTHER_POST_ADD`...) không có ô công thức tương ứng rõ ràng trong Excel được cung cấp (chỉ có nhãn cột ở `Core System template`/dòng 7, không có rule text) — cần thêm dữ liệu Excel (hoặc HR bổ sung) nếu muốn rà hết.
- Không đọc code Go (engine tính lương) — chỉ đối chiếu tầng cấu hình DB, đúng phạm vi được giao. Một số nghi vấn (mục 3.15 — định mức trích thưởng) có thể chỉ nằm trong code, không nằm trong DB.
- **Không sửa bất kỳ công thức/DB/config nào** — đúng yêu cầu "chỉ đọc" của phiên này.
