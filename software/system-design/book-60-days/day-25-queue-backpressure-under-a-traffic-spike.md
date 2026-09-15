---
id: software/system-design/book-60-days/day-25-queue-backpressure-under-a-traffic-spike
canonical_question: Queue Backpressure Under a Traffic Spike
aliases:
- System Design Day 25
- Queue Backpressure Under a Traffic Spike
- Day 25 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 25: Queue Backpressure Under a Traffic Spike

DAY 25 · SYSTEM DESIGN
Queue Backpressure Under a Traffic Spike
Your order processing service runs on SQS.
Normal load: 200 orders/min. Consumers keep up fine.
Then Black Friday hits. Producers start pushing 4,000 orders/min. Queue depth climbs to 80,000 messages
in 20 minutes. Your downstream DB is at 95% CPU. Consumers are falling behind and you're watching the
queue grow in real time.
You need to handle this backpressure. What do you do?
A) Scale consumers horizontally — add more Lambda functions / EC2 workers to chew through the
backlog faster.
B) Set a visibility timeout and route failures to a dead-letter queue to protect against poison pills.
C) Rate-limit producers at the source — use a token bucket or sliding window to cap how fast messages
enter the queue.
D) Switch to SQS delay queues — defer message visibility to spread out delivery and reduce consumer
pressure.

---

DAY 25 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
Why C wins, and why it doesn't wreck UX
The queue grows because the producer is winning the race. 4,000 in, 200 out. You can scale
consumers all day and that gap won't close on its own, especially with the DB already sitting at 95%
CPU.
The fix is upstream. Rate-limit the producer with a token bucket or sliding window. In AWS that's API
Gateway usage plans, Lambda reserved concurrency, or throttle middleware inside the service. Queue
depth stabilizes, consumers catch up at their natural pace, and the DB stops cooking.
The mental model: slow the tap, don't just widen the drain.
Now the part the diagram glossed over: the "producer" isn't your user.
In most real systems the order flow is decoupled. A user submits an order, it's written to the DB, and
they get their success response right away. A separate processor then reads those events (polling or
CDC) and emits them to the queue. That emitter is the producer you throttle.
So rate-limiting never touches checkout. The user already has their ack from the write. You're capping
how fast events flow into the queue, not how fast users can order. UX stays intact; the queue just stops
outrunning your consumers.
