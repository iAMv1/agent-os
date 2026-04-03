# ESLint Rules

## Configuration
- Use `@typescript-eslint/parser` for TypeScript files
- Extend `eslint:recommended` and `@typescript-eslint/recommended`
- Enable `no-unused-vars`, `no-console` (warn), `prefer-const`

## Rules to Enforce
- `@typescript-eslint/no-explicit-any`: error
- `@typescript-eslint/explicit-function-return-type`: warn
- `@typescript-eslint/no-unused-vars`: error
- `no-console`: warn (allow in development)
- `prefer-const`: error
- `eqeqeq`: error (always use === and !==)

## Auto-fix
- Run `eslint --fix` before committing
- Configure editor to auto-fix on save
- Use Prettier for formatting (separate from linting)

## Examples

### Good
```typescript
const name: string = "AgentOS";
function greet(user: User): string {
  return `Hello, ${user.name}`;
}
```

### Bad
```typescript
var name = "AgentOS";
function greet(user) {
  return "Hello, " + user.name;
}
```
