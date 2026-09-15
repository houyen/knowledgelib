---
id: computing/data-engineering/patterns/dynamic-query-design-pattern
canonical_question: How does the Dynamic Query Design Pattern construct programmatic,
  parameterized, and ad-hoc SQL queries safely?
aliases:
- dynamic query design pattern
- parameterized SQL generation
- ad-hoc querying pattern
- SQL compilation and injection prevention in pipelines
entity_type: engineering_pattern_guide
domain: computing > data-engineering > patterns
last_verified: '2026-09-15'
---

# Dynamic Query Design Pattern: Allowing for Ad-hoc Querying

Dynamic querying or ad-hoc querying your database is the primal instinct of any (data) person. Maybe the sole purpose of business intelligence and data warehouses existing is because we want to ask them questions, to get answers to update inventory or change business direction.

The dynamic query design pattern came up through writing the CEs and DEPs, something that pops up throughout the data engineering ecosystem. Whether you want to query your source database systems (OLTPs), or your enriched data marts, or your BI tool through an OLAP cube, notebooks or even agents these days, they all serve the same purpose: to serve you immediate answers to your questions.

To take a systematic approach to this problem, this pattern helps you get immediate answers to your questions and provides you with best practices to do so.

## Problem Statement

While starting within business intelligence, this yearn for answers is deeply ingrained into me. But there's one more challenge than simply answering a question, it's how to visualize it. This can be in the form of a dashboard, an Excel report, or asking a chatbot to use the terms of 2026.

But just answering the question might not be enough, as potentially a number in a chatbot doesn't show the full picture versus comparing that number by region lined out over the years. In the latter scenario, you might explore patterns you wouldn't otherwise.

Another aspect is speed. If the answers are slow, the ad-hoc might lose its appeal. This holds even more true with interactive AI-workflows where LLMs with MCP integration are querying the database or even full-blown git repositories with thousands or millions of lines of code.

But besides the challenges of how to visualize and making it fast, the question of ad-hoc and dynamically still holds true. So how do we achieve this? We need a systematic way of doing it for all systems, a map of how to do this. This is what this design pattern is all about. Dynamically and flexibly query data ad-hoc, without the need of running a full pipeline or moving lots of data beforehand.

If we don't take care of this design pattern, the impact is that we dump all data in data lakes or document stores like MongoDB where it's really hard to query data quickly. Ad-hoc is still possible, but needs a lot of untangling of JSON-trees and domain knowledge, whereas with a dynamic query design pattern we make it easy and fast to get the information we need.

## Design Considerations

This problem isn't anything entirely new, and it has occurred in BI and has been solved even beforehand with semantic layers or logical layers in SAP BO universe or Data Virtualizations that provide federation with SQL on top of your databases and data lakes. With this knowledge, we can drive the solutions towards a modern SAP BO Universe.

The requirement for fast and ad-hoc queries is driving a storage format that is quick to query from, something like an OLAP cube that returns queries in sub-seconds. As well as with modern OLAP systems, we want to define queries ad-hoc during query-time, and NOT during pre-processing or caching.

The tradeoffs are clear, we need to ingest or store the data in a format that is fast for retrieval. If possible though, we also want to minimize the amount of data engineering and ETL work, something that works autonomously with new upcoming data and data models.

```python
graph LR

    P_CachingDisk[P: Cache]
    P_ShortTerm[P: Short-term Storage]
    P_DataModeling[P: Data Modeling]
    P_Transformation_ETL[P: Business Transform]
    DP_DynamicQuerying[DP: Dynamic Querying]

    P_CachingDisk --> DP_DynamicQuerying
    P_ShortTerm --> DP_DynamicQuerying
    P_DataModeling --> DP_DynamicQuerying
    P_Transformation_ETL --> DP_DynamicQuerying
```

Looking at the data engineering patterns that are connected to this design pattern, we can get an idea of how this could look. With related data engineering patterns such as caching, short-term storage, data modeling and business transformation, we can think of solution architectures that suit these design considerations.

For a deeper understanding,

Check out the full graph with all its source CEs. To give you a broad understanding where are we coming from, these are the source CEs we are dealing with: Materialized Views, OBT, dbt table, Traditional OLAP, Modern OLAP, Semantic Layer, ODS, Data Warehouse, Message-Queue, Data Lake, CDP, Traditional ETL, Stored Procedures and Python Script.

### Querying vs. Business Logic?

What recurring problem or challenge does this design pattern address? And how is it connected to data modeling? How does one transform business domain knowledge into dynamic queries? This is also where it closely relates to design pattern Stratified Data Flow Modeling Design Pattern.

One thing is for sure, we want to avoid a rigid set of transformations defined in ETL code that needs to re-process data each time. This code and the pipelines are time-consuming to change in the process of creating insights. Finding other dimensions, or defining granularity ahead of time, it needs domain and technical people to understand the changes and implement them end to end.

With this pattern we enable a way to query ad-hoc, without any of these problems.

Looking at the source CEs, Modern OLAP System, Semantic Layers, or Data Virtualizations have solved some of these problems before. What are the convergent evolution patterns that stand out and we can use?

Some of the common patterns are querying ad-hoc, but more so, a certain cache that makes everything faster. A dedicated storage format that allows optimized and flexible queries, or has a sophisticated cache built in that autonomously updates in the best cases.

Others have called it similarly

For example, I saw John Mount calling it "flexible queries". Or, Joe Reis called it in relation to data modeling techniques: "Query-Driven Data Modeling" where Ben Rogojan and Joe discuss the continuation of Conceptual, Logical and Physical modeling with an added 4th layer called Query-Driven-Modeling. If you look at the illustration, it's a little similar to creating Data Mart for each dashboard.

### How We Model Data, Transactional vs. Master Data

Transactional Data is usually created like events with a timestamp and is immutable. On the other hand we have master data that changes over time, data like address, product details, etc. These are typically modeled as facts and dimensions.

This also has influence on how fast we can query data. Immutable events are easier to handle than changing master data as we need to update across a large data warehouse for example.

So we can say that the type of data has a big influence on how we model data, and how we fetch them fast as ad-hoc queries such as dynamic queries called in this design pattern.

### Pre-computation Vs Query-time Flexibility

Interestingly, the pendulum swing of caching inside BI workloads went from server-side caching to client-side approaches. E.g. the idea behind creating a data warehouse in the 1980s was to cache the data in an aggregated way so we could make fast business decisions. With DuckDB now we have a similar approach, but client-side.

If we look at the chronological evolution, caching approaches went from (1) Data warehouse for aggregations to (2) Materialized Views and OBT to (3) Dedicated OLAP cubes like SSAS. Later we got (4) Modern OLAP systems with optimized storage on ingest, (5) DuckDB with zero-copy layer interface, "no caching, but very fast reader for all sorts of data", and (6) RAG pipelines for AI chatbots to (7) data directly to web applications via WASM. Each of these has its own pros and cons, and in a way enables more ad-hoc querying.

Ultimately we want the simplicity of a database, but the speed of a cache or OLAP cube. This tension drives the design of dynamic query systems. Options include HTAP and Lakebase architectures, which let you query flexibly, but usually return queries slowly. For business users the sub-second interactivity is essential.

A key question is, "how do we store metrics? And where?" A metrics-first approach defines measures and dimensions as code (YAML), enabling version control and CI/CD for dashboards. But still, if we store them outside of the BI tools or the data app, different analytical tools need to implement these metrics. And for ad-hoc queries, we want to define them at query-time, meaning we do not have all metrics clearly defined, but in a structure that allows for easy on-the-fly querying.

It's the tradeoff between pre-computation and query-time flexibility as well as data freshness and query performance. Pre-computed aggregations deliver faster queries, but are rigid. Computing at query time means slower per-query, but flexible queries. In terms of freshness, more updates result in fresher data but slower queries or higher infrastructure costs.

Lastly, as a design consideration we need to choose between complexity and control as fully managed solutions are simpler but more expensive. Open-source solutions such as DuckDB + custom caching offer more control but require engineering investment and knowledge.

## Solution Architecture

So what are solutions, what's the pattern we can use to solve this issue, and get ad-hoc queries on-the-fly? Allowing us to query our metrics like revenue, profit, products, etc. on the fly.

On a high-level, we need to be able to do these three things:

1. An analytical solution that supports fast query responses with the simplicity of a database
2. Being able to model your data logically that serves as a layer between technical implementation and human/AI. Something like a Semantic Layer or Metrics Layer. Usually as facts and dimensions to be easy to use for business users and simplify complex source systems. A pre-requisite is that we can model and make changes without the need of reprocessing the warehouse or data pipelines. This allows the analytical system to optimize its cache autonomously based on the logical model.
3. We need an easy way to add new data or new measures (aggregations based on existing data).

So what's the solution, how do we integrate these three? What's the resulting solution we can use?

### Components for a Universal Analytics API

In a way we want to have a universal analytics API, that can be interfaced and easy to change with no-code for human beings and something that translates these added metrics into cached, fast returning (SQL) queries.

In 2022, before the term modern semantic layer started, I wrote about Building an Analytics API with GraphQL, which in hindsight was a solution I wanted for this pattern conceptually, but not fully fleshed out or finalized. Today, this still seems to be the use case, but how do we implement one?

Challenges then were building a no-code interface that everyone can use. On the other hand, code-first solutions are restrictive to only developers and lock out non-technical domain experts.

Usually solutions built get large pretty quickly and require multiple microservices, which creates a complex architecture with lots of bi-directional communication between different services. So a monolithic architecture gives you a simpler setup and a single API that you can interact with your various data sources through a single SQL API. It has the known disadvantages of tightly integrating into your web app.

There is the challenge of speed and the tradeoff from copying to flexibility of defining a logical layer. E.g. data virtualization gives you the flexibility in defining with tools such as Trino, Dremio, etc. These avoid the need for copying data around, but are slower. They still usually integrate with an advanced caching system for fast response times, allowing to join across multiple heterogeneous and different sources with one unified layer.

So how can we build a universal analytics API or layer? We need at least these components, and similar to Data-Asset Reusability Pattern:

- A powerful interface: No-code UI that is no-code, but produces code artefacts (YAML, extended SQL).
- Reusability: Variables & Templates so we can reuse existing business logic and parameterize easily. Avoids duplicating downstream. We need a system that works for event-based data and master, typical dimensional data, hence templates.
- Abstraction: Logical Data Model to define dimensions and metrics logically decoupled from physical storage. The API compiles these into optimized SQL at query-time. Add a new dimension without re-running any pipeline.
- Performance: Materialization & Cache to persist or pre-aggregate results to hit sub-second query targets. Autonomous cache invalidation tied to the logical model e.g. when a metric definition changes, only the affected materialization is refreshed.

```python
flowchart TB
    C(["Consumers — BI · Chatbot · Notebook · Web · Excel"])
    API(["Universal Analytics API — SQL · GraphQL · REST · MCP"])
    UI["① No-code UI<br/>Produces YAML · Extended SQL<br/>Domain experts → code artefacts"]
    TMPL["② Variables & Templates<br/>Reusable, parameterized business logic<br/>DRY across all consumers"]
    ABS["③ Logical Data Model<br/>Facts & Dims decoupled from storage<br/>YAML → optimized SQL at query-time"]
    MAT["④ Materialization & Cache<br/>Sub-second via pre-aggregation<br/>Auto-invalidates on model change"]
    S(["Storage — OLAP · Virtualization · DuckDB · Warehouse"])
    D(["Type of Data — Event-based, Master data, etc."])
	
    C --> API
    API --> UI
    API --> TMPL
    API --> ABS
    API --> MAT
    UI & TMPL & ABS & MAT --> S
	S --> D
	
    classDef pill fill:#111827,stroke:#374151,color:#9ca3af
    classDef api  fill:#1e1b4b,stroke:#6366f1,color:#e0e7ff,font-weight:bold
    classDef ui   fill:#431407,stroke:#f97316,color:#ffedd5
    classDef tmpl fill:#0c2340,stroke:#38bdf8,color:#e0f2fe
    classDef abs  fill:#2e1065,stroke:#a78bfa,color:#ede9fe
    classDef mat  fill:#052e16,stroke:#4ade80,color:#dcfce7
    class C,S,D pill
    class API api
    class UI ui
    class TMPL tmpl
    class ABS abs
    class MAT mat
```

### Components Interaction

If we think about component interactions and their relationships, we can see that we need a medium in which the dynamic queries can be created.

Based on its storage and type of source data, we need to connect and model these. The better the data modeling part, the easier to make it fast. That's where the data flow also plays a big role. In dynamic queries, usually we assume there's a pre-defined data warehouse or a structured form of data that is extracted from the source OLTP database, so we can either model them in the business entity or use the existing modeled base, both should be possible, and then define our metrics on top of it.

### SQL for Modeling Metrics

That's where SQL plays a big role for modeling and defining our metrics. The great work of Extending SQL for analytics is what we use here too.

The key to me are metrics layers that can be external but also integrated into common BI tools.  Declared declaratively with YAML to SQL conversions and vice-versa.

Today, these are also called Semantic Layer. Tools such as Cube, LookML and Malloy provide such features externally. Rill is another option that uses a metrics layer built in, but as it's plain YAML, it can easily be integrated and connected with external tools.

For the compute, we need Federated Query Engines such as Presto, Trino or Dremio, enabling querying data across multiple sources based on our ad-hoc defined queries, without moving it. Such federated query engines provide a single SQL interface to query data lakes, databases, and other storage systems, but no way to declaratively define metrics across the board.

Federated query engines are particularly useful for ad-hoc analysis where data resides in multiple locations, and we need compute to crunch our ad-hoc metric on the fly, or for caching them optimally.

The principles of federation and Data Virtualization provide the same way of centralizing metrics and avoiding moving parts, similar to our universal API layer. Tools like Apache Arrow or DuckDB can serve us here for fast in-memory transformation and responses.

Everything gets unified into SQL

As Matthias Broecheler said, that everything gets pulled back into SQL:

- MapReduce? Became Hive. Then SparkSQL.
- NoSQL? Morphed to “Not Only SQL” and then NewSQL.
- Graph? Led to pattern matching inside SQL.
- Vectors? SQL index type.
- Streaming? Enter: Flink SQL.

## Implementation Guide

So how do we implement such a dynamic query style solution that provides a unified layer to define metrics ad-hoc and have them returned immediately?

With all the design considerations and solution architecture in mind, there are different approaches you can take today. In this chapter we go through these different ones and I provide you with links and examples to implement such a system.

### Implementing Steps

What we need is to cover each component introduced. That leaves us with choosing

1. the analytical engine that gives us sub-second query response times
2. a place where you define all business metrics (not ETL), but complex calculations of your profit, or other measures.
3. a layer to logically define and update metrics, to change also at query-time

#### Choose Your OLAP Engine

Do we need an OLAP system? I'd say yes. Without one, we can define metrics on the fly, but not fast.

You could use a virtualization, but you won't get the speed. And setting up an OLAP cube or whole system is time-consuming and needs a lot of engineering knowledge? Yes, but there are also single-file OLAP cubes that work very fast such as DuckDB. So choosing the right one that suits your requirements will be key.

Options to choose the right OLAP engine for your needs depend on mostly three axes such as data scale with a range of GBs to TBs+. The deployment complexity that defines if you need an embedded, possibly simple, or an OLAP system that is either managed or needs lots of engineering to set up and tweak.

Check if they include a metrics layer or you need to build or integrate one.

We'll walk through concrete implementations later in this chapter in Examples and Use Cases.

The main advantage of choosing the right OLAP system or database is that these have an optimized storage on ingest (or can read in-line), no need to re-process after changing metrics definitions in your logical layer. The problem is that there's usually no place to put the metrics, you need to provide a system or write some glue code.

This is key for dynamic queries, you ingest once and query flexibly.

#### Define Location of Your Metrics and Its Layer

One question that always comes up, but never gets solved thoroughly, is where to store the metrics, best in a unified way. If you can define this early on, in what format, you can get great strengths from it.

Use a Metrics Layer or Semantic Layer that fits your requirements. Differentiations are usually the way of storage YAML + SQL, external or internal of your BI tools, and glue code/APIs for integrating it into your notebooks, data apps, dashboards.

Metrics SQL to create reusable, secure metric definitions. Here's an example metrics view definition with Rill

```python
type: metrics_view
model: ad_bids
security:
  access: "{{ .user.email }} NOT LIKE '%@excluded-domain.com'"
  row_filter: "{{ if not .user.admin }} publisher = '{{ .user.publisher }}' {{ end }}"
dimensions:
  - name: publisher
    expression: toUpper(publisher)
  - name: domain
    column: domain
measures:
  - name: total_records
    expression: COUNT(*)
  - name: total_revenue
    expression: SUM(revenue)
```

You see besides common definition of measures, uniquely defined in one place, and defining which dimensions work with it (similar to bus matrix that you might know from SSAS cubes), we can add additional context and conveniences.

E.g. security or creating logical constructs that are different from the physical table sources, and modeling the entities simpler in a way that makes sense to the business, and not to the database developer of the source database app.

These definitions are all very similar to other Semantic Layer definitions (e.g. Open Semantic Interchange (OSI) which tried to define a standard around semantic layers and uses the open-source MetricFlow definition). An example from theirs is:

```python
semantic_model:
  name: orders
  description: Core order data from the ERP system
  model: raw_orders
  
  entities:
    - name: order_id
      type: primary
    - name: customer_id
      type: foreign

  measures:
    - name: order_total
      expr: amount_usd
      agg: sum

  dimensions:
    - name: order_date
      type: time
      type_params:
        time_granularity: day
```

#### Choose the Right Semantic Layer

The semantic layer or metrics layer serves as a translator between various data presentation layers (BI, Notebooks, data apps) and data sources. It helps you integrate data sources, model metrics, and connect with data consumers, translating metrics into languages like SQL, REST, GraphQL or even Excel.

Choosing the right one defines key business metrics (like 'active' users or 'paying' customers) once company-wide, eliminating inconsistencies across different tools. Avoiding double implementation and work, it therefore helps the consistency across the company by a lot. These are obviously helping most if you are a large enterprise and have a lot of them. Don't use a semantic layer when you start out.

When you start out, use SQL, materialized Views, dbt, and persist all the tables. Or build your semantics in an OLAP cube or BI tool; if you only have one, no need to add an extra tool, re-check out CE chapter Materialized View vs. One Big Table (OBT) vs. dbt Table vs. Traditional OLAP Cube vs. DWA.

For choosing a semantic layer:

Check more at semantic Layer.

#### Unified API: Enable Dynamic Queries via API

One feature almost always needed, not from day one, but down the road, is having an external query to interface with your metrics layer. Be it just to list all metrics or dimensions, or get the definition of a specific measure.

Or later, even pulling data out of it, creating a federated API similar to Trino, but all around metrics and business logic. Really being ruthless in defining each measure once only, and correctly, checking with the business people and making sure they are correctly aggregated on yearly numbers for sales review meetings but also in detail to be able to drill down when needed to explore what happened on certain days.

As we are using specific Data Modeling Languages like LookML, MDX, DAX and many more, we can be very specific and precisely express exact semantics with no ambiguity. With the YAML-based approach to store metrics, we can reuse these metrics across the company, build advanced tests and automation around them, and with a REST API or similar, we can build integrations to all our apps that need to resolve business-critical data logic that is buried deep in complex SQL.

It's the tradeoff between building more complex integrations to APIs and semantic and metrics layers, but simplifying and stabilizing the business-critical metrics by defining them once, using them everywhere. Making maintainability and defining ownership much easier.

### Different Categories of Dynamic Queries

We've been exploring some tools in each category already. Here is another view of what tools and technologies make dynamic queries most useful.

- Semantic Layers: Cube, dbt Semantic Layer, MetricFlow
- Cloud OLAP: ClickHouse, Apache Druid, Apache Pinot, StarRocks
- Data Virtualization: Trino, Starburst, Dremio
- BI-as-Code: Rill, Evidence, Lightdash
- Embedded OLAP: DuckDB, chDB, SQLite with analytical extensions

### Common Pitfalls

If we look at common pitfalls, we can say first of all, don't start too early with a big complex system. Think about architecture and your company's data flow well. Basically going through the Challenges in Data Engineering that we've gone through earlier in the book.

With the day and age of AI agentic workflows, don't forget that well-defined metrics can be super valuable as context for autonomous AI approaches. As most AI implementations are lacking well-stewarded and tested data, measures and metrics in semantic layers are well tested and can be the differentiation factor for your use case. The semantic definitions provide the structured context agents need, while the SQL interface gives them a familiar, precise language to express queries without introducing hallucinations.

One common error as mentioned earlier is that you start too early with a complex system that is supposed to solve all issues and complexity at once. This is a myth, there's no such tool that solves all. Start step by step, and be aware that complexity might rise, but for a good cause of more correct business metrics in your analytics tools.

#### Performance Optimization

One challenge that remains to this day is caching your data independently and in best cases automatically. Caching means constantly duplicating data, storing it optimally, and updating data in case the source changes. Don't build your own caching system, use integrated caching features of semantic layer tools.

Cube replaced Redis with Cube Store, their bespoke caching solution built with DataFusion called Cube Store. The pre-aggregation database often became a scalability bottleneck for the analytical API. Their custom solution enabled them with sub-second query times.

### Security Considerations

Don't manually implement security, use semantic layer built-in row-level security and unified layer of authentication through the external API if you are at that stage already. Traditional SQL requires manual security implementation repeated in every query or every analytical system.

For example, Metrics SQL by Rill provides built-in security with expressions like: access: "{{ .user.email }} NOT LIKE '%@excluded-domain.com'" and row-level filtering, see above example.

## Examples and Use Cases

Let's now look at dedicated dynamic query examples, and use cases when to use them. We have looked at some dedicated tools and ways in the above implementation guide, but here we'll go more into dedicated tools and their strengths and limitations.

Each example contains a stack or tool showing the full pattern, or variation across different contexts and scales. We also look at more concrete code or configs if useful.

### ROAPI

A good example to start is ROAPI. Although it doesn't look actively maintained anymore, it's a good showcase for highlighting all the various aspects such a dynamic query project needs to cover. It was an early approach that solved all of the dynamic query pattern mentioned.

If you look at their architecture, you see they have a unified API through REST and even via Postgres protocol, which serves as a query input. They read from SaaS services such as Google Sheets or Airtable, but also from unstructured data, anything from CSV, to Parquet to relational databases. And the output is a serialized JSON or Arrow or Parquet.

ROAPI is interesting because it automatically spins up read-only APIs for static datasets without requiring you to write a single line of code. It builds on top of Apache Arrow and DataFusion, two of the very fast in-memory and on-the-fly query engines. It is mainly an in-memory engine acting as a logical layer in between source and output serialization.

Its pluggable query core design makes it possible for users to efficiently perform join queries across a diverse set of datasources from simple CSV/Parquet files in data warehouses, to MySQL/Postgres, to SaaS like Google Sheets.

What it lacks is a metrics definition layer, but it allows you to query an API server, exposing CSVs or data without writing any code.

### Metadata Store: Build Your Own. Glue between OLAP and UI

This missing metrics layer is what we have built at a previous job. We implemented a "Metadata Store" built on SQLite that was defined at build time, but would be integrated into the UI as a read-only SQLite database for predefined metrics. But within the UI, you could define additional metrics.

This metadata store we've built had the purpose of:

- Consolidate metrics among database, SmartAnalytics web app and ad-hoc queries through notebooks or modern OLAP system such as Druid that we used. It compressed all pre-defined metrics during release build to a read-only SQLite database that everyone could read. Complex business logic compressed to a single file.
- We've built a service around that database to make it easier to fetch metrics, get them as SQL statements, or get related dimensions, etc. It would also store and version the evolution of metrics over time. Each SQLite file got a version number and it was easy to jump between different versions, just swapping the one SQLite file.

Besides the common metadata that defines the columns of a row, it would also contain transformation logic that can be consumed by various executors, be that a knative function, Airflow DAG, Spark job, simple SQL query or any micro-service.

Extension to job orchestration

We extended even so far that we could define ad-hoc job orchestration, a DSL for orchestration.

### DuckDB with an OLAP Cache

Caching is a valid technique to improve performance as we've learned in the DEP Cache Pattern. In combination with a tiny and super fast OLAP database like DuckDB, this is a valid option to get the speed of dynamic queries while storing the metadata in local YAML files or directly within a local DuckDB database similar to the above Metadata Store approach where we stored all metadata in SQLite.

There are implementations that help you speed up your data queries by caching remote files locally such as QuackStore. This extension uses block-based caching to automatically store frequently accessed file portions in a local cache, dramatically reducing load times for repeated queries on the same data. I wrote more about them in a recent blog post about Simplicity of a Database, but the Speed of a Cache.

### Cube with Its Own Cache Layer

Cube is a typical semantic layer that has implemented its own cache layer Cube Store, and has multiple APIs with layers for modeling, access control, and caching. Probably showing best how to implement dynamic queries directly with a very extensive metrics layer to define KPIs and metrics.

If speed is not enough, Cube allows you to plug in any OLAP engine, data warehouse or relational database as backend.

### Cube Use Cases

- Cube provides multiple API interfaces: SQL API (Postgres-compatible), REST API, GraphQL API, DAX API (for Power BI), MDX API (for Excel via XMLA), AI API (for LLM text-to-semantic-layer queries), Google Sheets Add-on, Excel Add-in. Cube
- Cube D3 introduced: Analytics Chat (user-friendly chat for non-technical users), Workbooks (reimagined analytics workbook with AI), Data Apps (like Replit/Lovable but for data applications), Semantic Modeling (AI-powered model development). Cube
- "Now every Cube Core or Cube Cloud deployment comes with a built-in and instantly available DuckDB which has the HTTPFS extension installed and loaded by default." Cube

Cube provides multiple API interfaces: SQL API (Postgres-compatible), REST API, GraphQL API, DAX API (for Power BI), MDX API (for Excel via XMLA), AI API (for LLM text-to-semantic-layer queries), Google Sheets Add-on, Excel Add-in. Cube

Cube D3 introduced: Analytics Chat (user-friendly chat for non-technical users), Workbooks (reimagined analytics workbook with AI), Data Apps (like Replit/Lovable but for data applications), Semantic Modeling (AI-powered model development). Cube

"Now every Cube Core or Cube Cloud deployment comes with a built-in and instantly available DuckDB which has the HTTPFS extension installed and loaded by default." Cube

## Known Uses

The Dynamic Query Design Pattern is not only a theoretical construct, though I present it here for the first time. There are architectures that are close and use its patterns in previous years and decades.

For example, between 2010 and 2026, some major organizations independently converged on this pattern, each naming it differently but solving the same core problem: enabling flexible, on-the-fly metric queries without spinning up new ETL pipelines for every question.

### Google's Dremel is the origin story of the entire pattern

Google's Dremel is the foundational system that proved interactive ad-hoc querying could work at web scale. The 2010 VLDB paper demonstrated three innovations that map directly to the Dynamic Query pattern:

- A columnar storage format for nested data (reading only needed columns, dramatically reducing I/O), a multi-level execution tree borrowed from search infrastructure (root to intermediate to leaf servers scanning in parallel), and in-situ querying where data is analyzed in place on GFS/Colossus without import into a separate system.

Dremel had thousands of internal users at Google and was productized externally as BigQuery. Its architectural DNA also inspired Apache Drill, Snowflake's engine, and Databricks' Photon. The pattern variation is columnar OLAP with in-situ access + SQL interface over raw storage, eliminating ETL entirely by querying data where it lives.

### Netflix uses DataJunction to model metrics as a semantic graph

DataJunction (DJ) represents the most recent and architecturally distinctive implementation. DJ stores metric and dimension definitions as a connected semantic graph, analogous to how relational databases store view metadata, where nodes represent tables, dimensions, and metrics with rich dependency information. Its core capability is SQL parsing and SQL generation: users define metrics in SQL, DJ parses them into the graph, then generates optimized SQL targeting whatever backend is needed (Spark, Presto, or Apache Druid).

DJ exposes an API-first architecture where a single metric definition is consumable by dashboards (Netflix's internal Data Explorer backed by Druid), experimentation platforms, Superset, and ad-hoc tools. Multi-dimensional cubes are first-class features. This architecture reduced Netflix's metric onboarding time from weeks to near-trivial effort. DJ originated from an internal Facebook project (~2015, called MDF, Metrics and Dimensions Factory) and is now open source.

The pattern variation includes semantic graph layer + Druid OLAP + API-first consumption and helped Netflix find and use metric definitions across verticals (defined in DJ) and easily access, modify and experiment with new metrics across Netflix's data stack.

### Airbnb's Minerva became the canonical metrics layer

Airbnb's Minerva is perhaps the most thoroughly documented example of any of the semantic layers. Minerva maintains 12,000+ metric definitions and 4,000+ dimensions in a centralized GitHub repository using declarative YAML configurations that completely decouple business logic from physical tables.

At query time, the Minerva API receives a request specifying metrics, dimensions, and filters, then dynamically generates SQL using a "split-apply-combine" strategy, fetching atomic metric results independently from Apache Druid or Presto, joining and post-aggregating them before returning results. The API exposes a MySQL wire protocol, which means any SQL-compatible tool (Superset, Python, R, internal reporting frameworks) can consume metrics without knowing where or how data is physically stored.

### Apache Gravitino

Apache Gravitino was originally designed to provide a unified framework for metadata management across heterogeneous sources, regions, and clouds, calling it the metadata lake (or metalake).

Nowadays it evolved into a high-performance, geo-distributed, and federated metadata lake, but it still has some of the key features of a unified metadata management store with Schema Registry and Hive Metastore:

In their version 1.0 they enabled building jobs to accomplish metadata-driven actions, such as table compaction, TTL data management, and PII identification. Find more of Gravitino at GitHub, it pivoted into an open data catalog:

### Meta's Scuba processes a million ad-hoc queries per day

Meta's Scuba is the purest OLAP-first implementation of the pattern, paper from August 27, 2013. It is a distributed, in-memory database that ingests millions of rows per second and serves nearly one million queries per day at sub-second latency, storing data entirely in memory across hundreds of servers (each with 144 GB RAM). Every query aggregates data from all servers in parallel. Engineers access Scuba through Daiquery, a unified web-based notebook that serves as a single entry point to query any data source, Scuba for real-time data, Presto/Spark for the warehouse, providing a unified SQL interface that abstracts over multiple backends.

The pattern variation is in-memory OLAP engine + unified multi-backend query interface, where Daiquery acts as the semantic abstraction and Scuba provides the speed. Use cases include code regression analysis, ads revenue monitoring, and performance debugging, all without pre-built ETL pipelines.

Their next-generation system called Kraken, improvement of Scuba’s architecture, which decouples storage management from the query serving system and introduces a single, durable source of truth, described in a VLDB 2022 paper.

## Related Patterns

Complementary, alternative or related patterns that are relevant to know or can be combined.

### Complementary patterns

- Stratified Data Flow Modeling: Organizes data into layers that give Dynamic Queries a clean, stable surface to query against.
- Meta Grid by Ole Olesen-Bagneux: A broader framework for organizing metadata that complements the logical model component of this pattern.

### Alternatives

- Semantic Layer as MVC: The semantic layer maps closely to the MVC (Model View Controller) pattern and Active Record from Ruby on Rails (ORM). The model abstracts physical storage, the view exposes business-friendly representations, the controller handles query routing. Useful mental model if you're coming from software engineering. More at Exploring the Semantic Layer Through the Lens of MVC.

## Join the Discussion
