---
id: self-docs/general/brd-thuong-cau-hoi-can-hr-chot
canonical_question: 'Technical guide and specification: BRD Thưởng — Câu hỏi cần HR/BA
  chốt'
aliases:
- BRD Thưởng — Câu hỏi cần HR/BA chốt
- BRD Thuong Cau Hoi Can HR Chot 070926
entity_type: how_to
domain: self-docs > general
last_verified: 2026-09-17
---

# BRD Thưởng — Câu hỏi cần HR/BA chốt (070926)

Nguồn: `Payroll_BRD_Tracker_Item.xlsx` (sheet `Functions_Approval`) + `checklist.xlsx`, đối chiếu
PRD2 §4.4 (Bonus Logic) + SOP Flowchart mục 4.6. File này liệt kê **mọi điểm chưa chốt** trong 9
BRD Thưởng (TASK-REF, TASK-REF..29) — kể cả những điểm đã có default tạm trong code (Phase 1) nhưng
chưa phải quyết định chính thức từ HR, và những điểm hoàn toàn chưa code (Phase 2, chờ HR trước
khi làm). Dùng file này để đi detail với người chuyên trách/HR.

---

## Phần A — Đã code (Phase 1: TASK-REF/22/23/24/28), còn 3 điểm cần HR xác nhận lại

Cả 3 điểm dưới đây agent đã tự chọn 1 phương án hợp lý để không chặn tiến độ code, nhưng đây là
**quyết định nghiệp vụ ảnh hưởng trực tiếp số tiền thưởng thật** — cần HR xác nhận lại trước khi
đưa vào production, không chỉ là "làm cho chạy được".

### A1. Quy tắc loại trừ ngày nghỉ: LIÊN TỤC hay LŨY KẾ?

- **Mâu thuẫn giữa 2 nguồn:**
  - PRD2 §4.4 (văn bản gốc): *"Tự động loại trừ: Các ngày nghỉ thai sản, ốm đau, nghỉ không lương
    **lũy kế** từ 10 ngày trở lên theo thời gian xét."*
  - Ghi chú làm rõ thực địa trong TASK-REF (cùng file tracker): *"Thời gian tính thưởng = thời gian
    làm việc thực tế − nghỉ ko lương/thai sản/ốm đau ≥10 ngày **liên tục**."*
- **Đã code theo:** LIÊN TỤC (chỉ loại trừ 1 chuỗi ngày nghỉ liền nhau ≥10 ngày; 2 chuỗi rời rạc
  6+6 ngày = 12 ngày tổng nhưng KHÔNG bị loại trừ vì không chuỗi nào đạt 10).
- **Cần hỏi HR:** Chọn đúng cách nào? Nếu chọn "lũy kế" (cộng dồn cả kỳ xét, không cần liền
  nhau) thì phải sửa lại code — khác biệt có thể ra số tiền thưởng chênh lệch thật cho NV nghỉ
  rải rác nhiều đợt ngắn.

### A2. "Lương" dùng để tính bình quân là GROSS hay basic/net?

- Code hiện tại dùng cột `GROSS` ("Tổng thu nhập trong tháng") trong `payroll_records` làm cơ sở
  bình quân 12 tháng cho Lương tháng 13 và Tết Âm lịch.
- PRD2 §4.4 chỉ ghi chung chung "Bình quân lương 12 tháng", không nói rõ là gross, basic, hay
  net (thực nhận).
- **Cần hỏi HR:** "Bình quân lương" trong công thức Lương tháng 13 / Tết Âm lịch có đúng là
  **Tổng thu nhập (GROSS)** không, hay phải là **lương cơ bản (BASIC_SAL)** hoặc **lương thực
  nhận (NET_PAY)**? Đây là điểm ảnh hưởng số tiền lớn nhất trong toàn bộ Phase 1.

### A3. "Thời gian xét" tính theo ngày lịch hay ngày công chuẩn?

- Code hiện tại: `review_days_total` = số ngày LỊCH (calendar days, tính cả T7/CN/lễ) giữa ngày
  bắt đầu và kết thúc kỳ xét, ví dụ kỳ 01/01–31/12 = 365 ngày.
- **Cần hỏi HR:** Tỷ lệ `(thời gian tính thưởng / thời gian xét)` có nên tính theo ngày công
  chuẩn (như `std_days`/`std_days_ct` đã dùng cho bảng lương) thay vì ngày lịch không? Ảnh hưởng
  tới NV mới vào/nghỉ giữa kỳ.

---

## Phần B — TASK-REF: Quy tắc phân bổ Thưởng KPI (chưa code, chờ HR)

- **Nguồn PRD2 §4.4:** *"KPI: phân bổ theo kpi công ty, khối/BU/bộ phận, cá nhân."*
- **Vấn đề:** Không có tỷ trọng % nào giữa 4 cấp (công ty / khối-BU / bộ phận / cá nhân) ở bất kỳ
  đâu trong PRD1/PRD2/SOP.
- **Câu hỏi cần HR trả lời:**
  1. Tỷ trọng % phân bổ giữa 4 cấp KPI là bao nhiêu? (VD: 20% công ty / 30% khối-BU / 20% bộ
     phận / 30% cá nhân — cần bảng số thật, không phải ví dụ).
  2. Tỷ trọng này cố định toàn công ty hay khác nhau theo cấp bậc/chức danh?
  3. KPI cá nhân lấy dữ liệu từ đâu (hệ thống đánh giá KPI riêng, hay HR nhập tay mỗi đợt)?

## Phần C — TASK-REF: Tách thưởng khi điều động (chưa code, chờ HR)

- **Nguồn PRD2 §4.4:** *"Điều động: Tính phân tách tỷ lệ thưởng tương ứng với thời gian/tháng làm
  việc tại từng dự án trong năm → Phục vụ hạch toán chi phí."*
- **Đã trả lời trong tracker:** nguồn lịch sử điều động lấy từ Workday, không giới hạn số dự án/NV
  trong năm.
- **Còn vướng — chưa trả lời:**
  1. *"Cần align lại với HR, về One-Time Payment tại WD cho case này"* — Core System có tự tính +
     tách số tiền theo dự án, hay chỉ nhận tổng số tiền đã tách sẵn từ Workday (One-Time Payment)
     và chỉ hiển thị lại trên Payslip?
  2. Cơ chế kỹ thuật (prorate theo `employee_work_histories.date_effective/date_end` chồng lấn kỳ
     xét) khả thi về mặt code, nhưng **chưa biết Enterprise có phải là nơi tính chính thức con số này
     không** — nếu Workday đã tính và chỉ cần Enterprise hiển thị, phần lớn việc code ở Phase 2 sẽ khác
     hẳn (chỉ cần đọc, không cần tính).

## Phần D — TASK-REF: Thưởng công trình (chưa code, chờ HR)

- **Nguồn SOP Flowchart mục 4.6:** *"Thưởng dự án/công trình: Căn cứ theo đề xuất từ các công
  trình... → thiết lập rule tính trên hệ thống."* — KHÔNG có công thức cố định, mỗi đợt chi là 1
  rule cấu hình riêng theo đề xuất thực tế.
- **Câu hỏi cần HR trả lời:**
  1. Màn hình cấu hình rule thưởng công trình cần cho Admin/HR nhập những trường (field) gì?
     (VD: công trình áp dụng, quỹ thưởng, điều kiện đạt, công thức phân bổ theo NV...)
  2. Ai là người khởi tạo 1 rule mới mỗi đợt — HR nhập trực tiếp trên hệ thống, hay dựa trên 1 Tờ
     trình/đề xuất được duyệt riêng trước đó rồi HR mới nhập lại?
  3. *(Lưu ý dữ liệu — không phải câu hỏi nghiệp vụ)*: dòng ghi chú trong tracker gốc (cột "Ghi
     chú/Phụ thuộc" của TASK-REF) có tham chiếu chéo tới "TASK-REF" — có vẻ là lỗi đánh số/sai sót
     khi nhập liệu trong file gốc, không rõ ý định thật là gì. Cần hỏi người tạo tracker để xác
     nhận nội dung đúng là gì trước khi dùng dòng ghi chú đó.

## Phần E — TASK-REF: Quy tắc Thưởng VLN (chưa code, chờ HR)

- **Thuật ngữ:** VLN = "Vượt Lợi Nhuận" (đã xác nhận trong tracker).
- **Nguồn PRD2 §4.4:** *"VLN: set rule % thưởng tương ứng với quỹ vượt, tính theo thời gian và mức
  độ đóng góp → linh động cho HR set up rule."* — không có % cố định.
- **Câu hỏi cần HR trả lời:**
  1. Màn hình cấu hình rule VLN cần cho HR nhập những trường gì? (VD: ngưỡng quỹ lợi nhuận vượt
     kế hoạch, % thưởng theo từng bậc mức độ đóng góp, khoảng thời gian áp dụng...)
  2. Input/output cụ thể của "rule engine" này để dev/QA build và test được — hiện chưa có ví dụ
     số cụ thể nào.
  3. *"Cần align lại với HR, đây là One-Time Payment tại WD?"* — giống TASK-REF, chưa rõ Enterprise tính
     hay chỉ nhận số đã tính sẵn từ Workday.

## Phần F — TASK-REF (tổng): Ranh giới Enterprise tính vs Workday quản

- **Ghi chú gốc trong tracker:** *"One-Time Payment sẽ được manage tại WD, Core System sẽ chỉ lấy
  data về tính Payslip. Trường hợp cần Payslip Enterprise tính để load vào WD → chuyển qua phase sau."*
- **Câu hỏi cần HR/BA xác nhận dứt điểm** (câu hỏi này chi phối cả TASK-REF/27/29 ở trên, nên tách
  riêng thành 1 mục để hỏi 1 lần, áp dụng chung):
  1. Với TỪNG loại thưởng (KPI, công trình, VLN, phần tách theo điều động), Enterprise là nơi **tính +
     ghi sổ chính thức**, hay chỉ là nơi **hiển thị lại Payslip** từ số liệu Workday đã tính?
  2. Nếu có loại thưởng nào Enterprise phải tự tính (không chỉ hiển thị), Workday có cần nhận ngược số
     liệu đó để nạp vào hệ thống HR chính (One-Time Payment) không, hay Enterprise là điểm dừng cuối?

---

## Tóm tắt nhanh (bảng để mang theo họp)

| # | BRD | Loại vướng | Cần ai trả lời | Mức ảnh hưởng |
|---|-----|-----------|----------------|----------------|
| A1 | 06/21/23/24 (đã code) | Mâu thuẫn tài liệu (liên tục/lũy kế) | HR/BA | Cao — sai số tiền thưởng |
| A2 | 06/21/23/24 (đã code) | Thiếu định nghĩa "lương" | HR/BA (C&B) | Cao — sai số tiền thưởng |
| A3 | 06/21/23/24 (đã code) | Thiếu định nghĩa "thời gian xét" | HR/BA | Trung bình |
| B | 25 | Thiếu số liệu (tỷ trọng %) | HR (KPI/BSC) | Chặn — không code được nếu thiếu |
| C | 26 | Ranh giới Enterprise/WD chưa rõ | HR + đội Workday | Chặn thiết kế |
| D | 27 | Cần đặc tả màn hình cấu hình | HR/BA | Chặn — không code được nếu thiếu |
| E | 29 | Cần đặc tả màn hình cấu hình + ranh giới Enterprise/WD | HR/BA + đội Workday | Chặn — không code được nếu thiếu |
| F | 06 | Ranh giới Enterprise tính vs WD quản (áp dụng chung) | HR + đội Workday | Chặn thiết kế Phase 2 |
