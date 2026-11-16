#!/usr/bin/env python3
"""
Generate Vietnamese search aliases for English units and merge them into config/aliases_vi.json.

Run after adding or syncing English units, then re-run `import_knowledge.py --sync-only` so the overlay is indexed:

    python3 src/gen_aliases.py --dry-run          # list units that still lack aliases
    python3 src/gen_aliases.py                    # generate for all of them via the `gemini` CLI
    python3 src/gen_aliases.py --prefix software/ --limit 40
    python3 src/gen_aliases.py --ids a/b/c d/e/f  # explicit ids (also overwrites existing entries)

Units whose canonical question is already Vietnamese are skipped (they are searchable as-is).
The overlay is rewritten after every batch, so an interrupted run resumes where it stopped.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

REPO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CATALOG_PATH = os.path.join(REPO_DIR, "catalog.json")
OVERLAY_PATH = os.path.join(REPO_DIR, "config", "aliases_vi.json")

VI_CHARS = re.compile(
    "[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]", re.I
)
MIN_ALIASES, MAX_ALIASES = 3, 6
BODY_CHARS = 1500

PROMPT = """Bạn tạo cụm tìm kiếm tiếng Việt cho kho tri thức kỹ thuật. Đầu vào (stdin) là JSON: danh sách đơn vị tri thức tiếng Anh, mỗi đơn vị có id, question, aliases (tiếng Anh), preview.

Với MỖI đơn vị, viết 4 cụm tìm kiếm tiếng Việt có dấu mà người dùng Việt thực sự gõ:
1. Tên chủ đề ngắn (cụm danh từ).
2. Câu hỏi tự nhiên.
3. Cách hỏi theo tình huống hoặc so sánh.
4. Biến thể dùng thuật ngữ đời thường hoặc từ viết tắt.
Quy tắc: giữ nguyên thuật ngữ, tên riêng, viết tắt tiếng Anh (UML, ATAM, CRC, Kubernetes...); không dịch máy từng chữ; không bịa nội dung ngoài đơn vị; mỗi cụm dưới 12 từ.

Chỉ trả về MỘT đối tượng JSON, không markdown, không giải thích: {"<id>": ["cụm 1", "cụm 2", "cụm 3", "cụm 4"], ...} với đúng các id đã cho."""


def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4:]
    return text


def unit_payload(unit: dict) -> dict:
    body = ""
    try:
        with open(os.path.join(REPO_DIR, unit["id"] + ".md"), "r", encoding="utf-8") as f:
            body = strip_frontmatter(f.read()).strip()[:BODY_CHARS]
    except OSError:
        body = unit.get("content_preview", "") or ""
    return {
        "id": unit["id"],
        "question": unit.get("canonical_question", ""),
        "aliases": list(unit.get("aliases", []) or [])[:8],
        "preview": body,
    }


def select_units(units, overlay, ids, prefix, limit):
    if ids:
        wanted = set(ids)
        chosen = [u for u in units if u["id"] in wanted]
        missing = wanted - {u["id"] for u in chosen}
        if missing:
            print(f"WARN: ids not in catalog: {sorted(missing)}", file=sys.stderr)
    else:
        chosen = [
            u for u in units
            if u["id"] not in overlay and not VI_CHARS.search(u.get("canonical_question", ""))
        ]
    if prefix:
        chosen = [u for u in chosen if u["id"].startswith(prefix)]
    return chosen[:limit] if limit else chosen


def parse_response(text: str) -> dict:
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        raise ValueError("no JSON object in model output")
    return json.loads(text[start:end + 1])


def clean_aliases(raw) -> list:
    if not isinstance(raw, list):
        return []
    out, seen = [], set()
    for a in raw:
        text = re.sub(r"\s+", " ", str(a)).strip()
        if text and text.lower() not in seen:
            seen.add(text.lower())
            out.append(text)
    return out[:MAX_ALIASES]


def router_env() -> dict:
    """Env for Gemini CLI via the local 9router (plain OAuth `gemini` is no longer eligible).

    Key comes from $NINEROUTER_KEY or ~/.9router.env; nothing is stored in the repo.
    Returns {} when no key is found, so the CLI falls back to its own auth.
    """
    key = os.environ.get("NINEROUTER_KEY", "")
    if not key:
        try:
            with open(os.path.expanduser("~/.9router.env"), "r", encoding="utf-8") as f:
                for line in f:
                    m = re.match(r"\s*(?:export\s+)?NINEROUTER_KEY=(.*)", line)
                    if m:
                        key = m.group(1).strip().strip("\"'")
        except OSError:
            pass
    if not key:
        return {}
    return {
        "GEMINI_CLI_HOME": os.path.expanduser("~/.gemini-9r"),
        "GEMINI_API_KEY_AUTH_MECHANISM": "bearer",
        "GOOGLE_GEMINI_BASE_URL": os.environ.get("NINEROUTER_URL", "http://localhost:20128"),
        "GEMINI_API_KEY": key,
    }


def run_gemini(payload: list, model: str, timeout: int) -> dict:
    cmd = ["gemini", "--skip-trust", "-p", PROMPT, "-m", model]
    proc = subprocess.run(
        cmd, input=json.dumps(payload, ensure_ascii=False), capture_output=True,
        text=True, timeout=timeout, cwd=tempfile.gettempdir(), env={**os.environ, **router_env()},
    )
    if proc.returncode != 0:
        raise RuntimeError(f"gemini exit {proc.returncode}: {proc.stderr.strip()[:300]}")
    return parse_response(proc.stdout)


def save_overlay(overlay: dict) -> None:
    os.makedirs(os.path.dirname(OVERLAY_PATH), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(OVERLAY_PATH), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(dict(sorted(overlay.items())), f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, OVERLAY_PATH)


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate Vietnamese aliases into config/aliases_vi.json")
    ap.add_argument("--ids", nargs="+", help="explicit unit ids (overwrite existing entries)")
    ap.add_argument("--prefix", help="only units whose id starts with this")
    ap.add_argument("--limit", type=int, help="max units this run")
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--model", default="ag/gemini-3.8-flash-high", help="model id (9router)")
    ap.add_argument("--timeout", type=int, default=300, help="seconds per gemini call")
    ap.add_argument("--dry-run", action="store_true", help="list pending units, call nothing")
    args = ap.parse_args()

    catalog = load_json(CATALOG_PATH, {})
    units = catalog.get("units", [])
    overlay = load_json(OVERLAY_PATH, {})
    pending = select_units(units, overlay, args.ids, args.prefix, args.limit)
    print(f"{len(pending)} unit(s) pending ({len(overlay)} already in overlay)")
    if args.dry_run or not pending:
        for u in pending:
            print("  ", u["id"])
        return 0

    batches = [pending[i:i + args.batch_size] for i in range(0, len(pending), args.batch_size)]
    lock, done, failed = threading.Lock(), 0, []

    def work(batch):
        ids = [u["id"] for u in batch]
        result = run_gemini([unit_payload(u) for u in batch], args.model, args.timeout)
        good = {}
        for uid in ids:
            aliases = clean_aliases(result.get(uid))
            if len(aliases) >= MIN_ALIASES:
                good[uid] = aliases
        return ids, good

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(work, b): b for b in batches}
        for fut in as_completed(futures):
            try:
                ids, good = fut.result()
            except Exception as exc:  # one bad batch must not lose the others
                failed += [u["id"] for u in futures[fut]]
                print(f"batch failed: {exc}", file=sys.stderr)
                continue
            with lock:
                overlay.update(good)
                save_overlay(overlay)
                done += len(good)
            failed += [uid for uid in ids if uid not in good]
            print(f"saved {len(good)}/{len(ids)}  (total {done}/{len(pending)})")

    if failed:
        print(f"{len(failed)} unit(s) got no usable aliases; re-run to retry:", file=sys.stderr)
        for uid in failed:
            print("  ", uid, file=sys.stderr)
    print("Next: python3 src/import_knowledge.py --sync-only  (catalog + re-index overlay)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
