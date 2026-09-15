---
id: computing/data-engineering/patterns/dwh-mdm-data-lake-reverse-etl-and-cdp-evolution
canonical_question: How did Master Data Management (MDM) and Data Warehouses converge
  into Data Lakes, Reverse ETL, and Customer Data Platforms (CDP)?
aliases:
- DWH vs MDM vs Data Lake
- Reverse ETL pattern
- Customer Data Platform CDP architecture
- operational analytics vs analytical warehouse
entity_type: engineering_pattern_guide
domain: computing > data-engineering > patterns
last_verified: '2026-09-15'
---

# Data Warehouses vs. Master Data Management vs. Data Lakes vs. Reverse ETL vs. CDP

The history of ETL and data management technologies.

Most of my career started with a term called ETL. But what is it, and why is it still relevant today? What other terms relate to it, and do we even need them? This and more we will explore in this chapter.

```python
gantt
    title Evolution of ETL and Data Management Technologies
    dateFormat  YYYY-MM-DD
    axisFormat %Y

    section ETL (Data Warehouses)
    Stored Procedures      :sp, 1974, 365d
    Traditional ETL Tools  :etl, 1998, 365d
    SSIS, OWB, etc.        :etl, 2004, 365d
    Evolution to ELT       :elt, 2010, 365d
    BigQuery, Redshift     :bq_rs, 2012, 365d
    dbt                    :dbt, 2018, 365d

    section Master Data Management
    %% Master Files           :mdm, 1898, 365d
    MDM Concepts (Master Files 1898)           :mdm, 1990, 365d
    Master Data Services (MDS)           :mds, 2010, 365d
    Reverse ETL            :modern_mdm, 2021, 365d

    section ELT (Data Lakes)
    Concept ELT :dl, 2000, 365d
    Emergence of Data Lakes:dl, 2010, 365d
    DL File Formats :fm, 2013, 365d
    DL Table Formats :tf, 2018, 365d
	Open-Source ELT (Airbyte, etc.) :ab, 2020, 365d
    Data Lakehouse :dl, 2021, 365d

    section CDP (Customer Data Platform)
    CRM Systems            :crm, 1985, 365d
    Customer Data Management (CDM) :cdm, 1990, 365d
    Salesforce :sf, 1999, 365d
    Rise of CDPs           :cdp, 2013, 365d
```

## Data Warehouse

A data warehouse is the beginning of ETL history as I know it. It uses ETL (Extract Transform Load) to process data from its sources, combine it with others, and make it a control plane, creating helpful metrics that steer the company.

Data Warehouse is more than a Convergent Evolution

A data warehouse is also a design pattern if you want, as it's formed over the years according to some core data warehousing principles. In this chapter, I treat it as CE and aim to extract its patterns and create new design patterns with other patterns extracted.

### Definition

A data warehouse (DWH), an enterprise data warehouse (EDW), is the traditional data collection approach established in the 1980s. The DWH is crucial for integrating data from numerous sources, serving as a single source of truth, and managing data through cleaning, historical tracking, and data consolidation.

It facilitates enhanced executive insight into corporate performance through management dashboards, reports, or ad-hoc analyses.

Relates to the previous chapter and CE Traditional ETL Tools

As a data warehouse uses ETL heavily which relates to the chapter of Traditional ETL Tools, where we went through the evolution of traditional ETL tools and the core concepts of ETL. Please visit that chapter if you want to know more about this specific. In this chapter, we will focus more on data warehouses.

### History & Evolution

Data warehouses first appeared in the late 1980s when IBM researchers Barry Devlin and Paul Murphy devised the business data warehouse to reduce the high costs and redundancies of transferring data from operational systems to multiple independent decision-support systems. This architectural innovation aimed to streamline data flow to support better decision-making.

Key developments shaped the evolution of data warehouses over the decades. In the early days, concepts like "dimensions" and "facts" were introduced by General Mills and Dartmouth College in the 1960s, followed by the implementation of dimensional data marts by ACNielsen and IRI in the 1970s. The technology gained further traction in the 1980s and 1990s with the emergence of specialized systems and software from companies like Sperry Univac, Teradata, Red Brick Systems, and Prism Solutions, enhancing data warehousing capabilities for decision support.

Entering the 2000s, the data warehousing landscape saw a shift towards more resilient and adaptable models, such as the Data Vault by Dan Linstedt and the conceptualization of DW 2.0 by Bill Inmon, which brought forth a newer generation of data warehousing with improved scalability and dynamic architectures. This evolution reflects data warehouses' growing complexity and expanding role in contemporary analytics and decision-making processes1.

Today, in 2024, data warehouses are everywhere. If you need analytics, you build small warehouses. With the advancement of technology, this now takes a couple of minutes. New features and advances are made in real-time data integration solutions, like Change Data Capture (CDC) and ELT (Extract, Load, Transform), reflecting the shift toward immediate data processing needs with cloud-native ETL/ELT and streaming.

The increasing volume of data drives this shift, as the decreasing costs of storage and computing resources and the rise of cloud data platforms that efficiently support analyzing diverse data sources and let you get started immediately.

The future directions for data warehouses and ETL are broad. New features will make it easier to start a DWH without the need for years of ETL experience (e.g. dbt), add new layers such as a Semantic Layer, or generally ease the way to integrate with other modern data stack tools, e.g., data catalogs, orchestration, or even reverse ETL (more later in this chapter). These advancements leverage modern data architectures and improve the data warehouse process.

### Core Concepts

The core principles and concepts of a data warehouse are multifaceted. Still, the key is to apply business logic and make it readily available to all companies through data marts (and dashboards later). This forces you to model your data in a way that makes sense to business users.

Another core is integrating different sources to extract business knowledge from combined sources. It also stores data in an aggregated and analytically optimized form to answer historical questions rather than only current ones.

Data warehouses are instrumental in analyzing various types of business data sources. This is especially obvious when we run analytic queries on operational databases. Running complex queries on a database necessitates a temporary fixed state, which can disrupt transactional databases. In such scenarios, a data warehouse performs the analytics, allowing the transactional database to continue handling transactions efficiently.

Another critical characteristic of DWHs is their capability to analyze data from diverse origins, for example, by combining Google Analytics with CRM data. This is possible due to the data loading approach with ETL, where data is transformed and structured.

## Master Data Management

Master Data Management is like data governance—it has been around for a long time but is still needed. I did it throughout my career as a business intelligence specialist. Still, it was pushed into the corner when we got into big data and data engineering, where we talked more about tools and innovations.

Nevertheless, MDM is still relevant today. That is what we talk about in this chapter.

### Definition

But what is Master Data Management (MDM)? MDM is a crucial methodology for centralizing Master Data. It serves as a bridge between business professionals, the primary knowledge holders, and their data experts.

Let's say you have customers in your ERP and CRM systems. How do you ensure spelling corrections coming through the CRM are correctly reflected in the downstream systems? That's right; this is what MDM is doing.

MDM is a preferred tool for ensuring data uniformity, accuracy, stewardship, semantic consistency, and accountability, particularly regarding enterprise-scale Data Assets.

### History & Evolution

1890 Herman Hollerith created a punch card system to speed up the U.S. census, saving time and money. This led to the early separation of data into two types: static and changing, similar to today's master and transaction data. Hollerith's work eventually contributed to IBM's foundation and introduced the concept of categorizing data, a critical step for future data management.

By 1898, Edwin G. Seibels's invention of the lateral file revolutionized how businesses stored documents, creating master files containing important information like customer names and addresses. The Social Security Administration's creation of a master file in 1936 highlighted the government's use of master data for administrative purposes. This era marked the beginning of organizing critical information in a more accessible way, laying the groundwork for digital data management.

Master Data Management (MDM) took shape in the 1990s, addressing the challenges of managing increasing volumes of data and meeting new regulatory requirements. MDM systems provided a unified platform for essential data, improving data accuracy and organizational efficiency. This evolution from Hollerith's punch cards to comprehensive MDM systems underscores the ongoing effort to optimize data management in response to technological advancements and regulatory demands.

Later 2010, a tool called Master Data Services (MDS) by Microsoft was first shipped with Microsoft SQL Server 2008 R2, which made it famous for the masses, integrating it into Excel and bringing MDM to the people.

### Core Concepts

Master data management consistently maintains accuracy and uniformity above different systems, with the right domain expert in the driver's seat. It's done once, in a central place for all others.

It's a clearly defined, governed process that involves stakeholders' responsibilities and accountability. The steps are clear to technical and business people.

Master defines master data in a single system where people can look up its values. Data is fuzzily correlated with each other to mitigate typos or other data quality issues. This ensures that critical data has the right quality to be trusted.

## Data Lake

The data lake is opposite a data warehouse, which integrates its data using the ELT (Extract, Load, Transform) pattern. This approach became prominent with the rise of cloud computing and big data technologies.

### Definition

A Data Lake is a versatile storage system containing many unstructured and structured data within the Storage Layer. This data is stored without a predetermined purpose, allowing for flexibility and scalability. Data Lakes can be built using various technologies, including Hadoop, NoSQL, Amazon Simple Storage Service, and relational databases, and they accommodate diverse data formats such as Excel, CSV, Text, Logs, and more.

#### Key Capabilities

The concept of a data lake emerged from the need to capture and leverage new types of enterprise data. Early adopters found that significant insights could be gleaned from applications designed to utilize this data. Key capabilities of a data lake include:

- Capturing and storing raw data at scale affordably
- Housing various data types in a unified repository
- Allowing data transformations for undefined purposes
- Facilitating new data processing methods
- Supporting focused analytics for specific use cases

#### Components of a Data Lake

The core components are a sophisticated architecture to store, manage, and analyze vast quantities of data.

We have three layers with the foundation Storage Layer, predominantly hosted on cloud-based object storage services such as AWS S3, Azure Blob Storage, and Google Cloud Storage. This layer excels at handling distributed files, offering remarkable scalability, security, and reliability with minimal maintenance. It is well suited for both structured and unstructured data.

The data lake file formats, such as Apache Parquet, Avro, and ORC, are elevated from the storage layer, representing the evolution of data storage mechanisms. These formats are tailored for the cloud, bringing efficiency through column-oriented, compressed, and optimized storage solutions for analytics.

They support advanced features like schema evolution and split-ability, making them indispensable for efficient data exchange and processing across diverse systems and platforms. Their industry momentum, community support, and capabilities in facilitating data schema evolution influence their adoption.

The third layer of a data lake architecture is the data lake table formats, including Delta Lake, Apache Iceberg, and Apache Hudi. These introduce a layer of abstraction, turning distributed files into unified tables. This transformation allows for database-like interactions with the data lake, incorporating SQL support, ACID transactions, schema enforcement, and time travel for historical data analysis.

These formats are crucial to turning the data lake from a mere storage solution into a powerful analytical engine supporting complex data workflows, governance, and sharing mechanisms. Together, these components form the backbone of modern data lakes, enabling organizations to leverage their data assets fully.

Read more in-depth about Data Lake and Lakehouse

You can read more in-depth details on this topic, including the capabilities of Data Lakes, the comparison to a lakehouse, and trends on the market on my Data Lake and Lakehouse Guide.

### History & Evolution

As initially proposed in the 2014 Data Lake paper, data lakes can be constructed using various technologies and support multiple data formats, including Excel, CSV, Text, Logs, Apache Parquet, and Apache Arrow. The foundation of every data lake is a primary storage provider like AWS S3 or Azure Blob, which is then enhanced with essential database-like features, as explained above.

A brief evolution of data lakes goes like this:

1. Hadoop & Hive: A First-Generation data lake table format with MapReduce. Already enabled SQL expressions.
2. AWS S3: The Next Generation of a simple data lake storage. No function but immensely less maintenance and an excellent programmatic API interface
3. Data Lake File Format: Suitable file formats for the cloud that is column-oriented, well-compressed, and optimized for Analytics. File formats such as Apache Parquet, ORC, and Apache Avro.
4. Data Lake Table Format: Delta Lake, Apache Iceberg, and Hudi with full-fledged database-like features.
5. Data Lakehouse: Next evolution of a data lake with added ML and data governance features.

The latest advancements in storage layer technologies and data lake file and table formats have contributed to the evolution of data lakes, enhancing their ability to efficiently store, compress, and query large volumes of data.

#### History of ELT

ELT is the main driver behind data lakes.

The concept has existed since the early 2000s but started gaining significant popularity and recognition in the late 2010s. Specifically, its popularity rose as cloud-based data warehouses like Amazon Redshift, Google BigQuery, and Snowflake became more widespread, and robust and scalable computing resources became more accessible.

The shift from ETL to ELT allowed for more efficient processing of large volumes of data in the storage layer, making ELT a preferred approach in many scenarios. While it's hard to pinpoint when ELT became popular, its rise occurred around the mid-to-late 2010s, as companies increasingly adopted cloud technologies for data management and analytics.

ELT and data lakes have become increasingly popular due to several factors. Data is being generated in ever-larger volumes, often without human input. Storage costs are getting cheaper either on-prem or in the cloud. Compute’s price has decreased with the plurality of open source tools (e.g., Apache Spark, Apache Hadoop, Apache Beam) and cloud offerings (e.g., AWS, Microsoft Azure, and Google Cloud). Modern cloud data platforms offer low-cost solutions to analyze heterogeneous, remote, and distributed data sources in a single environment.

#### Future Evolution

With data lakehouses and thriving table formats, Delta, Hudi, and Iceberg are getting de-facto Open Standards and integrated at big data warehouse companies such as Snowflake with the Iceberg Table, Microsoft Fabric with Delta Lake, and others.

With XTable able to convert from one format to another, these open standards will stay long. And that's a good thing, as our precious data are no longer locked into proprietary formats and can be used by almost all tools the longer the standards expand.

We'll discuss this later; another immediate benefit will be Data Sharing. As the underlying gets standardized, we do not need to copy data from one system to the other; we can instead directly read the data and integrate it more easily. It will be faster and have better data quality as data stays closer to its source.

Also, streaming and real-time will get easier as we can consolidate and stream our batch processes into these same table sinks.

### Core Concepts

But why would you need a data lake? Besides the critical capabilities mentioned above, a data lake is a comprehensive data storage solution that can leverage database features based on top of distributed files, which allows you to work with your files as you'd with a database. You might save the cost of a data warehouse or expensive SSD storage.

You get database-like features from Data Lake Table Formats and their underlying Data Lake File Formats. Think of the latter as optimized CSV files in the cloud with a storage-optimized format that supports columnar queries in an open-source format.

The data lake works around the limitations of traditional data warehouses and BI tools' proprietary formats. Loading your files directly into a data lake can eliminate non-needed ETL pipelines and complex maintenance on data we'd figure out later that were not needed at all. Making the data open and easily accessible for any data-savvy people and allowing ad-hoc queries to dig into the data before needing a heavy lift like traditional ETL. Which led to the core concept and loading strategy behind a data lake, ELT.

A significant disadvantage is governance. As we can easily add new data without friction, there is no process and lots of duplication of the same information. A Data Lakehouse, which is the next evolution of such a data lake, tries to add more governance and added features. More on this later in the chapter on Lakehousing.

## Reverse ETL

This could be a sub-section of master data management, the CE term of this chapter. However, I included it in this chapter to address its benefits and origin. Let's explore the difference and whether we still need it today.

### Definition

Reverse ETL occurs when the sources and destinations of the ETL process are switched: data is transferred out of the centralized repository and into third-party applications and platforms—your sales, marketing, or customer support team.

In the reverse ETL process, the data warehouse is a single source of truth that stores the most accurate, up-to-date information and propagates it to various third-party systems as necessary.

Reverse ETL makes it easier for your employees, mainly non-technical users, to access the data and insights inside their already familiar platforms. After loading data from different sources into a data warehouse and performing beneficial, usually complex consolidations and transformations, we'd like to use these insights or work within our source systems again.

It's a way of sharing that knowledge back to the data warehouse or data lake. It came up until very recently and is very similar to Master Data Management with a more modern name. Some even call it ELtP, an alternative to ETL and Reverse ETL. It stands for Extract, load, transform, and publish.

On the other hand, sharing back to the source is a little tricky, as we create a loop if we are not careful. With data pipelines, we try to make a direct acyclic way, also called DAG, to avoid loops specifically; we need to think about the use case carefully.

Reverse ETL Just Another Name for MDM?

Maxime Beauchemin in calls. reverse ETL, a more recent addition that tackles integrating data warehouses into operational systems (read SaaS services here), seems like a modern new way of tackling a subset of what traditionally we might have called Master Data Management.

### History & Evolution

There was no clear point when this term was created, but Hightouch was among the first to write about it around 2021/22.

Google Trends the last five years for reverse ETL

Since then, it has always existed but has yet to be as prominent as other endeavors. It merged with the next chapter, Customer Data Platforms (CDPs), as these are a more substantial subset oriented around business needs to provide analytics on a subset of your data compared to a data warehouse or lake.

Moving into CDP (Customer Data Platform)?

Interestingly, despite Hightouch's initial push for reverse ETL, they have since moved on and pivoted more toward CDPs and data activation, at least in terms of marketing. This also shows that the market needs to be bigger or, more likely, that it is just a subset of ETL and data pipelines the data engineering department is handling.

### Core Concepts

Reduced to its core, reverse ETL brings valid transformed data back to the source for further analysis by its business analysts and users. It also provides operational analytics with added context within the source systems that would otherwise be missed.

It is sometimes called data activation, as data is shared with a broader audience, syncing data consistently and efficiently.

## Customer Data Platform (CDP)

Lastly, we discuss customer data platforms directly related to reverse ETL, as you need them to sync to this bespoke data platform.

### Definition

A customer Data Platform (CDP) is a system that collects large quantities of customer data (i.e., information about your customers) from various channels and devices, helping to make this data more accessible to the people who need it.

CDPs sort and categorize data and cleanse it to remove inaccurate or out-of-date information. A CDP is a data warehouse solely focused on customer data, with the CDP being more business-driven and a DWH more engineering-driven. Forbes describes it as a customer data platform like a CRM but on steroids because it helps you collect information and use it to engage your customers more meaningfully.

It's the pinnacle place of your customer data.

The question is, how do you achieve a CDP? I'd argue you can either build Data Marts dedicated to your customer data or otherwise use reverse ETL to export data from your source, DWH, or lake into a dedicated data platform.

What is a CDI (Customer Data Infrastructure) then?

A CDP is also often compared with CDI (Customer Data Infrastructure).

A customer data infrastructure solution provides prebuilt data connectors that collect data from point solutions and send that data to the systems that need it. They are a data pipeline, just moving the data from one place to another. CDIs typically start on the technical side (since they help alleviate the need for building homegrown APIs) and make their way into the business over time.  They sometimes have some minimal data storage capabilities, but they are not a replacement for a CDP (Customer Data Platform).

### History & Evolution

The Customer Data Platform (CDP) has evolved alongside marketing technologies, notably CRM systems and Data Management Platforms (DMP).

TeleMagic, the first CRM, launched in 1985, was followed by Act! in 1987 and others, which integrated sales and marketing data. The 1990s saw the rise of CDM with on-premise solutions. Salesforce revolutionized the market in 1999 with its cloud-based subscription model, leading to the popularity of SaaS by 2007. However, early CRM systems often needed to meet expectations.

Vendors added APIs to customer databases to improve interoperability, creating CDPs connected with various martech platforms. DMPs emerged in the 2000s, focusing on anonymous customer profiles for advertising but needing to improve in managing known data and long-term storage.

By the early 2010s, the martech landscape was fragmented, with companies using numerous tools. The need for a unified customer view led to the creation of CDPs in 2013, a term coined by David Raab.

Since 2013, CDPs have grown into all-encompassing data management solutions with AI and machine learning capabilities for advanced analytics and customer journey optimization. They are essential for data privacy compliance and have become a central part of the martech stack, expected to reach a $20.5 billion market size by 2027. CDPs serve as a unified source of customer data, complementing CRM and DMP systems2.

### Core Concepts

A core feature of CDPs is their focus on specific marketing or customer data, which allows you and your users to feel comfortable and easily navigate your analytics in a single place with almost no technical knowledge.

Real-time data processing. CDPs are trying to get live data, enabling a fast and accurate picture of your core data at any time and enabling you to react to recent events while having a historical view.

Another rising feature is the focus on regulations such as GDPR and CCPA, handling compliance at a central place for all sensitive user data, and handling delete requests. With that centralization, you also simplify audits or data usage protocols, making it a secure and privacy-saving way of analyzing customer or match data.

## The Underlying Patterns

This chapter has explored terms like Data Warehouses, Master Data Management, Data Lakes, reverse ETL, and CDPs, noting their overlaps and unique distinctions. Each was developed at different times but aimed to achieve similar goals in data management and accessibility.

That is a good illustration of convergent evolutions built out at different times but achieved the same goals. Let's analyze what these are in this part.

We've encountered several convergent evolutions in this discourse, each serving distinct roles in the data ecosystem:

- Data Warehouses: A central repository for consolidated data from various sources, optimized for query and analysis.
- Master Data Management (MDM): Ensures data accuracy and uniformity across the organization by centralizing the management of core business entities.
- Data Lakes: Store vast amounts of raw data in its native format until needed, focusing on flexibility and scalability.
- Reverse ETL: Moves processed data from centralized systems back into operational systems, facilitating actionability across business functions.
- CDPs: Aggregate and organize customer data from multiple sources to provide a comprehensive view of the customer journey.

### Patterns (or Commonalities)

The convergent evolutions share several vital patterns:

- Data Sharing: Emerges from data lakes with open standards around table formats, whereas reverse ETL pushes its data to third-party data platforms. Similarly, MDM systems focus on distributing cleansed and unified data across enterprise systems, ensuring consistency and reliability. Sharing data across systems and platforms is a common goal. Reflecting a broader theme across technologies, the aim is to make data universally accessible and actionable across different platforms and various end-users.
- Reusability: In Master Data Management and Data Warehouse, we reuse existing work once it's done, benefiting the whole organization, enhancing consistency, and reducing duplication of work.
- Business Transformation (ETL): Transforming raw data into actionable insights is essential for data-driven decision-making. CDPs might be seen as a specialized data warehouse subset that encapsulates our era's trend toward specialization. CDPs cater to specific business needs, such as enhancing customer experience through detailed, real-time data analytics, while data warehouses try to hold data across all domains. In the middle, we have reverse ETL tools, facilitating the operationalization of data across business functions.
- In-Memory / Ad-Hoc Querying: Data Warehouses and CDPs enable fast, ad-hoc analytics and flexible data exploration without pre-aggregated reports, catering to immediate business intelligence and analytical needs.

### Differences

Despite their commonalities, these technologies also have distinct features. Data Lakes' openness contrasts with the traditionally more structured environment of Data Warehouses.

Furthermore, the transformation process in ETL versus ELT highlights the evolving approaches to data processing: while ETL emphasizes pre-loading data transformation, ELT leans towards transforming data once it's already in the target system.

The distinction between CDPs and Reverse ETL tools underscores the different focuses within data management practices. While CDPs are centered on analyzing and leveraging customer data within, Reverse ETL tools prioritize the outward movement of data to enhance operational systems.

## Key DE Patterns: Data Sharing, Reusability, Business Transformation (ETL) and `In-Memory / Ad-Hoc Querying

Four patterns consistently emerge across convergent evolutions: the ability to make data accessible with data sharing, help with business logic and transformation optimized for users in a reusable way, and allow queries to be ad-hoc.

```python
graph LR
    CE_REVERSE_ETL[CE: REVERSE_ETL]
    CE_MDM[CE: MDM]
    CE_CDP[CE: CDP]
    P_Reusability[P: Reusability]
	P_Transformation_ETL["P: Business Transformation (ETL)"]
    P_DataSharing[P: Data Sharing]
    %% P_ImplicitOrchestration[P: Implicit Orchestration]

    CE_DataWarehouse[CE: Data Warehouse]
    CE_DataLake[CE: Data Lake]
    %% P_TableFormats[P: Open Table Format]
    P_InMemory[P: In-Memory / Ad-Hoc Querying]

    CE_DataWarehouse --> P_Transformation_ETL
	CE_DataWarehouse --> P_Reusability
    CE_DataWarehouse --> P_InMemory

	CE_DataLake --> P_ELT
	CE_DataLake --> P_Transformation_ETL
	CE_DataLake --> P_DataSharing
    CE_REVERSE_ETL --> P_DataSharing
    CE_MDM --> P_Reusability
    CE_MDM --> P_DataSharing
    CE_CDP --> P_Transformation_ETL
    CE_CDP --> P_InMemory
	
	%% Singular connections: removed here
    %% CE_REVERSE_ETL --> P_ImplicitOrchestration
	%% CE_DataWarehouse --> P_CachingDisk
	%% CE_DataLake --> P_TableFormats
```

### Data Sharing

Data-sharing insights are easy and flexible. Advanced sharing techniques with open formats and standards allow data integration without copying. That gives you the advantage of having live updates without the need to re-fetch them.

### Business Transformation

We've already discussed business transformation as a pattern in the previous chapter.

### Reusability

We've already discussed reusability as a pattern in the previous chapter.

### In-Memory / Ad-Hoc Querying

We've already discussed caching as a pattern in the previous chapter.

## Wrapping Up

I hope you enjoy this history of ETL and its related convergent evolutions. We will go into much more detail in future key patterns (Data-Sharing, Business Transformation, Reusability, and In-Memory and Ad-hoc Queries) and their resulting data engineering design patterns in Chapter 5: DEDP.

Feel free to leave a comment below and start the discussion around ETL.

## Join the Discussion

1. Years and numbers from Data Warehouse Wikipedia ↩
2. Read more on The History of the Customer Data Platform (CDP) and CRM. ↩

Years and numbers from Data Warehouse Wikipedia ↩

Read more on The History of the Customer Data Platform (CDP) and CRM. ↩
