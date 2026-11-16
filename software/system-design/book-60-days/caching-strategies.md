---
id: software/system-design/book-60-days/caching-strategies
canonical_question: How should caching layers, invalidation workflows, and read replica consistency be designed to prevent stale data and system overload?
aliases:
- cache invalidation strategies and patterns
- preventing cache stampede thundering herd
- bloom filter vs redis set high cardinality
- transactional outbox cache consistency
- read after write consistency read replicas
- cdn cache purge automated deploy
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: '2026-11-16'
source_type: summary
source: Summary in our own words of scenario days 08, 15, 18, 19, 26, 43 from "60 Days of System Design Questions" (Joud Awad), a scenario workbook. No text copied.
---

# Distributed Caching, Invalidation, and Replication Consistency

## TL;DR
Decouple cache updates from primary write paths by treating databases as the sole authority and caches as disposable accelerators. Eliminate distributed race conditions and thundering herds through deterministic pre-warming, transactional outboxes, and probabilistic data structures rather than synchronous locking or manual intervention. When reads scale across asynchronous replicas, enforce consistency at the user session level rather than compromising global database throughput.

## Multi-Writer Product Catalogs: Cache-Aside vs. Inline Mutation
**Problem:** Multiple independent services (admin, inventory, orders) write directly to the database, causing cached catalog entries to serve stale pricing and inventory under heavy traffic.

**Recommended Approach:** Cache-aside (lazy loading). Mutating services execute updates against PostgreSQL, issue a key deletion (`DEL product:id`) in Redis, and terminate. Subsequent read operations encounter a cache miss, load authoritative data from the database, and asynchronously repopulate Redis. PostgreSQL remains the sole authority. If Redis experiences downtime, client queries route directly to the database with degraded latency but intact consistency.

**Why Alternatives Fail:**
- *Write-through:* Requires synchronous updates to both PostgreSQL and Redis. Because cross-engine distributed transactions do not exist here, a Redis timeout leaves PostgreSQL updated while Redis retains stale data. Furthermore, every independent writer must maintain Redis credentials and network connectivity, causing write availability to fail if Redis degrades.
- *Write-behind (write-back):* Buffers mutations in Redis before asynchronously flushing to PostgreSQL. An unexpected Redis failure, OOM termination, or replication lag destroys pending financial and inventory transactions permanently.
- *Read-through:* Automates read-side cache repopulation through an inline provider, but does not address write distribution across disjoint services. Writers still require out-of-band invalidation logic.

| Pattern | Write Path Behavior | Failure Mode | Suitability |
| :--- | :--- | :--- | :--- |
| **Cache-Aside** | Write DB, delete cache key | Cache miss forces DB read | Multi-writer transactional systems |
| **Write-Through** | Write DB + cache simultaneously | Network blips cause cache-DB split | Single dedicated writer services |
| **Write-Behind** | Write cache, async flush DB | Process crash causes data loss | Non-critical counters, logging |
| **Read-Through** | Bypasses write layer entirely | Does not invalidate stale multi-writer data | Pure read-heavy single-source caches |

## High-Volume Negative Existence Checks: Bloom Filters vs. In-Memory Sets
**Problem:** A recommendation engine with 50 million users and 80 billion tracking rows experiences severe P99 latency degradation (>600ms) due to cold relational point lookups checking if a user has seen a post.

**Recommended Approach:** Deploy a per-user Bloom filter within Redis, short-circuiting queries to PostgreSQL. Because roughly 97% of recommendation checks query items a user has never encountered, the filter definitively confirms non-existence in sub-millisecond time. Only a positive ("maybe seen") result triggers a confirmation lookup against PostgreSQL. Sizing the filter for 10,000 posts at a 1% false-positive rate requires roughly 12 KB per user (~600 GB total for 50M users), completely eliminating database thrashing while guaranteeing zero false negatives.

**Why Alternatives Fail:**
- *Redis SET per user:* High-activity accounts with 50,000+ views consume 3 to 4 MB per set. Storing this cardinality across the entire user base demands over 4 TB of RAM, driving unsustainable hosting costs or triggering random key evictions on active users.
- *Cassandra migration:* While Cassandra scales row writes, the underlying bottleneck is disk-bound point lookups across network boundaries under 120,000 RPS. Swapping primary storage introduces extensive infrastructure overhead without solving random read latency.
- *PostgreSQL read replicas with connection pooling:* Adding compute does not eliminate the physical I/O cost of index scans across an 80-billion-row footprint. Disk latency on cold reads continues to breach the 100ms threshold.

| Architecture | Storage Overhead (50M Users) | Accuracy Profile | Latency Impact |
| :--- | :--- | :--- | :--- |
| **Redis Bloom Filter** | ~600 GB total (~12 KB/user) | 1% false positive, 0% false negative | Sub-millisecond on 97% of requests |
| **Redis SET** | >4 TB total (linear per item) | 100% exact match | High RAM exhaustion risk |
| **Cassandra Cluster** | High disk storage footprint | 100% exact match | Network/disk bounds remain at high RPS |
| **PostgreSQL Replicas** | High disk/compute footprint | 100% exact match | B-tree disk lookups breach latency SLAs |

## Hot Key TTL Expiration: Deterministic Pre-Warming vs. Mutex Traps
**Problem:** A hot endpoint handling 8,000 RPS suffers a cache stampede whenever its 60-second TTL expires, drowning a database sized for 200 RPS.

**Recommended Approach:** Scheduled cache pre-warming combined with `stale-while-revalidate`. A background scheduler refreshes the cached record at fixed 45-second intervals, ensuring the TTL in production never counts down to zero. Serving the existing value during refresh ensures incoming spikes never stall on database responses.

**Why Alternatives Fail:**
- *Request coalescing:* Merges in-flight queries within an isolated application process. In an environment with 50 distributed Node.js containers, each instance coalesces independently, still allowing a 50x query burst onto the database upon expiry.
- *Distributed mutex locks:* Permitting a single request to query the database while thousands wait queues network sockets. If database latency stutters to 500ms under load, thread pools exhaust, request timeouts surge, and the application layer collapses.
- *Probabilistic early expiry (XFetch):* Jitter-based refreshes reduce the mathematical likelihood of expiration cliffs but lack deterministic guarantees. Unexpected traffic drops followed by sudden bursts still expose cold keys to traffic spikes.

| Mitigation Strategy | Concurrency Handling | Node Coordination | Primary Vulnerability |
| :--- | :--- | :--- | :--- |
| **Cache Pre-Warming** | Background refresh before expiry | None (centralized worker) | Minimal compute overhead for scheduled jobs |
| **Request Coalescing** | In-process deduplication | Requires distributed coordination | Scales poorly across multi-container tiers |
| **Mutex Locking** | Serialized DB execution | Shared Redis lock | Queued requests exhaust connection pools |
| **Probabilistic Expiry** | Asymmetric time-based trigger | None | Non-deterministic under sudden traffic spikes |

## Write Consistency Under Partial Failures: Transactional Outbox
**Problem:** In a service handling 600 read RPS and 80 write RPS, sporadic network timeouts between database updates and manual cache invalidation leave stale data visible for extended windows.

**Recommended Approach:** The Transactional Outbox pattern. The service writes the updated entity and an outbox event record within the same ACID database transaction. An asynchronous worker or change data capture (CDC) process consumes this table and issues cache evictions or updates in Redis. If Redis becomes temporarily unreachable, the outbox retains the events, allowing automated replay upon reconnection without leaving stale states.

**Why Alternatives Fail:**
- *Synchronous write-through:* Coupling the database and Redis in the write path forces user latency to absorb dual network round-trips. An outage in Redis halts all incoming writes.
- *Write-behind caching:* Accepting mutations into Redis first risks total data loss if the cache node crashes, runs out of memory, or fails over prior to persistence.
- *Write-around caching:* Skipping the cache on writes reduces writes to Redis, but immediate subsequent reads can capture stale data if database replicas lag, while write-heavy workloads degrade overall cache utility.

| Invalidation Approach | Atomicity Mechanism | Failure Behavior | Complexity |
| :--- | :--- | :--- | :--- |
| **Transactional Outbox** | Single DB transaction + CDC worker | Durable replay on Redis failure | Moderate (requires consumer worker) |
| **Synchronous Write-Through** | Non-atomic consecutive calls | Redis down = write downtime | Low implementation, high operational risk |
| **Write-Behind** | Async batch flush from memory | Node crash = permanent data loss | Low latency, zero durability guarantee |
| **Write-Around** | Write DB only, read miss populates | Read-after-write anomalies | Minimal code, poor hit ratios on updates |

## CDN Edge Deployments: Automated Invalidation vs. Passive Draining
**Problem:** Production deployments push new front-end assets, but global users continue to receive outdated JavaScript bundles because manual dashboard purges targeted the wrong environment.

**Recommended Approach:** Anycast routing configured with `stale-while-revalidate` and automated, event-driven purges executed via CI/CD pipelines. Anycast ensures requests route to the nearest Point of Presence (PoP). CI/CD pipelines execute targeted API purges against specific asset paths on deployment, removing human error. Concurrently, `stale-while-revalidate` allows edge nodes to serve current cache contents while fetching new bundles in the background, preventing origin stampedes.

**Why Alternatives Fail:**
- *Anycast + long TTLs + tag-based purge:* While tag invalidations allow grouped purges, relying purely on long TTLs without a safety fallback means that if the invalidation API encounters an upstream outage during a release, outdated assets persist for hours.
- *Unicast + aggressive TTLs + manual purge:* Unicast negates CDN latency benefits by routing global traffic to a single geographic origin. Manual purges introduce human failure during off-hours deployments.
- *Anycast + short TTLs + no purge strategy:* Relying strictly on rapid TTL decay creates frequent origin stampedes under high request volumes, while preventing teams from immediately forcing emergency hotfixes to the edge.

| CDN Configuration | Edge Routing | Purge Trigger | Edge Cache Behavior Under Deploy |
| :--- | :--- | :--- | :--- |
| **Anycast + Auto API Purge** | Geo-optimized Anycast | CI/CD Pipeline | Instant background fetch via stale-while-revalidate |
| **Long TTL + Tagged Purge** | Geo-optimized Anycast | API tag call | Vulnerable to API transport failures |
| **Unicast + Manual Purge** | Single edge location | Human operator | High latency, high operational error rate |
| **Short TTL Passive Decay** | Geo-optimized Anycast | Natural expiry | High origin load spikes, no instant rollback |

## Replication Lag: Read-Your-Writes Session Pinning
**Problem:** Offloading 100% of read traffic to a read replica with 200ms replication lag causes users to view stale state immediately after updating profile, checkout, or payment data.

**Recommended Approach:** Read-your-writes session pinning. When a client performs a write, the application server flags that user's session (e.g., via a short-lived cookie, Redis token, or local timestamp) to route all subsequent reads directly to the primary database for a brief window matching replication lag (such as 1 to 3 seconds). Once the lag threshold clears, reads seamlessly revert to the replica tier. Unmodified user sessions continue reading from replicas unaffected.

**Why Alternatives Fail:**
- *Static "critical read" routing:* Classifying specific business logic endpoints to always hit the primary inevitably expands over time, routing excessive read traffic back to the primary and negating the replica tier.
- *Synchronous replication:* Forcing the primary database to wait for replica acknowledgments prior to completing a write inflates write latency (jumping from ~20ms to >100ms) and ties primary write uptime to replica health.
- *Replica lag monitoring with retry loops:* Average measured replication lag does not prevent immediate sub-200ms read-after-write collisions. Retrying queries blocks execution threads and drives cascading connection exhaustion.

| Consistency Pattern | Routing Target | Latency Overhead | Scalability Impact |
| :--- | :--- | :--- | :--- |
| **Read-Your-Writes Pinning** | Primary for writer, replica for others | None for global reads | High; preserves replica offloading |
| **Static Critical Routing** | Hardcoded primary for selected queries | None | Poor; primary workload steadily expands |
| **Synchronous Replication** | Replicas acknowledge write | 4x–6x write latency increase | Low; coupled system availability |
| **Lag-Based Polling Retry** | Replica with primary fallback | Polling delays block workers | Degrades sharply under write load |

## Decision cheatsheet

| Symptom / Constraint | Root Failure Mode | Architectural Selection | Operational Safeguard |
| :--- | :--- | :--- | :--- |
| **Multiple services write to shared database; stale reads appear** | Out-of-band updates leave stale cache copies | **Cache-aside** (invalidate on write, reload on miss) | Delete cache key; avoid explicit in-line cache updates |
| **Massive negative existence checks saturate DB disk I/O** | 90%+ cold point-lookups traversing huge indexes | **Per-user Bloom filters** in Redis | Fall through to database only on positive hits |
| **Single hot key expiration collapses primary storage** | Thundering herd / cache stampede | **Cache pre-warming** with scheduled worker | Back with `stale-while-revalidate` |
| **Crash between database write and cache invalidation** | Dual-write distributed race condition | **Transactional Outbox** pattern via CDC/worker | Replay events from durable log on cache recovery |
| **Deployment ships stale assets globally; manual step skipped** | Operator error and edge routing misconfiguration | **Anycast edge** + CI/CD automated API purge | Pair with short-term background origin revalidation |
| **Users see stale states immediately after checkout/update** | Read queries hit asynchronous replica during lag | **Read-your-writes** temporal session routing | Route only mutating user to primary for 1–3s |

---
*Source: Summary in our own words of scenario days 08, 15, 18, 19, 26, 43 from "60 Days of System Design Questions" (Joud Awad), a scenario workbook. No text copied.*
