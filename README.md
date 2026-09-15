# 📚 KnowledgeLib Data Repository

A structured, offline-first, tree-organized knowledge repository and agent skill integration for AI-assisted engineering, domain research, and enterprise knowledge retrieval.

---

## 🌟 Overview

KnowledgeLib organizes domain expertise into modular **Knowledge Units** formatted in Markdown with standardized **YAML Frontmatter**. It supports high-speed hybrid search combining local vector embeddings (via ChromaDB) and keyword/canonical alias matching (via `catalog.json`).

* **Total Knowledge Units:** 1,984 Units
* **Primary Search Engine:** Persistent ChromaDB Vector Store (`.chroma_db`)
* **Fallback & Catalog Index:** `catalog.json`
* **Agent Integration:** Antigravity / Claude Code / Cursor / Copilot skill protocol (`SKILL.md`)

---

## 🗂️ Domain Taxonomy & Organization

```text
knowledgelib_data/
├── software/                 # Software architecture, system design, CRM, ITSM, ITAM
│   ├── system-design/        # 60 Days System Design book, Zanzibar Auth
│   ├── crm/salesforce/       # Salesforce platform, Apex, SOQL, flows
│   ├── itsm/servicenow/      # ServiceNow architecture, CMDB, workflows
│   ├── itam/                 # IT asset management, HAM/SAM lifecycle
│   └── ai/                   # Prompt patterns, transformer architecture
├── computing/                # Data engineering, networking, telecommunications
│   ├── data-engineering/     # Patterns of Data Engineering (DEDP)
│   └── telecom/              # Telecom billing, OSS/BSS, protocols
├── finance/                  # Payments, capital markets, banking, insurance
│   ├── payments/             # SWIFT, ISO 20022, SEPA, clearing & settlement
│   ├── capital-markets/      # Securities law, trading manual, LBO, valuation
│   ├── banking/              # Commercial lending, credit risk, trade finance
│   └── insurance/            # P&C license manual, Medicare, health, life
├── compliance/               # BCP, ESG, regulatory governance
│   ├── bcp/                  # Business continuity planning, FFIEC standards
│   └── esg/                  # ESG standards (GRI, SASB, TCFD, CSRD)
├── business/                 # E-commerce, management, operations
│   └── ecommerce/            # E-commerce models, BRD, funnel metrics
└── scripts/                  # Automated batch ingestion and processing pipelines
```

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
from agent_client import KnowledgeLibClient

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

### 3. Ingesting New Knowledge
To import a new document (PDF, DOCX, MD, TXT, EPUB):
```bash
python3 import_knowledge.py "/path/to/document.pdf" \
  --domain-path "software/ai/custom-topic" \
  --domain "software > ai > custom_topic" \
  --type "reference_guide"
```

Or synchronize the entire catalog and vector store:
```bash
python3 sync_knowledgelib.py
```

---

## 🛠️ Local Tools & Ingestion Scripts (`scripts/`)
*(Thư mục `scripts/` được quản lý cục bộ và bỏ qua trong `.gitignore` để bảo vệ các cấu hình bot và biến môi trường cá nhân)*

* `scripts/process_batch_1_payment.py`: Batch processor for payment domain documents.
* `scripts/process_batch_2_capital_market.py`: Batch processor for capital markets manuals.
* `scripts/process_batch_3_banking.py`: Batch processor for commercial banking and lending.
* `scripts/process_batch_4_insurance.py`: Batch processor for insurance and health coverage.
* `scripts/process_remaining_batches.py`: Master processor for Salesforce, ServiceNow, ITAM, BCP, ESG, Ecommerce, Telecom.
* `scripts/ingest_dedp_book.py`: Web crawler and processor for the complete *Patterns of Data Engineering* book.


---

## 📄 License

This repository is licensed under the MIT License. See [LICENSE](LICENSE) for details.
