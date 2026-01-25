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
        for category_identifier in category_path:
            category = api.get_or_create_category(session, identifier=category_identifier, parent_id=parent_id)
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
        statement = select(Category).where(Category.identifier == identifier)
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
    path = [category.identifier]
    current = category
    while current.parent:
        current = current.parent
        path.append(current.identifier)
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
