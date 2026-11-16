---
id: software/system-design/bytebytego-archive-2025/llm-fundamentals-transformers
canonical_question: How do modern large language models work across their architecture, training pipelines, adaptation methods, and deployment stacks?
aliases:
- how transformer architecture works
- modern large language model design
- full fine-tuning vs lora vs rag
- mixture of experts llm architecture
- deepseek r1 grok 3 gpt oss comparison
- tokenization and attention in llms
entity_type: book_chapter
domain: software > system-design > bytebytego-archive-2025
last_verified: '2026-11-16'
source_type: summary
source: Summary in our own words of 16 articles from the ByteByteGo "2025 Archive" (system design newsletter collection). No text copied.
---

# Architecture, Training, and Adaptation of Modern Large Language Models

## TL;DR
Modern large language models rely on the Transformer architecture, which converts text into subword numerical vectors, applies self-attention to identify cross-token relationships, and generates output probabilistically. High-end implementations optimize compute via Mixture-of-Experts routing, reinforcement learning methods like Group Relative Policy Optimization, and multi-modal context compression. Once pretrained, systems are adapted to production tasks through specialized strategies balancing parameter updates against dynamic external retrieval.

## The AI Hierarchy: From Core ML to Generative AI
Artificial intelligence encompasses any system designed to simulate human intellectual tasks such as reasoning, learning, and sensory perception. Within this broad domain, machine learning focuses specifically on algorithms that improve performance through exposure to data rather than explicit rule programming. 

```
Artificial Intelligence (AI)
└── Machine Learning (ML)
    └── Deep Learning (DL)
        └── Generative AI (GenAI / Transformers)
```

Deep learning advances machine learning by using multi-layered artificial neural networks capable of automatically learning hierarchical feature representations from raw input. Generative AI builds on deep learning using transformer-based models to produce novel text, images, audio, and code mimicking their underlying training distributions.

## Anatomy of the Transformer Architecture
The Transformer is the core foundation for prominent models including GPT, Claude, Gemini, DeepSeek, and Llama. A standard transformer consists of an encoder that ingests input data and a decoder that generates responses.

```
Input Text ──> Preprocessing ──> Subword Tokenizer (BPE) ──> Token IDs ──> Vector Embeddings
                                                                              │
                                                                   + Positional Encoding
                                                                              │
                                                                              ▼
                                                                  Multi-Head Attention
                                                                              │
                                                                       Add & Normalize
                                                                              │
                                                                              ▼
                                                                     Feed-Forward Network
                                                                              │
                                                                       Add & Normalize
                                                                              │
                                                                              ▼
                                                             Decoder / Output Probabilities
```

### 1. Ingestion and Tokenization
Raw text undergoes standardization (normalizing Unicode and spacing) before splitting:
- **Character-based:** Splits text into single characters. While simple, it generates excessively long sequences and high computational overhead.
- **Word-based:** Splits on entire words, causing massive dictionary sizes and failures when encountering unknown vocabulary.
- **Subword-based:** Modern standard (such as Byte-Pair Encoding or BPE). Breaks common sequences into fragments (e.g., decomposing complex terms into known subwords), maintaining a balanced vocabulary size with flexible coverage across text, code, and symbols.

### 2. Embeddings and Positional Encoding
Tokens are assigned numerical IDs and converted into dense multidimensional vectors via embedding tables. Because transformers process all tokens simultaneously rather than sequentially, positional encodings are added directly to the embeddings to preserve word order (e.g., distinguishing "the cat ate the fish" from "the fish ate the cat").

### 3. Attention and Feed-Forward Layers
- **Multi-Head Attention:** Calculates mathematical alignment scores between tokens across the entire sequence simultaneously, determining contextual relevance.
- **Add & Normalize:** Residual connections add input data back to attention outputs, followed by layer normalization to stabilize gradient propagation.
- **Feed-Forward Networks:** Applies non-linear mathematical transformations to enrich token representations.
- **Masked Multi-Head Attention (Decoder):** Masks subsequent positions in the sequence to ensure the model only relies on prior tokens during autoregressive generation.
- **Linear Layer and Softmax:** The final internal representations map to vocabulary-wide prediction scores (logits). The Softmax function converts these scores into normalized probabilities to select the next token.

## Adapting Models: Full Fine-Tuning vs. LoRA vs. RAG
Adapting a pretrained model to specialized domains involves clear trade-offs between computational overhead, persistence, and implementation complexity.

| Dimension | Full Fine-Tuning | LoRA (Low-Rank Adaptation) | RAG (Retrieval-Augmented Generation) |
| :--- | :--- | :--- | :--- |
| **Weights Modified** | 100% of network parameters | Only small adapter layers; base weights frozen | 0% (base model remains unchanged) |
| **Compute Overhead** | Extremely high; requires full training clusters | Low to moderate; accessible on single/few GPUs | Low training compute; bounded inference retrieval |
| **Storage Cost** | Heavy (saves an entire model copy per task) | Lightweight (saves only small adapter checkpoints) | Standard database and vector index storage |
| **Knowledge Dynamic** | Static until next retrain; risk of hallucination | Static until next retrain; risk of hallucination | Dynamic; retrieves real-time facts directly |
| **Primary Use Case** | Broad behavioral shifts or baseline domain training | Task-specific adaptation and custom styling | Factual document search, knowledge bases, live data |

## Architectural Innovations in Modern Systems
Recent models apply specialized architectural patterns to overcome computational bottlenecks and context window constraints:

```
                      ┌────────────────────────────────────────┐
                      │              Input Query               │
                      └──────────────────┬─────────────────────┘
                                         │
                    ┌────────────────────┴────────────────────┐
                    ▼                                         ▼
      Standard Dense Execution                   Mixture-of-Experts (MoE) Routing
   (All parameters fire per token)           (Router selects top experts per token)
                    │                                         │
                    │                    ┌────────────────────┼────────────────────┐
                    │                    ▼                    ▼                    ▼
                    │                Expert 1             Expert 2             Expert N
                    │               (Activated)          (Activated)          (Inactive)
                    │                    └────────────────────┬────────────────────┘
                    │                                         │
                    └────────────────────┬────────────────────┘
                                         ▼
                                Generated Response
```

### 1. Mixture-of-Experts (MoE) Routing
Instead of executing every parameter for each token, MoE architectures utilize a routing gate to selectively activate specialized sub-networks (experts):
- **DeepSeek-R1:** Uses a 671-billion parameter total MoE structure, activating only 37 billion parameters per task. Trained on 14.8 trillion tokens across 52 languages using 2,000 Nvidia GPUs (compared to roughly 25,000 GPUs over 90–100 days for GPT-4), completing its final training run for approximately $6 million under an MIT license.
- **OpenAI GPT-OSS (20B and 120B):** Released under an Apache 2.0 license using Byte-Pair Encoding. The 20B variant features 24 transformer layers, while the 120B variant features 36 layers. Both models route each token to the 2 best experts out of a total pool of up to 64 experts.

### 2. Reinforcement Learning Over Supervised Fine-Tuning
While standard training pipelines rely on supervised fine-tuning (SFT) over annotated datasets, DeepSeek-R1 implements Group Relative Policy Optimization (GRPO). GRPO scores multiple generated responses within the same context to optimize reasoning efficiency without requiring standard critic models. Similarly, xAI's Grok-3 (trained on the Colossus supercomputer using 100,000 Nvidia H100 GPUs across 200 million GPU hours) introduces distinct operational states: "Think Mode" to break complex problems into sequential steps, and "Big Brain Mode" for compute-intensive analytical simulations.

### 3. Context Window Compression via Vision
To circumvent the quadratic attention overhead associated with long document context windows, DeepSeek-OCR converts lengthy textual passages into visual representations. A visual encoder compresses the rendered page into a compact series of vision tokens, which are subsequently decoded by an MoE language model, bypassing token limits while retaining structural layouts and tables.

## The Generative AI Infrastructure Stack
Operating generative AI in production requires a multi-layer ecosystem:
1. **Cloud & Compute Infrastructure:** Scalable hardware platforms (Nvidia, AWS, GCP, Azure).
2. **Foundational Models:** Dense and MoE baselines (GPT, Claude, Gemini, Llama, Mistral, DeepSeek).
3. **Application Frameworks:** Orchestration and model integration tools (LangChain, PyTorch, Hugging Face).
4. **Data Management:** Vector databases (Pinecone, Weaviate) and embedding providers (Cohere, JinaAI, Nomic).
5. **Synthetic Data & Fine-Tuning:** Optimization tracking (Weights & Biases, OctoML) and synthetic training pipelines (Gretel, Tonic AI).
6. **Supervision & Safety:** Operational monitoring (WhyLabs, Helicone, Fiddler) paired with security guardrails (LLM Guard, Arthur AI, Garak).

## Common mistakes
- **Defaulting to Full Fine-Tuning for Factual Updates:** Updating base weights to inject dynamic knowledge is computationally wasteful and fails to stop hallucinations. Teams should use RAG for real-time external data and reserve fine-tuning for modifying output structure or tone.
- **Using Word-Level or Character-Level Tokenization:** Word-level tokenization creates unmanageably large vocabularies that crash on novel terms, while character-level tokenization inflates sequence lengths and attention computation. Modern systems should always rely on subword schemes like BPE.
- **Running Dense Activations on Massive Parameter Sets:** Running every layer parameter on every token limits inference throughput. Deploying MoE routing ensures high parameter capacity while constraining execution costs to active experts.
- **Processing Massive Text Inputs Uncompressed:** Passing raw long-form text directly into standard attention layers triggers rapid memory and compute exhaustion. High-volume ingestion pipelines should adopt context compression techniques, such as visual tokenization or retrieval filtering.

---
*Source: Summary in our own words of 16 articles from the ByteByteGo "2025 Archive" (system design newsletter collection). No text copied.*
