#!/usr/bin/env bash
# test-rules.sh — test cho bin/rules-pull.py (fixture tạm, không đụng knowledgelib thật trừ smoke cuối).
set -uo pipefail
cd "$(dirname "$0")"
RP="python3 bin/rules-pull.py"
T=0; P=0; F=0
assert(){ local want="$1" desc="$2" got="$3"; T=$((T+1))
  if [ "$got" = "$want" ]; then P=$((P+1)); printf '  \033[1;32mok\033[0m  %s\n' "$desc"
  else F=$((F+1)); printf '  \033[1;31mNO\033[0m  %s \033[2m(want %s got %s)\033[0m\n' "$desc" "$want" "$got"; fi; }
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
KL="$TMP/kl"; R="$TMP/repo"; mkdir -p "$KL/software/coding-rules" "$R"
mkku(){ # $1=version $2=extra rule yaml
cat > "$KL/software/coding-rules/go-code-rules.md" <<KU
---
id: software/coding-rules/go-code-rules
---
**rule_set:** \`go\` · **rule_set_version:** \`$1\`

\`\`\`yaml
rules:
  - id: GO-ERR-01
    severity: error
    kind: machine
    check: "golangci:errorlint"
    statement: "Wrap error: dùng %w."
    scope: [prod]
    evidence: "vd: có dấu hai chấm trong chuỗi"
  - id: GO-SIZE-01
    severity: warn
    kind: review
    statement: "Hàm ngắn."
$2
\`\`\`
KU
}

echo "── A. pull cơ bản ──"
mkku 0.1.0 ""
$RP --lang go --root "$R" --kl "$KL" >/dev/null 2>&1;             assert 0 "pull lần đầu" $?
[ -f "$R/docs/rules/go.md" ] && g=1 || g=0;                        assert 1 "sinh docs/rules/go.md" $g
[ -f "$R/rules.lock" ] && g=1 || g=0;                              assert 1 "sinh rules.lock" $g
grep -q "GO-ERR-01" "$R/docs/rules/go.md" && g=1 || g=0;           assert 1 "doc chứa rule id" $g
grep -q "dấu hai chấm" "$R/docs/rules/go.md" && g=1 || g=0;        assert 1 "chuỗi có ': ' không vỡ YAML (quote)" $g
$RP --lang go --root "$R" --kl "$KL" --check >/dev/null 2>&1;      assert 0 "--check khớp sau pull (idempotent)" $?

echo "── B. KU đổi → diff thấy được ──"
mkku 0.2.0 "  - id: GO-CTX-01
    severity: error
    kind: review
    statement: \"Ctx đầu tiên.\""
$RP --lang go --root "$R" --kl "$KL" --check >/dev/null 2>&1;      assert 1 "--check lệch khi KU đổi" $?
out=$($RP --lang go --root "$R" --kl "$KL" --diff 2>&1)
echo "$out" | grep -q "version 0.1.0 → 0.2.0" && g=1 || g=0;       assert 1 "--diff báo đổi version" $g
echo "$out" | grep -q "+ GO-CTX-01" && g=1 || g=0;                assert 1 "--diff báo rule thêm" $g
grep -q "GO-CTX-01" "$R/docs/rules/go.md" && g=1 || g=0;           assert 0 "--diff không ghi file" $g
$RP --lang go --root "$R" --kl "$KL" >/dev/null 2>&1;              assert 0 "pull bản mới" $?
grep -q "GO-CTX-01" "$R/docs/rules/go.md" && g=1 || g=0;           assert 1 "doc có rule mới sau pull" $g

echo "── C. override cục bộ ──"
cat > "$R/rules.local.yaml" <<'YML'
overrides:
  - id: GO-SIZE-01
    action: disable
    reason: "repo cũ, chờ ratchet"
YML
$RP --lang go --root "$R" --kl "$KL" >/dev/null 2>&1;              assert 0 "pull với override" $?
grep -q "GO-SIZE-01\*\* \[" "$R/docs/rules/go.md" && g=1 || g=0;   assert 0 "rule bị tắt không nằm trong danh sách" $g
grep -q "repo cũ, chờ ratchet" "$R/docs/rules/go.md" && g=1 || g=0; assert 1 "lý do override hiện trong doc" $g
cp "$R/rules.local.yaml" "$TMP/keep.yaml"
$RP --lang go --root "$R" --kl "$KL" >/dev/null 2>&1
cmp -s "$R/rules.local.yaml" "$TMP/keep.yaml" && g=1 || g=0;       assert 1 "pull không ghi đè rules.local.yaml" $g
cat > "$R/rules.local.yaml" <<'YML'
overrides:
  - id: GO-SIZE-01
    action: disable
YML
$RP --lang go --root "$R" --kl "$KL" >/dev/null 2>&1;              assert 2 "override thiếu reason bị từ chối" $?
rm "$R/rules.local.yaml"

echo "── D. lỗi đầu vào (exit 2) ──"
$RP --lang rust --root "$R" --kl "$KL" >/dev/null 2>&1;            assert 2 "lang lạ" $?
$RP --lang js-ts --root "$R" --kl "$KL" >/dev/null 2>&1;           assert 2 "thiếu KU" $?
printf 'x' > "$KL/software/coding-rules/js-ts-code-rules.md"
$RP --lang js-ts --root "$R" --kl "$KL" >/dev/null 2>&1;           assert 2 "KU thiếu version/khối rules" $?

echo "── E. --wire-claude ──"
printf '# demo\n' > "$R/CLAUDE.md"
$RP --lang go --root "$R" --kl "$KL" --wire-claude >/dev/null 2>&1
$RP --lang go --root "$R" --kl "$KL" --wire-claude >/dev/null 2>&1
n=$(grep -c "@docs/rules/go.md" "$R/CLAUDE.md");                  assert 1 "thêm @import đúng một lần (idempotent)" $n

echo "── F. smoke trên KU thật (bỏ qua nếu chưa có) ──"
REAL="${KNOWLEDGELIB_HOME:-$HOME/Documents/Repo/knowledgelib_data}"
if [ -f "$REAL/software/coding-rules/go-code-rules.md" ] && [ -f "$REAL/software/coding-rules/js-ts-code-rules.md" ]; then
  R2="$TMP/real"; mkdir -p "$R2"
  $RP --lang js-ts,go --root "$R2" --kl "$REAL" >/dev/null 2>&1;    assert 0 "parse + render KU thật (js-ts, go)" $?
  n=$(grep -c "^- \*\*" "$R2/docs/rules/go.md");                   [ "$n" -ge 10 ] && g=ok || g=few; assert ok "doc Go thật có ≥10 rule" $g
else
  echo "  (bỏ qua: chưa có KU thật)"
fi

echo "── G. rules.local.md ──"
cat > "$R/rules.local.md" <<'LOC'
### Stack đặc thù
- Chỉ dùng TypeScript strict.
LOC
$RP --lang go --root "$R" --kl "$KL" >/dev/null 2>&1;              assert 0 "pull với rules.local.md" $?
grep -q "## Ghi chú riêng của repo (rules.local.md)" "$R/docs/rules/go.md" && g=1 || g=0; assert 1 "doc chứa heading rules.local.md" $g
grep -q "Chỉ dùng TypeScript strict" "$R/docs/rules/go.md" && g=1 || g=0;                  assert 1 "doc chứa nội dung rules.local.md" $g

echo "- Thêm dòng ghi chú mới." >> "$R/rules.local.md"
$RP --lang go --root "$R" --kl "$KL" --check >/dev/null 2>&1;      assert 1 "--check lệch khi rules.local.md đổi" $?
out=$($RP --lang go --root "$R" --kl "$KL" --diff 2>&1)
echo "$out" | grep -q "~ rules.local.md" && g=1 || g=0;            assert 1 "--diff có dòng ~ rules.local.md" $g

$RP --lang go --root "$R" --kl "$KL" >/dev/null 2>&1;              assert 0 "pull lại sau khi rules.local.md đổi" $?
$RP --lang go --root "$R" --kl "$KL" --check >/dev/null 2>&1;      assert 0 "--check khớp sau pull lại" $?

rm -f "$R/rules.local.md"
$RP --lang go --root "$R" --kl "$KL" --check >/dev/null 2>&1;      assert 1 "--check lệch khi xóa rules.local.md" $?
$RP --lang go --root "$R" --kl "$KL" >/dev/null 2>&1;              assert 0 "pull sau khi xóa rules.local.md" $?
grep -q "## Ghi chú riêng của repo (rules.local.md)" "$R/docs/rules/go.md" && g=1 || g=0; assert 0 "doc không còn heading rules.local.md" $g
$RP --lang go --root "$R" --kl "$KL" --check >/dev/null 2>&1;      assert 0 "--check khớp sau pull xóa" $?

python3 -c "import json; d=json.load(open('$R/rules.lock')); [s.pop('local_notes_sha', None) for s in d.get('sets', {}).values()]; json.dump(d, open('$R/rules.lock', 'w'))"
$RP --lang go --root "$R" --kl "$KL" --check >/dev/null 2>&1;      assert 0 "lock cũ không có local_notes_sha + không có file: --check exit 0" $?

cat > "$R/rules.local.md" <<'LOC'
Nội dung cố định
LOC
cp "$R/rules.local.md" "$TMP/keep_notes.md"
$RP --lang go --root "$R" --kl "$KL" >/dev/null 2>&1
cmp -s "$R/rules.local.md" "$TMP/keep_notes.md" && g=1 || g=0;     assert 1 "pull không ghi đè rules.local.md" $g
rm -f "$R/rules.local.md" "$TMP/keep_notes.md"

echo; printf '\033[1mTỔNG: %d test · %d PASS · %d FAIL\033[0m\n' "$T" "$P" "$F"
[ "$F" -eq 0 ]
