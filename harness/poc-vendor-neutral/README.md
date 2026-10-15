# my-agent-harness

Personal Minimal Viable Agent Harness. Vendor-neutral: 1 policy.yaml → gen-converters.py sinh wiring cho Claude / opencode / Cursor / Codex / Kiro / CI / pre-commit.

Nguồn gốc: chiết từ harness tham khảo (Claude). Từ 2026-10-15 rút gọn còn 6 rule thật sự có dấu vết dùng (audit log + hook); các rule llmwiki/ADR/proposal/pull-gate đã bỏ vì không repo nào có đối tượng để gác.

## Cài vào 1 dự án bất kỳ

```bash
git clone --depth 1 https://github.com/houyen/my-agent-harness.git /tmp/my-agent-harness
bash /tmp/my-agent-harness/install.sh /path/to/target-project
```

Cờ:
- `--vendor claude,opencode,cursor,codex,kiro` — ép danh sách vendor (mặc định tự dò)
- `--no-verify` — bỏ chạy demo.sh + test-broad.sh sau khi cài
- `--clean` — gỡ bản cũ trước khi cài
- `--with-wiki` — seed khung llmwiki/ (raw/, wiki/..., index.md, log.md). Chỉ là thư mục; hiện KHÔNG còn rule nào gác wiki
- `--with-skills` — cài skill llmwiki (global, qua npx)
- `--with-knowledgelib` — đăng ký MCP KnowledgeLib GLOBAL (xem mục dưới)
- `--full` — bật cả 4 (--with-wiki --with-skills --with-knowledgelib)

## Rule đang gác

| ID | Tên | Loại | Chặn? | Việc làm |
|---|---|---|---|---|
| R4 | audit-log | hook `PostToolUse` | không | Ghi `.claude/audit/audit.jsonl` + `log.md` mỗi Write/Edit |
| R8 | session-health | hook `SessionStart` | không | Báo số rule + check drift policy |
| R19 | knowledgelib-nudge | hook `UserPromptSubmit` | không | Nhắc tra `knowledgelib_search` mỗi N prompt |
| R20 | self-docs-canonical | `require_frontmatter` | có (session + repo) | `self-docs/*.md` phải có 6 trường canonical + body |
| R21 | self-docs-sync | hook `Stop` | không | Sanitize + sync self-docs sang KnowledgeLib |
| R22 | orca-browser-only | hook `PreToolUse` | có | Cấm mở trình duyệt hệ thống, dùng Orca |

ID giữ nguyên số cũ; khoảng trống (R1–R3, R5–R7, R9–R18) là rule đã bỏ.

## Sửa luật

Sửa `policy.yaml` → chạy lại `python3 gen-converters.py` (sinh `out/`) hoặc chạy lại `install.sh` (tự gen + cắm).

## Browser policy (R22)

- **R22 orca-browser-only**: hook `PreToolUse` (Bash) chặn (exit 2) lệnh mở trình duyệt mặc định của hệ thống — `open <url|*.html>`, `open -a <browser>`, `xdg-open`, `python -m webbrowser`, `osascript ... open location` — và nhắc dùng browser của Orca (`orca tab create --url ...`). Site chặn browser nhúng (vd Google sign-in) thì in URL cho user tự dán, không tự mở Chrome. Mở khoá tạm: `HARNESS_ALLOW_SYSTEM_BROWSER=1`. Chỉ soi token đầu mỗi đoạn shell nên không chặn nhầm commit message; `sudo -u ... open` là gap đã biết (fail-open).

## Rule code theo ngôn ngữ (rules-pull)

Bộ rule code (Go, JS/TS...) lưu trong knowledgelib dạng KU `software/coding-rules/<lang>-code-rules.md`; harness kéo về từng repo:

```bash
python3 bin/rules-pull.py --lang js-ts,go --root /path/to/repo [--kl ~/Documents/Repo/knowledgelib_data]
python3 bin/rules-pull.py --lang go --diff     # xem KU đã đổi gì so với rules.lock, không ghi
python3 bin/rules-pull.py --lang go --check    # exit 1 nếu repo lệch KU (dùng cho CI)
python3 bin/rules-pull.py --lang go --wire-claude   # thêm @docs/rules/go.md vào CLAUDE.md
```

- Sinh `docs/rules/<js|go>.md` (không sửa tay) + `rules.lock` (version + hash từng rule → update luôn có diff).
- `rules.local.yaml` (repo tự viết, pull không ghi đè): `overrides: [{id, action: disable|severity, severity, reason}]`. **`reason` bắt buộc.**
- `rules.local.md` (repo tự viết, pull không ghi đè): ghi chú riêng của repo (stack, quy ước đặc thù); nối nguyên văn vào cuối `docs/rules/<out>.md` dưới heading `## Ghi chú riêng của repo (rules.local.md)`.
- `rules.lock` theo dõi `local_notes_sha`: sửa hoặc xóa `rules.local.md` làm `--check` báo lệch và `--diff` in `~ rules.local.md`.
- Chưa sinh config lint (eslint/golangci) từ dữ liệu — mới sinh tài liệu; bước sau.
- Test: `bash test-rules.sh`.

### Đề xuất rule mới từ repo (rules-propose)

Hàng đợi đề xuất rule từ repo lên KU, duyệt trước khi merge vào knowledgelib:

```bash
# Thêm đề xuất vào rules-proposals/<lang>/<ID>.yaml
python3 bin/rules-propose.py add --lang go --id GO-ERR-05 --severity warn --kind review \
  --statement "..." --evidence "..." --origin "..." [--scope prod,tests] [--root .] [--kl PATH]

# Xem danh sách đề xuất (pending / merged)
python3 bin/rules-propose.py list [--lang go] [--root .]

# Merge đề xuất vào KU (tăng version, cập nhật last_verified; chỉ chạy khi có duyệt)
python3 bin/rules-propose.py merge --lang go --id GO-ERR-05 --approve-by "<tên>" [--patch] [--root .] [--kl PATH]
```

- Test: `bash test-propose.sh`.

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
bash demo.sh           # 8 case nhanh (R20 path/hook/files, fail-open, sinh wiring)
bash test-broad.sh     # 38 case (R20 canonical, robustness, R22 browser-guard)
bash test-rules.sh     # rules-pull
bash test-propose.sh   # rules-propose
```


## Không mang theo (đặc thù dự án gốc, không vendor-neutral)

- Rule đã bỏ 2026-10-15 (R1–R3, R5–R7, R9–R18: raw/wiki/proposal/ADR/pull-gate/seq-glass/no-ai-attribution) và validator production của chúng (`proposal_complete.py`, `decision_adr.py`, `no_ai_attribution.py`, `patterns_guard.py`, `report_show_path.py`). Muốn lấy lại: `git log -- policy.yaml` trước commit rút gọn.
- `~/.claude/harness` global engine + `install-harness.sh --global` — cơ chế global-shared riêng của bootstrap cũ (GH#51/council-038), không cần cho bộ minimal này.
- Skill llmwiki (`npx skills add <owner>/<repo>#<ref> --global`) — cài riêng, không phải phần của harness. `install.sh --with-skills` cần đặt `SKILLS_REF` tường minh.

## Tuỳ chọn tải từ mạng (opt-in, mặc định TẮT)
Không có gì tự tải/chạy mã từ xa. Chỉ bật khi bạn tự đặt env, trỏ tới nguồn bạn tin cậy:
- `REPO_RAW=<raw url>` — `install.sh --with-wiki` tải overstack.html/templates và có thể chạy `install-harness.sh --global` từ nguồn đó.
- `SKILLS_REF=<owner>/<repo>#<ref>` — `install.sh --with-skills`.
- `HARNESS_REMOTE_POLICY=<raw url policy.yaml>` — hook đầu phiên so policy với bản gốc.

## License
MIT — dùng, sửa, phân phối lại, kể cả biến thành sản phẩm của riêng bạn. Xem [LICENSE](LICENSE).
