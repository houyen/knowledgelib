---
id: software/system-design/book-60-days/day-03-rate-limiting-without-boundary-bursts
canonical_question: Rate Limiting Without Boundary Bursts
aliases:
- System Design Day 03
- Rate Limiting Without Boundary Bursts
- Day 03 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 03: Rate Limiting Without Boundary Bursts

DAY 03 · SYSTEM DESIGN
Rate Limiting Without Boundary Bursts
You run a SaaS API. POST /v1/messages is the money endpoint.
Plan limit: 100 requests/minute per API key. Customers keep getting 429s at minute boundaries even
though their average RPS is well under the cap.
Here's what's happening in prod:
• 12:59:58 →  customer sends 90 requests (batched job kicked off)
• 13:00:02 →  same customer sends 90 more (next tick)
• Your counter resets at 13:00:00
• Both bursts pass. 180 requests in 4 seconds. Your downstream database starts crying.
Now Support is on your back about 429s, and SRE is on your back about traffic spikes. You need to replace
the limiter this week.
FOUR OPTIONS ON THE TABLE:
A Fixed Window — bucket per (api_key, minute). Increment, check, reject. Simple, fast, one Redis
key per user.

---

DAY 03 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
Answer: C — Token Bucket ✅
Here's why, and why the other three trip up good engineers:
Why C wins (Token Bucket):
Token Bucket is what AWS API Gateway, Stripe, GitHub, and basically every mature public API runs.
Each API key gets a bucket of 100 tokens, refilling at ~1.66 tokens/sec. Every request takes a token.
Empty bucket = 429.
This fixes the boundary-burst bug exactly: no window resets. The 12:59:58 burst drains the bucket,
and 13:00:02 finds an almost-empty bucket — not a shiny new 100-request allowance. O(1) memory
per key, O(1) check, trivially distributed.
