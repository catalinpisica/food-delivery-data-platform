# Food Delivery Data Platform — Architecture

## 1. Project objective

This project builds a small but realistic **end-to-end data platform for a simulated food-delivery company**.

Its primary purpose is educational: to learn data engineering concepts and technologies through a coherent system rather than isolated tutorials.

Its secondary purpose is to serve as a portfolio project that can be discussed and demonstrated during Data Engineering interviews.

The project should demonstrate understanding of:

* operational databases;
* batch ingestion;
* incremental ingestion;
* event-driven architecture;
* Kafka;
* object storage;
* Bronze/Silver data-lake patterns;
* Parquet;
* Spark batch processing;
* Spark Structured Streaming;
* analytical warehouses;
* dbt;
* dimensional modeling;
* Slowly Changing Dimensions;
* orchestration;
* data quality;
* failure handling;
* data reconciliation;
* CI/CD;
* containerization;
* reproducibility.

The objective is **not** to simulate production-scale traffic.

The objective is to correctly implement and understand the engineering patterns that would exist in a larger platform.

---

# 2. Constraints

## 2.1 Cost

The core platform must be usable without paid cloud services.

The project must not require:

* AWS;
* Google Cloud;
* Microsoft Azure;
* Snowflake;
* Databricks;
* another usage-billed data warehouse.

This minimizes the risk of unexpected cloud costs.

All core infrastructure should run as self-hosted services inside the development environment.

---

## 2.2 Development environment

Primary environment:

```text
GitHub Codespaces
```

Services run primarily through:

```text
Docker
+
Docker Compose
```

The architecture must remain portable.

It should eventually also work on:

```text
personal Linux / macOS / Windows machine
        ↓
Docker
        ↓
same project services
```

Codespaces is therefore a development host, not an architectural dependency.

---

## 2.3 Runtime model

This is not a continuously running production service.

The platform should be capable of being:

```text
started
↓
populated
↓
pipeline executed
↓
demonstrated
↓
stopped
```

The environment should be reproducible rather than dependent on months of accumulated state.

---

## 2.4 Data scale

The data generator should support configurable sizes.

Initial target profiles:

| Profile  | Approximate orders | Purpose                  |
| -------- | -----------------: | ------------------------ |
| `tiny`   |                500 | everyday development     |
| `dev`    |              5,000 | integration testing      |
| `demo`   |             50,000 | larger demonstrations    |
| `stress` |       configurable | optional experimentation |

Each order may generate several lifecycle events.

The exact number depends on whether it is delivered, cancelled, etc.

The project deliberately does not require millions of records.

---

# 3. Architecture principles

## 3.1 Every component has one primary responsibility

The architecture should avoid overlapping tools without a clear reason.

Broadly:

```text
PostgreSQL
    → operational application state

Kafka
    → event stream

SeaweedFS
    → object storage / data lake

Spark
    → technical data processing

ClickHouse
    → analytical warehouse

dbt
    → business / analytical transformations

Kestra
    → workflow orchestration

Docker Compose
    → local infrastructure

GitHub Actions
    → CI
```

---

## 3.2 Separate operational state from events

PostgreSQL represents:

> What does the application currently believe to be true?

Kafka represents:

> What happened over time?

For example, PostgreSQL may contain:

```text
order_id = 123
status = DELIVERED
```

while Kafka contains:

```text
ORDER_CREATED
RESTAURANT_ACCEPTED
COURIER_ASSIGNED
ORDER_PICKED_UP
ORDER_DELIVERED
```

This distinction is fundamental to the project.

---

## 3.3 Preserve raw data

Raw data should be retained before semantic processing.

The Bronze layer should make it possible to replay downstream transformations if processing logic changes.

---

## 3.4 Separate technical processing from business modeling

Spark primarily handles **technical data processing**.

Examples:

* parsing;
* schema enforcement;
* deduplication;
* malformed data;
* event-time handling;
* file preparation;
* batch processing.

dbt primarily handles **analytical/business modeling**.

Examples:

* fact tables;
* dimensions;
* business definitions;
* delivery KPIs;
* customer metrics;
* restaurant metrics;
* business-level tests.

---

## 3.5 Correctness over artificial scale

Some technologies used here would not be necessary for several hundred or thousand records.

For example, Spark is intentionally included because the project aims to teach:

* Spark DataFrames;
* distributed-processing concepts;
* transformations and actions;
* partitions;
* shuffles;
* Spark SQL;
* Structured Streaming;
* checkpointing;
* event-time processing.

The project must not claim that Spark is required by the dataset size.

---

# 4. High-level architecture

```text
                         SOURCES

             ┌────────────┬─────────────┐
             │            │             │
        PostgreSQL                  Weather API
          OLTP                         │
             │                         │
             ▼                         │
        Debezium CDC                   │
             │                         │
             ▼                         │
      Kafka-compatible                 │
       event topics                    │
             │                         │
             ▼                         │
       CDC raw writer                  │
             │                         │
             ▼                         │
      SeaweedFS RAW                    │
        JSONL objects                  │
             │                         │
             ▼                         │
           Spark                       │
       batch / streaming               │
             │                         │
             └────────────┬────────────┘
                          ▼
                    ┌───────────┐
                    │ SeaweedFS │
                    │           │
                    │  BRONZE   │
                    └─────┬─────┘
                          │
                          ▼
                       Spark
                   batch processing
                          │
                          ▼
                    ┌───────────┐
                    │ SeaweedFS │
                    │           │
                    │  SILVER   │
                    └─────┬─────┘
                          │
                          ▼
                    ┌───────────┐
                    │ClickHouse │
                    │  landing  │
                    └─────┬─────┘
                          │
                         dbt
                          │
              ┌───────────┼────────────┐
              ▼           ▼            ▼
          dimensions     facts        marts
```

Cross-cutting responsibilities:

```text
Kestra
    → orchestration

Docker Compose
    → infrastructure/runtime

dbt + processing checks
    → data quality

GitHub Actions
    → CI
```

---

# 5. Technology stack

| Responsibility             | Technology                 |
| -------------------------- | -------------------------- |
| Development environment    | GitHub Codespaces          |
| Source simulator           | Python                     |
| Operational database       | PostgreSQL                 |
| Change data capture        | Debezium                   |
| Event streaming            | Redpanda / Apache Kafka protocol |
| Object storage / data lake | SeaweedFS                  |
| Raw file format            | JSONL                      |
| Processed file format      | Apache Parquet             |
| Distributed processing     | Apache Spark               |
| Streaming processing       | Spark Structured Streaming |
| Analytical warehouse       | ClickHouse                 |
| Analytics transformations  | dbt                        |
| Orchestration              | Kestra                     |
| Containers                 | Docker                     |
| Multi-service environment  | Docker Compose             |
| Version control            | Git                        |
| Repository                 | GitHub                     |
| CI                         | GitHub Actions             |
| External enrichment        | Weather API                |

---

# 6. Source systems

The project initially contains two source patterns and one event stream derived from the operational database:

```text
PostgreSQL
    → mutable relational operational data

Debezium CDC + Kafka-compatible topics
    → continuous stream of PostgreSQL changes

Weather API
    → external API data
```

This deliberately provides experience with different ingestion patterns.

The main source flow is:

```text
delivery-simulator -> PostgreSQL -> Debezium CDC -> Redpanda topics -> SeaweedFS raw JSONL
```

PostgreSQL is the OLTP system of record. The simulator writes operational rows to PostgreSQL, and Debezium publishes those database changes into Kafka-compatible topics.

The simulator should not publish directly to Kafka in the main pipeline path. Direct Kafka publishing may be used only for small local smoke tests while learning or troubleshooting the broker.

CDC events are landed in SeaweedFS as raw JSONL objects before semantic processing. Spark will later read this raw layer and write cleaned Parquet datasets.

---

# 7. Simulated food-delivery domain

The simulator models a simplified food-delivery platform.

Core entities:

```text
Customer
Restaurant
Menu Item
Courier
Zone
Order
Order Item
Delivery
```

Relationships:

```text
Customer ───────┐
                │
Restaurant ─────┼──── Order ──── Order Item
                │        │
Courier ────────┘        │
                         └──── Delivery

Restaurant ───────────── Menu Item

Zone ───── Customer
     ├─── Restaurant
     └─── Courier
```

The application is intentionally limited.

Initial versions do not need:

* reviews;
* subscriptions;
* payment processors;
* support tickets;
* promotions;
* live courier GPS telemetry;
* restaurant employee systems.

These may become future extensions only if they add educational value.

---

# 8. Operational PostgreSQL model

PostgreSQL represents the application's current operational state.

## 8.1 `zones`

Grain:

> One row per delivery zone.

Fields:

```text
zone_id
zone_name
city
latitude
longitude
created_at
```

Initially, the simulated business can operate within Amsterdam.

Example conceptual zones:

```text
Amsterdam Centrum
Amsterdam West
Amsterdam Zuid
Amsterdam Oost
Amsterdam Noord
```

---

## 8.2 `customers`

Grain:

> One row per customer.

Fields:

```text
customer_id
zone_id
signup_channel
created_at
updated_at
is_active
```

No synthetic names, emails or phone numbers are required because they add no useful data-engineering behavior.

Possible signup channels:

```text
organic
paid_search
referral
social
```

---

## 8.3 `restaurants`

Grain:

> One row per restaurant.

Fields:

```text
restaurant_id
restaurant_name
zone_id
cuisine_type
price_category
created_at
updated_at
is_active
```

Possible cuisine categories include:

```text
Italian
Indian
Japanese
Turkish
Chinese
Dutch
Thai
Mexican
Burgers
Healthy
```

Controlled categorical values provide useful future data-quality tests.

---

## 8.4 `menu_items`

Grain:

> One row per menu item.

Fields:

```text
menu_item_id
restaurant_id
item_name
category
price_cents
created_at
updated_at
is_available
```

Money should be stored using integer cents rather than binary floating-point numbers.

Example:

```text
€12.50
```

is represented operationally as:

```text
1250
```

---

## 8.5 `couriers`

Grain:

> One row per courier.

Fields:

```text
courier_id
home_zone_id
vehicle_type
created_at
updated_at
status
```

Possible vehicles:

```text
bike
ebike
scooter
car
```

Possible operational statuses:

```text
offline
available
delivering
```

---

## 8.6 `orders`

Grain:

> One row per order.

Fields:

```text
order_id
customer_id
restaurant_id
courier_id

customer_zone_id
restaurant_zone_id

status

subtotal_cents
delivery_fee_cents
total_amount_cents

created_at
updated_at
```

`courier_id` may initially be null.

Customer and restaurant zones are copied onto the order so that the order retains the geographic state that existed when the transaction occurred.

Historical orders should not change meaning if a customer or restaurant later moves.

---

## 8.7 `order_items`

Grain:

> One row per menu item within an order.

Fields:

```text
order_item_id
order_id
menu_item_id
quantity
unit_price_cents
total_price_cents
created_at
```

The item price is copied onto the transaction.

Historical revenue must not change when the menu price changes later.

---

## 8.8 `deliveries`

Grain:

> One row per delivery.

Fields:

```text
delivery_id
order_id
courier_id
status
assigned_at
picked_up_at
delivered_at
created_at
updated_at
```

Orders and deliveries represent different concepts:

```text
order
    → commercial transaction

delivery
    → physical fulfilment
```

---

# 9. Order lifecycle

The normal order state machine is:

```text
CREATED
   │
   ▼
ACCEPTED
   │
   ▼
COURIER_ASSIGNED
   │
   ▼
PICKED_UP
   │
   ▼
DELIVERED
```

Orders can also be cancelled before pickup:

```text
CREATED ───────────→ CANCELLED

ACCEPTED ──────────→ CANCELLED

COURIER_ASSIGNED ──→ CANCELLED
```

The simulator should normally generate valid transitions.

The data-quality testing mode may deliberately inject invalid ones.

---

# 10. Kafka / CDC architecture

## 10.1 Primary CDC topics

The initial Kafka-compatible topics should come from PostgreSQL table changes captured by Debezium.

Conceptual initial topics:

```text
orders
order_items
deliveries
```

These topics represent changes to operational tables.

Messages should be keyed by the table's primary identifier where possible:

```text
order_id
order_item_id
delivery_id
```

For order-related processing, downstream consumers can still connect records using shared fields such as `order_id`.

## 10.2 Raw CDC landing

The raw CDC writer consumes Debezium topics and writes the original Kafka messages into SeaweedFS.

Initial raw storage layout:

```text
s3://food-delivery-raw/raw/cdc/orders/
s3://food-delivery-raw/raw/cdc/order_items/
s3://food-delivery-raw/raw/cdc/deliveries/
```

Raw CDC files use JSONL:

```text
one Kafka message per line
```

This layer should preserve the original Debezium message value and useful Kafka metadata such as topic, partition, offset, Kafka timestamp, and landing timestamp.

## 10.3 Future domain-event topic

A later version may add a domain-event topic such as:

```text
order_events
```

That topic would represent business events like `ORDER_CREATED` or `ORDER_DELIVERED`, rather than raw database row changes.

---

## 10.4 Dead-letter handling

Rejected events may be written to:

```text
dead_letter_events
```

or persisted to the quarantine area of the data lake, depending on where validation fails.

---

## 10.5 Future event types

Initial order lifecycle events:

```text
ORDER_CREATED
RESTAURANT_ACCEPTED
COURIER_ASSIGNED
ORDER_PICKED_UP
ORDER_DELIVERED
ORDER_CANCELLED
```

Additional event domains should not be added until there is a concrete reason.

---

# 11. Standard event envelope

All events should follow a common envelope.

Conceptually:

```json
{
  "event_id": "...",
  "event_type": "ORDER_CREATED",
  "event_version": 1,
  "event_time": "...",
  "emitted_at": "...",
  "producer": "delivery-simulator",
  "aggregate_type": "order",
  "aggregate_id": "...",
  "payload": {}
}
```

Important fields:

### `event_id`

Globally identifies the event.

Used for:

* lineage;
* debugging;
* deduplication;
* idempotency.

### `event_type`

Describes what happened.

### `event_version`

Provides an explicit mechanism for future schema evolution.

### `event_time`

The time the business event actually occurred.

### `emitted_at`

The time the producing application published the event.

This distinction allows the project to explore:

```text
event time
vs
publication time
vs
Kafka ingestion time
vs
Spark processing time
```

### `aggregate_id`

For order events:

```text
aggregate_id = order_id
```

---

# 12. Event payload strategy

Events should contain enough information to describe what happened.

They should not blindly copy the complete current PostgreSQL order record into every message.

For example:

### `ORDER_CREATED`

May contain:

```text
customer_id
restaurant_id
customer_zone_id
restaurant_zone_id
subtotal_cents
delivery_fee_cents
total_amount_cents
item_count
```

### `COURIER_ASSIGNED`

May contain:

```text
courier_id
courier_zone_id
```

### `ORDER_CANCELLED`

May contain:

```text
cancelled_by
cancellation_reason
```

This creates a meaningful distinction between event history and relational current state.

---

# 13. Intentionally imperfect event data

The simulator should eventually support configurable injection of realistic data problems.

Examples:

```text
duplicate events
late-arriving events
out-of-order events
malformed events
missing required attributes
invalid state transitions
```

Possible configuration:

```yaml
data_quality:
  duplicate_event_rate: 0.005
  late_event_rate: 0.01
  malformed_event_rate: 0.001
```

Exact rates can be decided during implementation.

The simulator should support both:

```text
clean mode
```

and:

```text
realistic / failure-injection mode
```

---

# 14. External weather data

Weather provides a real external dataset that has a meaningful relationship with food-delivery operations.

Potential analytical questions include:

```text
Does rain increase order volume?

Does rain increase delivery duration?

Does severe weather increase cancellations?

Does weather affect average order value?
```

The desired analytical grain is:

> One row per zone per hour.

Conceptual schema:

```text
zone_id
weather_timestamp
temperature_c
precipitation_mm
wind_speed_kmh
weather_code
```

Zones are mapped to API requests through their latitude and longitude.

---

# 15. Timestamp convention

Internally, timestamps should be stored consistently in **UTC**.

Local Amsterdam time should be derived only where needed for analytics.

This avoids ambiguity around:

* time zones;
* daylight-saving changes;
* source-system differences.

Analytical models may expose fields such as:

```text
local_date
local_hour
```

when useful.

---

# 16. Data lake

SeaweedFS acts as the local object-storage layer.

The exact physical layout may evolve during implementation, but the conceptual layers are:

```text
Bronze
Silver
Quarantine
```

Gold/business-facing data lives primarily in ClickHouse rather than being duplicated into another Gold object-storage layer.

---

# 17. Bronze layer

Bronze represents source-aligned raw data.

Principle:

> Preserve what arrived with as little semantic transformation as practical.

Conceptual structure:

```text
bronze/

├── postgres/
│   ├── customers/
│   ├── restaurants/
│   ├── menu_items/
│   ├── couriers/
│   ├── orders/
│   ├── order_items/
│   └── deliveries/
│
├── kafka/
│   └── order_events/
│
└── weather/
```

Raw data should remain replayable.

---

# 18. Bronze metadata

## 18.1 Kafka metadata

Kafka-originating records should preserve useful ingestion metadata such as:

```text
_kafka_topic
_kafka_partition
_kafka_offset
_kafka_timestamp
_ingested_at
```

This supports lineage and debugging.

---

## 18.2 PostgreSQL metadata

Batch-ingested relational records should include metadata such as:

```text
_ingested_at
_batch_id
_source_table
_extraction_watermark
```

where appropriate.

---

# 19. Incremental PostgreSQL ingestion

Mutable PostgreSQL tables should not be fully reloaded on every run once incremental ingestion is implemented.

Candidate mutable tables:

```text
customers
restaurants
menu_items
couriers
orders
deliveries
```

A timestamp such as:

```text
updated_at
```

can act as the initial extraction watermark.

Conceptually:

```sql
SELECT *
FROM orders
WHERE updated_at > previous_watermark
  AND updated_at <= current_watermark
```

The exact implementation must handle boundary conditions carefully to avoid missed or duplicated data.

Pipeline metadata should eventually record:

```text
source_name
table_name
previous_watermark
current_watermark
batch_id
status
row_count
started_at
finished_at
```

---

# 20. Silver layer

Silver represents data that is technically trustworthy.

Silver data should be:

```text
typed
validated
deduplicated
normalized
technically consistent
```

Conceptual layout:

```text
silver/

├── customers/
├── restaurants/
├── menu_items/
├── couriers/
├── orders/
├── order_items/
├── deliveries/
├── order_events/
└── weather_hourly/
```

Processed lake datasets should primarily use:

```text
Apache Parquet
```

---

# 21. Why Parquet

Parquet provides an opportunity to learn:

* columnar storage;
* schemas;
* compression;
* predicate pushdown;
* partition pruning;
* file sizing;
* data partitioning;
* small-file problems.

Datasets may eventually be partitioned using meaningful fields such as dates.

Partition strategy should be chosen based on query/access patterns rather than mechanically partitioning every field.

---

# 22. Spark responsibilities

Spark has two major roles.

## 22.1 Structured Streaming

Streaming flow:

```text
Kafka
  ↓
Spark Structured Streaming
  ↓
validation / processing
  ↓
object storage
```

The project should use this to learn:

* streaming DataFrames;
* event time;
* processing time;
* watermarks;
* late events;
* checkpointing;
* deduplication;
* Kafka offsets;
* restart behavior.

---

## 22.2 Batch processing

Batch flow:

```text
Bronze
  ↓
Spark
  ↓
Silver
```

Typical responsibilities:

```text
schema enforcement
type conversion
timestamp normalization
deduplication
technical validation
normalization
file compaction
technical enrichment
```

Spark should not become the primary layer for business KPI logic.

---

# 23. Quarantine and rejected data

Invalid data should not simply disappear.

A quarantine area should preserve rejected records where useful.

Conceptually:

```text
quarantine/
    order_events/
    ...
```

Quarantined records may include:

```text
original_record
error_code
error_message
detected_at
batch_id
Kafka metadata
```

Possible error categories:

```text
INVALID_EVENT_SCHEMA
UNKNOWN_EVENT_TYPE
MISSING_ORDER_ID
INVALID_TIMESTAMP
INVALID_STATE_TRANSITION
```

This provides an explicit failure-handling path.

---

# 24. ClickHouse analytical warehouse

ClickHouse acts as the local/self-hosted analytical warehouse.

Its first layer should remain relatively source-aligned.

Conceptually:

```text
landing.customers
landing.restaurants
landing.menu_items
landing.couriers
landing.orders
landing.order_items
landing.deliveries
landing.order_events
landing.weather_hourly
```

These tables represent clean data loaded from Silver.

Business modeling occurs above this layer through dbt.

---

# 25. dbt architecture

The dbt project should broadly contain:

```text
staging
    ↓
intermediate
    ↓
core facts/dimensions
    ↓
analytical marts
```

---

## 25.1 Staging

Models:

```text
stg_customers
stg_restaurants
stg_menu_items
stg_couriers
stg_orders
stg_order_items
stg_deliveries
stg_order_events
stg_weather_hourly
```

Typical staging responsibilities:

```text
rename fields
standardize naming
basic type cleanup
currency conversion
simple source-derived fields
```

For example:

```text
total_amount_cents
```

may become an analytical decimal/euro value.

---

## 25.2 Intermediate models

Initial candidates:

```text
int_order_lifecycle
int_delivery_metrics
int_orders_with_weather
```

### `int_order_lifecycle`

Grain:

> One row per order.

Possible fields:

```text
order_id
created_at
accepted_at
courier_assigned_at
picked_up_at
delivered_at
cancelled_at
```

The lifecycle can be reconstructed from the event stream.

### `int_delivery_metrics`

Derived durations may include:

```text
acceptance_seconds
assignment_seconds
preparation_seconds
delivery_seconds
total_fulfilment_seconds
```

### `int_orders_with_weather`

Orders can be associated with weather using:

```text
zone
+
relevant hourly timestamp
```

---

# 26. Dimensional model

The analytical model should use explicit grains and a relatively conventional star-schema approach.

---

## 26.1 `dim_customer`

Grain:

> One row per customer.

Potential fields:

```text
customer_key
customer_id
signup_date
signup_channel
home_zone
is_active
```

---

## 26.2 `dim_restaurant`

This is the initial deliberate **Slowly Changing Dimension Type 2** learning use case.

Potential fields:

```text
restaurant_key
restaurant_id
restaurant_name
cuisine_type
price_category
zone
is_active
valid_from
valid_to
is_current
```

Historical restaurant attributes should remain queryable when selected attributes change.

The project should not automatically make every dimension SCD Type 2.

---

## 26.3 `dim_courier`

Grain:

> One row per courier.

Potential fields:

```text
courier_key
courier_id
vehicle_type
home_zone
is_active
```

---

## 26.4 `dim_zone`

Potential fields:

```text
zone_key
zone_id
zone_name
city
latitude
longitude
```

---

## 26.5 `dim_date`

Potential fields:

```text
date_key
date
day_of_week
day_name
week
month
quarter
year
is_weekend
```

---

# 27. Fact tables

## 27.1 `fct_orders`

Grain:

> One row per order.

Potential fields:

```text
order_id

customer_key
restaurant_key
courier_key
customer_zone_key
restaurant_zone_key
order_date_key

item_count

subtotal
delivery_fee
total_amount

order_status

created_at
accepted_at
assigned_at
picked_up_at
delivered_at
cancelled_at

acceptance_minutes
assignment_minutes
preparation_minutes
delivery_minutes
total_fulfilment_minutes

is_delivered
is_cancelled
```

---

## 27.2 `fct_order_items`

Grain:

> One row per item line within an order.

Potential fields:

```text
order_id
menu_item_id
restaurant_key
date_key
quantity
unit_price
line_total
```

---

## 27.3 `fct_order_events`

Grain:

> One row per order lifecycle event.

Potential fields:

```text
event_id
order_id
event_type
event_time
processing_delay_seconds
kafka_partition
kafka_offset
```

This fact is particularly useful for examining the streaming pipeline itself.

---

## 27.4 `fct_weather_hourly`

Grain:

> One row per zone per hour.

Potential fields:

```text
zone_key
weather_hour
temperature_c
precipitation_mm
wind_speed_kmh
weather_code
is_raining
```

---

# 28. Analytical marts

Initial marts:

```text
mart_restaurant_performance
mart_delivery_performance
mart_customer_behavior
mart_weather_impact
```

---

## 28.1 `mart_restaurant_performance`

Possible grain:

> Restaurant × day.

Possible metrics:

```text
orders
delivered_orders
cancelled_orders
revenue
average_order_value
average_delivery_minutes
cancellation_rate
```

---

## 28.2 `mart_delivery_performance`

Possible grain:

> Zone × hour.

Possible metrics:

```text
order_count
average_delivery_minutes
p50_delivery_minutes
p95_delivery_minutes
courier_count
```

---

## 28.3 `mart_customer_behavior`

Possible grain:

> Customer.

Possible metrics:

```text
total_orders
total_spend
average_order_value
first_order_date
latest_order_date
favorite_cuisine
```

---

## 28.4 `mart_weather_impact`

Possible grain:

> Weather condition × time period.

Possible metrics:

```text
orders
average_delivery_time
cancellation_rate
average_order_value
```

---

# 29. Data quality

Data quality should exist at multiple layers.

## Ingestion

Examples:

```text
source returned records
required fields exist
batch completed
schema can be parsed
```

## Spark / processing

Examples:

```text
duplicate event_id
invalid timestamp
unknown event type
malformed JSON
invalid identifiers
technical schema violation
```

## dbt

Use built-in and custom tests for:

```text
unique
not_null
relationships
accepted_values
business invariants
```

Examples:

```text
order_id must be unique in fct_orders

customer foreign keys should resolve

restaurant foreign keys should resolve

order status must belong to expected values
```

Custom tests should be implemented where they teach useful business/data-quality concepts.

---

# 30. Operational/event reconciliation

A major data-quality exercise will compare:

```text
PostgreSQL current order state
```

against:

```text
state reconstructed from Kafka events
```

Example:

```text
PostgreSQL:
order 123 = DELIVERED

Kafka history:
ORDER_CREATED
RESTAURANT_ACCEPTED
COURIER_ASSIGNED
ORDER_PICKED_UP
ORDER_DELIVERED
```

This is consistent.

But:

```text
PostgreSQL:
order 123 = DELIVERED

Kafka history:
ORDER_CREATED
RESTAURANT_ACCEPTED
COURIER_ASSIGNED
```

indicates a discrepancy that should be investigated.

This provides a realistic reconciliation problem.

---

# 31. Orchestration

Kestra orchestrates **discrete workflows**.

Potential dependency chain:

```text
PostgreSQL ingestion ─┐
                      │
Weather ingestion ────┤
                      ▼
                Spark batch
                      ↓
              ClickHouse load
                      ↓
                  dbt build
                      ↓
                  dbt tests
                      ↓
             quality checks
```

The Kafka/Spark streaming process should not be artificially represented as a simple daily batch DAG.

Long-running streaming processes and scheduled workflows have different operational semantics.

---

# 32. Observability

Version 1 should keep observability relatively simple.

Initial sources:

```text
Docker logs
Kestra execution logs
Spark logs
Kafka consumer information
dbt results
pipeline metadata
```

A pipeline metadata model may eventually record:

```text
run_id
pipeline_name
started_at
finished_at
status
rows_read
rows_written
rows_rejected
```

Prometheus, Grafana, OpenTelemetry and similar platforms are not part of the initial architecture.

They may be considered later if they solve a concrete learning problem.

---

# 33. Container architecture

Services should eventually be managed using Docker Compose.

Conceptually:

```text
Docker Compose

├── postgres
├── kafka
├── seaweedfs
├── clickhouse
├── spark
├── kestra
└── simulator
```

Not every service must run at all times.

Docker Compose profiles or equivalent mechanisms may be used to start only relevant subsets of the platform.

For example, conceptually:

```text
source
streaming
warehouse
orchestration
full
```

Exact Compose organization should be decided during implementation.

---

# 34. Reproducibility

The project should not depend on irreplaceable state in a particular Codespace.

The target experience is eventually something conceptually similar to:

```text
clone repository
      ↓
create environment
      ↓
start services
      ↓
initialize schemas
      ↓
generate synthetic data
      ↓
run pipelines
      ↓
query analytical models
```

Generated datasets and local service state should be reproducible.

Important project logic must live in Git.

---

# 35. CI

GitHub Actions should eventually validate appropriate parts of the project.

Potential CI checks:

```text
Python linting
Python unit tests
SQL linting
dbt parse / compile
dbt tests where practical
configuration validation
Docker configuration validation
small integration tests
```

CI should remain lightweight.

There is no reason to launch the entire largest possible platform for every commit.

---

# 36. Explicit non-goals

The initial project does **not** aim to demonstrate:

* production-scale data volume;
* Kubernetes;
* multi-region infrastructure;
* multi-broker production Kafka;
* cloud networking;
* real customer data;
* real payment systems;
* machine learning;
* production-grade observability;
* real-time GPS telemetry;
* enterprise security architecture;
* full application/backend development.

These can distract from the core objective.

---

# 37. Technologies intentionally excluded from v1

The following technologies should not be added without a new concrete requirement:

```text
AWS
GCP
Azure
Snowflake
Databricks
Kubernetes
Terraform / OpenTofu
Airflow
Flink
Trino
Iceberg
Grafana
Prometheus
```

Their exclusion does not mean they are bad technologies.

They simply do not currently solve a problem that justifies adding them to this project.

Terraform/OpenTofu may become relevant if genuine infrastructure provisioning is introduced later.

---

# 38. Planned implementation sequence

Current intended order:

```text
1. Git/GitHub/Codespaces setup

2. Docker fundamentals

3. PostgreSQL
   ├── container
   ├── schema
   ├── constraints
   └── indexes

4. Python simulator
   ├── reference entities
   ├── orders
   ├── state machine
   └── configurable data scale

5. Incremental PostgreSQL ingestion
   ├── extraction
   ├── watermarks
   └── metadata

6. Kafka
   ├── broker
   ├── topics
   ├── producer
   ├── partitions
   └── lifecycle events

7. Object storage / Bronze

8. Spark Structured Streaming

9. Spark batch Bronze → Silver processing

10. ClickHouse

11. dbt
    ├── staging
    ├── intermediate
    ├── dimensions
    ├── facts
    └── marts

12. Kestra orchestration

13. Data-quality and reconciliation workflows

14. GitHub Actions / CI

15. Documentation and reproducible demo workflow
```

The implementation order may evolve as dependencies become clearer.

---

# 39. Architecture evolution

This file describes the **current agreed architecture**, not an immutable final state.

Changes are encouraged when implementation teaches us that another approach is better.

However, architecture should evolve deliberately.

For meaningful changes:

```text
identify problem
    ↓
understand alternatives
    ↓
discuss trade-offs
    ↓
choose solution
    ↓
update architecture.md
    ↓
implement
```

The repository should preserve not only what was built, but enough rationale to understand why it was built that way.
