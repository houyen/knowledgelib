---
id: computing/data-engineering/patterns/data-engineering-workspace-packaging-pattern
canonical_question: How does the Workspace Packaging Pattern standardize environment
  dependencies, containerization, and deployment for data pipelines?
aliases:
- workspace packaging pattern
- data pipeline containerization Docker
- dependency management data engineering
- reproducible data workspaces
entity_type: engineering_pattern_guide
domain: computing > data-engineering > patterns
last_verified: '2026-09-15'
---

# Data Engineering Workspace Packaging Pattern

Appropriately Packaged Data Engineering Workloads.

When we start creating data platforms as data engineers, where we enable teams or business people to create their analytics faster and with better tooling, one issue that often comes up down the line is packaging. How can a team bring in their custom code and their business logic to the platform? Yes, they can save a long complex SQL inside the BI tool, but what if another team would like to use these insights? What if it's too slow?

Packaging is a pattern that has been used often, especially with the introduction of Docker. It works on every machine, regardless of whether it's Mac, Linux, or Windows. But usually, we need more. We need workspaces for different teams. Workspaces are a declaration of tools and logic a team has built, that can be tested on development, test, and executed on production.

Each team needs to be able to customize their workspaces to their needs, and the workspace must be designed such that it can run anywhere. This pattern is about how to implement and use it in different projects in a generic way that works anywhere.

## Intent

This pattern will help you organize data engineering code and artifacts in a packaged way that can be released, maintained and secured by different teams or people. It's a way of organizing DE artifacts that works well for:

1. Data engineers who develop the automation or tooling,
2. The business people or developers who create the business logic or integration of data
3. And the DevOps team, to deploy it to different environments like dev, test, prod

All of them need to work in sync, and the overlapping artifact is the workspace, which can be packaged (containerized or virtualized, depending on the technology used).

It solves the problem of organization and establishment of security practices so that not only platform admins like data engineers can change failing data pipelines or ship new code.

We can define the pattern in one sentence:

> The data engineering workspace packaging pattern encapsulates team-specific data tools, business logic, and configurations into portable, deployable units that enable consistent execution across environments while allowing teams to maintain autonomy over their data engineering workflows.

The data engineering workspace packaging pattern encapsulates team-specific data tools, business logic, and configurations into portable, deployable units that enable consistent execution across environments while allowing teams to maintain autonomy over their data engineering workflows.

## Origin of the Pattern

So, what are the characteristics of a packaging pattern for data engineering? Let's have a look at the explored convergent evolution terms in this book, giving us some insights into how it consists of:

```python
graph TD
    P_DEPackaging[P: DE Packaging]
    CE_Microservices[CE: Microservices]
    CE_DataMesh[CE: Data Mesh]
    CE_Containerization[CE: Containerization]

    %% Connections
    CE_Containerization --> P_DEPackaging
    CE_Microservices --> P_DEPackaging
    CE_DataMesh --> P_DEPackaging
```

### The History of Packaging DE Artifacts

The history of packaging artifacts in a transformative and effective way is not something that has been around for long. Because data engineering isn't that old yet and the landscape is changing daily, there's no universal way of packaging data engineering work yet. But it definitely starts with the modern data stack and modular systems, where it is hard to deliver any end-to-end increment easily. When zoomed out to the data platform, each tool does one task well but isn't integrated, so it was impossible to package end to end.

But with modern orchestration and Docker, things are changing. We can run data pipelines from loading source data to visualization on different environments with a set of definitions. We can package different tasks into a single DAG and define infrastructure configuratively. Complex workloads can be simplified with one setup.

If we look at the history of orchestration in the first chapter, orchestration across different databases, systems, and programming languages is something recent.

You might ask, "Weren't stored procedures a way of packaging custom logic?" No, in my opinion, because stored procedures only happened in one database system. The code is written as part of a single platform. That's also why it wasn't a problem, and still isn't if you have a single vendor running all your data tasks (and a reason to potentially skip this chapter if that is the case for you 😉).

### Key is Packaging and Containers

Packaging is something that also got popular outside of data engineering. When introduced to the tech-changing technology called Docker, we could all of a sudden "package" code that ran on any machine (at least that's the theory).

The best analogy is the ship containers. With the standardization of container size, shipping across the globe flourished because now everyone could transport anything, anywhere, as long as it fitted into a container of the defined dimension.

Image from  Use Docker and Airflow to deploy your Data Science workflow | by Madan Krishnan.

The challenge is the standardization of a dimension and standard to be agreed upon by everyone. If we find such a package for data engineering, all of a sudden, we can run it anywhere. The equivalent in data engineering is the Declarative Data Stack, where the config is in YAML and the engine can be anything as long as the YAML is defined in a standard way.

Docker applied the same principles to virtualization as containers did to shipping. It standardized it with a so-called "Dockerfile", that has well-defined properties, that then the Docker engine is capable of running on Mac, Windows or Linux. Docker made it easy to create, deploy and run applications by using standardized containers where developers can package applications, libraries and dependencies in a well-defined structure.

Image from  Use Docker and Airflow to deploy your Data Science workflow | by Madan Krishnan.

So the question is, how do we package it for data engineering work specifically? How does the pattern work, and what's important?

## Sub-Patterns and Their Features

Sub-patterns are characteristics of the workspace packaging pattern. They show us the differences within this pattern and visualize its origins from convergent evolution. We can categorize these four as of now:

1. Containerization: Standardize runtime environments with all dependencies for consistent cross-infrastructure execution. Examples: Dockerfile, Declarative Data Stack, DuckDB
2. Service Boundaries: Define clear interfaces enabling independent deployment and loose coupling between team domains. Examples: Microservices, Data Contracts, API Gateways
3. Resource Abstraction: Separate reusable technical utilities from business logic into versioned, shareable packages. Examples: HelloDATA-BE, PyPI packages, dbt packages

We can categorize these into the following sub-patterns: "Runtime Standardization", "Domain Isolation", and "Component Abstraction". Let's go into more detail about each of these patterns and what this means for us data engineers.

### Runtime Standardization Pattern

Standardizing the runtime and its infrastructure is a must when you want to create workspaces that work across data platforms. But how do we do this?

Docker is one way. Docker is a set of platform-as-a-service products that use OS-level virtualization to deliver software in packages called containers. Docker packages can hold complex data engineering requirements into a single Dockerfile. Everyone can run it on any machine.

Think of containers on ships transporting goods. It was the breakthrough with standardized container size that fitted on every boat and harbor. A Dockerfile is the same standard but for software. In some sense, DuckDB and alike compute engines are a simplified version and can be a similar enabler because they let you define and run arbitrary configuration (mostly SQL) on any machine as it's just a small binary that can run anywhere.

The compute and storage separation also helps to allow data engineering workspaces to standardize because that makes the workspace less stateful. Less data means less complexity. No compute implementation, so it gets easier to separate and integrate into different domains, especially with integration into declarative data stacks.

### Domain Isolation Pattern

Isolation and clearly defined interfaces and contracts are another sub-pattern needed for data engineering workspaces to work well. These allow enabling independent deployment and loose coupling between team domains, inspired by microservices and newer data mesh. The most common interfaces are REST APIs, with clearly defined contracts and (database) schema definition.

Teams maintain autonomy over their data engineering workflows. A clear isolation also allows independent deployability for each workspace without affecting others. But with workspaces, we need more flexibility. We need to be able to add a new Python package, or change the way the data can be consumed. The workspace is in a format in which teams can define their tools and business logic.

A common way can be as a git repository. Most important is that it attaches to the platform and the platform can deploy it independently and configuratively to defined environments, like development, test or production.

### Component Abstraction Pattern

Last ingredient that this pattern needs is the way of abstracting away complexity or reducing duplicated code into a workspace. Similar to what PyPI packages allow, to use certain functions, versioned, we can use a versioned workspace, though the workspaces are a more complete implementation of a data engineering solution end-to-end compared to PyPI. But it should be a utility that can be easily deployed and rolled back to an older version in case of error.

You could also think of packaging technically complex code into a data engineering workspace, and more UI and potentially lighter code into visualization workspace.

Easily fix some business code or technical implementation once, and re-deploy across the data platform on different environments with no side-effects.

## Core Problems Addressed

The core problem is that once you have a working data platform with a couple of data tools, it's very hard to push changes in a reliable, isolated, and consistent way. It feels more like patchwork, putting one more bandage here, another one there. We fix pipelines with patches on top of patches, until the next error appears.

Data engineering packaging workspaces approach this more holistically and coherently, giving us the tools to deploy to a data stack in a standardized way.

Let's look at each sub-pattern and check each pattern and the core problem each solves (pattern → core problem):

- Runtime Standardization → Environment inconsistency
- Domain Isolation → Team coupling and change-management overhead
- Component Abstraction → Code duplication and complexity growth

Each impacts a slightly different angle, from "works on my machine" failures to deployment bottlenecks that only data engineers can fix to manual bug fixes everywhere (patchworking).

## Pattern Usage Guidelines

Let's move on to the real use cases, when to use the data engineering packaging workspace pattern and its sub-patterns?

### General Implementation Considerations

As extensively written above, we have three main different types of sub-patterns. The table below shows the differences in purpose, scale, and scope, but also implementation examples and common tools or technologies we can use, showcasing how data engineering workspace packaging patterns appear.

### When to Use

Generally, we can say that the workspace packaging pattern should be considered for a larger organization with multiple teams working on data. A need for consistency and reliable code for dev/test/prod environments is desired or enabling of independence for different teams or domains.

Also when the bottleneck of data engineers needs to be avoided, such packaging strategies with workspaces make a lot of sense.

### When to Avoid

If you are just starting out and unsure yet where your data platform might end up, or you are a very small team of data engineers, it might be the wrong choice to invest a lot of time to make everything perfectly packaged and easy to deploy.

Although a small team might need external help from technical business people, data analysts, domain experts, if that is the case, it could still make sense to spend the time to enable these people to free up the data engineers' time to automate more technical challenges.

If requirements are changing daily or weekly, it's hard to build something more rigid. Also if it's a simple one-off task, it is definitely an overkill to approach it so systematically. Also if you do not have extended DevOps or infrastructure know-how, it might be a big burden to implement something worthwhile.

This is also represented in the common pitfall, that is to over-engineer simple data tasks. Don't use workspace packaging when you need to quickly prototype or when working on exploratory data analysis. Creating containers, versioned packages, and isolated deployments is not worth the effort for simple, one-time analytics tasks.

Other pitfalls include abstracting too early, creating too many small packages, or neglecting documentation which is needed for people to understand how to add to the system through these workspaces.

### Sub-Pattern Selection Guide

Here's a simple decision tree and guide for choosing between sub-patterns based on use case requirements, technical constraints, and team capabilities:

```python
graph TD
    Start[Start] --> Q1{Environment consistency<br/>problems?}
    Q1 -->|Yes| Q2{Multiple deployment<br/>environments?}
    Q1 -->|No| Q3{Multiple teams working<br/>on data pipelines?}
    
    Q2 -->|Yes| RS[Runtime Standardization Pattern<br/>Use when: 'Works on my machine' failures]
    Q2 -->|No| Q3
    
    Q3 -->|Yes| Q4{Teams blocking<br/>each other?}
    Q3 -->|No| Q5{Code duplication<br/>across systems?}
    
    Q4 -->|Yes| DI[Domain Isolation Pattern<br/>Use when: Independent deployments needed]
    Q4 -->|No| Q5
    
    Q5 -->|Yes| CA[Component Abstraction Pattern<br/>Use when: Shared business logic exists]
    Q5 -->|No| NP[No Pattern Needed]

    %% Combination scenarios
    RS --> C1{Also need team<br/>independence?}
    DI --> C2{Also have environment<br/>inconsistencies?}
    CA --> C3{Also need deployment<br/>standardization?}
    
    C1 -->|Yes| COMBO1[Runtime Standardization +<br/>Domain Isolation]
    C2 -->|Yes| COMBO2[Domain Isolation +<br/>Runtime Standardization]
    C3 -->|Yes| COMBO3[Component Abstraction +<br/>Runtime Standardization]

    %% Styling
    classDef endpoint fill:#e8f5e9,stroke:#2e7d32
    classDef decision fill:#e3f2fd,stroke:#1976d2
    classDef no_pattern fill:#fce4ec,stroke:#ad1457
    
    class Q1,Q2,Q3,Q4,Q5,C1,C2,C3 decision
    class RS,DI,CA,COMBO1,COMBO2,COMBO3,NP endpoint
    class NP no_pattern
```

## Pattern Examples

How to solve this is heavily dependent on how your organization is deploying, or generally working. And there are hundreds of different solutions to tackle this. In this part, let's look at some concrete examples.

### HelloDATA-BE: git-Workspace Integration through Airflow

A first implementation that I tried with the open-source HelloDATA BE, where the platform provides an entire data platform end-to-end with tools like dbt, Airflow, and Superset and much more, unified into a single portal. Making it an enterprise-grade data platform.

But the challenge was to add nicely packaged data engineering artifacts. For example, a customer wanted to add an additional dbt transformation, or another one needed to pull data from another REST-API, or a custom python transofrmation. We could create HelloDATA Data Engineering Workspaces.

These workspaces are integrated through Airflow, the orchestrator. The runtime standardization pattern appears through the consistent Dockerfile that each workspace contains and a DAG that will be copied to the data platform. Meaning the external team can define itself how often the DAG is running, what it does and define Python packages needed.

They can run the DAG in the portal and in case of an error, update a git repository independently, the CI/CD pipeline will run and copy the latest version to the defined environment. This showcases the domain isolation that lets teams work independently.

We even created a starter-pack for people to use and add their changes. You can see the structure of this packages containing different parts, but most important is the Airflow DAG and the Dockerfile:

```python
├── Dockerfile
├── Makefile
├── README.md
├── build-and-push.sh
├── deployment
│   └── deployment-needs.yaml
└── src
    ├── dags
    │   └── airflow
    │       ├── .astro
    │       │   ├── config.yaml
    │       ├── Dockerfile
    │       ├── Makefile
    │       ├── README.md
    │       ├── airflow_settings.yaml
    │       ├── dags
    │       │   ├── .airflowignore
    │       │   └── boiler-example.py
    │       ├── include
    │       │   └── .kube
    │       │       └── config
    │       ├── packages.txt
    │       ├── plugins
    │       ├── requirements.txt
    └── duckdb
        └── query_duckdb.py
```

Example structure of HelloDATA-BE workspace

To run it locally you could run Airflow with Astro on your machine, and point the data accesses to local Postgres databases, or remote, if you have access.

You might say, "but isn't that dangerous if people can do whatever they want", or say, "how do they install that in the first place?". Initially, nobody can install or add anything, so the first time it needs someone from the infrastructure team (this could also be automated, but it might be better when someone checks), adding the deployment-configurations to the Kubernetes cluster. Adding the right credentials to source databases for dev/test/prod. We even added a deployment folder, for people to add volume-mounts and other configs, a way to communicate to the DevOps team.

You can find the full documentation on HelloDATA BE Docs, but you can imagine how this can be very empowering for people using the platform, and also relieve the HelloDATA team from changing small things that the external teams know better anyway, but instead can focus on the bigger framework and improvements to the platform.

Above a great overview how such a packaging workspace fits into the bigger data engineering architecture.

### GitLab: Enterprise Workspace Schema Implementation

GitLab provides another compelling example through their publicly available Enterprise Data Warehouse documentation. Their implementation demonstrates how the different sub-patterns can work together in practice.

GitLab's domain isolation pattern manifests through dedicated schemas: COMMON for shared dimensional models, SPECIFIC for application-specific data, WORKSPACE for development and experimentation, and LEGACY for historical systems. This schema separation enables teams to work independently in safe environments while maintaining clear boundaries and governance.

Supporting this schema-based isolation, GitLab implements component abstraction through their dedicated gitlab-data-utils repository—"a repo for commonly used utilities within the data org"—containing shared components like orchestration utils. This centralized approach allows data teams to share reusable components across different projects while maintaining version control.

The runtime standardization pattern is used through their dbt-image repository that packages dbt into standardized Docker images. This ensures consistent dbt environments across different stages of their data pipeline, eliminating environment-specific deployment issues.

Unfortunately, not all repositories remain publicly accessible, but these examples provide valuable insights into enterprise-scale workspace packaging implementation.

### Example Structure and Workflow of Deploying

Best practices for repo and folder structure and the question of mono vs multiple repositories.

Some try to keep everything in one mono-repo:

> Following to see what others do, but I keep dbt, pipelines, devops, ad-hoc queries, IaaC, and documentation in one repo.
On mobile so I can’t share a proper directory structure, but it’s something like: Analyses Docs Devops Macros Models Pipelines Scripts Seeds Snapshots Tests.

Following to see what others do, but I keep dbt, pipelines, devops, ad-hoc queries, IaaC, and documentation in one repo.

On mobile so I can’t share a proper directory structure, but it’s something like: Analyses Docs Devops Macros Models Pipelines Scripts Seeds Snapshots Tests.

Another organization by another Reddit user called u/jfftilton is to structure it into a mono repository as well - he says organization depends. He likes to go the mono repository route as much as possible.

The below is assuming a single team is doing all of the work extract load and transformation. Some organizations separate these two functions.

```python
├── pyproject.toml
├── README.md
├── src
│   ├── extract_load
│   ├── pipelines
│   └── utils
├── tests
│   └── __init__.py
└── transform
```

This is how he created the repo. This is a common structure, and compared to the above HelloDATA approach, is missing the infrastructure integration with Docker or others.

The Reddit user goes on to say that he starts a project using pyproject then has his extract_load scripts in a directory generally separated out by source or maybe type such as source1 or SQL Server (generally uses dlt for this) then he has his dbt project labeled transform and lately has been using prefect pipelines in the pipelines directory. He schedules everything in GitHub actions.

And then setting up three database environments that sets up and run with three branches:

```python
dev_branch -> dev_db
qa_branch -> qa_db
main_branch -> prod_db
```

The code review is performed from a feature into the dev branch and then automatically promotes to as after X successful pipeline runs then to main branch after y successful runs.

This shows that there are many different ways of organizing your data engineering workload, but not all of them provide the full runtime integration, domain isolation or abstraction.

## Trade-offs

The data engineering workspace packaging pattern offers many advantages, but with it comes also some maintenance burden that should not be underestimated. It needs a thorough end-to-end integration in the full data stack, without that, it makes workspaces less useful. But that also requires building the architecture on top of that philosophy and a heavy investment into it.

Again, if you have a larger enterprise, and want to enable teams themselves, I believe there's no way around it. A centralized data platform, with the ability to develop, test and create new features in dedicated workspaces, isolated and abstracted away.

Full integration happens through infrastructure deployment integration, which requires that your data platform is already built on top of Infrastructure as Code or as a Declarative Data Stack with Kubernetes, Terraform or alike. With that, the runtime integration with compute or integration such as HelloDATA-BE with its Airflow integration as engine did, is possible.

The learning curve might be another trade-off. The pattern might introduce high complexity with integrated toolchain and skills ranging from containerization, CI/CD pipelines, and infrastructure concepts. These concepts are sometimes too steep for data analysts who are usually writing SQL queries, needing to understand Docker, git, and deployment processes.

When issues arise in production, debugging (and as well testing) becomes much harder as problems can occur at multiple layers - within the workspace container, in the orchestration layer, or in the infrastructure deployment. The abstraction that makes workspaces portable also makes it harder to diagnose problems, especially for teams less familiar with containerized environments. This can be mitigated by great implementations and clear interfaces that force failures within workspaces to be easier to debug.

It could lead to performance overhead due to more levels of computations and the isolation mechanism. Especially on the development side, where CI/CD pipelines need to run to build the new workspace and its artifacts to run and test on development. Especially if you have frequent changes and running many concurrent workspaces.

While workspaces certainly solve some dependency issues, they can create new ones. Managing versions across multiple workspaces, ensuring compatibility between shared components, and handling dependency conflicts between different teams' requirements can become a challenge. Though these can be mitigated with Docker where dependencies can be mostly defined and isolated within the workspace. Only the interfaces need to be aligned.

Secret distribution needs a clear concept. Usually tools like Vault (HashiCorp) are used, or similar products, to commit the secrets hashed to the workspace. But still, source databases are usually not known by workspace developers, so there needs to be a secret integration that ensures consistent security policies across workspaces.

## Related Patterns

As identified in the Convergent Evolution -> Design Design Patterns Overview, the data engineering design pattern based on the workspace packaging pattern  is Declarative Orchestration and Open Data Platform - Lakehouse.

```python
graph LR

    DP_DeclarativePipeline[DP: Declarative Orchestration]
    DP_OpenData[DP: Open Data Platform - Lakehouse]
    P_DEPackaging[P: DE Packaging Workspaces]
	
	P_DEPackaging --> DP_DeclarativePipeline
    P_DEPackaging --> DP_OpenData
```

Previous chapter, Monolith vs. Microservice in a Modern Data Stack, about the difference between monolith and microservices architecture with Data Mesh contains related content if you haven't read it yet.

Do you have other use cases of implementing or applying the workspace packaging pattern for data engineering workloads? Do you see other characteristics or advantages of this pattern? Please let me know in the comments below.

- DevOps time is eating data engineering: "I recall 10 years ago when we patiently waited for the data scientist to arrive and solve all our problems. Today, it's almost the same, yet we wait for a DevOps person who knows how to deploy, manage, and release new versions in a non-disruptive way." Workspace packaging addresses this by making deployment self-service, freeing data engineers to focus on data problems rather than infrastructure. The State of DevOps in Data Engineering
- The Data Mesh workspace problem: After implementing Data Mesh at multiple companies, a pattern emerges: "Having a strong central platform/governance team that sets the standards and provides the tooling, and then letting domains build data products on top of that, is the only setup that doesn't blow up over time." Workspaces provide the standardized tooling that prevents "every domain ending up with different tools, workflows, and security assumptions." Data Mesh
- uv and modern Python packaging: The Python packaging landscape is rapidly improving. uv (Python packaging in Rust) and Mise are simplifying environment management, making workspace standardization easier than ever. The days of "dependency hell" are diminishing with modern tooling.

DevOps time is eating data engineering: "I recall 10 years ago when we patiently waited for the data scientist to arrive and solve all our problems. Today, it's almost the same, yet we wait for a DevOps person who knows how to deploy, manage, and release new versions in a non-disruptive way." Workspace packaging addresses this by making deployment self-service, freeing data engineers to focus on data problems rather than infrastructure. The State of DevOps in Data Engineering

The Data Mesh workspace problem: After implementing Data Mesh at multiple companies, a pattern emerges: "Having a strong central platform/governance team that sets the standards and provides the tooling, and then letting domains build data products on top of that, is the only setup that doesn't blow up over time." Workspaces provide the standardized tooling that prevents "every domain ending up with different tools, workflows, and security assumptions." Data Mesh

uv and modern Python packaging: The Python packaging landscape is rapidly improving. uv (Python packaging in Rust) and Mise are simplifying environment management, making workspace standardization easier than ever. The days of "dependency hell" are diminishing with modern tooling.

## Join the Discussion
