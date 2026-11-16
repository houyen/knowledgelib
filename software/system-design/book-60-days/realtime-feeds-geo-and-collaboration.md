---
id: software/system-design/book-60-days/realtime-feeds-geo-and-collaboration
canonical_question: How should distributed systems handle high-throughput fanout, real-time geospatial proximity searches, and concurrent multi-writer synchronization without data loss?
aliases:
- celebrity feed fanout architecture
- real-time geospatial proximity at scale
- h3 vs geohash vs postgis
- crdt vs operational transformation vs vector clocks
- offline sync conflict resolution strategies
- distributed multi-writer conflict handling
- push vs pull hybrid feed architecture
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: '2026-11-16'
source_type: summary
source: Summary in our own words of scenario days 23, 35, 37, 44 from "60 Days of System Design Questions" (Joud Awad), a scenario workbook. No text copied.
---

# Scaling Distributed State: Fanout, Geospatial Indexing, and Concurrent Sync

## TL;DR

Scale dictates data placement: push paths fail under high fanout, spatial trees fail under write-heavy telemetry, and uncoordinated writes fail under network partitions. Isolate asymmetric publishers behind hybrid push-pull boundaries, map dynamic spatial coordinates onto discrete hexagonal partitions rather than continuous spatial indexes, and use Conflict-Free Replicated Data Types (CRDTs) to guarantee convergent state without centralized locks or silent overwrite penalties.

## Celebrity Feed Fanout: Balancing Push and Pull

One high-follower account can compromise an entire push-based distribution model by amplifying writes beyond cluster capacity.

### Recommended Pattern: Hybrid Fanout

Fan out writes to local caches only for accounts with standard follower counts (e.g., under 10,000 followers), while switching to fanout-on-read for accounts above that threshold. When a user requests their timeline:
1. Fetch the precomputed feed cache (in-memory storage like Redis) containing aggregated posts from standard accounts.
2. Query the recent posts of followed high-follower accounts directly.
3. Merge and deduplicate the two sorted streams in application memory.

Because high-follower accounts represent a bounded subset of any user's follow list, the real-time merge overhead remains low and predictable, avoiding multi-second tail latency spikes while eliminating massive write amplification.

### Traps and Failure Modes

*   **Fanout-on-Write (Push Everywhere):** Writing each post directly to every follower's timeline cache delivers low read latency until an account with 2,000,000 followers publishes. At an average write cost of 1ms per entry, this generates 2,000 seconds of cumulative write work, exhausting queue capacity, causing write replication lag, and triggering thundering herd problems across cache nodes.
*   **Fanout-on-Read (Pull Everywhere):** Forgoing precomputation requires querying the posts of all followed users at read time. If a user follows 500 accounts, the read path must execute 500 lookups (or a large relational join) and sort the results in memory. Caching this result provides minimal relief because timelines invalidate quickly, keeping read replica database utilization dangerously high.
*   **Materialized Feed Table via Event Streams:** Shifting denormalized feed updates to background consumers via Change Data Capture (CDC) or event brokers relieves the immediate synchronous HTTP handler. However, it merely defers identical write amplification to worker queues while adding distributed coordination, idempotency requirements, and reconciliation overhead.

### Architecture Comparison

| Model | Write Work (2M Followers) | Read Latency | Complexity | Bottleneck |
| :--- | :--- | :--- | :--- | :--- |
| **Pure Push (Write)** | 2,000,000 cache writes | Under 20ms | Low | Cache cluster bandwidth & queue saturation |
| **Pure Pull (Read)** | 1 database insert | 800ms – 4,000ms | Moderate | Read replica I/O and query merge cost |
| **Materialized Table** | 2,000,000 row inserts (async)| Under 50ms | High | Stream consumer lag and storage bloat |
| **Hybrid (Push/Pull)** | Bounded writes (<10k per post)| Under 50ms | Moderate | In-memory merge logic at read time |

## High-Throughput Geospatial Queries: Driver Proximity

Continuous coordinate broadcasts from hundreds of thousands of moving entities overwhelm traditional spatial indexes that prioritize read complexity over update frequency.

### Recommended Pattern: Discrete Hexagonal Grid (H3)

Map coordinates onto discrete spatial cells using a hierarchical hexagonal indexing system (such as Uber's H3) stored in in-memory sets (e.g., Redis). 
1. Quantize each driver's latitude and longitude into an H3 cell index at a fixed resolution.
2. Store driver identifiers in an in-memory set keyed by cell ID, updating the membership on each GPS ping.
3. Query nearby entities by computing the target coordinate's cell along with its immediate neighbors (a $k$-ring query of 1 center cell plus 6 surrounding cells) and retrieving IDs from the corresponding sets.

Hexagons possess a critical geometric property: all 6 adjacent neighbors share identical centroid distances. Unlike square-based grids where diagonal neighbors are approximately 41% further than orthogonal ones, hexagonal grids eliminate directional distortion and simplify radius-bounded searches to sub-10ms lookups.

### Traps and Failure Modes

*   **Relational Bounding Boxes (`BETWEEN lat/lng`):** Running range scans across latitude and longitude fields forces relational databases into full table scans or two-dimensional composite index traversals that collapse past 1,000 concurrent entities.
*   **PostGIS with Spatial Indexes (GiST / R-Tree):** R-Tree variants are optimized for complex spatial geometries and bounded analytical queries. When 500,000 drivers publish locations every 5 seconds, the engine must process 100,000 updates per second. GiST index rebalancing dominates server CPU and disk write bandwidth, preventing horizontal scale-out.
*   **Geohash Partitioning:** Geohashes interleave coordinate bits onto a Z-order space-filling curve. This curve contains severe discontinuities: two physical locations separated by a single meter can produce distinct string prefixes if they sit across a quadrant boundary. String prefix lookups frequently omit proximate entities unless complex, multi-edge expansion logic is implemented.
*   **In-Memory Quadtrees:** Dynamic quadtrees continuously rebalance, delete, and re-insert nodes as entities cross bounding boxes. Under high update volumes in densely populated urban centers, quadtrees develop deep, asymmetric branches that degrade traversal speeds and induce high lock contention.

### Geospatial Index Comparison

| Indexing Strategy | Boundary Uniformity | 100k Writes/sec Capability | Read Mechanism | Failure Mode Under High Concurrency |
| :--- | :--- | :--- | :--- | :--- |
| **PostGIS (GiST)** | High (exact geometry) | Fails (heavy index rebuilds) | Spatial index scan | Database write exhaustion |
| **Geohash** | Low (Z-curve edge gaps) | Moderate | String prefix scan | False negatives across cell borders |
| **Quadtree** | Moderate (rectangular) | Low (locking & rebalancing) | Tree traversal | Asymmetric branch contention |
| **H3 Hexagonal Grid** | High (6 equidistant edges) | High (O(1) memory set writes) | $k$-ring set union | Memory consumption of high-res sets |

## Multi-Writer Collaborative Editing: Resolving Concurrent Writes

Concurrent edits across distributed replicas cause irrecoverable data corruption when systems fail to preserve intent or lack commutative merge semantics.

### Recommended Pattern: Conflict-Free Replicated Data Types (CRDTs)

Implement state-based or operation-based CRDTs (such as RGA or YATA for sequences, and LWW-Element-Sets for key-value stores) where mutations are designed to be mathematically commutative, associative, and idempotent.
*   Assign globally unique identifiers to individual data entities (characters, blocks, or canvas shapes).
*   Structure updates so concurrent operations converge to an identical deterministic state across all replicas regardless of network delivery sequence or connection latency.
*   Eliminate centralized sequencing dependencies, allowing clients to apply changes optimistically to local memory while background transports sync state.

### Traps and Alternative Models

*   **Last-Write-Wins (LWW):** Resolves collisions by discarding mutations with older physical timestamps. Clocks across client devices drift, and concurrent operations at identical keys silently destroy data without notifying the author. Acceptable exclusively for append-only logs or transient telemetric gauges.
*   **Vector Clocks:** Accurately capture causal ordering ("happened-before" relationships) and identify concurrent updates. However, vector clocks only detect collisions; they do not resolve them. The application layer or end user must supply explicit merge code for every conceivable data permutation.
*   **Operational Transformation (OT):** Transforms positional indices of incoming operations against previously processed concurrent operations. While historically effective for centralized applications, OT requires a central sequencing authority to establish a total order of operations, and the complexity of transformation functions grows quadratically ($O(N^2)$) with each added mutation type.

### Concurrency Strategy Tradeoffs

| Mechanism | Coordination Model | Merge Complexity | Data Preservation | Distributed Suitability |
| :--- | :--- | :--- | :--- | :--- |
| **Last-Write-Wins** | None (timestamp order) | None (overwrite) | Zero (silent data loss) | High (coarse tracking only) |
| **Vector Clocks** | None (causal tracking) | High (delegated to user) | Full (surfaces branches)| High (detection only) |
| **Operational Transformation** | Central server required | High ($O(N^2)$ pairs) | High | Low (fails on P2P/decentralized) |
| **CRDTs** | None (mathematical merge) | Low (built into data type) | Full (deterministic) | High (local-first, peer-to-peer) |

## Offline-First Synchronization: Preventing Data Loss in Field Operations

Prolonged disconnections, intermittent networks, and diverged local schemas break naive offline sync engines that rely on monolithic API payloads or last-write heuristics.

### Recommended Pattern: Local CRDT Engine with Versioned Storage

Deploy a structured CRDT runtime (e.g., Automerge or Yjs) within client applications, backed by an indexed client database with strict schema migrations (e.g., IndexedDB via Dexie.js).
*   Record user changes as discrete operational changesets rather than entire record snapshots.
*   On reconnection, transmit compact operational diffs to the sync server.
*   Run deterministic CRDT merges on both client and server; operations commute freely even after hours of offline deviation, eliminating manual merge conflicts while preserving every edit.
*   Manage local schema migrations explicitly to avoid unhandled runtime failures when an offline client re-establishes communication against an upgraded server endpoint.

### Traps and Alternative Models

*   **Browser `localStorage` with JSON Diffs:** `localStorage` is restricted to approximately 5MB of synchronous storage, lacks indexing, and can be cleared unpredictably by browser routines. Manual JSON diff algorithms frequently fail on nested collections, field deletions, and concurrent array modifications.
*   **IndexedDB with Composite-Key Last-Write-Wins:** Pairing IndexedDB with schema migration libraries manages storage scale, but using timestamps (`updated_at` + `device_id`) still permanently discards real operational edits when offline workers sync after online peers have altered the same record.
*   **Vector Clocks with Interactive Merge UI:** Preserves all write paths and detects conflicts accurately. However, requiring manual human resolution across multiple operational fields introduces severe cognitive friction and operational delays, breaking automated field workflows.

## Decision Cheatsheet

| Symptom / Requirement | Anti-Pattern | Recommended Architecture | Implementation Core |
| :--- | :--- | :--- | :--- |
| **Asymmetric follower distribution causes read/write spikes** | Global Fanout-on-Write | Hybrid Fanout | Push for regular users; pull and merge for accounts above threshold |
| **High-frequency coordinate updates (100k+ writes/sec)** | R-Tree / PostGIS / Quadtree | Discrete Hexagonal Spatial Grid | H3 quantization + In-memory Set lookups ($k$-ring) |
| **Spatial proximity queries miss targets near borders** | Geohash string prefixing | Hexagonal Ring Indexing | H3 $k$-ring (equidistant center-to-edge radius coverage) |
| **Concurrent edits overwrite document modifications** | Last-Write-Wins (LWW) | Sequence / State CRDTs | Commutative operations (e.g., Yjs, Automerge, RGA) |
| **Real-time collaboration across distributed nodes** | Operational Transformation | Conflict-Free Replicated Data Types | Peer-to-peer deterministic operational convergence |
| **Long-duration offline field edits lose data upon sync** | Snapshot Overwrites / LWW | Operation-Based CRDT Sync | Client-side CRDT engine with migration-safe IndexedDB |
| **High conflict rate requires zero manual human intervention** | Vector Clocks + Merge Modals | CRDT Convergence | Mathematically defined conflict resolution rules |

---
*Source: Summary in our own words of scenario days 23, 35, 37, 44 from "60 Days of System Design Questions" (Joud Awad), a scenario workbook. No text copied.*
