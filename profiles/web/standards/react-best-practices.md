# React Best Practices

## Component Structure
- Use functional components with hooks
- Keep components small and focused (single responsibility)
- Extract reusable logic into custom hooks
- Use composition over inheritance

## State Management
- Use `useState` for local component state
- Use `useContext` for shared state across components
- Use external state libraries (Zustand, Redux) for complex global state
- Avoid prop drilling — use context or state management

## Performance
- Use `React.memo()` for expensive components
- Use `useMemo` for expensive computations
- Use `useCallback` for functions passed as props
- Lazy load routes and heavy components with `React.lazy()`

## Naming
- Component names: PascalCase (`UserProfile`)
- Hook names: camelCase with `use` prefix (`useAuth`)
- Event handlers: `handle<Event>` (`handleClick`)
- Boolean props: `is*`, `has*`, `can*` (`isLoading`)

## Examples

### Good
```tsx
const UserCard: React.FC<UserCardProps> = ({ user, onSelect }) => {
  const handleClick = useCallback(() => onSelect(user.id), [user.id, onSelect]);
  
  return <div onClick={handleClick}>{user.name}</div>;
};
```

### Bad
```tsx
function UserCard(props) {
  return <div onClick={() => props.onSelect(props.user.id)}>{props.user.name}</div>;
}
```
