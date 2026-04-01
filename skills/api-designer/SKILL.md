---
name: api-designer
description: Use when you need to design REST or GraphQL APIs following industry best practices. Covers endpoint design, request/response schemas, versioning, pagination, error handling, authentication, and documentation.
when_to_use: Before building new APIs, when redesigning existing APIs, when creating API specifications for frontend-backend contracts, or when reviewing API designs for correctness and usability.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
arguments:
  - api-type
  - scope
  - style
argument-hint: "[rest|graphql|both] [single-endpoint|full-service|microservice] [minimal|standard|enterprise]"
---

# API Designer

Design robust, consistent, and developer-friendly APIs. Covers REST and GraphQL with best practices for naming, versioning, error handling, pagination, authentication, and documentation.

<HARD-GATE>
Do NOT design an API without first defining the resources and their relationships. Do NOT skip error response standardization. Do NOT design endpoints that expose internal implementation details.
</HARD-GATE>

## The Iron Law

Every API endpoint must have: a clear purpose, defined input schema, defined output schema, error responses, authentication requirements, and rate limiting strategy.

## When to Use

- Designing a new API from scratch
- Redesigning an existing API that has problems
- Creating API contracts between frontend and backend teams
- Reviewing API designs before implementation
- Migrating between API versions
- Designing webhook or event-driven interfaces

## When NOT to Use

- Internal-only scripts with no external consumers
- Simple CRUD wrappers with no business logic
- When a third-party API already solves the problem
- Prototyping where speed matters more than design

## The Process

### Phase 1: Requirements & Domain Modeling

1. **Identify resources and operations**
   ```
   Resources:
   ├── What are the nouns in your domain?
   ├── What are the relationships between them?
   ├── What operations can be performed on each?
   └── What are the access patterns?
   ```

2. **Define use cases**
   - Who are the API consumers?
   - What are their primary workflows?
   - What data do they need to read/write?
   - What are the performance requirements?

3. **Choose API style**
   - **REST**: Resource-oriented, cacheable, simple operations
   - **GraphQL**: Flexible queries, single endpoint, complex data needs
   - **gRPC**: High performance, internal services, streaming

### Phase 2: REST API Design

4. **Resource naming conventions**
   ```
   Good:
   GET    /users              — List users
   GET    /users/{id}         — Get specific user
   POST   /users              — Create user
   PUT    /users/{id}         — Replace user
   PATCH  /users/{id}         — Partial update
   DELETE /users/{id}         — Delete user
   GET    /users/{id}/orders  — Nested resource

   Bad:
   GET    /getUser            — Verb in path
   POST   /createUser         — Verb in path
   GET    /users?id=123       — ID in query for single resource
   GET    /users_list         — Inconsistent naming
   ```

5. **Request design**
   - Use appropriate HTTP methods (GET, POST, PUT, PATCH, DELETE)
   - Query parameters for filtering, sorting, pagination
   - Request body for complex input (POST, PUT, PATCH)
   - Headers for metadata (auth, content-type, idempotency key)

6. **Response design**
   ```
   Success Response:
   {
     "data": { ... },
     "meta": {
       "page": 1,
       "per_page": 20,
       "total": 150,
       "total_pages": 8
     }
   }

   Error Response:
   {
     "error": {
       "code": "VALIDATION_ERROR",
       "message": "Invalid input",
       "details": [
         { "field": "email", "message": "Invalid email format" }
       ],
       "request_id": "req_abc123"
     }
   }
   ```

7. **Pagination strategy**
   - Cursor-based for large/infinite datasets
   - Offset-based for small datasets with page navigation
   - Always include total count (or note if unavailable)
   - Default page size: 20, max: 100

8. **Filtering and sorting**
   ```
   GET /users?status=active&role=admin
   GET /users?sort=-created_at,name
   GET /users?fields=id,name,email
   ```

9. **Versioning strategy**
   - URL path: `/v1/users` (recommended)
   - Header: `API-Version: 2024-01-01`
   - Never break existing versions — add new ones
   - Deprecate with `Sunset` header and migration guide

### Phase 3: GraphQL API Design

10. **Schema design**
    - Types should match domain concepts
    - Use interfaces for shared fields
    - Avoid overly nested types (max 3 levels)
    - Design for the consumer's query patterns

11. **Query and mutation design**
    ```graphql
    # Good: Clear, specific operations
    type Query {
      user(id: ID!): User
      users(filter: UserFilter, pagination: PaginationInput): UserConnection
    }

    type Mutation {
      createUser(input: CreateUserInput!): CreateUserPayload!
      updateUser(id: ID!, input: UpdateUserInput!): UpdateUserPayload!
    }

    # Payload pattern for mutations
    type CreateUserPayload {
      user: User
      errors: [Error!]
    }
    ```

12. **Pagination in GraphQL**
    - Use Relay cursor connection specification
    - `edges`, `node`, `pageInfo` pattern
    - Support `first`, `last`, `before`, `after`

13. **Error handling in GraphQL**
    - Use `errors` array for execution errors
    - Use payload `errors` field for business logic errors
    - Include error codes for programmatic handling

### Phase 4: Cross-Cutting Concerns

14. **Authentication & Authorization**
    ```
    Auth Strategies:
    ├── API Keys — Service-to-service, simple
    ├── JWT/OAuth2 — User-facing, delegated access
    ├── mTLS — High-security internal services
    └── Session — Browser-based applications

    Authorization:
    ├── Resource-level: Can user access this resource?
    ├── Field-level: Can user see this field?
    └── Action-level: Can user perform this action?
    ```

15. **Rate limiting**
    - Set appropriate limits per endpoint
    - Return `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
    - Use `429 Too Many Requests` with `Retry-After` header
    - Different limits for authenticated vs unauthenticated

16. **Caching strategy**
    - Use `ETag` and `Last-Modified` for conditional requests
    - Set appropriate `Cache-Control` headers
    - Cache immutable resources aggressively
    - Invalidate caches on mutations

17. **Idempotency**
    - GET, PUT, DELETE must be idempotent
    - POST: support `Idempotency-Key` header
    - Return same response for same key within time window

### Phase 5: Documentation & Specification

18. **Generate API specification**
    - REST: OpenAPI 3.0 (Swagger) specification
    - GraphQL: SDL with descriptions
    - Include examples for every endpoint
    - Document all error codes and responses

19. **Write developer documentation**
    ```
    API Documentation Structure:
    ├── Getting Started
    │   ├── Authentication
    │   ├── Base URL
    │   └── Rate Limits
    ├── Resources
    │   ├── [Resource Name]
    │   │   ├── List
    │   │   ├── Get
    │   │   ├── Create
    │   │   ├── Update
    │   │   └── Delete
    └── Reference
        ├── Error Codes
        ├── Webhooks
        └── SDKs/Libraries
    ```

## Anti-Slop Rules

<Good>
- "POST /users — Creates a new user. Requires `email` (string, required), `name` (string, required). Returns 201 with user object. Errors: 400 VALIDATION_ERROR, 409 DUPLICATE_EMAIL."
- "GET /users supports cursor pagination via `?cursor=xxx&limit=20`. Returns `UserConnection` with `edges`, `pageInfo`."
- "All error responses follow standard format with `error.code`, `error.message`, `error.details`, and `error.request_id`."
</Good>

<Bad>
- "GET /getUsers — Returns users"
- "POST /user — Takes user data and creates it"
- No error response format defined
- No pagination strategy specified
- No authentication requirements documented
- Endpoints that expose database table names directly
</Bad>

## API Design Checklist

- [ ] Resources named as plural nouns
- [ ] HTTP methods used correctly
- [ ] Consistent naming convention (kebab-case or snake_case)
- [ ] Pagination on all list endpoints
- [ ] Filtering and sorting supported
- [ ] Standardized error response format
- [ ] Authentication requirements documented
- [ ] Rate limits defined
- [ ] Versioning strategy chosen
- [ ] Idempotency keys for mutations
- [ ] Request/response schemas defined
- [ ] API specification generated (OpenAPI/SDL)
- [ ] Example requests and responses provided
- [ ] Deprecation policy defined

## Integration

Related skills: `code-reviewer`, `security-auditor`, `database-designer`, `devops-engineer`
