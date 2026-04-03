# Component Patterns

## Container/Presentational Pattern
- Separate data fetching (container) from rendering (presentational)
- Presentational components receive data via props only
- Container components handle state, API calls, and business logic

## Compound Components
- Use `React.Children.map` and `React.cloneElement` for compound patterns
- Example: `<Select><Option /></Select>`
- Share implicit state through React context

## Render Props
- Use render props for reusable behavior injection
- Example: `<DataProvider render={data => <List items={data} />} />`

## Custom Hooks Pattern
- Extract shared stateful logic into `use*` hooks
- Hooks should be pure functions with no side effects beyond React state
- Test hooks independently with `@testing-library/react-hooks`

## File Organization
```
src/components/
├── UserCard/
│   ├── UserCard.tsx       # Main component
│   ├── UserCard.test.tsx  # Tests
│   ├── UserCard.stories.tsx # Storybook
│   └── index.ts           # Barrel export
```
