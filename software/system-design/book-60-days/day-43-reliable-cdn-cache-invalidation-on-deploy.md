---
id: software/system-design/book-60-days/day-43-reliable-cdn-cache-invalidation-on-deploy
canonical_question: Reliable CDN Cache Invalidation on Deploy
aliases:
- System Design Day 43
- Reliable CDN Cache Invalidation on Deploy
- Day 43 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 43: Reliable CDN Cache Invalidation on Deploy

DAY 43 · SYSTEM DESIGN
Reliable CDN Cache Invalidation on Deploy
Your CDN saved you from explaining a 400ms load time to your VP.
Then your deploy shipped. And nobody got the fix.
Here's what happened:
Your edge nodes were still serving the old JS bundle — TTL hadn't expired. You triggered a cache purge
manually. But you hit the wrong environment. Prod kept serving the stale version for 6 more hours.
You need a CDN configuration that handles invalidation reliably under deploy pressure. Which one do you
pick?
A) Anycast routing + stale-while-revalidate + event-driven purge via API on deploy
B) Unicast routing + aggressive TTLs + manual cache purge via dashboard
C) Anycast routing + long TTLs + tag-based invalidation via API
D) Anycast routing + short TTLs + no invalidation strategy (let caches expire naturally)

---

DAY 43 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
A — Anycast + stale-while-revalidate + event-driven purge — the right answer
Anycast advertises the same IP from multiple PoPs. BGP routes each user to the closest edge
automatically. Tokyo user hits Tokyo — not Virginia.
Stale-while-revalidate: serve the cached version immediately, fetch a fresh copy in the background.
Users never wait on a cache miss to resolve.
Event-driven purge: your CI/CD pipeline fires a Cloudflare or CloudFront API call on every deploy,
targeting exactly the changed assets. No manual steps. No wrong-env clicks. No 2 AM mistakes.
