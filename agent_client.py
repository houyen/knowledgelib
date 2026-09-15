#!/usr/bin/env python3
"""
KnowledgeLib Hybrid Vector Client Helper (ChromaDB + Keyword Search).
Dùng cho Agent chạy trên các repository khác trên cùng máy local để tìm kiếm và trích xuất tri thức từ knowledgelib_data.
"""

import os
import sys
import json
import re

try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

DEFAULT_KNOWLEDGELIB_PATH = os.path.abspath(os.path.dirname(__file__))

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
        """Kiểm tra nhanh xem câu hỏi có nằm trong scope tri thức không."""
        query_lower = query.lower()
        return any(kw in query_lower for kw in KNOWLEDGE_ROUTER_KEYWORDS)

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
                results.append((score, unit_copy))

        results.sort(key=lambda x: x[0], reverse=True)
        return [unit for score, unit in results[:top_k]]

    def search(self, query: str, top_k: int = 3) -> list:
        """Hybrid Search: Ưu tiên Vector Search, nếu không tìm thấy sẽ dùng Keyword Search."""
        vec_results = self.vector_search(query, top_k=top_k)
        if vec_results:
            return vec_results
        return self.keyword_search(query, top_k=top_k)

    def get_unit_content(self, unit_id: str) -> str:
        """Đọc toàn bộ nội dung tệp Markdown của Unit."""
        file_path = os.path.join(self.data_path, f"{unit_id}.md")
        if not os.path.exists(file_path):
            return f"Error: Unit file not found at {file_path}"
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def query_and_get(self, query: str) -> dict:
        """
        Hàm giao tiếp chuẩn cho Agent:
        Tra cứu Hybrid Vector Search -> Trả về Metadata & Content Markdown.
        """
        matched_units = self.search(query, top_k=1)
        if not matched_units:
            return {
                "status": "not_found",
                "message": "No matching knowledge unit found.",
                "should_fallback_to_llm": True
            }
        
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
