---
name: ba-requirements
description: >-
  Vai Business Analyst: biến lời nghiệp vụ thô (ghi chú họp, email, BRD cũ, file Excel) thành bộ yêu cầu
  kiểm chứng được — quy trình as-is/to-be, business rule đánh số, user story + acceptance criteria Gherkin,
  danh sách câu hỏi mở cần nghiệp vụ chốt, ma trận truy vết. Tra KnowledgeLib trước khi viết.
  Trigger: "phân tích yêu cầu", "viết BRD", "viết SRS", "user story", "acceptance criteria", "as-is to-be",
  "câu hỏi cần chốt với nghiệp vụ", "/ba-requirements".
metadata:
  design-standard: "solid-what-how/1"
  contract-version: "1.0.0"
  role: BA
---

# Skill: ba-requirements

## WHAT

### Purpose và context
- **Purpose:** từ nguồn nghiệp vụ thô ra MỘT file yêu cầu mà dev, QC và nghiệp vụ cùng đọc được, mỗi dòng truy về được nguồn.
- **Trigger:** có ghi chú họp / email / BRD / màn hình hệ thống cũ và cần chốt "làm cái gì, đúng là thế nào".
- **Non-goals:** không thiết kế giải pháp kỹ thuật (đó là `sa-solution-design`); không xếp ưu tiên, cắt release (đó là `po-backlog`); không tự quyết thay nghiệp vụ ở chỗ nguồn im lặng.

### Mental model
`nguồn thô → actor + mục tiêu → as-is → to-be → business rule (BR-nn) → user story (US-nn) + AC Gherkin → câu hỏi mở (Q-nn) → ma trận truy vết`.

### Input và output contract
| | Field | Required? | Ý nghĩa |
|---|---|---|---|
| In | nguồn nghiệp vụ nguyên văn | có | ghi chú họp, email, BRD, Excel mẫu, ảnh màn hình |
| In | phạm vi (module / quy trình) | có | ranh giới phân tích |
| In | code/config hệ thống hiện tại | không | đối chiếu as-is thật thay vì as-is được kể |
| Out | `docs/requirements/DDMMYY-<tên>-REQ.md` | có | đủ 7 mục ở W06 |
| Out | danh sách Q-nn | có | câu hỏi đóng (có/không, chọn A/B) gửi nghiệp vụ |

### Rules
- RULE-01 (MUST): mỗi BR/US ghi **nguồn** (file + dòng, hoặc "người X nói ngày Y"). Không nguồn → chuyển thành Q-nn, không viết thành yêu cầu.
- RULE-02 (MUST): AC viết Gherkin `Given/When/Then` với **số liệu cụ thể** (ngày, số tiền, trạng thái), có ít nhất 1 case biên và 1 case từ chối cho mỗi story.
- RULE-03 (MUST): tách **quy tắc nghiệp vụ** khỏi **hành vi màn hình**. Rule đổi theo chính sách, màn hình đổi theo thiết kế.
- RULE-04 (MUST): câu hỏi mở là câu hỏi **đóng**, kèm phương án mặc định và hệ quả nếu chọn sai.
- RULE-05 (MUST): thuật ngữ nghiệp vụ vào bảng glossary một lần, dùng thống nhất, không đồng nghĩa lẫn lộn.
- RULE-06 (SHOULD): story đạt INVEST; story chứa "và" ở phần hành động → tách.
- RULE-07 (MUST): dữ liệu cá nhân, tên khách hàng, mã ticket nội bộ không đưa vào file nếu file sẽ ra ngoài dự án.

### Failure boundaries
- Nguồn mâu thuẫn nhau → ghi cả hai, mở Q-nn, **không tự chọn**.
- Thiếu actor hoặc phạm vi → **clarify** trước W02.
- Không đọc được as-is thật (không có quyền code/hệ thống) → ghi rõ "as-is theo lời kể", đánh dấu rủi ro.

## HOW

### Main workflow
| Step | Type | Action | Exit |
|---|---|---|---|
| W01 | deterministic | `knowledgelib_search` 2–3 truy vấn theo miền nghiệp vụ (vd "payroll approval flow", "BRD ecommerce") + `knowledgelib_get_memory_index` nếu là dự án nội bộ | danh sách unit liên quan, hoặc ghi "kho chưa có" |
| W02 | judgment | Rút actor, mục tiêu, phạm vi trong/ngoài | bảng actor–mục tiêu |
| W03 | judgment | Vẽ as-is và to-be dạng bảng bước (ai · làm gì · hệ thống · dữ liệu vào/ra); cần hình thì gọi skill `diagram` | 2 bảng quy trình |
| W04 | judgment | Rút business rule BR-nn (điều kiện → kết quả, có ví dụ số) | bảng BR |
| W05 | judgment | Viết US-nn + AC Gherkin, nối mỗi US với BR liên quan | bảng US |
| W06 | effect | Ghi file REQ: 1 Bối cảnh · 2 Glossary · 3 As-is/To-be · 4 BR · 5 US+AC · 6 Câu hỏi mở · 7 Ma trận truy vết (nguồn → BR → US → AC) | file REQ |
| W07 | deterministic | Tự kiểm: mọi US có ≥1 AC biên + ≥1 AC từ chối; mọi BR có nguồn; không Q-nn dạng mở | pass, hoặc sửa lặp W04–W06 |

### Branches
| ID | Guard | Hành vi |
|---|---|---|
| B01 | nguồn là BRD có sẵn | chế độ **review**: chỉ xuất khoảng trống, mâu thuẫn, Q-nn; không viết lại BRD |
| B02 | người đọc là nghiệp vụ non-IT | thêm bản tóm tắt 1 trang không thuật ngữ kỹ thuật; UAT thì chuyển `uat-nonit-testcase` |
| B03 | tri thức rút ra dùng lại được | đề xuất nạp vào KnowledgeLib qua `extract_tech_notes.py` (đã ẩn danh) |

### Example
- **Positive:** "ghi chú họp C&B về huỷ chốt công" → 4 BR, 6 US, 5 Q-nn dạng "Huỷ chốt sau khi đã tính lương: (A) chặn, (B) cho phép và tính lại — mặc định A".
- **Boundary:** hai email nói ngược nhau về hạn duyệt → ghi cả hai, Q-03, không story nào dựa vào hạn đó.
