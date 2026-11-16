---
id: software/system-design/bytebytego-archive-2025/ai-agents-mcp-a2a
canonical_question: How do AI agents operate, and how does the Model Context Protocol (MCP) enable their integration with external systems?
aliases:
- ai agent architecture
- model context protocol mcp
- mcp vs api
- mcp vs a2a protocol
- ai agent frameworks comparison
- types of ai agents
- open source ai agent tech stack
entity_type: book_chapter
domain: software > system-design > bytebytego-archive-2025
last_verified: '2026-11-16'
source_type: summary
source: Summary in our own words of 18 articles from the ByteByteGo "2025 Archive" (system design newsletter collection). No text copied.
---

# AI Agents and the Model Context Protocol (MCP): Architecture, Frameworks, and Integration

## TL;DR
AI agents combine foundational language models, iterative reasoning loops, memory, and external tooling to accomplish goals autonomously or with a human in the loop. The Model Context Protocol (MCP) establishes an open, self-describing client-server standard that connects these agents to disparate tools, filesystems, and databases without bespoke integration code. When scaling autonomous workflows, systems pair MCP for vertical resource access with orchestration frameworks (such as LangGraph or CrewAI) and inter-agent standards (such as Agent-to-Agent protocol) for horizontal collaboration.

## Core Architecture and Types of AI Agents
An AI agent is an autonomous software component that senses environmental context, maintains internal state, reasons through objectives, and invokes actions to produce changes. Rather than executing static single-prompt completions, agents employ iterative execution patterns such as ReAct (Reasoning and Acting) and Chain of Thought (CoT). In this cycle, the foundational model acts as the cognitive core: it evaluates an incoming goal, plans intermediate sub-tasks, dispatches actions via external tools, records observed outputs into short-term or long-term memory, and refines subsequent steps until the goal criteria are satisfied.

Agent systems fall into five distinct architectural tiers based on internal sophistication:

1. **Simple Reflex Agents**: Operate on rigid condition-action definitions without tracking historical context or internal states.
2. **Model-Based Reflex Agents**: Maintain an internal representation of environmental mechanics to handle partial observability beyond direct sensory input.
3. **Goal-Based Agents**: Evaluate potential sequences of actions specifically against defined completion targets.
4. **Utility-Based Agents**: Score competing pathways against trade-offs to select optimal outcomes rather than binary goal satisfaction.
5. **Learning Agents**: Use continuous performance feedback loops to adapt decision boundaries and operational behaviors over time.

Deployments range from single personal assistants to multi-agent swarms using agent debate, automated handoffs, or coordinated human-in-the-loop governance.

## The Agentic AI Technology Stack
Building autonomous systems requires a multi-layered software stack spanning foundational models down to data persistence layers:

- **Foundation Models**: The cognitive engines providing semantic reasoning, code synthesis, and planning. While proprietary models (such as GPT-4 and Claude) remain standard, open-weight alternatives (such as Llama, Mistral, Qwen, DeepSeek, Phi, and Gemma) run locally via runtimes like Ollama or Hugging Face.
- **Agent Frameworks**: Libraries managing pipelines, memory retention, and tool orchestration. Key frameworks include **LangChain** (structured sequential chaining and document ingestion), **AutoGen** (conversational workflows with code execution), **CrewAI** (role-based collaborative agent teams), **LlamaIndex** (document parsing and vector querying), and **Semantic Kernel** (plugin-centric enterprise orchestration).
- **Embeddings and Data Storage**: Retrieval-Augmented Generation (RAG) relies on embedding providers (Nomic, JinaAI, LLMAware) combined with vector databases and stores (PostgreSQL with PGVector, Milvus, Weaviate, Redis, and FAISS).
- **Execution & Serving**: Backend frameworks like FastAPI and Netflix Metaflow manage lifecycle execution, while Next.js and Streamlit handle user interfaces.

### Workflow Orchestration: Visual Builders vs. Programmatic Graphs
Workflow execution bifurcates into visual automation pipelines and programmatic state machines:

| Dimension | N8N | LangGraph |
| :--- | :--- | :--- |
| **Paradigm** | Node-based visual pipeline | Code-centric graph framework (Python) |
| **Execution Flow** | Linear, event-driven, decision branching | Cyclic state machine with looping and branching |
| **State Handling** | Local node outputs passed sequentially | Unified, shared mutable state across the entire graph |
| **Agent Support** | Tool invocation and memory nodes in a visual flow | Fine-grained multi-agent routing and conditional retries |
| **Primary Use Case** | Low-code automation connecting APIs with AI tasks | Complex, custom multi-agent logic requiring precise code control |

## Model Context Protocol (MCP) Architecture
Historically, connecting LLMs to external systems required writing bespoke API clients and supplying documentation within system prompts. Anthropic introduced the Model Context Protocol (MCP) as an open standard to establish universal interoperability between language models and tools.

MCP adopts a client-server architecture consisting of three entities:
1. **Host**: The surrounding execution runtime (such as Claude Desktop or an IDE) that manages user sessions and hosts the client.
2. **MCP Client**: The internal interface within the host that translates agent intents into standardized protocol messages.
3. **MCP Server**: A targeted adapter exposing the endpoints, schemas, and credentials of external services to the client.

```
+-------------------------------------------------------------+
| Host (IDE, Desktop Application, AI Runtime)                 |
|                                                             |
|   +-------------------+          +-----------------------+  |
|   | Foundation Model  |<-------->| MCP Client            |  |
|   +-------------------+          +-----------+-----------+  |
+----------------------------------------------|--------------+
                                               | (Standardized Protocol)
                 +-----------------------------+-----------------------------+
                 |                             |                             |
                 v                             v                             v
      +---------------------+       +---------------------+       +---------------------+
      | MCP Server: DB      |       | MCP Server: Files   |       | MCP Server: Dev     |
      | (PostgreSQL, Redis) |       | (Local, Drive)      |       | (GitHub, Docker)    |
      +---------------------+       +---------------------+       +---------------------+
```

### Protocol Primitives
MCP defines strict primitives divided across client and server roles:
- **Client Primitives**:
  - *Roots*: Boundary definitions that define secure file access boundaries for servers.
  - *Sampling*: An abstraction allowing the server to request model inferences via the client.
- **Server Primitives**:
  - *Tools*: Executable functions that the model can run with explicit side effects (e.g., executing a SQL query, triggering Docker commands).
  - *Resources*: Read-only contextual payloads, database schemas, or file contents that the client can reference.
  - *Prompts*: Parameterized prompt templates and guided instructions bundled by the server.

Standard MCP implementations support operations across enterprise tools, including local filesystems, GitHub, Slack, Docker, PostgreSQL, Google Drive, Notion, Stripe, Brave Search, and Perplexity.

## Protocol and Integration Comparisons

### Traditional APIs vs. Model Context Protocol
While APIs facilitate software-to-software exchange, MCP introduces an AI-native interface layer:

| Feature | Traditional API | Model Context Protocol (MCP) |
| :--- | :--- | :--- |
| **Design Target** | Deterministic software systems | LLMs, AI agents, and development environments |
| **Schema Discovery** | External human documentation (OpenAPI, Swagger) | Native self-describing protocol primitives |
| **Format Standardization**| Heterogeneous styles (REST, GraphQL, gRPC, SOAP) | Uniform protocol for tools, prompts, and resources |
| **Integration Overhead**| Custom glue code required for each endpoint | Single generic client connector per host environment |

### MCP vs. Agent-to-Agent (A2A) Protocol
Modern enterprise agent systems frequently combine MCP and Google's Agent-to-Agent (A2A) protocol in a complementary topology:

| Attribute | Model Context Protocol (MCP) | Agent-to-Agent (A2A) Protocol |
| :--- | :--- | :--- |
| **Primary Direction** | Vertical integration (Agent to Data/Tools) | Horizontal communication (Agent to Agent) |
| **Target Endpoints** | Databases, filesystems, APIs, infrastructure | Peer autonomous agents and reasoning engines |
| **Core Function** | Supplies situational data and executes commands | Coordinates sub-task delegation, negotiation, and handoffs |
| **System Analogy** | The peripheral bus (USB/PCIe) of the agent | The network protocol (TCP/HTTP) between autonomous agents |

In a combined topology, individual agents use MCP servers to pull local data or query external services, while simultaneously collaborating over A2A to partition tasks, exchange intermediate steps, and aggregate final results.

## Common Mistakes and Trade-offs
- **Conflating Agents with Protocols**: Treating MCP as an autonomous reasoning system rather than a transport and discovery layer. An MCP server provides context and tools; it does not reason, plan, or maintain goals on its own.
- **Over-Engineering Reflex Scenarios**: Implementing dynamic multi-agent loops or utility-based architectures for deterministic, rule-based operations where simple reflex agents or linear scripts are faster and less expensive.
- **Misapplying Visual Pipelines to State-Machine Logic**: Forcing cyclical reasoning, dynamic retries, or complex self-healing loops into rigid linear automation tools (like N8N) instead of using state-graph architectures (like LangGraph).
- **Ignoring Horizontal Coordination at Scale**: Relying solely on vertical tool integration (MCP) when building multi-agent architectures, resulting in duplicate data retrieval and uncoordinated execution rather than structured handoffs via inter-agent protocols (like A2A).

---
*Source: Summary in our own words of 18 articles from the ByteByteGo "2025 Archive" (system design newsletter collection). No text copied.*
