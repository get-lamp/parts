# Implementation Plan: Implement CLI commands and autocomplete

**Branch**: `001-cli-commands` | **Date**: 2026-02-08 | **Spec**: [link]
**Input**: Feature specification from `/specs/001-cli-commands/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This feature will implement a set of CLI commands for interacting with the parts database, including showing parts, listing categories, adding/subtracting quantity, and adding new parts and categories. It will also add an autocomplete feature to the CLI.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: SQLModel, Ruff
**Storage**: SQLite
**Testing**: pytest
**Target Platform**: Linux server
**Project Type**: single
**Performance Goals**: Autocomplete suggestions should appear in < 200ms
**Constraints**: The existing data model and layer boundaries must be respected.
**Scale/Scope**: The CLI will be the primary interface for this application.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Tech Stack**: Python, SQLite, SQLModel
- **Libraries**: Ruff for linting
- **Style**: 120 char line limit, minimize verbosity, no classes, comments explain 'why'.
- **Testing**: All behavior covered by pytest tests.
- **Layer Boundaries**: `cli.py` -> `parts.api.py` -> `parts.parser.py`/`parts.db.py`/`models.py`

## Project Structure

### Documentation (this feature)

```text
specs/001-cli-commands/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
```text
# Option 1: Single project (DEFAULT)
parts/
├── __init__.py
├── api.py
├── db.py
├── models.py
└── parser.py

tests/
├── __init__.py
├── conftest.py
├── data.py
├── test_api.py
└── test_parser.py
```

**Structure Decision**: The existing project structure will be used.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
|           |            |                                     |