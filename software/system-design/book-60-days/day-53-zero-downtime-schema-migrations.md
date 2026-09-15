---
id: software/system-design/book-60-days/day-53-zero-downtime-schema-migrations
canonical_question: Zero-Downtime Schema Migrations
aliases:
- System Design Day 53
- Zero-Downtime Schema Migrations
- Day 53 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 53: Zero-Downtime Schema Migrations

DAY 53 · SYSTEM DESIGN
Zero-Downtime Schema Migrations
Your migration ran fine in staging.
Then you ran it in production.
The app went down.
Not because the SQL was wrong. Because you ran it on a live table with 40 million rows while 8 services
were actively writing to it.
Your setup:
→  PostgreSQL. users table. 40M rows. Active writes from 8 services.
→  Product request: split full_name into first_name + last_name.
→  You have a 2-hour maintenance window tonight.
The engineering question: how do you ship this without downtime?
A) Run ALTER TABLE to drop full_name and add first_name + last_name in a single migration during the
maintenance window.
B) Add first_name + last_name as nullable columns first →  backfill →  update all services to write to both
→  drop full_name only after everything is migrated.

---

DAY 53 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
Why B is correct
Two phases.
Phase 1 — Expand: add first_name and last_name as nullable columns. On PostgreSQL, adding a
nullable column with no default is a metadata-only operation — near-instant, no lock. Backfill in
small batches (rate-limited, no row lock escalation). Update services to write to both columns
simultaneously.
Phase 2 — Contract: once every service is writing to the new columns and reads are fully migrated,
drop full_name. You control the timing.
The key property: every step is independently reversible. If something breaks after Phase 1, you stop
— the old column still exists, old services still work.
Slower than A? Yes. 3am pages? Zero.
