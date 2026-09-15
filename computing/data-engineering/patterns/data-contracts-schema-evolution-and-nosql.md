---
id: computing/data-engineering/patterns/data-contracts-schema-evolution-and-nosql
canonical_question: How do Data Contracts, Schema Evolution (Avro, Protobuf), and
  NoSQL address schema drift and producer-consumer decoupling?
aliases:
- data contracts pattern
- schema evolution in data engineering
- NoSQL vs relational schema drift
- producer consumer data contract
- schema registry Avro Protobuf
entity_type: engineering_pattern_guide
domain: computing > data-engineering > patterns
last_verified: '2026-09-15'
---

# Schema Evolution vs. Data Contracts vs. NoSQL

The history of managing database changes.

Since the databases' inception and working with them, we have needed to carefully handle table updates, such as new columns, changing the data type, or adding new tables altogether. These changes affect the entire organization, affecting application code, analytics, and downstream systems.

This chapter explores three distinct approaches that emerged: Schema Evolution, NoSQL, and Data Contracts. Data quality and change management around schemas will be around for a while. With our data systems' ever-increasing complexity, having a thoughtful strategy for handling these changes remains essential. Whether you call it schema evolution, data contracts, or something else, the challenge of managing database changes continues to be at the heart of data engineering.

```python
gantt
    title Evolution of Schema Changes
    dateFormat  YYYY
    axisFormat %Y
    
    section Schema Evolution
System R & Oracle (Major Rebuilds)    :1970, 1975
    Static Schema Era                     :1975, 1976
    DDL & Release Management              :1976, 2001
    Roddick Research                      :milestone, 1995, 1d
    Dimensional Modeling (Kimball)        :milestone, 1996, 1d
    Slowly Changing Dimensions            :1996, 2000
    Data Vault 1.0 (Linstedt)            :milestone, 2000, 1d
    ORM & Hibernate                       :2000, 2006
    Liquibase                            :milestone, 2006, 1d
    CRDTs                                 :2011, 2012
    Schema Registry                       :2011, 2014
    CI/CD                                :2015, 2023

    section NoSQL
    First NoSQL Term (Strozzi)           :milestone, 1998, 1d
    Google BigTable Paper                 :milestone, 2006, 1d
    Amazon Dynamo Paper                   :milestone, 2007, 1d
    NoSQL Term Reintroduced              :milestone, 2009, 1d
    Released (MongoDB, Cassandra, Redis)  :milestone, 2009, 1d
    Neo4j                                :milestone, 2010, 1d
    NewSQL Emergence & Schema-on-Read    :2015, 2020
    
    section Data Contracts
    Protobuf                             :milestone, 2008, 1d
    Avro                                 :milestone, 2009, 1d
    Data Contract term internally        :milestone, 2019, 1d
    Data Catalogs (Amundsen, DataHub)    :2019, 2020
    Data Contract publicly               :milestone, 2022, 1d
    Software-Defined Assets              :2022, 2023
    The Rise of Data Contracts           :milestone, 2023, 1d
    Unity Catalog                        :2024, 2025
```

## Schema Evolution

Schema Evolution usually refers to changes in the schema of a database system in an effortless way that handles new columns and changed types.

This is especially crucial in distributed or event-driven systems. Kafka is a good example. It implemented one of the first Schema Registry, which Apache Kafka started with, ensuring back-and-forth data compatibility.

### Definition

Schema Evolution is the systematic process of modifying a database's structural organization (schema) while preserving existing data and maintaining system functionality. It encompasses the ability to handle structural changes such as adding or removing columns, modifying data types, and altering relationships between tables, all while ensuring data integrity and consistency.

An essential part of schema evolution is schema versioning in Open Table Formats, often called or connected with Time Travel (versioned data from different timestamps where you can jump forward and back). Although it's more related to the data than the database schema, it is included.

We can version either partially or fully versioning.

Challenges that arise from schema changes include correctly handling data conversion between schema versions, auto conversion vs. manual patches written by DBAs or data engineers, and handling complex integrity across the org and data landscape without breaking upstream data pipelines or dashboards.

We could implement different approaches to data conversion: eager/immediate, lazy conversion when data is accessed, or a view-based approach with no conversion on the physical tables.

### History & Evolution

Early in databases such as Oracle and MSQL, changing tables or columns had tremendous upstream change outcomes. At that time, we had Subversion with DDL changes go through a manual, high-effort release management cycle with separated teams. Every change had to be approved and planned.

Changes were often assumed to be static and designed with the assumption of minimal change. However, with the growth of data warehouses, we needed more changes. The business required business intelligence specialists to fix and optimize the business context that we didn't restore to the source system, leading to more changes.

In the early 1970s, databases like System R and Oracle treated schema changes as primary operations requiring complete rebuilds. Changes went through strict release management cycles. The rise of data warehouses in the 1990s brought data warehouses new challenges as business requirements grew more dynamic. Researcher John F. Roddick highlighted schema evolution challenges in 1995, while Kimball's dimensional modeling and Slowly Changing Dimension introduced new model techniques upstream, adding new ways of managing changing dimensions.

In the object-oriented era (the late 1990s-2000s), the early 2000s saw ORM (Object-Relational Mapping) systems revolutionize schema management. Hibernate introduced automatic schema updates, while object-oriented databases brought new approaches to schema evolution.

In the Modern Era (2010s-Present), tools like Flyway (2010) and Liquibase (2006) introduced "migrations as code." The rise of NoSQL databases and cloud platforms brought schema-less designs and automatic adaptation.

In 2009, protocols like Protobuf and file formats like Apache Avro made it easier to integrate schema within data. Later, in 2011, tools like Apache Kafka's Schema Registry emerged, and automated testing frameworks have become essential for managing these complexities.

Also, around 2011, CRDTs were introduced, an interesting general-purpose data structure uniquely built multi-user from the ground up to handle schema changes gracefully with a Local First approach.

Agile development emerged around 2015. It integrates schema evolution with CI/CD pipelines, focusing heavily on testing and zero downtime. Challenges include managing schema evolution in microservices, handling event-sourcing systems, and balancing flexibility with consistency in distributed environments.

Data Vault

Data Vault is a related data modeling technique specifically focused on data changes. It could be its sub-chapter here, but I decided to include it here in schema evolution, as there are other Data Modeling Techniques like dimensional modeling, relational modeling, and many more. But data vault framework of systematically handling changes with hubs, links, and satellites.

#### Advancements in Schema Evolution

Over time, advances in schema evolution have been made:

- Schema Versioning: Maintaining multiple versions of a schema to support backward compatibility.
- Schema Modification Operators (SMOs): Defined operations that transform one schema into another, aiding in systematic schema evolution. Automating the database schema evolution process.
- Automated Tools: Data Warehouse Automation, Templating (later in data asset reusability chapter) with Jinja Template and others.

Apache Kafka, for instance, introduced the Schema Registry to manage schema versions and ensure compatibility between producers and consumers. This approach allows systems to handle new fields or data types gracefully, ensuring both backward and forward compatibility.
Tools like schemachange for Snowflake databases have been developed to automate and manage schema changes effectively.
- Apache Kafka, for instance, introduced the Schema Registry to manage schema versions and ensure compatibility between producers and consumers. This approach allows systems to handle new fields or data types gracefully, ensuring both backward and forward compatibility.
- Tools like schemachange for Snowflake databases have been developed to automate and manage schema changes effectively.
- CI/CD Tests: Today, schema evolution is integral to agile development and automated tests with continuous integration/deployment (CI/CD) pipelines. Testing schema modifications do not disrupt system functionality.

- Apache Kafka, for instance, introduced the Schema Registry to manage schema versions and ensure compatibility between producers and consumers. This approach allows systems to handle new fields or data types gracefully, ensuring both backward and forward compatibility.
- Tools like schemachange for Snowflake databases have been developed to automate and manage schema changes effectively.

Schema Registry as the First Data Contract?

A schema registry might be the first implementation to close to a data contract. It provides a RESTful interface to query db schemas, e.g., Confluent used Apache Avro for the schemas. It stores the versioned history of all schemas, seeing the schema evolution.

It's a separate instance outside of Kafka, the producer, meaning the consumer and the producer can implement their software against that interface. We'll look at data contracts in a later chapter.

A nice benefit is that once you have the schema's definitions as a file (YAML, JSON, API) in a registry/contract, you can use the declarative state, adding features such as versioning, automated tests/checks, notifications, etc.

Actual schema registry are:

- Confluent Kafak Schema Registry
- Snowplow Iglu Server

### Core Concepts

The core concepts are handling database changes on the physical table level and handling change management and downstream implications. In best cases, it is versioned to rollback in case of changes and integrated into some release management that downstream systems can subscribe to.

Related concepts are transaction logs, such as those in Data Lake Table Formats, which protocol the changes within the table and allow Time Travel functionalities.

Core functionality and features schema evolution can support backward and forward compatibility, allowing apps to read older and newer entries. Mitigate breaking changes; the popular approach is with additive changes where only new fields are added without deleting existing ones—and versioned data schema.

Apache Arrow Flight Protocol

An interesting one is Apache Arrow Flight Protocol, which enables data transfer over the network with Apache Arrow. With getting the default protocol to convert data from format to format, it's interesting how they handle schema change.

## NoSQL

Next, the evolution led us to use NoSQL for schema change management. Although it was initially controversial, it still has its place today. However, I feel we are back at more defined structures. Let's explore how NoSQL came about and how we can use it.

### Definition

NoSQL handles data without explicitly defining the schema, its columns, and data types. Because it is more fluid and dynamic, each data set usually contains the schema, which is typically defined in JSON.

It often stands for "Not Only SQL" or non-relational rather than "No SQL". It is mainly used for event streaming, as speed is a top priority. The schema will be handled and confirmed in a table later, if at all. It is particularly well-suited for handling unstructured or semi-structured data. Other use cases are dynamic and fast-changing schemas, where the producer can send either all, new, or only a few columns.

There are different types of NoSQL databases: document-based, key-value stores, wide-column stores, and graph databases.

### History & Evolution

The origin of non-relational databases dates back to the late 1960s, but Carlo Strozzi first coined the term "NoSQL" in 1998 for his lightweight open-source relational database. However, Strozzi's usage differed from the modern understanding of NoSQL, as his database was still relational. He later suggested that the current movement should have been called "NoREL" instead, as it ultimately departs from the relational model.

The modern NoSQL movement gained momentum in 2009 when Johan Oskarsson, a Last.fm developer, organized an event to discuss "open-source distributed, non-relational databases." Since then, new emerging non-relational, distributed data stores, including open-source alternatives to Google's Bigtable/MapReduce and Amazon's Dynamo, have driven the needs of Web 2.0 with the need for big data and more real-time applications.1

NoSQL databases shifted database design philosophy, prioritizing features like simplified design, horizontal scaling, and improved availability. While early NoSQL systems often sacrificed ACID transactions and consistency for performance and scalability, modern NoSQL databases like MongoDB have these features. NoSQL has matured and has found its place, usually in combination with relational databases.

Major NoSQL databases that have emerged in 2009-2010 and used widely:

- MongoDB (document store)
- Cassandra (wide-column store)
- Redis (key-value store)
- Neo4j (graph database)

### Core Concepts

Concepts that arise from the NoSQL era are that not all data needs ACID transactions. Sometimes speed is more important than consistency, usually referenced as CAP theorem (Consistency, Availability, Partition tolerance), and how NoSQL databases prioritize availability and partition tolerance over strict consistency, implementing this through the BASE principle (Basically Available, Soft state, Eventually consistent). This trade-off supports use cases such as horizontal scalability over vertical scaling, making adding more machines simple.

The schema flexibility concept is central to NoSQL, enabling rapid development and flexible use cases. This is particularly powerful when handling small chunks of streamed data that include the schema but are produced fast. Related concepts are Change Data Capture (CDC) and event sourcing, where changes to data are captured as a series of events. The idea of eventual consistency emerged from this approach, accepting that data will eventually be consistent across all nodes rather than immediately.

This ties into Data Locality, where data is stored close to where it's needed most, and distributed architecture, where data can be spread across multiple nodes while maintaining system reliability through replication and sharding.

It is also crucial to focus on specific data access patterns. Each type of NoSQL database is optimized for particular use cases, whether it's document storage for hierarchical data, graph databases for connected data, or key-value stores for simple, high-speed lookups. This specialization allows for better performance in specific scenarios than traditional databases' one-size-fits-all approach.

## Data Contract

Data Contracts is a newer term that is very interesting. Let's explore more.

Data contracts reminded me of Don't Fall for the Hype

It got me thinking, "Aren't data contracts just another word for data quality and what we've always done with schema evolution, drift, and general data governance?" However, my short take is that data quality and change management around data schema will not disappear. On the contrary, they remain essential despite ever-increasing complexity. Integrating them into a thought-through data modeling architecture is critical. Let's see more in this chapter.

Data Contracts are API-like agreements between software/data engineers who own services and data consumers who understand how the business works. The goal is to generate well-modeled, high-quality, trusted, real-time data. The teams producing and consuming could be two separate companies.

A pivotal difference to everyday schema management is that there is a third element besides the source and destination column definition, a contract that both agree on. The question is, what is that contract? An excellent illustration by Mehdi when he says that Apache Kafka could be the interface that defines the contract:

Image by Mehdio from Data Contracts — From Zero To Hero

Related, not the same: Data Products

Data Products could be the interface for users to define the data contracts between domain experts and the data assets, and depends on downstream tasks:

- Data Contract: Enforce data quality.
- Data Product: The data itself and interface

### History & Evolution

The concept of data contracts emerged from a long-standing challenge in data engineering: ensuring reliable data exchange between producers and consumers.

Protobuf and the file format Apache Avro were early data contract enablers with sophisticated built-in schema features. JSON is the default, and no additional functionality has been added. The initial version of protocol buffers (“Proto1”) was developed in early 2001 and used at Google. Apache Avro was initially created in 2009 by Doug Cutting and other developers at Cloudera.

Andrew Jones coined the term data contract internally at GoCardless in 2019. He first wrote about it publicly in 2021 and in more detail later that year. Chad Sanderson became another primary voice in popularizing and defining data contracts and started the rise of data contracts in 2022.

I learned that data contracts were also discovered separately by Jochen Christ and Simon Harrer, who worked at INNOQ and shared on DataContract.com. Some first movers and implementers of data contracts were CloudEvents, which had its first release in 2018, and Schemata around 2022.

### Core Concepts

Data contracts are database versions of real-world contracts, regulating data between producers and consumers. Core concepts are a defined interface between the two parties, creating a clearly defined agreement that can be validated and enforced — most of all, through clearly defined expectations.

If done declaratively with a YAML or a JSON file, we can build automatic tests, versioning, and automation on top of it. Checks that check the quality, if the contract is met, notifications if not. This ensures that the quality a company needs is met and improves overall quality and data governance.

With open contracts, we nourish transparency and accountability with metadata that defines ownership and responsibility, is tracked, and is visible to everyone. The data contract concepts help organizations move from ad hoc data exchange patterns to more structured, reliable approaches for managing data quality and system compatibility.

Existing Tools

The implementation of data contracts can leverage existing tools rather than requiring entirely new infrastructure. For example, data orchestration tools support data contracts through their Software-Defined Assets feature, while data quality tools can enforce contract requirements through automated checks and validations.

Besides Protobuf, Avro, and JSON, newer tools are focusing on this problem, such as Recap, which is used by Gable, too.

Another option is to add contracts a level further to the database with open table formats such as Delta Lake, Hudi, and Apache Iceberg. By defining the schema within the table, we essentially have a contract, and all writing that does not conform to it will be declined (get an error). It is not the most graceful way of dealing with differences, but it can be seen as a contract.

Related to Data Mesh

The recent Data Mesh also uses data contracts, primarily to communicate and express the typical specifications of how data should look and the expectations of the data. Data contracts are born out of frustrations and the desire to enforce consistency between producer and consumer.

## The Underlying Patterns

In this chapter, we'll analyze the patterns behind the similar convergent evolution terms of Schema evolution (including terms such as SCD and dimensional modeling, data vault, CRDTs, schema registry), NoSQL, and data contracts (including data catalogs).

We have seen that these terms are sometimes hard to keep apart. Let's repeat the unique characteristics of each CE:

- Schema Evolution: Managing database changes while preserving integrity
- NoSQL: Flexible per-document schemas prioritizing speed over consistency
- Data Contracts: Producer-consumer agreements with automated validation rules

Let's focus on the patterns they share next.

### Patterns (or Commonalities)

The convergent evolutions share several vital patterns:

- All of the discussed convergent evolutions support and handle change management, provide data consistency and integrity, and define and track the evolution of columns and data types over time.
- We are improving overall data governance with general change management and integration into data contracts, schema registry, data, and unity catalogs. Each provides version support by tracking and managing schemas/contracts.
- They all relate to data assets such as tables or files.
- All improve data quality and avoid Schema Drift, which occurs when the source evolves and replicates schema drift/divergence across databases.

### Differences

We also encounter distinct differences between them:

- Use cases: NoSQL focuses on dynamic and flexible schema, whereas data contracts and schema evolution prefer rigidly defined use cases.
- Granularity: Data contracts can be finer-grained and introduce a third-party interface between the producer and consumer, the contract. Schema evolution is a one-to-one relation to the table, and NoSQL operates at the document level.
- Implementation: Schema evolution uses migrations and registries, NoSQL embeds schemas per document, and data contracts utilize declarative YAML/JSON files
- Async vs. Sync: CRDTs can handle offline changes, while data contracts or schema registries need a sync call to check the schema.
- Scope: Schema evolution typically concerns data structure, whereas data contracts also address semantics, validation, and other aspects.

## Key DE Patterns: change management, data lineage, data versioning, and data asset

The above commonalities and differences underscore the evolution of managing database changes, aligning with the growing demands of modern data engineering and analytics. Below, we see four recurring patterns we can extract.

```python
graph LR
    CE_SchemaEvolution[CE: Schema Evolution]
    CE_DataContract[CE: Data Contracts]
    CE_NoSQL[CE: NoSQL]
    P_ChangeMgmt[P: Change Management]
    P_DataVersion[P: Data Versioning]
    P_DataAsset[P: Data Asset]
    P_DataLineage[P: Data Lineage]

    CE_SchemaEvolution --> P_ChangeMgmt
    CE_SchemaEvolution --> P_DataLineage
    CE_SchemaEvolution --> P_DataVersion
    
    CE_DataContract --> P_ChangeMgmt
    CE_DataContract --> P_DataVersion
    CE_DataContract --> P_DataAsset
    
    CE_NoSQL --> P_ChangeMgmt
```

### Change Management

Change management is the common trait of all convergent evolution. It is the ability to handle changes without breaking systems. This includes renaming fields, changing data types, adding new fields, etc. You can also define the interface for the table and set expectations in contracts. Before any data exchange, a contract (interface) is determined to ensure both producer and consumer have the same understanding. You can also dynamically use different schemas with NoSQL.

### Data Versioning

Versioning is a significant topic for database schemas. This is part of data contracts written to a third-party tool or place, mainly in JSON or YAML. Therefore, versioning is easy. However, there are other ways to evolve a schema, such as reverting a DDL, tracking updates with slowly changing dimensions, or using a schema registry.

Versions also allow for Time Travel use cases, where rollback of the schema is an option in case of error.

### Data Lineage

Data lineage is always a big topic and is mostly part of schema evolution with data catalogs or general modeling techniques such as dimensional modeling and data vault, where we need to know the source table for our data model.

Data versioning and data lineage also strengthen the data quality.

### Data Asset

Data assets represent the actual data, which is stateful and generated upstream. They could be a database table, a BI report, or a file on S3. Data assets are essential, especially in data contracts, as contracts always include an asset to apply the contract.

Data assets allow producers and consumers to be distinct from each other, avoiding tight coupling. This way, if one side changes, it doesn’t break the other. Assets are also predestined for documentation. As system users want to use the assets, it makes sense to maintain schemas, data contracts, changes, and versions on the assets, not the pipelines themselves.

Read more about Change Management patterns, Declarative and Asset-based Governance, and other connected patterns.

## Join the Discussion

1. Source NoSQL - Wikipedia ↩

Source NoSQL - Wikipedia ↩
