from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from sqlalchemy.orm import selectinload
from sqlmodel import select
import parts.api as api
from parts.db import get_db_context
from parts.models import Category, Part


class GrammarAutocomplete(Completer):
    def __init__(self):
        self.sentence = []
        super().__init__()

    def get_completions(self, document, complete_event):
        words = document.text.split(" ")
        sentence = words[:-1]
        last_word = words[-1]

        if "/" in last_word:
            yield from self._complete_category_path(last_word)
            return

        next_types, next_subtypes = api.get_next_legal_token_types(" ".join(sentence))

        if len(last_word) >= 2 or len(sentence) >= 1:
            matches = api.match_token(last_word, entity_types=next_types, token_types=next_subtypes)

            for match in matches:
                yield Completion(match.identifier, start_position=-len(last_word))

    def _complete_category_path(self, path_text):
        path_parts = path_text.split("/")
        resolved = path_parts[:-1]
        fragment = path_parts[-1]

        with get_db_context() as session:
            parent_id = None
            current_cat = None
            for component in resolved:
                cat = session.exec(
                    select(Category).where(Category.identifier == component).where(Category.parent_id == parent_id)
                ).first()
                if cat is None:
                    return
                parent_id = cat.id
                current_cat = cat

            children = session.exec(select(Category).where(Category.parent_id == parent_id)).all()
            for child in children:
                if child.identifier.startswith(fragment):
                    yield Completion(child.identifier, start_position=-len(fragment))

            if current_cat is not None:
                parts = session.exec(select(Part).where(Part.category_id == current_cat.identifier)).all()
                for part in parts:
                    if part.identifier.startswith(fragment):
                        yield Completion(part.identifier, start_position=-len(fragment))

        """
        # keywords
        for keyword in self.grammar.keywords:
            if keyword.startswith(last_word):
                yield Completion(keyword, start_position=-len(last_word))

        # identifiers
        if len(last_word) >= 2:
            matches = parts.parser.api.match_token(last_word, entity_types=[], token_types=["identifier"])

            for match in matches:
                yield Completion(match.identifier, start_position=-len(last_word))
        """


def main():
    # api.init()

    session = PromptSession()
    completer = GrammarAutocomplete()

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
            elif command in ("exit", "q"):
                break
            elif not args:
                _lookup(command)
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

    with get_db_context() as session:
        parent_id = None
        for category_identifier in category_path:
            category = api.get_or_create_category(session, identifier=category_identifier, parent_id=parent_id)
            parent_id = category.id

        part = api.create_part(
            db=session,
            cat_id=parent_id,
            identifier=identifier,
            descript=description,
        )
        print(f"Added part: {part.identifier}")


def delete(args):
    if len(args) != 1:
        print("Usage: del <category-identifier>|<part-identifier>")
        return

    identifier = args[0]

    with get_db_context() as session:
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


def _lookup(token):
    leaf = token.split("/")[-1]
    with get_db_context() as session:
        part = session.exec(
            select(Part)
            .where(Part.identifier == leaf)
            .options(selectinload(Part.category).selectinload(Category.parent))
        ).first()
        if part:
            _show_part(part)
            return

        category = session.exec(select(Category).where(Category.identifier == leaf)).first()
        if category:
            list_items([token])
            return

    print(f"Not found: {token}")


def _show_part(part):
    category_path = _get_category_path(part.category) if part.category else ""
    print(f"identifier  {part.identifier}")
    if category_path:
        print(f"category    {category_path}")
    print(f"qty         {part.qty or 0}")
    if part.description:
        print(f"description {part.description}")
    if part.datasheet:
        print(f"datasheet   {part.datasheet}")


def _get_category_path(category: Category) -> str:
    path = [category.identifier]
    current = category
    while current.parent:
        current = current.parent
        path.append(current.identifier)
    return "/".join(reversed(path))


def list_items(args):
    with get_db_context() as session:
        results = api.list_parts(session, args[0] if args else None)

        rows = []
        for part in results:
            category_path = _get_category_path(part.category) if part.category else ""
            rows.append((category_path, part.identifier, part.description or ""))

        if not rows:
            return

        col1_w = max(len(r[0]) for r in rows)
        col2_w = max(len(r[1]) for r in rows)

        for cat, ident, desc in rows:
            print(f"{cat:<{col1_w}}  {ident:<{col2_w}}  {desc}")


def show_help():
    print("Commands:")
    print("  add <category>[/<child-category>/...] <identifier> [<description>]")
    print("  del <category-identifier>|<part-identifier>")
    print("  list [<category>/<child-category>/...]")
    print("  help")
    print("  exit")


if __name__ == "__main__":
    main()
