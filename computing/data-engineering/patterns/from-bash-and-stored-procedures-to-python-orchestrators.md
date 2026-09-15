---
id: computing/data-engineering/patterns/from-bash-and-stored-procedures-to-python-orchestrators
canonical_question: How did data orchestration evolve from Bash scripts and database
  stored procedures to Python DAGs and workflow orchestrators?
aliases:
- bash vs stored procedures vs python ETL
- data pipeline orchestration evolution
- Airflow Dagster Prefect lineage
- procedural SQL to code orchestrator
entity_type: engineering_pattern_guide
domain: computing > data-engineering > patterns
last_verified: '2026-09-15'
---

# Bash-Script vs. Stored Procedure vs. Traditional ETL Tools vs. Python-Script

The history of data orchestration.

Everyone needs an orchestrator, especially when the stack gets more complicated. But what about cron, a simple Python script, or even a bash one? What about the early stored procedure, SSIS? This chapter will look at common ways of orchestrating your tasks.

But what do you need? Mostly, a higher-level tools/approaches you use to orchestrate/schedule any of your tasks. Could that even be done implicitly? Let's check this out in this chapter.

```python
gantt
    title Evolution of Orchestration
    dateFormat  YYYY-MM-DD
    axisFormat %Y

    section Bash scripts and Cron
    Shell (Unix/CLIs) :cron, 1960-01-01, 365d
    Widespread Adoption of Cron :cron, 1975-01-01, 365d
    Introduction of Bash Scripting :bash, 1989-06-08, 365d
	
    section Stored Procedure
    Early Stored Procedures :sp_early, 1974-01-01, 365d
    Stored Procedures in SQL Databases :sp_sql, 1986-01-01, 365d
    Stored Procedures in Oracle :sp_sql, 1991-01-01, 365d
	
    section Traditional ETL Tools
	Data Transformation Services (DTS) :dts, 1998-01-01, 365d
	Oracle Warehouse Builder (OWB) :owb, 2003-01-01, 365d
    Informatica PowerCenter :informatica, 2004-01-01, 365d
    SSIS :ssis, 2005-01-01, 365d
	
    section Python Scripts & Frameworks
    Python Language Creation :py_creation, 1989-02-20, 365d
    The Rise of Python (NumPy, SciPy, Pandas) : milestone, 2000-01-01, 5110d
    Luigi, Oozie, Azkaban :luigi, 2011-01-01, 365d
    %section Modern Orchestration
    Airflow :py_complex, 2015-01-01, 365d
    Temporal (microservice) :temp, 2016-01-01, 365d
    Dagster (data-aware) :py_complex, 2018-01-01, 365d
	Kestra (YAML) :kestra, 2019-01-01,365d
    Mage.ai (notebook-style) :py_complex, 2022-01-01, 365d
```

> A quick thanks to Dagster for sponsoring this chapter. I use Dagster whenever I can, and I've been a user since almost day one. Dagster bundles and orchestrates the Modern Data Stack, helping data engineers handle complexity in a developer-friendly way. This support makes it possible to share this chapter freely. If that sounds interesting, please visit them on their website below.

A quick thanks to Dagster for sponsoring this chapter. I use Dagster whenever I can, and I've been a user since almost day one. Dagster bundles and orchestrates the Modern Data Stack, helping data engineers handle complexity in a developer-friendly way. This support makes it possible to share this chapter freely. If that sounds interesting, please visit them on their website below.

## Bash Script and Cron

When I started my career, we used a 500-line long bash script that scheduled and started any task. It solved many repetitive tasks once, and everyone could reuse it. For example, it would handle parameter or error handling or upload the data to the FTP server at the end. Tasks that had to be done consistently. It was an easy and powerful way of orchestrating.

### Definition

A bash script is the early orchestration version; it abstracts everything irrelevant to that specific task or transformation. You open a new file and save it with the ending of .sh, add the #!/bin/bash (or a shell of choice) to the beginning, and you are ready.

Used in combination, and still widely used, is Cron and its cron jobs. It's the simplest way to schedule a job in a Unix system, reliably and with a simple command or script. A typical cron expression example 0 8 * * * is used to schedule a job to run daily at 8 AM. This expression is part of a crontab file, which defines the schedule for cron jobs.

The difference between Bash and Shell

Shell scripts are scripts written for a shell, or command-line interpreter, of an operating system. The term shell script is generic and can apply to scripts written for any shell (like sh, csh, ksh, etc.).

Specifically, Bash (Bourne Again SHell) scripts are written for the Bash shell, a more feature-rich successor of the original Bourne shell (sh, referred to with #!/bin/bash). Bash includes enhancements such as better variable handling and arithmetic operations, which aren't standard in basic shell scripts.

I use the term bash and shell scripts interchangeably in my writing.

#### Example Bash Script

Let's look at a complex example of what such a generic bash script looks like to get a better understanding. Below global_run_script.sh was designed for scheduling and running stored procedures or other tasks. It's a multi-purpose tool primarily used for handling files in a database environment.

A simplified version of such a script and how it could look like:

```python
#!/bin/bash

# Initialize variables
application='DEFAULT_APP'
job_status='OK'

# Parse arguments
for arg in "$@"; do
  key=$(echo $arg | cut -d= -f1)
  value=$(echo $arg | cut -d= -f2)
  case $key in
    GRP) ascii_group=$value ;;
    DAT) date=$value ;;
    SYS) system=$value ;;
    SRV) server=$value ;;
    APP) application=$value ;;
  esac
done

# Check mandatory parameter (Group)
if [ -z "$ascii_group" ]; then
  echo "Error: Group parameter is missing."
  exit 1
fi

# Database Interaction (Simplified)
# Assuming a function `query_database` exists for database interaction
work_date=$(query_database "SELECT TO_CHAR(work_date, 'YYMMDD') FROM system_table;")
if [ $? -ne 0 ]; then
  echo "Database query failed."
  exit 1
fi
date=${date:-$work_date}

# Processing ASCII files (Simplified)
echo "Processing started with the following parameters:"
echo " - Group:   $ascii_group"
echo " - Date:    $date"
[ -n "$system" ] && echo " - System:  $system"
[ -n "$server" ] && echo " - Server:  $server"
[ -n "$application" ] && echo " - App:     $application"

# Retrieving ASCII files (Example query)
ascii_files=$(query_database "SELECT file_name FROM ascii_files WHERE group_name = '$ascii_group';")
if [ $? -ne 0 ]; then
  echo "Error retrieving ASCII files."
  exit 1
fi

# Process each ASCII file
for file in $ascii_files; do
  echo "Processing file: $file"
  # File processing logic goes here (e.g., compression, moving, SQL execution)
done

echo "Processing completed."

# Finalization
# Additional cleanup or final steps can be added here
```

Such an script illustrates its capabilities and limitations, below are the key components explained:

1. Initialization: Checks if the script is correctly called and sets up env variables.
2. Parameter Validation: Parsing argument and processes command-line arguments to set various parameters. Ensures the essential parameters are provided. If not, it logs an error and exits.
3. Database Interaction: Connecting to a database using sqlplus and retrieving the work date. Checks for errors and exits if any issues are encountered.
4. File processing:

File Archiving and Preprocessing: Archives older versions of files and prepares new files for processing.
SQL Command Execution: Generates SQL commands to be executed for each file, handles its errors, and logs them if necessary.
Sub-process Execution: Executes generated SQL commands in sub-processes and waits for all sub-processes to finish before proceeding.
5. File Archiving and Preprocessing: Archives older versions of files and prepares new files for processing.
6. SQL Command Execution: Generates SQL commands to be executed for each file, handles its errors, and logs them if necessary.
7. Sub-process Execution: Executes generated SQL commands in sub-processes and waits for all sub-processes to finish before proceeding.
8. Post-Processing Checks: Verifies the output of each sub-process for errors, concatenates parts of split files if needed, and handles disk space errors.
9. File Distribution: Prepares files for different hosts and executes another script for FTP distribution.
10. Finalization: Running another script for job completion tasks.

1. File Archiving and Preprocessing: Archives older versions of files and prepares new files for processing.
2. SQL Command Execution: Generates SQL commands to be executed for each file, handles its errors, and logs them if necessary.
3. Sub-process Execution: Executes generated SQL commands in sub-processes and waits for all sub-processes to finish before proceeding.

The script shows how orchestration was done in the past. It combines scheduling, parameter handling, database interaction, file processing, and error handling in a single script.

Newer orchestration tools we'll explore later offer more robust, feature-rich, and modern alternatives.

### History & Evolution

In the early days of Unix, the operating system was equipped with numerous small, specialized libraries. As complexities increased, methods to order tasks into workflows were needed. Bash scripts aren't designed for that, but it is what was available.

The first shell (Bourne shell sh) and command-line interface (CLI) were introduced in the 1960s and early 1970s with the birth of Unix. Later, Bash (Bourne Again SHell), an enhanced version of Bourne shell, became the go-to for system administration and task automation when introduced in 1989. They offered extensive flexibility and simplicity at the same time. The elegance of combining scripting language with command-line utilities opened up many possibilities for scheduling important work.

Before Bash shell, cron became an indispensable tool for time-based task scheduling in Unix-based systems. Written by Ken Thompson, one of Unix's original creators, cron was added to Unix version 7, released in 1979. Cron revolutionized scheduling tasks, allowing for automation at specific times or intervals. This was particularly crucial for tasks requiring regular execution, like nightly backups or hourly system checks.

Cron initially functioned as a basic scheduler, executing tasks at predetermined times and dates. However, with evolving administrative needs, cron also evolved. Introduced crontab files enhanced flexibility, permitting complex scheduling configurations for functions.

Cron's scheduling capabilities, combined with the execution management of bash scripts, formed an efficient orchestration mechanism. This synergy allowed cron to handle the scheduling while bash scripts took charge of executing and managing tasks. This collaboration laid the groundwork for orchestration for a long time.

Unix Philosophy

Unix Pipes are a way of solving a problem with different Unix libraries, passing the output to the next downstream, making it easy to stack different steps together with its standardized data format (separated lines with \n). They are comparable to bash scripts, where we follow the Unix Philosophy and use the best tool at its task and stack them together. These are the underlying orchestration tools that have survived until today.

### Core Concepts

Bash scripts are known for their versatility, making pinpointing a few core concepts challenging.

However, their scripting flexibility stands out, allowing the combination of various Unix commands and tools to create effective pipelines and workflows. This flexibility is crucial in building complex automation tasks.

Secondly, parameter handling is vital, enabling bash scripts to adapt to various input parameters and making them highly adaptable for different scenarios aligned with the Unix Philosophy. A core to this day is the portability of bash scripts and simple text files, allowing them to be easily integrated and run in different Unix systems.

Cron, on the other hand, enhances Unix scripting with its primary feature, time-based scheduling. It is essential for automating tasks at specific times, such as daily or weekly routines, making it an ideal tool for simple yet effective automation.

The cron syntax provides a robust and flexible way to define scheduling patterns. Another critical aspect of cron is its ability to manage system-wide and user-level ops, offering a versatile approach to cater to a wide range of scheduling needs, whether at a system-wide level or for individual users.

Lastly, cron is known for its minimal overhead, which adds very little strain on system resources while ensuring that tasks are executed as planned, making it a reliable and efficient scheduler.

## Stored Procedure

Stored procedures are another way of orchestration; instead of running on the server or local computer, they run on the database. Each database has its programming language if you will.

For example, PL/SQL  or T-SQL are famous examples of creating stored procedures and orchestrating complex SQL. Before Python was ubiquitous in data, stored procedures were and still are used in specific domains. You might ask why?  Let's find out.

### Definition

A stored procedure is a piece of code that runs natively on the database and comes with a ship that runs solely on the database and comes shipped natively with your database of choice. You can run SQL commands, but on top, I also added glue code that's needed to work with SQL and environments around. For example, fetching its output, removing columns, and using it for the executing query.

Stored procedures are powerful. As mentioned, the most known ones and the ones I grew up with were written in PL/SQL (Oracle) and T-SQL (Microsoft).

In these languages, you can write stored procedures that are usually a sequence of instructions to execute your SQL statement. Unlike Object-Oriented Programming where you define classes, it was all defined in one script used when you couldn't solve it with plain SQL. They are the orchestrator of databases and are similar to bash and cron jobs, although limited to their database and their functionality.

The advantage is their performance, as it comes shipped with the database. Therefore (almost) no network latency, plus the language is optimized for that specific database. While SQL is optimized by the query optimizer, PL/SQL or T-SQL SPs are directly handled by the database engine, handling parallelization, transactions, security, and others. This encapsulation and benefits within the database server itself is what has historically made stored procedures so efficient and powerful, especially for complex data operations.

A simple example from the Oracle docs where we set up a cursor with SQL is that based on a condition (in this case, the 5 first one), insert values to the table. When finished, we commit these rows:

```python
DECLARE
   CURSOR c1 is
      SELECT ename, empno, sal FROM emp
         ORDER BY sal DESC;   -- start with highest paid employee
   my_ename VARCHAR2(10);
   my_empno NUMBER(4);
   my_sal   NUMBER(7,2);
BEGIN
   OPEN c1;
   FOR i IN 1..5 LOOP
      FETCH c1 INTO my_ename, my_empno, my_sal;
      EXIT WHEN c1%NOTFOUND;  /* in case the number requested */
                              /* is more than the total       */
                              /* number of employees          */
      INSERT INTO temp VALUES (my_sal, my_empno, my_ename);
      COMMIT;
   END LOOP;
   CLOSE c1;
END;
```

### History & Evolution

Stored procedures have been fundamental to database management systems (DBMS) for decades. Their history goes back to the early beginnings in the 1970s-1980s when stored procedures originated with the emergence of relational databases.

Systems like IBM's System R, one of the first relational databases, began incorporating stored procedure-like capabilities. The rise of SQL in the 1980s-1990s and the introduction of SQL as a standard database language led to the broader adoption of stored procedures.

They became integral in databases like Oracle (with PL/SQL introduced in 1995) and Microsoft SQL Server (introducing T-SQL). As databases grew in size and complexity, stored procedures became essential for performance optimization in the 1990s-2000s, reducing network traffic and ensuring data integrity through complex transactions.

From the 2000s to the present, with more versatile programming languages like Python and Java, the roles of stored procedures shifted. They remain critical for specific tasks where close database integration is required but are starting to be complemented by external scripts and applications for complex data processing.

### Core Concepts

The core of stored procedures is instructing and managing SQL queries sequentially. Everything runs database-centric, leveraging the compute of the database and reducing network latency.

Stored procedures also translate business logic into code that persists in the outcome as database tables. They can fulfill complex business requirements and, therefore, are very powerful. The downside, and what mostly happened, is that code gets messy. You lose overview as stored procedures can call other stored procedures and end up with the famous spaghetti code.

Transaction management is another core concept; it provides a secure mechanism to ensure data integrity and consistency, especially in multi-user environments. We do not need to worry about it.

## Traditional ETL Tools

Traditional ETL (Extract, Transform, Load) tools have been pivotal in the landscape of data processing and business intelligence. These tools are designed to extract data from various sources, transform it into a format suitable for analysis, and load it into a destination, such as a data warehouse. Among the noteworthy ETL tools are Informatica, IBM Datastage, Cognos, Microsoft SSIS, and Oracle OWB.

### Definition

Traditional ETL tools are software applications designed to facilitate extracting data from various sources, transforming it to fit operational needs, and loading it into a destination database or data warehouse for analysis and reporting.

It was the start of GUI-heavy tools where designing was made easy and streamlined by designing the data flow with drag-and-drop tools. These tools form the backbone of data warehousing and business intelligence (BI) systems, enabling organizations to consolidate data from their internal systems, such as CRM, ERP, etc., that produce critical data, connecting them for a cohesive report.

### History & Evolution

The history of traditional ETL tools traces back to early 1998, a period marked by an explosion in data volume and variety. Organizations wanted consolidated insights from various data sources. The introduction of ETL tools like Data Transformation Services (DTS), OWB, Informatica PowerCenter, and SSIS represented the start of the ETL movement.

These tools focused on batch processing and handling large volumes of data at night. The evolution advanced with enhanced user interfaces, allowing for drag-and-drop ETL management, designing complex processes, and integrating advanced analytics functions.

Throughout the 2000s and into the 2010s, these ETL tools have continuously adapted to new data sources, including cloud-based storage and big data systems, offering more flexible and scalable solutions to meet the growing demand.

### Core Concepts

The core concepts of these underlays are in the early Extract Transform and Load (ETL) approach.  It revolves around extracting data from their sources and connecting them to make sense of it and generate critical business insights.

ETL can be reduced to these three steps:

1. Extract: Connecting to various data sources, ranging from traditional databases to cloud storage and APIs, and extracting the relevant data. This stage is crucial for ensuring data accuracy and completeness.
2. Transform: Once the data is extracted, we add business logic onto it called transformation. This can include cleansing, deduplication, integration, and conversion to ensure the data is in the right format and quality for analysis. The transformation process is often where the most critical logic is applied.
3. Load: The final stage involves loading the transformed data into a target system, typically a data warehouse, data mart, or other analytical database. This step must be highly automated and reliable, ensuring that the data is available for reporting, analytics, and business intelligence applications.

Traditional ETL tools have provided a robust foundation for data integration and transformation. Traditional ETL tools and the concept of ETL remain vital components of today's organizations' data architecture, offering proven capabilities and reliability for complex data integration tasks.

New Data Processing Paradigms: ELT (Extract, Load, Transform)

ELT (Extract, Load, and Transform) represents a newer data integration methodology where data is first extracted (E) from source systems, then loaded (L) as raw data into a target system, followed by transformation (T) within the target. This approach, executed within the destination data warehouse, contrasts with the traditional ETL method, where data undergoes transformation prior to reaching its destination.

The evolution from ETL to ELT has been triggered by the decreasing costs of cloud computing and storage, alongside the emergence of cloud-based data warehouses like Redshift, BigQuery, and Snowflake.

ELT is notably utilized in data lake environments. Airbyte emerged as a benchmark for open-source ELT in 2020, while Fivetran, being the pioneer, operates on a closed-source model. More on ETL vs ELT.

## Python Scripts and Frameworks

ETL processes are evolving. Nowadays, the trend leans towards more programmatic or configuration-driven platforms such as Apache Airflow, Dagster, and Temporal. This shift coincides with growing data demands and the need for quicker data accessibility, steering the trend towards ETL/ELT.

The next iteration, though, is Python. Why Python? Why not JavaScript, Rust, or others? Because Python has dominated the field of data engineering, it is the equivalent of English. It's one of the simplest programming languages and also the language of data after SQL.

Python, as such, is a programming language, but here we speak about Python scripts specifically. As with a bash script, a python script is the next higher level to orchestrate tasks within a script, with any possibilities. Providing us with frameworks specifically made for orchestrations so we stay manageable and stand above the chaos with endless possibilities.

### Definition

A Python script does need a lot of explanation. It is as simple as a script.py file with simple Python instructions, but they can get as complex as you wish, including full-fledged frameworks that do only orchestration.

Below is an example where we read a JSON file that might come from a web API or a configuration file, filter some data as our data processing step, and export it as CSV for working on the next step:

```python
import pandas as pd

# Define the file paths
input_file = 'data.json'
output_file = 'processed_data.csv'

# Read the JSON file directly using Pandas
data = pd.read_json(input_file)

# Process the data
# Example: Filtering rows based on a specific condition
processed_data = data[data['column_name'] > some_value]

# Write the processed data to a new CSV file
processed_data.to_csv(output_file, index=False)

print("Data processing complete. Processed output saved to:", output_file)
```

This can be run with Python installed on your machine or server with python script.py. We use Pandas here to simplify reading files into a table-like format. This showcases already a big strength of Python with its ecosystem; there are libraries available for almost every task, going deep into data, machine learning, and other domains.

Today though, we have even more comfort. There are plenty of data orchestrator frameworks written in Python that handle and provide us with many of the complex capabilities of an orchestrator, such as logging, state management, re-try, backfill, overall UI, and many more.

At their core, an orchestrator framework:

- Triggers computations at the right time
- Models dependencies computations
- Tracks the execution history of computations

In summary, they excel in timing events, identifying and addressing errors, and restoring correct states. Let's have a look at the different types of orchestrators that arose.

#### Different Types of Orchestrators

Today, the market has a lot to offer. Therefore, we also have different types of orchestration.

There are many Python orchestrators but even more types of orchestrators. For example, you'd have an orchestrator exposed as a service within your cloud provider, even severless. You could have a no-code orchestrator that doesn't necessarily need coding; SSIS is an example to name one that has been used for a decade.

There are mostly free open-source orchestrators and simple time-based, like cron or like.

Let's have a look at these types:

- Workflow Orchestration: The beginning of Python orchestration, scheduling tasks.
- Data-aware Orchestration: More than just a task, these orchestrators know the data context. Therefore, you can define what should be done, and the orchestrator can figure out how. It's done in a declarative way. It's similar to what SQL is doing, where the query optimizer is finding the best way.
- YAML Orchestration: The gap between drag-and-drop is YAML. You can build your pipelines with an elegant UI but don't lose the declarative and code-first approach, as these tools generate "code" (YAML). It's the only way to use no-code solutions.
- Implicit Orchestration: Lately, there is an inclination towards avoiding DAGs. It's based on independent message queues. Maybe the ultimate abstraction? (More in later chapter).

In-Line Orchestrators

In-line schedulers within each cloud or open-source tool have an orchestrator, e.g., the data warehouse automation tool, Microsoft Fabric, Databricks, or anyone else. It needs a way of scheduling itself and its tasks in order. But these are not considered true orchestrations to me. These are more a means to an end.

### History & Evolution

The evolution of Python scripts and frameworks in data orchestration mirrors broader shifts in data engineering and software development. Here's a brief overview, capturing the key milestones and trends:

The creation of Python was first released in 1989 by Guido van Rossum, aiming to be a successor to the ABC language. It was designed to be highly readable and to encourage rapid development and integration. The creation of Python laid the groundwork for a language that would later become pivotal in the data engineering and orchestration landscape.

The early 2000s saw the rise of Python in data engineering, significantly influenced by the release of libraries such as NumPy, SciPy, and Pandas. These tools transformed Python into a powerful language for data manipulation, analysis, and processing, setting the stage for its use in data orchestration.

#### Modern Orchestration Frameworks Emerge

Parts of the modern orchestration frameworks in Python.

- Airflow (2015): Apache Airflow, released in 2015 by Airbnb, marked a significant milestone in Python-based orchestration. It introduced a platform for programmatically authoring, scheduling, and monitoring workflows, utilizing Python to define complex data pipelines.
- Temporal (2016):  Stateful, microservices orchestration platform, optimized for even driven application orchestration.
- Dagster (2018)1: Dagster emerged as a data-aware orchestration framework, emphasizing the data context within workflows. It allowed developers to define pipelines aware of the data they process, making orchestration suitable for complex heterogeneous environments.
- Kestra (2019): Introducing a YAML-based orchestration framework, Kestra simplified pipeline creation through declarative YAML configurations, bridging the gap between code-first and no-code approaches.
- Mage.ai (2022): Introducing a notebook-style approach to data pipeline development, catering to the increasing demand for more accessible and flexible orchestration tools that align with data scientists' workflows.
- And many more; check out the Awesome Pipeline List if you want an updated list of tools and frameworks.

#### Shifts in Orchestration

I have noticed different shifts in line with the different types of orchestrators.

Away from managing tasks and workflows to understanding and managing data as assets, which Dagster started at the beginning of 2022 with Software-Defined Asset. Lesser strict task- or DAG-based orchestration towards more holistic and data-centric models. This reflects a broader understanding of data pipelines as components of larger data ecosystems.

As code is the best abstraction to software, to quote Maxime Beauchemin, no-code solutions never really worked. But with YAML-based orchestrators supporting a UI that understands and generates that YAML code, it's possible to support the best of both worlds. This is the shift towards YAML orchestration.

Another third trend I noticed is implicit orchestration, which reduces reliance on explicit DAG definitions. It is mainly used in streaming data pipelines. Instead of a physical orchestrator, the DAG automatically manages dependencies and workflows based on even queues that trigger events, leading to more dynamic and flexible orchestration strategies. I call this implicit orchestration.

#### Future Evolution

The evolution of Python and its frameworks in orchestration is a continuous adaptation to the changing needs of data engineers. From simple script execution to complex, data-aware orchestration platforms.

Python has become the backbone of the Modern Data Stack. It offers bundling and reusability of powerful features to address the broad challenges in the data engineering ecosystem. Although Python lacks speed, as many would say, it mitigates with powerful third-party tools (Pandas, NumPy, Polars, etc.) and new integrations written in Rust that build APIs to port back to the usability of Python. This is another key for Python to survive and stay the primary programming language for orchestration.

### Core Concepts

Core concept orchestration with Python scripts or frameworks, giving you versatility.

Where a simple Python script gives you flexibility, a framework provides much-needed abstraction. Abstractions let you focus on the core business logic or the task. Instead of figuring out how to write locally to disc, or to a data lake, or how to set dependencies correctly, you focus on the actual conversion, transformation, and movement that need to be done.

I sometimes call it microservices on steroids. Why? Because it lets you write independent transformations with the freedom of Python to write what you want (analogy to a microservice), but with the benefit of having standard features such as logging, dependencies, backfill, hand-over data from task to task, and so much more, sorted out by the framework.

Also, microservices are excellent at scaling but could be better at aligning different code snippets or apps. A framework or modern orchestrator handles everything around reusability and abstraction. Each task or step can be its small microservice as part of a more extensive data pipeline or stream of data flow.

The key is that the code is written idempotently, with the technique of Functional Data Engineering. With that in mind, unlike a microservice that always needs to start from zero, a data pipeline can pick up where it left off or run only parts where required.

## The Underlying Patterns

In this chapter, we'll analyze the patterns behind the similar convergent evolution terms of bash crips and cron vs. stored procedures. How traditional ETL tools came into the picture and simple Python scripts to modern frameworks.

We've seen the history of orchestration. Let's recap the common unique characteristics of these orchestration approaches:

- Bash scripts and Cron: Simplest and frictionless scheduling of instructions on any Unix system.
- Stored Procedure: Managing SQL closest to the database without latency.
- Traditional ETL Tools: Human-friendly interfaces for no-less-code approaches.
- Python scripts and Frameworks: Powerful and endless possibilities to run anything with Python.

Let's focus on the patterns they share next.

### Patterns (or Commonalities)

Discuss the commonalities between the topics of the chapter.

- Supporting data engineering lifecycle with data ingestion, processing, and analytics packed into one abstraction, hiding complexity for business and analytical users.
- Abstraction and Reusability: Higher levels of abstraction and reusability. Whether through encapsulating data flow logic in ETL tools, abstracting away the complexities of task scheduling in bash scripts, or leveraging frameworks for common data engineering patterns in Python scripts, the goal is to simplify the orchestration process and make components reusable across projects and teams.
- Integration and Extensibility: Bash scripts and stored procedures provided early examples of how data tasks can be integrated into larger systems and automated processes. Traditional ETL tools built on this by offering connectors and adapters for various data sources and destinations, making it easier to integrate diverse systems. Python scripts and frameworks take this further by facilitating integration through extensive libraries and APIs and being inherently extensible, allowing developers to customize and extend functionality to meet specific project requirements.

### Differences

Highlight the distinct features or methodologies.

Interestingly, the pendulum swung between procedural/sequential vs. object-oriented. Initially, the orchestration was largely procedural or sequential, focusing on the step-by-step execution of tasks (bash scripts, stored procedures). Over time, there's been a trend towards more object-oriented approaches, especially with Python scripts and frameworks, allowing for encapsulation, inheritance, and polymorphism. This shift supports more complex, scalable, and maintainable codebases. With the latest declarative frameworks, we are back to functional step-by-step instructions.

A similar swing he has between imperative and declarative orchestration. As early orchestration had to run imperatively and focus on explicit steps required to achieve a task, newer frameworks heavily use reusability and concentrate on a declarative approach, including YAML, hiding away complex technical implementation and letting us focus on the business logic.

The communication with the integrated stack. For modern tools, use gRPC to integrate and have an efficient, fast way of inter-service communication. Older tools handle communication entirely within the code and snippet.

The change from tool and even database native orchestration to tool agnostic orchestration where you won't define dependencies within a tool but on top of data assets/queues. But you set event-based triggers, allowing a thin orchestration layer.

Data Warehouse Automation vs Directed Acyclic Graph

An Interesting Question: How does the modeling part of Data Warehouse Automation tools (DWAs) (as discussed in previous chapter) compare to a DAG?

One answer is that while DWAs model dimensional data structures for analytical processing, DAGs in an orchestrator model the flow of tasks and their dependencies within data pipelines. One is data modeling, and the other is part of orchestration. Two different domains but similar intentions. It would be interesting to dig deeper.

## Key DE Patterns: Data-Flow Modeling, Business Transformation, Reusability, Implicit Orchestration

The above commonalities and differences underscore the evolution of data orchestration tools, aligning with the growing demands of modern data engineering and analytics. Below, we see four recurring patterns we can extract.

```python
graph LR

    CE_StoredProcedures[CE: Stored Procedures]
    CE_BashCron[CE: Bash / Cron]
    CE_PythonScript[CE: Python Script]
    P_ImplicitOrchestration[P: Implicit Orchestration]
    P_Reusability[P: Reusability]
	P_Transformation[P: Business Transformation]
    P_Orchestration["P: Data-Flow Modeling (Orchestration)"]
    CE_ETL[CE: Traditional ETL Tools]

    CE_BashCron --> P_Orchestration
    CE_StoredProcedures --> P_Orchestration
    CE_StoredProcedures --> P_Transformation
    CE_ETL --> P_Orchestration
    CE_ETL --> P_Transformation
    CE_PythonScript --> P_Orchestration
    CE_PythonScript --> P_Reusability
    CE_PythonScript --> P_ImplicitOrchestration
    CE_PythonScript --> P_Transformation
```

### Data-Flow Modeling

Data-flow modeling is the pattern of orchestration that emerged from the above-mentioned convergent evolutions. It represents a holistic approach to managing and optimizing the movement and transformation of data across systems and platforms. By abstracting the complexities of data processing, data-flow modeling enables engineers to design scalable, resilient, and maintainable data pipelines.

This pattern emphasizes the importance of a well-defined, modular architecture where each component is focused on specific tasks yet seamlessly integrates with others to form a cohesive data processing ecosystem. As a result, it facilitates a more efficient allocation of resources. It supports the rapid adaptation to changing data sources, formats, and processing requirements, ensuring that data engineering practices can keep pace with the demands of modern data-driven organizations.

### Business Transformation

We've already discussed business transformation as a pattern in the previous chapter.

### Reusability

More declarative approaches, where the focus is on what needs to be done rather than how. Asset-aware, optimizing for data dependencies and the lifecycle of data assets. More on reusability as a pattern in the previous chapter.

### Implicit Orchestration

Implicit orchestration emphasizes the flexibility and dynamism of data engineering practices, leaning heavily on event-driven architecture and decentralized data processing principles. This pattern diverges from traditional, centralized orchestration (like DAGs in Airflow) in favor of a model where events trigger actions, closely aligning with the concepts of Software-Defined Assets and Microservices.

At its heart, implicit orchestration is about leveraging event-driven mechanisms (e.g., webhooks, pub/sub systems, work queues, message buses) to automate and manage data flows. This model negates the need for a physical orchestrator, relying instead on a responsive, event-triggered execution environment.  Discussed more on

## Wrapping Up

I hope you enjoy this history of orchestration. We will dig deeper into the key patterns (Data-Flow Modeling, Business Transformation, Reusability, and Implicit Orchestration) and their resulting data engineering design patterns in Chapter 5: DEDP. Feel free to leave a comment below and start the discussion around orchestration.

## Join the Discussion

1. On Sponsorship: While Dagster sponsored this chapter, it's important to note that their inclusion is based on the significant value they bring to the field of data orchestration, not because of the sponsorship. ↩

On Sponsorship: While Dagster sponsored this chapter, it's important to note that their inclusion is based on the significant value they bring to the field of data orchestration, not because of the sponsorship. ↩
