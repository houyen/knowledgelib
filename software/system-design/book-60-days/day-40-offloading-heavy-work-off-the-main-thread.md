---
id: software/system-design/book-60-days/day-40-offloading-heavy-work-off-the-main-thread
canonical_question: Offloading Heavy Work Off the Main Thread
aliases:
- System Design Day 40
- Offloading Heavy Work Off the Main Thread
- Day 40 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 40: Offloading Heavy Work Off the Main Thread

DAY 40 · SYSTEM DESIGN
Offloading Heavy Work Off the Main Thread
Your React dashboard freezes for 4 seconds every time a user uploads a CSV.
Not a network freeze. A browser freeze. Tab unresponsive. Animations stuck. The "Page Unresponsive"
dialog popping up on Chrome.
Here's what's happening in prod:
• User drops a 80MB CSV (200k rows, 40 columns) into the upload zone
• Your code: Papa.parse(file, { complete: ... }) on the main thread
• Parsing + validation + schema mapping = 3.8s of synchronous JS
• During those 3.8s: scroll dies, the loading spinner stops spinning, input lag goes infinite
• Your INP score on the perf dashboard is now red. Lighthouse is screaming.
Product wants this fixed before the enterprise demo on Friday. Four options on the table:
A requestIdleCallback + time-slicing — chunk the parse into 5ms slices, yield between rows, let the
browser breathe.

---

DAY 40 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
Why B wins:
The actual problem isn't speed. It's where the work runs. The main thread is the same thread that
handles scroll, input, layout, paint, and animation. Anything synchronous on it = jank. Period.
A Web Worker is a separate OS-level thread with its own event loop. You ship the file (transferable via
postMessage with a Transferable so it's zero-copy), parse it over there, send back the parsed rows.
Main thread stays at 60fps the entire time. INP drops from 3800ms to ~80ms. Done.
This is what Figma does for its rendering pipeline, what Google Sheets does for formula recalc, what
Excalidraw does for its scene processing, what VS Code Web does for syntax highlighting. Every
serious browser-based product runs heavy compute in a worker. It is the boring, correct, ten-year-old
answer.
