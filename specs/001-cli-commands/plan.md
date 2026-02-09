# Implementation Plan: Implement CLI commands and autocomplete

**Branch**: `001-cli-commands` | **Date**: 2026-02-08 | **Spec**: `/home/no-carrier/src/64k/agentic/parts/specs/001-cli-commands/spec.md`

## Summary

This feature will implement a set of CLI commands for interacting with the parts database, including showing parts, listing categories, adding/subtracting quantity, and adding new parts and categories. It will also add an advanced autocomplete feature to the CLI, including sub-category navigation and caching.

## Technical Context

**Language/Version**: Python
**Primary Dependencies**: SQLModel, Ruff
**Storage**: SQLite
**Testing**: pytest
**Target Platform**: Linux
**Project Type**: Single project (CLI application)
**Performance Goals**: Autocomplete suggestions must be returned in < 200ms.
**Constraints**: Must adhere to the existing data model, layer boundaries, and use the existing `get_next_legal_token_types` function and `LEXICON` cache.
**Scale/Scope**: This will be the primary user interface for the application.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Tech Stack**: Aligns with Python, SQLite, SQLModel.
- **Libraries**: Aligns with Ruff for linting.
- **Style**: Adheres to the style guide (120 char limit, functions over classes, etc.).
- **Testing**: All new CLI and API functionality will be covered by pytest tests.
- **Layer Boundaries**: All interactions will follow the `cli.py` -> `parts.api.py` -> `parts.parser.py`/`parts.db.py` flow.
- **Existing Codebase**: The plan will leverage existing fixtures from `conftest.py` and respect the immutability of `_grammar` and `LEXICON` structure.

**Result**: PASS. No violations detected.

## Project Structure

### Documentation (this feature)

```text
specs/001-cli-commands/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── cli.md
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

The implementation will modify the existing project structure.

```text
parts/
├── api.py           # To be modified
├── models.py        # To be modified
└── parser.py        # To be modified
cli.py               # To be created/modified
tests/
├── test_api.py      # To be modified
└── test_parser.py   # To be modified
test_cli.py          # To be created
```

**Structure Decision**: Adhere to the existing single project structure. New functionality will be added to `cli.py` and `parts/api.py`, with corresponding tests in `tests/`.

## Complexity Tracking

No violations to the constitution were identified.
