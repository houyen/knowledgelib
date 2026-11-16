---
id: software/system-design/book-60-days/database-performance-and-scaling
canonical_question: How do you choose the right architectural pattern to eliminate database bottlenecks across querying, sharding, indexing, connection pooling, and storage scale?
aliases:
- database performance bottlenecks and sharding strategies
- fixing high write latency and hot partitions
- connection pool exhaustion pgbouncer rds
- bigquery partition and clustering cost optimization
- full text search postgres vs elasticsearch scale
- orm n plus 1 query optimization patterns
- database scaling patterns decision guide
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: '2026-11-16'
source_type: summary
source: Summary in our own words of scenario days 02, 05, 12, 13, 16, 45, 49 from "60 Days of System Design Questions" (Joud Awad), a scenario workbook. No text copied.
---

# Database Scaling and Bottleneck Remediation Patterns

## TL;DR
Database scaling breakdowns happen when general-purpose patterns collide with skewed access distributions. Fix bottlenecks by aligning storage and retrieval paths to the actual query shape: colocate related data on single shards, split connection pools by transaction lifespan, and narrow index scope to active data slices. When relational engines hit fundamental hardware or locking limits, transition to purpose-built primitives like write-sharded partition keys, compound warehouse pruning, or dedicated inverted search indices.

## Resolving ORM N+1 Query Overhead
Loading 50 records triggers 51 sequential database roundtrips (1 parent query plus 50 child lookups), pushing endpoint P95 latency to 2.4s.

Use eager loading with an explicit join (`include: { customer: true }`). A single `LEFT JOIN` fetches both parent and child records in one roundtrip, dropping P95 latency to ~80ms without introducing operational overhead or infrastructure dependencies.

### Why the alternatives fail
- **DataLoader batching (`WHERE id IN (...)`)**: Designed to batch unpredictable traversal graphs in GraphQL resolvers; adding it to a straightforward REST endpoint introduces queueing abstractions to solve a problem native SQL handles in one pass.
- **Redis caching**: Masks inefficient query patterns instead of eliminating them; still executes 50 distinct network calls per request, creates cache invalidation bugs when records change, and risks thundering herds on cold starts.
- **Denormalization (duplicating customer data onto orders)**: Transforms a read optimization into write amplification; risks persistent data discrepancies when shared attributes update without comprehensive backfill paths.

| Pattern | Latency Impact | Operational Overhead | Data Consistency |
| :--- | :--- | :--- | :--- |
| **Eager Loading (JOIN)** | ~80ms P95 | None (Native SQL) | Strong (ACID) |
| DataLoader | Moderate | Moderate (App queue) | Strong |
| Redis Cache | Poor (50 roundtrips) | High (Infra + invalidation) | Eventual (Drift risk) |
| Denormalization | Fast read | High write logic | Poor (Stale fields) |

## Database Sharding Under Skewed Tenant Read Patterns
A 500M row order table growing by 3M rows weekly exceeds vertical scaling limits, where 80% of reads query an individual customer's last 30 days of activity.

Implement directory-based sharding with an external mapping table (cached in memory). Storing all records for a given customer on a dedicated shard guarantees that 80% of read traffic executes on a single node without scatter-gather overhead, while allowing point migrations of outsized "whale" accounts without rehashing the entire database.

### Why the alternatives fail
- **Hash sharding on `order_id`**: Scatters a single customer's historical orders across the entire cluster, turning every customer-filtered query into a scatter-gather fan-out bound by the slowest node.
- **Range sharding on `created_at`**: Directs 100% of the 400 RPS write stream and the majority of active reads onto the newest chronological shard, creating severe single-node resource exhaustion.
- **Consistent hashing with virtual nodes**: Distributes keys uniformly but lacks a mechanism to isolate or migrate specific high-throughput enterprise accounts that land on the same physical shard.

| Strategy | Read Localization (80% Reads) | Hotspot Exposure | Large Account Migration |
| :--- | :--- | :--- | :--- |
| **Directory-Based (Customer)** | High (Single node) | Low (Rebalanceable) | Direct (Point remap) |
| Hash (`order_id`) | None (Scatter-gather) | Very Low | Inflexible |
| Range (`created_at`) | High (Temporal) | Critical (Active shard melts) | Impossible |
| Consistent Hashing | Moderate | Moderate | Inflexible |

## Indexing High-Ingest Tables with Narrow Dashboard Queries
An ingestion pipeline of 8K writes/sec causes write latency to surge from 12ms to 140ms across 4 existing indexes, while analytics queries require filtering on `(tenant_id, event_type, created_at)` for recent signups.

Apply a partial B-tree index using `WHERE event_type = 'signup' AND created_at > now() - interval '7 days'`. Because signup events represent roughly 4% of traffic and the 7-day window covers ~5% of table volume, the index covers only ~0.2% of total rows. Inserts outside this predicate bypass index maintenance entirely, restoring write throughput while providing full index coverage for matching dashboard queries.

### Why the alternatives fail
- **Covering index with `INCLUDE (user_id, payload)`**: Ingesting wide JSONB blobs into index leaf pages forces heavy disk writes on every insert and update, driving P99 write latency toward 800ms.
- **Full composite B-tree on `(tenant_id, event_type, created_at)`**: Forces index tree recalculations across all 8K writes/sec for every tenant and event type to accelerate queries scanning a minute fraction of the dataset.
- **Read replica offloading**: Replica nodes must process write-ahead logs and update the identical set of indexes, transferring the write bottleneck into severe replication lag.

| Indexing Technique | Write Path Impact | Target Query Latency | Storage Footprint |
| :--- | :--- | :--- | :--- |
| **Partial Index** | Negligible (~0.2% rows) | Sub-millisecond scan | Minimal |
| Covering (`INCLUDE`) | Extreme (JSONB write bloat) | Fast (Index-only scan) | Massive |
| Full Composite B-Tree | High (100% of writes) | Sub-millisecond scan | Large |
| Read Replica Routing | High (Replication lag) | Low on primary | High (Duplicate compute) |

## Connection Pooling for Heterogeneous Workloads
A single PostgreSQL instance capped at 300 connections must support an 800 RPS REST API (requesting 400 connections), long-running 30–90s analytics queries, and 0–200 concurrent bursty Lambda invocations.

Deploy PgBouncer using split pool modes: transaction mode for the REST API and Lambda functions, and session mode for analytics workers. Transaction pooling collapses hundreds of stateless, short-lived client connections into 30–50 database connections. Session pooling allocates dedicated connections to background workers, preserving session-level parameters, cursors, and temporary tables.

### Why the alternatives fail
- **Universal transaction mode**: Reallocates connections between individual transactions; long-running workers lose temporary tables, cursors, and session states (`SET LOCAL`), leading to runtime failures.
- **RDS Proxy (Lambda) + PgBouncer (API)**: Adds operational complexity and financial overhead without solving session retention for long-running worker tasks.
- **Dedicated read replica for workers**: Offloads CPU load but ignores connection math; long-running jobs holding connections for 90 seconds rapidly exhaust the replica's connection ceiling.

| Pooling Setup | Stateless Multiplexing | Stateful Query Safety | Infrastructure Overhead |
| :--- | :--- | :--- | :--- |
| **Dual-Mode PgBouncer** | Optimal (30–50 conns) | Full (Session preserved) | Minimal (Single service) |
| Universal Transaction Mode | Optimal | Unsafe (State discarded) | Minimal |
| RDS Proxy + PgBouncer | Good | Incompatible with workers | High (Dual proxies) |
| Dedicated Read Replica | None (Connections held) | High | High (Extra RDS node) |

## Mitigating Hot Partition Keys in Distributed NoSQL
A multi-tenant DynamoDB table running 12K writes/sec suffers throughput throttling and 400ms latency spikes because a single tenant drives 9K writes/sec to its partition key.

Implement application-level write sharding by appending a pseudo-random suffix (such as `tenant_id#0` through `tenant_id#9`) to the partition key on write. This fans the 9K writes across 10 physical partitions (~900 writes/sec each), keeping throughput beneath physical partition thresholds while requiring reads for that tenant to scatter-gather across all suffixes.

### Why the alternatives fail
- **Partition splitting**: DynamoDB splits partitions automatically based on aggregate throughput, but all writes containing the identical partition key hash to the same physical destination partition post-split.
- **Client-side write jitter**: Jitter smooths brief concurrent bursts (thundering herds), but provides zero throughput reduction against a sustained 9K writes/sec stream while adding artificial client latency.
- **Time-bucketing (`tenant_id#YYYY-MM-DD-HH`)**: Reassigns the write hotspot to a new partition key every hour without lowering instantaneous write volume, while complicating historical queries across 24 keys per day.

| Hot Partition Strategy | Sustained Throughput Fix | Read Complexity | Implementation Tier |
| :--- | :--- | :--- | :--- |
| **Write Sharding (Suffixes)** | Effective (Divided by N) | Moderate (Fan-out query) | Application layer |
| Partition Splitting | Ineffective (Same hash target) | Unchanged | Managed storage |
| Client Jitter | Ineffective (Burst only) | Unchanged | Client transport |
| Time Bucketing | Ineffective (Moves hotspot) | High (Multi-key scan) | Schema key design |

## Data Warehouse Cost Optimization via Partitioning and Clustering
Analysts querying a 3.2 TB BigQuery events table for 30-day customer slices trigger full-table scans, resulting in a $4,200 monthly bill across 12 queries.

Partition the table by ingestion date and cluster it by `customer_id`. Date partitioning prunes roughly 94% of storage blocks for a 30-day window on 18 months of historical data. Clustering groups rows by customer within those remaining blocks, pruning an additional 90–95% of data during scan time, dropping total scanned bytes from 3.2 TB to ~12 GB and reducing monthly costs to ~$70.

### Why the alternatives fail
- **Date partitioning only**: Filters unneeded date ranges but scans all customers within the 30-day period (~500 GB scanned per query), leaving significant query costs unaddressed.
- **Customer ID range partitioning**: Skewed customer activity concentrates 80% of data into high-volume enterprise partitions, eliminating pruning benefits and forcing full scans of the hottest partition across all dates.
- **Redshift DISTKEY and SORTKEY without partitioning**: Accelerates node joins and disk sorting, but still requires cluster-wide full table scans and creates storage skew when enterprise customers dominate.

| Data Warehouse Strategy | Scanned Data (30-day Query) | Relative Cost | Skew Handling |
| :--- | :--- | :--- | :--- |
| **Date Partition + Customer Cluster** | ~12 GB | ~$70/month | High |
| Date Partitioning Only | ~500 GB | ~$1,400/month | High |
| Customer ID Partitioning | High (Hot partitions) | High | Poor |
| DISTKEY + SORTKEY (No Partitions) | Full Table (3.2 TB) | High | Poor |

## Transitioning Relational Full-Text Search to Dedicated Engines
A SaaS document table scaling to 100M rows experiences full-text query latency degradation to 4.2s P95 on PostgreSQL, failing a sub-200ms P99 latency target.

Migrate search operations to an external Elasticsearch cluster. Utilizing an inverted index with compressed posting lists, immutable segments, native BM25 relevance scoring during retrieval, and horizontal shard distribution delivers sub-100ms P99 search latencies at 100M document scale.

### Why the alternatives fail
- **PostgreSQL GIN indexes on `tsvector`**: Effective between 1M and 5M documents; at 100M documents, GIN index sizes inflate (40–80GB), horizontal scaling is absent, and query latency stalls around ~500ms.
- **Redis query caching**: Captures repetitive queries for roughly 40% of traffic, but leaves 60% of requests on the 4.2s tail latency path while incurring constant cache invalidation churn from document updates.
- **Lightweight search engines (Typesense / Meilisearch)**: Deliver strong developer ergonomics up to 30M records, but lack the distributed partition management, custom scoring controls, and operational tooling required for 100M documents under rigid SLAs.

| Search Architecture | P99 Latency (100M Docs) | Ops Complexity | Horizontal Sharding |
| :--- | :--- | :--- | :--- |
| **Elasticsearch** | <100ms | High (Cluster ops) | Native |
| PostgreSQL GIN Index | ~500ms | Low (In-database) | None |
| Redis Query Cache | 4.2s tail (Bypassed) | Moderate | Not applicable |
| Lightweight Engines | 200–400ms | Moderate | Limited at scale |

## Decision cheatsheet

| Symptom / Workload Pattern | Recommended Pattern | Core Mechanism |
| :--- | :--- | :--- |
| Sequential N+1 queries in ORM | Eager loading with `JOIN` | Single relational query roundtrip |
| High-volume reads on tenant subsets | Directory-based sharding | Single-shard read colocation + whale migration |
| High write ingest bottlenecked by index updates | Filtered partial index | Excludes non-matching rows from index maintenance |
| Connection pool exhaustion across mixed lifespans | PgBouncer split modes (Tx + Session) | Multiplexes stateless traffic; preserves stateful sessions |
| Throughput throttling on a single partition key | Write sharding (randomized suffixes) | Distributes traffic across physical shards |
| Expensive warehouse scans on dual-filter analytics | Date partitioning + attribute clustering | Macro partition pruning combined with micro block skipping |
| Full-text search latency degradation past 50M docs | Dedicated inverted index (Elasticsearch) | Sharded posting-list intersections with retrieval-time BM25 |

---
*Source: Summary in our own words of scenario days 02, 05, 12, 13, 16, 45, 49 from "60 Days of System Design Questions" (Joud Awad), a scenario workbook. No text copied.*
