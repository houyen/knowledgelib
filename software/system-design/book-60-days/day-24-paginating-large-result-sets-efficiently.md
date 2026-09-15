---
id: software/system-design/book-60-days/day-24-paginating-large-result-sets-efficiently
canonical_question: Paginating Large Result Sets Efficiently
aliases:
- System Design Day 24
- Paginating Large Result Sets Efficiently
- Day 24 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 24: Paginating Large Result Sets Efficiently

DAY 24 · SYSTEM DESIGN
Paginating Large Result Sets Efficiently
Your API returns 10 million orders.
The frontend asks for "page 5."
Offset 40, limit 10. Simple enough — until your DBA messages you at 2 AM.
Query time: 4.2 seconds. Table scans climbing. Prod is lagging.
Here's the stack: PostgreSQL, 50M rows in orders, sorted by created_at DESC. Users can filter by status.
You're paginating an admin dashboard used by 200 concurrent support agents.
Offset pagination worked fine at 10K rows. At 50M, it's reading and discarding 40 million rows just to
return 10.
You need to fix this before the next sprint ships the customer-facing version — which will have 10x the
traffic.
Here's your setup:
• Table: orders — 50M rows, indexed on created_at, user_id, status
• Query: sorted by created_at DESC, filtered by status
• Client: needs "previous/next" navigation + jump-to-page

---

DAY 24 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
Option A — Cursor pagination ✅  CORRECT
Encode the last seen (created_at, id) into an opaque token. On the next request, decode it and use
WHERE created_at < :last_ts OR (created_at = :last_ts AND id < :last_id) as your anchor.
Why this wins here:
• Query always hits the index at the anchor point — no scan, no discard
• p99 stays flat whether you're on page 1 or page 50,000
• Works with the status filter: WHERE status = 'pending' AND (created_at, id) < (anchor)
• The cursor is position-stable: new rows inserted before your cursor don't shift your page
The UX tradeoff: no jump-to-page. Only previous/next. But this is the right tradeoff for the
dashboard. Support agents navigate sequentially. Nobody needs "jump to page 3,847."
At 50M rows with concurrent filters, cursor pagination is the only approach that hits p99 < 200ms
reliably.
