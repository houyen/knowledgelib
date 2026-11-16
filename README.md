# 📚 KnowledgeLib Data Repository

A structured, offline-first, tree-organized knowledge repository and agent skill integration for AI-assisted engineering, domain research, and enterprise knowledge retrieval.

---

## 🌟 Overview

KnowledgeLib organizes domain expertise into modular **Knowledge Units** formatted in Markdown with standardized **YAML Frontmatter**. It supports high-speed hybrid search combining local vector embeddings (via ChromaDB) and keyword/canonical alias matching (via `catalog.json`).

* **Total Knowledge Units:** 2,098 Units (catalog as of 2026-11-16)
* **Primary Search Engine:** Persistent ChromaDB Vector Store (`.chroma_db`)
* **Fallback & Catalog Index:** `catalog.json`
* **Agent Integration:** Antigravity / Claude Code / Cursor / Copilot skill protocol (`SKILL.md`)

---

## 🗂️ Domain Taxonomy & Organization

| Domain | Units | Top subdomains (units) |
|---|---:|---|
| `business/` | 596 | erp-integration (166), erp-selection (33), retail-transformation (24), agent-prompts (24), build-vs-buy (21), industry-benchmarks (17), +36 |
| `software/` | 342 | system-design (76), patterns (53), devops (44), debugging (41), migrations (36), security (29), +10 |
| `consumer-electronics/` | 274 | audio (60), gaming (38), phones (36), tv (31), monitors (28), tablets (25), +8 |
| `home/` | 164 | kitchen (37), furniture (33), smart-home (24), office (15), sleep (14), appliances (13), +6 |
| `consulting/` | 161 | agent-prompts (30), recipes (29), signal-stack (27), compliance-moat (22), oia (20), retail-ai (18), +1 |
| `finance/` | 141 | saas-benchmarks (27), insurance (17), financial-ops (14), capital-markets (14), payments (13), banking (11), +6 |
| `self-docs/` | 105 | engine (46), files (19), integration (17), security (13), database (4), operations (3), +2 |
| `computing/` | 87 | laptops (38), data-engineering (19), peripherals (12), networking (9), components (5), telecom (3), +1 |
| `fitness/` | 49 | equipment (25), wearables (19), recovery (5) |
| `compliance/` | 41 | privacy (10), startup-legal (7), tax (6), financial (5), bcp (4), esg (4), +2 |
| `outdoor/` | 37 | garden (26), camping (6), grilling (3), optics (1), hiking (1) |
| `signal-library/` | 19 | retail-sources (12), retail (4), retail-assets (2), agent-prompts (1) |
| `baby/` | 18 | gear (12), feeding (4), nursery (2) |
| `personal-care/` | 16 | grooming (7), beauty (6), wellness (3) |
| `lifestyle/` | 15 | wedding (15) |
| `pet/` | 14 | dogs (11), cats (3) |
| `health/` | 9 | monitoring (4), healthcare-domain (3), hearing (2) |
| `travel/` | 8 | accessories (4), luggage (3), bags (1) |
| `energy/` | 2 | us (2) |

Role skills that sit on top of the library live in `skills/` (`ba-requirements`, `po-backlog`, `sa-solution-design`, `data-spec`).

---

## 🚀 Getting Started

### 1. Requirements & Setup
Ensure Python 3.10+ is installed:
```bash
pip install chromadb pypdf python-docx beautifulsoup4 pyyaml
```

### 2. Querying the Knowledge Base
You can query knowledge units via the Python client:
```python
from src.agent_client import KnowledgeLibClient

client = KnowledgeLibClient()
result = client.query_and_get("How do Data Contracts prevent schema drift?")

print(result["status"])
print(result["unit_id"])
print(result["content"][:500])
```

Or invoke the skill in your AI assistant:
```text
/knowledgelib What are the 7 core legal principles of insurance?
```

### Search quality and the embedding model
Search is hybrid: a multilingual vector index (`intfloat/multilingual-e5-base`, ONNX, CPU) fused with BM25 over
question, aliases, domain and preview. The model (~1 GB) is downloaded once from Hugging Face on first use; without it
the client falls back to the legacy English-only index and BM25.

```bash
python3 src/index_health.py --fix                                   # build / refresh the vector index (incremental)
python3 src/retrieval_eval.py                                       # internal-docs golden set
python3 src/retrieval_eval.py --golden tests/retrieval_eval/golden_general.json
```

Set `KNOWLEDGELIB_EMBED_MODEL` to use another E5 model, or `KNOWLEDGELIB_EMBED_DISABLE=1` to skip the model entirely.

**Vietnamese aliases.** English units get Vietnamese search phrases from `config/aliases_vi.json` (merged at index time,
unit files untouched). After adding English units, generate theirs and re-index:

```bash
python3 src/gen_aliases.py --dry-run     # units still missing aliases (Vietnamese units are skipped)
python3 src/gen_aliases.py               # generate via Gemini CLI (through local 9router, key from ~/.9router.env)
python3 src/import_knowledge.py --sync-only   # update catalog + re-index so the new aliases are searchable
```

### 3. Interactive Web UI
For human browsing and interactive search, launch the local Web UI:
```bash
python3 src/web_ui.py
```
Then navigate to `http://127.0.0.1:8000`.

### 4. Ingesting New Knowledge
To import a new document (PDF, DOCX, MD, TXT, EPUB):
```bash
python3 src/import_knowledge.py "/path/to/document.pdf" \
  --domain-path "software/ai/custom-topic" \
  --domain "software > ai > custom_topic" \
  --type "reference_guide"
```

Or synchronize the entire catalog and vector store:
```bash
python3 src/sync_knowledgelib.py
```

---

## 📄 License

This repository is licensed under the MIT License. See [LICENSE](LICENSE) for details.
