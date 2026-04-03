# Testing Standards

## Test Organization
- Place tests alongside source code or in dedicated test directory
- Follow the same directory structure as source code
- Name test files to match the code they test
- Group tests by functionality being tested

## Test Types
- **Unit Tests** — Test individual functions and methods
- **Integration Tests** — Test component interactions
- **End-to-End Tests** — Test complete user workflows
- **Performance Tests** — Test speed and resource usage

## Test Quality
- Tests should be independent and repeatable
- Use descriptive test names that explain the scenario
- Test both happy path and edge cases
- Mock external dependencies appropriately
- Aim for meaningful coverage, not just high numbers

## Test Execution
- Run tests before committing changes
- Use CI/CD to run tests automatically
- Fix failing tests immediately
- Keep test suites fast
