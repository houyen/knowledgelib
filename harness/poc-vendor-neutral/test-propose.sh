#!/usr/bin/env bash
# test-propose.sh — test cho bin/rules-propose.py (dùng fixture tạm, không đụng KU thật).
set -uo pipefail
cd "$(dirname "$0")"
RPP="python3 bin/rules-propose.py"
T=0; P=0; F=0
assert(){ local want="$1" desc="$2" got="$3"; T=$((T+1))
  if [ "$got" = "$want" ]; then P=$((P+1)); printf '  \033[1;32mok\033[0m  %s\n' "$desc"
  else F=$((F+1)); printf '  \033[1;31mNO\033[0m  %s \033[2m(want %s got %s)\033[0m\n' "$desc" "$want" "$got"; fi; }

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
KL="$TMP/kl"; R="$TMP/repo"; mkdir -p "$KL/software/coding-rules" "$R"

mkku(){ # $1=version
cat > "$KL/software/coding-rules/go-code-rules.md" <<KU
---
id: software/coding-rules/go-code-rules
last_verified: '2026-09-01'
---
**rule_set:** \`go\` · **rule_set_version:** \`$1\`

\`\`\`yaml
rules:
  - id: "GO-ERR-01"
    severity: "error"
    kind: "machine"
    statement: "Wrap error."
    scope: [prod]
    origin: "test"
    evidence: "test evidence"
\`\`\`
KU
}

mkku 0.1.0

echo "── 1. add thành công ──"
$RPP add --lang go --id GO-ERR-02 --severity warn --kind review \
  --statement "Hàm ngắn" --evidence "Có dẫn chứng" --origin "repo test" \
  --root "$R" --kl "$KL" >/dev/null 2>&1; assert 0 "add thành công" $?
[ -f "$R/rules-proposals/go/GO-ERR-02.yaml" ] && g=1 || g=0; assert 1 "file đề xuất được tạo" $g

echo "── 2. thiếu evidence → 2 ──"
$RPP add --lang go --id GO-ERR-03 --severity warn --kind review \
  --statement "Hàm ngắn" --evidence "" --origin "repo test" \
  --root "$R" --kl "$KL" >/dev/null 2>&1; assert 2 "thiếu evidence bị từ chối" $?

echo "── 3. id sai định dạng → 2 ──"
$RPP add --lang go --id GO-err-03 --severity warn --kind review \
  --statement "Hàm ngắn" --evidence "abc" --origin "repo test" \
  --root "$R" --kl "$KL" >/dev/null 2>&1; assert 2 "id chữ thường bị từ chối" $?
$RPP add --lang go --id GO-ERR-1 --severity warn --kind review \
  --statement "Hàm ngắn" --evidence "abc" --origin "repo test" \
  --root "$R" --kl "$KL" >/dev/null 2>&1; assert 2 "id 1 số bị từ chối" $?

echo "── 4. tiền tố sai lang → 2 ──"
$RPP add --lang go --id JS-ERR-03 --severity warn --kind review \
  --statement "Hàm ngắn" --evidence "abc" --origin "repo test" \
  --root "$R" --kl "$KL" >/dev/null 2>&1; assert 2 "tiền tố JS cho lang go bị từ chối" $?

echo "── 5. id trùng KU → 2 ──"
$RPP add --lang go --id GO-ERR-01 --severity warn --kind review \
  --statement "Hàm ngắn" --evidence "abc" --origin "repo test" \
  --root "$R" --kl "$KL" >/dev/null 2>&1; assert 2 "id trùng KU bị từ chối" $?

echo "── 6. id trùng đề xuất → 2 ──"
$RPP add --lang go --id GO-ERR-02 --severity warn --kind review \
  --statement "Hàm ngắn trùng" --evidence "abc" --origin "repo test" \
  --root "$R" --kl "$KL" >/dev/null 2>&1; assert 2 "id trùng đề xuất đã có bị từ chối" $?

echo "── 7. severity / kind sai → 2 ──"
$RPP add --lang go --id GO-ERR-04 --severity info --kind review \
  --statement "Hàm ngắn" --evidence "abc" --origin "repo test" \
  --root "$R" --kl "$KL" >/dev/null 2>&1; assert 2 "severity info bị từ chối" $?
$RPP add --lang go --id GO-ERR-04 --severity warn --kind manual \
  --statement "Hàm ngắn" --evidence "abc" --origin "repo test" \
  --root "$R" --kl "$KL" >/dev/null 2>&1; assert 2 "kind manual bị từ chối" $?

echo "── 8. chứa email → 2 ──"
$RPP add --lang go --id GO-ERR-04 --severity warn --kind review \
  --statement "Gửi mail user@example.com" --evidence "abc" --origin "repo test" \
  --root "$R" --kl "$KL" >/dev/null 2>&1; assert 2 "statement chứa email bị từ chối" $?

echo "── 9. chứa /Users/ → 2 ──"
$RPP add --lang go --id GO-ERR-04 --severity warn --kind review \
  --statement "Đường dẫn" --evidence "file ở /Users/thaidt/code" --origin "repo test" \
  --root "$R" --kl "$KL" >/dev/null 2>&1; assert 2 "evidence chứa /Users/ bị từ chối" $?

echo "── 10. chuỗi có ': ' vẫn parse được sau khi merge ──"
$RPP add --lang go --id GO-ERR-05 --severity warn --kind review \
  --statement "Lỗi có dấu hai chấm: chi tiết" --evidence "Dẫn chứng: mục 3" --origin "test: repo" \
  --root "$R" --kl "$KL" >/dev/null 2>&1; assert 0 "add rule có dấu ': '" $?

echo "── 11. list hiển thị pending ──"
out=$($RPP list --root "$R" 2>&1)
echo "$out" | grep -q "GO-ERR-02" && echo "$out" | grep -q "pending" && g=1 || g=0
assert 1 "list hiển thị GO-ERR-02 pending" $g

echo "── 12. merge thiếu --approve-by → 2 ──"
$RPP merge --lang go --id GO-ERR-05 --approve-by "" --root "$R" --kl "$KL" >/dev/null 2>&1
assert 2 "merge thiếu approve-by bị từ chối" $?

echo "── 13. merge thành công ──"
$RPP merge --lang go --id GO-ERR-05 --approve-by "Claude" --root "$R" --kl "$KL" >/dev/null 2>&1
assert 0 "merge thành công exit 0" $?
grep -q "GO-ERR-05" "$KL/software/coding-rules/go-code-rules.md" && g=1 || g=0
assert 1 "rule GO-ERR-05 xuất hiện trong KU" $g
grep -q "rule_set_version:\*\* \`0.2.0\`" "$KL/software/coding-rules/go-code-rules.md" && g=1 || g=0
assert 1 "version tăng lên 0.2.0 (minor)" $g
grep -q "last_verified: '$(date +%Y-%m-%d)'" "$KL/software/coding-rules/go-code-rules.md" && g=1 || g=0
assert 1 "last_verified cập nhật ngày hôm nay" $g
[ -f "$R/rules-proposals/go/merged/GO-ERR-05.yaml" ] && g=1 || g=0
assert 1 "đề xuất chuyển sang thư mục merged/" $g
[ ! -f "$R/rules-proposals/go/GO-ERR-05.yaml" ] && g=1 || g=0
assert 1 "đề xuất pending cũ đã được dọn" $g

# Test patch version
$RPP add --lang go --id GO-ERR-06 --severity warn --kind review \
  --statement "Rule patch" --evidence "abc" --origin "test" --root "$R" --kl "$KL" >/dev/null 2>&1
$RPP merge --lang go --id GO-ERR-06 --approve-by "Claude" --patch --root "$R" --kl "$KL" >/dev/null 2>&1
grep -q "rule_set_version:\*\* \`0.2.1\`" "$KL/software/coding-rules/go-code-rules.md" && g=1 || g=0
assert 1 "--patch tăng đúng version patch (0.2.1)" $g

echo "── 14. merge làm parse lỗi → KU giữ nguyên byte (cmp) + exit 2 ──"
# Tạo KU giả bị hỏng cú pháp khi chèn
cat > "$KL/software/coding-rules/go-code-rules.md" <<'BADKU'
---
id: software/coding-rules/go-code-rules
last_verified: '2026-09-01'
---
**rule_set:** `go` · **rule_set_version:** `0.3.0`

```yaml
rules: [không phải list hợp lệ: {
```
BADKU
cp "$KL/software/coding-rules/go-code-rules.md" "$TMP/ku_backup_bad.md"
$RPP add --lang go --id GO-ERR-07 --severity warn --kind review \
  --statement "Rule thử fail" --evidence "abc" --origin "test" --root "$R" --kl "$KL" >/dev/null 2>&1
$RPP merge --lang go --id GO-ERR-07 --approve-by "Claude" --root "$R" --kl "$KL" >/dev/null 2>&1
assert 2 "merge vào KU hỏng bị exit 2" $?
cmp -s "$KL/software/coding-rules/go-code-rules.md" "$TMP/ku_backup_bad.md" && g=1 || g=0
assert 1 "KU khôi phục nguyên trạng byte khi parse lỗi" $g

echo; printf '\033[1mTỔNG: %d test · %d PASS · %d FAIL\033[0m\n' "$T" "$P" "$F"
[ "$F" -eq 0 ]
