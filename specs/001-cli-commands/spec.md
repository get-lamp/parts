# Feature Specification: CLI Commands and Autocomplete

**Feature Branch**: `001-cli-commands`
**Created**: 2026-02-08
**Status**: Draft

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Command Line Interaction (Priority: P1)
As a user, I want to interact with the parts database through a command-line interface so that I can manage parts and categories efficiently.

**Why this priority**: This is the core functionality of the application.

**Independent Test**: The CLI can be tested by running the various commands and verifying the output and database state changes.

**Acceptance Scenarios**:
1. **Given** a part identifier, **When** I enter the identifier, **Then** the part's data is displayed.
2. **Given** a category identifier, **When** I enter the identifier, **Then** the category path and its sub-categories and parts are listed.
3. **Given** a part identifier and a quantity, **When** I use the `+` operator, **Then** the part's quantity is increased.
4. **Given** a part identifier and a quantity, **When** I use the `-` operator, **Then** the part's quantity is decreased.
5. **Given** the `add cat` or `add part` command, **When** I follow the prompts, **Then** a new category or part is created in the database.

### User Story 2 - Advanced Autocomplete (Priority: P2)
As a user, I want the CLI to provide intelligent autocomplete suggestions to speed up my workflow.

**Why this priority**: This feature significantly improves the user experience.

**Independent Test**: The autocomplete functionality can be tested by typing partial commands and verifying the suggestions.

**Acceptance Scenarios**:
1. **Given** an empty prompt, **When** I type 2 or more characters, **Then** autocomplete shows relevant options.
2. **Given** a complete word in the prompt, **When** I trigger autocomplete, **Then** the system offers the next logical continuation of the command.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a CLI for interacting with the parts database.
- **FR-002**: System MUST implement the following commands: show part, list category, add quantity, subtract quantity, add part, add category.
- **FR-003**: System MUST provide autocomplete suggestions based on the current input.
- **FR-004**: Autocomplete MUST trigger on strings of 2 or more characters from an empty prompt.
- **FR-005**: Autocomplete MUST offer continuations after a full word is typed.
- **FR-006**: Autocomplete MUST suggest sub-categories when a category is followed by a '/'.

### Key Entities *(include if feature involves data)*

- **Part**: Represents a physical component.
- **Category**: Represents a category of parts.

### Dependencies and Assumptions

- **DP-001**: Autocomplete functionality is dependent on the existing `parts/api.py::get_next_legal_token_types` function for narrowing down suggestions. This function can be refactored or improved as needed.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All specified CLI commands are functional and perform their described actions correctly.
- **SC-002**: Autocomplete suggestions are provided in under 200ms.
- **SC-003**: The CLI is the primary and fully functional interface for the application.

## Clarifications

### Session 2026-02-08
- Q: How should `get_next_legal_token_types` behave in the following edge cases: return all possible starting token types for an empty sentence. For invalid or incomplete sentences, return an empty list or a list of very general token types. → A: Return all possible starting token types for an empty sentence. For invalid or incomplete sentences, return an empty list or a list of very general token types.
- Q: If `get_next_legal_token_types` encounters an unrecoverable error, how should the autocomplete feature behave? → A: Display no suggestions but allow the user to continue typing. Log the error internally.
- Q: What should happen if a user provides a non-existent part identifier to a command like `show`, `+`, or `-`? → A: Display "Error: Part not found." to stderr.
- Q: How should autocomplete handle sub-category navigation? → A: If a user types a category followed by a '/', the autocomplete should suggest sub-categories of that category.

## Question 2: Error Handling for `get_next_legal_token_types`

**Context**: The autocomplete relies on `parts/api.py::get_next_legal_token_types`.

**What we need to know**: If `get_next_legal_token_types` encounters an unrecoverable error, how should the autocomplete feature behave?

**Recommended:** Option A - This ensures a resilient user experience by providing a graceful fallback, preventing the autocomplete from crashing, and potentially logging the error for debugging without disrupting the user.

| Option | Description | Implications |
|--------|-------------|--------------|
| A      | Display no suggestions but allow the user to continue typing. Log the error internally. | The user can still type, and the error can be investigated. |
| B      | Display a generic error message to the user. | This might be disruptive to the user experience. |
| C      | Disable autocomplete until the error is resolved. | This would severely impact usability. |
| Short | Provide a different short answer (<=5 words) | Provide a different short answer (<=5 words) |

You can reply with the option letter (e.g., "A"), accept the recommendation by saying "yes" or "recommended", or provide your own short answer.
