# Type Hinting Standards

## Function Signatures
- Always add type hints to parameters and return types
- Use `Optional[T]` for parameters that can be `None`
- Use `Union[T1, T2]` for multiple possible types (Python 3.9+: `T1 | T2`)
- Use `Any` sparingly — prefer specific types

## Class Definitions
- Add type hints to all instance attributes
- Use `__init__` parameter type hints
- Consider using `dataclasses` for data containers

## Generic Types
- Use `typing.Generic` for container classes
- Use `TypeVar` for generic function signatures
- Use `Protocol` for structural subtyping

## Validation
- Run `mypy --strict` for comprehensive type checking
- Use `reveal_type()` for debugging type inference
- Add `# type: ignore` only with specific error code and comment

## Examples

### Good
```python
def process_items(items: list[str], max_count: int | None = None) -> dict[str, int]:
    """Process a list of items and return counts."""
    limit = max_count or len(items)
    return {item: items.count(item) for item in items[:limit]}
```

### Bad
```python
def process_items(items, max_count=None):
    limit = max_count or len(items)
    return {item: items.count(item) for item in items[:limit]}
```
