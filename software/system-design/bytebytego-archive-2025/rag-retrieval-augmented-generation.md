---
id: software/system-design/bytebytego-archive-2025/rag-retrieval-augmented-generation
canonical_question: How does Retrieval-Augmented Generation (RAG) work, and how is it architected across modern application stacks?
aliases:
- rag architecture overview
- retrieval augmented generation guide
- rag vs agentic rag
- rag vs fine tuning
- rag application tech stack
- open source rag tools
- how to build rag on aws
entity_type: book_chapter
domain: software > system-design > bytebytego-archive-2025
last_verified: '2026-11-16'
source_type: summary
source: Summary in our own words of 6 articles from the ByteByteGo "2025 Archive" (system design newsletter collection). No text copied.
---

# Retrieval-Augmented Generation (RAG): Architecture, Tech Stacks, and Design Patterns

## TL;DR
Retrieval-Augmented Generation (RAG) grounds large language model responses in external, domain-specific knowledge bases without requiring model retraining. The architecture runs across an ingestion pipeline that parses, chunks, and indexes data into vector stores, alongside a runtime querying pipeline that matches user prompts against indexed vectors to augment context. For dynamic or multi-step tasks, Agentic RAG extends standard RAG by introducing autonomous planning, tool execution, and memory, contrasting with offline fine-tuning that bakes domain data directly into model weights.

## The Two-Stage Lifecycle: Ingestion and Query Execution
RAG decouples institutional knowledge from base model parameters by implementing two distinct operational stages: ingestion and querying.

### 1. Ingestion Stage
The ingestion stage transforms unstructured domain information into searchable representations:
- **Raw Storage:** Unstructured sources—such as PDFs, web pages, internal documents, codebase repositories, databases, or APIs—are collected and saved into raw storage (such as Amazon S3).
- **Parsing and Chunking:** Specialized ingestion routines or serverless compute functions (such as AWS Lambda) extract clean text, strip extraneous markup, and segment documents into smaller, manageable text chunks.
- **Embedding Generation:** Each text chunk is processed through an embedding model (e.g., Amazon Bedrock Titan Embeddings, Cohere, Nomic) to generate high-dimensional vectors that capture semantic relationships.
- **Vector Indexing:** The resulting embeddings are stored with associated metadata in a vector database or indexing service (such as OpenSearch Serverless, DynamoDB, Milvus, or Weaviate) to enable similarity searches.

### 2. Querying Stage
The querying stage executes at runtime when an end-user issues a request:
- **Request Dispatch:** A query originating from a frontend application (built with Next.js, Vue.js, SvelteKit, or Streamlit) passes through an API Gateway to a backend query service.
- **Query Embedding:** The backend converts the incoming query prompt into a vector representation using the same embedding model family used during ingestion.
- **Similarity Search:** The system executes a semantic similarity search across the vector database to locate the pre-indexed document chunks closest to the query vector.
- **Context Augmentation:** The top matching chunks are extracted and merged with the user's original query and system instructions into an enriched context prompt.
- **Generation:** The augmented prompt is sent to an LLM endpoint (such as OpenAI GPT, Claude Sonnet, Google Gemini, or open-source alternatives), which synthesizes an accurate, context-aware response for the user.

## The AI Application Stack for RAG Systems
A complete RAG architecture spans multiple functional layers, combining managed cloud services and open-source frameworks:

| Stack Layer | Architectural Role | Example Technologies |
| :--- | :--- | :--- |
| **Frontend Frameworks** | Delivers user interfaces and manages client-side interactions. | Next.js, Vue.js, SvelteKit, Streamlit |
| **Data Ingestion & Extraction** | Extracts text from unstructured sources, cleans data, and orchestrates ETL. | LlamaParse, Firecrawl, ScrapeGraph AI, Docking, Megaparser, Document AI, Apache Airflow, Kubeflow, Apache NiFi |
| **Embedding Models** | Converts natural language text and search queries into numerical vectors. | Amazon Titan, OpenAI, Cohere, JinaAI, Nomic, LLMWare, Cognita, Sentence Transformers |
| **Databases & Vector Storage** | Houses vectors and metadata; executes similarity lookups and hybrid search. | Weaviate, Milvus, Postgres (pgVector), Chroma, Pinecone, FAISS, OpenSearch Serverless, DynamoDB |
| **Retrieval & Ranking** | Refines raw vector retrieval through similarity algorithms and re-rankers. | Meta FAISS, ElasticSearch kNN, Haystack Retrievers, JinaAI Rerankers, Weaviate Hybrid Search |
| **Orchestration Frameworks** | Coordinates prompt chaining, model switching, memory, and data connectors. | LangChain, LlamaIndex, Haystack, Semantic Kernel, Ollama, Hugging Face, OpenRouter |
| **Large Language Models (LLMs)** | Synthesizes contextual data to produce the final natural language answer. | OpenAI GPT, Claude, Gemini, Llama, Mistral, DeepSeek, Qwen 2.5, Gemma, Phi-2 |

## Comparing RAG, Agentic RAG, and Fine-Tuning
Adapting language models to proprietary information requires selecting the appropriate pattern based on data volatility, workflow complexity, and operational overhead.

| Attribute | Traditional RAG | Agentic RAG | Model Fine-Tuning |
| :--- | :--- | :--- | :--- |
| **Knowledge Mechanism** | Runtime external retrieval via similarity search. | Autonomous tool execution, multi-agent coordination, and runtime retrieval. | Offline parameter updating using domain-specific training sets. |
| **Information Freshness** | High; immediately reflects updates to indexed sources. | High; can query live vector stores, APIs, and external tools dynamically. | Static; locked to the date and content of the training dataset. |
| **Workflow Logic** | Linear pipeline (embed query -> retrieve chunks -> generate answer). | Iterative and dynamic (agent decides retrieval strategy and refines queries). | Single-shot model inference without retrieval steps. |
| **Execution Tooling** | Vector database similarity search. | Model Context Protocol (MCP) servers, vector search, multi-agent systems, memory. | Compute-heavy training clusters and model registry pipelines. |
| **Adaptability** | Rigid; static queries against pre-indexed content. | High; adapts query strategies and resolves multi-step questions. | Low at runtime; requires full re-training cycles to alter facts. |

### Agentic RAG Mechanics
Traditional RAG relies on a single retrieval pass against a static database, making it brittle when queries require cross-referencing multiple domains or adjusting strategies mid-flight. Agentic RAG addresses this by routing the prompt to an AI agent. The agent uses short-term and long-term memory to maintain context across steps, devises an adaptive retrieval plan, invokes specialized tools (such as vector search, secondary agents, or MCP servers), and refines queries iteratively before passing the final contextualized prompt to the LLM.

### RAG versus Fine-Tuning
Fine-tuning adjusts internal neural network weights offline. While it excels at teaching models specific stylistic nuances, terminology, or deterministic task formatting, it is unsuited for rapidly evolving knowledge bases due to retraining costs and lack of provenance. RAG maintains live external links to documents, APIs, and databases, ensuring up-to-the-minute freshness and verifiable citations.

## Common mistakes
- **Using traditional RAG for complex, multi-step queries:** Deploying a simple, single-pass retrieval pipeline when questions require iterative investigation or multi-source synthesis leads to incomplete answers; dynamic tasks require Agentic RAG with memory and tool routing.
- **Attempting to keep knowledge fresh via fine-tuning:** Relying on weight adjustments rather than runtime retrieval for frequently modified documentation results in stale information, hallucinations, and recurring retraining costs.
- **Skipping specialized document extraction tools during ingestion:** Passing complex, unstructured sources like PDFs or web pages directly into chunkers without dedicated parsers (such as LlamaParse, Firecrawl, or Document AI) introduces noisy artifacts that degrade vector retrieval quality.
- **Relying solely on naive vector similarity without re-ranking:** Using raw vector distance without incorporating hybrid search (combining keyword and semantic search) or dedicated ranking layers (such as JinaAI Rerankers) frequently injects irrelevant context into the prompt.
- **Tightly coupling orchestration code to a single model provider:** Hardcoding pipeline logic directly to a single LLM vendor rather than abstracting orchestration through frameworks (like LangChain, LlamaIndex, or Haystack) prevents seamless model switching between proprietary APIs and open-source models.

---
*Source: Summary in our own words of 6 articles from the ByteByteGo "2025 Archive" (system design newsletter collection). No text copied.*
