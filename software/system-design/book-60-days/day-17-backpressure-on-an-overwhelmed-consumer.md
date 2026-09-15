---
id: software/system-design/book-60-days/day-17-backpressure-on-an-overwhelmed-consumer
canonical_question: Backpressure on an Overwhelmed Consumer
aliases:
- System Design Day 17
- Backpressure on an Overwhelmed Consumer
- Day 17 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 17: Backpressure on an Overwhelmed Consumer

DAY 17 · SYSTEM DESIGN
Backpressure on an Overwhelmed Consumer
Your Kafka consumer is processing 800 events/sec.
The producer just hit 5,000 events/sec and it's not slowing down.
Lag chart: 12 minutes behind and climbing. Consumer memory: 89% and rising. The on-call alert just fired.
You have ~4 minutes before the JVM starts GC-thrashing and the pod gets OOM-killed.
Here's the setup:
Producer →  Kafka topic (5K events/sec, growing)
Consumer →  spring-kafka @KafkaListener, batch=500, processes ~800 events/sec
Downstream →  Postgres write + external HTTP call (the real bottleneck)
SLA →  events must be processed, not silently dropped
The consumer can't keep up. The producer doesn't know it. What do you do?
A Drop events on the floor — fail fast, return early, let the lag burn down. The system stays alive.

---

DAY 17 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
Answer: D — Rate-limit + load-shed ✅
Why D wins:
The SLA says events must be processed — not dropped, not blocked. That kills A and B immediately.
Cap the consumer's intake at ~1K/sec with headroom, route overflow to a durable secondary topic
(events.overflow) with its own consumer group that drains during off-peak. Producer keeps
producing. Primary consumer keeps a steady heartbeat. Overflow gets processed later. That's graceful
degradation. Stripe and Shopify publish architecture posts on this exact pattern.
