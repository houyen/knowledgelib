#!/usr/bin/env bash
# demo.sh — chứng minh PoC chạy thật: 1 LÕI deny đúng/sai, rồi sinh wiring mọi vendor.
set -uo pipefail
cd "$(dirname "$0")"
CLI="bin/llmwiki-validate.py"
pass=0; fail=0
ok()   { printf '  \033[1;32mPASS\033[0m %s\n' "$1"; pass=$((pass+1)); }
bad()  { printf '  \033[1;31mFAIL\033[0m %s\n' "$1"; fail=$((fail+1)); }
# expect <mô tả> <exit-mong-đợi> -- <lệnh...>
expect() { local d="$1" want="$2"; shift 3; "$@" >/dev/null 2>&1; local got=$?; [ "$got" = "$want" ] && ok "$d (exit $got)" || bad "$d (muốn $want, được $got)"; }

echo "── 1. LÕI: mode path ──"
expect "ghi src/app.ts"                       0 -- python3 "$CLI" path src/app.ts
expect "ghi self-docs/x.md (path mode không soi nội dung)" 0 -- python3 "$CLI" path self-docs/x.md

echo "── 2. LÕI: mode claude-hook (PreToolUse JSON stdin) · R20 ──"
echo '{"tool_name":"Write","tool_input":{"file_path":"self-docs/y.md","content":"# y no frontmatter"}}' | python3 "$CLI" claude-hook >/dev/null 2>&1
[ $? = 2 ] && ok "self-doc THIẾU frontmatter bị chặn" || bad "self-doc thiếu frontmatter KHÔNG bị chặn"
echo '{"tool_name":"Write","tool_input":{"file_path":"self-docs/x.md","content":"---\nid: x\ncanonical_question: q\naliases: [a]\nentity_type: runbook\ndomain: d\nlast_verified: 2026-09-17\n---\n# x\n\nbody"}}' | python3 "$CLI" claude-hook >/dev/null 2>&1
[ $? = 0 ] && ok "self-doc đủ canonical được phép" || bad "self-doc đủ canonical bị chặn nhầm"
echo '{"tool_name":"Write","tool_input":{"file_path":"src/app.ts","content":"x"}}' | python3 "$CLI" claude-hook >/dev/null 2>&1
[ $? = 0 ] && ok "file ngoài self-docs được phép" || bad "file ngoài self-docs bị chặn nhầm"

echo "── 3. LÕI: mode files (layer=repo) ──"
tmp="$(mktemp -d)"; mkdir -p "$tmp/self-docs"
printf '%b' '---\nid: g\ncanonical_question: q\naliases: [a]\nentity_type: runbook\ndomain: d\nlast_verified: 2026-09-17\n---\n# g\n\nbody\n' > "$tmp/self-docs/good.md"
echo "# bad" > "$tmp/self-docs/bad.md"
expect "repo: self-doc tốt qua"             0 -- bash -c "cd '$tmp' && python3 '$PWD/$CLI' --policy '$PWD/policy.yaml' files self-docs/good.md"
expect "repo: self-doc thiếu frontmatter fail" 1 -- bash -c "cd '$tmp' && python3 '$PWD/$CLI' --policy '$PWD/policy.yaml' files self-docs/bad.md"
rm -rf "$tmp"

echo "── 4. fail-open: policy lỗi → KHÔNG chặn ──"
expect "policy thiếu → exit 0 (fail-open)" 0 -- python3 "$CLI" --policy /no/such/policy.yaml path self-docs/x.md

echo "── 5. Sinh wiring mọi vendor từ 1 policy.yaml ──"
python3 gen-converters.py

echo
echo "── Cây out/ ──"
find out -type f | sort | sed 's,^,  ,'
echo
printf '\033[1mKẾT QUẢ: %d PASS · %d FAIL\033[0m\n' "$pass" "$fail"
[ "$fail" = 0 ] || exit 1
