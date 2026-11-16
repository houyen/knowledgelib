---
name: data-spec
description: >-
  Vai Data Analyst/Engineer: đặc tả dữ liệu trước khi viết SQL/pipeline — định nghĩa chỉ số (công thức,
  grain, bộ lọc, chủ sở hữu), mapping nguồn→đích từng cột, data contract (schema, khoá, độ tươi, SLA),
  quy tắc chất lượng dữ liệu kiểm được, và truy vấn đối soát. Profile dữ liệu thật trước khi khẳng định.
  Trigger: "định nghĩa KPI", "metric definition", "mapping nguồn đích", "source to target", "data contract",
  "data quality rule", "đối soát số liệu", "thiết kế báo cáo", "data dictionary", "/data-spec".
metadata:
  design-standard: "solid-what-how/1"
  contract-version: "1.0.0"
  role: Data
---

# Skill: data-spec

## WHAT

### Purpose và context
- **Purpose:** một bản đặc tả để hai người khác nhau viết SQL ra **cùng một con số**, và biết khi nào số đó sai.
- **Trigger:** báo cáo/dashboard mới, chuyển dữ liệu giữa hệ thống, hoặc hai nguồn ra hai số khác nhau.
- **Non-goals:** không dựng dashboard (dùng `dataviz`); không tối ưu hạ tầng pipeline; không quyết định nghiệp vụ "chỉ số nào quan trọng" (đó là `po-backlog`).

### Mental model
`câu hỏi kinh doanh → chỉ số (công thức + grain) → nguồn thật (profile) → mapping cột → contract → quy tắc chất lượng → truy vấn đối soát`.

### Input và output contract
| | Field | Required? | Ý nghĩa |
|---|---|---|---|
| In | câu hỏi kinh doanh / mẫu báo cáo | có | cái số phải trả lời |
| In | schema nguồn (DDL, file mẫu, quyền truy vấn) | có | để profile thật |
| In | số đối chiếu đã được tin (báo cáo cũ, sổ kế toán) | không | mốc đối soát |
| Out | `docs/data/DDMMYY-<tên>-DATA-SPEC.md` | có | đủ 6 mục ở W06 |
| Out | file SQL đối soát | nếu có quyền truy vấn | chạy được, có kết quả kỳ vọng |

### Rules
- RULE-01 (MUST): mỗi chỉ số ghi đủ: tên · công thức · **grain** (một dòng là gì) · bộ lọc · múi giờ/kỳ · đơn vị · chủ sở hữu · ví dụ tính tay 1 dòng.
- RULE-02 (MUST): **profile trước khi viết**: số dòng, null, giá trị khác biệt, min/max ngày, trùng khoá. Khẳng định về dữ liệu phải kèm truy vấn đã chạy.
- RULE-03 (MUST): mapping ở mức **cột**: nguồn.cột → phép biến đổi → đích.cột, kiểu dữ liệu, xử lý null, giá trị mặc định.
- RULE-04 (MUST): mọi phép join ghi rõ lực lượng (1-1, 1-n, n-n) và đã kiểm fan-out chưa.
- RULE-05 (MUST): quy tắc chất lượng viết thành kiểm tra chạy được (unique, not null, khoảng giá trị, toàn vẹn tham chiếu, độ tươi), mỗi quy tắc có mức nghiêm trọng và việc làm khi vi phạm.
- RULE-06 (MUST): có ít nhất một truy vấn **đối soát** với số đã được tin; lệch thì giải thích từng khoản, không làm tròn cho khớp.
- RULE-07 (MUST): dữ liệu cá nhân đánh dấu cột, ghi cách che/tổng hợp; không dán dòng dữ liệu thật có PII vào spec.
- RULE-08 (SHOULD): thay đổi schema theo hướng tương thích ngược; thay đổi phá vỡ phải có phiên bản contract mới.

### Failure boundaries
- Không có quyền truy vấn nguồn → spec ở trạng thái **chưa profile**, mọi khẳng định dữ liệu ghi "giả định".
- Chỉ số có hai cách hiểu → ghi cả hai công thức, tính thử cả hai trên cùng mẫu, hỏi chủ sở hữu.
- Đối soát lệch không giải thích được → **failed**, không giao spec như đã xong.

## HOW

### Main workflow
| Step | Type | Action | Exit |
|---|---|---|---|
| W01 | deterministic | `knowledgelib_search` theo miền (vd "data contracts schema evolution", "saas metrics", "canonical data model") | định nghĩa chuẩn/benchmark có nguồn, hoặc "kho chưa có" |
| W02 | judgment | Chốt chỉ số theo RULE-01 | bảng chỉ số |
| W03 | deterministic | Profile nguồn bằng SQL/script, lưu truy vấn + kết quả | bảng profile |
| W04 | judgment | Viết mapping cột + lực lượng join | bảng mapping |
| W05 | judgment | Viết contract (schema, khoá, độ tươi, SLA, chủ sở hữu) và quy tắc chất lượng | contract + bảng quy tắc |
| W06 | effect | Ghi DATA-SPEC: 1 Câu hỏi & chỉ số · 2 Nguồn & profile · 3 Mapping · 4 Contract · 5 Quy tắc chất lượng · 6 Đối soát | file spec |
| W07 | deterministic | Chạy truy vấn đối soát; kiểm mọi join có lực lượng, mọi chỉ số có ví dụ tính tay | khớp hoặc lệch đã giải thích |

### Branches
| ID | Guard | Hành vi |
|---|---|---|
| B01 | chỉ cần từ điển dữ liệu | dừng sau W03, xuất bảng cột · kiểu · ý nghĩa · ví dụ · tỉ lệ null |
| B02 | chuyển đổi dữ liệu giữa hệ thống (migration) | thêm mục thứ tự nạp, đếm trước/sau từng bảng, kế hoạch rollback |
| B03 | dùng dbt | xuất thêm `schema.yml` với tests tương ứng RULE-05 |
| B04 | cần biểu đồ | chuyển sang `dataviz` sau khi W07 pass |

### Example
- **Positive:** "tổng quỹ lương theo phòng ban, tháng" → grain = nhân viên × kỳ lương, profile lộ 12 nhân viên đổi phòng giữa kỳ → quy tắc phân bổ ghi rõ, đối soát khớp sổ lương.
- **Boundary:** join nhân viên × hợp đồng ra 1-n làm tổng lương gấp đôi → RULE-04 bắt được, sửa bằng hợp đồng hiệu lực cuối kỳ.
