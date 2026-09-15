---
id: software/system-design/book-60-days/day-37-multi-writer-conflicts-in-collaborative-editing
canonical_question: Multi-Writer Conflicts in Collaborative Editing
aliases:
- System Design Day 37
- Multi-Writer Conflicts in Collaborative Editing
- Day 37 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 37: Multi-Writer Conflicts in Collaborative Editing

DAY 37 · SYSTEM DESIGN
Multi-Writer Conflicts in Collaborative Editing
Two users edit the same document at 9:03 AM.
No locking. No coordination. Just two clients writing to the same record.
Both changes hit your server 300ms apart. One lands first. The other overwrites it.
User A's work is gone. They never get an error. They just… lose their change.
This is the multi-writer conflict problem. Every collaborative system hits it eventually. Your choices:
A) Last-Write-Wins (LWW) — highest timestamp takes the record. Loser's change disappears silently.
B) Vector Clocks — track causality per replica, detect conflicting versions, surface them to the application
for resolution.
C) CRDTs (Conflict-free Replicated Data Types) — data structures that mathematically merge concurrent
writes without coordination.
D) Operational Transformation (OT) — transform each operation relative to concurrent operations before
applying, keeping intent intact.

---

DAY 37 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
Answer: C — CRDTs (but the real answer depends on your conflict model — full breakdown below)
C — CRDTs wins at scale
CRDTs are data structures designed so any two replicas can always be merged — mathematically,
without coordination. The key insight: if operations are commutative, associative, and idempotent,
conflicts structurally can't exist.
Examples:
• G-Counter: only increments. Merge = take max per replica. Always converges.
• LWW-Element-Set: union of adds + removes with timestamps.
• RGA / YATA (sequence CRDTs): each character gets a unique ID, concurrent inserts are
deterministically ordered — this is collaborative text editing.
Figma's canvas runs on CRDTs. Notion's block model is CRDT-based. At millions of concurrent writers
across distributed regions, every node converges independently — zero coordination required.
