#!/usr/bin/env python3
"""
Retrieval regression harness cho KnowledgeLib.

Đo Recall@k / MRR của KnowledgeLibClient.search() trên một golden set
(câu hỏi -> unit id đúng). Chỉ đọc, không ghi catalog / Chroma.

    python3 src/retrieval_eval.py                         # golden mặc định, in bảng
    python3 src/retrieval_eval.py --min-r3 0.65           # exit 1 nếu Recall@3 < 0.65
    python3 src/retrieval_eval.py --golden my.json --json

Golden file: JSON list [{"q": "...", "gold": ["unit/id", ...], "note": "..."}]
(`gold` nhiều id = mọi id đó đều chấp nhận được, ví dụ 2 bản trùng của cùng tài liệu).
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
DEFAULT_GOLDEN = os.path.join(REPO, "tests", "retrieval_eval", "golden_selfdocs.json")
KS = (1, 3, 5)


def load_golden(path: str) -> list:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    out = []
    for i, row in enumerate(data):
        q, gold = row.get("q"), row.get("gold")
        if not q or not isinstance(gold, list) or not gold:
            raise ValueError(f"golden[{i}] thiếu 'q' hoặc 'gold' (list không rỗng)")
        out.append({"q": q, "gold": set(gold), "note": row.get("note", "")})
    return out


def first_hit_rank(ranked_ids: list, gold: set):
    """Vị trí (0-based) của kết quả đúng đầu tiên, hoặc None."""
    for pos, uid in enumerate(ranked_ids):
        if uid in gold:
            return pos
    return None


def evaluate(search_fn, golden: list, ks=KS) -> dict:
    """search_fn(query, top_k) -> list[{'id': ...}]. Trả metrics + danh sách miss."""
    top_k = max(ks)
    hits = {k: 0 for k in ks}
    rr = 0.0
    misses = []
    for row in golden:
        ranked = [r["id"] for r in search_fn(row["q"], top_k)]
        pos = first_hit_rank(ranked, row["gold"])
        if pos is None:
            misses.append({"q": row["q"], "gold": sorted(row["gold"]), "top1": ranked[:1]})
            continue
        rr += 1.0 / (pos + 1)
        for k in ks:
            hits[k] += pos < k
    n = len(golden)
    return {
        "n": n,
        **{f"recall@{k}": (hits[k] / n if n else 0.0) for k in ks},
        "mrr": rr / n if n else 0.0,
        "misses": misses,
    }


def print_table(res: dict) -> None:
    print(f"n={res['n']}  " + "  ".join(f"R@{k} {res[f'recall@{k}']:.3f}" for k in KS) + f"  MRR {res['mrr']:.3f}")
    if res["misses"]:
        print(f"Miss ({len(res['misses'])}):")
        for m in res["misses"]:
            print(f"  - {m['q']}\n      gold: {m['gold'][0]}{' (+%d)' % (len(m['gold']) - 1) if len(m['gold']) > 1 else ''}"
                  f" | top1: {m['top1'][0] if m['top1'] else '(rỗng)'}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Retrieval regression eval cho KnowledgeLib.")
    ap.add_argument("--golden", default=DEFAULT_GOLDEN)
    ap.add_argument("--dir", default=REPO, help="Thư mục kho dữ liệu (KNOWLEDGELIB_PATH)")
    ap.add_argument("--min-r3", type=float, default=None, help="Ngưỡng Recall@3 tối thiểu, dưới thì exit 1")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    sys.path.insert(0, HERE)
    os.environ.setdefault("KNOWLEDGELIB_PATH", os.path.abspath(args.dir))
    from agent_client import KnowledgeLibClient  # noqa: E402

    client = KnowledgeLibClient(args.dir)
    if client.collection is None:
        print("⚠️ Chroma không dùng được: số đo chỉ phản ánh keyword catalog.", file=sys.stderr)

    res = evaluate(lambda q, k: client.search(q, top_k=k), load_golden(args.golden))
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print_table(res)
    if args.min_r3 is not None and res["recall@3"] < args.min_r3:
        print(f"❌ Recall@3 {res['recall@3']:.3f} < ngưỡng {args.min_r3}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
