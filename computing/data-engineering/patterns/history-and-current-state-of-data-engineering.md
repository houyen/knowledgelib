---
id: computing/data-engineering/patterns/history-and-current-state-of-data-engineering
canonical_question: How did data engineering evolve from 1970s SQL and BI to Big Data,
  Cloud Data Warehouses, and Vector DBs?
aliases:
- history and state of data engineering
- evolution from BI to data engineering
- Maxime Beauchemin rise of data engineer
- declarative data stacks
- Rust in data engineering
entity_type: engineering_pattern_guide
domain: computing > data-engineering > patterns
last_verified: '2026-09-15'
---

# The History and State of Data Engineering

To set the stage for this book for the upcoming data engineering design patterns, let's discuss the current state of data engineering at the time of writing this book. We'll explore the history of data engineering and the common challenges we face today.

## The History of Data Engineering

Much has been written about data engineering, but how long does it exist, and where does it come from?

When I started my career as a computer scientist in 2003, there was no data engineering, no big data, no data science. Back then, we called it Business Intelligence, Data Warehouse Developer, or ETL Developer here in Switzerland.

So when was the first time data engineering started? I remember vividly when I released my first viral1 article about Data Engineering, the future of Data Warehousing back in March 2018. Since then, new technologies and Data Engineering Concepts have been appearing weekly.

### But how did we get here?

As mentioned, building data warehouses was a thing when I started. The typical questions were Inmon vs Kimball, which architecture you use, and which problem of BI you solve.

But let's do this in order.

Data warehousing is traced back to the 1980s when the word data warehouse was formally defined by Bill Inmon and set the theoretical foundation for data warehousing principles. Bill Inmon is recognized by many as the father of data warehousing.

### SQL

In contrast, SQL became a standard database language in the 1980s. SQL was proposed by Edgar F. Codd in 1970 as a way to abstract the complexities of data storage and retrieval mechanisms, enabling developers to focus on data manipulation and extraction.

Over the years, SQL has evolved to include many types such as Transact-SQL (T-SQL) used by Microsoft SQL Server and Procedural Language/SQL (PL/SQL) used by Oracle Database. These variations extend the functionality of standard SQL, allowing developers to write procedural code, a so-called stored procedure where you can instruct simple order commands, the opposite of the object-oriented paradigm at the time. But you could also create rather complex calculations, and perform stacks of combined SQL queries, almost like an orchestrator today (more on this in  Ch. 4: Orchestration).

### Dimensional Modeling

Later in 1996, Ralph Kimball's The Data Warehouse Toolkit set the foundations of dimensional modeling, a data modeling approach that is used to this day.

### From Business Intelligence to Big Data

I remember a time when massively parallel processing (MPP) databases entered the scene, a computing system that uses many processors (or computers) to perform simultaneous calculations.

Handling higher quantities of data than we would've considered before.  That was the time of the business intelligence engineer and their mission? Manage new bigger data warehouses and data.

In the 2000s, the dot-com bubble had just burst, the start of the tech titans we know today. Companies like Yahoo, Google, and Amazon. But with growth came challenges. Their databases weren’t doing it anymore. They needed something else.

### MapReduce and Hadoop

Enter MapReduce and Hadoop. Google, as ambitious as ever, stepped into the spotlight in the early 2000s. They released not one, but two groundbreaking papers: the Google File System paper in 2003 and the MapReduce paper in 2004.

It was the first blueprint for the big data era. Not to be left behind, Yahoo responded with the Hadoop-distributed file system in 2006. At the same time, hardware prices were plummeting.  This era was heavily influenced by Hadoop - a toolbox for big data engineers. Inside this box were tools like:

- Hadoop Common: Think of it as the essential libraries and utilities; it's the backbone that ensures all Hadoop components seamlessly communicate and work in harmony.
- Hadoop Distributed File System (HDFS): Hadoop's vast storage heart, distributes huge data chunks across a network of machines, ensuring quick access and reliable backup through data replication.
- Hadoop YARN: The maestro of resource management; it harmoniously allocates cluster resources, ensuring every task gets the resources it needs for efficient execution.
- Hadoop MapReduce: The brain of parallel data processing; it breaks down massive data tasks into manageable chunks, processes them simultaneously, and then combines results for swift insights.

That was also the start where BI engineers and early big data engineers had to know different technologies, the traditional relational databases, and now the new open source filesystems. It went from data modeling to software development to mastering Hive and Spark, and the skillset kept expanding.

### Cloud Revolution

And then came the clouds. Remember when Amazon announced AWS? Back then, it felt like the future. Google Cloud and Microsoft Azure weren’t far behind. The game was changing: companies no longer needed to break the bank to own hardware. The cloud was offering flexibility that was unheard of.

In the early 2010s, new ground-taking technologies appeared, from Amazon Redshift to Snowflake. Now, any company, big or small, could harness the same powerful data tools, and they didn’t stop coming. It was the first open-source wave in data engineering—with most famously to this day:

- Orchestrating with Airflow (2014)
- First open-source BI tool Superset (2015)
- Transforming with dbt (2016)

### Entering Data Engineering

That was when the "Big data engineer" grew up. Because of that time, all data felt "big," and big doesn't really quantify how big it is. So, we simply embraced data engineer.

In 2017, Maxime Beauchemin - after having created Airflow and Superset years before – Max published the "Rise of the Data Engineer" - defined for the first time what data engineering meant and explained the shift from business intelligence to data engineering. At that time, we became aware of the rise of the data engineer.

Later in January 2018, he laid out another foundation, the fundamentals and patterns for the start of data engineering, describing Functional Data Engineering.

Later and today, this evolved further into the Modern Data Stack (MDS), or Open Data Stack (ODS) if you use open source only with Open Standards.

## The State of Data Engineering

We have seen in the history of data engineering, in the last few years, the data landscape has witnessed rapid and transformative changes. As businesses continue to use the power of data, jobs, tools, and methodologies evolve to address emerging challenges. This part delves into these developments, offering a bird's-eye view of the present of data engineering before we round it up with a view into the future.

### The State of Data: Observations and Trends

Below you see a list of trends and observations I had over the last two years and some quotes from other data engineers in the field. This will hopefully help us to get the perspective that data engineering has today.

#### 2022

- The declarative approach took center stage across various domains, from Kubernetes' "code as infrastructure" to "orchestration as code" and "integration as code." This approach underpins the rise of the semantic layer—a declarative strategy for metrics definition, and all other domains that more or less have to embrace this approach.
- Metadata trends emerge with a focus on data cataloging, lineage, and discovery.
- The Rust programming language, known for its robustness and performance capabilities, emerged as a potential powerhouse for data-intensive applications. To clarify, while comparing Rust to Apache Spark might be like comparing apples to oranges, the emphasis here is on frameworks like Ballista (Arrow-Rust). Inspired by Spark, Ballista offers advantages like deterministic memory usage (thanks to Rust), superior memory efficiency (sometimes up to 10x less than Spark), and the ability to process more data on a single node due to reduced overhead from distributed computing.
- With the rise of data privacy regulations, including GDPR and CCPA, the emphasis on privacy and governance has heightened across enterprises.

#### 2023

- Admitting the potential loss of control with the Modern Data Stack, data modeling experienced a renaissance. However, leveraging MDS posed challenges, especially in enterprise size.
- AI technologies, especially generative AI models like ChatGPT, oscillated between hype and their real-world applicability. Vector databases like Pinecone and Qdrant became instrumental, competing with traditional databases and more modern ones such as DuckDB with adding columnar-vectorized capabilities.
- The MDS landscape saw significant shifts— from dbt layoffs to its acquisition of Transform and a trend towards lightweight CLIs for improved MDS integration. Overcoming the challenge many people in enterprises face, to utilize the MDS effectively.
- We witness a defragmented, unbundled data stack. The "Open Data Stack" is gaining traction, with increasing alignment in Open Standards. Key integrations include Parquet as the go-to file format, with Iceberg and Delta ruling the Table Format sector. The semantic layer also evolves, making metric definitions in YAML more streamlined.

#### 2024 (and 2025)

- Data engineering is still going strong. Stronger than ever, I'd say, especially since every industry focuses on data. AI won't take our jobs; the opposite, as there will be more chaos, and people who know how to model the data and its flow, understand the business requirements, and can deliver high-quality insights will always be used.
- AI will lead us back to the fundamentals. Someone needs to understand and refactor generated code and simplify. If AI cannot help us anymore, if it's out of knowledge with a specific topic, what then? That's where the fundamentals are essential. Data Modeling, Data Engineering Lifecycle, SQL, and many more.
- What will change, though, is how we learn— how we use the data. Once we've centralized, cleaned, and automated the data, we can do cool stuff with advanced technology. The presentation will be more "fancy," hopefully more insightful, and easier to understand. Throughout my career, a key task has always been to present the data understandably. Because no matter how fancy your pipeline, tooling, or even your profound insights, if the presentation is not up to it or the data quality is terrible, no one cares.
- Small data stack continues to drive more as it saves us money, speeds things up, and simplifies infrastructure wherever possible. Also, new use cases such as embedded analytics DB, running it as part of the data pipeline, etc. are possible.

### Highlights from Other Perspectives

From the "State of Data Engineering 2023":

- Economic slowdowns seemed to influence the demand for data practitioners. However, open-source technologies demonstrated resilience, offering potential growth vectors even amidst downturns.
- On the data lakes front, a clear demarcation between storage and querying/compute engines became evident. Snowflake's collaboration with S3-compatible storage solutions was a highlight.
- Metadata management saw leaders in Apache Hudi, Apache Iceberg, and Delta Lake—all open-source solutions. However, data table formats still lacked uniformity in many organizations.
- With more recognition for git-like data versioning, lakeFS emerged as a pioneer. Analytics engines based on Apache Arrow, such as Arrow Datafusion and InfluxDB, witnessed increasing interest.
- Orchestration and Observability sectors grew, with acquisitions like IBM's purchase of DataBand making headlines. Additionally, the GenAI trend left an indelible mark on data science and analytics usability.

From the "Modern Transactional Stack":

- Transactional databases remain quintessential in application design, ensuring data accuracy. However, modern architectures, notably microservices, introduced additional layers of complexity. Solutions aimed at offering transactional state management in vast distributed apps were on the rise. These fell broadly into two categories: Workflow Orchestration and Database + Workflow.
- The convergence of workflow-centric and database-centric approaches signaled a potential future where these methods might amalgamate, offering holistic solutions to modern app transactional requirements.

From "The Future of Data":

- The narrative underscored the importance of software engineering practices in data teams, leading to efficient management of intricate data structures. The blurring lines between traditionally underserved teams and data capabilities were evident.
- The dream of a unified semantic layer remained, with companies and open-source solutions vying to offer the best possible tools. Yet, the fundamental challenge for data teams—understanding and maintaining business logic—persisted.

## The Future

The data landscape continues to evolve rapidly, blending technological advancements with emerging challenges. As declarative approaches gain prominence, metadata trends flourish, and the focus on privacy sharpens, data modeling offers help in the middle of complexity. As we think of the future of data engineering 🔮, the importance of governance, open standards, and integrated approaches will be the true potential of data.

The story of data is a testament to human innovation, but also to any other field that is loosely governed and starting to find its place. From Business Intelligence to Big Data, this journey shows a history of various challenges and milestones achieved. But as always, the story will never be over. As I'm writing this in the middle of the AI revolution with Generative AI, the hype is real, and there will be new ones. But no matter what happens, under all of them is the need for fresh, organized, and clean data.

This book will try to calm things down and focus on the patterns that were used throughout the different eras. We will focus on repetitive terms, called convergent evolutions, that have appeared through the evolution of data engineering, highlighting their use before and today, and find design patterns that emerge from them.

## Join the Discussion

1. 200 likes back then was a lot 😉. ↩

200 likes back then was a lot 😉. ↩
