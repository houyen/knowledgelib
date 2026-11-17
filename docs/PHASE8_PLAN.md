# PHASE 8 — Dùng KnowledgeLib trên nhiều máy cá nhân

## Quyết định
- Mục đích cá nhân, không chia sẻ. VPS duy nhất (2 GB / 1 vCPU) đang chạy `tu-vi-app-poc`, không đủ cho model e5-base (~2,5-3 GB khi chạy web + MCP). **Bỏ VPS, bỏ Cloudflare Access, bỏ bootstrap script.**
- Chọn hướng A: mỗi máy clone repo, chạy MCP stdio local. Hướng dẫn: `docs/MULTI_MACHINE.md`.

## Đã làm (Phase 1, commit 9d6488f)
Chuẩn bị sẵn cho trường hợp phải đưa lên mạng sau này; mặc định tắt, hành vi cũ không đổi.
- MCP streamable-http qua env; `KNOWLEDGELIB_READONLY=1` bỏ ingest và memory-index.
- `KNOWLEDGELIB_EXCLUDE_DOMAINS` lọc unit (MCP + web UI, 404).
- `src/access_auth.py`: middleware JWT Cloudflare Access (`CF_ACCESS_TEAM`, `CF_ACCESS_AUD`).
- Web UI host/port từ env; chặn path traversal khi đọc unit.
- Test: `tests/test_access_and_readonly.py`.

## Phương án dự phòng (chỉ làm khi cần)
- **B. Tunnel từ Mac**: `cloudflared` + Access trên máy cá nhân, dùng code Phase 1. Chỉ truy cập được khi Mac bật. Với MCP cần service token (client MCP không làm được Email OTP).
- **C. VPS nhẹ**: một process gộp web + MCP, không nạp model (BM25 + alias tiếng Việt), ~200-300 MB RAM. Đo golden set trước khi chấp nhận mất tìm kiếm ngữ nghĩa.
- **D. C + `multilingual-e5-small`** (~120 MB model): ~500-700 MB RAM, sát giới hạn khi chung với tu-vi.

## Rủi ro còn lại
- Repo public: `self-docs/` nằm trong lịch sử GitHub, độc lập với hướng triển khai (xử lý ở mục 4 của backlog).
- Index vector lệch giữa các máy vì mỗi máy tự dựng.
- `query_misses.jsonl` phình dần: cần logrotate hoặc giới hạn kích thước.
