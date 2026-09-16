# Phase 5 — Ingestion cải thiện — Plan thi hành (cho Gemini CLI)

> Tài liệu này viết để một agent KHÔNG có context hội thoại (chạy headless, không hỏi lại được) vẫn code đúng. Đọc hết trước khi sửa file nào. Không tự suy diễn ngoài phạm vi mô tả — nếu thiếu thông tin, chọn phương án AN TOÀN NHẤT (không phá vỡ API cũ, không ghi đè dữ liệu thật) và ghi chú lại trong PR/commit message.

## Bối cảnh (đã verify bằng đọc code thật, không phải suy đoán)

- Repo: `knowledgelib_data`. File liên quan: `import_knowledge.py`, `agent_client.py`, `mcp_server.py`, `catalog.json`, `.env.example`.
- `.env.example` đã khai báo sẵn `GEMINI_API_KEY` — dự định dùng Gemini API cho splitting thông minh (Task 3), không cần chọn provider khác.
- `import_knowledge.py:24-26` — `REPO_DIR`, `CATALOG_PATH`, `DB_DIR` là hằng số module-level tính 1 lần lúc import (`os.path.abspath(os.path.dirname(__file__))`), **không đọc** `KNOWLEDGELIB_PATH` env var — khác với `agent_client.py` (đã sửa ở Phase 1) và `web_ui.py`/`mcp_server.py` (Phase 2/4). Đây là nợ kỹ thuật cần dọn trước (Task 0), vì không dọn thì KHÔNG viết được test cách ly (test sẽ đụng vào `catalog.json`/`.chroma_db` thật của repo).
- Bug thật đã phát hiện lúc test Phase 2 (đã fix bằng `git restore`, chưa fix trong code): `scan_and_collect_all_markdown_units()` (dòng 140-183) có `ignore_files` set (dòng 143) nhưng thiếu `"AGENTS.md"` → chạy `--sync-only` từng biến `AGENTS.md` thành 1 "unit" rác (`id: "AGENTS"`, content rỗng) trong `catalog.json`. Phải fix (Task 1).
- `run_import()` (dòng 227-274) là hàm callable đã tách sẵn ở Phase 2 — **KHÔNG được đổi tên tham số cũ hay thứ tự**, vì `main()` (CLI) và `mcp_server.py::knowledgelib_ingest` đang gọi theo tên (`file_path`, `domain_path`, `domain`, `entity_type`, `sync_only`). Chỉ được **thêm** tham số mới có giá trị mặc định.
- Test suite hiện tại: 19/19 pass (`tests/test_agent_client.py`, `tests/test_mcp_server.py`, `tests/test_web_ui.py`). Chưa có `tests/test_import_knowledge.py` — Phase 5 sẽ là lần đầu test file này.
- Cài deps: máy dev không có venv, dùng `python3 -m pip install --user --break-system-packages -r requirements.txt`. Chạy test bằng `rtk proxy python3 -m pytest tests/ -q` (không dùng `python3 -m pytest` trần — có wrapper `rtk` filter output gây hiểu lầm kết quả cũ/stale, xem lịch sử Phase 2).

## Ràng buộc bao trùm (áp dụng cho MỌI task dưới đây)

1. **Không chạy `--sync-only` hay bất kỳ lệnh ghi thật vào `catalog.json`/`.chroma_db` của repo thật** trong lúc phát triển/test. Luôn test qua `tmp_path` (pytest fixture) + `monkeypatch.setenv("KNOWLEDGELIB_PATH", str(tmp_path))`, giống pattern đã dùng trong `tests/test_agent_client.py` và `tests/test_web_ui.py`.
2. Không commit thay đổi `catalog.json`/`.chroma_db` thật trừ khi được yêu cầu rõ ràng.
3. Giữ backward-compat 100% cho `run_import()`, `main()` CLI, `knowledgelib_ingest` MCP tool — chỉ thêm, không sửa/xoá signature cũ.
4. `GEMINI_API_KEY` đọc từ `os.environ`, không hardcode, không log giá trị ra `print`/console/exception message.
5. Sau mỗi task: chạy toàn bộ `pytest` hiện có, đảm bảo không regression, rồi mới thêm test mới cho task đó.
6. Dùng đúng version dependency **thật sự cài được** trên máy (`pip show` / `importlib.metadata.version`) khi ghi vào `requirements.txt` — không đoán version.

---

## Task 0 — Fix nền tảng: `REPO_DIR`/`CATALOG_PATH`/`DB_DIR` đọc `KNOWLEDGELIB_PATH` env

**File:** `import_knowledge.py`

**Vấn đề cụ thể:** dòng 24-26:
```python
REPO_DIR = os.path.abspath(os.path.dirname(__file__))
CATALOG_PATH = os.path.join(REPO_DIR, "catalog.json")
DB_DIR = os.path.join(REPO_DIR, ".chroma_db")
```
Đây là hằng số đóng băng lúc import module — giống bug đã gặp ở `web_ui.py` Phase 4 (`DEFAULT_KNOWLEDGELIB_PATH` không đọc lại env khi test set qua `monkeypatch` sau khi module đã import). Nếu không sửa, mọi test Phase 5 (Task 1, 2, 3) sẽ không cô lập được khỏi dữ liệu thật.

**Cách sửa đề xuất (đơn giản nhất, ít đổi signature nhất):**
- Đổi 3 hằng số module-level thành 1 hàm:
  ```python
  def _repo_dir() -> str:
      return os.environ.get("KNOWLEDGELIB_PATH", os.path.abspath(os.path.dirname(__file__)))
  ```
- Trong mọi hàm hiện đang dùng `REPO_DIR`/`CATALOG_PATH`/`DB_DIR` như biến toàn cục (`save_units_to_tree`, `scan_and_collect_all_markdown_units`, `update_catalog_and_vector_db`), thay bằng gọi `_repo_dir()` tại đầu hàm và tính `catalog_path = os.path.join(repo_dir, "catalog.json")` cục bộ, thay vì dùng hằng số global. Liệt kê các chỗ cần sửa (đã grep, số dòng có thể lệch nhỏ sau Task 1/2 chèn code — search theo tên biến, không theo số dòng cứng):
  - `save_units_to_tree()`: dùng `REPO_DIR` để tính `target_dir` và `unit_id` (relpath).
  - `scan_and_collect_all_markdown_units()`: dùng `REPO_DIR` cho `os.walk`.
  - `update_catalog_and_vector_db()`: dùng `CATALOG_PATH` để đọc/ghi, dùng `REPO_DIR` khi gọi `reindex_chromadb(catalog_data, REPO_DIR)`.
- `sync_knowledgelib.py::reindex_chromadb(catalog_data, target_dir)` đã nhận `target_dir` làm tham số — không cần sửa file này, chỉ cần đảm bảo `update_catalog_and_vector_db()` truyền đúng `_repo_dir()` thay vì hằng số cũ.

**Test:** `tests/test_import_knowledge.py` (file mới) — fixture `repo(tmp_path, monkeypatch)` giống hệt pattern trong `tests/test_web_ui.py` (tạo `catalog.json` tối thiểu, set `KNOWLEDGELIB_PATH`). Viết 1 test đơn giản xác nhận `update_catalog_and_vector_db(sync_only=True)` đọc/ghi đúng vào `tmp_path/catalog.json`, KHÔNG đụng vào `catalog.json` thật của repo (assert file thật không đổi mtime, hoặc đơn giản hơn: assert nội dung `tmp_path/catalog.json` sau khi chạy khác với nội dung catalog thật — đủ để chứng minh cô lập).

---

## Task 1 — Fix bug: `scan_and_collect_all_markdown_units()` bỏ sót `AGENTS.md`

**File:** `import_knowledge.py`, hàm `scan_and_collect_all_markdown_units()`, dòng có `ignore_files = {...}` (hiện tại: `{'SKILL.md', 'AGENT_PROMPT_SNIPPET.md', 'agent.md', 'walkthrough_index.md', 'walkthrough_index_full.md', 'README.md', 'LICENSE.md'}`).

**Sửa:** thêm `'AGENTS.md'` vào set này. Đồng thời rà lại thư mục gốc repo (`ls` root) để xác nhận không còn file `.md` non-knowledge nào khác lọt ignore list — nếu có, thêm luôn (ví dụ `PHASE5_PLAN.md` chính tài liệu này cũng phải được ignore, vì nó không phải Knowledge Unit — thêm `'PHASE5_PLAN.md'` vào set).

**Test:** `tests/test_import_knowledge.py::test_sync_only_ignores_non_knowledge_root_files` — trong fixture `repo`, tạo thêm `tmp_path/AGENTS.md` với nội dung bất kỳ, gọi `scan_and_collect_all_markdown_units()` (cần Task 0 xong để hàm này đọc đúng `tmp_path` qua env), assert kết quả **không chứa** `id == "AGENTS"`.

---

## Task 2 — Dedup check trước khi import (content hash)

**Mục tiêu:** tránh 1 tài liệu bị nạp trùng nhiều lần tạo ra nhiều unit trùng nội dung trong catalog.

**File:** `import_knowledge.py`

1. **Hàm mới** `compute_content_hash(content: str) -> str`:
   - Chuẩn hoá: `content.strip().lower()`, loại khoảng trắng thừa (ví dụ `re.sub(r"\s+", " ", ...)`) trước khi hash, để tránh false-negative do khác biệt whitespace/newline vô hại.
   - Trả `hashlib.sha256(normalized.encode("utf-8")).hexdigest()`.
   - Đặt gần đầu file, cạnh các hàm helper khác (sau `parse_pdf_pages`, trước `split_text_into_units`).

2. **Field mới trong schema unit**: `content_hash`.
   - `save_units_to_tree()`: thêm `content_hash` vào cả `meta` (ghi vào YAML frontmatter của file `.md`) và `saved_file_infos` (dict trả về đưa vào catalog).
   - `scan_and_collect_all_markdown_units()`: đọc `meta.get("content_hash")` từ frontmatter khi có, đưa vào `unit_entry`. Nếu file cũ không có field này (unit đã tồn tại trước Phase 5), để `None`/rỗng — không tính lại hash từ content_preview (không đủ dữ liệu, content_preview bị cắt 300 ký tự).

3. **Hàm mới** `find_duplicate_unit_id(content_hash: str, existing_units: list[dict]) -> str | None`:
   - Duyệt `existing_units`, so `u.get("content_hash") == content_hash` (bỏ qua unit không có hash), trả `id` đầu tiên khớp, hoặc `None`.

4. **Sửa `run_import()`**:
   - Trước khi gọi `save_units_to_tree(units, ...)`, load catalog hiện tại để lấy `existing_units` (đọc `CATALOG_PATH`/`_repo_dir()`-based path; nếu file chưa tồn tại → `existing_units = []`, không lỗi).
   - Với mỗi `unit` trong `units` (kết quả `split_text_into_units`), tính `compute_content_hash(unit["content"])`. Nếu `find_duplicate_unit_id(...)` trả về khác `None` → **loại unit này khỏi danh sách sẽ ghi file**, gom vào `skipped_duplicates: [{"content_hash":..., "existing_unit_id":...}]`.
   - Chỉ gọi `save_units_to_tree()` với các unit KHÔNG trùng.
   - Response `run_import()` thêm field:
     ```python
     "skipped_duplicates": [...],  # list, rỗng nếu không có trùng
     ```
     `unit_count` giữ nguyên ý nghĩa cũ (chỉ đếm unit MỚI thực sự ghi ra file).

**Test:**
- `test_run_import_skips_exact_duplicate_on_second_call`: gọi `run_import(file_path=<file .md có content cố định>, domain_path=..., sync_only=False)` 2 lần liên tiếp trên cùng `tmp_path` repo. Lần 2: assert `result["unit_count"] == 0`, `len(result["skipped_duplicates"]) == 1`, và **không có file `.md` mới nào được tạo thêm** trong `domain_path` (đếm số file trước/sau).
- `test_compute_content_hash_normalizes_whitespace`: 2 chuỗi khác nhau chỉ ở khoảng trắng/newline phải cho cùng hash.

---

## Task 3 — LLM-assisted splitting (Gemini API), fallback về regex splitter cũ

**Mục tiêu:** `split_text_into_units()` hiện dựa heading-regex cứng (`chapter|day|section|part` + số) — fail với tài liệu không theo format đó. Thay bằng LLM phân tách ngữ nghĩa, nhưng **không được xoá hàm regex cũ** — nó là fallback bắt buộc khi không có API key / gọi lỗi / response không hợp lệ.

1. **Dependency mới**: Gemini Python SDK. Gemini (agent thực thi) phải tự chạy `pip install` để xác định tên package + version thật đang cài được (gợi ý: SDK chính thức hiện tại là `google-genai`, nhưng PHẢI verify bằng cài đặt thật, không copy tên này mù quáng — có thể đã đổi). Ghi version thật vào `requirements.txt` theo pattern `>=X.Y.Z,<X+1.0` như các dep khác trong file.

2. **File mới `llm_splitter.py`** (tách riêng khỏi `import_knowledge.py`, để `import_knowledge.py` không phụ thuộc cứng SDK ngoài khi ingest không cần LLM):
   ```python
   def split_text_with_llm(
       pages: list[tuple[int, str]],
       doc_name: str,
       api_key: str | None = None,
   ) -> list[dict] | None:
       """
       Trả list[{"num": str, "title": str, "content": str}] giống schema của
       split_text_into_units() trong import_knowledge.py, để 2 hàm hoán đổi
       cho nhau được ở call site.
       Trả None (KHÔNG raise) nếu: thiếu api_key, SDK lỗi, call thất bại,
       response không parse được JSON hợp lệ, hoặc bất kỳ unit nào thiếu
       "title"/"content" non-empty -- để caller fallback an toàn về regex.
       """
   ```
   - `api_key` mặc định lấy từ `os.environ.get("GEMINI_API_KEY")` nếu không truyền.
   - Giới hạn kích thước request: text quá dài (ước lượng ~30-40k ký tự là ngưỡng an toàn, Gemini agent tự điều chỉnh theo giới hạn context thật của model đang dùng) → chia theo `pages` thành nhiều batch, gọi API nhiều lần, nối kết quả list lại (đánh lại `num` tuần tự sau khi nối, tránh trùng số giữa các batch).
   - Prompt: yêu cầu model trả **JSON thuần** (không markdown code fence) là 1 list object `{"title": ..., "content": ...}` theo ranh giới chương/mục ngữ nghĩa thật trong text, giữ nguyên văn nội dung gốc (không tóm tắt, không paraphrase — đây là ingest tri thức, không phải summarize).
   - Validate response: `json.loads` trong `try/except`, nếu lỗi → `return None`. Validate từng phần tử có `title`/`content` non-empty string, nếu không → loại phần tử đó (không fail toàn bộ vì 1 phần tử lỗi) hoặc `return None` nếu SAU KHI loại còn 0 phần tử.

3. **Sửa `run_import()`** trong `import_knowledge.py`:
   - Thêm tham số mới `use_llm_split: bool = True` (default bật — nhưng hàm `split_text_with_llm` tự trả `None` nếu không có key, nên hành vi hiện tại của agent không có `GEMINI_API_KEY` vẫn y hệt trước đây, không breaking).
   - Logic thay thế dòng `units = split_text_into_units(pages, doc_name)`:
     ```python
     units = None
     if use_llm_split:
         units = split_text_with_llm(pages, doc_name)
     split_method = "llm" if units else "regex"
     if not units:
         units = split_text_into_units(pages, doc_name)
     ```
   - Response dict thêm field `"split_method": split_method`.

4. **Sửa `mcp_server.py::knowledgelib_ingest`**:
   - Thêm param `use_llm_split: bool = True`, truyền thẳng xuống `run_import(...)`.
   - Cập nhật docstring tool mô tả hành vi mới (LLM split mặc định, fallback regex).

5. **Sửa `main()` CLI** trong `import_knowledge.py` (tuỳ chọn nhưng khuyến nghị):
   - Thêm flag `--no-llm-split` (action `store_true`) → khi bật, gọi `run_import(..., use_llm_split=False)`. Giữ mặc định CLI hiện tại (không flag) = `use_llm_split=True`.

**Test:** `tests/test_llm_splitter.py` (file mới, KHÔNG được gọi Gemini API thật trong CI — mock hoàn toàn):
- `test_no_api_key_returns_none_without_calling_api`: `monkeypatch.delenv("GEMINI_API_KEY", raising=False)`, gọi `split_text_with_llm(pages, "doc")` → assert `None`, và mock ở tầng SDK client để assert **không có lời gọi mạng nào xảy ra** (ví dụ patch class client, assert `not called`).
- `test_valid_response_parses_units`: mock SDK trả JSON hợp lệ → assert list unit đúng schema `num/title/content`.
- `test_invalid_json_response_returns_none`: mock SDK trả text không phải JSON → assert `None`.
- `test_run_import_falls_back_to_regex_when_llm_returns_none`: trong `tests/test_import_knowledge.py`, `monkeypatch` `llm_splitter.split_text_with_llm` (hoặc patch tại điểm import trong `import_knowledge.py`) trả `None`, gọi `run_import(file_path=..., use_llm_split=True)` → assert `result["split_method"] == "regex"` và unit vẫn được tạo bình thường (không lỗi, không rỗng).

---

## Thứ tự thực hiện

**Task 0 → Task 1 → Task 2 → Task 3**, theo đúng thứ tự vì:
- Task 0 là điều kiện bắt buộc để viết được test cách ly cho Task 1/2/3 (không có nó, mọi test sau sẽ đụng dữ liệu thật).
- Task 1 là fix bug nhanh, độc lập, không phụ thuộc Task 2/3.
- Task 2 (dedup) độc lập với LLM, nên làm trước Task 3 để có nền dedup sẵn khi LLM splitter sinh ra unit mới (tránh trùng lặp ngay từ lần đầu tích hợp LLM).
- Task 3 (LLM splitter) effort/risk cao nhất (dependency ngoài, gọi API thật, cần mock test kỹ) — để cuối, có fallback an toàn về hành vi cũ nên không block release nếu API có vấn đề.

## Sau khi xong cả 4 task

- Chạy `rtk proxy python3 -m pytest tests/ -q`, xác nhận **toàn bộ** test (cũ + mới) pass, không chỉ test mới.
- Không tự ý chạy `git commit`/`git push` — dừng lại, báo cáo kết quả cho user review trước khi commit (theo protocol chung của repo: chỉ commit khi được yêu cầu rõ).
