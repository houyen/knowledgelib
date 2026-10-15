#!/usr/bin/env bash
# setup-9router.sh — cấu hình client (OpenCode / Claude Code / Gemini CLI) trỏ vào 9router local.
# Idempotent. KHÔNG chứa bí mật: key lấy từ env / file ~/.9router.env, mật khẩu dashboard từ env.
#
#   bash setup-9router.sh        # hỏi key + mật khẩu dashboard (nhập ẩn, KHÔNG vào shell history)
#   bash setup-9router.sh --multi  # thêm: cài launcher 9router-multi, provider 9router-b (:20129), alias oc-all,
#                                  # combo 'all' cho instance 2 (xem README: kiến trúc 2 instance)
#   NINEROUTER_URL=http://localhost:20128 (mặc định)
# Chạy không tương tác (CI): đặt NINEROUTER_KEY / NINEROUTER_DASH_PASSWORD từ secret store,
# đừng gõ inline trên dòng lệnh (sẽ lọt vào ~/.zsh_history).
set -euo pipefail

URL="${NINEROUTER_URL:-http://localhost:20128}"
URL2="${NINEROUTER_URL2:-http://localhost:20129}"   # instance 2 (chỉ dùng với --multi)
MULTI=0; for a in "$@"; do [ "$a" = "--multi" ] && MULTI=1; done
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENVF="$HOME/.9router.env"
OCJ="$HOME/.config/opencode/opencode.json"
ZRC="$HOME/.zshrc"
G9="$HOME/.gemini-9r/.gemini/settings.json"

say() { printf '[9router] %s\n' "$*"; }

# nhập ẩn khi chạy tương tác và chưa có env
if [ -t 0 ]; then
  if [ -z "${NINEROUTER_KEY:-}" ]; then
    read -rsp "[9router] API key (Enter để bỏ qua): " NINEROUTER_KEY; echo
  fi
  if [ -z "${NINEROUTER_DASH_PASSWORD:-}" ]; then
    read -rsp "[9router] Mật khẩu dashboard (Enter để bỏ qua): " NINEROUTER_DASH_PASSWORD; echo
  fi
fi

# 1) key file (chmod 600, tạo file với umask chặt trước khi ghi)
if [ -n "${NINEROUTER_KEY:-}" ]; then
  ( umask 077; printf 'export NINEROUTER_KEY=%q\n' "$NINEROUTER_KEY" > "$ENVF" ); chmod 600 "$ENVF"
  say "ghi key vào $ENVF"
elif [ ! -e "$ENVF" ]; then
  printf 'export NINEROUTER_KEY="PASTE_KEY_HERE"\n' > "$ENVF"; chmod 600 "$ENVF"
  say "tạo $ENVF (placeholder) — dán key từ dashboard $URL/dashboard vào đó"
else
  say "giữ nguyên $ENVF"
fi

# 2) OpenCode provider (không ghi đè file có sẵn)
if [ -e "$OCJ" ]; then
  say "$OCJ đã có — KHÔNG ghi đè. Thêm tay provider '9router' nếu chưa có (xem README.md)."
else
  mkdir -p "$(dirname "$OCJ")"
  cat > "$OCJ" <<EOF
{
  "\$schema": "https://opencode.ai/config.json",
  "provider": {
    "9router": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "9router",
      "options": { "baseURL": "$URL/v1", "apiKey": "{env:NINEROUTER_KEY}" },
      "models": {
        "ag/gemini-3.8-flash-high": {},
        "ag/gemini-3.1-pro-low": {},
        "ag/claude-sonnet-4-6": {},
        "fast": {},
        "smart": {}
      }
    }
  },
  "model": "9router/fast"
}
EOF
  say "tạo $OCJ"
fi

# 2b) --multi: launcher + provider cho instance 2 (idempotent, merge JSON, không ghi đè phần có sẵn)
if [ "$MULTI" = 1 ]; then
  mkdir -p "$HOME/.local/bin"
  cp "$HERE/9router-multi" "$HOME/.local/bin/9router-multi" && chmod +x "$HOME/.local/bin/9router-multi"
  say "cài launcher → ~/.local/bin/9router-multi (cần ~/.local/bin trong PATH)"
  URL2="$URL2" OCJ="$OCJ" python3 - <<'PY'
import json, os
p = os.environ["OCJ"]
d = json.load(open(p)) if os.path.exists(p) else {"$schema": "https://opencode.ai/config.json", "provider": {}}
prov = d.setdefault("provider", {})
if "9router-b" not in prov:
    prov["9router-b"] = {
        "npm": "@ai-sdk/openai-compatible", "name": "9router set2",
        "options": {"baseURL": os.environ["URL2"] + "/v1", "apiKey": "{env:NINEROUTER_KEY}"},
        "models": {"all": {"name": "Combo all (set2)"}},
    }
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(d, open(p, "w"), indent=2, ensure_ascii=False); open(p, "a").write("\n")
    print("[9router] thêm provider 9router-b vào", p)
else:
    print("[9router] provider 9router-b đã có — bỏ qua")
PY
fi

# 3) Gemini CLI: home riêng, auth bằng API key (không đụng ~/.gemini OAuth)
mkdir -p "$(dirname "$G9")"
[ -e "$G9" ] || printf '{\n  "security": { "auth": { "selectedType": "gemini-api-key" } }\n}\n' > "$G9"

# 4) block ~/.zshrc (đánh dấu để không chèn lặp)
if grep -q '>>> 9router-config >>>' "$ZRC" 2>/dev/null; then
  say "$ZRC đã có block 9router-config — bỏ qua"
else
  cat >> "$ZRC" <<EOF

# >>> 9router-config >>>
[ -f ~/.9router.env ] && source ~/.9router.env
# Claude Code qua 9router. \`claude\` thường vẫn là Claude thật. KHÔNG export ANTHROPIC_BASE_URL toàn cục.
claude-ag() {
  ANTHROPIC_BASE_URL=$URL \\
  ANTHROPIC_AUTH_TOKEN="\$NINEROUTER_KEY" \\
  ANTHROPIC_MODEL=smart \\
  ANTHROPIC_DEFAULT_SONNET_MODEL=smart \\
  ANTHROPIC_DEFAULT_OPUS_MODEL=ag/claude-opus-4-6-thinking \\
  ANTHROPIC_DEFAULT_HAIKU_MODEL=ag/gemini-3.8-flash-high \\
  claude "\$@"
}
alias oc-fast='opencode -m 9router/fast'
alias oc-smart='opencode -m 9router/smart'
alias oc-flash='opencode -m 9router/ag/gemini-3.8-flash-high'
# Gemini CLI: cần bearer vì 9router không nhận header x-goog-api-key
gemini-9r() {
  GEMINI_CLI_HOME=\$HOME/.gemini-9r \\
  GEMINI_API_KEY_AUTH_MECHANISM=bearer \\
  GOOGLE_GEMINI_BASE_URL=$URL \\
  GEMINI_API_KEY="\$NINEROUTER_KEY" \\
  gemini -m "\${GEMINI_9R_MODEL:-smart}" "\$@"
}
# <<< 9router-config <<<
EOF
  say "thêm block vào $ZRC"
fi

# 4b) --multi: alias oc-all vào block 9router-config (kể cả khi block đã có từ trước)
if [ "$MULTI" = 1 ] && ! grep -q "alias oc-all=" "$ZRC" 2>/dev/null; then
  ZRC="$ZRC" python3 - <<'PY'
import os
p = os.environ["ZRC"]; s = open(p).read(); end = "# <<< 9router-config <<<"
line = "alias oc-all='opencode -m 9router-b/all'   # bo account 2 @ :20129 — can `9router-multi start`\n"
if end in s:
    open(p, "w").write(s.replace(end, line + end, 1)); print("[9router] thêm alias oc-all")
else:
    print("[9router] chưa có block 9router-config — thêm tay alias oc-all")
PY
fi

# 5) combo qua API dashboard (tuỳ chọn, cần mật khẩu). Hàm dùng chung cho instance 1 và 2.
JAR=""; cleanup() { if [ -n "$JAR" ]; then rm -f "$JAR"; fi; }; trap cleanup EXIT
api_login() {  # api_login <base-url> → nạp cookie vào $JAR
  python3 -c 'import json,os;print(json.dumps({"password":os.environ["NINEROUTER_DASH_PASSWORD"]}))' \
    | curl -fsS -o /dev/null -c "$JAR" -X POST "$1/api/auth/login" -H 'Content-Type: application/json' -d @-
}
have() {  # have <base-url> <name>
  curl -fsS -b "$JAR" "$1/api/combos" | python3 -c "import sys,json;print(any(c['name']=='$2' for c in json.load(sys.stdin)['combos']))"
}
mk() {  # mk <base-url> <name> <json-models>
  if [ "$(have "$1" "$2")" = "True" ]; then say "combo '$2' đã có — bỏ qua"; return; fi
  curl -fsS -b "$JAR" -X POST "$1/api/combos" -H 'Content-Type: application/json' \
    -d "{\"name\":\"$2\",\"models\":$3}" >/dev/null && say "tạo combo '$2' @ $1"
}
if [ -n "${NINEROUTER_DASH_PASSWORD:-}" ]; then
  JAR="$(mktemp)"
  api_login "$URL"
  # smart trước, fast lồng smart ở cuối (9router hỗ trợ combo lồng + fallthrough)
  mk "$URL" smart '["ag/claude-sonnet-4-6","ag/gemini-3.1-pro-low","ag/gemini-3.8-flash-high"]'
  mk "$URL" fast  '["ag/gemini-3.8-flash-high","ag/gemini-3.7-flash-high","ag/gemini-3.5-flash-high","smart"]'
  if [ "$MULTI" = 1 ]; then
    if curl -fsS -m 3 -o /dev/null "$URL2/api/health"; then
      api_login "$URL2"
      # 'all' = mọi model ag/* dùng được, xen kẽ các họ để hết quota một họ thì nhảy sang họ khác.
      # Danh sách kiểm chứng 2026-09-24 — chỉnh theo `curl $URL2/v1/models` (catalog của Antigravity đổi theo thời gian).
      mk "$URL2" all '["ag/claude-sonnet-4-6","ag/gemini-pro-agent","ag/gemini-3.8-flash-high","ag/gpt-oss-120b-medium","ag/gemini-3.8-flash-medium","ag/gemini-3.6-flash-high","ag/gemini-3-flash-agent","ag/gemini-3.8-flash","ag/gemini-3.6-flash-medium","ag/gemini-3-flash","ag/gemini-3.8-flash-low","ag/gemini-3.6-flash-low"]'
    else
      say "instance 2 ($URL2) chưa chạy — chạy '9router-multi start' rồi chạy lại script để tạo combo 'all'"
    fi
  fi
else
  say "bỏ qua tạo combo (không có NINEROUTER_DASH_PASSWORD) — tạo tay theo README.md"
fi

say "xong. Chạy: source ~/.zshrc  rồi  oc-fast | oc-smart | claude-ag | gemini-9r"
if [ "$MULTI" = 1 ]; then say "multi: 9router-multi start && 9router-multi autostart on  rồi  oc-all"; fi
