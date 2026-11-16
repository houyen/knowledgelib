---
id: software/system-design/bytebytego-archive-2025/nosql-databases-caching-redis
canonical_question: How do modern database models, distributed storage architectures, and multi-tier caching systems differ across performance, persistence, and reliability trade-offs?
aliases:
- database paradigm comparison
- nosql vs relational architecture
- redis persistence and caching patterns
- mongodb sharding and replication
- amazon s3 distributed storage architecture
- cache failure modes and mitigations
- multi-tier system caching guide
entity_type: book_chapter
domain: software > system-design > bytebytego-archive-2025
last_verified: '2026-11-16'
source_type: summary
source: Summary in our own words of 10 articles from the ByteByteGo "2025 Archive" (system design newsletter collection). No text copied.
---

# Modern Database Paradigms, Distributed Storage, and Caching Architecture

## TL;DR
Modern applications require purpose-built data stores rather than a single database engine, spanning relational, document, wide-column, key-value, blob, and in-memory tiers. Caching operates across every infrastructure layer—from browser headers to database buffer pools—to bypass disk and network bottlenecks. Maintaining reliability across this ecosystem requires distinct architectural strategies for sharding, replication, data persistence, and edge-case failure modes like cache stampedes.

## Storage Categories and Infrastructure Mapping

Selecting a storage engine depends on access access patterns, transactional guarantees, and schema variability. Cloud providers map these paradigms to managed offerings optimized for particular access characteristics.

| Paradigm | Primary Workload & Strengths | Representative Engines | AWS Managed Equivalent |
| :--- | :--- | :--- | :--- |
| **Relational (RDBMS)** | Strict schemas, ACID transactions, complex joins | PostgreSQL, MySQL, Oracle | RDS, Aurora |
| **Key-Value** | Low-latency primary-key reads and writes | DynamoDB, FoundationDB, Riak, Redis | DynamoDB |
| **Document** | Hierarchical, evolving schemas formatted in BSON/JSON | MongoDB, CouchDB, Firestore | DocumentDB |
| **Wide-Column** | Massive semi-structured tables partitioned across clusters | Apache Cassandra, ScyllaDB, HBase | Amazon Keyspaces |
| **In-Memory** | Microsecond caching, session state, real-time counters | Redis, Memcached | ElastiCache |
| **Object / Blob** | Unstructured binary payloads (media, backups, archives) | Amazon S3 | Amazon S3 |
| **Search / Analytical** | Full-text indexing, log inspection, columnar analytics | Elasticsearch, ClickHouse | OpenSearch, Redshift |

Beyond these primary categories, specialized workloads employ Graph databases for relationship traversal, Time-Series engines for timestamp-ordered metrics, Immutable Ledgers for verifiable audit trails, and Vector databases for high-dimensional machine learning similarity search.

## Distributed Store Internals: Sharding, Replication, and Persistence

Distributed datastores trade single-node simplicity for horizontal scale and fault isolation. Examining the internal mechanics of representative systems reveals how data routes, replicates, and survives power outages.

### Horizontal Scaling in Document Stores (MongoDB)
MongoDB partitions data using a three-tier topology:
1. **Routing Tier (`mongos`):** Client drivers connect to query routers that inspect queries, check partition keys, and direct operations to target partitions without maintaining state.
2. **Configuration Cluster:** Dedicated metadata servers store the mapping between shard keys and physical clusters, directing routers to partition boundaries.
3. **Partition Sets (Shards):** Each shard runs as an independent replica set. A single elected primary processes incoming writes and streams operations to secondaries. If the primary drops offline, secondaries run an automated election to promote a successor.

### In-Memory Execution with Disk Backing (Redis)
Redis executes read and write operations inside RAM for minimal latency, offering two decoupled mechanisms to preserve state against process termination:
- **Append-Only File (AOF):** Logs write commands to disk strictly *after* modifying memory. Because logging occurs post-execution, write operations stay non-blocking. Durability during a crash is restored by replaying the command sequence.
- **Redis Database Snapshots (RDB):** Captures point-in-time binary images of dataset state. The primary process invokes `bgsave`, which forks a child process. Relying on OS copy-on-write, the child dumps memory to disk without stalling concurrent mutations on the main thread.
- **Hybrid Approach:** Merges compact RDB base images with incremental AOF logs to balance rapid system recovery with low data-loss windows.

Specialized in-memory primitives also dictate storage efficiency: sorted sets (`zset`) maintain rank order and remove duplicate entries for abuse prevention, hashes group entity counters efficiently, and bitmaps collapse millions of binary flags (such as membership or session status) into minimal memory footprints.

### Massive-Scale Object Architecture (Amazon S3)
To sustain millions of concurrent requests while storing more than 350 trillion items with 99.999999999% durability, Amazon S3 organizes responsibilities across five distinct microservice tiers:
- **Front-End Transport:** Resolves incoming DNS, authenticates API credentials, enforces rate controls, and balances traffic across regions.
- **Metadata and Indexing Engine:** Manages an isolated global catalog and key-partitioning mechanism that maps unique object IDs to physical disk locations.
- **Data Placement and Storage:** Distributes data slices across independent Availability Zones using erasure coding instead of naive full-payload duplication, minimizing storage overhead while surviving hardware destruction.
- **Durability and Self-Healing:** Continuously scans stored blocks with background auditing sweeps, calculates cryptographic checksums, and replaces degraded hardware slices automatically.
- **Security and Governance:** Handles bucket policies, AWS IAM verification, DDoS defenses, immutable write constraints via Object Lock, and historical versioning.

## The Multi-Layer Caching Topology

Caching is not confined to a standalone key-value cluster; it forms a distributed hierarchy from client interface to disk storage engine:

```
[ Client / Browser ]      --> Cache-Control, ETag HTTP headers
        │
[ Content Delivery Network ] --> Edge caching of static assets and payloads
        │
[ Load Balancer ]         --> Reverse-proxy response caching
        │
[ Messaging Tier ]        --> Message retention buffers on disk (e.g., Kafka)
        │
[ Application Service ]   --> CPU L1-L3, runtime heap memory, local disk caches
        │
[ Distributed Cache ]     --> Remote shared clusters (Redis, Memcached)
        │
[ Search Subsystem ]      --> Inverted indices (Elasticsearch)
        │
[ Database Engine ]       --> Write-Ahead Logs (WAL), Buffer Pools, Materialized Views
```

Within database engines, data hits multiple memory staging grounds: incoming writes land in a sequential Write-Ahead Log (WAL) before B-Trees recalculate, while incoming reads traverse memory buffer pools to prevent reading table spaces from slow storage volumes.

## Cache Failure Modes and Defenses

When caches lose synchronization with primary data stores or drop traffic unexpectedly, downstream components face catastrophic load spikes.

| Failure Mode | Trigger Mechanism | Primary Mitigations |
| :--- | :--- | :--- |
| **Thundering Herd** | Bulk keys expire at the exact same second, sending massive concurrent query bursts to the database. | 1. Append randomized jitter intervals to key TTL values.<br>2. Rate-limit or allow only critical traffic to reach the primary DB while the cache warms. |
| **Cache Penetration** | Repeated requests target keys that exist neither in the cache nor the database, bypassing memory lookup. | 1. Write `null` or empty placeholders into the cache for missing keys.<br>2. Evaluate key existence using a Bloom filter ahead of the cache layer. |
| **Cache Breakdown** | A single hyper-trafficked ("hot") key carrying high read volume expires, leaking thousands of queries. | 1. Permanently exempt top hot keys from time-to-live expirations.<br>2. Implement mutex locks so only one worker refreshes the key from the DB. |
| **Cache Crash** | The distributed cache cluster becomes entirely unreachable, redirecting all read volume to disks. | 1. Enforce aggressive circuit breakers to protect relational databases.<br>2. Deploy multi-node clustering and automatic failover replicas. |

## Common Mistakes

- **Applying uniform expiration timestamps across batch updates:** Writing large datasets with identical TTL values guarantees a thundering herd when the clock interval lapses; developers must always introduce random jitter.
- **Allowing unvalidated key misses to touch persistent storage:** Querying relational tables for missing identifiers without fronting lookups with a Bloom filter or caching empty/null results leaves the database exposed to query penetration attacks.
- **Setting arbitrary TTL windows on high-frequency hot keys:** Evicting a hot record responsible for a large share of system throughput triggers immediate cache breakdown; critical keys should be updated proactively or kept persistent without automatic expiry.
- **Failing to decouple cache crashes from core database access:** Omitting circuit breakers means a failed Redis or Memcached node cascades instantly into a complete primary database outage due to unbounded traffic shifting.

---
*Source: Summary in our own words of 10 articles from the ByteByteGo "2025 Archive" (system design newsletter collection). No text copied.*
