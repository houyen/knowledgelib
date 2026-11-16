---
id: software/system-design/book-60-days/ai-agent-design
canonical_question: How should production AI agent systems be architected for workflow coordination, memory management, tool dispatch, multi-agent state, and observability?
aliases:
- production AI agent architecture
- agent orchestration patterns
- AI agent memory systems
- ReAct loop vs parallel tool calling
- multi-agent coordination models
- LLM agent observability and tracing
- DAG execution for agent workflows
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: '2026-11-16'
source_type: summary
source: Summary in our own words of scenario days 29, 42, 48, 55, 58 from "60 Days of System Design Questions" (Joud Awad), a scenario workbook. No text copied.
---

# Production AI Agent System Design

## TL;DR
Production agent pipelines fail when developers treat non-deterministic LLMs as self-coordinating services or bury complexity in prompts. Model multi-step dependencies explicitly as directed acyclic graphs (DAGs), retain state via rolling episodic summaries rather than raw token dumps, combine ReAct reasoning with parallel dispatch for tool execution, and anchor state in a centralized orchestrator. When systems degrade, span-level distributed tracing with token and payload attribution is the only reliable diagnostic tool.

---

## 1. Multi-Agent Workflow Coordination

**Problem:** A multi-role pipeline (planning, researching, implementing, reviewing) suffers from race conditions where dependent workers start prematurely, review cycles fail to loop back, and single-agent timeouts freeze the entire 40-second workflow without actionable error reporting.

### Recommended: Directed Acyclic Graph (DAG) Execution
Pipelines with strict execution dependencies (e.g., an implementation agent requiring inputs from both a planning agent and a context researcher) and iterative cycles (e.g., automated review pushing code back to implementation) should be designed as DAGs with cyclic loop capabilities. 

Engines such as LangGraph, Temporal, AWS Step Functions, Prefect, or Dagster manage dependencies declaratively. Execution of a downstream node halts until all designated upstream parents finish successfully. Furthermore, per-node timeout budgets isolate individual service lags, preventing pipeline hangs. Cyclic edges allow automated retries upon review failure, and native graph runners generate full execution traces for every run.

### Traps & Alternative Trade-offs
*   **Centralized Imperative Orchestrator:** Writing an imperative controller with database updates and sequential timeouts seems simple initially, but it defaults to synchronous execution. Supporting parallel branches (such as simultaneous planning and researching) requires hand-rolled barrier-synchronization logic that becomes brittle and difficult to maintain.
*   **Event-Bus Choreography:** While suitable for loosely coupled, fire-and-forget distributed systems, pub/sub architectures lack a native "join" barrier to hold an agent until multiple parallel predecessors publish their messages. Moving this synchronization into worker agents pollutes domain logic with coordination state.
*   **Supervisor Meta-Agent:** Introducing a master LLM to monitor and route work adds prompt latency, introduces single-point LLM failure risks, and merely hides an implicit graph inside an LLM's context window. Supervisors excel as human-escalation layers over a graph, but perform poorly as basic workflow plumbing.

| Coordination Model | Concurrency Handling | Error Isolation | Retries & Cycles | Operational Overhead |
| :--- | :--- | :--- | :--- | :--- |
| **DAG Engine (Recommended)** | Native join/fork barriers | Per-node timeout budgets | First-class graph edges | Low (framework native) |
| **Centralized Controller** | Requires manual threading/async | Manual timer logic | Hard-coded retry loops | Medium (boilerplate heavy) |
| **Event Choreography** | Poor (no multi-event barriers) | Decentralized error capture | Distributed event loops | High (scattered state) |
| **Supervisor Meta-Agent** | Inefficient (all hops via LLM) | Dependent on LLM judgment | Unpredictable rerouting | Very High (added cost/latency) |

---

## 2. Agent Memory Architecture

**Problem:** By the third step of a multi-stage request, an agent fed with raw chat logs consumes over 8,000 tokens of context, loses track of its current goal, and hallucinates as if beginning on turn one.

### Recommended: Episodic Memory with Summarization
Long-running agents require a tiered memory architecture:
1.  **Short-term buffer:** Retain the raw context of the last $N$ turns verbatim.
2.  **Episodic summarization:** Compress older turns into structured event summaries using a lightweight background pass.
3.  **Dynamic injection:** Inject only task-relevant episodic summaries and current state definitions alongside the short-term buffer on each turn.

This structure avoids context saturation, curtails token costs, and prevents the attention drift observed in Anthropic, OpenAI Assistants API, and LangChain Memory v2 designs.

### Traps & Alternative Trade-offs
*   **In-Context Window Only:** Packing full conversation history directly into the prompt breaks down around 15 turns or 8,000 tokens. The model suffers from the "lost-in-the-middle" effect, overlooking vital instructions placed in the middle of deep context, while token consumption grows quadratically.
*   **Pure Vector Store Retrieval:** Querying past interactions strictly by embedding similarity frequently fetches historical conversations matching keywords (e.g., past trips to the same city) rather than maintaining the procedural state of the active task. Vector stores serve semantic reference lookup, not sequential task tracking.
*   **Redis Key-Value State:** Redis provides deterministic speed, but forces the developer to design an intricate working-memory schema that the agent must explicitly decide to read and write via tool interactions, creating high overhead for dynamic conversations.

| Memory Strategy | Context Scalability | Procedural State Reliability | Implementation Complexity | Primary Failure Mode |
| :--- | :--- | :--- | :--- | :--- |
| **Episodic Summaries (Recommended)** | High (compressed history) | High (structured task events) | Medium | Summary information loss |
| **In-Context Full History** | Very Low (<15 turns) | Degrades over time | Minimal | Context saturation / Lost-in-middle |
| **Vector Store Top-K** | High (infinite turns) | Poor (confuses past vs. present) | Medium | Irrelevant historical retrieval |
| **Redis Key-Value** | High (offloaded memory) | High (strictly defined) | High | Schema brittleness / Tool misuse |

---

## 3. Tool Selection and Invocation Strategy

**Problem:** An agent equipped with over a dozen distinct tools must interpret ambiguous requests, sequence multi-stage actions, execute lookups efficiently, and terminate execution cleanly without looping.

### Recommended: ReAct Loop Augmented by Parallel Dispatch
Adopt a ReAct (Reason + Act) loop as the operational foundation. The model outputs a thought trace, fires an action, absorbs the resulting observation, and then decides its next step.

When multiple tools have zero data dependencies (e.g., retrieving user preferences and querying a calendar simultaneously), exploit native parallel tool calling (supported by GPT-4o and Claude 3.5 Sonnet) during the initial fan-out phase. Transition back to the step-by-step ReAct loop once intermediate outputs dictate subsequent calls.

### Traps & Alternative Trade-offs
*   **Strict Forced Function Schemas:** Enforcing rigid JSON output schemas on every turn disables free-form intermediate reasoning. Without a scratchpad to evaluate ambiguity, handle unexpected tool errors, or branch conditionally, decision quality drops sharply.
*   **Unconstrained Parallel Calling:** Emitting all planned calls concurrently fails whenever Tool B relies on outputs from Tool A. Running dependent tools in parallel results in malformed arguments, downstream failures, and hallucinated compensations.
*   **Planner-Executor Split:** Generating a static execution DAG upfront via a planner model before handing it to a blind executor functions well in high-complexity frameworks (e.g., Devin, AutoGPT). However, it introduces significant replanning latency whenever real-world API responses deviate from initial assumptions.

| Tool Dispatch Model | Reasoning Capability | Execution Latency | Resilience to API Surprises | Best Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **ReAct + Parallel (Recommended)** | High (evaluates observations) | Low on fan-out; Medium on sequential | High (adapts per turn) | General production workflows |
| **Pure ReAct** | High (thinks per step) | High (strict serial roundtrips) | High (adapts per turn) | Strictly dependent call chains |
| **Forced Function Schema** | Low (no intermediate reasoning) | Low | Low (fails on ambiguous edge cases) | Strict downstream API validation |
| **Planner-Executor Split** | High (global plan generation) | Lowest on execution; High on replan | Low without complex replan loops | Workflows with 10+ stable tools |

---

## 4. Parallel Multi-Agent Coordination and State

**Problem:** A multi-agent research pipeline spawning dynamic sub-agents must execute parallel tasks, update a common context layer, and aggregate outputs without deadlocks or state pollution.

### Recommended: Centralized Orchestrator
Maintain a single centralized controller managing stateless, task-focused worker agents. The orchestrator owns the canonical state log, task dispatch, timeout budgets, and final aggregation. 

Worker agents ingest input parameters, execute locally, and return responses without mutating global memory directly. Centralizing state mutation creates a deterministic audit trail that allows runs to be replayed, debugged, and checkpointed using systems like LangGraph or CrewAI.

### Traps & Alternative Trade-offs
*   **Decentralized Peer Handoff:** Allowing agents to invoke each other directly creates unmonitored execution loops (Agent A passing to Agent B, then to Agent C, and back to A) with no central circuit breaker or conflict resolution mechanism.
*   **Shared Blackboard / Message Queue:** Using a shared key-value store or queue without a controller provides a data-sharing medium, but fails to govern execution scheduling. Teams inevitably build an unobservable orchestrator through complex polling loops across agents.
*   **Hierarchical Nesting:** Nesting orchestrators within sub-orchestrators adds architectural overhead and recursion latency. Reserve this pattern exclusively for problems that decompose naturally into distinct, multi-layered sub-trees.

| Topology | State Management | Failure Debuggability | Looping / Deadlock Risk | Architecture Complexity |
| :--- | :--- | :--- | :--- | :--- |
| **Centralized Controller (Recommended)** | Single source of truth | High (replayable state logs) | Low (central circuit breaker) | Moderate |
| **Peer-to-Peer Handoff** | Fragmented across agents | Very Low (distributed hops) | High (infinite handoff loops) | Low initially, chaotic at scale |
| **Shared Blackboard** | Shared state, decoupled calls | Medium (state logs exist) | Moderate (state-race conditions) | Moderate (requires polling logic) |
| **Hierarchical Tree** | Scoped per sub-tree | Moderate (nested traces) | Low (bounded by parent tree) | High (deep recursion layers) |

---

## 5. Agent Pipeline Observability

**Problem:** Production agent requests fail silently with HTTP 200 statuses, daily token consumption triples unexpectedly, and single-span latencies stretch to 14 seconds without clear attribution in standard APM tools.

### Recommended: Span-Level Structured Tracing
LLM observability requires tracing that extends beyond standard HTTP request metrics. Instrument every transaction with hierarchical trace and span attributes via dedicated tooling (LangSmith, Helicone, Arize, Langfuse) or OpenTelemetry standards. Every nested span must capture:
*   Precise model identifiers and routing fallbacks.
*   Granular prompt and completion token counts.
*   Exact prompt inputs, raw responses, and tool call payloads.
*   Retrieval-augmented generation (RAG) metadata, including retrieved chunk IDs and scores.
*   Per-hop latency breakdowns.

This granularity instantly exposes systemic bugs—such as recursive loops burning token budgets, secondary fallback models causing latency spikes, or empty context chunks causing hallucinations.

### Traps & Alternative Trade-offs
*   **LLM-as-a-Judge Eval Suites:** Evals track aggregate historical performance across dataset samples. During an active production outage, broad quality scores cannot pinpoint why a specific user request degraded. Tracing provides the diagnostic bedrock upon which offline evals rely.
*   **High-Level Cost Dashboards:** Simple cost alerts notify teams that spend has accelerated, but offer zero context on which pipeline branch, user query pattern, or sub-agent triggered the expense.
*   **Proprietary In-House Logging:** Building custom infrastructure to trace asynchronous, multi-branch LLM execution trees requires rebuilding trace visualizers, context propagators, PII redactors, and token math from scratch, diverting focus from resolving runtime issues.

| Observability Method | Granular Root-Cause Identification | Production Incident Utility | Metric Depth | Implementation Overhead |
| :--- | :--- | :--- | :--- | :--- |
| **Span-Level LLM Traces (Recommended)** | Immediate (pinpoints bad tool/model hop) | High (essential for triage) | Tokens, latency, payloads, chunk IDs | Low (via OpenTelemetry / SaaS) |
| **LLM-as-a-Judge Evals** | Low (surfaces aggregate trends only) | Low during live fires | Quality, toxicity, drift metrics | High (eval prompt tuning) |
| **High-Level Cost Alerts** | None (indicates symptom, not cause) | Moderate (stops financial bleed) | Aggregated dollar spend | Minimal |
| **Custom Middleware Logging** | Variable (usually lacks graph visualization) | Low to Medium | Unstandardized flat logs | Very High (reinventing tracing) |

---

## Decision Cheatsheet

| Observed System Symptom | Root Architecture Flaw | Recommended Solution Pattern |
| :--- | :--- | :--- |
| Downstream agent runs with missing inputs; step timeouts hang entire pipeline | Sequential or uncoordinated pipeline execution | Migrate to a DAG workflow with explicit join edges and per-step deadlines |
| Pipeline produces bugs caught by review, but cannot loop back to fix them | Linear execution without conditional edges | Implement cyclic graph routing to return failure payloads to the worker |
| Agent forgets original constraints after 10–15 turns or burns tokens unnecessarily | Unbounded in-context history leading to attention loss | Implement episodic summarization combined with a short-term sliding turn window |
| Semantic search retrieves historical turns from past trips instead of current state | Using vector similarity search for procedural task memory | Use structured episodic summaries or state variables instead of pure embedding lookups |
| Tool invocation requires 4+ serial roundtrips for independent operations | Defaulting to purely serial ReAct processing | Utilize parallel tool dispatch for independent lookups; resume ReAct for sequential steps |
| Structured tool dispatch fails on ambiguous inputs or unexpected API errors | Constraining the model to rigid JSON output without a thought step | Restore a ReAct scratchpad so the model can reason before emitting calls |
| Multi-agent handoffs enter circular routing ping-pong loops | Decentralized peer-to-peer delegation without an arbitrator | Centralize dispatch and routing logic in a single orchestrator |
| HTTP 200 logs mask hallucinations, 3x cost surges, and 14s query spikes | Monolithic HTTP spans obscuring internal execution stages | Instrument span-level LLM tracing recording token counts, payloads, and per-hop latencies |

---
*Source: Summary in our own words of scenario days 29, 42, 48, 55, 58 from "60 Days of System Design Questions" (Joud Awad), a scenario workbook. No text copied.*
