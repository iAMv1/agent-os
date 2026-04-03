# Changelog

All notable changes to AgentOS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Cross-platform installation scripts (Unix `.sh` and Windows `.ps1`)
- Profile system with inheritance chains (default, python, javascript, web, api)
- 5 slash commands: `/discover-standards`, `/inject-standards`, `/shape-spec`, `/ralph-loop`, `/workflow`
- Comprehensive documentation (7 new docs files)
- 44 automated tests covering all engine components
- `pyproject.toml` for Python package management
- Capability registry JSON export at `registry/capability-registry.json`
- Uninstall scripts for clean removal

### Fixed
- **Critical**: Fixed fatal import bug in `workflow-engine.py` (was importing from non-existent subdirectories)
- Fixed test suite to match actual API surface of engine components
- Fixed empty directory references (populated `registry/`, created `templates/`)

### Changed
- Restructured README to be concise and marketing-focused
- Documentation now links to `docs/INSTALLATION.md` instead of inline instructions
- Engine files now use flat imports (no subdirectory structure)

## [0.1.0] - 2026-04-03

### Initial Release
- Three-pillar architecture: Ralph Loop + Superpowers + Workflow Engine
- Workflow engine with task classifier, capability registry, workflow composer, execution engine, and adaptation layer
- 71 capabilities cataloged (35 tools, 11 agents, 11 services, 5 hooks, 9 commands)
- 7 workflow templates (Requirements, Architecture, Implementation, Testing, Deployment, Maintenance, Full SDLC)
- 27 universal skills
- Python package with session management, memory extraction, context deduplication, MCP management, tool system, self-healing, and git integration
