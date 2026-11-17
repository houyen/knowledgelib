# Dùng KnowledgeLib trên nhiều máy cá nhân (MCP stdio local)

Không server, không mở cổng, không xác thực. Mỗi máy tự giữ một bản repo và tự dựng index.

## Máy mới
```bash
git clone <repo-url> knowledgelib_data && cd knowledgelib_data
python3 -m pip install -r requirements.txt
python3 src/import_knowledge.py --sync-only     # lần đầu tải model ~1 GB, dựng .chroma_db
```
Dùng trong dự án khác: thêm vào `.mcp.json` của dự án đó (đường dẫn tuyệt đối tới repo):
```json
{
  "mcpServers": {
    "knowledgelib": {
      "command": "python3",
      "args": ["/abs/path/knowledgelib_data/src/mcp_server.py"],
      "env": { "KNOWLEDGELIB_PATH": "/abs/path/knowledgelib_data" }
    }
  }
}
```
Trong chính repo này `.mcp.json` đã có sẵn.

## Cập nhật dữ liệu
```bash
git pull --ff-only
python3 src/import_knowledge.py --sync-only     # chỉ cần khi catalog.json đổi
```
`.chroma_db` không đồng bộ qua git; mỗi máy tự dựng, nên vector có thể lệch giữa các máy (kết quả chấp nhận được, BM25 giống nhau).

## Kiểm tra
```bash
python3 src/index_health.py                     # index khớp catalog?
python3 src/agent_client.py "thiết kế hệ thống" # tìm thử
python3 -m pytest -q
```

## Tuỳ chọn
- Web UI local: `python3 src/web_ui.py` (127.0.0.1:8000; đổi bằng `KNOWLEDGELIB_WEB_HOST/PORT`).
- Máy yếu RAM: `KNOWLEDGELIB_EMBED_MODEL=intfloat/multilingual-e5-small` (nhỏ hơn, phải dựng lại index và đo chất lượng).
- Chưa cần: `KNOWLEDGELIB_READONLY`, `KNOWLEDGELIB_EXCLUDE_DOMAINS`, `CF_ACCESS_*` (chỉ dùng khi đưa lên mạng, xem PHASE8_PLAN).
