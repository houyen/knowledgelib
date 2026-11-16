---
name: sa-solution-design
description: >-
  Vai Solution Architect: từ yêu cầu ra thiết kế giải pháp có căn cứ — yêu cầu phi chức năng đo được,
  2–3 phương án so trên cùng tiêu chí, quyết định ghi ADR (MADR), sơ đồ C4 mức context + container,
  hợp đồng tích hợp (API/sự kiện/lô), rủi ro và kế hoạch chuyển đổi. Tra KnowledgeLib (system-design,
  erp-integration, patterns, self-docs) trước khi đề xuất.
  Trigger: "thiết kế giải pháp", "solution design", "viết ADR", "so sánh kiến trúc", "C4", "NFR",
  "thiết kế tích hợp", "HLD", "/sa-solution-design".
metadata:
  design-standard: "solid-what-how/1"
  contract-version: "1.0.0"
  role: SA
---

# Skill: sa-solution-design

## WHAT

### Purpose và context
- **Purpose:** một tài liệu thiết kế mà người duyệt thấy được **đã cân những gì và vì sao chọn**, không chỉ thấy phương án thắng.
- **Trigger:** tính năng/hệ thống mới, tích hợp hệ thống ngoài, hoặc đổi kiến trúc có chi phí quay lui cao.
- **Non-goals:** không viết code; không thiết kế chi tiết lớp/hàm (LLD); không thay `ba-requirements` làm rõ nghiệp vụ.

### Mental model
`yêu cầu + ràng buộc → NFR đo được → phương án (≥2) → tiêu chí × phương án → ADR → C4 context/container → hợp đồng tích hợp → rủi ro + chuyển đổi`.

### Input và output contract
| | Field | Required? | Ý nghĩa |
|---|---|---|---|
| In | yêu cầu chức năng (file REQ/PRD) | có | cái cần giải |
| In | ràng buộc (stack hiện có, ngân sách, hạn, tuân thủ) | có | giới hạn không gian phương án |
| In | codebase / sơ đồ hiện trạng | không | có thì đọc thật, không đoán |
| Out | `docs/architecture/DDMMYY-<tên>-SAD.md` | có | đủ 8 mục ở W07 |
| Out | `docs/adr/NNNN-<quyết-định>.md` | mỗi quyết định khó quay lui | định dạng MADR |

### Rules
- RULE-01 (MUST): NFR là **con số có điều kiện đo**: "p95 < 800 ms với 3.000 dòng import", không phải "nhanh".
- RULE-02 (MUST): tối thiểu **2 phương án thật** (một phương án luôn là "không làm / giữ nguyên" nếu khả thi), so trên cùng bộ tiêu chí.
- RULE-03 (MUST): mỗi quyết định khó quay lui ra một ADR: bối cảnh · phương án đã xét · quyết định · hệ quả (cả hệ quả xấu).
- RULE-04 (MUST): hợp đồng tích hợp ghi đủ: chiều dữ liệu, định dạng, xác thực, idempotency, retry/timeout, xử lý lỗi, khối lượng, ai sở hữu.
- RULE-05 (MUST): khẳng định về hệ thống hiện tại phải **đọc từ code/config**, có đường dẫn file. Chưa đọc được → ghi "giả định".
- RULE-06 (MUST): sơ đồ sinh bằng skill `diagram` (Mermaid/C4), không mô tả hình bằng lời rồi bỏ đó.
- RULE-07 (SHOULD): ưu tiên phương án ít thành phần mới nhất mà vẫn đạt NFR; thành phần mới phải trả lời "ai vận hành".
- RULE-08 (MUST): có mục dữ liệu nhạy cảm: loại dữ liệu, nơi lưu, ai truy cập, mã hoá, lưu vết.

### Failure boundaries
- Không có NFR nào đo được → **clarify**; đề xuất số mặc định để người dùng sửa, không tự coi là chốt.
- Chỉ nghĩ ra một phương án → nói rõ, nêu lý do không gian phương án hẹp; không bịa phương án rơm.
- Thiếu thông tin hệ thống ngoài (API bên thứ ba) → hợp đồng tích hợp để trạng thái **draft**, liệt kê câu cần hỏi.

## HOW

### Main workflow
| Step | Type | Action | Exit |
|---|---|---|---|
| W01 | deterministic | `knowledgelib_search` top_k=5 theo từng trục: mẫu kiến trúc, tích hợp, gotcha nội bộ (`self-docs`) | unit liên quan kèm id, hoặc "kho chưa có" |
| W02 | deterministic | Đọc hiện trạng từ code/config nếu có | bảng thành phần hiện có + đường dẫn |
| W03 | judgment | Chốt NFR đo được và ràng buộc | bảng NFR |
| W04 | judgment | Dựng 2–3 phương án, mỗi phương án: thành phần, luồng chính, chi phí, rủi ro | bảng phương án |
| W05 | judgment | Chấm tiêu chí × phương án, chọn, viết ADR | ADR |
| W06 | effect | Sinh C4 context + container bằng `diagram`; viết hợp đồng tích hợp | sơ đồ + bảng hợp đồng |
| W07 | effect | Ghi SAD: 1 Bối cảnh · 2 NFR · 3 Phương án · 4 Quyết định (link ADR) · 5 C4 · 6 Hợp đồng tích hợp · 7 Dữ liệu & bảo mật · 8 Rủi ro, chuyển đổi, rollback | file SAD |
| W08 | deterministic | Tự kiểm: mọi NFR có số; ≥2 phương án; mỗi ADR có hệ quả xấu; mọi khẳng định hiện trạng có đường dẫn | pass, hoặc lặp |

### Branches
| ID | Guard | Hành vi |
|---|---|---|
| B01 | chỉ một quyết định nhỏ | chỉ xuất ADR, bỏ SAD |
| B02 | cần phản biện | gọi skill `council` trên bảng phương án trước W05 |
| B03 | tích hợp ERP/HRIS (Workday, SAP, Odoo, Salesforce) | bắt buộc tra `business/erp-integration` và `self-docs/integration` ở W01 |
| B04 | quyết định xong, có bài học | đề xuất nạp ADR đã ẩn danh vào KnowledgeLib |

### Example
- **Positive:** "đồng bộ hợp đồng từ HRIS về payroll" → NFR (trễ ≤15 phút, 5.000 bản ghi/ngày), 3 phương án (poll · webhook · file lô), ADR chọn poll + lý do, hợp đồng tích hợp đủ 8 trường.
- **Boundary:** bên thứ ba chưa cấp tài liệu API → hợp đồng draft + 6 câu hỏi, SAD ghi rõ phần chưa chốt.
