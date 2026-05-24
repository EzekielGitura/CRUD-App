import argparse
from typing import Iterable, Optional

from app import crud


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage items in a JSON CRUD store.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser("create", help="Create an item")
    create_parser.add_argument("--name", required=True)
    create_parser.add_argument("--description", required=True)

    subparsers.add_parser("list", help="List all items")

    get_parser = subparsers.add_parser("get", help="Get an item by ID")
    get_parser.add_argument("--id", required=True)

    update_parser = subparsers.add_parser("update", help="Update an item")
    update_parser.add_argument("--id", required=True)
    update_parser.add_argument("--name")
    update_parser.add_argument("--description")

    delete_parser = subparsers.add_parser("delete", help="Delete an item")
    delete_parser.add_argument("--id", required=True)

    return parser


def _print_item(item) -> None:
    print(f"{item.id}: {item.name}")
    print(f"  {item.description}")
    print(f"  created: {item.created_at}")
    if item.updated_at:
        print(f"  updated: {item.updated_at}")


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "create":
            item = crud.create_item(args.name, args.description)
            print(f"Created item {item.id}")
            return 0

        if args.command == "list":
            items = crud.get_items()
            if not items:
                print("No items found.")
                return 0

            for item in items:
                _print_item(item)
            return 0

        if args.command == "get":
            item = crud.get_item_by_id(args.id)
            if item is None:
                print(f"Item not found: {args.id}")
                return 1

            _print_item(item)
            return 0

        if args.command == "update":
            if args.name is None and args.description is None:
                print("Error: provide --name, --description, or both.")
                return 1

            item = crud.update_item(args.id, name=args.name, description=args.description)
            if item is None:
                print(f"Item not found: {args.id}")
                return 1

            print(f"Updated item {item.id}")
            return 0

        if args.command == "delete":
            if not crud.delete_item(args.id):
                print(f"Item not found: {args.id}")
                return 1

            print(f"Deleted item {args.id}")
            return 0

    except ValueError as exc:
        print(f"Error: {exc}")
        return 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
