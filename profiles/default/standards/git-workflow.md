# Git Workflow

## Branch Strategy
- `main` — Production-ready code
- `develop` — Integration branch for features
- `feature/*` — New features and enhancements
- `fix/*` — Bug fixes
- `release/*` — Release preparation

## Commit Messages
- Use conventional commits format: `type(scope): description`
- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
- Keep subject line under 72 characters
- Use imperative mood ("Add feature" not "Added feature")

## Pull Requests
- Create PRs for all changes to main branches
- Include description of changes and testing done
- Request review from at least one team member
- Squash and merge for clean history

## Code Review
- Review for correctness, clarity, and completeness
- Check for security implications
- Verify tests cover new functionality
- Ensure documentation is updated
