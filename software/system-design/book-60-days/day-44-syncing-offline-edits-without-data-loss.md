---
id: software/system-design/book-60-days/day-44-syncing-offline-edits-without-data-loss
canonical_question: Syncing Offline Edits Without Data Loss
aliases:
- System Design Day 44
- Syncing Offline Edits Without Data Loss
- Day 44 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 44: Syncing Offline Edits Without Data Loss

DAY 44 · SYSTEM DESIGN
Syncing Offline Edits Without Data Loss
Your team just shipped "offline mode" for your field-service app.
Technicians work in basements, tunnels, plant floors — connectivity is unreliable.
The demo looked great. Navigator.onLine said false, the app kept working, the sync button pulsed green.
You shipped to 400 users.
Then the incident reports started.
Technician in Munich finishes a repair job offline, syncs when she gets signal. Her updates are gone —
overwritten by a colleague who edited the same record online 12 minutes earlier. Last-write-wins. Her write
lost.
Technician in São Paulo opens the app, goes offline, edits three assets. Comes back online. App throws an
unhandled promise rejection and crashes. IndexedDB schema was on version 2. The update shipped version
3. The migration never ran because he'd never opened the app while online.
You're now asked to actually fix offline-first — not demo it.
Here's the setup:
• 400 field technicians, avg offline window of 40 minutes

---

DAY 44 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
Why D wins (CRDT engine — Automerge / Yjs):
CRDTs (Conflict-free Replicated Data Types) are the only approach where merge is mathematically
guaranteed to produce the same result regardless of the order operations arrive. They're commutative,
associative, and idempotent.
Two technicians can edit the same asset record offline for 6 hours, sync in any order — and the final
state is always deterministic. No merge UI. No "who wins" logic. No data loss.
Linear uses Automerge. Figma uses a custom CRDT for multiplayer. Notion runs a similar model for
their block store. This isn't overengineering — it's what teams reach after trying everything else.
Tradeoff: CRDT payloads are larger (they carry operation history). Yjs is lighter than Automerge for
most cases. Server-side merge logic needs to understand CRDT ops, not just overwrite rows.
