---
id: computing/data-engineering/patterns/challenges-in-data-engineering-lifecycle
canonical_question: What are the core challenges, pyramid of work product, and failure
  modes across the data engineering lifecycle?
aliases:
- challenges in data engineering
- data engineering lifecycle challenges
- pyramid of work product data
- data quality and ingestion pain points
entity_type: engineering_pattern_guide
domain: computing > data-engineering > patterns
last_verified: '2026-09-15'
---

# Challenges in Data Engineering

To understand design patterns and their usefulness, we need to know what challenges we face daily. And to be frank, there's a lot of them.

## The Data Lifecycle

The best way to do that is with the data engineering lifecycle, which we'll discuss at length below, and with where people experience the problems along the data lifecycle. The image shows where people feel the pain from data collection to action taken based on data.

Image 1: Flow of data and where people experience the problems | Image by Matt Arderne, Original source: Forbes.com

It's the same picture I had present when I started my journey. We always had to fix the problems of upstream (data generated before) data generators introduced. Every day or week, there was a state of data that wasn't tested or expected because the UI needed to filter characters in a numbered field or just things like that.

The image 1 illustrates the data lifecycle well, let's discuss them a little more:

1. Data gets collected: These are the data we think we need to make informed decisions later on
2. The most significant part, and also what causes the most problems, such as cleaning, joining, unifying, and clarifying business requirements or unknowns that should have been discussed before.
3. Visualizing the hard work. Most importantly, this is what non-technical people will see and care about. In today's world, these could also be data sets as more data-savvy people can work with them (thanks to dbt and others)
4. Here, we could stop, but we can go on with in-depth analysis, machine learning, and crunching sophisticated or dedicated tools.
5. Interpreting the data and communicating a clear message is as important as all the steps before.
6. Based on communication, feedback, and discussion, it's time to make decisions and change something in a product company.

You know the drill: "My dashboard shows the wrong number", "Why this aggregation does not include X", "Ups, we didn't read the data correctly", or we took the wrong (too fast) conclusion. Sometimes, we experience problems if the data needs to be corrected. Even more today, all our apps rely on real-time or a flood of data.

But how do we escape that?

## From Work to Outcome: The Pyramid of Work Product

I cherish the illustration below, comparing our work and mapping it to its function and outcome. This ties nicely into what we discuss in entering data engineering, where first-time data engineering was introduced as Functional Data Engineering.

Usually we design from the bottom-up. In today's world that means specific work, called work product below, for data engineers:

1. Setup a Data Infrastructure: Choose a storage format (database, table format), and decide how you want to orchestrate (bash, SQL, Python).
2. Building a Data Foundation: Model your data schemas, translate the business logic into SQL/Python, clean up, and define the database layers.
3. Make Data Accessible: Decide how you want to present your data to your stakeholders. A fancy dashboard, some interactive notebooks, or a simple data set that people can work with, or still need to export to Excel 😉.

An illustration of the data outcome vs. its function | Image from The future of the data engineers by Analytics at Meta

When we look at the outcome, we'll have the beloved insights we so desperately strive for through consistent measurement and high-quality data based on a stable yet observable data platform.

Keep it Simple

With the latest trends, we can choose from a wide variety of tools, it's wise to keep the tools as low as possible, to keep it simple. This is something highly important to understand. Also, if you have the resources, sticking to open-source protects the solution from locking into a certain vendor, as well as being free to change anything from the data platform as opposed to waiting and praying, that the vendor will implement your feature.

If resources or time is a problem, choosing dedicated vendor tools can make perfect sense too.

## Challenges along the Data Engineering Lifecycle

But what is causing the Problem? I like to dive into these with another illustration, the Data Engineering Lifecycle.

To understand the challenges within data engineering, we need to check the view of data engineering as a whole. This is where the Data Engineering Lifecycle fits in perfectly.

Data engineers today oversee the whole data engineering process, from collecting data from various sources to making it available for downstream processes. The role requires familiarity with the multiple stages of the data engineering lifecycle and an aptitude for evaluating data tools.

Problems can arise from all dimensions from optimal performance across several dimensions, including price, speed, flexibility, scalability, simplicity, reusability, and interoperability.

The data engineering lifecycle illustrates the challenges of data engineering in one image.

Data Engineering Lifecycle | Image by Fundamentals of Data Engineering (Joe Reis, Matt Housley)

I'm borrowing the definition from the Fundamentals of Data Engineering book by Joe and Matt as it defines the data engineering lifecycle in a simple overview. There are different illustrations, but the lifecycle captures the end-to-end flow of a data engineering project, with pluggable components, also called undercurrents.

In this chapter, I'm not focusing on the general definitions, as these can be read in the fundamentals of data engineering, but on the challenges that arise from each.

Let's dive into the separate core of the lifecycle and, later, its undercurrents.

## Core Data Engineering Lifecycle Challenges

The core is the top of the illustration, without the undercurrents.

### Generation Challenges

The data is generated exponentially as every small device is producing them. With the more data we have, many are demanding more analytics to help them make decisions for businesses. The generation layer is where a vast amount of this data is created.

These are the apps, websites, and devices we use. It's our source systems we get our data from for analytics. These systems are most important to us data engineers, but also the ones we have the least influence on. We can't control them.

Generation and its frequency of data can be hugely different, depending on the application. It could be a real-time app that produces data every minute or older, or it could be more traditional, e.g., an accountant system that produces data much less often.

With more data, we are also experiencing another challenge; it's harder to find the right data. Not all data is useful, and crunching the increased volume is sometimes difficult. We need bigger servers or new approaches that scale better. That's a simple reason why the Cloud Data Provider such as Amazon, Microsoft, and Google grew exceptionally fast. But more on that later.

We, as data engineers, generally do not access productions directly. We copy or, better, synchronize the data. There are several challenges with that. Because we need production right access. Reading data will reduce the speed of the production servers; in the worst case, it can even produce an error if production wants to update while we read. There are multiple approaches to read these changes, such as installing Database Triggers, reading the CDC ahead log, or simply accessing data during the night, but more on this in data integration.

Another is the schema of the data. Added columns, removed or even changed fields. As well as changed data over time can be non-trivial. As it's not as easy to read deletes, if they are not tracked, we might miss some. More in the data ingestion/integrationnchapter below.

### Storage Challenges

The next challenge is that once we generate the data, we need to store it in our data platform, either a data warehouse, data lake, or a data lakehouse.

Storage is essential. We have several options. Are we using a simple Postgres, a relational database, or storing it on a cheaper S3 storage but accepting the slower query time and overhead of managing the distributed files or any new storage technology?

This depends on how much data we have or potentially will have in the future. Although that is always hard to say, in the worst case, you can upgrade later, too, besides optimizing for a potential future case that will not exist.

Usually, this is conceived in a term called the Three Vs (volume, velocity and variety), something initially related to the term big data, which summarized our challenges of storing data excellently:

1. Volume refers to vast amounts of data, which can be generated, for instance, from cell phones, social media, photographs, etc.
2. Velocity refers to the speed at which these incredible amounts of data are being generated, collected, and analyzed.
3. Variety: refers to the types of data available, ranging from structured data (like names and phone numbers that fit neatly into traditional databases) to mostly unstructured data (such as images, audio, and social media updates).

### Data Ingestion (or Integration) Challenges

Next up is the integration of data.

This is where we decide how to get the data stored on our storage layer. This can vary greatly in complexity from a simple bash script to a sophisticated ETL (Extract Transform Load) or ELT (Extract Load and Transform) platform. Don't worry too much about the differences between these two, they are getting more similar than ever (more in Ch. 3: ETL (Data Warehouses), ELT (Data Lakes), Reverse ETL, CDP (Customer Data Platform), Master Data Management).

I'd define data integration as follows:

> Data integration is the process of combining data from various source systems into a single unified destination. This can be accomplished via manual integration (scripts), data virtualization, and application integration.

Data integration is the process of combining data from various source systems into a single unified destination. This can be accomplished via manual integration (scripts), data virtualization, and application integration.

Compared to data ingestion, as it's called in the book:

> I see ingestion as a close synonym for integration. However, there is a subtle difference as integration is one level higher. Ingestion is the act of integrating, as integration is the concept of integrating data into your data storage solution.

I see ingestion as a close synonym for integration. However, there is a subtle difference as integration is one level higher. Ingestion is the act of integrating, as integration is the concept of integrating data into your data storage solution.

It's hardly connected to the generation part, where we already talked about triggers to closely follow changes, data schema that changes, or the frequency of ingesting it. You could ingest as a stream or just batch.

Data Architecture & Modeling

This is where data modeling and designing a well-thought-through data architecture plays a vital role1. You need to think about how to duplicate data and, if so, on what layer. How do you keep complexity low? What are your business users expecting from your last presenting layer? Do they know a dimensional model?

What are the use cases for the data I’m ingesting? Can I reuse this data rather than create multiple versions of the same dataset?

Before you start ingesting any data, you'd need to be able to answer simple questions like:

- What data do I ingest, and which to exclude explicitly (more is not always more)?
- How frequently do you need them to answer the critical business questions and start your company, for example?
- How will you modify your storage layer? Are you using the Classical Architecture of Data Warehouse with staging-cleansing-core-mart?
- Do your source data change often, meaning something like Data Vault would make sense, or are you choosing a different approach?
- What format (e.g., semi- or unstructured data) is the incoming data? Can my storage layer handle it (or Parquet files can't be directly ingested into MySQL)?
- Are we pulling from a relational database, API, or exported files?
- Who are your users and stakeholders who use your data product?

These questions are heavily connected to the transformation layer or even serving. Let's recall the data lifecycle in its core one more before we dive into the following two layers:

Core of Data Engineering Lifecycle | Image by Fundamentals of Data Engineering (Joe Reis, Matt Housley)

Asking the Right Questions & Domain Knowledge

Sometimes, it's hard to know these questions up front, but sometimes, it's just a matter of talking to the domain experts. In any case, the better the understanding of data engineers and the alignment with the stakeholders you are building it for, the better the solution will get.

### Transformation Challenges

Now, let's go to the fun part for data engineers: automating the Excel business logic into SQL or Python 😉.

It's arguably the most essential part, as the transformation layer is where the business logic gets implemented into the code. The better you do it, the more accurate the numbers will be in your serving layer, usually at a lesser bill.

One significant challenge is keeping the business logic updated. As business needs evolve, the logic must be frequently revised, which can be complex and time-consuming. Understanding and updating business logic often requires extensive discussions, meetings, and a deep understanding of the business processes, making it a collaborative yet challenging endeavor.

Another aspect is the difficulty in selecting the right tool for transformation, given the thousands available. Each tool has strengths and weaknesses, and choosing the most suitable one can be overwhelming but crucial for effective data transformation.

The ever-lasting question is, should we persist the data or define it logically and persist it on demand? A transformation layer with dbt or a Semantic Layer that does it on the fly is becoming popular. Should we create an OLAP cube that offers sub-second query responses, or are we okay with slower query responses?

There are many options, and knowing what is best ahead of time is sometimes challenging. It's also where the data modeling or architecture from earlier comes in handy. It's like having a guiding map instead of mindlessly deciding on tools and techniques. If you are not careful, it might come at a hefty bill later on as you are doing the work multiple times, and that gets you different numbers on your dashboards.

### Serving Challenges

The Serving layer is the most important - not for data engineers - but for our customers and people using our data. This is where we sell our work. You can have the best updated, cleaned data. No one might be interested if you can't adequately present them or miss the right charts.

Therefore, it's essential to tell a story with your data. Make people understand your source data, how you aggregated them, and what the insights are. If people like it, and it's even frequently updated and high quality, you will win.

First, you must choose a suitable format for your stakeholders. Are they a fancy dashboard, a notebook, a data set, or even an app? Or do you need to export into Excel, or are we providing an analytical API for data scientists to connect with Python or R?

Also, be careful from the beginning that your transformation layer architecture and modeling will fit the needs of your chosen tool. Can they work with facts and dimensions, or do they need one big table or relational tables?

Presenting your KPIs and metrics convincingly, which might be the biggest challenge of all, creating a compelling story.

## Undercurrents

Undercurrents are the critical foundation of the lifecycle. Acting across multiple stages of the data engineering lifecycle: security, data management, DataOps, data architecture, orchestration, and software engineering.

Each part of the data engineering lifecycle can adequately function with these undercurrents. Let's find out the challenge of each.

### Orchestration Challenges

The first undercurrent we will focus on is getting more critical than ever with the growing Modern Data Stack and its tools.

But, to talk about challenges, there are several, I see.

When using orchestration technologies, you often need to manage intermediate stages like preparing, wrangling, cleaning, and copying data across systems or formats. This is especially true with unstructured data, which must be structured.

Orchestrators must accurately model dependencies between computations and invoke them at the right time. This involves understanding the sequence and conditions under which various data tasks should be executed. Pipelines as code is another critical concept. Data engineers use languages like Python to define data tasks and dependencies, creating a sophisticated orchestration of data movements and transformations.

Keeping track of what computation has run and managing errors is crucial. Orchestrators need to identify when something goes wrong and understand how to correct these errors, as they will be able to set data quality checkpoints.

The tools used for orchestration have evolved from basic task schedulers like cron to modern orchestrators that integrate with the Modern Data Stack. This evolution reflects a shift from focusing solely on tasks to a more holistic approach involving data assets and complex workflows.

The choice of orchestration tool is critical, as can be understood from these challenges. The same goes for which programming language your orchestration tool will be in. Above all, they need to have good metadata management for monitoring and automation and be open. In the end, it must be integrated into the whole data engineering lifecycle.

We can summarize it to these points:

- Complexity management: simplify the management of complex systems, ensuring seamless data flow and process integration.
- Handling Heterogeneous Architectures: incorporating more diverse data tools, orchestrators adeptly manage and integrate these heterogeneous systems, providing a unified platform for data operations.
- Continuous Data Quality and Error Handling: constantly cleaning out data errors, reacting to new data inputs, maintaining data quality and integrity, and adapting to ongoing changes.
- Data Governance: ensuring compliance and enforcing data governance policies. Help navigate the complexities of legal and ethical data use.

Modern orchestrators underline their growing importance in managing the sophisticated demands of today's data engineering challenges. They are not just tools for scheduling and workflow management but have evolved into comprehensive solutions that cater to the nuanced needs of the data lifecycle.

### Software Engineering Challenges

Data engineering has historically come from database administration and business intelligence with sequential database programs (stored procedures) such as PL-SQL or T-SQL. It's more like giving step-by-step instructions rather than high-level thoughts leading into an object-oriented, highly reusable code base.

With the rise of data engineering, more software engineering patterns such as git-integration, Python, and testability with unit tests found their way into data. This brings us to specific challenges that traditional BI engineers were not faced with but are welcome for the better.

Differences between Data Engineering and Software Engineering

The significant difference between data and software engineering is having no control over the data. As a SW engineer, you are the app toward the users, meaning you control what data you get; you can compile and test all.

In data engineering, it's the opposite. We start with data we can't control and go towards more control later in the layers—more on Data Engineer vs Software Engineer.

Intertwined with software engineering, data engineering presents a dynamic and evolving landscape. The challenge of managing core data processing code remains central at its core. Despite the trend towards higher-level abstractions, the necessity for writing and working core processing code in frameworks like Spark or SQL persists across the data engineering lifecycle. These skills are essential, from data ingestion to transformation and serving.

Another significant aspect is the development of open-source frameworks. Data engineers do not just adopt these tools but actively contribute to them. This continual innovation and specialization process, as seen in the evolution of popular tools, requires a deep engagement with the open source and an understanding of the broader implications of tool adoption.

In streaming data processing, data engineers face unique software engineering challenges. The transition from batch to real-time processing demands a nuanced approach to tasks like joins and windowing. Mastery over various platforms, including function platforms like AWS Lambda or dedicated stream processors like Spark, Flink, and others, becomes crucial in managing these complexities.

Data engineers often engage in general-purpose problem-solving. They encounter unique scenarios requiring custom solutions beyond the confines of specific tools and frameworks. Whether it's developing new connectors for data sources or handling complex data transformations, the ability to apply software engineering principles to these problems is indispensable.

Added to the mix is keeping up with the uprising of new programming languages. Keeping up with Python, Scala, Java, SQL, and emerging Rust is challenging. Each language demands continuous learning, with Python's ease of use, Scala's functional approach, Java's enterprise robustness, SQL's database centrality, and Rust's focus on safety and performance.

The intersection of data engineering with software engineering creates a multifaceted field where continuous adaptation and skill evolution are essential. The challenges that arise from this require technical expertise, strategic foresight, and adaptability, shaping the ongoing development of the data engineering domain.

### Security Challenges

Security is getting more critical. Especially for us data engineers, we have the data that shouldn't be leaked.

The challenge is to keep it protected with the latest security trends, essentially being ahead of the hackers, without compromising innovation. User permission is a big part of security, which can sometimes explode the project scope if you require row-level security.

The balance between security and innovation is challenging. Without innovation, there is no product. But with the needed security precautions, you'll retain all your customers once you get hacked.

For example, this is less critical if you build in-house for larger enterprises.

### Data Management Challenges

The challenges of data management overlap with the orchestration ones. Why? The more orchestration is the control plane (more on this later in Ch. Orchestration), the more it handles end-to-end data governance with discoverability, especially data lineage.

Another overlap in data modeling is very much done in the data transformation layer. And to be clear, the challenge of data management is to focus on the operation and the data lifecycle overall.

Other challenges we have here are:

- Storage and operations: Balancing scalability and cost-efficiency is crucial for storing significant volumes of data while ensuring fast and reliable access.
- Data lifecycle management: Manages data from creation to deletion effectively, ensuring its relevance, accuracy, and compliance with retention policies.
- Data Ethics and Privacy: Protecting sensitive data and following evolving regulatory requirements is critical for maintaining trust and compliance.
- Discovery of data: The more data we have, the better it is to find the right and most updated data. This is where data catalogs can help.

Each of them is a challenge of its own.

### DataOps Challenges

DataOps is a big one. It's close to the Data Engineering Lifecycle but close to the product and the way of working. It intercepts with agile, lean, DevOps, and product thinking.

An excellent illustration of the interceptions of DataOps | Image by The Rise of DataOps

The difference to DevOps is essential here. DevOps aims to improve the release and quality of software products, whereas DataOps does it for the data engineering product.

Infrastructure as code (IaC) is increasingly critical to improve velocity, efficiency, and automation. As open-source tooling and cloud environments become standard, data engineers are employing IaC frameworks for effective deployment and management of infrastructure. This means that with something like Kubernetes, you want your deployments to be just code, versioned, automated, and deployed platform agnostic.

Cloud services, containerization, and tools like Kubernetes and Helm, integrating these elements into DataOps practices needs a deep understanding of dataOps practices. While this automation is critical, its application is challenging. It requires incorporating diverse tools and processes and adapting them. Ensuring consistency and reliability through automation in such a dynamic environment is complex.

Most of DataOps is also a people thing. Have the right culture and mentality, following the same lean and agile product thinking approach and establishing and maintaining a culture of collaboration and continuous improvement. This cultural shift is crucial but difficult, requiring changing long-standing mindsets and practices. Teams must embrace agility and lean principles, often demanding significant organizational changes.

Achieving effective observability and monitoring poses yet another challenge. DataOps demands a proactive approach to monitoring data quality and system performance. However, setting up systems that provide real-time insights without overwhelming the team with false alarms is intricate. Balancing sensitivity and specificity in monitoring is a nuanced task, often requiring iterative refinement.

### Data Architecture Challenges

We've already discussed the importance of Data Engineering Architecture and modeling in this chapter's first two intro sections. They are essential to everything we do, especially in the beginning, before we even start building.

The challenge, obviously, is you need to have lots of experience in building data engineering platforms or solutions; in the best case, you have a strong data architect as part of your team.

Also highly critical is to balance between doing enough architecture beforehand but not too much, as it can also stop you from building a POC or getting started. The data architecture involves many domains, techniques, tools, and frameworks, and you can only know some things upfront.

An excellent architectural illustration is below. That illustrates the challenge of designing a data platform with many moving parts. And all of it is changing rapidly still.

Unified Data Infrastructure and its Architecture | Image by Emerging Architectures for Modern Data Infrastructure

Also, data architectures are in constant change. So, the challenge to be updated with the latest and, e.g., knowing the difference to older architecture principles or challenges (e.g., the BI challenge in the next section) is always a plus.

We will explore data architecture, modeling, and approaches in more detail in Ch. 5: DEDP and Data Modeling Approaches.

## Historic Challenges that Business Intelligence had

Before we close this chapter, let's bring in business intelligence challenges and what data engineering is helping us most. This will help us to put the challenges of data engineers in perspective.

Business intelligence had some substantial problems with speed and transparency. Below is a summary of the issues I experienced or heard people discussing over my BI engineer career. Here is a non-exhaustive list:

- It takes too long to integrate additional sources, and BI engineers are overloaded with work. That's one reason why data silos and analyses are created in every department with disconnected Excel spreadsheets, which are consistently out-of-date and require significant manipulation and reconciliation. The lack of speed is a disadvantage and can be mitigated with Data Warehouse Automation (DWA).
- Transparency is a problem for users other than BI engineers. Only they can see inside the transformation logic mostly hidden in proprietary ETL tools.
- Business people or managers are dependent on BI engineers. There is no easy way to access the ETL or get real-time data.
- The BI department makes it more complicated than it required to be. The impression was that it shouldn't be as complex. For us, it is clear with all the transformations, business logic cleaning, star schema transformation, performance tuning, working with big data, and the list goes on and on. But for non-BI'lers, this is hard to understand.
- Difficulties to handle (semi-) unstructured data formats like JSON, images, audio, video, e-mails, documents, etc. Slice-and-dice is done on aggregated data, while unstructured data like those above could do better. On top of that, these unstructured data stretch the nightly ETL jobs even more as they take longer to process.
- General data availability only once a day (traditionally). We get everything in real-time in our private lives, and everyone demands the same from modern BI systems.

## Conclusion

As we have seen, the field of data engineering has 100s of challenges. It takes a lot of work to keep the overview. Hopefully, it helps when we categorize them as part of the data engineer lifecycle. This way, we can focus on the challenges in each category.

Let's keep them in mind while we explore the different terms introduced over time, their patterns, and how we can use best practices to make the right choice automatically, the data engineering design patterns.

If you want to know more about each term in this chapter, not the challenge, but definitions and what it is, read on in Joe and Matt's book, Fundamentals of Data Engineering, which they explain in detail.

## Join the Discussion

1. More in the Undercurrent Data Architecture Challenges. ↩

More in the Undercurrent Data Architecture Challenges. ↩
