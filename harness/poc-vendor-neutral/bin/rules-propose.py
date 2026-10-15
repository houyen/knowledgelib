#!/usr/bin/env python3
"""rules-propose — hàng đợi đề xuất rule từ repo, merge có duyệt vào knowledgelib.

Lệnh:
  rules-propose.py add   --lang go --id GO-ERR-05 --severity warn --kind review \\
                         --statement "..." --evidence "..." --origin "..." [--check "..."] [--scope prod,tests] [--root .] [--kl PATH]
  rules-propose.py list  [--lang go] [--root .]
  rules-propose.py merge --lang go --id GO-ERR-05 --approve-by "<tên>" [--patch] [--root .] [--kl PATH]

Exit: 0 ok · 2 lỗi đầu vào/xác thực/parse
"""
import argparse
import datetime
import json
import os
import re
import shutil
import sys
import yaml

# Tái sử dụng các hàm nếu có thể
OUT_NAME = {"js-ts": "js", "go": "go"}
ID_PREFIX = {"js-ts": "JS", "go": "GO"}
VALID_SEVERITIES = {"error", "warn"}
VALID_KINDS = {"machine", "review", "refactor"}


class Fail(Exception):
    pass


def kl_home(arg):
    return os.path.expanduser(arg or os.environ.get("KNOWLEDGELIB_HOME") or "~/Documents/Repo/knowledgelib_data")


def validate_clean_content(text, field_name):
    # nội dung chứa email (regex \S+@\S+\.\S+), /Users/, hoặc chuỗi giống token (ghp_, sk-, AKIA)
    if re.search(r"\S+@\S+\.\S+", text):
        raise Fail(f"{field_name} chứa địa chỉ email: không hợp lệ (bảo mật/PII)")
    if "/Users/" in text:
        raise Fail(f"{field_name} chứa đường dẫn tuyệt đối /Users/: không hợp lệ")
    if re.search(r"(ghp_[a-zA-Z0-9]+|sk-[a-zA-Z0-9]+|AKIA[A-Z0-9]{16})", text):
        raise Fail(f"{field_name} chứa chuỗi giống token/secret: không hợp lệ")


def check_id_in_ku(kl, lang, rule_id):
    rel = f"software/coding-rules/{lang}-code-rules.md"
    path = os.path.join(kl, rel)
    if not os.path.isfile(path):
        return
    text = open(path, encoding="utf-8").read()
    # Tìm khối yaml rules:
    block = None
    for m in re.finditer(r"```yaml\n(.*?)```", text, re.S):
        if re.search(r"^rules:\s*$", m.group(1), re.M):
            block = m.group(1)
            break
    if block:
        try:
            data = yaml.safe_load(block) or {}
            for r in data.get("rules") or []:
                if r.get("id") == rule_id:
                    raise Fail(f"id '{rule_id}' đã tồn tại trong KU ({rel})")
        except yaml.YAMLError:
            pass


def cmd_add(a):
    root = os.path.abspath(a.root)
    kl = kl_home(a.kl)
    lang = a.lang
    if lang not in ID_PREFIX:
        raise Fail(f"lang lạ: {lang} (hỗ trợ: {', '.join(sorted(ID_PREFIX))})")

    rule_id = a.id
    expected_prefix = ID_PREFIX[lang]
    if not re.match(r"^(JS|GO)-[A-Z]+-\d{2}$", rule_id):
        raise Fail(f"id '{rule_id}' không khớp định dạng ^(JS|GO)-[A-Z]+-\\d{{2}}$")
    if not rule_id.startswith(f"{expected_prefix}-"):
        raise Fail(f"id '{rule_id}' có tiền tố không khớp với lang '{lang}' (cần '{expected_prefix}-')")

    evidence = str(a.evidence or "").strip()
    if not evidence:
        raise Fail("--evidence rỗng ('không bằng chứng, không đề xuất')")

    severity = a.severity
    if severity not in VALID_SEVERITIES:
        raise Fail(f"severity '{severity}' không hợp lệ (phải là {', '.join(sorted(VALID_SEVERITIES))})")

    kind = a.kind
    if kind not in VALID_KINDS:
        raise Fail(f"kind '{kind}' không hợp lệ (phải là {', '.join(sorted(VALID_KINDS))})")

    statement = str(a.statement or "").strip()
    if not statement:
        raise Fail("--statement không được để trống")

    origin = str(a.origin or "").strip()
    if not origin:
        raise Fail("--origin không được để trống")

    check = str(a.check or "").strip() if a.check else None

    # Kiểm tra PII / secrets
    for val, name in [
        (rule_id, "id"),
        (statement, "statement"),
        (evidence, "evidence"),
        (origin, "origin"),
        (check or "", "check"),
    ]:
        validate_clean_content(val, name)

    # Kiểm tra id đã có trong đề xuất pending hay chưa
    proposal_dir = os.path.join(root, "rules-proposals", lang)
    proposal_file = os.path.join(proposal_dir, f"{rule_id}.yaml")
    if os.path.isfile(proposal_file):
        raise Fail(f"đề xuất cho id '{rule_id}' đã tồn tại: {proposal_file}")

    # Kiểm tra id trong KU
    check_id_in_ku(kl, lang, rule_id)

    scope_list = [s.strip() for s in (a.scope or "prod").split(",") if s.strip()]

    today = datetime.date.today().isoformat()

    # Tạo nội dung YAML với json.dumps(...) để luôn bọc nháy kép cho chuỗi
    os.makedirs(proposal_dir, exist_ok=True)
    lines = [
        f"id: {json.dumps(rule_id, ensure_ascii=False)}",
        f"severity: {json.dumps(severity, ensure_ascii=False)}",
        f"kind: {json.dumps(kind, ensure_ascii=False)}",
    ]
    if check:
        lines.append(f"check: {json.dumps(check, ensure_ascii=False)}")
    lines.append(f"statement: {json.dumps(statement, ensure_ascii=False)}")
    lines.append(f"scope: [{', '.join(scope_list)}]")
    lines.append(f"origin: {json.dumps(origin, ensure_ascii=False)}")
    lines.append(f"evidence: {json.dumps(evidence, ensure_ascii=False)}")
    lines.append(f"proposed_at: {json.dumps(today, ensure_ascii=False)}")

    with open(proposal_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Đã tạo đề xuất: {proposal_file}")
    return 0


def cmd_list(a):
    root = os.path.abspath(a.root)
    base_dir = os.path.join(root, "rules-proposals")
    if not os.path.isdir(base_dir):
        # In header trống
        print(f"{'ID':<15} {'LANG':<8} {'SEVERITY':<10} {'PROPOSED':<12} {'STATUS'}")
        return 0

    langs = [a.lang] if a.lang else [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    langs.sort()

    rows = []
    for lang in langs:
        ldir = os.path.join(base_dir, lang)
        if not os.path.isdir(ldir):
            continue
        # pending
        for fname in os.listdir(ldir):
            if fname.endswith(".yaml") and os.path.isfile(os.path.join(ldir, fname)):
                try:
                    data = yaml.safe_load(open(os.path.join(ldir, fname), encoding="utf-8")) or {}
                    rows.append({
                        "id": data.get("id", fname[:-5]),
                        "lang": lang,
                        "severity": data.get("severity", "-"),
                        "proposed_at": data.get("proposed_at", "-"),
                        "status": "pending"
                    })
                except Exception:
                    pass
        # merged
        mdir = os.path.join(ldir, "merged")
        if os.path.isdir(mdir):
            for fname in os.listdir(mdir):
                if fname.endswith(".yaml") and os.path.isfile(os.path.join(mdir, fname)):
                    try:
                        data = yaml.safe_load(open(os.path.join(mdir, fname), encoding="utf-8")) or {}
                        rows.append({
                            "id": data.get("id", fname[:-5]),
                            "lang": lang,
                            "severity": data.get("severity", "-"),
                            "proposed_at": data.get("proposed_at", "-"),
                            "status": "merged"
                        })
                    except Exception:
                        pass

    rows.sort(key=lambda x: (x["lang"], x["id"], x["status"]))
    print(f"{'ID':<15} {'LANG':<8} {'SEVERITY':<10} {'PROPOSED':<12} {'STATUS'}")
    for r in rows:
        print(f"{r['id']:<15} {r['lang']:<8} {r['severity']:<10} {str(r['proposed_at']):<12} {r['status']}")
    return 0


def bump_version(v_str, is_patch=False):
    # v_str kiểu "0.1.0"
    m = re.match(r"^(\d+)\.(\d+)\.(\d+)$", v_str.strip())
    if not m:
        raise Fail(f"Phiên bản không đúng định dạng x.y.z: {v_str}")
    major, minor, patch = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if is_patch:
        patch += 1
    else:
        minor += 1
        patch = 0
    return f"{major}.{minor}.{patch}"


def cmd_merge(a):
    root = os.path.abspath(a.root)
    kl = kl_home(a.kl)
    lang = a.lang
    rule_id = a.id
    approve_by = str(a.approve_by or "").strip()
    if not approve_by:
        raise Fail("--approve-by không được để trống")

    proposal_path = os.path.join(root, "rules-proposals", lang, f"{rule_id}.yaml")
    if not os.path.isfile(proposal_path):
        raise Fail(f"Không tìm thấy đề xuất pending: {proposal_path}")

    try:
        prop = yaml.safe_load(open(proposal_path, encoding="utf-8")) or {}
    except Exception as e:
        raise Fail(f"Lỗi đọc file đề xuất YAML: {e}")

    # Kiểm tra lại các ràng buộc của prop
    for k in ("id", "severity", "kind", "statement", "evidence", "origin"):
        if not prop.get(k):
            raise Fail(f"Đề xuất thiếu trường '{k}'")
    for k in ("id", "statement", "evidence", "origin", "check"):
        if prop.get(k):
            validate_clean_content(str(prop[k]), k)

    # Đọc KU
    rel = f"software/coding-rules/{lang}-code-rules.md"
    ku_path = os.path.join(kl, rel)
    if not os.path.isfile(ku_path):
        raise Fail(f"Không tìm thấy KU: {ku_path}")

    # Đọc KU text
    ku_text = open(ku_path, encoding="utf-8").read()

    # Kiểm tra id chưa có trong KU
    check_id_in_ku(kl, lang, rule_id)

    # Tìm dòng version: **rule_set_version:** `x.y.z`
    mv = re.search(r"\*\*rule_set_version:\*\*\s*`([^`]+)`", ku_text)
    if not mv:
        raise Fail(f"{rel}: thiếu dòng **rule_set_version:** `x.y.z`")
    old_version = mv.group(1)
    new_version = bump_version(old_version, is_patch=a.patch)

    today = datetime.date.today().isoformat()

    # Sao lưu KU trước khi chỉnh sửa
    ku_backup = ku_text

    # 1. Thay version và last_verified
    # last_verified: 'YYYY-MM-DD' hoặc last_verified: YYYY-MM-DD
    new_ku_text = re.sub(
        r"(\*\*rule_set_version:\*\*\s*`)[^`]+(`)",
        rf"\g<1>{new_version}\g<2>",
        ku_text,
        count=1
    )
    new_ku_text = re.sub(
        r"(last_verified:\s*['\"]?)[^'\"\n]+(['\"]?)",
        rf"\g<1>{today}\g<2>",
        new_ku_text,
        count=1
    )

    # 2. Định dạng rule block cần chèn (4 spaces indent như thông lệ)
    rule_lines = [
        f"  - id: {json.dumps(prop['id'], ensure_ascii=False)}",
        f"    severity: {json.dumps(prop['severity'], ensure_ascii=False)}",
        f"    kind: {json.dumps(prop['kind'], ensure_ascii=False)}",
    ]
    if prop.get("check"):
        rule_lines.append(f"    check: {json.dumps(prop['check'], ensure_ascii=False)}")
    rule_lines.append(f"    statement: {json.dumps(prop['statement'], ensure_ascii=False)}")
    scope = prop.get("scope") or ["prod"]
    if isinstance(scope, list):
        scope_str = ", ".join(scope)
    else:
        scope_str = str(scope)
    rule_lines.append(f"    scope: [{scope_str}]")
    rule_lines.append(f"    origin: {json.dumps(prop['origin'], ensure_ascii=False)}")
    rule_lines.append(f"    evidence: {json.dumps(prop['evidence'], ensure_ascii=False)}")
    rule_entry_text = "\n".join(rule_lines) + "\n"

    # Tìm vị trí kết thúc của khối rules trong ```yaml rules: ... ```
    # Khối yaml bắt đầu bằng ```yaml có dòng rules:
    yaml_block_match = None
    for m in re.finditer(r"```yaml\n(.*?)```", new_ku_text, re.S):
        if re.search(r"^rules:\s*$", m.group(1), re.M):
            yaml_block_match = m
            break
    if not yaml_block_match:
        raise Fail(f"{rel}: thiếu khối ```yaml rules:```")

    # Điểm kết thúc khối nằm ngay trước dấu đóng ```
    end_pos = yaml_block_match.end(1)
    # Chèn rule_entry_text vào end_pos
    new_ku_text = new_ku_text[:end_pos] + rule_entry_text + new_ku_text[end_pos:]

    # Ghi KU tạm thời để kiểm parse
    with open(ku_path, "w", encoding="utf-8") as f:
        f.write(new_ku_text)

    # Kiểm tra parse KU bằng loader
    parse_ok = False
    try:
        # Import hoặc gọi hàm load_ku
        # Đọc lại file xem YAML có hợp lệ và rule_hashes load được không
        parsed_block = None
        for m in re.finditer(r"```yaml\n(.*?)```", new_ku_text, re.S):
            if re.search(r"^rules:\s*$", m.group(1), re.M):
                parsed_block = m.group(1)
                break
        if parsed_block:
            rules_data = (yaml.safe_load(parsed_block) or {}).get("rules") or []
            # Kiểm tra rule mới có nằm trong rules_data không
            found_new = any(r.get("id") == rule_id for r in rules_data)
            if found_new:
                parse_ok = True
    except Exception:
        parse_ok = False

    if not parse_ok:
        # Khôi phục nguyên trạng KU byte-for-byte
        with open(ku_path, "w", encoding="utf-8") as f:
            f.write(ku_backup)
        raise Fail(f"Merge thất bại: Parse KU sau khi chèn bị lỗi. Đã khôi phục nguyên trạng {ku_path}.")

    # Chuyển đề xuất sang merged/
    merged_dir = os.path.join(root, "rules-proposals", lang, "merged")
    os.makedirs(merged_dir, exist_ok=True)
    merged_path = os.path.join(merged_dir, f"{rule_id}.yaml")

    # Đọc lại text của proposal, nối thêm merged_by và merged_at
    prop_raw = open(proposal_path, encoding="utf-8").read().rstrip("\n")
    prop_raw += f"\nmerged_by: {json.dumps(approve_by, ensure_ascii=False)}\n"
    prop_raw += f"merged_at: {json.dumps(today, ensure_ascii=False)}\n"
    with open(merged_path, "w", encoding="utf-8") as f:
        f.write(prop_raw)
    os.remove(proposal_path)

    print(f"Đã merge rule {rule_id} vào {rel} (version {old_version} -> {new_version}).")
    print(f"Đã chuyển đề xuất sang: {merged_path}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    # add
    p_add = sub.add_parser("add")
    p_add.add_argument("--lang", required=True)
    p_add.add_argument("--id", required=True)
    p_add.add_argument("--severity", required=True)
    p_add.add_argument("--kind", required=True)
    p_add.add_argument("--statement", required=True)
    p_add.add_argument("--evidence", required=True)
    p_add.add_argument("--origin", required=True)
    p_add.add_argument("--check")
    p_add.add_argument("--scope", default="prod")
    p_add.add_argument("--root", default=".")
    p_add.add_argument("--kl")

    # list
    p_list = sub.add_parser("list")
    p_list.add_argument("--lang")
    p_list.add_argument("--root", default=".")

    # merge
    p_merge = sub.add_parser("merge")
    p_merge.add_argument("--lang", required=True)
    p_merge.add_argument("--id", required=True)
    p_merge.add_argument("--approve-by", required=True)
    p_merge.add_argument("--patch", action="store_true")
    p_merge.add_argument("--root", default=".")
    p_merge.add_argument("--kl")

    a = ap.parse_args()
    if a.cmd == "add":
        return cmd_add(a)
    elif a.cmd == "list":
        return cmd_list(a)
    elif a.cmd == "merge":
        return cmd_merge(a)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Fail as e:
        print(f"rules-propose: {e}", file=sys.stderr)
        sys.exit(2)
