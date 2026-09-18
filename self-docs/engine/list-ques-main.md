---
id: self-docs/engine/list-ques-main
canonical_question: 'Technical guide and specification: List Ques Main'
aliases:
- List Ques Main
entity_type: how_to
domain: self-docs > engine
last_verified: 2026-09-17
---

### A. Cụm OT

**Core System tự tính**

1. Dữ liệu chấm công hiện có (Workday) có breakdown đúng 6 loại giờ OT (thường/nghỉ/lễ × ngày/đêm) không, hay chỉ có tổng giờ OT chung? Nếu chỉ có tổng, nguồn lịch ngày lễ để Core System tự phân loại lấy ở đâu?
2. Cách tách phần chịu thuế/không chịu thuế của tiền OT theo đúng luật thuế TNCN hiện hành cho lương làm thêm giờ
3. Hệ số 150%/200%/300% + phụ cấp ca đêm 30% có đúng mức công ty đang áp dụng không, hay công ty có thoả ước lao động tập thể cao hơn? (Excel `AY11` ghi "trả thêm 100%" cho ngày lễ — cần đối chiếu lại cách diễn đạt này có khớp 300% hay không).

### B. Cụm bổ nhiệm 2 mức lương giữa kỳ (mục 3.2) — *(trùng câu hỏi số 17 đã có sẵn trong* `Questions-draft`*)*

4. Khi nhân viên được bổ nhiệm/tăng lương giữa kỳ lương (có 2 mức lương khác nhau trong cùng 1 kỳ): Core System tự tách 2 giai đoạn theo ngày hiệu lực quyết định, hay Workday đẩy sẵn 2 dòng lương riêng?
5. Rule tách 2 giai đoạn này có áp dụng luôn cho phụ cấp trách nhiệm khi phụ cấp thay đổi giữa kỳ không?

### C. Cụm PC cơm theo địa điểm (mục 3.4) — *(trùng câu hỏi số 1, 2, 14 đã có sẵn trong* `Questions-draft`*)*

6. Số bữa cơm/ngày theo địa điểm (VP 1 bữa, site &lt;30km 2 bữa, site ≥30km 3 bữa) do Workday tính sẵn rồi đẩy sang, hay Core System phải tự tính?
7. Nếu Core System tự tính: dữ liệu "khoảng cách công trường" lấy từ đâu, ai cập nhật/duy trì?
8. Khi nhân viên đi làm đúng ngày lễ hoặc ngày nghỉ (không phải Chủ nhật): có tính thêm bữa cơm không, tính theo cách nào?

### D. Cụm PC điện thoại/đi lại/xăng theo level + prorate &lt;14 ngày (mục 3.5, 3.6) — *(trùng câu hỏi số 3, 13, 14 đã có sẵn trong* `Questions-draft`*)*

9. PC điện thoại "theo level" (Excel `AS10`) — bảng tra level → mức trần cụ thể là gì? (DB hiện dùng trần cố định 400.000đ cho mọi level, không đúng theo Excel).
10. Ngưỡng "dưới 14 ngày đi làm thực tế thì phụ cấp tính theo tỷ lệ" — tính trên loại ngày nào: chỉ ngày đi làm thực tế, hay gồm cả ngày nghỉ hưởng lương?
11. Công thức chia tỷ lệ chính xác: chia cho ngày công chuẩn (`STD_DAYS`) hay chia cho 14?
12. Rule &lt;14 ngày này áp dụng cho đúng 4 khoản phụ cấp (điện thoại, đi lại chịu/không chịu thuế, xăng) hay cả 7 loại phụ cấp?
13. Nhân sự điều động (chuyển giữa VP/công trường hoặc giữa 2 công trường trong cùng kỳ lương) — phụ cấp tính theo nơi làm việc cuối kỳ, hay chia tỷ lệ theo số ngày ở từng nơi?

### E. Cụm thưởng bình quân 12 tháng (mục 3.8) — *(trùng câu hỏi số 21 đã có sẵn trong* `Questions-draft`*)*

14. Lương bình quân 12 tháng liền kề (dùng để tính Thưởng Tết Âm lịch, tối đa 15 triệu, và Lương tháng 13) — Core System tự lưu lịch sử lương để tính, hay Workday cung cấp sẵn con số bình quân?
15. "Thời gian tính thưởng" (dùng trong công thức `= thời gian tính thưởng/365 × định mức`) đếm từ ngày nào đến ngày nào — từ ngày vào làm, hay từ đầu năm tài chính?

### F. Cụm BHXH nghỉ ≥14 ngày (mục 3.9) — đã có hướng riêng

16. *[done](Không phải câu hỏi — ghi nhớ)* User sẽ phối hợp đội adapter tạo dữ liệu "số ngày nghỉ liên tục trong tháng" rồi bắn sang backend; không cần hỏi HR thêm ở đây, chỉ cần xác nhận tên field/format khi đội adapter có kết quả.

### G. Cụm thuế TNCN thử việc (mục 3.12) — *(trùng câu hỏi số 3, 25, 26 đã có sẵn trong* `Questions-draft`*)*

17. Nhân viên thử việc (không phải thực tập, người Việt) tính thuế TNCN theo biểu luỹ tiến giống nhân viên chính thức (như DB đang làm), hay 10% cố định trên tổng thu nhập (như Excel gốc `CH11` ghi)?
18. Hợp đồng vãng lai/dưới 3 tháng có cần thêm 1 nhánh riêng tính 10% cố định theo quy định thuế hiện hành không (DB hiện chưa có nhánh này)?
19. Cơ sở tính thuế cho các nhánh 10%/20% là "tổng thu nhập" (GROSS, chưa trừ gì) như Excel ghi, hay "thu nhập tính thuế" (`TAXABLE_INC`, đã trừ bảo hiểm/giảm trừ) như DB hiện đang dùng?

