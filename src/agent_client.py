#!/usr/bin/env python3
"""
KnowledgeLib Hybrid Vector Client Helper (ChromaDB + Keyword Search).
Dùng cho Agent chạy trên các repository khác trên cùng máy local để tìm kiếm và trích xuất tri thức từ knowledgelib_data.
"""

import os
import sys
import json
import math
import re
from collections import Counter, defaultdict

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from query_miss_log import log_miss
from embedding import LEGACY_COLLECTION, ML_COLLECTION, load_embedder
from alias_overlay import load_extra_aliases, merged_aliases

try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

DEFAULT_KNOWLEDGELIB_PATH = os.environ.get(
    "KNOWLEDGELIB_PATH", os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

# Danh sách từ khóa Router (Cơ chế 3 Gatekeeper)
KNOWLEDGE_ROUTER_KEYWORDS = {
    # Product & Reviews
    "best", "compare", "vs", "review", "top", "2025", "2026", "buying guide",
    # Consumer & Baby & Home
    "baby", "bottle", "stroller", "car seat", "crib", "monitor", "cleaner", "coffee", "mattress",
    # Electronics & Hardware
    "laptop", "phone", "tv", "audio", "headphone", "monitor", "camera", "gpu", "keyboard",
    # Tech & Software & DevOps
    "system design", "devops", "debugging", "security", "migration", "architecture", "vpn", "docker", "kubernetes",
    # Business & SaaS & Finance
    "gtm", "saas", "pricing", "valuation", "benchmark", "metrics", "compliance", "iso", "gdpr", "soc2"
}

# Ngưỡng vector distance (cosine) để coi câu hỏi "trong scope" khi không match whitelist.
# Mỗi model có thang distance riêng nên ngưỡng đi theo collection đang dùng:
#  - legacy (all-MiniLM-L6-v2): trong scope ~0.25-0.55, ngoài scope ~0.7-0.85.
#  - multilingual-e5-base: similarity dồn về vùng cao. Đo 5 câu mỗi loại: trong scope 0.107-0.194,
#    ngoài scope 0.155-0.222. Tách được phần lớn nhưng còn chồng lấn, nên ngưỡng đặt chặt (ưu tiên
#    không cho câu ngoài scope lọt qua); câu hợp lệ bị rớt vẫn còn whitelist từ khoá.
VECTOR_SCOPE_DISTANCE_THRESHOLD = 0.6
ML_VECTOR_SCOPE_DISTANCE_THRESHOLD = 0.14

# Hybrid fusion: điểm = ALPHA * vector_norm + (1 - ALPHA) * bm25_norm (min-max trong pool ứng viên).
# Đo trên golden set: fusion theo điểm tốt hơn RRF theo hạng, vì RRF đẩy unit chỉ xuất hiện ở một
# nguồn xuống dù nguồn đó rất chắc chắn.
FUSION_ALPHA = 0.4
FUSION_POOL = 50

# Giữ lại để tương thích (templates/web UI đọc khoá rrf_score).
RRF_K = 60

# Hệ số ưu tiên cho tài liệu nội bộ (self-docs). Chỉ ở mức phân định khi hai unit ngang điểm:
# hệ số lớn (1.4 trước đây) làm self-docs lấn át câu hỏi kiến thức chung.
SELF_DOCS_BOOST = 1.03

# BM25
BM25_K1 = 1.2
BM25_B = 0.75


def excluded_domains() -> list:
    """Domain/thư mục bị ẩn (KNOWLEDGELIB_EXCLUDE_DOMAINS, phân tách bằng dấu phẩy). Đọc mỗi lần gọi để test và đổi env có hiệu lực ngay."""
    raw = os.environ.get("KNOWLEDGELIB_EXCLUDE_DOMAINS", "")
    return [d.strip().strip("/").lower() for d in raw.split(",") if d.strip().strip("/")]


def is_excluded(unit_id: str = "", domain: str = "") -> bool:
    """True nếu unit nằm dưới một domain bị loại. Khớp theo đoạn đầu của id (thư mục) hoặc domain ("a > b")."""
    ex = excluded_domains()
    if not ex:
        return False
    uid = os.path.normpath((unit_id or "").strip().lstrip("/")).replace("\\", "/").lower()
    dom = (domain or "").strip().lower()
    for d in ex:
        if uid == d or uid.startswith(d + "/") or dom == d or dom.startswith(d + " >") or dom.startswith(d + "/"):
            return True
    return False


def _tokens(text: str) -> list:
    """Unigram + bigram. Bigram giữ được từ ghép tiếng Việt ("thiết kế", "bàn giao")."""
    words = re.findall(r"\w+", (text or "").lower())
    return words + [a + "_" + b for a, b in zip(words, words[1:])]


class KnowledgeLibClient:
    def __init__(self, data_path: str = DEFAULT_KNOWLEDGELIB_PATH):
        self.data_path = os.path.abspath(data_path)
        self.catalog_path = os.path.join(self.data_path, "catalog.json")
        self.db_dir = os.path.join(self.data_path, ".chroma_db")
        self.catalog = self._load_catalog()
        
        self._bm25 = None

        # Cấu hình ChromaDB Vector Search Persistent
        self.chroma_client = None
        self.collection = None
        self.embedder = None  # None -> collection legacy tự embed bằng model mặc định của Chroma
        if CHROMADB_AVAILABLE and os.path.exists(self.db_dir):
            try:
                self.chroma_client = chromadb.PersistentClient(path=self.db_dir)
                self.collection = self._open_best_collection()
            except BaseException as e:
                # Rust binding của chromadb có thể panic (pyo3 PanicException kế thừa BaseException,
                # `except Exception` không bắt được) -> vẫn phải rơi về keyword search thay vì sập process.
                if isinstance(e, (KeyboardInterrupt, SystemExit)):
                    raise
                self.chroma_client = None
                self.collection = None
                self.embedder = None
                print(f"Warning: ChromaDB initialization error ({e}). Falling back to catalog keyword search.")

    def _open_best_collection(self):
        """Ưu tiên collection đa ngữ (e5) nếu đã index và nạp được model; không thì dùng legacy."""
        try:
            ml = self.chroma_client.get_collection(name=ML_COLLECTION)
        except Exception:
            ml = None
        if ml is not None and ml.count() > 0:
            embedder = load_embedder()
            if embedder is not None:
                self.embedder = embedder
                return ml
        return self.chroma_client.get_collection(name=LEGACY_COLLECTION)

    def _load_catalog(self) -> dict:
        if not os.path.exists(self.catalog_path):
            raise FileNotFoundError(f"Catalog file not found at: {self.catalog_path}")
        with open(self.catalog_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def is_knowledge_query(self, query: str) -> bool:
        """
        Kiểm tra nhanh xem câu hỏi có nằm trong scope tri thức không.
        Pass nếu match whitelist từ khóa HOẶC vector distance đủ gần (semantic gate),
        để câu hỏi hợp lệ nhưng thiếu đúng từ khóa trong danh sách vẫn lọt qua.
        """
        query_lower = query.lower()
        if any(kw in query_lower for kw in KNOWLEDGE_ROUTER_KEYWORDS):
            return True

        vec_results = self.vector_search(query, top_k=1)
        threshold = ML_VECTOR_SCOPE_DISTANCE_THRESHOLD if self.embedder else VECTOR_SCOPE_DISTANCE_THRESHOLD
        if vec_results and vec_results[0]["distance"] < threshold:
            return True

        return False

    def vector_search(self, query: str, top_k: int = 3) -> list:
        """Tìm kiếm ngữ nghĩa (Semantic Vector Search) qua ChromaDB."""
        if not self.collection:
            return []
        try:
            if self.embedder is not None:
                results = self.collection.query(
                    query_embeddings=self.embedder.embed_queries([query]),
                    n_results=top_k
                )
            else:
                results = self.collection.query(
                    query_texts=[query],
                    n_results=top_k
                )
            matched_units = []
            if results and results.get("ids") and len(results["ids"]) > 0:
                ids = results["ids"][0]
                metadatas = results["metadatas"][0] if results.get("metadatas") else []
                distances = results["distances"][0] if results.get("distances") else []
                
                for idx, unit_id in enumerate(ids):
                    meta = metadatas[idx] if idx < len(metadatas) else {}
                    dist = distances[idx] if idx < len(distances) else 1.0
                    matched_units.append({
                        "id": unit_id,
                        "canonical_question": meta.get("canonical_question", ""),
                        "domain": meta.get("domain", ""),
                        "entity_type": meta.get("entity_type", ""),
                        "distance": dist,
                        "search_type": "vector"
                    })
            return matched_units
        except BaseException as e:  # gồm cả pyo3 PanicException, xem __init__
            if isinstance(e, (KeyboardInterrupt, SystemExit)):
                raise
            print(f"Vector search failed: {e}")
            return []

    def _build_bm25(self) -> dict:
        """Chỉ mục BM25 trong bộ nhớ trên câu hỏi (x3), alias (x2), domain và content_preview."""
        units = [u for u in self.catalog.get("units", []) if u.get("id")]
        extra = load_extra_aliases(self.data_path)  # alias tiếng Việt cho unit tiếng Anh (config/aliases_vi.json)
        docs = []
        for unit in units:
            toks = _tokens(unit.get("canonical_question", "")) * 3
            for alias in merged_aliases(unit, extra):
                toks += _tokens(str(alias)) * 2
            toks += _tokens(re.sub(r"[>_\-/]", " ", unit.get("domain", "") or ""))
            toks += _tokens(unit.get("content_preview", ""))
            docs.append(Counter(toks))
        n = len(docs)
        lengths = [sum(d.values()) for d in docs]
        avg_len = (sum(lengths) / n) if n else 0.0
        df = Counter()
        postings = defaultdict(list)
        for idx, doc in enumerate(docs):
            df.update(doc.keys())
            for tok, freq in doc.items():
                postings[tok].append((idx, freq))
        # IDF theo ngôn ngữ: kho chủ yếu tiếng Anh nên từ tiếng Việt rất phổ biến ("phân tích", "cho")
        # vẫn hiếm trên toàn kho và được IDF cao, lấn át từ khoá thật (vd "PESTLE"). Token có dấu
        # được tính IDF trên tập unit có chứa token có dấu, không phải trên toàn kho.
        n_accented = sum(1 for doc in docs if any(not tok.isascii() for tok in doc)) or n
        idf = {}
        for tok, cnt in df.items():
            total = n if tok.isascii() else max(n_accented, cnt)
            idf[tok] = math.log(1 + (total - cnt + 0.5) / (cnt + 0.5))
        return {"units": units, "lengths": lengths, "avg_len": avg_len, "postings": postings, "idf": idf}

    def keyword_search(self, query: str, top_k: int = 3) -> list:
        """Tìm kiếm từ khoá bằng BM25 (khớp nguyên token, có IDF) thay cho so khớp chuỗi con."""
        if self._bm25 is None:
            self._bm25 = self._build_bm25()
        index = self._bm25
        scores = defaultdict(float)
        for tok in set(_tokens(query)):
            if len(tok) < 2:
                continue
            idf = index["idf"].get(tok)
            if idf is None:
                continue
            for idx, freq in index["postings"][tok]:
                norm = freq + BM25_K1 * (1 - BM25_B + BM25_B * index["lengths"][idx] / (index["avg_len"] or 1.0))
                scores[idx] += idf * freq * (BM25_K1 + 1) / norm

        ranked = sorted(scores, key=lambda i: scores[i], reverse=True)[:top_k]
        results = []
        for idx in ranked:
            unit_copy = dict(index["units"][idx])
            unit_copy["search_type"] = "keyword"
            unit_copy["score"] = round(scores[idx], 4)
            results.append(unit_copy)
        return results

    def search(self, query: str, top_k: int = 3) -> list:
        """
        Hybrid Search: Vector (ngữ nghĩa, đa ngữ) + BM25 (từ khoá), trộn theo ĐIỂM đã chuẩn hoá
        min-max trong pool ứng viên: fused = ALPHA * vector + (1 - ALPHA) * bm25.
        Chỉ có một nguồn (vd chưa có vector index) thì dùng điểm của nguồn đó.
        """
        pool_size = max(top_k * 5, FUSION_POOL)
        vec_results = self.vector_search(query, top_k=pool_size)
        kw_results = self.keyword_search(query, top_k=pool_size)

        def _normalize(pairs):
            if not pairs:
                return {}
            values = [v for _, v in pairs]
            hi, lo = max(values), min(values)
            span = hi - lo
            return {uid: ((v - lo) / span if span else 1.0) for uid, v in pairs}

        vec_norm = _normalize([(r["id"], 1.0 - (r.get("distance") or 0.0)) for r in vec_results])
        # BM25 chuẩn hoá theo điểm cao nhất (giữ tỉ lệ, pool nhỏ không bị kéo về 0);
        # vector phải min-max vì cosine của e5 dồn trong một dải hẹp.
        kw_top = max((r.get("score") or 0.0 for r in kw_results), default=0.0)
        kw_norm = {r["id"]: ((r.get("score") or 0.0) / kw_top if kw_top else 0.0) for r in kw_results}
        if vec_norm and kw_norm:
            w_vec, w_kw = FUSION_ALPHA, 1.0 - FUSION_ALPHA
        else:
            w_vec, w_kw = (1.0, 0.0) if vec_norm else (0.0, 1.0)

        merged = {}
        for r in vec_results:
            d = merged.setdefault(r["id"], {"id": r["id"], "sources": set()})
            d["canonical_question"] = r.get("canonical_question", "")
            d["domain"] = r.get("domain", "")
            d["entity_type"] = r.get("entity_type", "")
            d["distance"] = r.get("distance")
            d["sources"].add("vector")
        for r in kw_results:
            d = merged.setdefault(r["id"], {"id": r["id"], "sources": set()})
            d["canonical_question"] = r.get("canonical_question", d.get("canonical_question", ""))
            d["domain"] = r.get("domain", d.get("domain", ""))
            d["entity_type"] = r.get("entity_type", d.get("entity_type", ""))
            d["aliases"] = r.get("aliases", [])
            d["score"] = r.get("score")
            d["sources"].add("keyword")

        fused = {}
        for unit_id, d in merged.items():
            value = w_vec * vec_norm.get(unit_id, 0.0) + w_kw * kw_norm.get(unit_id, 0.0)
            # Tiered Retrieval Boost: ưu tiên nhẹ tài liệu nội bộ (self-docs) khi ngang điểm.
            if (d.get("domain") or "").startswith("self-docs"):
                value *= SELF_DOCS_BOOST
            fused[unit_id] = value

        ranked_ids = [
            uid for uid in sorted(fused, key=lambda uid: fused[uid], reverse=True)
            if not is_excluded(uid, merged[uid].get("domain", ""))
        ][:top_k]

        results = []
        for unit_id in ranked_ids:
            d = merged[unit_id]
            sources = d.pop("sources")
            d["search_type"] = "hybrid" if len(sources) > 1 else next(iter(sources))
            d["fused_score"] = fused[unit_id]
            d["rrf_score"] = fused[unit_id]  # tên cũ, giữ cho web UI / client hiện có
            d.setdefault("distance", None)
            d.setdefault("score", None)
            d.setdefault("aliases", [])
            results.append(d)
        return results

    def get_unit_content(self, unit_id: str) -> str:
        """Đọc toàn bộ nội dung tệp Markdown của Unit. Unit bị loại báo y hệt unit không tồn tại (không lộ sự tồn tại)."""
        if is_excluded(unit_id):
            return f"Error: Unit file not found at {os.path.join(self.data_path, f'{unit_id}.md')}"
        file_path = os.path.join(self.data_path, f"{unit_id}.md")
        inside = os.path.abspath(file_path).startswith(self.data_path + os.sep)
        if not inside or not os.path.exists(file_path):
            return f"Error: Unit file not found at {file_path}"
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def query_and_get(self, query: str, top_k: int = 1) -> dict:
        """
        Hàm giao tiếp chuẩn cho Agent:
        Tra cứu Hybrid Search -> Trả về Metadata & Content Markdown.

        top_k=1 (mặc định, tương thích ngược): trả schema đơn (unit_id/metadata/content ở top-level).
        top_k>1: trả "matches": [{unit_id, search_type, metadata, content}, ...] để agent tự chọn.
        """
        matched_units = self.search(query, top_k=top_k)
        if not matched_units:
            log_miss(query, source="query_and_get", repo_dir=self.data_path)
            return {
                "status": "not_found",
                "message": "No matching knowledge unit found.",
                "should_fallback_to_llm": True
            }

        if top_k == 1:
            top_unit = matched_units[0]
            unit_id = top_unit["id"]
            content = self.get_unit_content(unit_id)
            return {
                "status": "success",
                "unit_id": unit_id,
                "search_type": top_unit.get("search_type", "hybrid"),
                "metadata": top_unit,
                "content": content,
                "should_fallback_to_llm": False
            }

        matches = []
        for unit in matched_units:
            matches.append({
                "unit_id": unit["id"],
                "search_type": unit.get("search_type", "hybrid"),
                "metadata": unit,
                "content": self.get_unit_content(unit["id"]),
            })
        return {
            "status": "success",
            "matches": matches,
            "should_fallback_to_llm": False
        }

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "cloud storage solution for small business"
    client = KnowledgeLibClient()
    
    print(f"🔍 Query: '{query}'")
    print(f"🚦 Is Knowledge Scope: {client.is_knowledge_query(query)}")
    
    res = client.query_and_get(query)
    print(f"📌 Status: {res['status']}")
    if res['status'] == 'success':
        print(f"✅ Matched Unit ID: {res['unit_id']} (Search Type: {res['search_type']})")
        print(f"📄 Content Snippet: {res['content'][:180]}...")
