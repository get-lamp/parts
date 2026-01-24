from uuid import uuid4

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from sqlmodel import Session, select

from parts.db import engine, _insert, _get
from parts.models import Category, Part
import parts.api as api


def main():
    # api.init()
    session = PromptSession()
    completer = WordCompleter(["add", "del", "list", "help", "exit"], ignore_case=True)

    while True:
        try:
            text = session.prompt("> ", completer=completer)
            parts = text.split()
            command = parts[0]
            args = parts[1:]

            if command == "add":
                add(args)
            elif command == "del":
                delete(args)
            elif command == "list":
                list_items(args)
            elif command == "help":
                show_help()
            elif command == "exit":
                break
            else:
                print(f"Unknown command: {command}")
        except KeyboardInterrupt:
            continue
        except EOFError:
            break


def add(args):
    if len(args) < 2:
        print("Usage: add <category>[/<child-category>/...] <identifier> [<description>]")
        return

    category_path = args[0].split("/")
    identifier = args[1]
    description = " ".join(args[2:]) if len(args) > 2 else ""

    with Session(engine) as session:
        parent_id = None
        for category_name in category_path:
            category = api.get_or_create_category(session, name=category_name, parent_id=parent_id)
            parent_id = category.id

        part = api.create_part(
            db=session,
            category_id=parent_id,
            identifier=identifier,
            description=description,
        )
        print(f"Added part: {part.identifier}")


def delete(args):
    if len(args) != 1:
        print("Usage: del <category-identifier>|<part-identifier>")
        return

    identifier = args[0]

    with Session(engine) as session:
        # Try to find and delete a part
        statement = select(Part).where(Part.identifier == identifier)
        part = session.exec(statement).first()
        if part:
            api.delete_part(session, part)
            print(f"Deleted part: {identifier}")
            return

        # Try to find and delete a category
        statement = select(Category).where(Category.name == identifier)
        category = session.exec(statement).first()
        if category:
            # Check if the category is empty
            if category.parts or category.children:
                print(f"Category is not empty: {identifier}")
                return

            api.delete_category(session, category)
            print(f"Deleted category: {identifier}")
            return

        print(f"Part or category not found: {identifier}")


def _get_category_path(category: Category) -> str:
    path = [category.name]
    current = category
    while current.parent:
        current = current.parent
        path.append(current.name)
    return "/".join(reversed(path))


def list_items(args):
    results = api.list(args)

    for part in results:
        output_line = f"{part.path} {part.description}" if part.path else f"{part.identifier} {part.description}"
        print(output_line)


def show_help():
    print("Commands:")
    print("  add <category>[/<child-category>/...] <identifier> [<description>]")
    print("  del <category-identifier>|<part-identifier>")
    print("  list [<category>/<child-category>/...]")
    print("  help")
    print("  exit")


if __name__ == "__main__":
    main()


def test_create_and_get_category(session):
    category = _insert(session, Category(name="Electronics"))
    assert category.id is not None
    assert category.name == "Electronics"

    fetched_category = _get(session, Category, category.id)
    assert fetched_category.name == "Electronics"


def test_create_and_get_part(session):
    category = _insert(session, Category(name="Mechanics"))

    part_uuid = uuid4()
    part = _insert(
        session,
        Part(
            uuid=part_uuid,
            category_id=category.id,
            identifier="Bolt_M3",
            qty=100,
            datasheet="http://example.com/bolt.pdf",
            description="M3 Hex Bolt",
        ),
    )

    assert part.id is not None
    assert part.uuid == part_uuid
    assert part.identifier == "Bolt_M3"

    fetched_part = _get(session, Part, part.id)
    assert fetched_part.uuid == part_uuid
    assert fetched_part.category.name == "Mechanics"


def test_create_and_get_nested_categories(session):
    parent_category = _insert(session, Category(name="Electronics"))
    assert parent_category.id is not None
    assert parent_category.name == "Electronics"

    child_category = _insert(session, Category(name="Resistors", parent_id=parent_category.id))

    assert child_category.id is not None
    assert child_category.name == "Resistors"
    assert child_category.parent_id == parent_category.id

    # Fetch parent again to check children relationship
    fetched_parent_category = _get(session, Category, parent_category.id)
    assert len(fetched_parent_category.children) == 1
    assert fetched_parent_category.children[0].name == "Resistors"

    # Fetch child again to check parent relationship
    fetched_child_category = _get(session, Category, child_category.id)
    assert fetched_child_category.parent is not None
    assert fetched_child_category.parent.name == "Electronics"
