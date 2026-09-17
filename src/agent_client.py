#!/usr/bin/env python3
"""
KnowledgeLib Hybrid Vector Client Helper (ChromaDB + Keyword Search).
Dùng cho Agent chạy trên các repository khác trên cùng máy local để tìm kiếm và trích xuất tri thức từ knowledgelib_data.
"""

import os
import sys
import json
import re

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from query_miss_log import log_miss

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
# Calibrated: câu hỏi liên quan tri thức trong kho -> distance ~0.25-0.55; câu hỏi ngoài scope -> ~0.7-0.85.
VECTOR_SCOPE_DISTANCE_THRESHOLD = 0.6

# Reciprocal Rank Fusion constant cho hybrid search (giá trị chuẩn theo paper RRF, ít nhạy với k).
RRF_K = 60

class KnowledgeLibClient:
    def __init__(self, data_path: str = DEFAULT_KNOWLEDGELIB_PATH):
        self.data_path = os.path.abspath(data_path)
        self.catalog_path = os.path.join(self.data_path, "catalog.json")
        self.db_dir = os.path.join(self.data_path, ".chroma_db")
        self.catalog = self._load_catalog()
        
        # Cấu hình ChromaDB Vector Search Persistent
        self.chroma_client = None
        self.collection = None
        if CHROMADB_AVAILABLE and os.path.exists(self.db_dir):
            try:
                self.chroma_client = chromadb.PersistentClient(path=self.db_dir)
                self.collection = self.chroma_client.get_collection(name="knowledgelib_units")
            except Exception as e:
                print(f"Warning: ChromaDB initialization error ({e}). Falling back to catalog keyword search.")

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
        if vec_results and vec_results[0]["distance"] < VECTOR_SCOPE_DISTANCE_THRESHOLD:
            return True

        return False

    def vector_search(self, query: str, top_k: int = 3) -> list:
        """Tìm kiếm ngữ nghĩa (Semantic Vector Search) qua ChromaDB."""
        if not self.collection:
            return []
        try:
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
        except Exception as e:
            print(f"Vector search failed: {e}")
            return []

    def keyword_search(self, query: str, top_k: int = 3) -> list:
        """Tìm kiếm khớp từ khóa (Keyword/Alias Search)."""
        query_words = set(re.findall(r'\w+', query.lower()))
        results = []

        for unit in self.catalog.get("units", []):
            score = 0
            canonical = unit.get("canonical_question", "").lower()
            aliases = [a.lower() for a in unit.get("aliases", [])]
            domain = unit.get("domain", "").lower()
            
            for word in query_words:
                if len(word) < 2:
                    continue
                if word in canonical:
                    score += 3
                for alias in aliases:
                    if word in alias:
                        score += 2
                if word in domain:
                    score += 1

            if score > 0:
                unit_copy = dict(unit)
                unit_copy["search_type"] = "keyword"
                unit_copy["score"] = score
                results.append((score, unit_copy))

        results.sort(key=lambda x: x[0], reverse=True)
        return [unit for score, unit in results[:top_k]]

    def search(self, query: str, top_k: int = 3) -> list:
        """
        Hybrid Search thật: chạy song song Vector + Keyword search, kết hợp điểm
        bằng Reciprocal Rank Fusion (RRF) thay vì chỉ OR (vector trước, rỗng mới fallback).
        RRF không cần chuẩn hoá thang điểm giữa 2 nguồn khác nhau (distance vs keyword score).
        """
        pool_size = max(top_k * 3, 10)
        vec_results = self.vector_search(query, top_k=pool_size)
        kw_results = self.keyword_search(query, top_k=pool_size)

        rrf_scores = {}
        merged = {}

        for rank, r in enumerate(vec_results):
            unit_id = r["id"]
            rrf_scores[unit_id] = rrf_scores.get(unit_id, 0.0) + 1.0 / (RRF_K + rank + 1)
            d = merged.setdefault(unit_id, {"id": unit_id, "sources": set()})
            d["canonical_question"] = r.get("canonical_question", "")
            d["domain"] = r.get("domain", "")
            d["entity_type"] = r.get("entity_type", "")
            d["distance"] = r.get("distance")
            d["sources"].add("vector")

        for rank, r in enumerate(kw_results):
            unit_id = r["id"]
            rrf_scores[unit_id] = rrf_scores.get(unit_id, 0.0) + 1.0 / (RRF_K + rank + 1)
            d = merged.setdefault(unit_id, {"id": unit_id, "sources": set()})
            d["canonical_question"] = r.get("canonical_question", d.get("canonical_question", ""))
            d["domain"] = r.get("domain", d.get("domain", ""))
            d["entity_type"] = r.get("entity_type", d.get("entity_type", ""))
            d["aliases"] = r.get("aliases", [])
            d["score"] = r.get("score")
            d["sources"].add("keyword")

        ranked_ids = sorted(rrf_scores, key=lambda uid: rrf_scores[uid], reverse=True)[:top_k]

        results = []
        for unit_id in ranked_ids:
            d = merged[unit_id]
            sources = d.pop("sources")
            d["search_type"] = "hybrid" if len(sources) > 1 else next(iter(sources))
            d["rrf_score"] = rrf_scores[unit_id]
            d.setdefault("distance", None)
            d.setdefault("score", None)
            d.setdefault("aliases", [])
            results.append(d)
        return results

    def get_unit_content(self, unit_id: str) -> str:
        """Đọc toàn bộ nội dung tệp Markdown của Unit."""
        file_path = os.path.join(self.data_path, f"{unit_id}.md")
        if not os.path.exists(file_path):
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
