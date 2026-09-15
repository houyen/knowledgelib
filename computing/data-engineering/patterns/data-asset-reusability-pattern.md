---
id: computing/data-engineering/patterns/data-asset-reusability-pattern
canonical_question: How does the Data Asset Reusability Pattern modularize datasets,
  intermediate tables, and transformations across teams?
aliases:
- data asset reusability pattern
- reusable data models
- modular data pipelines
- data as a product reusability
entity_type: engineering_pattern_guide
domain: computing > data-engineering > patterns
last_verified: '2026-09-15'
---

# Data-Asset Reusability Pattern

Fast iteration with deterministic templates, configurations, or abstraction. Efficient data reuse.

Reusability is achieved through four approaches: templating for standardized code, materialization for data reuse, abstraction for complexity management, and generation for scalable implementations. We encapsulate specific technical or business logic into logical constructs to achieve reusability.

The data-asset reusability pattern and its applications have been fundamental since the inception of data movement. It addresses two key challenges: reusing existing code, like writing integration logic once and using it for multiple source tables, and reusing data assets efficiently by avoiding data duplication and creating siloed data. By focusing on code and data reusability, we can improve maintainability and reduce complexity across the data stack.

In this chapter, we explore how we are doing this and what common practices and existing tools are in the data ecosystem.

> A big thanks to Cívica for sponsoring this chapter. Cívica specializes in developing business solutions based on technology and in executing digital transformation, business intelligence, and data engineering projects. They are a key player in the data engineering space in Spain. I thank them for making this chapter available to everyone in the data community.

A big thanks to Cívica for sponsoring this chapter. Cívica specializes in developing business solutions based on technology and in executing digital transformation, business intelligence, and data engineering projects. They are a key player in the data engineering space in Spain. I thank them for making this chapter available to everyone in the data community.

## Intent

The pattern of reusability for data assets is necessary and something we always do after the initial creation of a data pipeline, a SQL statement, etc. It solves the problem of DRY (Don't repeat yourself). In the data engineering lifecycle, we must optimize and minimize duplications to reduce maintainability, make it easier to understand the business logic, and improve overall quality.

We can define the pattern like this:

> The data-asset reusability pattern minimizes duplicated business logic. It enhances maintainability by abstracting complex data engineering logic into reusable templates, components, and materialized assets that can be consistently applied across an organization's data stack.

The data-asset reusability pattern minimizes duplicated business logic. It enhances maintainability by abstracting complex data engineering logic into reusable templates, components, and materialized assets that can be consistently applied across an organization's data stack.

## Origin of the Pattern

With the convergent evolution from previous chapters, we can see how this pattern emerges throughout different evolutions.

```python
graph TD
    CE_Microservices[CE: Microservices]
    CE_MDM[CE: MDM]
    CE_PythonScript[CE: Python Script]
    CE_DWA[CE: DWA]
    CE_dbt[CE: dbt table]
    CE_MV[CE: MV]
    CE_SemanticLayer[CE: Semantic Layer]
    P_Reusability[P: Data-Asset Reusability]

    %% Connections
    CE_Microservices --> P_Reusability
    CE_PythonScript --> P_Reusability
    CE_DWA --> P_Reusability
    CE_dbt --> P_Reusability
    CE_MDM --> P_Reusability
    CE_MV --> P_Reusability
    CE_SemanticLayer --> P_Reusability
```

### The History of Reusability

The reusability of code and data is key to working with data. Reproducing similar pipeline or business metric implementations requires a lot of developer power and computing when copying data multiple times. Avoiding duplication also enhances discoverability and maintainability.

Following the DRY principles is a common thread for code improvements. With SQL, the most common language of a data person, we can leverage the declarative features by writing a select query to define what we want instead of defining how the database should resolve or get the data, which is done automatically through each database's query planner.

However, SQL has the disadvantage of not having variables. We can't reference an existing block or query, which usually leads to duplicating certain blocks of the query, making maintainability harder as we'd need to update not only one but two places now.

That's why dbt became so popular: We can build a full lineage graph, build on materialized tables, and use advanced templates and macros with Jinja Template. It's giving us superpowers compared to plain SQL, including generated documentation, lineage graphs, tests, and version control.

However, dbt was one of many companies that introduced it. Data Warehouse Automation tools have used templates to, for example, define different types of source tables and flag them as transactional tables or core data, which need other ways of integrating into a data warehouse and, ergo, various templates. This continues, while you could have templates for Data Vault modeling or SCD2 if you need the history of specific tables. Making it super easy to get a complex feature by just choosing a template. The technical logic has already been created, and we can reuse it.

## Sub-Patterns and their Features

Sub-patterns are characteristics of the data-asset reusability pattern. They show us the differences within this pattern and visualize its origins from CEs. Categorized into these four:

1. Variables or Templates: Templates, references, and imports like object-oriented programming. Examples: Jinja Template, dbt, CTEs.
2. Materialization: Persist so others can reuse that data (dbt, Materialized Views)
3. Logical Abstraction: Bundle complex logic (e.g., dimension with 20+ tables) into an abstraction to simplify. Examples: Master Data Management
4. Generator (+YAML): Put complex logic into code or config once, and generate for all tables. Data Warehouse Automation, Declarative Data Stack/DWA, Metrics Layer

```python
graph LR
    %% Convergent Evolutions
    CE_Microservices[CE: Microservices]
    CE_MDM[CE: MDM]
    CE_PythonScript[CE: Python Script]
    CE_DWA[CE: DWA]
    CE_dbt[CE: dbt table]
    CE_MV[CE: MV]
    CE_Semantic[CE: Semantic Layer]

    %% Main Pattern
    P_Reusability[P: Data-Asset Reusability]

    %% Sub-Patterns
    SP_Template[SP: Template Parameterization Pattern]
    SP_Material[SP: Asset Materialization Pattern]
    SP_Logic[SP: Logic Encapsulation Pattern]
    SP_Config[SP: Parametric-Driven Generation Pattern]

    %% Convergent Evolution to Main Pattern
    CE_Microservices --> P_Reusability
    CE_PythonScript --> P_Reusability
    CE_DWA --> P_Reusability
    CE_dbt --> P_Reusability
    CE_MDM --> P_Reusability
    CE_MV --> P_Reusability
    CE_Semantic --> P_Reusability

    %% Main Pattern to Sub-Patterns
    P_Reusability --> SP_Template
    P_Reusability --> SP_Material
    P_Reusability --> SP_Logic
    P_Reusability --> SP_Config

    %% Specific influences on sub-patterns
    CE_dbt --> SP_Template
    CE_PythonScript --> SP_Template
    
    CE_MV --> SP_Material
    CE_dbt --> SP_Material
    
    CE_MDM --> SP_Logic
    CE_Semantic --> SP_Logic
    CE_Microservices --> SP_Logic
    
    CE_DWA --> SP_Config

    %% Styling
    classDef convergentEvolution fill:#e1f5fe,stroke:#01579b
    classDef pattern fill:#e8f5e9,stroke:#2e7d32
    classDef subPattern fill:#f3e5f5,stroke:#7b1fa2

    class CE_Microservices,CE_MDM,CE_PythonScript,CE_DWA,CE_dbt,CE_MV,CE_Semantic convergentEvolution
    class P_Reusability pattern
    class SP_Template,SP_Material,SP_Logic,SP_Config subPattern
```

We can categorize these into the following sub-patterns: "Template Parameterization", "Asset Materialization", "Logic Encapsulation" and "Parametric-Driven Generation". Let's go into more detail about each of these patterns and what this means for us data engineers.

### Template Parameterization Pattern

Variable and templates are probably the most known and easiest to use medium. We can define a variable to reuse a certain function or return set, or if more complex, we use a full-fledged template that we can ingest multiple variables and configs to make it super flexible.

Throughout my career, this option has been a well-known and efficient way of making the reusability of data assets and data engineering code.

Convergent evolution, which we discussed earlier, that fits into this category, are dbt and Jinja Templates, CTEs, and Data Warehouse Automation, although they also use a combination with a generator.

If we use Apache Airflow's templated fields, Terraform, orchestration templates, SQL Macros, or anything else, variables or templates are a daily option we data engineers need to think of.

### Asset Materialization Pattern

Another very related approach is materialization. So instead of reusing the code - the SQL or Python code - we reuse the data, the assets. This is one of the oldest tricks we have, and we've done that with Materialized Views (MV) for many years. Behind each MV, we have an SQL query that can get materialized (therefore the name) to disk, and upstream data pipelines, dashboards, or data apps that can then use the cached and persisted data instead of writing the SQL code inside their apps.

Typical examples here are Materialized Views, dbt, and One Big Table, typically what we discussed in chapter Materialized View vs. One Big Table (OBT) vs. dbt Table vs. Traditional OLAP Cube vs. DWA.

### Logic Encapsulation Pattern

A more advanced but highly effective approach is abstraction. The best abstraction converts complex logic into simple abstractions. Early abstractions were BI semantic layers, such as the SAP BO Universe tool, where we built a logical layer based on our raw source tables. For example, an SAP customer was defined by 20 related tables; in the SAP universe, we modeled that as one entity, abstracting away all the joins and granularity considerations one would need to know.

Today, we have more advanced abstractions. The best-known is the Semantic Layer, which sits on top of our heterogeneous data landscape and provides a single interface to all data apps, dashboards, and notebooks.

Another example is orchestrators. We use abstractions and resources for Spark, Snowflake, etc., so that when building a data pipeline, we do not need to consider the complex interfaces of an Apache Spark cluster or how we run it; that is abstracted away. There are thousands more examples, as abstractions are everywhere. Data engineering is such a complex space that everyone needs abstractions.

Abstraction also has its downside. The best way to understand its pros and cons is to compare it to the Declarative vs. Imperative approach. Most enhanced data engineering tools are built on top of declarative features, as an imperative programming style won't work with high complexity.

### Parametric-Driven Generation Pattern

The generator approach generates code based on configs and templates, helping us to write the SCD2 logic that we use for all tables we want to historize only once. If we need history, we can just configure the table name and generate it.

Great examples are Data Warehouse Automation Tools, Declarative Data Stacks, or programming patterns such as the Factory Pattern.

These allow us to focus on the core implementation once, and then we generate it for the destination database or environment where our data platform is running.

### Common Features among the Sub-Patterns

All sub-patterns have these common features:

- All focus on code/logic reusability - they aim to write logic once and reuse it multiple times instead of duplicating effort
- They all serve as abstraction layers - whether through templates, materialized views, logic encapsulation, or generators, they hide complexity from end users
- All sub-patterns support scalability - they make it easier to apply the same logic or transformations across multiple use cases or data assets
- Each pattern emphasizes configuration over implementation - they separate the "what" (configuration) from the "how" (underlying implementation)
- All sub-patterns aim to reduce errors by centralizing logic in one place rather than having it scattered across multiple implementations

Leading to the data-asset reusability pattern that focuses on an Data Assets and makes it more approachable throughout complex, heterogeneous data landscapes.

## Core Problems Addressed

A core problem addressed with the data-asset reusability pattern is, that it's hard to have a control plane view of your data assets, meaning your data lake dumps, your highly cleaned and aggregated data marts tables, your BI dashboards, or data app that hold valuable data transformation as part of their data sets. Especially when you add more tools and different modeling techniques to the mix, it's the problem of not repeating yourself is hard, as you don't really know if there's already an existing data set to use.

Data Catalogs and Cloud Data Platforms solve these problems by having a central dictionary to look up data sets; some even have features such as rating, owner, and more that help avoid duplicating any data assets. But how do we solve it with generic patterns?

### Sub-Patterns

Let's look at each sub-pattern, which addresses specific data engineering challenges - briefly highlight each problem that each sub-pattern tackles:

- Templates → Code duplication
- Materialization → Performance vs Storage
- Abstraction → Complexity
- Generation → Scale and standardization

Including the challenge and impact of each, we can distinguish the sub-patterns like this:

## Pattern Usage Guidelines

Now, we need to answer the question of when and where we are using this data-asset reusability pattern and its sub-patterns. What are the real use cases for these?

### General Implementation Considerations

As extensively written above, we have four main different types of sub-patterns. The table below shows the differences in purpose, scale, and scope, but also implementation examples and common tools or technologies we can use, showcasing how data-asset reusable patterns appear.

The common pitfall is to over-engineer simple solutions. Don't use the pattern when you want to quickly set up a test when you must be super flexible with a high level of control. Abstracting everything and creating interfaces between the different abstractions is not worth the effort in these cases.

Let's look at key decision factors when to use and avoid this pattern.

### When to Use

You should use the data-asset reusability pattern, when you work in complex data engineering environments, potentially fast dev cycles, or when you want to speed up things with simply persisting existing SQL queries.

Avoid repetitive SQL statements or transformations that are used across teams. Or you want to improve the consistency of important business logic. Standardization for aligning on data modeling approaches such as Slowly Changing Dimension, Data Vault, or others across multiple tables.

Or when your data platform uses multiple technologies that profit from content implementation through abstractions, building standardizations in your organization, and ensuring better data quality and governance.

### When to Avoid

If you build or have a small and simple data platform, or when the benefits of creating the template or abstractions are smaller than the gain from reusing it, meaning if you only use it twice, it might not be worth the effort.

Also, if you need fine-grained control over individual parts of your stack, with abstraction and reusability in place, it gets harder to keep that control. For example, if the business requirements constantly change, it's not worth building abstractions or detailed reusable templates.

### Sub-Pattern Selection Guide

Here's a simple decision tree and guide for choosing between sub-patterns based on use case requirements, technical constraints, and team capabilities:

```python
graph TD
    Start[Start] --> Q1{Need to standardize<br/>across teams?}
    Q1 -->|Yes| Q2{Large scale<br/>standardization?}
    Q1 -->|No| Q3{Performance<br/>critical?}
    
    Q2 -->|Yes| G[Generator Pattern<br/>Use when: Many similar implementations]
    Q2 -->|No| T[Template Pattern<br/>Use when: Shared logic needed]
    
    Q3 -->|Yes| Q4{Storage cost<br/>concerns?}
    Q3 -->|No| Q5{Complex business<br/>logic?}
    
    Q4 -->|No| M[Materialization Pattern<br/>Use when: Query optimization needed]
    Q4 -->|Yes| Q5
    
    Q5 -->|Yes| A[Logical Abstraction Pattern<br/>Use when: Need to simplify complexity]
    Q5 -->|No| R[Regular Implementation<br/>No pattern needed]

    %% Styling
    classDef decision fill:#f0f7ff,stroke:#4a90e2
    classDef endpoint fill:#e8f5e9,stroke:#2e7d32
    
    class Q1,Q2,Q3,Q4,Q5 decision
    class G,T,M,A,R endpoint
```

## Pattern Examples

Let's look at some concrete examples that are used in real life.

#### Abstraction Layer: API-Based Systems

A good example of how this data-asset reusability is manifesting through abstraction is data orchestration. In this example, focusing on Dagster. It highlights its abstraction of data assets on different levels:

- Asset data catalog through API interface
- Separation of technical execution and business logic through resources and other component abstraction
- The declarative approach lets the data pipeline parameterize (Parametric Data Pipeline), through abstraction

To achieve these different levels of abstraction, Dagster needs clearly defined interfaces. This is achieved with APIs gating between internal communication. Instead of intertwining it into a monolith, we can separate different modules, such as execution. More like a Microservices approach.

Data control plane in Dagster from Data Platform Week's Keynote, from Nov, 2024.

In Dagster, they have an internal catalog, data assets, and other application layer content that communicate through the Dagster API. The same goes for their integrations, which are external parts that have clearly defined interfaces.

Finding the right amount of abstraction is hard, and integrating these into a tool that others need to use, even more. That's why many say, Dagster is harder to adopt than other Data Orchestrators, why? Because you need to learn these abstractions and are limited if you want to do something out of scope. But on the other hand, you get all batteries included when you start using it, without writing an extra line of code for restartability, backfilling, a nice UI, etc.

Based on your notes, I'll write two focused examples and add a third section pointing to other key implementations:

#### Template Pattern: dbt and Business Rules

dbt exemplifies the template pattern by enabling Jinja templates to write business rules. Consider this scenario:

```python
-- reusable template for SCD Type 2
{% macro scd_type_2(table_name, business_key, tracked_columns) %}
  SELECT 
    {{ business_key }},
    {{ tracked_columns }},
    CURRENT_TIMESTAMP as valid_from,
    NULL as valid_to,
    TRUE as is_current
  FROM {{ table_name }}
{% endmacro %}
```

This template abstracts complex SCD Type 2 logic into a reusable component, letting teams focus on business rules rather than implementation details.

#### Semantic Layer: Advanced Abstraction Example

Modern semantic layers demonstrate sophisticated abstraction by unifying complex data models, cache layer, feature rich APIs and permission management into simple abstraction. For instance:

```python
# Metric definition in semantic layer
metrics:
  revenue:
    description: "Total revenue across all channels"
    type: "sum"
    sql: amount
    joins:
      - orders
      - customers
    filters:
      status: "completed"
```

This abstraction can hides complex joins and business logic behind a simple metric definition, making it reusable across all data consumers. It avoids re-creating this implementation in each BI dashboard, notebook, and data app. Plus, as it's declarative with YAML, we can version control it, do complex automation, or apply other software engineering best practices.

#### Additional Pattern Implementations

Key implementations from the ecosystem:

- Data Warehouse Automation: Tools like WhereScape, biGENiUS, using templates for staging and core layers
- Apache Arrow: Unifying in-memory formats for efficient data transfer
- Master Data Management: Centralizing and standardizing entity definitions
- Microservices Approach: Breaking down complex data operations into reusable components
- Data Mart: Providing standardized, reusable data models for reporting
- Declarative Data Stack: Another generator pattern configures the entire data stack based on a single file, potentially generating all data tools.
- Extending SQL for analytics: Extending the SQL standard to include metrics, enlarging the declarative syntax of SQL, and increasing the abstraction capabilities for simplifying all business intelligence and data applications upstream.
- Normalization: A foundational Data Modeling Technique that enforces data reusability by eliminating redundancy through decomposition into related tables, making attributes reusable across the database rather than duplicating them
- Ibis:  Universal interface for data wrangling with Python. Write once, and transpile to all SQL dialects or databases.

## Trade-offs

The data-asset reusability pattern offers advantages that outweigh its limitations and costs. At its core, this pattern reduces maintenance overhead by centralizing logic and ensuring consistent implementation across systems. Once the reusable components are established, organizations see faster development cycles, as teams can leverage existing assets rather than building from scratch. This standardization also enhances governance and control, making enforcing data quality standards and maintaining compliance across the data platform easier.

However, these benefits also come with some risks. The initial investment in reusable components cannot be avoided, requiring careful design, alignment, and documentation. Organizations must be prepared for a longer initial development cycle. Depending on the used sub-patterns, the learning curve is longer and includes understanding how to use and implement reusable components effectively.

A proper risk factor is the urge for over-abstraction, which leads to more complex systems with many components that need to fit together. Although not applying any data-asset patterns might increase maintainability or effectiveness, overdoing it might do similar harm. This complexity can also manifest as performance overhead, with more moving parts. It's wise to carefully balance the reusability against the need for abstractions, templates, or a generator approach.

While reusability can reduce long-term maintenance costs; continuous documentation, training, and support investment are required to ensure effective utilization. Organizations must carefully evaluate storage versus compute trade-offs. While materializing frequently used queries often reduces overall costs by avoiding repeated computations, unnecessary materialization of rarely accessed data can lead to wasted storage resources. Finding the right balance is materializing high-impact, frequently accessed assets while leaving less regularly used queries to run on demand.

The success of this pattern heavily depends on organizational culture and team capabilities. A strong engineering culture that values standardization and documentation is essential for effective implementation. Teams must be willing to invest time in understanding and properly implementing reusable components rather than taking shortcuts with quick, custom solutions. This cultural aspect represents a hidden cost that organizations often overlook when adopting reusability patterns.

## Related Patterns

As identified in the Convergent Evolution -> Design Design Patterns Overview, the data engineering design pattern based on the data-asset reusability pattern is Declarative Orchestration.

```python
graph LR
  P_Reusability[P: Data-Asset Reusability]
  DP_DeclarativePipeline[DP: Declarative Orchestration]

  P_Reusability --> DP_DeclarativePipeline
```

Previous chapter, The history of data orchestration, about templating with Bash-Script vs. Stored Procedure vs. Traditional ETL Tools vs. Python-Script contains related content if you haven't read it yet.

Other related patterns:

- Factory Pattern provides a foundation for our Generator pattern by moving general logic to a higher level (like moving from specific Truck implementation to a general Logistics class that can handle various vehicle types)
- Abstract Factory aligns closely with our logical abstraction approach, offering ways to create families of related objects
- Cache-Aside Pattern influences our materialization strategies for data assets
- Template Method Pattern informs our approach to code reuse and parameterization
- Facade Pattern relates to our logical abstraction methodology, providing simplified interfaces to complex systems
- Parametric Data Pipeline is connected to the generator pattern, and explored more on The Struggle for Code Reuse in the Data Transformation Layer

Do you have other use cases of implementing or applying the data-asset reusability, or any of the sub-patterns? Do you see other characteristics or advantages of this pattern? Please let me know in the comments below. Jump to next chapter for exploring the next pattern.

## Join the Discussion
