---
id: software/system-design/book-60-days/day-49-controlling-data-warehouse-query-costs
canonical_question: Controlling Data-Warehouse Query Costs
aliases:
- System Design Day 49
- Controlling Data-Warehouse Query Costs
- Day 49 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 49: Controlling Data-Warehouse Query Costs



---

DAY 49 · SYSTEM DESIGN
Controlling Data-Warehouse Query Costs
Your data team just opened a $4,200 BigQuery bill.
For a single month. One analyst. 12 queries.
The queries weren't wrong. They weren't inefficient SQL. They were reasonable analytics queries — "give
me last 30 days of events for customer X." The problem was that every single one scanned the full 3.2 TB
table. No partition pruning. No cost control. Just full scans, every time.
This is the most expensive silent bug in data engineering. You write a query. It looks fast. It returns results.
And every run quietly eats through terabytes you're paying per-byte to scan.
The fix is partition strategy — but picking the wrong one doesn't just fail to help, it actively makes things
worse.
Here's the setup:
You're running a 3.2 TB events table on BigQuery. 18 months of data. Ingested daily. Analyst queries almost
always filter on two things: a date range ("last 30 days") and a customer_id ("for customer X").
Which partition + clustering strategy do you pick?
A) Partition by ingestion date — date range queries only scan the relevant day-partitions.

---

DAY 49 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
Why D wins:
Your analyst queries always filter on two columns: a date range and a customer_id. A single-key
strategy protects one and ignores the other.
Here's what D does in BigQuery:
• Partition by date →  BigQuery skips every partition outside the date range before scanning a single
row. For a "last 30 days" query on 18 months of data, you immediately eliminate ~94% of the table.
• Cluster by customer_id →  Within each scanned partition, BigQuery sorts the rows by customer_id
into storage blocks. A filter on customer_id now skips 90–95% of the remaining rows.
Combined: a "last 30 days for customer X" query goes from scanning 3.2 TB →  ~12 GB. Bill drops
from $4,200 →  ~$70/month. Same queries. Same data. Right strategy.
This pattern works across every major warehouse: BigQuery (partition + cluster), Snowflake (micro-
partitioning + cluster keys), Redshift (partition key + SORTKEY compound).
