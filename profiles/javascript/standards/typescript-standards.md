# TypeScript Standards

## Code Style
- Use 2 spaces for indentation
- Maximum line length: 120 characters
- Use `const` by default, `let` only when reassignment is needed
- Never use `var`

## Type Safety
- Enable `strict: true` in `tsconfig.json`
- Avoid `any` — use `unknown` when type is truly unknown
- Use explicit return types on exported functions
- Use interfaces for object shapes, types for unions

## Imports
- Use ES module syntax (`import`/`export`)
- Group imports: external, internal, relative
- Use barrel exports (`index.ts`) sparingly

## Naming
- Use PascalCase for types, interfaces, classes
- Use camelCase for variables, functions, methods
- Use UPPER_SNAKE_CASE for constants
- Prefix interfaces with `I` only when it represents a contract

## Error Handling
- Use typed errors with custom error classes
- Never swallow errors silently
- Use `try/catch` with type narrowing in catch blocks
