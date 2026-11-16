---
id: software/system-design/book-60-days/api-evolution-and-decoupling
canonical_question: How do you safely scale and evolve production systems across API routing, database migrations, pagination, and transport protocols without downtime?
aliases:
- system design production evolution
- zero downtime schema migration postgres
- cursor pagination over large datasets
- api gateway vs bff mobile decoupling
- strangler fig pattern monolith migration
- http3 edge vs http2 origin cdn
- api versioning strategies and tradeoffs
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: '2026-11-16'
source_type: summary
source: Summary in our own words of scenario days 01, 24, 36, 47, 52, 53 from "60 Days of System Design Questions" (Joud Awad), a scenario workbook. No text copied.
---

# Architecture Patterns for Production Scaling and Zero-Downtime Evolution

## TL;DR
Decouple client transport from backend topologies using edge gateways and incremental proxies like the Strangler Fig. For data access at massive scale, exchange arbitrary page jumping for index-anchored cursor pagination, and replace blocking schema changes with expand-and-contract migrations. Concentrate protocol shifts where physical links degrade—deploying HTTP/3 over QUIC on lossy last-mile client networks while preserving stable HTTP/2 inside the datacenter.

## Decoupling Mobile Clients from Backend Services
Direct client-to-service communication forces client teams to repeatedly configure domains, authentication flows, and error contracts whenever new backend components launch.

An API Gateway provides a single, unified entry point that terminates incoming requests under a single domain and routes traffic to backend targets. It centralizes cross-cutting concerns—such as authentication, authorization, rate limiting, request logging, and TLS termination—behind consistent URL paths. When new services launch, backend teams update gateway routing tables with zero client-side code alterations.

Alternative strategies fail to address transport coupling:
- **Backend for Frontend (BFF):** Tailors data schemas and aggregates payloads specifically for distinct client categories (such as mobile versus web). It adds a dedicated service layer to build and maintain rather than solving raw domain sprawl.
- **Load Balancer:** Distributes identical traffic across uniform instances of the same service at Layer 4 or basic Layer 7; it lacks application-level path routing between distinct domains.
- **GraphQL Federation:** Unifies schemas at the query layer. It requires writing subgraphs across backend services and still demands a gateway in front, turning a swift transport fix into an extended migration.

| Approach | Primary Focus | Client Code Changes | Operational Overhead |
| :--- | :--- | :--- | :--- |
| **API Gateway** | Transport decoupling & route centralization | None | Low (routing rules) |
| **BFF** | Client-tailored payload reshaping | High (endpoint redirection) | High (extra application tier) |
| **Load Balancer** | Traffic balancing among identical nodes | None (incapable of domain routing) | Low (wrong layer) |
| **GraphQL Federation**| Unified data graph across services | Complete rewrite to GraphQL | Very high (subgraph implementation) |

## Efficient Pagination Over Massive Datasets
Offset pagination on large datasets forces databases to scan and discard millions of rows, degrading query latency as offsets grow deep.

Cursor pagination encodes the last seen sort keys (such as timestamp and unique identifier) into an opaque token. The subsequent request decodes this anchor to query strictly newer records using index seek conditions. This eliminates row discards, stabilizes query latency well within sub-200ms SLAs regardless of dataset depth, handles concurrent inserts without page drift, and respects filtering criteria. It trades away arbitrary page jumping for sequential next-and-previous navigation, aligning with typical administrative and feed workflows.

Other pagination approaches fall short at scale:
- **Keyset Pagination:** Uses explicit tuple comparisons directly in SQL queries. In PostgreSQL, multi-column equality filters like status combined with row comparisons frequently confuse the query planner, degrading into partial index scans.
- **Deferred Joins:** Retrieve only primary keys using offset limits within an inner query before joining the full table. While reducing memory pressure, the inner scan remains $O(\text{offset})$ and degrades at high page depths.
- **Covering Indexes:** Reduce heap lookups by storing indexed query columns together. However, an index cannot alter the algorithmic overhead of offset scanning and row discarding.

| Pagination Method | Algorithmic Complexity | Deep Page Latency | Jump-to-Page Support |
| :--- | :--- | :--- | :--- |
| **Cursor Pagination** | $O(1)$ index seek | Stable (<200ms) | No (sequential only) |
| **Keyset Pagination** | $O(1)$ seek (breaks on tuple filters) | Variable | No (sequential only) |
| **Deferred Join** | $O(\text{offset})$ index scan + $O(\text{limit})$ join | Moderate degradation | Yes |
| **Covering Index** | $O(\text{offset})$ index scan | High degradation | Yes |

## Edge Transport Optimization: HTTP/3 vs. HTTP/2
Packet loss over mobile networks introduces head-of-line blocking under TCP, driving p99 tail latencies above acceptable thresholds.

Deploying HTTP/3 from clients to CDN edge nodes combined with HTTP/2 from edge nodes to backend origins isolates transport risks. HTTP/3 runs on QUIC (UDP), ensuring individual packet loss on one stream does not pause unrelated streams multiplexed on the same connection. Paired with 0-RTT handshakes, client reconnects bypass connection negotiation overhead. In contrast, the internal datacenter leg operates over stable, low-loss infrastructure where HTTP/2 multiplexing excels without the cryptographic CPU penalties or enterprise firewall UDP port 443 throttling that can impact QUIC.

Less nuanced deployments create operational pitfalls:
- **HTTP/2 End-to-End:** Leaves the mobile last mile vulnerable to TCP-level head-of-line stalls whenever packets drop during network transitions.
- **HTTP/3 End-to-End:** Introduces operational risk to origin infrastructure, where corporate firewalls and cloud load balancers may block or rate-limit UDP 443, adding unnecessary encryption overhead to reliable private networks.
- **HTTP/2 Only:** Leaves the core mobile latency bottleneck unmitigated.

| Deployment Strategy | Client-to-Edge | Edge-to-Origin | Packet Loss Resilience | Datacenter Complexity |
| :--- | :--- | :--- | :--- | :--- |
| **Split Edge H3 / Origin H2** | HTTP/3 (QUIC/UDP) | HTTP/2 (TCP) | High (independent streams) | Low (standard TCP) |
| **End-to-End HTTP/2** | HTTP/2 (TCP) | HTTP/2 (TCP) | Low (TCP head-of-line stalls) | Low |
| **End-to-End HTTP/3** | HTTP/3 (QUIC/UDP) | HTTP/3 (QUIC/UDP) | High | High (UDP blocks, CPU costs) |

## API Versioning Strategies Under Breaking Changes
Altering response structures breaks uncoordinated API consumers unless transport visibility, caching rules, and client capabilities are carefully aligned.

Content negotiation using custom accept headers represents the formal specification standard by requesting resource representations rather than creating alternate network routes. However, URL path versioning acts as the prevailing operational standard. Explicit URL paths integrate automatically with CDNs, proxies, and log aggregators without custom instrumentation. While URL paths produce parallel route maintenance and require deliberate deprecation schedules, they eliminate the client failures common to header configurations.

Alternative versioning mechanics introduce operational friction:
- **Content Negotiation:** Client libraries handle accept headers inconsistently, proxies occasionally strip custom values, and misconfigurations trigger unhelpful 406 Not Acceptable status codes.
- **Header Versioning:** Keeps URLs clean, but version values are absent from standard browser navigation and raw access logs. When clients fail to transmit the header, servers defaulting to the latest version cause unexpected breakages.
- **Query Parameter Versioning:** Quick to stand up, but separates CDN caching keys per query variant and leads to untracked version sprawl across sprawling fleets.

| Versioning Strategy | Routing Visibility | Edge Caching Compatibility | Primary Tradeoff |
| :--- | :--- | :--- | :--- |
| **URL Path** (`/v1`) | Obvious in all logs and proxies | Native (path-based caching) | Parallel route maintenance |
| **Content Negotiation** | Hidden inside request headers | Requires `Vary: Accept` handling | Inconsistent client libraries |
| **Header Versioning** | Hidden unless instrumented | Requires custom cache key headers | Silent default-to-latest breakages |
| **Query Parameters** | Visible in URLs | Poor (fragments cache keys) | Uncontrolled version sprawl |

## Incrementally Strangling Monolithic Architectures
Extracting high-load components from legacy monoliths without halting parallel product development requires continuous, low-risk traffic diversion.

The Strangler Fig pattern places an edge proxy or facade directly in front of the application architecture. Incoming requests for the extracted domain route to the new microservice, while all remaining endpoints continue to hit the monolith. This architecture supports incremental, route-by-route migrations that run concurrently in production. Each change remains individually reversible, and monolithic code is retired only after the extracted service proves stability under production load.

Direct or monolithic alternatives invite delivery failures:
- **Branch by Abstraction:** Encapsulates code behind internal interfaces and feature flags within a shared codebase. It serves as an internal refactoring technique rather than an independent service deployment strategy.
- **Big Bang Rewrite:** Attempting to freeze code while rewriting a system from scratch leads to diverging requirements, delayed releases, lost edge-case bug fixes, and unvalidated cutover risks.
- **Database-First Migration:** Isolating storage schemas before extracting business logic breaks monolithic ORM relationships immediately, causing distributed transaction failures before distributed operational tooling is established.

| Strategy | Ongoing Feature Impact | Rollback Capability | Core Operational Risk |
| :--- | :--- | :--- | :--- |
| **Strangler Fig** | None (routes evolve concurrently) | Granular per endpoint | Routing proxy misconfiguration |
| **Branch by Abstraction**| None | Toggle via feature flag | Monolith deployment lockstep |
| **Big Bang Rewrite** | High (demands feature freezes) | All-or-nothing event | Specification divergence |
| **Database-First** | High (breaks existing ORMs) | High complexity | Premature distributed data split |

## Zero-Downtime Database Schema Migrations
Executing structural alterations on massive, high-write database tables can trigger exclusive table locks that stall active services and crash applications.

The Expand and Contract pattern safely executes schema changes across non-breaking phases:
1. **Expand:** Add target fields as nullable columns without defaults. In systems like PostgreSQL, this executes as an instantaneous metadata-only catalog update that avoids table locks.
2. **Backfill:** Populate legacy data into new columns asynchronously using rate-limited, small batches to prevent row-lock escalation.
3. **Dual-Write:** Update application services to write concurrently to both old and new columns while reading from the old columns.
4. **Contract:** Switch application reads to the new columns, verify complete system migration, remove dual-writing code, and safely drop the deprecated column.

Shortcut techniques frequently cause downtime:
- **Direct Table Alterations:** Executing `ALTER TABLE` to drop and add columns in an active table acquires an exclusive lock. On large tables, this lock blocks concurrent reads and writes, backing up connection pools and causing timeouts regardless of maintenance windows.
- **Shadow Tables (v2):** Rebuilding data into a second table and dual-writing across both solves deep structural redesigns (such as primary key shifts), but adds unnecessary application overhead for simple column splits.
- **Database Views:** Creating write-through views that alias legacy columns temporarily defers application updates, but does not execute the required underlying data migration.

| Migration Technique | Table Lock Footprint | Rollback Support | Implementation Complexity |
| :--- | :--- | :--- | :--- |
| **Expand and Contract** | Metadata-only (instantaneous) | Safe at every milestone | Moderate (phased rollouts) |
| **Direct Alteration** | Exclusive table lock (blocks I/O) | High risk (all-or-nothing) | Low |
| **Shadow Table (v2)** | Metadata-only | High complexity | Very high (overkill for column splits) |
| **Database View** | Low | High | Merely postpones migration |

## Decision cheatsheet

| Operational Symptom | Root Architectural Cause | Recommended Pattern | Antipattern to Avoid |
| :--- | :--- | :--- | :--- |
| Client configurations break on every newly launched microservice | Direct client-to-service transport coupling | **API Gateway** | Exposing internal service domains directly or introducing an unneeded BFF |
| Deep query latencies reach seconds on 50M-row tables | Offset discards scanned rows sequentially | **Cursor Pagination** (encoded token) | Offset queries, multi-column raw keyset tuples, or deferred joins |
| Tail latencies climb over mobile network transitions | TCP head-of-line blocking under packet loss | **HTTP/3 Edge with HTTP/2 Origin** | Running HTTP/2 end-to-end or forcing HTTP/3 inside the datacenter |
| Breaking API updates crash third-party client integrations | Inconsistent versioning formats and visibility | **URL Path Versioning** | Silent defaults on missing headers or fragmented query parameters |
| Monolith deployments bottleneck around an isolated feature | Monolithic code coupling prevents independent releases | **Strangler Fig Pattern** | Big-bang application rewrites or splitting database schemas first |
| Schema alterations trigger connection pool exhaustion | Exclusive locks hold against high-write tables | **Expand and Contract** | Direct `ALTER TABLE` column operations during maintenance windows |

---
*Source: Summary in our own words of scenario days 01, 24, 36, 47, 52, 53 from "60 Days of System Design Questions" (Joud Awad), a scenario workbook. No text copied.*
