# Tasks: CLI Commands and Autocomplete

**Input**: Design documents from `/specs/001-cli-commands/`

## Phase 1: Foundational (Blocking Prerequisites)

- [ ] T001 [P] Modify `parts/models.py` to add `package` and `pins` fields to the `Part` model.
- [ ] T002 [P] Create `tests/test_cli.py` to house tests for the command-line interface.
- [ ] T003 [P] Add tests to `tests/test_models.py` to verify the new `Part` model fields.

---

## Phase 2: User Story 1 - Command Line Interaction (Priority: P1) 🎯 MVP

**Goal**: Implement the core CLI commands for viewing and managing parts and categories.

**Independent Test**: The CLI can be tested by invoking each command with valid and invalid inputs and asserting the output and database state.

### Tests for User Story 1 (TDD)

- [ ] T004 [P] [US1] In `tests/test_api.py`, write a test for a new function `get_part_details` that retrieves a part and its full category path.
- [ ] T005 [P] [US1] In `tests/test_api.py`, write a test for a new function `get_category_details` that retrieves a category, its full path, its sub-categories, and its parts.
- [ ] T006 [P] [US1] In `tests/test_api.py`, write tests for updating part quantities (`add_part_quantity`, `subtract_part_quantity`).
- [ ] T007 [P] [US1] In `tests/test_api.py`, write tests for adding a new `Part` and `Category`.
- [ ] T008 [P] [US1] In `tests/test_cli.py`, write unit tests for the function that handles the `show part` command logic.
- [ ] T009 [P] [US1] In `tests/test_cli.py`, write unit tests for the function that handles the `list category` command logic.
- [ ] T010 [P] [US1] In `tests/test_cli.py`, write unit tests for the functions that handle quantity modification (`+` and `-`).
- [ ] T011 [P] [US1] In `tests/test_cli.py`, write unit tests for the functions that handle the interactive `add part` and `add cat` commands.

### Implementation for User Story 1

- [ ] T012 [US1] In `parts/api.py`, implement `get_part_details`.
- [ ] T013 [US1] In `parts/api.py`, implement `get_category_details`.
- [ ] T014 [US1] In `parts/api.py`, implement `add_part_quantity` and `subtract_part_quantity`.
- [ ] T015 [US1] In `parts/api.py`, implement `add_part` and `add_category`.
- [ ] T016 [US1] In `cli.py`, implement the main application loop and command parsing.
- [ ] T017 [US1] In `cli.py`, implement the logic for the `show part`, `list category`, and quantity modification commands.
- [ ] T018 [US1] In `cli.py`, implement the interactive prompts for `add part` and `add cat`.

---

## Phase 3: User Story 2 - Advanced Autocomplete (Priority: P2)

**Goal**: Implement an intelligent autocomplete system to enhance the CLI's usability.

**Independent Test**: The autocomplete can be tested by simulating user input and asserting the correctness of the suggested completions.

### Tests for User Story 2 (TDD)

- [ ] T019 [P] [US2] In `tests/test_api.py`, write tests for `get_next_legal_token_types` to handle empty and invalid inputs.
- [ ] T020 [P] [US2] In `tests/test_api.py`, write tests to verify that `get_next_legal_token_types` correctly suggests sub-categories when given a category followed by a '/'.
- [ ] T021 [P] [US2] In `tests/test_api.py`, write tests to ensure that autocomplete results are being cached in `parts.parser.LEXICON`.
- [ ] T022 [P] [US2] In `tests/test_cli.py`, write tests for the autocomplete behavior in various scenarios.

### Implementation for User Story 2

- [ ] T023 [US2] In `parts/api.py`, refactor `get_next_legal_token_types` to handle the edge cases and sub-category logic defined in the spec.
- [ ] T024 [US2] In `parts/api.py`, implement the caching logic for `get_next_legal_token_types` using `parts.parser.LEXICON`.
- [ ] T025 [US2] In `cli.py`, integrate the autocomplete functionality into the input prompt.

---

## Phase 4: Polish & Cross-Cutting Concerns

- [ ] T026 [P] Update the `README.md` with instructions on how to use the new CLI commands.
- [ ] T027 [P] Ensure all code is formatted with `ruff` and passes linting checks.
- [ ] T028 [P] Manually run through the scenarios in `quickstart.md` to ensure everything works as expected.
