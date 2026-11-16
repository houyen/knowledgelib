---
id: software/system-design/book-60-days/llm-application-design
canonical_question: How should engineering teams design reliable, high-throughput production architectures for LLM knowledge retrieval, classification, structured outputs, and vector storage?
aliases:
- production llm system design patterns
- choosing vector databases for high throughput
- handling embedding drift and model upgrades
- enforcing structured json outputs from llms
- optimizing llm classification few shot vs cot
- managing large document context windows rag
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: '2026-11-16'
source_type: summary
source: Summary in our own words of scenario days 27, 28, 34, 38, 46, 54 from "60 Days of System Design Questions" (Joud Awad), a scenario workbook. No text copied.
---

# Production LLM Architecture: Retrieval, Classification, Contracts, and Vector Infrastructure

## TL;DR
Decouple dynamic facts from model parameters by routing ephemeral data through retrieval pipelines rather than retraining weights. Enforce strict data contracts using native constrained decoding at the API layer, and bridge classification accuracy deficits by seeding prompts with ambiguous edge-case demonstrations instead of chaining verbose reasoning. For data stores, isolate vector versions during embedding model migrations to prevent geometric contamination, and select vector engines that execute metadata filtering inline with approximate nearest-neighbor traversal.

---

## 1. Knowledge Freshness: Decoupling Memory from Reasoning

### The Problem
A customer support agent backed by a static model generates outdated answers after recurring product releases, producing a 15% error rate on 2,000 daily queries.

### Recommended Pattern: Retrieval-Augmented Generation (RAG)
Keep the underlying foundation model frozen and offload domain knowledge to a query-time retrieval pipeline. Document changes in the knowledge base are re-indexed independently without initiating training jobs. When a request arrives, the service fetches relevant segments from the vector store and injects them into the prompt. This isolates volatile information from model weights, allowing updates to reflect instantly in production answers while avoiding model fine-tuning overhead.

### Traps and Failure Modes
- **Fine-Tuning Base Weights:** Treating factual updates as a fine-tuning problem bakes transient knowledge into network weights. Weekly product updates trigger weekly retraining runs, accumulating steep compute expenses and introducing catastrophic forgetting of earlier domain contexts. Fine-tuning adjusts style, tone, and grammar—not mutable facts.
- **Fine-Tuning + RAG Hybrid:** Implementing an dual architecture before establishing a baseline retrieval layer introduces unnecessary complexity. Hybrid setups require substantial operational investment and should only be evaluated after standard retrieval hits clear quality limits.
- **System Prompt Inflation:** Concatenating product documentation into the primary prompt quickly exhausts context windows, bloats latency, and spikes token costs. Manually curating text snippets inside prompt templates is an unscalable, brittle reimplementation of automated retrieval.

| Strategy | Update Latency | Compute / Maintenance Cost | Risk of Stale Knowledge |
| :--- | :--- | :--- | :--- |
| **RAG (Recommended)** | Instantaneous (pipeline ingestion) | Low (embedding generation only) | Minimal; reflects current index |
| **Fine-Tuning** | Days to weeks per training loop | High (recurrent GPU training) | High between training cycles |
| **Hybrid (FT + RAG)** | High engineering overhead | Very high (dual pipelines) | Low, but excessive operational surface |
| **Prompt Engineering** | Manual on every release | Low direct cost, high token overhead | High; drops content past token limits |

---

## 2. Ticket Classification: Calibrating Boundaries Under Noisy Inputs

### The Problem
A triage pipeline handling 50,000 support tickets weekly stalls at 71% classification accuracy across six categories, requiring a jump past 90% without swapping models or increasing inference expenditure.

### Recommended Pattern: Targeted Few-Shot Edge-Case Priming
Inject three to five production samples illustrating confusing boundary conditions directly into the prompt context. Rather than demonstrating obvious classifications, the examples must target historically mislabeled overlaps—such as payment complaints triggered by authentication failures. This calibrates the model's pattern recognition against ambiguous boundaries, routinely raising accuracy to 88–93% while adding negligible token overhead.

### Traps and Failure Modes
- **Zero-Shot Prompt Clarification:** Elaborating rule sets and enumerating exceptions in the system prompt caps accuracy near 78–82%. Natural language definitions cannot reliably instruct a probabilistic model on how to prioritize intersecting intents when real customer inputs blend multiple categories.
- **Chain-of-Thought (CoT) Prompting:** Demanding intermediate reasoning increases latency by 200–400ms without improving classification accuracy. When dealing with overlapping labels, the model frequently latches onto an early detail in its rationalization chain, generating a plausible narrative that concludes with the incorrect category.
- **Self-Consistency Voting:** Running five parallel passes at higher temperature and aggregating votes achieves 93–96% accuracy, but scales inference costs by 500% ($500/week versus $100/week). For high-volume support triage where human routing errors cost cents, majority voting is an inefficient allocation of capital.

| Strategy | Production Accuracy | In-Flight Latency Delta | Relative Inference Cost |
| :--- | :--- | :--- | :--- |
| **Few-Shot Boundary Priming** | 88% – 93% | Minimal (+~150 input tokens) | ~1.0x |
| **Zero-Shot Instruction Tuning** | 78% – 82% | Neutral | ~1.0x |
| **Chain-of-Thought (CoT)** | 70% – 73% | High (+200ms to +400ms) | ~1.3x – 1.6x (output tokens) |
| **Self-Consistency (5x)** | 93% – 96% | High (bounded by slowest call) | ~5.0x |

---

## 3. Large Context Ingestion: Handling Massive Input Spans

### The Problem
A 150,000-word source manual exceeds the 128K token ceiling of an inference model, requiring precise factual question-answering over granular provisions.

### Recommended Pattern: Overlapping Chunking with Vector Retrieval
Divide the corpus into overlapping segments of approximately 500 tokens, preserving 10–20% token overlap across sentence and paragraph boundaries. Ingest these chunks into an approximate nearest neighbors (ANN) index. At query time, extract the top-$k$ semantically matching passages and construct a compact context window. This maintains query performance within fixed token constraints, bounds latency, and retains localized precision.

### Traps and Failure Modes
- **Sliding Window Inference:** Iterating across the document through sequential overlapping calls requires $O(n)$ model evaluations per question. Processing 150,000 words this way takes several minutes per query and fails to reconcile facts dispersed across non-adjacent segments.
- **Progressive Hierarchical Summarization:** Compressing sections recursively into rolled-up summaries strips specific clauses, dates, and identifier keys. While functional for global executive summaries, lossy compression makes exact factual extraction on specific sub-clauses impossible.
- **Tail or Head Truncation:** Slicing the input to fit arbitrary token ceilings drops source context blind. Furthermore, positional degradation ("lost in the middle") impairs retrieval when answers reside deep within large contexts.

| Method | Latency per Query | Query Cost Complexity | Granular Fact Preservation |
| :--- | :--- | :--- | :--- |
| **Chunked Vector Retrieval** | <100ms retrieval + 1 LLM call | $O(1)$ inference | High (isolated verbatim chunks) |
| **Sliding Window Execution** | Minutes (sequential scans) | $O(n)$ inference | High, but fails across distant spans |
| **Progressive Summarization** | Minutes (pre-pass reduction) | $O(n)$ build, $O(1)$ query | Very Low (lossy compression) |
| **Hard Truncation** | Fast (single call) | $O(1)$ inference | Zero for truncated regions |

---

## 4. Output Contracts: Enforcing Typed Payloads at the Boundary

### The Problem
An automated customer refund agent generates informal schema variations (e.g., text numbers, missing IDs, or conversational text), breaking downstream transactional pipelines.

### Recommended Pattern: API-Level Constrained Decoding
Bind model generation directly to schema definitions (such as JSON Schema via OpenAI Structured Outputs, Gemini response schemas, or Bedrock tool specifications). At the engine level, invalid tokens are dynamically masked from the probability distribution during generation. The resulting stream is guaranteed to match the declared types, eliminating parsing failures, deserialization errors, and fallback retry loops.

### Traps and Failure Modes
- **Prompt-Based Formatting Mandates:** Directing the model to "output only raw JSON" remains an advisory suggestion. Under temperature variance and complex context, edge-case requests generate explanatory preambles, markdown formatting fences, or type-coerced values that break API contracts.
- **Post-Hoc Retry Loops:** Catching schema validation exceptions in an application layer and invoking corrective retries incurs compound latency and multiplies API charges during upstream traffic spikes. Retries fail when the model repeatedly struggles with ambiguous underlying inputs.
- **LLM-as-a-Judge Gateways:** Delegating schema verification to an auxiliary scoring model introduces 200–500ms of latency without providing structural guarantees. Evaluation models are subject to the same probabilistic drift and can approve subtly invalid JSON.

| Technique | Schema Reliability | Latency Overhead | Behavior Under Edge Cases |
| :--- | :--- | :--- | :--- |
| **Constrained Decoding (Native)** | 100% deterministic | None | Tokens forced into schema path |
| **Prompt Engineering Only** | ~95% – 98% | None | Generates prose fences / malformed types |
| **Validation + Retries** | Variable (bounded by retries) | Unpredictable (spikes 2x–3x) | Exceeds retry ceilings on hard inputs |
| **LLM-as-a-Judge** | Subjective / Non-guaranteed | High (+200ms – 500ms) | Vulnerable to hallucinated approvals |

---

## 5. Vector Storage: Sizing for Throughput and Filtered Queries

### The Problem
A B2B search workload requires sub-100ms p99 latency across 4 million 1536-dimensional embeddings (~24GB raw data), with a query load of 300 req/s peaking to 900 req/s under strict multi-tenant boundary constraints.

### Recommended Pattern: Dedicated In-Memory Engines with Native Single-Stage Filtering (Qdrant)
Deploy a purpose-built vector engine written in a systems language that co-locates metadata filtering with HNSW graph exploration. In multi-tenant environments, users search exclusively within isolated workspace boundaries. Running vector distance calculations and payload filters concurrently preserves index recall without requiring expensive post-filtering passes. Native memory mapping and low-overhead runtimes provide stable resource utilization under 900 req/s spikes.

### Traps and Failure Modes
- **Relational Extensions (pgvector):** Managing 4 million high-dimensional rows in relational buffer pools degrades under sustained concurrent access. At 300+ req/s, transactional locks, cache contention, and background maintenance operations (such as VACUUM) cause latency to spike unpredictably.
- **Pure Serverless Vector Services (Pinecone):** While reducing maintenance overhead, query-unit pricing tiers at 300–900 continuous req/s lead to high operating costs. Proprietary APIs also complicate storage migrations.
- **Complex Multi-Modal Platforms (Weaviate):** Running heavy containerized clusters introduces operational maintenance debt when the primary workload only requires fast, dense filtered retrieval.

| Engine Candidate | 300–900 req/s Concurrency | Multi-Tenant Filtering Architecture | Operational Profile |
| :--- | :--- | :--- | :--- |
| **Qdrant (Recommended)** | High throughput (Rust native) | Single-stage payload filtering | Lean self-hosted or managed footprint |
| **pgvector** | Degrades under heavy query load | Pre-filter or post-filter join overhead | Shared with transactional database |
| **Pinecone** | Supported | Managed metadata filtering | High volume-based billing |
| **Weaviate** | Supported | Inverted index integration | Heavy Kubernetes operational surface |

---

## 6. Embedding Drift: Managing Model Updates Across Large Indexes

### The Problem
A production vector corpus of 50 million chunks (400GB index) suffers degraded search quality after upstream document updates and regular 6-week embedding model revisions. Full index builds cost $800 and take 4 hours.

### Recommended Pattern: Vector Registry with Dual-Index Hot Swaps
Assign explicit model version tags to all stored embeddings. When releasing a new embedding model, spin up an independent index corresponding to that version. Direct ingestion pipelines to populate the target space, route read traffic through shadow validation or partial canaries, and execute an atomic routing shift once the migration completes. This prevents comparisons across incompatible vector spaces while maintaining zero query downtime.

### Traps and Failure Modes
- **Incremental In-Place Upserts:** Only re-embedding modified source records creates an index containing vectors produced by different model checkpoints. Nearest-neighbor math breaks down when calculating similarity across divergent geometric projections, degrading recall across the entire dataset.
- **Unconditional Weekly Re-Indexing:** Re-embedding 50 million chunks on a recurring schedule wastes API spend and compute resources when underlying documents or model versions have not changed.
- **Sampling-Based Drift Detection:** Calculating cosine distance between stored vectors and random fresh embeddings alerts teams to the presence of drift, but fails to isolate which vectors are obsolete or reconcile the index. Monitoring is an alert mechanism, not a migration strategy.

| Strategy | Mathematical Vector Consistency | Zero-Downtime Migration | Infrastructure Cost Profile |
| :--- | :--- | :--- | :--- |
| **Version Registry + Hot Swap** | Guaranteed (pure spaces) | Native via traffic routing | Predictable; isolated to upgrade periods |
| **Incremental In-Place Upserts** | Broken (mixed coordinate spaces) | Yes, but returns corrupted results | Low direct spend, high quality loss |
| **Periodic Full Rebuilding** | Maintained after rebuild | Blocked during 4-hour re-indexes | High, recurring wasteful spend |
| **Drift Detection Alerts Only** | Unaddressed | None | Low (observation only) |

---

## Decision Cheatsheet

| Symptom / Requirement | Root Cause | Selected Pattern |
| :--- | :--- | :--- |
| Model delivers outdated product facts | Static parameter weights | RAG: Isolate evolving data into a vector pipeline |
| Classification accuracy hits ceiling on messy inputs | Unclear category boundary definitions | Few-shot prompting with ambiguous boundary examples |
| Source text exceeds context window | Hardware and memory capacity constraints | Overlapping sentence-level chunking with top-$k$ retrieval |
| Downstream systems fail on malformed JSON | Probabilistic token sampling | Constrained decoding via API response schema definitions |
| Multi-tenant queries slow down under high RPS | Decoupled metadata filtering and ANN search | Dedicated vector database with single-stage payload filtering |
| Search recall degrades following model updates | Vectors evaluated across disparate geometric spaces | Version registry with parallel index hot-swapping |

---
*Source: Summary in our own words of scenario days 27, 28, 34, 38, 46, 54 from "60 Days of System Design Questions" (Joud Awad), a scenario workbook. No text copied.*
