import subprocess
from prompt_toolkit import PromptSession, prompt as pt_prompt
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
from sqlalchemy.orm import selectinload
from sqlmodel import select
import parts.api as api
from parts.db import get_db_context
from parts.models import Category, Part


class CategoryPathCompleter(Completer):
    def __init__(self, datasheets_only=False):
        self.datasheets_only = datasheets_only
        super().__init__()

    def get_completions(self, document, complete_event):
        path_parts = document.text.split("/")
        resolved = path_parts[:-1]
        fragment = path_parts[-1]

        with get_db_context() as session:
            parent_id = None
            current_cat = None
            for component in resolved:
                query = select(Category).where(Category.identifier == component)
                if parent_id is not None:
                    query = query.where(Category.parent_id == parent_id)
                cat = session.exec(query).first()
                if cat is None:
                    return
                parent_id = cat.id
                current_cat = cat

            for child in session.exec(select(Category).where(Category.parent_id == parent_id)).all():
                if child.identifier.startswith(fragment):
                    yield Completion(child.identifier, start_position=-len(fragment))

            if current_cat is not None:
                query = select(Part).where(Part.category_id == current_cat.identifier)
                if self.datasheets_only:
                    query = query.where(Part.datasheet.isnot(None))
                for part in session.exec(query).all():
                    if part.identifier.startswith(fragment):
                        yield Completion(part.identifier, start_position=-len(fragment))


class GrammarAutocomplete(Completer):
    COMMANDS = ["add", "datasheet", "del", "list", "ll", "exit", "quit", "q"]

    def get_completions(self, document, complete_event):
        words = document.text.split(" ")
        sentence = words[:-1]
        last_word = words[-1]
        command = sentence[0] if sentence else None

        if "/" in last_word:
            yield from CategoryPathCompleter(datasheets_only=(command == "datasheet")).get_completions(
                Document(last_word), complete_event
            )
            return

        if command is None:
            for cmd in self.COMMANDS:
                if cmd.startswith(last_word):
                    yield Completion(cmd, start_position=-len(last_word))

        if len(last_word) >= 2 or len(sentence) >= 1:
            next_types, next_subtypes = api.get_next_legal_token_types(" ".join(sentence))

            if len(next_types) == 0:
                return

            matches = api.match_token(last_word, entity_types=next_types, token_types=next_subtypes)
            for match in matches:
                yield Completion(match.identifier, start_position=-len(last_word))


def _parse_qty(s):
    """Parse '+3' -> ('add', 3), '-1' -> ('sub', 1), '42' -> ('set', 42). Returns (None, None) if not a qty arg."""
    if s.startswith("+"):
        try:
            return ("add", int(s[1:]))
        except ValueError:
            return (None, None)
    elif s.startswith("-"):
        try:
            return ("sub", int(s[1:]))
        except ValueError:
            return (None, None)
    else:
        try:
            return ("set", int(s))
        except ValueError:
            return (None, None)


def update_qty(part_ref, arg):
    op, val = _parse_qty(arg)
    leaf = part_ref.split("/")[-1]
    with get_db_context() as session:
        part = session.exec(
            select(Part)
            .where(Part.identifier == leaf)
            .options(selectinload(Part.category).selectinload(Category.parent))
        ).first()
        if not part:
            print(f"Part not found: {leaf}")
            return
        if op == "add":
            part.qty = (part.qty or 0) + val
        elif op == "sub":
            part.qty = (part.qty or 0) - val
        else:
            part.qty = val
        session.add(part)
        session.commit()
        _show_part(part)


def main():
    # api.init()

    session = PromptSession()
    completer = GrammarAutocomplete()

    while True:
        try:
            text = session.prompt("> ", completer=completer)
            parts = text.split()
            if len(text) == 0:
                continue

            # first word is the command
            command = parts[0]
            # rest of the line is passed by argument to the command handler
            args = parts[1:]

            if command == "add":
                add(args)
            elif command == "del":
                delete(args)
            elif command in ("list", "ll"):
                list_items(args)
            elif command == "datasheet":
                datasheet_cmd(args)
            elif command == "help":
                show_help()
            elif command in ("quit", "exit", "q"):
                break
            elif not args:
                _lookup(command)
            elif _parse_qty(args[0]) != (None, None):
                update_qty(command, args[0])
            else:
                print(f"Unknown command: {command}")
        except KeyboardInterrupt:
            continue
        except EOFError:
            break


def add(args):
    category_str = None
    identifier = None

    if args:
        arg = args[0]
        if "/" in arg:
            if arg.endswith("/"):
                category_str = arg.rstrip("/")
            else:
                last_slash = arg.rfind("/")
                category_str = arg[:last_slash]
                identifier = arg[last_slash + 1 :] or None
        else:
            identifier = arg

    if category_str is None:
        category_str = pt_prompt("category: ", completer=CategoryPathCompleter())

    if identifier is None:
        identifier = pt_prompt("identifier: ").strip()
        while not identifier:
            identifier = pt_prompt("identifier: ").strip()

    description = pt_prompt("description: ")

    qty_input = pt_prompt("qty: ", default="1").strip()
    try:
        qty = int(qty_input) if qty_input else 1
    except ValueError:
        qty = 1

    category_components = [c for c in category_str.split("/") if c] if category_str else []

    with get_db_context() as session:
        leaf_cat_identifier = None
        parent_id = None
        for cat_id_str in category_components:
            cat = api.get_or_create_category(session, identifier=cat_id_str, parent_id=parent_id)
            parent_id = cat.id
            leaf_cat_identifier = cat.identifier

        part = api.create_part(
            db=session,
            cat_id=leaf_cat_identifier,
            identifier=identifier,
            descript=description,
            qty=qty,
        )
        print(f"Added: {part.identifier}")


def delete(args):
    if len(args) != 1:
        print("Usage: del <category-identifier>|<part-identifier>")
        return

    identifier = args[0].split("/")[-1]

    with get_db_context() as session:
        # Try to find and delete a part
        statement = select(Part).where(Part.identifier == identifier)
        part = session.exec(statement).first()
        if part:
            confirm = input(f"Delete part '{identifier}'? [y/N] ")
            if confirm.lower() not in ("y", "yes"):
                return
            api.delete_part(session, part)
            print(f"Deleted part: {identifier}")
            return

        # Try to find and delete a category
        statement = select(Category).where(Category.identifier == identifier)
        category = session.exec(statement).first()
        if category:
            if category.parts or category.children:
                confirm = input(f"Category '{identifier}' is not empty. Delete anyway? [y/N] ")
                if confirm.lower() not in ("y", "yes"):
                    return
            else:
                confirm = input(f"Delete category '{identifier}'? [y/N] ")
                if confirm.lower() not in ("y", "yes"):
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


def _print_parts_table(parts):
    rows = [((_get_category_path(p.category) if p.category else ""), p.identifier, str(p.qty or 0), p.description or "") for p in parts]
    if not rows:
        return
    col1_w = max(len(r[0]) for r in rows)
    col2_w = max(len(r[1]) for r in rows)
    col3_w = max(len(r[2]) for r in rows)
    for cat, ident, qty, desc in rows:
        print(f"{cat:<{col1_w}}  {ident:<{col2_w}}  {qty:>{col3_w}}  {desc}")


def list_items(args):
    with get_db_context() as session:
        results = api.list_parts(session, args[0] if args else None)
        _print_parts_table(results)


def datasheet_cmd(args):
    if not args:
        with get_db_context() as session:
            results = [p for p in api.list_parts(session) if p.datasheet]
            _print_parts_table(results)
        return

    leaf = args[0].split("/")[-1]
    with get_db_context() as session:
        part = session.exec(select(Part).where(Part.identifier == leaf)).first()

    if not part:
        print(f"Part not found: {leaf}")
        return
    if not part.datasheet:
        print(f"No datasheet for: {part.identifier}")
        return

    subprocess.run(["open", part.datasheet])


def show_help():
    print("Commands:")
    print("  add <category>[/<child-category>/...] <identifier> [<description>]")
    print("  del <category-identifier>|<part-identifier>")
    print("  list [<category>/<child-category>/...]")
    print("  help")
    print("  exit")


if __name__ == "__main__":
    main()
