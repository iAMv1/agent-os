# REST Conventions

## URL Design
- Use nouns for resources, not verbs (`/users`, not `/getUsers`)
- Use plural nouns for collections (`/users`, `/todos`)
- Use nested resources for relationships (`/users/{id}/todos`)
- Use query parameters for filtering, sorting, pagination (`?status=active&sort=name&page=2`)

## HTTP Methods
- `GET` — Retrieve resources (idempotent, no side effects)
- `POST` — Create new resources
- `PUT` — Replace entire resource (idempotent)
- `PATCH` — Partial update of resource
- `DELETE` — Remove resource (idempotent)

## Response Format
```json
{
  "data": { ... },
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 100
  }
}
```

## Error Responses
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": [
      { "field": "email", "message": "Invalid email format" }
    ]
  }
}
```

## Status Codes
- `200` — Success
- `201` — Created
- `400` — Bad Request (validation error)
- `401` — Unauthorized (not authenticated)
- `403` — Forbidden (not authorized)
- `404` — Not Found
- `500` — Internal Server Error
