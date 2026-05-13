import os
import shutil

from parts import api
from parts.db import with_db

DATA_DIR = "./data"
DATASHEET_DIR = "./datasheets"


@with_db
def seed_data(session):
    api.init()

    # First pass: Create all categories based on non-leaf directories
    category_map = {}  # (identifier, parent_id) -> category_object

    for root, dirs, files in os.walk(DATA_DIR):
        relative_path = os.path.relpath(root, DATA_DIR)
        if relative_path == ".":  # Skip the root data directory itself as a category
            continue

        path_components = relative_path.split(os.sep)

        # Only process as a category if it's not a leaf folder in terms of containing other categories
        if dirs:  # if there are subdirectories, it's a category
            parent_id_for_this_category = None
            for component in path_components:
                category_key = (component, parent_id_for_this_category)

                if category_key not in category_map:
                    created_category = api.create_category(
                        db=session,
                        identifier=component,
                        parent_id=parent_id_for_this_category,
                    )

                    category_map[category_key] = created_category
                else:
                    created_category = category_map[category_key]

                parent_id_for_this_category = created_category.id

    # Second pass: Create parts in leaf directories
    for root, dirs, files in os.walk(DATA_DIR):
        if not dirs:  # This is a leaf folder, containing parts
            relative_path = os.path.relpath(root, DATA_DIR)
            path_components = relative_path.split(os.sep)

            # The last component of the path is implicitly the part's identifier folder, not a category.
            # Its parent is the actual category.
            parent_category_id_for_part = None

            if len(path_components) > 1:
                temp_parent_id = None

                # All components EXCEPT the last one (the part identifier folder)
                for component in path_components[:-1]:
                    category_key = (component, temp_parent_id)
                    if category_key in category_map:
                        temp_parent_id = category_map[category_key].id
                    else:
                        print(f"Warning: Parent category '{component}' not found for path '{relative_path}'")
                        break
                parent_category_id_for_part = temp_parent_id

            for file in files:
                if file.endswith(".data"):
                    data_file_path = os.path.join(root, file)
                    with open(data_file_path, "r") as f:
                        lines = f.readlines()
                        identifier = lines[0].strip()
                        try:
                            qty = int(lines[1].strip())
                        except (ValueError, IndexError):
                            qty = 0
                        try:
                            description = lines[2].strip()
                        except IndexError:
                            description = ""

                    datasheet_path = None
                    for f_other in os.listdir(root):
                        if f_other.endswith(".pdf"):
                            source_path = os.path.join(root, f_other)
                            file_extension = os.path.splitext(f_other)[1]
                            dest_filename = f"{identifier}{file_extension}"
                            dest_path = os.path.join(DATASHEET_DIR, dest_filename)
                            shutil.copy(source_path, dest_path)
                            datasheet_path = dest_path
                            break

                    api.create_part(
                        db=session,
                        identifier=identifier,
                        descript=description,
                        qty=qty,
                        datasheet=datasheet_path,
                        cat_id=parent_category_id_for_part,
                    )


if __name__ == "__main__":
    seed_data()
