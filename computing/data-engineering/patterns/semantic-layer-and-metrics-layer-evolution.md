---
id: computing/data-engineering/patterns/semantic-layer-and-metrics-layer-evolution
canonical_question: What is the Semantic Layer (Metrics Layer) in data engineering
  and how does it prevent fragmented business metric definitions?
aliases:
- semantic layer data engineering
- metrics layer pattern
- business intelligence semantic model
- Cube dbt Semantic Layer
- single source of truth metrics
entity_type: engineering_pattern_guide
domain: computing > data-engineering > patterns
last_verified: '2026-09-15'
---

# Business Intelligence, Semantic Layer, Modern OLAP, Data Virtualization

The history of semantic SQL.

In business intelligence (BI), we have been doing reports for a long. But what's the pattern behind BI? How is the semantic layer similar to BI? Is there a typical pattern behind these two? Let's figure out in this chapter.

Let's start with the visual evolution of the terms we compare in this chapter and some highlights[^note1]:

```python
gantt
    title Evolution Semantic SQL
    dateFormat  YYYY
	axisFormat %Y
    %excludes 2000, 2001, 2002, 2003, 2004, 2005

    section Business Intelligence Reports/Dashboard
    SAP BO                  :done,    des1, 1991, 365d
    SSRS                    :done,    des14, 2004, 365d
    Maturing BI tools       :active,  des2, 2016, 365d
    Looker (LookML)         :done,    des3, 2019, 365d
    Rill Data               :done,    des3, 2022, 365d

    section Semantic Layer
    SAP BO Universe         :done,       des1, 1991, 365d
    MDM                     :active,     des4, 2008, 365d
	Oracle BI (OBIEE / Siebel) :done,       desc15, 1999, 365d
    Kimball Concept SL      :done,       des5, 2016, 365d
    dbt Jinja templates     :done,       des12, 2018, 365d
    Modern SL               :milestone,  m2, 2022, 365d

    section Modern OLAP
    Druid                   :done,   des6, 2012, 365d
    Pinot                   :done,   des7, 2014, 365d
    ClickHouse              :done,   des8, 2014, 365d
    DuckDB                  :done,   des19, 2019, 365d

    section Data Virtualization
    Dremio                  :done,  des11, 2017, 365d
    %TIBCO                   :done,  des16, 20XX, 365d
    %Denodo                  :done,  des17, 20XX, 365d
    Presto/Trino            :done,  des18, 2013, 365d
```

Dates used in the Gantt diagram are picked from Wikipedia

## Business Intelligence Dashboard / Report

Let's start with business intelligence and its product, dashboard, and reports.

### Definition

Business intelligence should produce a simple business overview, boost efficiency, and automate repetitive tasks across your organization. In more detail:

- Roll-up capability - (data) visualization over the most important KPIs (aggregations) - like an airplane cockpit, gives you the essential information at one glance.
- Drill-down possibilities - from the above high-level overview, drill down into the very details to figure out why something is not performing as planned. Slice and dice or pivot your data from different angles.
- Single source of truth - instead of multiple spreadsheets or other tools with different numbers, the process is automated and done for all unified. Employees can talk about business problems instead of the various numbers everyone has. Reporting, budgeting, and forecasting are automatically updated consistently, accurately, and promptly.
- Empower users: The so-called self-service BI allows users to analyze their data instead of only BI or IT persons.

### History & Evolution

If you have been in the industry for a while, you know the most common BI Tools, such as Tableau, Click, and many others. In the old days, we built reports with SSRS, Oracle OBIEE, etc.

But the hard work was always behind the scenes to build a fast, interactive cube, where you can slice and dice by known entities of your business. Usually, the data was presented in a star schema with facts and dimensions, where the dashboard or BI layer joined them dynamically inside the tool based on the dimensions and measures you chose.

The need for more transparency and the long time it took to integrate additional sources, besides other problems of BI, brought out more modern BI tools. Today, these tools are more declarative as the trends go, lighter, and narrow to a dedicated use case. More thoughts are brought into creating Measures and KPIs, making them available outside of the BI tools only.

### Core Concepts

A report or a dashboard, at its very core, is a visualization of data. The whole process, from raw to clean and valuable data, is invisible if you're not a data person. The only way to showcase that data is via a visualization tool.

Another concept is to describe the company's success in numbers. Most commonly known as KPIs or measures.

## Semantic Layer

Much later, in 2021, the modern semantic layer came out with the synonym Headless BI. A sub-layer of the semantic layer is also called the Metrics Layer. But with that out of the way, let's dive into the definition, history, and core concepts.

### Definition

A Semantic Layer is a logical translation layer between your data and your business users. It converts complex data into understandable business concepts:

> A semantic layer calculates complex business metrics at query time. It sits between your data sources/transformation layer and your analytics tools. You define a metric’s aggregations (daily, weekly, monthly, and quarterly) and dimensions (region, customer, product). Examples of metrics could be “monthly active users”, “weekly revenue”, “number of paying customers”, and so on.

A semantic layer calculates complex business metrics at query time. It sits between your data sources/transformation layer and your analytics tools. You define a metric’s aggregations (daily, weekly, monthly, and quarterly) and dimensions (region, customer, product). Examples of metrics could be “monthly active users”, “weekly revenue”, “number of paying customers”, and so on.

For example, your database may store millions of sales receipts containing information such as sale amount, location, time of sale, etc. However, your business users may need more technical capabilities to convert raw data into actionable insights such as revenue per store, which brand is most popular, etc. By translating business terms into a format understood by the underlying database, the Semantic Layer allows business users to access data using terms they are familiar with.

A semantic layer is a translation between any data presentation layer (Business Intelligence, notebooks, data apps) and the data sources. A translation layer includes many features, such as integrating data sources, modeling the metrics, and integrating with the data consumers by translating metrics into SQL, REST, or GraphQL.

Also, keep in mind that there are nuanced different types of semantic layer:

- Thin: Do small renaming and add some aggregations.
- Thick: This is on top of the OLTP or the physical tables, including the transformation logic.

### History & Evolution

The semantic layer is not something entirely new. The concept has existed since 1991, when Business Object patented it. As an early business intelligence engineer, I used lots of BI tools. I was always impressed by the BO universe and how you could abstract complex queries and models away from the business users and design them to their understanding of the world.

Designing a Semantic Layer in SAP BusinessObjects Universe Designer  | Source: YouTube

The primary or critical component of business intelligence was always a semantic layer. It allowed an abstraction or translation from technical terms to business terms, such as facts and dimensions, and mapped it to more understandable models for the business. But it was always part of the BI Tools or the query or reporting layer.

Later, when we had OLAP Cubes, such as the famous SSAS one, they also had their semantic layer called data source view or cube structure, where you defined relations, measures, dimensions, and calculated measures. Also, remember the famous Bus Matrix, where you define measures to their dimensions.

SSAS Dimensions and Cube Basics | Source: Exsilio Blog

The SAP BO Universe was a semantic layer that closed the gap between technology and business with an intermediate layer. You could define logical objects on top of physical ones, basically CTE at query time. Similar but not a semantic layer, Master Data Management (MDM) came up later and tried to ensure master data (e.g., customer, product, address) was consistent, accurate, and maintained once with semantic consistency. It was giving accountability with stewardship to the business users. I used MDM’s most popular tool  SQL Master Data Services (MDS) by Microsoft, which was announced in 2008 and updated last in 2015.

Around the same time (July 2008) as MDS was announced, another tool called Jinja Template was released for the first time. It is not a semantic layer but helps define complex business logic within Python or SQL code. The Jinja template didn’t get much popularity inside the data world until dbt was announced and used heavily to mitigate the downside of SQL, creating complex models. dbt was initially started at RJMetrics in 2016 but took off later in 2018 when Fishtown Analytics (now called dbt Labs) more publicly showed it, and the market was more ready for it.

People built huge semantic business layers on top of dbt and Jinja templates but lacked many features, such as ad-hoc definition and a declarative approach–dbt is imperative. You need to run a dbt run to get anything.

Besides other BI tools having similar modeling language to define metrics, Looker, with its LookML language, popularized the modern semantic layer methodology. It wasn’t called such, but people saw its benefit and used Looker heavily. Later, when data grew exponentially and companies didn’t use a single BI tool any longer, the need for transferring these metrics and calculated business logic to other tools such as Notebooks and Excel sheets grew.

In 2021, the “new" modern semantic layer rose in popularity with tools MetriQL, Minerva by Airbnb, MetricFlow, Supergrain, or Cube.

The Evolution of the Semantic Layer Chronological

- 1991: SAP BusinessObjects Universe and BI semantic layer
- 2008: Master Data Management (MDM) (with MDS from Microsoft in 2008)
- 2010: Oracle BI / Siebel had its first semantic layer
- 2013: Kimball discussed the concept of a semantic layer in #158 Making Sense of the Semantic Layer
- 2016: Maturing BI tools with an integrated semantic layer, such as Tableau, TARGIT, PowerBI, Apache Superset, etc., have their own metrics layer definition
- 2018: Jinja templates and dbt eroding the transformation layer into a semantic layer
- 2019: Looker and LookML popularized as the first real semantic layer
- 2022: Modern Semantic Layer, Metric Layer or Headless BI tools such as MetriQL, MetricFlow, Minerva, dbt arose with the explosion of data tools (BI tools, notebooks, spreadsheets, machine learning models, data apps, reverse ETL, …) {{</ admonition >}}

Semantic Layer and its relation to MVC pattern

The concept of a Semantic Layer shares similarities with the MVC (Model-View-Controller) model, particularly as popularized by Ruby on Rails through its Active Record pattern. In a conversation with Artyom Keydunov & Pavel Tiunov from Cube.dev, Artyom drew parallels between the two:

- Just as the MVC model focuses on decoupling data, the Cube Semantic Layer serves a similar purpose. In Cube, this decoupling is evident in how they create views akin to database views while the model and component handle the rest.
- The Semantic Layer can be likened to the Active Record in Ruby on Rails. Active Record is an implementation of the ORM (Object-Relational Mapping) pattern, which abstracts and simplifies database interactions. Similarly, the Semantic Layer abstracts complex data structures, making them more understandable and accessible to business users.
- At its core, the Semantic Layer represents the Logical Data Model in Data Modeling, serving as an intermediary between raw data and its representation to end-users.

This comparison underscores the universality of certain design patterns across different domains and technologies. Whether web development with Ruby on Rails or data engineering with tools like Cube, the principles of abstraction, simplification, and decoupling remain consistent.

### Core Concepts

The core of the semantic layers is a map from the metrics to the physical tables. Think of a menu in the restaurant; you order the menu, but you need to know how it's made.

It also builds strong capabilities on top of your business logic, such as having a SQL, REST, and GraphQL interface out of the box, making it easy to integrate (BI tools, notebook, or web app) into your data landscape and querying important company-wide metrics from a single source of truth through that API. It's a wrapper to write your complex business logic and metrics in a single place, declaratively and open for everyone to see.

Flexibility is another strength. You start without building a complex physical model and create a query immediately. Additionally, sync your metrics into multiple BI tools out of the box.

If you want to read more on the semantic layer, I wrote very detailed in The Rise of the Semantic Layer.

## Modern OLAP Systems

Let's check what OLAP systems were evolving over time, and why I calling them modern.

### Definition

I call the next generation of OLAP after SSAS, like Druid, Pinot, ClickHouse, and Kylin, the modern OLAP systems. Because these handle business logic at query time versus the traditional OLAP cubes such as SSAS, which had to be pre-processed and do not handle big data or even streaming.

Generally, OLAP is an acronym for Online Analytical Processing. OLAP performs multidimensional business data analysis and provides complex calculations, trend analysis, and sophisticated data modeling capability. An OLAP Cube is a multidimensional database optimized for data warehouse and online analytical processing (OLAP) applications.  An OLAP cube is a method of storing data in a multidimensional form, generally for reporting purposes. In OLAP cubes, data (measures) are categorized by dimensions.

### History & Evolution

The history between more modern OLAP systems and traditional OLAP cubes is exciting and vital.

The personified traditional OLAP cube is SSAS. It's still used today and is the rising star of OLAP cubes. SSAS, developed in the late 1990s, came with a query language known as multidimensional expressions (MDX) to query and perform analyses.

These traditional cubes had the advantage that they were processed ahead of time, and most used queries were cached ahead of time. This also had the disadvantage that you couldn't quickly change measures on the fly. Instead, you had to go into the solution, alter or add the measure, redeploy the solution in production, and reprocess the whole cube.

The modern cubes and OLAP systems took a different approach. These have the advantage that they define queries and measures at query time and do not need to pre-process the whole cube. That's why I am talking in this chapter about more modern OLAP systems, as these are close to what we are talking about in this chapter.

Modern OLAP technologies like Apache Druid, Apache Pinot, or ClickHouse are extensive. It is best suited for a customer-facing or sub-second experience that a cloud data warehouse will never achieve.

OLAP cubes are dead! Long live OLAP cubes.

Modern OLAP systems are very similar to semantic layers with cache functionality. A semantic layer is, to an extent, an OLAP cube with extended features such as access permission, API layer, and data modeling included. Some even coined yet another term, called Personalized API.  I myself called it Analytics API at the beginning of 2022. Let's wait until vector databases are also just called OLAP cubes :).

### Core Concepts

But why do we even use OLAP cubes? As we have a transactional source system (OLTP), and we need to make historical analytics on the fly, usually querying the DWH or even the source database directly with aggregated SQLs like SUM(), COUNT(), etc., is fine for one-time analysis. But for business and operational users who want to slice and dice the data with a BI tool, we need (sub-) seconds response time. That's where the OLAP cubes come into play, as they usually know about predefined dimensions and facts and can, therefore, reply quickly to the user's request.

Another newer concept of OLAP cubes, especially modern OLAP systems, is querying real-time data. For example, Apache Druid can sink data from a batch or a stream to the same cube.

## Data Virtualizations / Data Federation

Data virtualization, also called federated queries, is the next convergent evolution we look at.

### Definition

Data Virtualizations help you when you have many source systems from different technologies. Still, all of them are relatively fast in response time, and if you run a few operational applications, you might consider Data Virtualization. In that way, you don't move and copy data around and pre-aggregate. Still, you have a "Semantic Layer" where you create your business models (like cubes), and only if you query this data virtualization layer does it query the data source. If you use, e.g., Dremio, you use open-source technology such as Apache Arrow, which will cache and optimize a lot of in-memory for you that you have as well astonishing fast response times.

Data virtualization can be an alternative to fighting against data inconsistencies and investing in data governance costs. Other reasons for data virtualization include rapid prototyping for batch data movement, self-service analytics via a virtual sandbox, and regulatory constraints on moving data.

### History & Evolution

Several tools made data virtualization 1.0 famous, such as:

- Dremio[^note3]
- Cisco Data Virtualization (previously called Composite Software and now integrated into TIBCO)
- Denodo Platform for Data Virtualization
- Informatica Data Virtualization Technology
- IBM Big SQL
- Incorta[^note3]

Nowadays, it's also called data federation, very similar to virtualization, mainly referred to technologies like Presto[^note3] or Trino.

Many of these older and newer tools have rebranded themselves to be a lakehouse platform, which begs the question: "Is a lakehouse nothing more than a data virtualization?"

They have similar attributes, but a lakehouse includes an open storage layer (Delta Lake, Iceberg, Hudi). In contrast, data virtualization is more ad-hoc, query-time driven. Still, the lakehouse from Databricks tries to store only once and avoid data movement as much as possible by querying it with their compute engine Photon.

The problem is that the platform is not open-source, only storage and the metrics are not defined declaratively. Data virtualizations are essentially a semantic layer but without the metrics layer. We'll discuss more of all the similarities later in The Underlying Patterns.

Dremio and database-like indexes

Dremio has patented database-like indexes on source systems with Data Reflections. They are producing more cost-effective query plans than performing query push-downs to the data sources.

### Core Concepts

Compared to ETL, there is no data movement and, therefore, no data inconsistency in data virtualization. You are pointing to the actual source and loading it, for the most part, into memory for fast query answers. You need to invest less in data governance and save money for copying, computing, and crunching these copies again.

There are also significant drawbacks, such as speed. It will be slower than a materialized query, although this hardly depends on your technology and how much your tool is caching.

Also, it will affect your source system as these are live connections or query push-downs, which, in the worst case, could interfere with some operational applications.

Handling Master Data Management (MDM) is more challenging as you might not be able to clean out customer names, etc., begging the question, where do I clean the data? What happens if a source system changes data? Will it break my report?

## The Underlying Patterns

In this chapter, we'll analyze the patterns behind the similar convergent evolution terms of business intelligence, semantic layer, modern OLAP, and data virtualization and why these are related to each other.

Let's repeat and summarize the unique characteristics of each CE:

- Business Intelligence Dashboards/Reports: Places a premium on visualizing key business metrics and KPIs. Its simplicity lies in its direct approach to visualization.
- Semantic Layers: Stands out for its translation and abstraction of complex data structures. It leans towards a more open, declarative approach, often using formats like YAML for defining metrics and KPIs.
- Modern OLAP Systems: Distinguished by its deep dive into multidimensional data analysis. It often encapsulates business logic in a more closed-source manner, emphasizing caching and speed.
- Data Virtualizations/Data Federation: Unique in its focus on seamless access to data from multiple sources without duplication. It leans heavily on the technical side, ensuring data is accessible without unnecessary movement.

With these unique characteristics, let's focus on the patterns they share.

### Patterns (or Commonalities)

The common patterns and similarities I found among these CEs are:

1. Visualization/Business Focus: All CEs emphasize the importance of visualizing data for business users and, therefore, make data more accessible and understandable for business users.
2. Translation/Abstraction: The recurring theme is translating complex data structures into more understandable business terms. It's a form of layering, whether a visualization layer, semantic or OLAP cube, or a virtualization layer.

For example, you were choosing measures and dimensions in your BI tools that transformed them into an SQL query and returned the needed data for your dashboard or report, which is what we call the semantic layer today.
BI tools such as SAP BO or Looker have their semantic layer, named universe or logical layer. These layers have had the same purpose: to build SQL queries based on your chosen measures and return data on the fly.
Data Modeling:

Data modeling (ECM Modeling, Fact Dimensions....) has a strong connection in all of these CEs, as we essentially model the business with a (logical) data layer. Whether we have a superficial BI layer where we create business entities as facts and dimensions, or we try to make cubes, or virtualize specific critical dimensions across data sources, all of it is essentially data modeling.
The only difference is in how we do it, on the fly, in an ad-hoc way, or pre-persisted in tables or cache.

SQL: The language of the layer is SQL or YAML.
3. For example, you were choosing measures and dimensions in your BI tools that transformed them into an SQL query and returned the needed data for your dashboard or report, which is what we call the semantic layer today.
4. BI tools such as SAP BO or Looker have their semantic layer, named universe or logical layer. These layers have had the same purpose: to build SQL queries based on your chosen measures and return data on the fly.
5. Data Modeling:

Data modeling (ECM Modeling, Fact Dimensions....) has a strong connection in all of these CEs, as we essentially model the business with a (logical) data layer. Whether we have a superficial BI layer where we create business entities as facts and dimensions, or we try to make cubes, or virtualize specific critical dimensions across data sources, all of it is essentially data modeling.
The only difference is in how we do it, on the fly, in an ad-hoc way, or pre-persisted in tables or cache.
6. Data modeling (ECM Modeling, Fact Dimensions....) has a strong connection in all of these CEs, as we essentially model the business with a (logical) data layer. Whether we have a superficial BI layer where we create business entities as facts and dimensions, or we try to make cubes, or virtualize specific critical dimensions across data sources, all of it is essentially data modeling.
7. The only difference is in how we do it, on the fly, in an ad-hoc way, or pre-persisted in tables or cache.
8. SQL: The language of the layer is SQL or YAML.
9. Speed and Efficiency: The need for fast, efficient data processing and retrieval is a common thread.
10. Single Source of Truth: Ensuring data consistency and accuracy is a shared goal across the CEs.
11. Emphasis on Metrics and KPIs: Metrics, KPIs, and measures are central to the value proposition of each CE.

- For example, you were choosing measures and dimensions in your BI tools that transformed them into an SQL query and returned the needed data for your dashboard or report, which is what we call the semantic layer today.
- BI tools such as SAP BO or Looker have their semantic layer, named universe or logical layer. These layers have had the same purpose: to build SQL queries based on your chosen measures and return data on the fly.
- Data Modeling:

Data modeling (ECM Modeling, Fact Dimensions....) has a strong connection in all of these CEs, as we essentially model the business with a (logical) data layer. Whether we have a superficial BI layer where we create business entities as facts and dimensions, or we try to make cubes, or virtualize specific critical dimensions across data sources, all of it is essentially data modeling.
The only difference is in how we do it, on the fly, in an ad-hoc way, or pre-persisted in tables or cache.
- Data modeling (ECM Modeling, Fact Dimensions....) has a strong connection in all of these CEs, as we essentially model the business with a (logical) data layer. Whether we have a superficial BI layer where we create business entities as facts and dimensions, or we try to make cubes, or virtualize specific critical dimensions across data sources, all of it is essentially data modeling.
- The only difference is in how we do it, on the fly, in an ad-hoc way, or pre-persisted in tables or cache.
- SQL: The language of the layer is SQL or YAML.

- Data modeling (ECM Modeling, Fact Dimensions....) has a strong connection in all of these CEs, as we essentially model the business with a (logical) data layer. Whether we have a superficial BI layer where we create business entities as facts and dimensions, or we try to make cubes, or virtualize specific critical dimensions across data sources, all of it is essentially data modeling.
- The only difference is in how we do it, on the fly, in an ad-hoc way, or pre-persisted in tables or cache.

### Differences:

While the patterns provide a common thread across the CEs, each evolution also brings its unique features which have a different purpose:

- Focus on Metrics and KPIs: Business Intelligence Dashboards/Reports and Semantic Layers emphasize visualizing and translating key business metrics and KPIs. In contrast, Modern OLAP Systems and Data Virtualizations/Data Federation lean more towards the technical aspects, prioritizing caching, speed, and accessing data from multiple sources.
- Data Handling and Abstraction: While Business Intelligence Dashboards/Reports are centered around visualization, Semantic Layers translate and abstract complex data structures for business users. Modern OLAP Systems delve deep into multidimensional data analysis, and Data Virtualizations/Data Federation focuses on providing seamless access to data without the need for movement or duplication.
- Technical Complexity and Approach: Business Intelligence Dashboards/Reports offer a more straightforward approach, mainly centered around visualization. Semantic Layers introduce complexity by bridging technical data with business-friendly terms. Modern OLAP Systems, being highly specialized, delve into multidimensional data structures. In contrast, Data Virtualizations/Data Federation grapple with the intricacies of accessing data from diverse sources. Additionally, while traditional BI tools and Modern OLAP systems often encapsulate business logic in a closed-source manner, newer Semantic Layers are moving towards a more open, declarative approach, with metrics and KPIs defined transparently, often in formats like YAML.

By understanding the shared patterns and the differences of each CE, we gain a comprehensive view of the data engineering landscape, appreciating the common goals and the specialized roles each evolution plays.

## Key DE Patterns: Ad-hoc Querying, Caching

Two patterns consistently emerge across discussed convergent evolutions: the ability to perform Ad-hoc Querying and the emphasis on storing data Caching for rapid retrieval.

```python
graph LR

    P_CachingDisk[P: Caching]
    CE_BITool[CE: BI Tool]
    CE_SemanticLayer[CE: Semantic Layer]
    CE_ModernOLAP[CE: Modern OLAP System]
	CE_DataVirtualization[CE: Data Virtualization]
    P_InMemory[P: In-Memory / Ad-Hoc Querying]

    %% Linking Nodes

    CE_BITool --> P_InMemory
	CE_DataVirtualization --> P_InMemory
	CE_ModernOLAP --> P_CachingDisk
	CE_SemanticLayer --> P_CachingDisk
    CE_SemanticLayer --> P_InMemory
    CE_ModernOLAP --> P_InMemory
```

### Ad-hoc Querying (Or even Data Modeling?)

This pattern emphasizes the dynamic and flexible nature of querying. Instead of relying on predefined queries or structures, systems that support ad-hoc querying allow users to pose unique, on-the-fly questions to the data.

This flexibility is crucial for business intelligence and analytics, where the questions you want to ask might evolve over time or in response to previous insights. Tools like BI dashboards, semantic layers, and modern OLAP systems have all incorporated this capability to varying degrees, enabling users to drill down into data, pivot it from different angles, and explore it without constraints.

### Cache

The second pattern, Cache, focuses on the rapidity of data retrieval. By caching data, systems can access and process it much faster than if they were to retrieve it from the primary storage every time. This is especially beneficial for applications that demand real-time or near-real-time analytics, where any delay in data access can be detrimental.

While caching introduces challenges, such as ensuring data freshness and managing cache invalidation, the advantages in terms of speed are often deemed worth the complexities.

Modern OLAP systems, semantic layers, and data virtualization tools have all incorporated caching mechanisms to enhance performance.

## Wrapping Up

This was just a summary of these patterns and design patterns. We'll continue to go in-depth with these patterns in Ad-hoc Querying and Ch. 4: Cache and its resulting data engineering design patterns in Chapter 5: DEDP.

[^note1] There is no means to be complete

[^note3] Dremio, Presto, and Incorta have branded themself new as a data lakehouse platform.

## Join the Discussion
