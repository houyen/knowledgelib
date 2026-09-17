# Phase 6 — Query Gap Logging — Plan thi hành (cho Gemini CLI)

> Tài liệu cho agent headless (không hỏi lại được). Đọc hết trước khi sửa. Nếu thiếu thông tin, chọn phương án AN TOÀN NHẤT (không phá API cũ, không log dữ liệu nhạy cảm ra ngoài ý muốn) và ghi chú lại.

## Bối cảnh & lý do

Khi 1 câu hỏi không match được knowledge unit nào (`search()` trả `[]`), hệ thống hiện tại (đã có từ Phase 3) trả `should_fallback_to_llm: True` và dừng lại — **không lưu vết** câu hỏi đó ở đâu cả. Hệ quả: không biết được user/agent hay hỏi cái gì mà kho chưa có, nên không biết ưu tiên ingest tài liệu gì tiếp theo.

Mục tiêu Phase 6: ghi lại các "query miss" (không tìm thấy) vào 1 log file local, kèm 1 script tổng hợp để xem "top câu hỏi hay miss nhất" — biến việc chọn tài liệu cần nạp từ đoán mò sang có dữ liệu dẫn đường.

**Lưu ý cấu trúc repo hiện tại (đã đổi từ Phase 5):** code nằm trong `src/` (`src/agent_client.py`, `src/mcp_server.py`, `src/import_knowledge.py`, `src/web_ui.py`), dữ liệu (`catalog.json`, `.chroma_db/`, các domain folder) vẫn ở repo root. Mọi path mới trong plan này đặt trong `src/` cho code, và file log đặt ở repo root (cạnh `catalog.json`) vì nó là dữ liệu vận hành, không phải mã nguồn.

## Ràng buộc bao trùm

1. **Không bao giờ để việc logging làm crash luồng search chính** — mọi lệnh ghi log phải bọc `try/except`, lỗi ghi log chỉ `print` cảnh báo, không raise.
2. **Không log toàn bộ nội dung nhạy cảm ngoài ý muốn** — chỉ log: query text (nguyên văn), timestamp, nguồn gọi (`source`). Không log API key, không log nội dung file đang ingest.
3. File log **phải được gitignore** — đây là dữ liệu vận hành/query của người dùng, không phải knowledge content nên không commit vào repo public.
4. Không đổi signature của `search()`, `query_and_get()`, `knowledgelib_search` (MCP tool), route `/search` (web UI) — chỉ **thêm** lệnh gọi log ở nơi phát hiện "miss", không đổi giá trị trả về hiện có.
5. Sau khi code xong: chạy `rtk proxy python3 -m pytest tests/ -q`, đảm bảo toàn bộ test cũ (đang pass) + test mới đều xanh.

---

## Task 1 — Module ghi log: `src/query_miss_log.py` (file mới)

```python
def log_miss(query: str, source: str, repo_dir: str | None = None) -> None:
    """
    Append 1 dòng JSON vào <repo_dir>/query_misses.jsonl.
    source: định danh nơi gọi, ví dụ "query_and_get" | "mcp_search" | "web_ui".
    Không bao giờ raise ra ngoài -- lỗi ghi file chỉ print cảnh báo và return.
    repo_dir mặc định đọc từ KNOWLEDGELIB_PATH env (giống agent_client.py),
    fallback os.path.abspath(os.path.join(os.path.dirname(__file__), "..")).
    """
```
- Format mỗi dòng: `{"timestamp": "<ISO8601 UTC>", "query": "<nguyên văn>", "source": "<source>"}`.
- Dùng `datetime.now(timezone.utc).isoformat()` cho timestamp.
- Mở file bằng mode `"a"`, `encoding="utf-8"`, ghi `json.dumps(entry, ensure_ascii=False) + "\n"`.
- Tên file cố định: `query_misses.jsonl` — đặt ở `repo_dir` (root), KHÔNG đặt trong `src/`.

**Test:** `tests/test_query_miss_log.py` (file mới)
- `test_log_miss_appends_jsonl_line(tmp_path)`: gọi `log_miss("abc", "test_source", repo_dir=str(tmp_path))`, đọc lại file `tmp_path/query_misses.jsonl`, assert đúng 1 dòng, parse JSON được, có đủ 3 field, `query == "abc"`.
- `test_log_miss_appends_multiple_calls(tmp_path)`: gọi 2 lần liên tiếp, assert file có 2 dòng.
- `test_log_miss_never_raises_on_unwritable_path(tmp_path, monkeypatch)`: trỏ `repo_dir` vào 1 path không ghi được (ví dụ tạo file thường rồi trỏ path con vào trong nó, hoặc patch `open` để raise `OSError`) → assert `log_miss(...)` không raise exception.

---

## Task 2 — Gắn hook vào các điểm phát hiện "miss"

Có 3 điểm entry point độc lập hiện đang tự xử lý "không tìm thấy" theo cách khác nhau — phải gắn hook ở CẢ 3, không chỉ 1 chỗ trung tâm (vì `search()` là hàm primitive dùng nội bộ ở nhiều nơi khác nữa, ví dụ `is_knowledge_query()` gọi `vector_search()` trực tiếp — KHÔNG log miss ở đó, chỉ log ở các entry point thật sự đại diện "user/agent hỏi và không có kết quả"):

### 2a. `src/agent_client.py` — `KnowledgeLibClient.query_and_get()`
- Vị trí: nhánh `if not matched_units:` (hiện trả `{"status": "not_found", ...}`).
- Thêm: gọi `log_miss(query, source="query_and_get", repo_dir=self.data_path)` NGAY TRƯỚC khi return, bọc sẵn try/except đã có trong `log_miss` nên gọi trực tiếp không cần try/except lần 2 ở đây.
- Import: `from query_miss_log import log_miss` ở đầu file (cùng cách import phẳng như các module khác trong `src/`).

### 2b. `src/mcp_server.py` — tool `knowledgelib_search`
- Sau dòng `results = client.search(query, top_k=top_k)`, nếu `not results` (rỗng) → gọi `log_miss(query, source="mcp_search")` trước khi return.
- Import `log_miss` từ `query_miss_log` (cùng thư mục `src/`, theo pattern import hiện có của file này).

### 2c. `src/web_ui.py` — route `/search`
- Trong handler `search(...)`: sau khi có `results = get_client().search(q, top_k=top_k)` (chỉ khi `q.strip()` truthy, đúng nhánh hiện tại), nếu `q.strip()` và `not results` → gọi `log_miss(q, source="web_ui")`.
- KHÔNG log khi `q` rỗng (user chưa gõ gì, không phải 1 "miss" thật).

**Test:** thêm vào các file test hiện có, dùng `monkeypatch.setattr` để mock `log_miss` (KHÔNG ghi file thật trong test của agent_client/mcp_server/web_ui — việc ghi file thật đã test riêng ở Task 1):
- `tests/test_agent_client.py`: `test_query_and_get_not_found_logs_miss` — monkeypatch `agent_client.log_miss` bằng 1 `Mock`/list thu thập lời gọi, gọi `query_and_get("hoàn toàn không liên quan xyz123")`, assert mock được gọi đúng 1 lần với `query` khớp và `source="query_and_get"`.
- `tests/test_mcp_server.py`: `test_search_no_results_logs_miss` — tương tự, monkeypatch `mcp_server.log_miss`, gọi 1 query chắc chắn rỗng kết quả trong fixture catalog nhỏ, assert có gọi.
- `tests/test_web_ui.py`: `test_search_not_found_logs_miss` — monkeypatch `web_ui.log_miss`, gọi `/search?q=completelyunrelatedqueryxyz` (query đã dùng sẵn trong `test_search_not_found`), assert có gọi; test `/search?q=` (rỗng) KHÔNG gọi log_miss.

---

## Task 3 — Script tổng hợp: `src/query_gap_report.py` (file mới, CLI độc lập)

```python
def load_misses(log_path: str) -> list[dict]:
    """Đọc query_misses.jsonl, trả list dict. File không tồn tại -> trả []. Dòng lỗi JSON -> bỏ qua dòng đó, không crash."""

def aggregate_misses(misses: list[dict]) -> list[tuple[str, int]]:
    """
    Group theo query đã chuẩn hoá (strip + lower), đếm số lần xuất hiện.
    Trả list (query_chuẩn_hoá, count) sắp giảm dần theo count.
    """

def main():
    """argparse: --top N (default 20), --log-path (default <repo_root>/query_misses.jsonl).
    In ra bảng đơn giản: rank, count, query. Không cần format phức tạp (không phải web UI)."""
```
- Chạy độc lập: `python3 src/query_gap_report.py --top 20`.
- Không phụ thuộc `KnowledgeLibClient`/chromadb — chỉ đọc file JSONL thuần, để chạy nhanh không cần load catalog/vector db.

**Test:** `tests/test_query_gap_report.py`
- `test_aggregate_misses_counts_and_sorts`: input list dict giả (query trùng nhau khác hoa/thường/khoảng trắng) → assert gộp đúng, sort giảm dần.
- `test_load_misses_missing_file_returns_empty`: `load_misses("/path/khong/ton/tai.jsonl")` → `[]`.
- `test_load_misses_skips_malformed_lines`: file có 1 dòng JSON hỏng xen giữa 2 dòng hợp lệ → assert chỉ parse được 2 dòng hợp lệ, không raise.

---

## Task 4 — `.gitignore` + docs

- `.gitignore`: thêm dòng `query_misses.jsonl` (repo root, cạnh mục "Runtime State & Logs" đã có sẵn `*.log`).
- `SKILL.md`: thêm 1 đoạn ngắn ở mục có liên quan đến "Nguyên tắc Ưu tiên tuyệt đối Data Local" (chỗ nói về `should_fallback_to_llm`), ghi chú thêm: hệ thống tự log các query miss vào `query_misses.jsonl`, dùng `python3 src/query_gap_report.py --top 20` để xem câu hỏi hay thiếu data nhất — thông tin này giúp agent khác (hoặc chính user) biết nên ingest tài liệu gì tiếp theo.

---

## Thứ tự thực hiện

Task 1 → Task 2 → Task 3 → Task 4 (Task 3 độc lập với Task 2, có thể làm song song, nhưng Task 1 luôn phải xong trước vì Task 2/3 đều phụ thuộc `log_miss`/format file do Task 1 định nghĩa).

## Sau khi xong

- Chạy `rtk proxy python3 -m pytest tests/ -q`, xác nhận toàn bộ test (cũ + mới) pass.
- Không tự ý `git commit`/`git push` — dừng lại, báo kết quả cho user review trước.
