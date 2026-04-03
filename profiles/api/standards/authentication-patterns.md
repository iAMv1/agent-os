# Authentication Patterns

## Token-Based Authentication
- Use JWT (JSON Web Tokens) for stateless authentication
- Store tokens in HTTP-only cookies (not localStorage)
- Set reasonable expiration times (access: 15min, refresh: 7 days)
- Implement token refresh flow

## Authorization
- Use role-based access control (RBAC) for most applications
- Use attribute-based access control (ABAC) for complex permissions
- Validate permissions on every request (never trust client)
- Return `401` for unauthenticated, `403` for unauthorized

## Password Security
- Hash passwords with bcrypt (cost factor ≥ 12) or argon2
- Enforce minimum password requirements (8+ chars, complexity)
- Implement rate limiting on login endpoints
- Support password reset with time-limited tokens

## API Key Authentication
- Use API keys for service-to-service communication
- Rotate keys regularly
- Scope keys to specific permissions
- Never expose keys in client-side code

## Examples

### Good: JWT Auth Flow
```
1. POST /auth/login → { access_token, refresh_token }
2. GET /users/me (Authorization: Bearer <access_token>) → { user }
3. POST /auth/refresh (refresh_token) → { new_access_token }
```

### Bad
- Storing tokens in localStorage (XSS vulnerability)
- No token expiration
- Sending credentials in URL query parameters
