---
name: database-designer
description: Use when you need to design database schemas, plan migrations, optimize queries, or make database architecture decisions. Covers normalization, indexing, relationships, and performance tuning for SQL and NoSQL databases.
when_to_use: Before creating new database tables, when designing data models for applications, when optimizing slow queries, when planning database migrations, or when choosing between SQL and NoSQL solutions.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
arguments:
  - db-type
  - scope
  - optimization
argument-hint: "[postgresql|mysql|sqlite|mongodb|redis] [schema-design|query-optimization|migration-planning|full-audit] [none|indexes|partitioning|caching]"
---

# Database Designer

Design efficient, maintainable database schemas and optimize data access patterns. Covers normalization, indexing strategies, migration planning, and performance tuning for both SQL and NoSQL databases.

<HARD-GATE>
Do NOT design a schema without considering query patterns first. Do NOT add indexes without understanding their write cost. Do NOT write migrations without a rollback plan. Do NOT use ORMs without understanding the SQL they generate.
</HARD-GATE>

## The Iron Law

Every table/collection must have: a clear purpose, a primary key, appropriate indexes for query patterns, defined relationships, and a migration path from the previous state.

## When to Use

- Designing a new database schema from scratch
- Adding new tables or modifying existing ones
- Optimizing slow database queries
- Planning database migrations
- Choosing between SQL and NoSQL for a use case
- Reviewing data model designs before implementation
- Scaling an existing database

## When NOT to Use

- Simple key-value storage needs
- When a managed service (Auth0, Stripe) handles the data
- Prototyping where schema will change daily
- When the data is purely ephemeral

## The Process

### Phase 1: Requirements Analysis

1. **Identify data entities and relationships**
   ```
   Entity Analysis:
   ├── What are the entities (nouns) in your domain?
   ├── What are their attributes?
   ├── What are the relationships (1:1, 1:N, M:N)?
   ├── What are the cardinality constraints?
   └── What are the lifecycle states?
   ```

2. **Define query patterns**
   - What queries will be most common?
   - What queries must be fast (latency-critical)?
   - What are the read vs write ratios?
   - What are the access patterns (point lookup, range scan, aggregation)?

3. **Define constraints**
   - Data volume estimates (current and projected)
   - Latency requirements
   - Consistency requirements (strong vs eventual)
   - Compliance requirements (GDPR, HIPAA, PCI)

### Phase 2: Schema Design (SQL)

4. **Normalization**
   ```
   Normal Forms:
   ├── 1NF: Atomic values, no repeating groups
   ├── 2NF: No partial dependencies (all non-key attrs depend on full PK)
   ├── 3NF: No transitive dependencies (non-key attrs depend only on PK)
   └── BCNF: Every determinant is a candidate key

   Denormalize intentionally when:
   ├── Read performance is critical and writes are rare
   ├── Aggregations are expensive and change infrequently
   └── Data is append-only (audit logs, events)
   ```

5. **Define tables and columns**
   ```sql
   CREATE TABLE users (
     id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
     email       VARCHAR(255) NOT NULL UNIQUE,
     name        VARCHAR(255) NOT NULL,
     status      VARCHAR(20) NOT NULL DEFAULT 'active'
                   CHECK (status IN ('active', 'suspended', 'deleted')),
     created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
     updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
   );

   CREATE TABLE orders (
     id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
     user_id     UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
     total_cents INTEGER NOT NULL CHECK (total_cents >= 0),
     status      VARCHAR(20) NOT NULL DEFAULT 'pending',
     created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
     updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
   );

   -- Junction table for M:N
   CREATE TABLE order_items (
     order_id   UUID REFERENCES orders(id) ON DELETE CASCADE,
     product_id UUID REFERENCES products(id) ON DELETE RESTRICT,
     quantity   INTEGER NOT NULL CHECK (quantity > 0),
     price_cents INTEGER NOT NULL CHECK (price_cents >= 0),
     PRIMARY KEY (order_id, product_id)
   );
   ```

6. **Index design**
   ```
   Index Strategy:
   ├── B-Tree (default): Equality and range queries
   ├── Hash: Equality only, smaller footprint
   ├── GIN: Full-text search, JSONB, arrays
   ├── GiST: Geometric, full-text search
   └── BRIN: Large tables with natural ordering (time series)

   Index Rules:
   ├── Index columns used in WHERE, JOIN, ORDER BY
   ├── Composite indexes: most selective column first
   ├── Covering indexes for frequently queried column sets
   ├── Avoid indexes on low-cardinality columns (boolean, status)
   └── Monitor index usage — drop unused indexes
   ```

7. **Constraints and integrity**
   - Primary keys on every table
   - Foreign keys with appropriate ON DELETE behavior
   - CHECK constraints for data validation
   - UNIQUE constraints for natural keys
   - NOT NULL unless nullability is semantically meaningful

### Phase 3: Schema Design (NoSQL)

8. **Document database design (MongoDB)**
   ```
   Modeling Patterns:
   ├── Embedded: Related data accessed together
   ├── Referenced: Large or independently accessed data
   ├── Bucket: Time-series or grouped data
   └── Computed: Pre-computed aggregates

   Rules:
   ├── Data that is accessed together should be stored together
   ├── Documents should be < 16MB
   ├── Avoid unbounded arrays
   └── Design for the most common query pattern
   ```

9. **Key-value store design (Redis)**
   ```
   Key Naming Convention:
   entity:id:field       — Simple value
   entity:id             — Hash
   entity:id:relation    — Set/List/Sorted Set

   Data Structures:
   ├── String: Counters, caches, simple values
   ├── Hash: Objects with named fields
   ├── Set: Unique collections, tags
   ├── List: Queues, recent items
   └── Sorted Set: Leaderboards, time-ordered data
   ```

### Phase 4: Query Optimization

10. **Analyze query performance**
    ```
    EXPLAIN ANALYZE output tells you:
    ├── Sequential scan → missing index
    ├── Nested loop → consider hash join or index
    ├── Sort → consider index for ORDER BY
    ├── High rows removed by filter → more selective index
    └── High execution time → query needs rewrite
    ```

11. **Optimization techniques**
    - Add missing indexes (but monitor write impact)
    - Rewrite subqueries as JOINs
    - Use covering indexes to avoid table lookups
    - Partition large tables by time or tenant
    - Use materialized views for expensive aggregations
    - Batch writes instead of individual inserts
    - Use connection pooling

12. **N+1 query prevention**
    - Use JOINs or batch loading
    - DataLoader pattern for GraphQL/ORM
    - Eager loading for related entities
    - Monitor query count per request

### Phase 5: Migration Planning

13. **Write migrations**
    ```
    Migration Checklist:
    ├── Forward migration: What changes to make
    ├── Rollback migration: How to undo changes
    ├── Data migration: How to transform existing data
    ├── Zero-downtime strategy: How to deploy without downtime
    └── Verification: How to confirm migration succeeded

    Zero-Downtime Pattern:
    1. Add new column (nullable or with default)
    2. Deploy code that writes to both old and new
    3. Backfill existing data
    4. Deploy code that reads from new column
    5. Remove old column (in separate migration)
    ```

14. **Migration safety**
    - Test migrations on production-like data
    - Run migrations in transactions where possible
    - Add indexes concurrently (PostgreSQL: `CREATE INDEX CONCURRENTLY`)
    - Never drop columns in the same migration that adds replacements
    - Always have a rollback plan

## Anti-Slop Rules

<Good>
- "Added composite index on orders(user_id, created_at DESC) — supports the common query pattern 'get user's recent orders' and avoids filesort."
- "Normalized order_items into separate table — prevents data duplication and allows individual item tracking. M:N relationship properly modeled with junction table."
- "Migration uses CREATE INDEX CONCURRENTLY to avoid locking the table during index creation on the 10M row orders table."
</Good>

<Bad>
- "Added index on every column just in case"
- "Used SELECT * in all queries"
- "No foreign keys — we'll enforce in application code"
- "Migration drops a column without a backup plan"
- "Stored passwords in plaintext"
- "No migration rollback script"
</Bad>

## Database Decision Matrix

| Requirement | Recommended | Why |
|-------------|------------|-----|
| Complex queries, joins | PostgreSQL | Best SQL feature set |
| Simple CRUD, embedded | SQLite | Zero configuration |
| Flexible schema, documents | MongoDB | Schema flexibility |
| Caching, sessions | Redis | Sub-millisecond latency |
| Time-series data | TimescaleDB/InfluxDB | Optimized for time |
| Full-text search | Elasticsearch | Best search capabilities |
| Graph relationships | Neo4j | Native graph traversal |
| High write throughput | Cassandra | Linear scalability |

## Schema Design Checklist

- [ ] Every table has a primary key
- [ ] Foreign keys with appropriate ON DELETE behavior
- [ ] CHECK constraints for data validation
- [ ] Indexes for all query patterns
- [ ] No N+1 query patterns
- [ ] Migration has rollback plan
- [ ] Zero-downtime deployment strategy
- [ ] Connection pooling configured
- [ ] Backup strategy defined
- [ ] Monitoring for slow queries

## Integration

Related skills: `api-designer`, `code-reviewer`, `security-auditor`, `devops-engineer`
