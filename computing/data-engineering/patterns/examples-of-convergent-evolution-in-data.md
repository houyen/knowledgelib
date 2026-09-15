---
id: computing/data-engineering/patterns/examples-of-convergent-evolution-in-data
canonical_question: What are concrete examples of convergent evolution across modern
  data tools and traditional architectures?
aliases:
- examples of convergent evolution
- modern data stack vs traditional BI
- convergent architectural patterns in data
entity_type: architectural_concept_guide
domain: computing > data-engineering > patterns
last_verified: '2026-09-15'
---

# Convergent Evolution and its Patterns

After we learned what convergent evolution is and its relation to data engineering, Let's look at concrete examples and how these different evolutions have arisen.

## Convergent Evolution -> Pattern -> Design

We'll navigate from the bottom up, where the bottom is the terms we use or hear in our day-to-day work, the CEs. We'll group them and analyze history, similarities that lead to DE patterns, and later in chapter 5, data engineering design patterns.

Below is a first look at the convergent evolutions, their pattern, and the data engineering design pattern we will explore in this book. This visualization also shows how the different terms proceed into patterns and then design patterns.

Navigation Map

Use this diagram throughout the book as your navigation map

This comprehensive visualization shows how all chapters connect:

- CEs (Convergent Evolutions) → Technologies and approaches you know
- P (Patterns) → Common patterns that emerge from similar CEs (Chapter 5: DEP)
- DP (Design Patterns) → Best practice solutions (Chapter 6: DEDP)

How to use this map:

- Find familiar technologies (CEs) you work with
- Follow the arrows to discover relevant patterns
- Navigate to the design patterns that solve your challenges
- See the big picture of how everything connects

```python
flowchart LR
    %% Using subgraphs to organize CE -> P -> DP flow
    %% Connections can cross subgraph boundaries

    subgraph CE["Convergent Evolutions (Technologies)"]
        direction TB
        CE_MV[MV]
        CE_OBT[OBT]
        CE_dbt[dbt table]
        CE_DWA[DWA]
        CE_BITool[BI Tool]
        CE_SemanticLayer[Semantic Layer]
        CE_ModernOLAP[Modern OLAP]
        CE_TraditionalOLAP[Traditional OLAP]
        CE_DataVirtualization[Data Virtualization]
        CE_ODS[ODS]
        CE_MessageQueue[Message-Queue]
        CE_ETL_Tools[Traditional ETL]
        CE_REVERSE_ETL[Reverse ETL]
        CE_MDM[MDM]
        CE_CDP[CDP]
        CE_DataCatalog[Data Catalog]
        CE_DataLake[Data Lake]
        CE_DataWarehouse[Data Warehouse]
        CE_SchemaEvolution[Schema Evolution]
        CE_NoSQL[NoSQL]
        CE_CRDT[CRDT]
        CE_DataContract[Data Contracts]
        CE_Containerization[Containerization]
        CE_StoredProcedures[Stored Procedures]
        CE_BashCron[Bash / Cron]
        CE_PythonScript[Python Script]
        CE_Microservices[Microservices]
        CE_Monolith[Monolith]
        CE_DataMesh[Data Mesh]
        CE_ExportingCSVs[Exporting CSVs]
        CE_IaC[IaC]
    end

    subgraph P["Patterns (DEP - Chapter 5)"]
        direction TB
        P_CachingDisk[Cache]
        P_ELT[ELT]
        %% kafka, messagequeues etc.
        P_ShortTerm[Short-term Storage] %% Short-term storage (old: In-Memory connections)
        P_TableFormats[Open Table Format]
        P_DataSharing[Data Sharing]
        P_ChangeMgmt[Change Management]
        P_LocalFirst[Local First]
        P_DataAsset[Data Asset]
        P_DataLineage[Data Lineage]
        P_CostOptimization[Cost Optimization]
        P_DEPackaging[DE Packaging]
        P_Streaming[Streaming]
        P_ImplicitOrchestration[Implicit Orchestration]
        P_ModernDataStack[Modern Data Stack]
        P_Reusability[Reusability]
        P_Orchestration[Orchestration]
        P_DataVersion[Data Versioning]
        P_DevOps[DevOps in DE]
        P_DataModeling[Data Modeling] %% more technical compared to business transform ETL
        P_Transformation_ETL[Business Transform] %% more business related to model for business
        P_CDC_SCD[CDC and SCD]
        P_IncrementalProcessing[Incremental Processing]
        P_DataQualityTesting[Data Quality]
        P_IdempotencyRetry[Idempotency]
        P_ObservabilityMonitoring[Observability]
        P_DataPartitioning[Data Partitioning]
        P_ReverseETL_Activation[Reverse ETL Activation]
        P_ClientServer[Client-Server Architecture]
        P_WAP[Write-Audit-Publish]
    end

    subgraph DP["Design Patterns (DEDP - Chapter 6)"]
        direction TB
        DP_DynamicQuerying[Dynamic Querying]
        DP_OpenData[Open Data Platform]
        DP_CostManagement[Cost Management]
        DP_DeclarativeGovernance[Enterprise Governance]
        DP_DeclarativePipeline[Declarative Orchestration]
        DP_RealTime[Real-Time Platform]
        DP_Navigating_LLMs[Navigating LLMs]
        DP_DimensionalModeling[Dimensional Modeling]
        DP_OBT_Medallion[OBT vs Medallion]
        DP_IntegratedPlatform[Integrated Platform]
        DP_StratifiedDataFlow[Stratified Data Flow]
    end

    %% ========================================================================
    %% CE -> P Connections
    %% ========================================================================

    %% Cache connections
    CE_MV --> P_CachingDisk
    CE_OBT --> P_CachingDisk
    CE_TraditionalOLAP --> P_CachingDisk
    CE_dbt --> P_CachingDisk
    CE_ModernOLAP --> P_CachingDisk
    CE_ODS --> P_CachingDisk
    CE_SemanticLayer --> P_CachingDisk
    CE_DataWarehouse --> P_CachingDisk

    %% Data Lineage
    CE_ETL_Tools --> P_DataLineage
    CE_SchemaEvolution --> P_DataLineage

    %% Table Formats & ELT
    CE_DataLake --> P_TableFormats
    CE_DataLake --> P_ELT

    %% Write-Audit-Publish (WAP)
    CE_DataLake --> P_WAP
    CE_dbt --> P_WAP

    %% Transformation connections
    %% TODO: ETL and data modeling is very close, hard to say when it's either or
    CE_MV --> P_Transformation_ETL
    CE_dbt --> P_Transformation_ETL
    CE_OBT --> P_Transformation_ETL
    CE_DataWarehouse --> P_Transformation_ETL
    CE_DataLake --> P_Transformation_ETL
    CE_CDP --> P_Transformation_ETL
    CE_ETL_Tools --> P_Transformation_ETL
    CE_StoredProcedures --> P_Transformation_ETL
    CE_PythonScript --> P_Transformation_ETL
    CE_SemanticLayer --> P_Transformation_ETL
    CE_TraditionalOLAP --> P_Transformation_ETL 
    CE_BITool --> P_Transformation_ETL 
    
    %%short-term and data modeling
    CE_ODS --> P_ShortTerm
    CE_MessageQueue --> P_ShortTerm
    CE_ModernOLAP --> P_DataModeling
    CE_DataWarehouse --> P_DataModeling

    %% Change Management
    CE_SchemaEvolution --> P_ChangeMgmt
    CE_DataContract --> P_ChangeMgmt
    CE_NoSQL --> P_ChangeMgmt
    CE_CRDT --> P_ChangeMgmt

    %% Other patterns
    CE_CRDT --> P_LocalFirst
    CE_DataContract --> P_DataVersion
    CE_SchemaEvolution --> P_DataVersion
    CE_DataContract --> P_DataAsset
    CE_DataWarehouse --> P_CostOptimization

    %% DE Packaging
    CE_Containerization --> P_DEPackaging
    CE_Microservices --> P_DEPackaging
    CE_DataMesh --> P_DEPackaging

    %% Client-Server Architecture
    CE_Containerization --> P_ClientServer
    CE_Microservices --> P_ClientServer

    %% Reusability
    CE_MV --> P_Reusability
    CE_SemanticLayer --> P_Reusability
    CE_Microservices --> P_Reusability
    CE_MDM --> P_Reusability
    CE_PythonScript --> P_Reusability
    CE_DWA --> P_Reusability
    CE_dbt --> P_Reusability
    CE_DataVirtualization --> P_Reusability

    %% Modern Data Stack
    CE_Monolith --> P_ModernDataStack
    CE_DataMesh --> P_ModernDataStack
    CE_Microservices --> P_ModernDataStack

    %% Implicit Orchestration
    CE_MessageQueue --> P_ImplicitOrchestration
    CE_DataMesh --> P_ImplicitOrchestration
    CE_Microservices --> P_ImplicitOrchestration
    CE_PythonScript --> P_ImplicitOrchestration

    %% Orchestration
    CE_ETL_Tools --> P_Orchestration
    CE_StoredProcedures --> P_Orchestration
    CE_BashCron --> P_Orchestration
    CE_PythonScript --> P_Orchestration

    %% Data Sharing
    CE_REVERSE_ETL --> P_DataSharing
    CE_MDM --> P_DataSharing
    CE_ExportingCSVs --> P_DataSharing

    %% DevOps
    CE_IaC --> P_DevOps

    %% Data Modeling
    CE_OBT --> P_DataModeling
    CE_DataWarehouse --> P_DataModeling
    CE_dbt --> P_DataModeling

    %% CDC and SCD
    CE_ODS --> P_CDC_SCD
    CE_ETL_Tools --> P_CDC_SCD

    %% Incremental Processing
    CE_dbt --> P_IncrementalProcessing
    CE_ETL_Tools --> P_IncrementalProcessing

    %% Data Quality
    CE_DataContract --> P_DataQualityTesting
    CE_dbt --> P_DataQualityTesting

    %% Idempotency
    CE_ETL_Tools --> P_IdempotencyRetry
    CE_MessageQueue --> P_IdempotencyRetry

    %% Observability
    CE_DataCatalog --> P_ObservabilityMonitoring

    %% Data Partitioning
    CE_DataWarehouse --> P_DataPartitioning
    CE_DataLake --> P_DataPartitioning

    %% Reverse ETL Activation
    CE_REVERSE_ETL --> P_ReverseETL_Activation
    CE_CDP --> P_ReverseETL_Activation

    %% ========================================================================
    %% P -> P Connections
    %% ========================================================================
    P_DataLineage --> P_ObservabilityMonitoring

    %% ========================================================================
    %% P -> DP Connections
    %% ========================================================================

    %% Dynamic Querying
    P_CachingDisk --> DP_DynamicQuerying
    P_ShortTerm --> DP_DynamicQuerying
    P_DataModeling --> DP_DynamicQuerying
    P_Transformation_ETL --> DP_DynamicQuerying

    %% Open Data Platform
    P_TableFormats --> DP_OpenData
    P_Transformation_ETL --> DP_OpenData
    P_DataLineage --> DP_OpenData
    P_DEPackaging --> DP_OpenData
    P_DataVersion --> DP_OpenData
    P_DataSharing --> DP_OpenData
    P_ModernDataStack --> DP_OpenData
    P_DevOps --> DP_OpenData
    P_WAP --> DP_OpenData

    %% Cost Management
    P_CostOptimization --> DP_CostManagement

    %% Declarative Governance
    P_DataLineage --> DP_DeclarativeGovernance
    P_DataVersion --> DP_DeclarativeGovernance
    P_ChangeMgmt --> DP_DeclarativeGovernance
    P_DataQualityTesting --> DP_DeclarativeGovernance
    P_ObservabilityMonitoring --> DP_DeclarativeGovernance

    %% Declarative Pipeline
    P_DataLineage --> DP_DeclarativePipeline
    P_DEPackaging --> DP_DeclarativePipeline
    P_DataAsset --> DP_DeclarativePipeline
    P_ModernDataStack --> DP_DeclarativePipeline
    P_Reusability --> DP_DeclarativePipeline
    P_Orchestration --> DP_DeclarativePipeline
    P_IdempotencyRetry --> DP_DeclarativePipeline

    %% Real-Time Platform
    P_ImplicitOrchestration --> DP_RealTime
    P_Streaming --> DP_RealTime
    P_CDC_SCD --> DP_RealTime

    %% Navigating LLMs
    P_Orchestration --> DP_Navigating_LLMs

    %% Dimensional Modeling
    P_DataModeling --> DP_DimensionalModeling

    %% OBT vs Medallion
    P_DataModeling --> DP_OBT_Medallion
    P_IncrementalProcessing --> DP_OBT_Medallion
    P_DataPartitioning --> DP_OBT_Medallion

    %% Integrated Platform
    P_ReverseETL_Activation --> DP_IntegratedPlatform
    P_ClientServer --> DP_IntegratedPlatform

    %% Stratified Data Flow
    P_Orchestration --> DP_StratifiedDataFlow
    P_Transformation_ETL --> DP_StratifiedDataFlow
```

Latest Update: 2026-01-25

Reorganized with flowchart subgraphs for better rendering. CE, P, and DP nodes are now grouped into columns with cross-subgraph connections preserved.

In the following chapters, we'll dive deeper into these convergent evolutions.

## Join the Discussion
