# my-agent-harness

Personal Minimal Viable Agent Harness. Vendor-neutral: 1 policy.yaml → gen-converters.py sinh wiring cho Claude / opencode / Cursor / Codex / Kiro / CI / pre-commit.

Nguồn gốc: trích từ `harness/poc-vendor-neutral/` (Payroll CTD, 2026-07-16), verify lại standalone 2026-09-17 (demo.sh 13/13, test-broad.sh 74/74 PASS, không dính path/tên công ty).

## Cài vào 1 dự án bất kỳ

```bash
git clone <this-repo> /tmp/my-agent-harness
bash /tmp/my-agent-harness/install.sh /path/to/target-project
```

Cờ:
- `--vendor claude,opencode,cursor,codex,kiro` — ép danh sách vendor (mặc định tự dò)
- `--no-verify` — bỏ chạy demo.sh + test-broad.sh sau khi cài
- `--clean` — gỡ bản cũ trước khi cài
- `--with-wiki` — seed khung llmwiki/ (raw/, wiki/concepts, entities, sources/draft, index.md, log.md)
- `--with-skills` — cài skill llmwiki (global, qua npx)
- `--with-knowledgelib` — đăng ký MCP KnowledgeLib GLOBAL (xem mục dưới)
- `--full` — bật cả 4 (--with-wiki --with-skills --with-knowledgelib)

## Sửa luật

Sửa `policy.yaml` (R1–R21) → chạy lại `python3 gen-converters.py` (sinh `out/`) hoặc chạy lại `install.sh` (tự gen + cắm).

## KnowledgeLib & Self-Docs (R19–R21)

KnowledgeLib KHÔNG phải add-on riêng từng repo — là **1 kho tri thức DUY NHẤT dùng chung mọi repo** bạn làm việc, đăng ký GLOBAL ở `~/.claude.json` (`mcpServers.knowledgelib`), không phải project-scoped `.mcp.json`. Cài bằng `--with-knowledgelib` (hoặc `--full`):

```bash
KNOWLEDGELIB_HOME=/path/to/knowledgelib_data bash install.sh /path/to/project --with-knowledgelib
```

Mặc định `KNOWLEDGELIB_HOME=~/Documents/Repo/knowledgelib_data`. Idempotent — đã có entry thì bỏ qua, không đè.

- **R19 knowledgelib-nudge**: hook `UserPromptSubmit` nhắc agent tra KnowledgeLib khi cần kiến thức domain.
- **R20 self-docs-canonical**: gác cổng ghi file `self-docs/*.md` bắt buộc tuân thủ 6 trường YAML Frontmatter chuẩn (`id`, `canonical_question`, `aliases`, `entity_type`, `domain`, `last_verified`) và body không rỗng.
- **R21 self-docs-sync**: hook `Stop` tự động sanitize (khử PII/tên công ty) và đẩy tài liệu `self-docs/` về kho KnowledgeLib tập trung, đồng thời rebuild Memory Index. Có thể chạy tay bằng `python3 bin/sync-to-knowledgelib.py`.

**Nguyên tắc kiến trúc — On-Demand RAG vs Working Memory:**
- **Zero Eager Context Ingestion**: Tuyệt đối KHÔNG nạp toàn bộ KnowledgeLib hay mục lục index vào context của agent lúc bắt đầu phiên. Context của agent chỉ dành cho Working Memory của dự án hiện tại (`CLAUDE.md`, context task), tránh ô nhiễm ngữ cảnh và cạn token budget khi kho tri thức phình to.
- **Pull on-demand (RAG)**: Agent giữ context sạch; chỉ gọi MCP tool `knowledgelib_search` khi gặp câu hỏi domain-knowledge đã được index.
- Dữ liệu trả về chỉ làm **nền tảng và tham khảo**; AI chủ động đối chiếu và bổ sung thêm kiến thức hiện đại, chuyên sâu của AI để tối ưu câu trả lời.


**Di chuyển lên server nhà sau này:** chỉ sửa 1 chỗ — entry `mcpServers.knowledgelib` trong `~/.claude.json` (đổi `command`/`args`/`env` sang cách trỏ tới server mới) — không đụng project nào khác, vì mọi repo đều trỏ chung 1 entry global này.

## Test

```bash
bash demo.sh          # 13 case nhanh
bash test-broad.sh    # 80 case đầy đủ (bao gồm R20 canonical)
```


## Không mang theo (đặc thù Payroll CTD, không vendor-neutral)

- `harness/validators/*.py` (proposal_complete.py, decision_adr.py, no_ai_attribution.py, patterns_guard.py, report_show_path.py) — bản production siết hơn declarative rule ở đây, KHÔNG copy sang vì gắn với llmwiki layout riêng của repo đó.
- `~/.claude/harness` global engine + `install-harness.sh --global` — cơ chế global-shared riêng của bootstrap cũ (GH#51/council-038), không cần cho bộ minimal này.
- Skill llmwiki qua `npx skills add rheinmir/setup#orca --global` — cài riêng, không phải phần của harness.

## Origin
- Trích từ `/Users/thaidt/Documents/CTD/Payroll CTD/harness/poc-vendor-neutral/` (harness/foundation.yaml, commit context Payroll CTD)
- Ngày trích: 2026-09-17
