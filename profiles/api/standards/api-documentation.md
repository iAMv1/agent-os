# API Documentation

## OpenAPI/Swagger
- Document all endpoints with OpenAPI 3.0 specification
- Include request/response schemas for every endpoint
- Provide example request and response bodies
- Document authentication requirements per endpoint

## Documentation Structure
For each endpoint, document:
- **URL** and HTTP method
- **Description** — what this endpoint does
- **Authentication** — required auth type
- **Request** — headers, path params, query params, body schema
- **Response** — success response schema, error response schemas
- **Examples** — curl request and response example

## Inline Documentation
- Add docstrings to route handlers
- Document query parameters and their defaults
- Document error conditions and status codes
- Keep documentation in sync with code changes

## Auto-Generation
- Use framework tools to auto-generate docs from code:
  - FastAPI: automatic OpenAPI from type hints
  - Express: `swagger-jsdoc` with JSDoc comments
  - Django REST: `drf-spectacular` or `drf-yasg`
