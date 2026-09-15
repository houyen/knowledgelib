---
id: software/system-design/book-60-days/day-30-choosing-a-file-storage-backend
canonical_question: Choosing a File Storage Backend
aliases:
- System Design Day 30
- Choosing a File Storage Backend
- Day 30 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 30: Choosing a File Storage Backend

DAY 30 · SYSTEM DESIGN
Choosing a File Storage Backend
You're building a file upload service. 10TB of user files today. 100TB in 12 months.
Your team is having a fight.
The backend lead says: "Just use S3. Done."
The DevOps engineer says: "Mount an EBS volume. Simpler, faster."
The platform architect says: "We need EFS — multiple services need to read the same files."
The startup CTO says: "We can't afford cloud storage at scale. Self-host with MinIO."
All four have shipped this in production. All four have opinions backed by scars.
Here's the setup:
— Upload service (NestJS) receives files from mobile + web clients
— ML pipeline needs to read uploaded images for processing
— Audit service needs read access to the same files
— Files range from 5KB profile pics to 2GB video exports
— You're on AWS

---

DAY 30 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
Why A wins (S3):
One storage layer. Zero capacity planning. Every service reads from the same bucket using the S3 key
stored in your DB.
At 100TB →  ~$2,300/month. Lifecycle policies move cold files to Glacier automatically. S3 events
trigger your ML pipeline the moment a file lands. Versioning, encryption, audit logs — all built in,
zero extra work.
For greenfield cloud services, this is the default. You only deviate when you have a specific reason not
to.
