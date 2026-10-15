#!/usr/bin/env python3
"""
Index health check cho KnowledgeLib: catalog.json <-> ChromaDB <-> file .md.

Phát hiện:
  - missing_in_vector : unit có trong catalog nhưng chưa có trong Chroma (vector search không tìm ra)
  - stale_in_vector   : id còn trong Chroma nhưng đã biến khỏi catalog
  - missing_file      : unit trong catalog không có file .md
  - identical_body    : nhiều unit có body giống hệt nhau (md5)
  - near_dup          : cặp unit có cosine embedding >= threshold (chỉ cảnh báo, không chặn)

Chạy độc lập (không cần mạng):
    python3 src/index_health.py                 # báo cáo
    python3 src/index_health.py --strict        # exit 1 nếu có drift / trùng body
    python3 src/index_health.py --fix            # upsert lại Chroma từ catalog local
"""

import argparse
import hashlib
import json
import os
import sys

DEFAULT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
COLLECTION = "knowledgelib_units"
NEAR_DUP_THRESHOLD = 0.95


def read_body(unit_id: str, target_dir: str) -> str | None:
    """Trả body markdown (bỏ frontmatter), hoặc None nếu thiếu file."""
    path = os.path.join(target_dir, f"{unit_id}.md")
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return None
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            text = parts[2]
    return text.strip()


def open_collection(target_dir: str):
    """Mở collection Chroma, trả None nếu không dùng được (thiếu lib / chưa index)."""
    try:
        import chromadb
    except ImportError:
        return None
    db_dir = os.path.join(target_dir, ".chroma_db")
    if not os.path.isdir(db_dir):
        return None
    try:
        return chromadb.PersistentClient(path=db_dir).get_collection(name=COLLECTION)
    except BaseException as e:
        # chromadb Rust binding có thể panic (pyo3 PanicException là BaseException): không để làm sập caller.
        if isinstance(e, (KeyboardInterrupt, SystemExit)):
            raise
        return None


def check_drift(units: list, vector_ids, target_dir: str) -> dict:
    """So khớp catalog với tập id trong vector store và với file .md trên đĩa."""
    catalog_ids = [u["id"] for u in units if u.get("id")]
    vector_available = vector_ids is not None
    vids = set(vector_ids) if vector_available else set()
    cset = set(catalog_ids)
    return {
        "catalog_total": len(cset),
        "vector_available": vector_available,
        "vector_total": len(vids) if vector_available else None,
        "missing_in_vector": sorted(cset - vids) if vector_available else [],
        "stale_in_vector": sorted(vids - cset) if vector_available else [],
        "missing_file": sorted(i for i in cset if not os.path.exists(os.path.join(target_dir, f"{i}.md"))),
    }


def find_identical_bodies(units: list, target_dir: str) -> list:
    """Nhóm unit có body trùng khít (md5). Bỏ qua body rỗng."""
    groups = {}
    for u in units:
        uid = u.get("id")
        if not uid:
            continue
        body = read_body(uid, target_dir)
        if not body:
            continue
        groups.setdefault(hashlib.md5(body.encode("utf-8")).hexdigest(), []).append(uid)
    return sorted((sorted(v) for v in groups.values() if len(v) > 1), key=lambda g: g[0])


def find_near_duplicates(ids: list, vectors, threshold: float = NEAR_DUP_THRESHOLD, limit: int = 50) -> list:
    """Cặp (score, id_a, id_b) có cosine >= threshold. vectors: ma trận n x d, cùng thứ tự với ids."""
    import numpy as np

    if len(ids) < 2:
        return []
    m = np.asarray(vectors, dtype=np.float32)
    m = m / (np.linalg.norm(m, axis=1, keepdims=True) + 1e-9)
    sim = m @ m.T
    iu = np.triu_indices(len(ids), k=1)
    mask = sim[iu] >= threshold
    pairs = [(float(s), ids[a], ids[b]) for s, a, b in zip(sim[iu][mask], iu[0][mask], iu[1][mask])]
    pairs.sort(key=lambda p: -p[0])
    return pairs[:limit]


def fetch_embeddings(collection, ids: list, batch: int = 500):
    """Lấy embedding đã lưu trong Chroma (không tính lại). Trả (ids_có_vector, ma_trận)."""
    import numpy as np

    got_ids, rows = [], []
    for i in range(0, len(ids), batch):
        res = collection.get(ids=ids[i:i + batch], include=["embeddings"])
        embs = res.get("embeddings")
        if embs is None:
            continue
        for uid, vec in zip(res["ids"], embs):
            got_ids.append(uid)
            rows.append(vec)
    return got_ids, (np.asarray(rows, dtype=np.float32) if rows else np.zeros((0, 0), dtype=np.float32))


def run_checks(target_dir: str, units: list, scope: str = "self-docs", threshold: float = NEAR_DUP_THRESHOLD) -> dict:
    """Chạy toàn bộ kiểm tra. scope: 'self-docs' | 'all' cho near-dup (identical-body luôn quét toàn kho)."""
    coll = open_collection(target_dir)
    vector_ids = None
    if coll is not None:
        try:
            vector_ids = coll.get(include=[])["ids"]
        except Exception:
            vector_ids = None
    report = {"drift": check_drift(units, vector_ids, target_dir)}
    report["identical_body"] = find_identical_bodies(units, target_dir)

    report["near_dup"] = []
    report["near_dup_scope"] = scope
    if coll is not None and vector_ids is not None:
        indexed = set(vector_ids)
        pool = [u["id"] for u in units if u.get("id") in indexed]
        if scope != "all":
            pool = [i for i in pool if i.startswith(scope)]
        try:
            got_ids, mat = fetch_embeddings(coll, pool)
            report["near_dup"] = find_near_duplicates(got_ids, mat, threshold)
        except Exception as e:  # không để lỗi embedding làm hỏng sync
            report["near_dup_error"] = str(e)
    return report


def has_problems(report: dict) -> bool:
    d = report["drift"]
    return bool(d["missing_in_vector"] or d["stale_in_vector"] or d["missing_file"] or report["identical_body"])


def _show(items, limit=8):
    for it in items[:limit]:
        print(f"     - {it}")
    if len(items) > limit:
        print(f"     ... +{len(items) - limit} nữa")


def print_report(report: dict) -> None:
    d = report["drift"]
    print("🩺 Index health")
    print(f"   catalog: {d['catalog_total']} unit | vector: "
          f"{d['vector_total'] if d['vector_available'] else 'KHÔNG DÙNG ĐƯỢC (thiếu .chroma_db/lib)'}")
    if not d["vector_available"]:
        print("   ⚠️ Vector search tắt: agent_client rơi về keyword catalog. Chạy sync/reindex để dựng lại.")
    if d["missing_in_vector"]:
        print(f"   ⚠️ {len(d['missing_in_vector'])} unit có trong catalog nhưng THIẾU trong vector (không tìm ra bằng semantic):")
        _show(d["missing_in_vector"])
    if d["stale_in_vector"]:
        print(f"   ⚠️ {len(d['stale_in_vector'])} id còn trong vector nhưng đã mất khỏi catalog:")
        _show(d["stale_in_vector"])
    if d["missing_file"]:
        print(f"   ⚠️ {len(d['missing_file'])} unit trong catalog không có file .md:")
        _show(d["missing_file"])
    if report["identical_body"]:
        print(f"   ⚠️ {len(report['identical_body'])} nhóm unit có body GIỐNG HỆT (nên gộp, giữ 1 canonical):")
        _show([" == ".join(g) for g in report["identical_body"]])
    if report["near_dup"]:
        print(f"   ℹ️ {len(report['near_dup'])} cặp gần trùng (scope={report['near_dup_scope']}, cosine cao nhất trước):")
        _show([f"{s:.3f}  {a}  <>  {b}" for s, a, b in report["near_dup"]], limit=10)
    if "near_dup_error" in report:
        print(f"   ℹ️ Bỏ qua near-dup: {report['near_dup_error']}")
    if not has_problems(report) and not report["near_dup"]:
        print("   ✅ Không có drift hay trùng lặp.")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Kiểm tra sức khoẻ index KnowledgeLib (catalog/Chroma/file).")
    ap.add_argument("--dir", default=DEFAULT_DIR, help="Thư mục kho dữ liệu")
    ap.add_argument("--scope", default="self-docs", help="Tiền tố id quét near-dup, hoặc 'all'")
    ap.add_argument("--threshold", type=float, default=NEAR_DUP_THRESHOLD, help="Ngưỡng cosine near-dup")
    ap.add_argument("--strict", action="store_true", help="exit 1 nếu có drift/trùng body")
    ap.add_argument("--fix", action="store_true", help="Upsert lại Chroma từ catalog.json local (không cần mạng)")
    ap.add_argument("--json", action="store_true", help="In báo cáo JSON")
    args = ap.parse_args(argv)

    target_dir = os.path.abspath(args.dir)
    catalog_path = os.path.join(target_dir, "catalog.json")
    try:
        with open(catalog_path, "r", encoding="utf-8") as f:
            catalog = json.load(f)
    except (OSError, ValueError) as e:
        print(f"❌ Không đọc được {catalog_path}: {e}", file=sys.stderr)
        return 2

    if args.fix:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from sync_knowledgelib import reindex_chromadb  # noqa: E402

        reindex_chromadb(catalog, target_dir)

    report = run_checks(target_dir, catalog.get("units", []), scope=args.scope, threshold=args.threshold)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_report(report)
    return 1 if (args.strict and has_problems(report)) else 0


if __name__ == "__main__":
    code = main()
    # chromadb (Rust) có thể abort lúc interpreter teardown khi mở >1 client trong 1 process
    # ("recursive_mutex lock failed"), làm exit code sai. Thoát cứng sau khi flush.
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(code)
