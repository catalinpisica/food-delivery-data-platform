# AGENTS.md

## Project purpose

This repository is a **learning-first, end-to-end data engineering project** that simulates the data platform of a food-delivery company.

The project has two equally important goals:

1. **Learning** — develop practical understanding of data engineering concepts and technologies beyond dbt.
2. **Portfolio / interview demonstration** — produce a coherent, well-documented project that can be discussed and demonstrated in future Data Engineering interviews.

The project must not become a collection of technologies added for CV value. Every component should solve a clearly defined engineering problem.

The current agreed technical architecture is documented in [`architecture.md`](architecture.md).

---

## Learning-first instructions

This project is primarily intended to teach the user data engineering.

AI assistants working on this repository must optimize for **understanding**, not speed of completion.

### Explain before implementing

Before introducing a new concept, technology, command, configuration, or architectural pattern:

1. Explain what problem it solves.
2. Explain how it works conceptually.
3. Explain why it is appropriate here.
4. Explain relevant alternatives where useful.
5. Only then move to implementation.

Do not assume that familiarity with a technology name means understanding of the underlying concept.

Examples of concepts that should be explained when encountered include:

* Git working tree, staging area, commits, branches and remotes
* Docker images, containers, volumes, networks and ports
* OLTP vs OLAP
* primary keys and foreign keys
* indexes
* incremental ingestion
* watermarks
* idempotency
* Kafka topics, partitions, offsets and consumer groups
* event time vs processing time
* delivery semantics
* late-arriving and out-of-order events
* dead-letter queues
* Spark transformations, actions and lazy evaluation
* Spark partitions and shuffles
* Structured Streaming
* checkpointing and watermarks
* object storage
* Parquet
* columnar storage
* partition pruning
* small-file problems
* dimensional modeling
* facts and dimensions
* grain
* surrogate keys
* Slowly Changing Dimensions
* orchestration
* retries and backfills
* data quality
* lineage
* CI/CD

### Avoid copy-paste development

Do not default to providing large finished solutions for the user to blindly copy.

Prefer this learning loop:

```text
Explain concept
      ↓
Show a small example or skeleton
      ↓
User implements
      ↓
Review implementation
      ↓
Explain mistakes / improvements
      ↓
Continue
```

When practical, ask the user to write meaningful pieces themselves.

Small syntax examples, configuration fragments, pseudocode and skeletons are encouraged when they help understanding.

Full implementations are appropriate when:

* the user explicitly asks for one;
* the implementation is mostly boilerplate;
* the user has already attempted the task and needs a reference solution;
* writing it manually would add little educational value.

Even when providing complete code, explain the important parts rather than treating the code as self-explanatory.

### Explain commands

Do not provide terminal commands as unexplained magic.

For important commands, explain:

* what executable is being called;
* what important arguments or flags mean;
* what state the command changes;
* what output the user should expect.

There is no need to repeatedly explain a command that the user already understands unless something new about it matters.

### Encourage debugging

Errors are part of the learning process.

When something fails:

1. inspect the error;
2. explain what the error means;
3. identify likely causes;
4. guide the user through diagnosis;
5. avoid immediately replacing the user's implementation with a finished solution.

Teach debugging methodology rather than only fixing the immediate error.

### Check understanding where useful

For important concepts, occasionally ask the user to predict what will happen or explain a concept back before continuing.

Do not turn every step into a quiz. Use this selectively where it reinforces important engineering concepts.

---

## Engineering principles

### Every technology needs a reason

Do not add a technology solely because:

* it is popular;
* it appears frequently in job descriptions;
* it would look good on a CV;
* it appears in another reference architecture.

Every component must have a clearly documented responsibility.

For example:

* Kafka exists to model event-stream ingestion.
* Spark exists to teach distributed batch and streaming processing patterns.
* dbt exists for warehouse-side analytics/business transformations.
* ClickHouse exists as the analytical warehouse.
* Kestra exists to orchestrate discrete workflows.

If a technology no longer provides meaningful learning or architectural value, removing it is acceptable.

### Prefer the simplest useful implementation

Start with the simplest version that demonstrates the concept correctly.

Add complexity only when there is a concrete reason.

Examples:

* one Kafka broker before considering multi-broker clusters;
* one Spark worker before considering a larger cluster;
* one deliberate SCD Type 2 dimension rather than making every dimension SCD2;
* simple logging before adding a full observability stack.

### Correctness before scale

The project is not a benchmark.

Prioritize:

* correctness;
* reproducibility;
* failure handling;
* data modeling;
* data quality;
* architecture;
* understanding.

Do not optimize prematurely for massive data volumes.

### Be explicit about trade-offs

Architectural decisions should include their trade-offs.

If a technology is being used for learning even though the project scale does not technically require it, say so explicitly.

Do not manufacture false scalability claims.

---

## Technical constraints

### Cost

The project must remain **usable without paid cloud infrastructure**.

The goal is to eliminate the possibility of surprise AWS, GCP, Azure, Snowflake, Databricks or similar usage bills.

The core project must not require:

* AWS;
* Google Cloud;
* Microsoft Azure;
* Snowflake;
* Databricks;
* paid SaaS infrastructure.

External APIs used by the project must have a genuinely usable free option for the project's small workload.

If a proposed component introduces billing risk, discuss it before adding it.

### Development environment

The primary development environment is:

```text
GitHub repository
      ↓
GitHub Codespaces
      ↓
Docker / Docker Compose
      ↓
project services
```

The project must remain portable to a normal personal laptop later.

Do not introduce Codespaces-specific architecture when a normal containerized solution can work in both environments.

### Resource usage

Codespaces resources are limited.

The project should therefore:

* use modest synthetic datasets;
* avoid keeping unnecessary services running;
* support starting subsets of services when practical;
* avoid unnecessary memory-heavy components;
* keep generated artifacts disposable and reproducible.

### Data scale

Large datasets are not a goal.

The simulator should support configurable scales such as:

```text
tiny  → hundreds of orders
dev   → thousands of orders
demo  → tens of thousands of orders
```

Larger stress-test datasets may be added later but are optional.

### Security

Never commit:

* credentials;
* passwords;
* API keys;
* tokens;
* `.env` secrets;
* company code;
* company data;
* proprietary schemas;
* work credentials.

Use `.env.example` for documenting required environment variables without storing secrets.

---

## Architecture source of truth

[`architecture.md`](architecture.md) contains the **current agreed architecture**.

Treat it as the source of truth for:

* technologies;
* component responsibilities;
* data flows;
* operational data model;
* event model;
* lake architecture;
* warehouse architecture;
* dbt model structure;
* orchestration;
* quality strategy;
* project constraints.

Do not silently introduce architectural changes that conflict with that document.

If implementation reveals that an architectural decision should change:

1. explain the issue;
2. discuss the alternative;
3. agree on the change;
4. update `architecture.md`;
5. then change the implementation.

The architecture is allowed to evolve as the project teaches us new things.

It is not intended to freeze early decisions permanently.

---

## Documentation principles

Documentation should explain **why**, not only **what**.

Prefer:

> ClickHouse is used as the analytical warehouse because it provides a server-based OLAP database that can be self-hosted without cloud billing.

over:

> Warehouse: ClickHouse.

Important engineering decisions should be recoverable from the repository without requiring access to previous AI conversations.

Avoid duplicating large sections of architecture documentation across several files.

Use:

* `README.md` for project overview and usage;
* `architecture.md` for architectural decisions;
* `AGENTS.md` for AI collaboration instructions;
* code-level documentation where implementation details belong.

---

## How to make changes

Work incrementally.

A preferred implementation pattern is:

```text
Understand the problem
        ↓
Design the smallest solution
        ↓
Implement
        ↓
Test
        ↓
Inspect results
        ↓
Commit
        ↓
Move to next layer
```

Do not scaffold the entire future project with empty directories merely to make the repository look complete.

Add components when they begin to have an implementation.

Prefer meaningful Git commits such as:

```text
docs: define initial platform architecture

feat: add PostgreSQL source schema

feat: add synthetic customer generator

feat: implement order lifecycle simulation

feat: add incremental order ingestion

feat: publish order lifecycle events to Kafka

feat: add Spark event processing

feat: add dbt order fact model
```

Avoid giant commits containing unrelated layers of the platform.

---

## Current implementation philosophy

The project should be built approximately in this order:

```text
1. Repository and development environment
2. Docker fundamentals
3. PostgreSQL operational source
4. Python simulator
5. Incremental batch ingestion
6. Kafka event production
7. Raw object storage / Bronze layer
8. Spark Structured Streaming
9. Spark batch processing / Silver layer
10. ClickHouse warehouse
11. dbt transformations
12. Kestra orchestration
13. Data quality and reconciliation
14. CI/CD
15. Final documentation and demo workflow
```

This order can change if implementation reveals a better dependency sequence.

The objective is not merely to reach the final architecture.

The objective is to understand **how and why each layer is built**.
