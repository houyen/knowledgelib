# Phase 7 — Self-Docs Canonical Enforcement & Memory-Loading Improvements

> Tài liệu mô tả kiến trúc, kết quả đã thi hành và kế hoạch tiếp nối cho session làm việc tiếp theo (harness session).

---

## 1. Bối cảnh & Lý do

- Kho tài liệu nội bộ `self-docs/` ban đầu chỉ có 1 file (`self-docs/workday_job_change_api_guide.md`) nhưng bị lỗi **un-canonical**: thiếu YAML frontmatter, dẫn đến `canonical_question` bị gán cụt lủn theo tên file, `aliases` rỗng, `content_preview` rỗng và vector search không thể tìm thấy.
- Nguồn tài liệu sống thực tế nằm ở `/Users/thaidt/Documents/CTD/Payroll CTD/self-docs/` (70+ file Markdown, ~1.2MB tài liệu kỹ thuật về engine tính lương, RBAC hybrid scoping, Workday integration, database migration gotchas...). Các tài liệu này chứa tri thức kỹ thuật rất giá trị nhưng bị lẫn lộn context dự án (tên công ty, email nội bộ, ticket ID) và chưa theo chuẩn KnowledgeLib.
- AI Agent ở các repo khác không có cách nào nạp nhanh ma trận các sự thật kỹ thuật / runbook này vào context (Working Memory).

Mục tiêu Phase 7:
1. Xây dựng **Validator & Auto-fixer** để bảo đảm 100% tài liệu trong `self-docs/` tuân thủ Canonical Standard.
2. Xây dựng **Memory Loader** tạo ra Memory Index siêu nén (~30 tokens/unit) và tích hợp vào MCP server tool `knowledgelib_get_memory_index`.
3. Chuẩn bị pipeline chiết xuất (Anonymizer + Canonical Extractor) để ingest có chọn lọc từ `Payroll CTD/self-docs/` vào `knowledgelib_data`.

---

## 2. Các thành phần ĐÃ HOÀN THÀNH

### Task 1 — Canonical Validator & Auto-Fixer: `src/validate_canonical.py`
- Kiểm tra 6 trường bắt buộc: `id`, `canonical_question`, `aliases` (>=1), `entity_type` (trong enum chuẩn), `domain`, `last_verified` (YYYY-MM-DD), cùng markdown body non-empty.
- Hàm `auto_fix_file()`: tự động bóc tách tiêu đề H1, ngày tháng, suy đoán `entity_type` (`architecture_explainer`, `runbook`, `gotchas`, `troubleshooting`, `how_to`...) và inject Frontmatter hợp lệ.
- CLI: `python3 src/validate_canonical.py --dir self-docs --check` (exit 0 nếu pass, 1 nếu lỗi).

### Task 2 — Chuẩn hóa `self-docs/workday_job_change_api_guide.md`
- Đã bổ sung Frontmatter canonical hoàn chỉnh:
  - `id`: `self-docs/workday_job_change_api_guide`
  - `canonical_question`: "How to integrate Workday API for Job Change and Data Change business processes"
  - `aliases`: Song ngữ Anh - Việt (SOAP Staffing, Submit_Change_Job, WWS v45.2)
  - `entity_type`: `how_to`
  - `domain`: `self-docs > integration > workday`
  - `constraints`: Bắt buộc SOAP Staffing v45.2+ với WS-Security UsernameToken.
- Chạy `validate_canonical.py --dir self-docs --check` đạt 100% compliant.

### Task 3 — Memory Loader & Compact Index: `src/memory_loader.py`
- Quét các unit canonical, lọc metadata và preview 2 dòng đầu tiên.
- Gom nhóm theo 4 phân loại: Gotchas & Traps, Architecture & Core Rules, Operations & Runbooks, References.
- Sinh file `self-docs/MEMORY_INDEX.md` siêu nén (~30 tokens/unit).
- Tích hợp MCP tool `knowledgelib_get_memory_index(domain="self-docs")` trong `src/mcp_server.py`.
- Cập nhật `SKILL.md` bổ sung domain `self-docs` và tool MCP.

### Task 4 — Unit Tests (50/50 test suite passing)
- `tests/test_validate_canonical.py`: 5 tests kiểm thử validate hợp lệ, thiếu frontmatter, thiếu trường, auto-fix, directory scan.
- `tests/test_memory_loader.py`: 4 tests kiểm thử load canonical units, format compact index, export file, handle empty.
- Toàn bộ test cũ (Phase 1-6) + mới chạy qua `rtk proxy python3 -m pytest tests/ -q` đều xanh (50 passed).

---

## 3. Kế hoạch tiếp nối cho Harness Session (Next Steps)

### Task 5 — Tech-Log Extractor & Anonymizer: `src/extract_tech_notes.py`
- **Mục tiêu**: Đọc các file log / tài liệu từ nguồn (ví dụ `/Users/thaidt/Documents/CTD/Payroll CTD/self-docs/`), thực hiện:
  1. **Sanitize / Anonymize**:
     - Thay thế email nội bộ (`*@coteccons.vn` -> `user@company.test`).
     - Thay thế tên tổ chức/dự án nhạy cảm (`Coteccons`, `CTD` -> `Enterprise / Core System`).
     - Cắt bỏ các đoạn nhật ký cá nhân, sprint meeting chitchat, ticket tracking ID.
  2. **Canonicalize**:
     - Tự động gọi `generate_canonical_frontmatter` để gán metadata chuẩn.
     - Phân bổ vào thư mục mục tiêu: `self-docs/engine/`, `self-docs/security/`, `self-docs/database/`, hoặc `software/...`.
  3. **Hash Deduplication**:
     - Sử dụng `compute_content_hash` để chống trùng lặp.
- **Test**: `tests/test_extract_tech_notes.py` kiểm thử khả năng xóa PII/business data và sinh file canonical chuẩn.

### Task 6 — Tiered Retrieval Boost trong `src/agent_client.py`
- Trong hàm `search()` / thuật toán RRF của `KnowledgeLibClient`:
  - Thêm hệ số ưu tiên `self_docs_boost` (ví dụ 1.3x - 1.5x) cho các unit có `domain.startswith("self-docs")`.
  - Giúp các quy chuẩn nội bộ và runbook luôn được xếp hạng cao hơn tài liệu generic bên ngoài.
