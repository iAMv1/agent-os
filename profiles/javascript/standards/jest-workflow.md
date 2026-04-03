# Jest Workflow

## Test Organization
- Place tests alongside source files as `*.test.ts` or `*.spec.ts`
- Use `describe` blocks for grouping related tests
- Use `it` or `test` for individual test cases

## Test Structure
- Follow Arrange-Act-Assert pattern
- Use `beforeEach`/`afterEach` for setup/teardown
- Use `jest.mock()` for mocking modules
- Use `jest.fn()` for function mocks

## Running Tests
```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch

# Run specific test file
npm test -- path/to/test.test.ts
```

## Test Quality
- Test behavior, not implementation details
- Use descriptive test names: "should return X when Y"
- Mock external dependencies (APIs, databases, file system)
- Use `expect.assertions()` for async tests
