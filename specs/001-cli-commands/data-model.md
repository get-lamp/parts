# Data Model

The existing data model will be extended to support the new requirements for adding parts.

## Part Model (`parts/models.py`)

The `Part` model will be updated to include the following fields:

- `package`: `str` - The component package type (e.g., DIP, SOP, QFP).
- `pins`: `int` - The number of pins on the component.

### Existing Fields to be Used:
- `identifier`: `str`
- `qty`: `int`
- `datasheet`: `str`
- `description`: `str`
- `category_id`: `int` (Foreign Key)

## Category Model (`parts/models.py`)

No changes are required to the `Category` model.