# Quickstart Guide

This guide provides a brief overview of how to use the CLI application.

## Getting Started

To start the application, run the following command from the project root:

```bash
python cli.py
```

## Basic Commands

-   **Show a part**: Type the part's identifier and press Enter.
    ```
    > 74hc04
    ```

-   **List a category**: Type the category's identifier and press Enter.
    ```
    > gates
    ```

-   **Navigate sub-categories**: Use a `/` to navigate into sub-categories.
    ```
    > gates/not
    ```

-   **Adjust quantity**: Use `+` and `-` to change a part's quantity.
    ```
    > 74hc04 + 20
    > 74hc04 - 5
    ```

## Adding New Items

-   **Add a part**:
    ```
    > add part
    ```
    You will be prompted to enter the details for the new part.

-   **Add a category**:
    ```
    > add cat
    ```
    You will be prompted to enter the details for the new category.

## Autocomplete

The CLI features an advanced autocomplete system.
-   Start typing (at least 2 characters) and press `Tab` to see suggestions.
-   After typing a full word (like a category), press `Tab` to see what can come next.
-   Use `/` to explore sub-categories.