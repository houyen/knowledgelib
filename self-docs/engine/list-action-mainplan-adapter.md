---
id: self-docs/engine/list-action-mainplan-adapter
canonical_question: 'Technical guide and specification: List Action Mainplan Adapter'
aliases:
- List Action Mainplan Adapter
entity_type: how_to
domain: self-docs > engine
last_verified: 2026-09-17
---

### Danh sách B —ADAPTER

1. **[OT]** Lấy dữ liệu OT theo tag `Time_Calculation_Tag_ID` (`Cash_1x/2x/3x`, `Off_In_Lieu_1x`...) qua Workday API `Time_Tracking > Get_Calculated_Time_Blocks` (chỉ lấy block đã `APPROVED`), kèm `Calculated_Quantity` — đồng bộ vào `attendance_summary` (cột mới) để BE đọc qua "input hệ thống" (Q1, Q3).
2. **[Bổ nhiệm]** Đồng bộ 2 report Workday: `"Enterprise - Compensation Changes Report"` (định mức lương/phụ cấp thay đổi theo bộ phận + ngày hiệu lực) và `"Enterprise - List Detail of Work History"` (đối chiếu lịch sử công tác) — cần cho cả cụm 3.2 và 3.4 (định mức cơm theo bộ phận) (Q4, Q6).
3. **[PC điện thoại theo level]** Đồng bộ bảng tra level → mức trần PC điện thoại từ Workday (Q9 — "Tất cả số liệu theo WD").
4. **[Bình quân 12 tháng]** Tìm đúng report/API Workday cho lương bình quân 12 tháng liền kề — **user tự nhận chưa kiểm tra, cần đội adapter phụ giúp tìm** (Q14, trả lời nguyên văn "Chưa kiểm tra trong WD, cần phụ giúp để tìm đúng report hoặc API").
5. **[Ca đêm OT]** — chưa có trong câu trả lời hiện tại, cần hỏi bổ sung: dữ liệu ca đêm (3 mốc `*_NIGHT` trong `ot_multiplier_configs`) lấy từ tag nào trong `Get_Calculated_Time_Blocks`, hay cần API/report khác.

