---
id: self-docs/engine/list-ques-main-answer
canonical_question: 'Technical guide and specification: List Ques Main Answer'
aliases:
- List Ques Main Answer
entity_type: how_to
domain: self-docs > engine
last_verified: 2026-06-21
---

### A. Cụm OT

**Core System tự tính**

1. Dữ liệu chấm công hiện có (Workday) có breakdown đúng 6 loại giờ OT (thường/nghỉ/lễ × ngày/đêm) không, hay chỉ có tổng giờ OT chung? Nếu chỉ có tổng, nguồn lịch ngày lễ để Core System tự phân loại lấy ở đâu?

- OT*-\_Actual*(Cash*&\_Off_In_Lieu) | Sunday_Meal | Night_Meal | OT*-_Actual_(Cash) | -> Đang chờ confirm

2. Cách tách phần chịu thuế/không chịu thuế của tiền OT theo đúng luật thuế TNCN hiện hành cho lương làm thêm giờ

-

3. Hệ số 150%/200%/300% + phụ cấp ca đêm 30% có đúng mức công ty đang áp dụng không, hay công ty có thoả ước lao động tập thể cao hơn? (Excel `AY11` ghi "trả thêm 100%" cho ngày lễ — cần đối chiếu lại cách diễn đạt này có khớp 300% hay không).

- Với thông tin này dã được calculated qua các rules (eligible) của WD có trong Time_Tracking lấy nhưng phần được APPROVED
- Time_Tracking>Get_Calculated_Time_Blocks>Calculated_Time_Block_Response_Data>Calculated_Time_Block_Data>Calculation_Tag_Reference>Time_Calculation_TagObject>Time_Calculation_Tag_ID = "Cash_1x" | "Cash_2x" | "Cash_3x" đơn vị là unit, khi tính tổng thì cần thêm số tỉ lệ với Calculated_Quantity

### B. Cụm bổ nhiệm 2 mức lương giữa kỳ (mục 3.2) — _(trùng câu hỏi số 17 đã có sẵn trong_ `Questions-draft`_)_

4. Khi nhân viên được bổ nhiệm/tăng lương giữa kỳ lương (có 2 mức lương khác nhau trong cùng 1 kỳ): Core System tự tách 2 giai đoạn theo ngày hiệu lực quyết định, hay Workday đẩy sẵn 2 dòng lương riêng?

- Có thể xem mức lương và phụ cấp định mức thay đổi trong report Enterprise - Compensation Changes Report.
  {{tenant_url}}/ccx/service/customreport2/{{tenant}}/user@company.test/Enterprise\_-_Compensation_Changes_Report?Workflow_States!WID=b90bc51be01d4ae99b603b02b073714d&End_Date=2026-06-21-07:00&Start_Date=2026-06-02-07:00&Include_Subordinate_Organizations=1&Organizations!Organization_Reference_ID=CTDGROUP_0001
- Có thể đối chiếu chung với report Enterprise - List Detail of Work History
  {{tenant_url}}/ccx/service/customreport2/{{tenant}}/wd-support/Enterprise\_-_List_Detail_of_Work_History?Include_Subordinate_Organizations=1&Effective_on_or_After=2026-06-21-07:00&Effective_on_or_Before=2026-06-25-07:00&Supervisory_Organization!Organization_Reference_ID=CTD_ORG-2026-00001

5. Rule tách 2 giai đoạn này có áp dụng luôn cho phụ cấp trách nhiệm khi phụ cấp thay đổi giữa kỳ không?

- Có.
- WD chỉ cung cấp định mức, định mức này được xem như đã là định mức tại thời điểm tại bộ phận đó. Mình phải tính lại theo tỉ lệ ở từng bộ phận.

### C. Cụm PC cơm theo địa điểm (mục 3.4) — _(trùng câu hỏi số 1, 2, 14 đã có sẵn trong_ `Questions-draft`_)_

6. Số bữa cơm/ngày theo địa điểm (VP 1 bữa, site &lt;30km 2 bữa, site ≥30km 3 bữa) do Workday tính sẵn rồi đẩy sang, hay Core System phải tự tính?

- Số liệu của WD có định mức khi đổi bộ phận sẽ có compensations change.
- Dựa vào định mức cơm (VND) / 45000 = số định mức ngày tại bộ phận đó và tính theo ngày (dựa vào schedule để cộng cơm từng ngày).

7. Nếu Core System tự tính: dữ liệu "khoảng cách công trường" lấy từ đâu, ai cập nhật/duy trì?

- Lấy số liệu khoảng cách để HR đối chiếu

8. Khi nhân viên đi làm đúng ngày lễ hoặc ngày nghỉ (không phải Chủ nhật): có tính thêm bữa cơm không, tính theo cách nào?

- Có
- Như câu 3, dựa vào Time_Tracking, có số lượng phần cơm + cash 1x/2x/3x tùy thuộc vào ngày lễ/thường/OT
- Một ngày có thể nhận nhiều tag tính. Ví dụ, ngày lễ cash 2x => quy ra Cash_1x & Off_In_Lieu_1x = 1

### D. Cụm PC điện thoại/đi lại/xăng theo level + prorate &lt;14 ngày (mục 3.5, 3.6) — _(trùng câu hỏi số 3, 13, 14 đã có sẵn trong_ `Questions-draft`_)_

9. PC điện thoại "theo level" (Excel `AS10`) — bảng tra level → mức trần cụ thể là gì? (DB hiện dùng trần cố định 400.000đ cho mọi level, không đúng theo Excel).

- Tất cả số liệu theo WD.
- Việc tính thuế thì theo anh nhớ HR có nói 1 rules là nếu PC điện thoại >= mức trần thì phần chịu thuế = PC điện thoại - mức trần. Còn nhỏ hơn hoặc bằng mức trần thì không chịu thuế. Cần confirm lại mức trần chỗ này

10. Ngưỡng "dưới 14 ngày đi làm thực tế thì phụ cấp tính theo tỷ lệ" — tính trên loại ngày nào: chỉ ngày đi làm thực tế, hay gồm cả ngày nghỉ hưởng lương?

- Tổng số ngày công đi làm từ 21-20 (1) + Tổng nghỉ hưởng lương từ 21-20, cột BA đến BE (2) = (3)
- Tổng số ngày công đi làm từ 21-20 (1)(4) + Nghỉ lễ (5)
- Trường hợp số ngày đi làm thực tế dưới 14 (mười bốn) ngày = (3), phụ cấp điện thoại được tính theo tỷ lệ ngày làm việc thực tế và ngày nghỉ lễ trong tháng = (4)+(5) - CỦA BỘ PHẬN 1
- còn lại PC khác tính theo tỉ lệ

11. Công thức chia tỷ lệ chính xác: chia cho ngày công chuẩn (`STD_DAYS`) hay chia cho 14?

- Công thức chia tỷ lệ chính xác là công chuẩn có thể làm full trong kỳ lương tại bộ phận đó.

12. Rule &lt;14 ngày này áp dụng cho đúng 4 khoản phụ cấp (điện thoại, đi lại chịu/không chịu thuế, xăng) hay cả 7 loại phụ cấp?

- Chưa confirm

13. Nhân sự điều động (chuyển giữa VP/công trường hoặc giữa 2 công trường trong cùng kỳ lương) — phụ cấp tính theo nơi làm việc cuối kỳ, hay chia tỷ lệ theo số ngày ở từng nơi?

- Chia theo tỉ lệ với công chuẩn là công chuẩn có thể làm full trong kỳ lương ở mỗi bộ phận.

### E. Cụm thưởng bình quân 12 tháng (mục 3.8) — _(trùng câu hỏi số 21 đã có sẵn trong_ `Questions-draft`_)_

14. Lương bình quân 12 tháng liền kề (dùng để tính Thưởng Tết Âm lịch, tối đa 15 triệu, và Lương tháng 13) — Core System tự lưu lịch sử lương để tính, hay Workday cung cấp sẵn con số bình quân?

- Chưa kiểm tra trong WD, cần phụ giúp để tìm đúng report hoặc API

15. "Thời gian tính thưởng" (dùng trong công thức `= thời gian tính thưởng/365 × định mức`) đếm từ ngày nào đến ngày nào — từ ngày vào làm, hay từ đầu năm tài chính?

- Chưa confirm

### F. Cụm BHXH nghỉ ≥14 ngày (mục 3.9) — đã có hướng riêng

16. _[pause](Không phải câu hỏi — ghi nhớ)_ User sẽ phối hợp đội adapter tạo dữ liệu "số ngày nghỉ liên tục trong tháng" rồi bắn sang backend; không cần hỏi HR thêm ở đây, chỉ cần xác nhận tên field/format khi đội adapter có kết quả.

### G. Cụm thuế TNCN thử việc (mục 3.12) — _(trùng câu hỏi số 3, 25, 26 đã có sẵn trong_ `Questions-draft`_)_

17. Nhân viên thử việc (không phải thực tập, người Việt) tính thuế TNCN theo biểu luỹ tiến giống nhân viên chính thức (như DB đang làm), hay 10% cố định trên tổng thu nhập (như Excel gốc `CH11` ghi)?

- Chưa confirm

18. Hợp đồng vãng lai/dưới 3 tháng có cần thêm 1 nhánh riêng tính 10% cố định theo quy định thuế hiện hành không (DB hiện chưa có nhánh này)?

- Chưa confirm

19. Cơ sở tính thuế cho các nhánh 10%/20% là "tổng thu nhập" (GROSS, chưa trừ gì) như Excel ghi, hay "thu nhập tính thuế" (`TAXABLE_INC`, đã trừ bảo hiểm/giảm trừ) như DB hiện đang dùng?
