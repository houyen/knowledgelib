---
id: software/system-design/bytebytego-archive-2025/cicd-git-deployment-iac
canonical_question: How do modern software engineering teams manage, automate, and deploy code from local development to production?
aliases:
- software delivery lifecycle and deployment strategies
- git workflow gitflow and git reset guide
- ci cd pipeline stages from planning to production
- blue green vs canary vs ab deployment
- infrastructure as code and gitops landscape
- git vs github differences and commands
entity_type: book_chapter
domain: software > system-design > bytebytego-archive-2025
last_verified: '2026-11-16'
source_type: summary
source: Summary in our own words of 10 articles from the ByteByteGo "2025 Archive" (system design newsletter collection). No text copied.
---

# The Modern Software Delivery Lifecycle: From Version Control to Production Deployment

## TL;DR
Shipping software reliably requires combining local version control, structured branching, automated integration pipelines, and disciplined deployment strategies. Developers track and stage code using Git before pushing to shared platforms like GitHub, where automated CI/CD suites build, inspect, and package releases across isolated test environments. Deployments leverage patterns such as blue-green, canary, or GitOps-driven infrastructure automation to minimize downtime, reduce operational risk, and maintain system availability.

## Version Control Fundamentals: Git, GitHub, and Branching

Source code management starts locally on the developer's machine with Git and extends to centralized collaboration platforms like GitHub. While Git is a free, decentralized utility for recording local revision histories, GitHub provides managed cloud infrastructure, team permissions, issue tracking, and automation integrations.

| Dimension | Git | GitHub |
| :--- | :--- | :--- |
| **Primary Role** | Local version control engine | Cloud hosting and collaboration platform |
| **Maintenance & Ownership** | Open-source (Linux Foundation) | Commercial SaaS (Microsoft) |
| **Operational Scope** | Tracks file revisions on local disks | Centralizes remote repositories and teams |
| **Ecosystem & Tooling** | Command-line interface, local hooks | Web UI, project management, marketplace |
| **Dependency** | Functions completely independently | Requires Git to upload and manage code |

### The Local-to-Remote Git Lifecycle
Local file changes transition across three distinct states before synchronization:
1. **Working Directory:** Contains untracked files or unstaged modifications. Running `git diff HEAD` exposes the gap between this directory and the latest local snapshot.
2. **Staging Area (Index):** Additions prepared via `git add` assemble the specific changes targeted for the next revision.
3. **Local Repository (HEAD):** Executing `git commit -m "message"` seals the staged changes into the local history graph.
4. **Remote Repository:** Executing `git push` exports commits to remote hosts. For incoming updates, `git fetch` downloads remote modifications without merging them, whereas `git pull` fetches and executes a `git merge` directly into the current branch.

### Controlling History with `git reset`
When branch history requires adjustment, `git reset` repositions the branch reference (`HEAD`) backward with varying effects on the index and working directory.

| Command Option | Moves `HEAD` | Updates Index (Staging) | Modifies Working Directory |
| :--- | :--- | :--- | :--- |
| `git reset --soft <target>` | Yes | No | No (Preserves all local and staged edits) |
| `git reset --mixed <target>` (Default) | Yes | Yes | No (Preserves files on disk as unstaged changes) |
| `git reset --hard <target>` | Yes | Yes | Yes (Overwrites working files to mirror target commit) |

### Branch Isolation via Gitflow
For releases requiring strict stability, the Gitflow branching strategy structures collaboration across dedicated tracks:
- **`main`:** Contains production-ready releases.
- **`develop`:** Acts as the persistent integration highway where newly completed features land.
- **Feature branches:** Branch off from `develop` and merge back into `develop` once tests pass.
- **Release branches:** Fork from `develop` when a deployment milestone approaches, isolating stabilization and final bug fixes; completed release branches merge simultaneously into both `main` and `develop`.
- **Hotfix branches:** Created directly from `main` to address urgent production flaws, then merged back into both `main` and `develop` to prevent regression.

## The End-to-End Delivery Pipeline

Moving a feature into production spans structured stages that combine agile project management, quality validation, and progressive delivery across intermediate runtime tiers.

```
[Product Backlog / Jira]
           │
           ▼
[Sprint Planning & Implementation]
           │
           ▼
[Git Commit & GitHub Remote Push]
           │
           ▼
[CI Engine: Jenkins / JUnit / JaCoCo / SonarQube]
           │
           ▼
[Artifact Storage (JFrog) & Dev Deployment (Docker)]
           │
           ▼
[Multiple QA Environments (Functional, Regression, Perf)]
           │
           ▼
[User Acceptance Testing (UAT)]
           │
           ▼
[Scheduled Production Release (SRE / ELK / Prometheus)]
```

1. **Requirements and Planning:** Product Owners document functional criteria as user stories in Jira, which development teams estimate and pull into sprint backlogs.
2. **Development and Submission:** Engineers write code on isolated branches, verify logic locally, and push commits to GitHub.
3. **Automated Continuous Integration (CI):** Continuous integration orchestrators (such as Jenkins) trigger on push events, executing compilation, unit testing (JUnit), test coverage analysis (JaCoCo), and static security/quality analysis (SonarQube).
4. **Artifact Management and Dev Runtime:** Successful artifacts are packaged into containers via Docker and stored in artifact repositories like JFrog, followed by automated deployment to developer verification instances.
5. **Multi-Team QA Testing:** Independent QA environments allow separate teams to execute functional, integration, regression, and load testing concurrently without environment contention.
6. **User Acceptance Testing (UAT):** Builds that pass QA enter UAT to confirm business requirements with end users.
7. **Scheduled Production Delivery and Observability:** Release candidates deploy to production clusters according to release calendars, where Site Reliability Engineers (SREs) track performance and anomalies using tools like Prometheus and ELK.

## Service Deployment Strategies

Rolling out new application code demands choosing an operational strategy that balances infrastructure cost against user risk.

| Strategy | Operational Mechanism | Key Advantage | Inherent Trade-off |
| :--- | :--- | :--- | :--- |
| **Multi-Service** | Updates all dependent services across the environment simultaneously. | Quickest and easiest to execute initially. | Complex dependency chains make troubleshooting and rollbacks risky. |
| **Blue-Green** | Maintains two identical environments; router switches production traffic from Green to updated Blue. | Instant, zero-downtime traffic cutover and trivial rollback. | High expense; requires maintaining two complete production-capacity infrastructures. |
| **Canary** | Directs a tiny percentage of live user traffic to the new revision before wide rollout. | Limits blast radius of bugs; lower infrastructure overhead than blue-green. | Directs production traffic to unproven builds; requires rigorous observability to spot defects. |
| **A/B Testing** | Routes distinct cohorts to concurrent variants running behavioral or business experiments. | Enables live feature comparison and empirical user testing. | Demands careful traffic controls to avoid exposing features accidentally. |

## Infrastructure as Code, Automation, and GitOps

Infrastructure configuration follows the same engineering rigor as application source code, leveraging versioning, testing, and automated reconciliation.

- **Containerization and Orchestration:** Docker packages application runtimes and binaries into standard units, while Kubernetes manages lifecycle scheduling, scaling, and fault tolerance across container groups.
- **Provisioning vs. Configuration:** Dedicated Infrastructure as Code (IaC) solutions such as Terraform and AWS CloudFormation declare, construct, and destroy physical and cloud resources. Configuration managers like Ansible specialize in hardening operating systems, injecting settings, and managing packages post-provisioning.
- **GitOps:** Binds infrastructure definitions stored in Git with automated delivery pipelines, ensuring cloud environments match the declarative state committed to repositories.
- **System Task Automation (Cron):** For scheduled background routines on host systems, Unix/Linux cron automates backups, log rotations, and maintenance scripts. A five-field pattern schedules execution:

```
┌───────────── Minute (0 - 59)
│ ┌───────────── Hour (0 - 23)
│ │ ┌───────────── Day of Month (1 - 31)
│ │ │ ┌───────────── Month (1 - 12)
│ │ │ │ ┌───────────── Day of Week (0 - 6, Sunday to Saturday)
│ │ │ │ │
* * * * * <command-to-execute>
```

## Common Mistakes

- **Running Destructive Git Resets on Uncommitted Work:** Executing `git reset --hard` clears both the staging index and all modified files in the working directory, permanently erasing unstaged changes that were never committed.
- **Budgeting Insufficient Resources for Blue-Green Deployments:** Selecting a blue-green strategy without accounting for cloud budgets leads to failures, as it demands paying for double the server capacity during release transitions.
- **Deploying Canary Builds Without Automated Telemetry:** Pushing canary releases without real-time metrics (e.g., Prometheus monitoring and error rate thresholds) defeats the strategy, leaving bugs undetected until customers report outages.
- **Conflating Infrastructure Provisioning with Configuration Management:** Relying exclusively on configuration tools like Ansible to provision core cloud infrastructure leads to complex state tracking issues better resolved by declarative IaC tools like Terraform or CloudFormation.

---
*Source: Summary in our own words of 10 articles from the ByteByteGo "2025 Archive" (system design newsletter collection). No text copied.*
