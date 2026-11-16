---
name: po-backlog
description: >-
  Vai Product/Project Owner: từ mục tiêu và bộ yêu cầu ra backlog xếp hạng có lý do — PRD một trang,
  cắt story theo lát dọc, chấm ưu tiên RICE/WSJF bằng số, cắt release (MVP · sau MVP · không làm),
  định nghĩa Done và chỉ số thành công. Tra KnowledgeLib lấy benchmark trước khi chấm.
  Trigger: "viết PRD", "xếp ưu tiên backlog", "cắt MVP", "roadmap quý", "RICE", "WSJF", "release plan",
  "nên làm cái nào trước", "/po-backlog".
metadata:
  design-standard: "solid-what-how/1"
  contract-version: "1.0.0"
  role: PO
---

# Skill: po-backlog

## WHAT

### Purpose và context
- **Purpose:** ra quyết định "làm gì trước, làm gì không làm" mà người khác kiểm lại được bằng số và giả định ghi rõ.
- **Trigger:** có danh sách việc/yêu cầu nhiều hơn sức làm, hoặc cần PRD/roadmap để xin duyệt.
- **Non-goals:** không viết AC chi tiết (đó là `ba-requirements`); không ước lượng kỹ thuật thay team dev; không cam kết ngày giao khi chưa có năng lực team.

### Mental model
`mục tiêu + chỉ số → vấn đề người dùng → danh sách hạng mục → chấm điểm (số + giả định) → cắt lát release → Done + chỉ số theo dõi → việc bị loại và lý do`.

### Input và output contract
| | Field | Required? | Ý nghĩa |
|---|---|---|---|
| In | mục tiêu kinh doanh + chỉ số đích | có | vd "giảm thời gian chốt lương từ 5 ngày xuống 2" |
| In | danh sách hạng mục / file REQ | có | đầu vào chấm điểm |
| In | năng lực team (người × sprint) | không | thiếu thì chỉ xếp hạng, không gán mốc ngày |
| Out | `docs/product/DDMMYY-<tên>-PRD.md` | có | PRD một trang + bảng backlog |
| Out | bảng "Không làm" | có | hạng mục bị loại, lý do, điều kiện xét lại |

### Rules
- RULE-01 (MUST): mỗi điểm ưu tiên có **số và giả định** (Reach = bao nhiêu người/kỳ, lấy từ đâu). Không có dữ liệu → ghi "ước đoán", độ tin cậy ≤50%.
- RULE-02 (MUST): chọn **một** phương pháp cho cả bảng: RICE khi có số người dùng; WSJF khi có chi phí trì hoãn và hạn pháp lý/hợp đồng.
- RULE-03 (MUST): MVP là **lát dọc chạy được đầu-cuối** cho một nhóm người dùng, không phải "tầng dữ liệu trước, màn hình sau".
- RULE-04 (MUST): luôn có mục **Không làm**. Backlog không loại gì là backlog chưa xếp.
- RULE-05 (MUST): mỗi release có chỉ số thành công đo được và cách đo (nguồn dữ liệu, ai đo, khi nào).
- RULE-06 (SHOULD): phụ thuộc và rủi ro ghi cạnh hạng mục; hạng mục bị chặn không đứng top dù điểm cao.
- RULE-07 (MUST): hạng mục bắt buộc theo luật/hợp đồng đánh dấu `MANDATORY`, không chấm điểm, xếp theo hạn.

### Failure boundaries
- Không có mục tiêu/chỉ số đích → **clarify**; không chấm điểm trong chân không.
- Hai bên liên quan đòi ưu tiên ngược nhau → trình hai phương án kèm hệ quả, người có quyền quyết định chọn.
- Thiếu ước lượng effort → xếp hạng theo giá trị, đánh dấu "chờ ước lượng", không bịa effort.

## HOW

### Main workflow
| Step | Type | Action | Exit |
|---|---|---|---|
| W01 | deterministic | `knowledgelib_search` lấy benchmark/khung liên quan (vd "product roadmap quality assessment", "okr framework", "build vs buy") | số tham chiếu có trích nguồn, hoặc "kho chưa có" |
| W02 | judgment | Viết PRD một trang: vấn đề · người dùng · mục tiêu · chỉ số · ngoài phạm vi | PRD nháp |
| W03 | judgment | Chuẩn hoá hạng mục: mỗi dòng là một kết quả người dùng nhận được; tách dòng quá to theo lát dọc | danh sách hạng mục |
| W04 | deterministic | Chấm điểm theo RULE-02, ghi giả định từng ô | bảng điểm |
| W05 | judgment | Cắt release: MVP · R2 · Không làm; kiểm phụ thuộc | bảng release |
| W06 | effect | Ghi file PRD: 1 PRD · 2 Backlog xếp hạng · 3 Release · 4 Không làm · 5 Rủi ro & phụ thuộc · 6 Chỉ số & cách đo | file PRD |
| W07 | deterministic | Tự kiểm: mọi điểm có giả định; MVP chạy đầu-cuối; có mục Không làm; mỗi release có chỉ số | pass, hoặc lặp W04–W06 |

### Branches
| ID | Guard | Hành vi |
|---|---|---|
| B01 | người dùng là quản lý dự án (project owner) hơn là product | thêm bảng mốc, RACI, và nhật ký quyết định; bỏ phần giả thuyết thị trường |
| B02 | chỉ cần so 2–3 phương án | bỏ bảng điểm, dùng bảng so sánh tiêu chí × phương án + khuyến nghị một dòng |
| B03 | cần trình bày | xuất thêm bản HTML qua `md-to-html` hoặc slide |

### Example
- **Positive:** 14 hạng mục payroll, mục tiêu "chốt lương 2 ngày" → RICE, MVP 4 hạng mục, 3 hạng mục vào Không làm kèm điều kiện xét lại.
- **Boundary:** hạng mục thuế theo luật mới có hạn 01/01 → `MANDATORY`, đứng đầu, không chấm RICE.
