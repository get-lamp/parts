# Data Model

The existing data model will be extended to include `package` and `pins` in the `Part` model.

## Part

- **identifier**: str (indexed, unique)
- **qty**: int
- **package**: str (e.g. DIP, SMD...)
- **pins**: int
- **datasheet**: str
- **description**: str
- **category_id**: int (foreign key to Category)
