# Profile Template

> Copy this directory structure to `profiles/your-profile-name/` and fill in the TODO sections.

## Directory Structure

```
profiles/your-profile-name/
├── config.yml          # Profile configuration
└── standards/          # Profile-specific standards
    ├── coding-standards.md
    └── testing-standards.md
```

## config.yml

```yaml
# Profile: your-profile-name
# Description: TODO - What is this profile for?

inherits:
  - default              # Inherits from default profile
  # Add more parent profiles if needed

standards:
  - your-standard-name   # TODO: Add your profile-specific standards
  # These override or add to inherited standards
```

## Adding Standards

1. Create a new `.md` file in `standards/` using the standard template
2. Add the filename (without `.md`) to the `standards` list in `config.yml`
3. Test by running: `~/.agent-os/scripts/project-install.sh --profile your-profile-name`

## Inheritance Chain

```
your-profile-name → default
```

Standards are applied in order: parent first, then child. Child standards override parent standards with the same name.
