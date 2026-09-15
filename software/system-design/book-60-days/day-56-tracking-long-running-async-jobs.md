---
id: software/system-design/book-60-days/day-56-tracking-long-running-async-jobs
canonical_question: Tracking Long-Running Async Jobs
aliases:
- System Design Day 56
- Tracking Long-Running Async Jobs
- Day 56 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 56: Tracking Long-Running Async Jobs

DAY 56 · SYSTEM DESIGN
Tracking Long-Running Async Jobs
Your background job ran for 4 minutes and nobody knows if it finished.
That's not a job queue problem. That's a missing design problem.
Long-running jobs break every assumption you built for synchronous APIs. Your load balancer times out
after 30s. Your mobile client doesn't know whether to retry. Your retry logic re-runs a job that already half-
completed.
Here's the real scenario:
You're processing a video upload. The job takes 2–8 minutes. Millions of users.
What do you expose to the client?
A) Polling endpoint — client hits /jobs/:id/status every 5s until done
B) Webhook — job fires a POST to client's callback URL on completion
C) SSE / WebSocket — server pushes progress updates in real time
D) Synchronous wait — keep the HTTP connection open until the job finishes
One scales to millions without coupling your infrastructure to client uptime.

---

DAY 56 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
A) Polling — Correct for most cases
Client-controlled, stateless, scales independently. The server doesn't care if the client disconnects,
retries, or crashes — the job runs and the status endpoint just answers queries. 5s polling intervals on
a job that takes 2–8 minutes is trivially cheap. The key rules: make job IDs stable and idempotent, set
a TTL on job records so you don't accumulate state forever, and use exponential backoff not fixed
intervals. LinkedIn, YouTube, and S3 multipart uploads all use polling for async job status.
Answer 2
B) Webhook — Right idea, wrong default
Webhooks are great for server-to-server flows where the receiver has a stable HTTPS endpoint. They
fall apart for mobile clients (no public URL), in environments with NAT/firewall, and when the
receiver is down at delivery time. You'd need a retry queue, delivery guarantees, and signature
verification just to make it reliable. Webhooks work well as a supplementary delivery mechanism for
platform integrations — not as the primary client notification path for end users.
