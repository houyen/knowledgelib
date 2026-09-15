---
id: computing/data-engineering/patterns/materialized-views-obt-dbt-and-traditional-olap
canonical_question: How do Materialized Views, One Big Table (OBT), dbt Table Models,
  and Traditional OLAP cubes compare?
aliases:
- Materialized Views vs OBT
- dbt table models pattern
- One Big Table design pattern
- OLAP cubes vs modern cloud DWH
- data warehouse automation DWA
entity_type: engineering_pattern_guide
domain: computing > data-engineering > patterns
last_verified: '2026-09-15'
---

# Materialized View vs. One Big Table (OBT)  vs. dbt Table vs. Traditional OLAP Cube vs. DWA

The history of SQL.

Materialized Views is a technique to quickly persist a complex SQL query and allow quick responses for dashboards. But how is that different from One Big Table or even dbt tables? What are DWH automation tools, and what's the pattern behind them? Why are we doing it? Let's get into the details in this chapter.

```python
gantt
    title Evolution of SQL Tables
    dateFormat  YYYY-MM-DD
    axisFormat %Y

    section Materialized Views (MVs)
    %SQL         :SQL, 1970, 365d
    Oracle MV         :mv, 1998, 365d
    Google MV         :gcp_mv, 2020, 365d

    section Traditional OLAP Cubes
    SSAS                 :SSAS, 1996, 365d
    SAP BW & OLAP        :BW, 1998, 365d
    SAP HANA             :BW, 2010, 365d
    %Modern OLAP          :2013, 365d

    section Derived Tables
    Data Mart / Denormalized Table        :DM, 1990, 365d
    dbt table                 :dbt_dev, 2018, 365d
    One-Big-Table    :obt, 2021, 365d
    Wide Table      :wide_table, 2022, 365d
    Super Table      :super_table, 2022, 365d

    section Data Warehouse Automation
    BiGenius        :genius, 2011, 365d
    Qlik DWA (Attunity Compose) :qlik, 2017, 365d
	BimlFlex        :biml, 2018, 365d
    BiGenius-X        :genius, 2021, 365d
```

## Materialized View

Materialized Views (or short MVs) are what I started my career in 2008. I built data warehouses with Oracle, and MVs are still valid, though they have evolved. Similar terms have arisen, such as One Big Table, Wide Table, Super Table, Data Mart, or Snapshot. Let's compare and analyze the patterns behind them to identify the similarities and what they are distinctly doing differently.

### Definition

A materialized view is a database object containing the results of a SQL query. It might be a local copy of remotely located data, a subset of a table’s rows and columns, a join result, or a summary created using an aggregate function.

When a materialized view is executed, a potential complex SQL query is persisted in storage, enabling a fast query response for a downstream process or, in best cases, a dashboard or app.

#### How do Materialized Views work?

A materialized view is a simple technology that caches a SQL query to a disk. This is most effective as an SQL query can get hugely complex and, therefore, lengthy execution. Depending on the execution plan and what the query optimizer calculates, it can vary. We can mitigate this problem by storing the table on disk.

dbt, for example, is very popular this day; why? They do that, plus you can stack multiple materialized views and run them in order; more on that later when we talk about patterns.

That's it; that's how MVs work and the beauty of their simplified approach. Of course, there is much more behind the curtains, such as refresh types, different triggers, etc. But all of it is technology-specific and built towards the same goal of persisting a query to disk for faster query time.

An example in an Oracle database of how you can perform a complete refresh of materialized view with PL-SQL:

```python
exec dbms_mview.refresh(‘DEDP_MV’);
```

Or with plain SQL:

```python
BEGIN
   dbms_mview.refresh(‘DEDP_MV’, method => ‘C’);
END;
/
```

### History & Evolution

The Oracle Database first implemented materialized views in version 8i (1998). They were added later by Postgres and SQLServer.

In April 2020, 22 years later, Google announced materialized views capabilities in BigQuery. Google's Materialized views over BigLake metadata cache-enabled tables can reference structured data stored in cloud storage. These materialized views function like materialized views over BigQuery-managed storage tables, including the benefits of automatic refresh and intelligent tuning.

So there you have it, after so many years, and the technique is still newly announced today. There must be a vigorous pattern to materialize views that we can use.

History of SQL

SQL -> Data Mart -> Materialized View -> BI Report -> Traditional OLAP -> BI Dashboard -> Modern OLAP -> dbt tables -> One Big/Wide/Super Table -> Semantic Layer -> Natural Language Queries

### Core Concepts

A materialized view materialized SQL queries to disk. When a materialized view is executed, the SQL query is persisted in storage, enabling a fast query response.

Instead of recalculating the query each time it's needed, materialized views deliver pre-computed data, speeding up data access. Especially for large datasets or complex joins or aggregations—bridging between storage efficiency and query performance.

Materialized views follow the compute-once-read-many-times principle, balancing the load between read-and-write operations.

## Traditional OLAP Cube

Next, we have traditional OLAP Cubes. Compared to the previous chapter, where we discussed Modern OLAP Cubes, let's see what traditional means here.

### Definition

Traditional OLAP cubes represent the early form of Online Analytical Processing tools, characterized by their structured, multidimensional data storage approach.

These cubes allow for the efficient organization and querying of data along multiple dimensions, providing an interface for complex analytical queries. They are an optimized storage mechanism, significantly reducing the time to access pre-calculated data summaries across various dimensions.

### History & Evolution

Traditional OLAP cubes, like Microsoft's SQL Server Analysis Services (SSAS) and SAP's Business Warehouse (BW) cubes, emerged as pivotal tools for business intelligence in the late 1990s and early 2000s. Microsoft introduced SSAS as part of its SQL Server platform in 1998, revolutionizing how businesses interacted with and analyzed large volumes of data. These tools offered a way to pre-aggregate data, enabling rapid querying and analysis, a stark contrast to the row-based storage of traditional databases.

The evolution of OLAP cubes favored handling increasingly complex data sets, evolving from simple structures to more sophisticated, high-dimensional models. This advancement grew the business intelligence domain and data warehousing, reflecting the increasing demand for fast, efficient data processing tools and later dashboards in a data-driven business environment.

### Core Concepts

Pre-calculation of defined metrics. Ahead of time, company-wide metrics are defined within the cube, allowing it to preprocess all critical metrics on schedule, mainly after the data warehouse has run.

Sub-second responses. Optimized for business user drilling and filtering on a dashboard, traditional OLAP Cubes (as well as modern) provide super fast response time as everything is pre-processed. As you define dimensions that a measure can be filtered on ahead of time, the many possible queries are mostly calculated.

#### Growth and Cardinality

A core concept is handling the sheer number of possible combinations.

Let's say we model dimensions in a dimensional model. Each dimension, its columns, and its cardinality (a certain number of unique values) adds many combinations. Imagine you have three dimensions with each column; time might have 12 values (months), location might have ten values (different stores), and the product category might have five values.

The total number of combinations possible with these three dimensions is the product of their cardinalities. It would be 12 (time) × 10 (location) × 5 (product category) = 600 possible combinations. Imagine adding multiple columns and 100s of dimensions.  To clarify, we had 12 × 10 = 120 combinations before adding the product category. After adding one more, we have 480 more combinations.

That's why a traditional OLAP cube will reach its limitation; the bottleneck is the pre-calculation time that can't be done in a reasonable time (overnight) anymore.

Adding Many-to-Many Relationships to the mix, its complexity grows as a measure can relate to a dimension through other Bridge Tables, leading to more potential combinations. The exact growth pattern depends on the specific structure and cardinality of your cube's dimensions and measures.

## dbt Table

Another way of materializing an SQL statement that is highly used is dbt and its tables.

### Definition

A dbt table is a persisted SQL statement too. You define all tables within dbt and their relations to previous tables or advanced logic can be applied with Jinja Template.

Once you run dbt, it persists each SQL query into a physical table. There are different flavors; you can use dbt-duckdb or snowflake to persist in different technologies, but the key is that it will store data on disk after it's done.

### History & Evolution

dbt started from a small consultancy firm. It started at RJMetrics in 2016 but took off later in 2018 when Fishtown Analytics became more publicly visible, and the market was more ready for it. Later, it renamed itself to dbt Labs.

With a strong focus on community and releasing the code into the open, it grew fast in 2020. Many companies across the globe adopted the small CLI tool due to its simplicity and significantly enhancing features and capabilities.

With it, the concept of "analytics engineering" started to spread. Business people were not only BAs any longer; if they knew a little bit of coding, they could apply a small set of software engineering best practices to analytics code. This philosophy helped the growth, encouraging a more structured, maintainable, and collaborative approach to building SQL pipelines.

### Core Concepts

Enhancement of plain SQL. dbt tables are persisted SQLs on steroids.

#### Why dbt? Data Modeling with SQL

dbt has gained immense popularity and is the facto standard for working with SQL. SQL is the most used language besides Python for data engineers, as it is declarative and easy to learn the basics, and many business analysts or people working with Excel or similar tools might know a little already.

The declarative approach is handy as you only define the what, the SQL statement, your database, and the query optimizer handles the rest.

#### Downside of SQL

But let's face it: SQL also has its downside. If you have worked extensively with SQL, you know the spaghetti code that usually happens when using it. It's an issue because of the repeatability—no variable we can set and reuse in an SQL, no lineage graph, no data lineage.

#### The Power of dbt and Its Tables

dbt helps us with all that, decoupling SQL queries from storage and making them re-useable, relatable, schedulable, testable, and many more.

We can create these dependencies within SQL. You can declaratively build on each query, and you'll get errors if one changes but not the dependent one. You get a lineage graph and unit tests. It's added software engineering practice that we stitch on top of SQL engineering.

Warning

It's easy to build dbt tables and model them; we need to govern it so we won't end up with thousands of tables. As you will get many errors checked by the pre-compiling dbt,  good data modeling techniques are still needed and essential to succeed.

## One Big Table (OBT)

One Big Table, OBT, is another technique that came up recently to store data more efficiently data retrieval.

### Definition

One Big Table is one of the data modeling techniques that came with so-called big data and the boom of cloud platforms. It represents a wide table with many columns.

Synonyms, and Nothing New

The OBT technique is nothing new; at the start of my career, we built data marts with materialized views, and we used it in similar ways as OBT today.

They are very similar to initially discussed MVs and to data marts, Wide Tables, Super Table, Snapshots, or just any denormalized table.

Usually compared to fact tables and dimensions, it's a denormalized table containing all dimensions within the granularity needed for the use case with many duplicated dimension entries. For example, dimensions such as geography or customer will be repeated compared to a normalized table in a typical relational database fashion, e.g. Third Normal Form (3NF), where we'd model foreign keys to all the dimensions.

An OBT can contain hundreds of columns unlike relational, where you would normalize into new tables. With its columnar-oriented architecture, it's easy to add new columns and achieve Schema Evolution as there's zero cost. It is more of a metadata update, compared to expensive DDL in non-columnar formats. OBT can include nested format (Struct, Arrays, JSON) as well and is suitable for streaming as the structure is fixed, as we can do with modern OLAP cubes.

One big table is on the very right end of normalization as illustrated below:

Illustrating normalization vs denormalization | Source

With storing lots of data being a solved problem and getting cheaper with S3 and other places, OBTs ease up queries without the need of joining, which also makes much faster response time, even for long tables as most storage formats are columnar these days, meaning querying only what we need instead doing a full table scan on more traditional databases.

The downside is lots of management around creating and updating these tables. Changing dimensions (renaming of product, relocation of a customer) needs an update to many rows. We are backfilling new dimensional attributes.

Luckily, many of these challenges got easier with the latest Data Lake Table Formats; read more in The Underlying Patterns.

#### High-Quality Data Products

OBT, wide table, super table, or even materialized views can help build high-quality data products as it's easier to define formal ownership or commitments. That's also where the relation to data marts comes in, data marts. Data marts are the key to efficiently transforming information into insights in a data warehouse.

It is a spectrum from developers who build the application to the business domain experts. Therefore, the data marts, OBTs, and other synonyms are very close to the business. They are making applying data governance or defining service level agreements (SLAs) easier.

OBT also combines various tables into one big denormalized table, optimized for one business unit, simplifying analytical queries with dashboards or discovering data for non-technical users.

Due to the focus on data products, some even say it's integrating well with Data Mesh. Data Mesh uses data-as-a-product as a core principle. With the mentioned governance, high quality, and well-defined ownership, OBT plays well with the principles of decentralized resources.

#### Pros and Cons

It simplifies querying by reducing the need for multiple joins and enhancing query response time with a wide table of pre-persisted columns without joins.

On the other hand, challenges arise in changing dimensions or columns as they are repeated, and it's hard to keep them consistent across various OBTs or even within one.

Adding new dimensional attributes requires backfilling. If not, a Data Lake Table Format is used.

### History & Evolution

The term "One Big Table" (OBT) doesn't seem to have a single point of origin. This means it either came up from the natural language to make one big table, therefore also the close connection to existing terms, or someone tried to create a new marketing term. I initially found the first appearance in 2021 and later in 2022.

But it might have come from BigQuery with its insufficient joining capabilities. Google suggests people put everything in one big table1:

February 2028, Josh Andrews, dbt Slack

I haven’t looked at Bigquery in a while. Still, when I spoke to the Google team a couple of years ago about building a “true” data warehouse with facts and dimensions and asked for their recommendations about data modeling, they said essentially, “Just denormalize everything and put it in one big table” 2.

From there, it might have been a common term used in the community for the denormalized or wide table or even "Super Table". On the other hand, Super Table has been announced and will probably be introduced here in 2022. If you have more information about the origin, I'd be happy to hear from you.

### Core Concepts

The One Big Table approach, or OBT, represents a shift towards wide, denormalized models. The core ideas here are that storage is inexpensive, allowing for broad tables, and modern cloud databases have such robust computational capabilities that they can efficiently handle these extensive models.

This approach streamlines the process, moving data directly from staging to the final reporting mart without intermediate layers. However, this efficiency can come at a cost. Complex queries and extensive business logic can drive up computational expenses, particularly in large-scale enterprises.

Additionally, this model can lead to data redundancy and an over-reliance on source systems, limiting flexibility in data modeling. It's crucial to strategize the modeling of each layer to avoid data overload and maintain control over your pipelines.

A core feature is Schema Evolution. Easy to add columns, zero cost, only a metadata update, compared to expensive DDL in non-columnar formats.

OBT included nested format (Struct, Arrays, JSON). It's suitable for streaming as the structure is fixed, as modern OLAP cubes like Druid and ClickHouse also make heavy use of uses.

In summary, while OBT offers quick setup and operational simplicity, it requires careful consideration of computational costs and strategic data modeling to avoid scalability issues and data management complexities.

## Data Warehouse Automaton

Data Warehouse Automation, or short DWA, is a way to automate data warehouse builds.

### Definition

Data Warehouse Automation is an innovative technology approach that simplifies data warehouse design, development, deployment, and operation. It leverages templates, metadata, and design patterns to automate tedious, time-consuming tasks. This automation covers various aspects of data warehousing, from data modeling and ETL processes to documentation and testing. The goal is to accelerate development cycles, improve accuracy, and enhance the agility of data warehousing initiatives, which is closely tied to the growth of big data.

### History & Evolution

Data warehouse automation tries to innovate along the 1986 old architecture of data warehouses, which started around the early 2000s. Before the big data era, it needed to be faster to serve business needs by doing it the traditional way. The idea was that data warehouses do not go away but must be optimized. That's when the data warehouse tools started popping up, and they are still here today, although we hear them as loud as the Modern Data Stack or others.

But why is this? Traditional data warehousing processes were labor-intensive and error-prone, involving extensive hand-coding and manual tasks. The DWA tools brought a paradigm shift, focusing on generating much of the required code and documentation automatically. This shift reduced the time needed to build and maintain data warehouses, allowing for more consistent and reliable outcomes.

As businesses seek faster cycles and more efficient ways to manage large volumes of data, the role of DWA is still relevant today. Embracing DWA means moving towards a more strategic approach to data management due to its tool partner. The focus shifts from mundane, repetitive tasks to fast data analysis and business intelligence.

#### The Challenges of DWAs

Despite its advantages, DWA has its challenges.

1. Losing Control: There's a common fear of losing control over the code produced by DWA tools. However, many tools offer customizable templates, allowing control over the generated code.
2. Vendor Lock-in: Concerns about being tied to a specific vendor's technology are valid. Choosing a DWA tool that offers flexibility and openness can mitigate this risk.
3. Skill Requirements: DWA tools require a different skill set than traditional data warehousing. There's a learning curve, but the benefits of faster and more consistent delivery outweigh the initial investment in learning.
4. License Fees: Cost is a significant factor. However, various options, including open-source tools, cater to different budgetary requirements.
5. Emotional Resistance: The shift to automation can be met with resistance due to fears of redundancy or change. However, embracing these tools can lead to more engaging and strategic roles for developers.

#### The DWA Tools

Below is a non-complete list of Data Warehouse Automation tools in alphabetical order.

- biGENIUS-X: Easily design, build, and maintain any modern analytical data solution with advanced data automation, no matter the data management approach you choose.
- BimlFlex: A collection of templates, metadata definitions, and tooling enables you to build an end-to-end data solution without writing a single line of code.
- Qlik® Data Warehouse Automation (before Attunity Compose)
- TimeXtender: Metadata-driven automation software designed to fully automate the creation, maintenance, and operation of Discovery Hub®, as well as modern and enterprise data warehouses.
- WhereScape RED: Design, planning, and automation to cut the development life cycle of data warehouse projects by 80%.

Check out the DWA Guide for a complete list.

### Core Concepts

The core is automation, as the name reveals already. It uses templates to build a fast, non-repetitive data warehouse and its data marts.

Data warehouse automation tries to innovate along the data warehouse architecture. Building and modeling are still manual, so DWAs try to automate as much as possible along the process, leaving you to focus on the business knowledge and modeling it appropriately.

In conclusion, Data Warehouse Automation significantly improves data management technology but has some challenges. The tools empower and enable businesses to be more agile and responsive to their data needs.

## The Underlying Patterns

In this chapter, we'll analyze the patterns behind the similar convergent evolution terms of a materialized view, traditional OLAP cube, dbt table, or One Big Table, also a synonym for the wide or super table.

We have seen that these terms are sometimes hard to keep apart. Let's repeat the unique characteristics of each CE:

- Materialized View: Persist complex SQL queries into a fast queryable table.
- Traditional OLAP Cube: Pre-calculated metrics, allowing sub-second response time.
- dbt Table: Enhancing SQL with DRY principles with macros and templating, stacking them together, and visualizing the lineage.
- One Big Table: A methodology to use the computing power of cloud platforms and join multiple tables in a single, easily maintainable, and queryable table.
- Data Warehouse Automation: Innovate the data warehouse lifecycle with automation and templating.

Let's focus on the patterns they share next.

### Patterns (or Commonalities)

The common patterns and similarities I found among these convergent evolutions are:

- A common thread is to persist complex SQL queries into a table, abstracting business logic and making it readily available with added modeling techniques.
- Persisting to a physical table is effective caching, which almost all above CE do.
- Reusability to either reuse business logic or SQL queries that can be stacked together.
- We are capturing business transformation and business value within an easily accessible format.

All of it is a perception of the evolution of SQL, with SQL at the heart of each convergent evolution.

### Differences

Besides the commonalities, the differences are nuanced.

OBT and traditional OLAP cubes are modeling techniques, whereas materialized views and dbt tables are a technology or a way to apply such a technique.

Also, traditional cubes need software to edit and model the dimensions, facts, and bus matrix, whereas an MV and OBT only need SQL. An MV needs a database for it to work. dbt is similar to a traditional cube that needs software, but debt has an indifferent open core model where the framework is open source.

The cache of an SSAS cube is in a proprietary format, as a dbt table or an MV persisting in a native database table. But as an advantage, they also cache much more than simply the state of the table. An OLAP cube is more adaptable to query as you can add or remove dimensions and slice-and-dice where a dbt table or MV holds one single granularity and state.

## Key DE Patterns: Cache, Business Transformation, Reusability

Three patterns consistently emerge across convergent evolutions: the ability to store state and persisting data in cache that allows rapid retrieval.  Help with business logic and transformation that is easiest done in SQL and the reusability case, to use templates to develop complex queries or reuse a dedicated state for fast retrieval.

```python
graph LR

	P_Transformation[P: Business Transformation]
    P_CachingDisk[P: Cache]
    P_Reusability[P: Reusability]
	CE_DWA[CE: Data Warehouse Automation]

    CE_MV[CE: MV]
    CE_OBT[CE: OBT]
	CE_dbt[CE: dbt table]
    CE_TraditionalOLAP[CE: Traditional OLAP System]

    CE_OBT --> P_CachingDisk

    CE_MV --> P_CachingDisk
    CE_MV --> P_Transformation
    CE_dbt --> P_Transformation
    CE_OBT --> P_Transformation

	CE_dbt --> P_Reusability

	CE_TraditionalOLAP --> P_CachingDisk
	CE_dbt --> P_CachingDisk
	CE_DWA --> P_Reusability
```

### Cache

We've already discussed cache as a pattern in the previous chapter.

### Business Transformation

With complex data transformation and various business logic, we store state, essentially persistent business value, unlike caching, where we store short-term states only.

There is usually a lot at stake in the business transformation, as it's where you need the domain expert to automate the complex finance process or the supply change. But once mastered, data engineering brings the most value to the business.

### Reusability

A lot can be achieved Through reusability, templating, reusing SQL, or following the DRY principles. As SQL has limitations, this is where tools like dbt can lift SQL and give it superpowers.

As we can reuse and stack different transformations together, we also get extra features like testing, documentation, version control, and others that wouldn't be possible without templates and a code-first approach.

## Wrapping Up

An interesting pattern could be Open Table Format, which would use some of this pattern and apply it with a certain technology.

Besides, this was only a summary of these patterns. We'll continue to go in-depth with these patterns in Chapter Four: Caching, Business Transformation, and Reusability, resulting in its data engineering design patterns in Chapter 5: DEDP.

## Join the Discussion

1. Thanks, Edo, for pointing that out. ↩
2. Also see what Bora Beran has to say, Bigtable Product Lead at Google.  ↩

Thanks, Edo, for pointing that out. ↩

Also see what Bora Beran has to say, Bigtable Product Lead at Google.  ↩
