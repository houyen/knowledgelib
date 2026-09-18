---
id: self-docs/engine/adapter-workday-salary-rules-data-request
canonical_question: 'Technical guide and specification: Yêu cầu dữ liệu gửi đội Adapter
  — cụm rule lương Giai đoạn 2'
aliases:
- Yêu cầu dữ liệu gửi đội Adapter — cụm rule lương Giai đoạn 2
- Adapter Workday Salary Rules Data Request 210826
entity_type: how_to
domain: self-docs > engine
last_verified: 2026-09-17
---

# Yêu cầu dữ liệu gửi đội Adapter — cụm rule lương Giai đoạn 2 (OT, bổ nhiệm, PC theo bộ phận/level)

**Ngày:** 21/08/2026 ·  **Mục đích:** làm SONG SONG với backend — backend viết công thức trước theo tên trường tự đặt (xem mục "Contract" cuối file), đội adapter đồng bộ đúng dữ liệu Workday map vào các trường đó, sau đó 2 bên ngồi lại ghép code.

**Nguồn tham khảo đã có sẵn** (nhiều phần đã có XPath thật): `CTD_REPORT WORKDAY - ABSENCE & TIME TRACKING.xlsx` sheet `Monthly Attendance Report300726` (dòng 5=report nguồn, dòng 7=cách tính, dòng 9=XPath), và `self-docs/list_ques_main-answer.md` (câu trả lời HR/functional đã có, 19/08–21/08).

## Cập nhật 21/08/2026 — Trạng thái phía Backend + câu hỏi mới phát sinh

**Backend đã thi hành xong phần của mình** (Task 1-4 của `llmwiki/wiki/sources/draft/210826-Core System-be-attendance-segments-PLAN.md`, đã merge vào `release/uat-180826`, build/test xanh, **chưa push**): bảng contract, hàm tính PC cơm/6 phụ cấp/OT, 12 component mới — nhưng **CHƯA nối vào `GROSS`/phiếu lương thật**. Mục "Contract phía Backend" cuối file đã cập nhật thành tên bảng/cột **CHÍNH THỨC** (không còn "có thể đổi").

**Lý do chưa kích hoạt — quan trọng, đội adapter cần biết để ước lượng đúng mốc thời gian:** không phải chỉ chờ trả lời hết câu hỏi, mà là **chờ có DÒNG DỮ LIỆU THẬT** trong bảng `attendance_department_segments`. Công thức đã viết xong và test bằng số giả — nhưng nếu nối vào `GROSS` trước khi adapter thật sự đồng bộ, mọi nhân viên sẽ bị tính **0đ** cho các khoản này (bảng đang trống hoàn toàn), tức xoá sạch phụ cấp thật trên phiếu lương. Nên: **xin đội adapter cho biết mốc dự kiến pipeline thật chạy được** (câu 7 dưới đây) để backend biết khi nào an toàn để kích hoạt.

Câu hỏi mới, gộp thêm vào danh sách bên dưới:

**7. (MỚI) Mốc thời gian dự kiến pipeline đồng bộ thật chạy được** — không cần chính xác, chỉ cần ước lượng (tuần/tháng) để backend lên lịch bước "kích hoạt" (mục Adapt-checklist bước 5, `self-docs/files/ADAPT-CHECKLIST-attendance-segments-210826.md`).

**8. (MỚI, ưu tiên cao — chặn cả nhóm OT)** Xác nhận lại mục 1b bên dưới: OT ca đêm (`OT_WD_NIGHT`/`OT_WE_NIGHT`/`OT_HLD_NIGHT`) — đã hỏi 19/08 nhưng câu trả lời 21/08 (`list_ques_main-answer.md` câu 3) chỉ xác nhận `Cash_1x/2x/3x` (3 loại "normal"), **chưa nhắc gì tới ca đêm**. Cần xác nhận dứt điểm: có tag nào khác trong `Get_Calculated_Time_Blocks` cho ca đêm không, hay Workday hiện KHÔNG tách lương OT ca đêm — nếu không tách, báo ngay để backend/HR quyết định hướng khác (không chờ thêm).

---

## 1. OT 

Backend đã có sẵn bảng hệ số `ot_multiplier_configs` với đúng 6 mã: `OT_WD_NORMAL` (1.50), `OT_WD_NIGHT` (2.00), `OT_WE_NORMAL` (2.00), `OT_WE_NIGHT` (2.70), `OT_HLD_NORMAL` (3.00), `OT_HLD_NIGHT` (3.70).

**1a. Đã có nguồn cho 3 loại "normal" (ngày thường/nghỉ/lễ):**
Workday `Time_Tracking → Get_Calculated_Time_Blocks`, lọc `Status_Reference/ID[@type='Time_Tracking_Set_Up_Option_ID']='APPROVED'`, theo tag `Calculation_Tag_Reference/ID[@type='Time_Calculation_Tag_ID']`:

- `Cash_1x` → OT ngày thường (155 tương ứng `OT_WD_NORMAL`)
- `Cash_2x` → OT ngày nghỉ (`OT_WE_NORMAL`)
- `Cash_3x` → OT ngày lễ (`OT_HLD_NORMAL`)
- Đơn vị trả về là `Calculated_Quantity` (unit — cần xác nhận lại đơn vị chính xác là giờ hay ngày, xem mục 5).

**1b. CHƯA có nguồn — cần đội adapter tìm hoặc xác nhận không tồn tại:**
3 mã OT ca đêm (`OT_WD_NIGHT`, `OT_WE_NIGHT`, `OT_HLD_NIGHT`) — quét toàn bộ file field-mapping hiện có KHÔNG tìm thấy tag nào cho hệ số OT ca đêm (chỉ có `Night_Meal` — đó là phụ cấp cơm ca đêm, KHÔNG phải hệ số lương OT đêm, đừng nhầm 2 cái này).
**Việc cần làm:** kiểm trong Workday xem `Get_Calculated_Time_Blocks` có tag nào khác cho ca đêm không (gợi ý: có thể có mẫu `Cash_1x_Night`/`Night_OT` hoặc tag khác chưa xuất hiện trong sample cũ), hoặc hỏi trực tiếp RA/Workday functional consultant. Nếu xác nhận Workday KHÔNG tách riêng ca đêm, cần báo lại để backend/HR quyết định hướng khác (ví dụ tính ca đêm dựa vào giờ làm thực tế từ report khác, không qua tag).

## 2. Bổ nhiệm/tăng lương + điều động giữa kỳ (nhiều bộ phận trong 1 kỳ)

Nguồn đã xác nhận:

- `**Enterprise - Compensation Changes Report**` — định mức lương/phụ cấp thay đổi theo bộ phận + ngày hiệu lực.
- `**Enterprise - List Detail of Work History**` — đối chiếu lịch sử công tác.
- Cột `ts_worker_organization_change_diff` → tách "Departments[segment]" theo ngày đổi bộ phận, tính đoạn ngày kiểu `21/n → 20/n+1`.

**Việc cần làm:** đồng bộ 2 report trên, và **tính sẵn các "segment" theo bộ phận trong kỳ lương** (tối đa 4 segment/kỳ theo mẫu file gốc) — mỗi segment cần: mã bộ phận, ngày bắt đầu/kết thúc trong kỳ, ngày công chuẩn tại bộ phận đó, các định mức phụ cấp hiệu lực tại bộ phận đó (điện thoại, ô tô, nhiên liệu, đi lại, cơm, duyệt riêng, đặc biệt). **Không đẩy raw event, đẩy đã cắt sẵn theo segment** — backend sẽ đọc theo segment, không tự cắt.

## 3. PC cơm theo bộ phận

- Công thức: `định mức cơm bộ phận (VND) / 45.000 = số bữa/ngày tại bộ phận đó`.
- "Số ngày tính bữa ăn" có quy tắc riêng: VP nghỉ thứ 7 không tính cơm (5 ngày/tuần); Công trường (CT) thứ 7 vẫn tính (6 ngày/tuần); luôn bỏ ngày nghỉ lễ.
- Cộng thêm bữa khi đi làm ngày lễ/Chủ nhật qua tag `Sunday_Meal`/`Night_Meal` (cũng qua `Get_Calculated_Time_Blocks`).
- Một ngày có thể mang nhiều tag cùng lúc, cần quy đổi phức hợp (ví dụ: ngày lễ Cash_2x ⇒ quy đổi Cash_1x + Off_in_Lieu_1x = 1) — **cần đội adapter xác nhận rõ toàn bộ bảng quy đổi tổ hợp tag** (hiện chỉ có 1 ví dụ, chưa đủ để code tổng quát).

**Việc cần làm:** đồng bộ định mức cơm theo bộ phận (từ Compensation Changes Report, mục 2) + lịch làm việc theo ngày/bộ phận (schedule) + toàn bộ tag `Sunday_Meal`/`Night_Meal`/`Cash_*`/`Off_in_Lieu_*` mỗi ngày, kèm bảng quy đổi tổ hợp tag đầy đủ.

## 4. PC điện thoại/ô tô/nhiên liệu/đi lại/duyệt riêng/đặc biệt theo bộ phận + rule &lt;14 ngày

Công thức đã xác nhận (áp dụng đều cho **6 loại phụ cấp** trên, theo từng bộ phận/segment):

```
định mức phụ cấp tại bộ phận đó (mục 2)
Nếu (Tổng ngày công đi làm - phụ cấp) < 14:
    phụ cấp = (ngày công đi làm + ngày nghỉ lễ tại bộ phận đó) / ngày công chuẩn tại bộ phận đó × định mức
Ngược lại: tính theo tỷ lệ bình thường (ngày hưởng phụ cấp / ngày công chuẩn bộ phận × định mức)
```

Riêng PC điện thoại còn có rule thuế: nếu PC ≥ mức trần (theo level, WD cung cấp) → phần vượt trần chịu thuế; nếu ≤ mức trần → không chịu thuế toàn bộ (cấu trúc này backend ĐÃ có sẵn, chỉ cần đổi nguồn mức trần).

**Việc cần làm:** đồng bộ bảng tra level → mức trần PC điện thoại từ Workday; đồng bộ "ngày công chuẩn tại từng bộ phận" (không phải ngày công chuẩn chung cả kỳ) theo đúng ý N7 trong file gốc (VP thứ 7 = 1/2 ngày, CT thứ 7 = 1 ngày).

## 5. Xác nhận đơn vị dữ liệu (quan trọng, ảnh hưởng công thức)

`Calculated_Quantity` trả về từ `Get_Calculated_Time_Blocks` — cần đội adapter xác nhận rõ: đơn vị là **GIỜ** hay **NGÀY** cho từng tag (`Actual_Working_Day`, `Paid_Holiday`, `Cash_1x/2x/3x`...). Ghi chú cũ (`AR9`/`AS9` trong file gốc) có đoạn `div 8` cho OT Plan (giờ → ngày), gợi ý ít nhất một số tag trả về theo GIỜ — cần xác nhận từng tag một, không giả định đồng nhất.

## 6. Lương bình quân 12 tháng (thưởng Tết Âm lịch, Lương tháng 13)

Chưa có report/API nào được xác nhận (cả HR và file field-mapping đều chưa có). **Việc cần làm:** tìm trong Workday report/API nào cho "lương bình quân N tháng liền kề" của nhân viên — nếu Workday không có sẵn, báo lại để backend tự lưu lịch sử lương theo kỳ và tính (khác hướng, cần quyết định lại).

---

## Contract phía Backend — ĐÃ CHỐT tên bảng/cột (cập nhật 21/08, thay cho bản nháp cũ)

Bảng `attendance_department_segments` (Postgres, `internal/database/database.go` migration CB) —
**mỗi dòng = 1 (nhân viên, kỳ lương, số thứ tự bộ phận trong kỳ)**, tối đa 4 dòng/kỳ nếu nhân viên
đổi bộ phận. Khoá: `(emp_code, attendance_month, segment_no)`. Đội adapter ghi/upsert trực tiếp
(hoặc qua API sync sẽ thống nhất sau) vào đúng các cột sau:

| Cột | Kiểu | Nguồn (theo mục tương ứng ở trên) |
|---|---|---|
| `emp_code` | text | Mã nhân viên |
| `attendance_month` | date | Ngày đầu kỳ lương (VD kỳ 21/5-20/6 → `2026-06-01`) |
| `segment_no` | int | 1..4, tăng dần theo thứ tự bộ phận trong kỳ |
| `department_code`, `start_date`, `end_date` | text/date | Mục 2 |
| `std_days_at_dept`, `actual_work_days`, `holiday_days`, `paid_leave_days` | numeric | Mục 2, 4 |
| `meal_allowance_vnd`, `meal_days_eligible`, `sunday_meal_units`, `night_meal_units` | numeric | Mục 3 |
| `phone_allowance_vnd`, `phone_cap_vnd`, `fuel_allowance_vnd`, `transport_allowance_vnd`, `trip_override_vnd`, `special_allowance_vnd` | numeric | Mục 4 |
| `ot_weekday_normal_units` (← `Cash_1x`), `ot_weekend_normal_units` (← `Cash_2x`), `ot_holiday_normal_units` (← `Cash_3x`) | numeric | Mục 1a |
| `ot_weekday_night_units`, `ot_weekend_night_units`, `ot_holiday_night_units` | numeric | Mục 1b — **để 0 cho tới khi có nguồn** (câu 8) |

Đây là hợp đồng đã code xong phía backend (không còn thay đổi tên trừ khi có lý do mạnh) — đội
adapter có thể bắt đầu code theo đúng tên cột này ngay, không cần chờ thêm xác nhận từ backend.