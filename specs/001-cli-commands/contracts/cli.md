# CLI Contracts

This document outlines the commands that will be available in the CLI.

## Show Part

**Command**: `<part_identifier>`
**Description**: Displays the detailed data for a specific part, including its full category path.
**Example**: `> 74hc04`

## List Category

**Command**: `<category_identifier>`
**Description**: Displays the category's full path and lists all its direct sub-categories and parts.
**Example**: `> gates`
**Sub-category Example**: `> gates/not`

## Add Quantity

**Command**: `<part_identifier> + <quantity>`
**Description**: Increases the quantity of a specified part.
**Example**: `> 74hc04 + 10`

## Subtract Quantity

**Command**: `<part_identifier> - <quantity>`
**Description**: Decreases the quantity of a specified part.
**Example**: `> 74hc04 - 5`

## Add Part or Category

**Command**: `add part` or `add cat`
**Description**: Enters an interactive mode to add a new part or category. The user will be prompted for the required information.

## Autocomplete

**Behavior**:
-   Triggers on 2+ characters in an empty prompt.
-   Offers next legal tokens after a full word is typed.
-   Supports sub-category navigation using the `/` character.
-   Caches results in `parts.parser.LEXICON`.