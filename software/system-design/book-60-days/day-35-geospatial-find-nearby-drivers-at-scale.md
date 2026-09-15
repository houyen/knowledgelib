---
id: software/system-design/book-60-days/day-35-geospatial-find-nearby-drivers-at-scale
canonical_question: Geospatial Find Nearby Drivers at Scale
aliases:
- System Design Day 35
- Geospatial Find Nearby Drivers at Scale
- Day 35 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 35: Geospatial Find Nearby Drivers at Scale

DAY 35 · SYSTEM DESIGN
Geospatial “Find Nearby Drivers” at Scale
You're building the "find nearby drivers" feature for a ride-hailing app.
At peak, you have 500,000 active drivers updating their GPS location every 5 seconds. Riders query for
drivers within 2km. At scale, you're doing ~100,000 proximity queries per second.
Your naive implementation does this:
SELECT * FROM drivers
WHERE lat BETWEEN ? AND ?
AND lng BETWEEN ? AND ?
It works fine at 1,000 drivers. At 500,000, it's a full table scan on every query. Latency hits 800ms. Riders
see a spinner. Drivers miss trips.
Your team proposes 4 approaches to fix this:
A) Geohash partitioning — Encode each driver's location into a geohash string. Index by geohash prefix.
Proximity queries become a string lookup on the index.

---

DAY 35 · ANSWERS & EXPLANATIONS
Every option here ships with its own diagram, so no single image marks the answer; the author's pick is D — H3
Hexagonal Grid (Answer 1 below).
Answer 1 ✓  CORRECT ANSWER
Answer: D — H3 Hexagonal Grid
Why D wins:
Uber open-sourced H3 for exactly this problem. Hexagons have 6 neighbors, all equidistant from the
center. Squares (geohash) have corner neighbors that are ~40% farther — this distorts "within 2km"
queries. H3 also has 16 resolution levels (no reindexing on zoom changes). The killer feature: the k-
ring query (target cell + 6 neighbors) guarantees no driver gets missed near a boundary. Uber does
sub-10ms lookups at millions of drivers: get cells in ring →  fetch IDs from Redis set keyed by cell. Lyft,
Airbnb, DoorDash all use variants.
