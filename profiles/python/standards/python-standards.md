# Python Standards

## Code Style
- Follow PEP 8 conventions
- Use 4 spaces for indentation
- Maximum line length: 120 characters
- Use meaningful variable and function names

## Type Hints
- Add type hints to all function signatures
- Use `typing` module for complex types
- Run `mypy` for type checking

## Imports
- Standard library imports first
- Third-party imports second
- Local imports last
- Use absolute imports over relative imports

## Documentation
- Use docstrings for all public functions and classes
- Follow Google or NumPy docstring style
- Include Args, Returns, and Raises sections

## Error Handling
- Use specific exception types
- Create custom exception classes for domain errors
- Never use bare `except:` clauses
