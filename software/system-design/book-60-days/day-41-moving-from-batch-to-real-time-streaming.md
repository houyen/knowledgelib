---
id: software/system-design/book-60-days/day-41-moving-from-batch-to-real-time-streaming
canonical_question: Moving from Batch to Real-Time Streaming
aliases:
- System Design Day 41
- Moving from Batch to Real-Time Streaming
- Day 41 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 41: Moving from Batch to Real-Time Streaming

DAY 41 · SYSTEM DESIGN
Moving from Batch to Real-Time Streaming
Your data team just got a new SLA: surface fraud signals within 500ms of a transaction.
Right now you're running nightly Spark batch jobs. The business wants "real-time." Your team knows Spark.
Someone already opened a PR adding Spark Structured Streaming.
The transaction volume: 8,000 events/sec peak. You're on AWS. The fraud model runs in Python. The
output feeds a DynamoDB table the API reads from.
You need to redesign the pipeline. What do you pick?
A) Kafka Streams — event-by-event processing, stateful operators, sub-10ms latency. Lives inside your app
JVM.
B) Apache Flink — true streaming engine, exactly-once semantics, built for high-throughput stateful
processing.
C) Spark Structured Streaming — micro-batch under the hood, 100ms–5s windows, same API your team
already knows.
D) Keep the batch job, drop the window to 1 minute — "near real-time" at zero migration cost.

---

DAY 41 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
Why B wins (Apache Flink):
Flink is a true streaming engine — event-by-event, not batch. Every transaction triggers processing the
moment it arrives. Latency: sub-50ms end-to-end with proper tuning. At 8K events/sec, Flink doesn't
blink. Exactly-once semantics mean your fraud signals aren't double-counted when a node fails. The
Python fraud model integrates via PyFlink or a sidecar microservice. Flink's watermark model handles
out-of-order events cleanly — which matters when transactions arrive from distributed payment
processors with clock skew.
Operational overhead is real. But the SLA demands it. You're not reaching for Flink prematurely here
— the business asked for 500ms and gave you 8K events/sec. That's exactly the problem Flink was
built for.
