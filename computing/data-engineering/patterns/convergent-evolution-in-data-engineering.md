---
id: computing/data-engineering/patterns/convergent-evolution-in-data-engineering
canonical_question: What is convergent evolution in data engineering and why do modern
  tools reinvent older architectural solutions?
aliases:
- convergent evolution data engineering
- cyclical nature of data tools
- reinventing data patterns
- fundamental data modeling principles
entity_type: architectural_concept_guide
domain: computing > data-engineering > patterns
last_verified: '2026-09-15'
---

# Understanding Convergent Evolution

In this chapter, we'll dive into convergent evolutions and why they are relevant for this book.

## What is a Convergent Evolution?

As we have learned, flying is a convergent evolution that both the bird and the bee have known over a different evolution and different methodologies, but with the same outcome: to fly. This is the essence of convergent evolution.

Let's look at two more examples from nature: Firstly, echolocation in bats and whales, in which bats and whales evolved in entirely different environments. Yet, both have developed the ability to navigate and hunt prey using echolocation. Bats emit high-pitched sounds and hear the echoes bouncing back to them, while whales produce clicks that bounce off objects and return to their ears.

Secondly, vertebrates' and cephalopods' eyes work in opposite directions. Vertebrates, including humans, have camera eyes with a lens, retina, and optic nerve. Cephalopods, on the other side, like octopuses and squids, have similar eyes but with the retina located in front of the lens instead of behind it. Both groups evolved camera eyes independently to detect and process visual information in their environments.

Isn't that fascinating? It was to me, too, which made me realize that we have convergent evolutions everywhere, especially in data engineering.

The Opposite: Divergent Evolution

The opposite of convergent evolution is divergent evolution. On the contrary, it represents the evolutionary pattern in which species arrive at a distinct outcome over an evolutionary period. We may see that in some cases as well.

## Experience with Convergent Evolution

As a data professional with 20+ years of experience, I've repeatedly seen new terms coming up. I asked myself, are we constantly reinventing the same? As this became more prominent, I challenged myself to dig deeper and finally wrote this book.

You might have had similar experiences. You might have noticed many terms popped up through the sheer evolution and rapid growth within data engineering, and you asked yourself, too: "Haven't I heard of that before?". Whether or not you have had such experiences, you can think of such a thought as you just discovered a convergent evolution. You'd need to dig a bit to see if these terms are related and if they have the same outcome, such as flying for the bird/bee analogy, but if so, you'd have found one.

Myself, I had these experiences over and over again. While brainstorming and researching these repeated old terms, sometimes something I used ten years back, I found that these were commonly rebranded as the new shiny things. Sometimes, it was an existing technology but built additional features on top, but sometimes it needed to be improved. Also, no matter how similar or different the terms were, putting them into perspective and comparing them with older terms will help identify unique patterns that will help us navigate the field of data engineering.

## Example of a Convergent Evolution

Let's have some personal examples to make the concept more concrete.

It started with a term I used at the start of my business intelligence career in 2008, an excellent old term I used as my first advanced feature within Oracle Database, called Materialized Views (MV). A materialized view is fascinating as it stores a reasonably complex query into a physically stored table, which allows the user or the dashboard to query in seconds with the disadvantage of the need to refresh the MVs. If you fast forward to today, we are storing SQLs all the time. Have you heard of a tool called dbt? It's essentially managing your SQL in an organized matter, but to be able to use anything, you'd need to run dbt, which materializes all your tables from an SQL into a physical table that can be queried.

Another relation is the One Big Table (OBT). OBTs denormalize multiple tables into a single table with lots of columns. The same you'd do with a materialized view in a data mart layer. Some synonyms are Wide Tables and Super Table, which describe the same. There is another technique called Snapshotting, which we use often to snapshot months or days into snapshots for fast query time. These are similar to all the above terms that are trying to achieve: having a fast cache to retrieve data quickly.

So here it is: the first pattern is Caching.

If you want to take it even further, there are now new terms such as Semantic Layer, which yet again tries to have a fast query response for your BI tools but is more focused on metrics and KPIs. E.g., the tool called Cube implemented its own caching mechanism for this.

So you see, the terms are coming back. The Oracle Database first implemented materialized views in version 8i (1998). They were added later by Postgres and SQLServer. In April 2020, even Google announced April 2020 materialized views capabilities in BigQuery.

This is just an example of one convergent evolution. Hopefully, you will understand the relations we are trying to explore in this book. Since discovering these repeated terms, I see it everywhere in the data engineering field, and so might you from now on 😀 .

## Don't Fall for the Hype

Convergent evolution also helps demystify the hype. As everyone tries to create new terms, sometimes to the right and sometimes not, to create some kind of artificial hype, CEs help us to navigate beyond the hype by focusing on the patterns and the history of a term.

It's important to remember that because a term is new, doesn't mean the technology is. Some will be here in two years, some in five, and some are gone as fast as they started.

One Big Table (OBT), mainly a big denormalized table, is the same as core and data mart dimensional modeling by Kimball, published initially in February 1996, using a technique called materialization to persist.

Reverse ETL is an additional step to the existing data pipeline, or you might call it Master Data Management (MDM), where business people in typically "stewardship" add business data back to the DWH. Semantic Layers have been here since the beginning of Business Intelligence tools (called BO Universe); one could say it's also a fancy term for OLAP cubes. Highly praised, although they have existed since the beginning of BI with SSAS (MS), OBIEE (Oracle), and SAP BI/BW (SAP).

Data Mesh is another hyped term and, in some sense, another name for microservices, which we are arguing regularly between breaking out of monolithic data warehouses vs. more decentralized self-service business intelligence.

And, data contracts, haven't we validated schemas and data types all our life? 😉 A lakehouse is a data warehouse based on open standards. And there are many more we'll explore, much as the saying goes:

> Parlance evolves faster than technology.

Parlance evolves faster than technology.

Let's not get caught up in buzzwords and hype. Let's focus on understanding the technology and its capabilities rather than the name it's given. This book explores these convergent evolutions and their patterns, validating them against typical data architecture.

## The Factor Time: The Lindy Effect

We can also trust in the factor of time. All good things will stand by the time. The Lindy Effect is a good example. It says the older something is, the longer it’s likely to be around in the future. Materialized Views, ODS (Operational Data Store), and Classical Architecture of Data Warehouse are techniques I learned at the very beginning of my career, and they are still relevant to this day. But I can clearly sense that people not using or learning them today, they directly jump into implementing, or instead, reinventing a new term that is similar.

The other part, with so much information available online, it's harder to learn the fundamentals or even know which one these are, making it impossible to know all of it. Because old techniques that are still talked about today are battle-tested and likely be around for another long time, it makes sense to revisit them, learn their advantages, and combine them with today's world. Extracting powerful features and patterns. This brings us to analyze different convergent evolutions within data engineering.

The Power behind Longevity

Longevity implies a resistance to change, obsolescence, or competition, and greater odds of continued existence into the future.

If we find these common patterns that stood the test of time and survived through the old terms and can be applied universally, that will be helpful data engineering patterns, and make them even more valuable for more years to come. These findings are the data engineering design patterns that I will introduce in Part 2 in more detail.

## Let's find the Patterns behind CEs

I hope you, too, got all fascinated and want to dig into them to turn this convergent evolution into patterns and best practices. Analyzing how the different evolutions have brought up different strengths and weaknesses will help us apply.

To summarize this chapter, the identified convergent evolution terms that stood at the time of twenty years, in fact, are the data engineering design patterns. Let's next dig into the different convergent evolutions and find the patterns that will stand for many years to come.

## Join the Discussion
