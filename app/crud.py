import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.models import Item
from app.utils import validate_item_data


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if os.environ.get("CRUD_DB_PATH"):
    DB_PATH = os.environ["CRUD_DB_PATH"]
elif os.environ.get("VERCEL") or os.environ.get("VERCEL_ENV"):
    DB_PATH = str(Path(tempfile.gettempdir()) / "crud-app-db.json")
else:
    DB_PATH = str(PROJECT_ROOT / "data" / "db.json")


def _empty_db() -> Dict[str, List[Dict[str, Any]]]:
    return {"items": []}


def _load_db() -> Dict[str, List[Dict[str, Any]]]:
    path = Path(DB_PATH)
    if not path.exists():
        return _empty_db()

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if "items" not in data or not isinstance(data["items"], list):
        return _empty_db()

    return data


def _save_db(data: Dict[str, List[Dict[str, Any]]]) -> None:
    path = Path(DB_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def _find_item_index(items: List[Dict[str, Any]], item_id: str) -> Optional[int]:
    for index, item in enumerate(items):
        if str(item.get("id")) == str(item_id):
            return index
    return None


def create_item(name: str, description: str) -> Item:
    """Create and persist a new item."""
    errors = validate_item_data({"name": name, "description": description})
    if errors:
        raise ValueError("; ".join(errors))

    db = _load_db()
    item = Item.create(str(uuid4()), name.strip(), description.strip())
    db["items"].append(item.to_dict())
    _save_db(db)
    return item


def get_items(limit: Optional[int] = None, offset: int = 0) -> List[Item]:
    """Return all items, optionally sliced for simple pagination."""
    items = [Item.from_dict(item) for item in _load_db()["items"]]

    if offset:
        items = items[offset:]
    if limit is not None:
        items = items[:limit]

    return items


def get_item_by_id(item_id: str) -> Optional[Item]:
    """Return one item by ID, or None when it does not exist."""
    db = _load_db()
    index = _find_item_index(db["items"], item_id)
    if index is None:
        return None
    return Item.from_dict(db["items"][index])


def update_item(
    item_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> Optional[Item]:
    """Update an existing item."""
    db = _load_db()
    index = _find_item_index(db["items"], item_id)
    if index is None:
        return None

    item = Item.from_dict(db["items"][index])
    new_name = item.name if name is None else name.strip()
    new_description = item.description if description is None else description.strip()

    errors = validate_item_data({"name": new_name, "description": new_description})
    if errors:
        raise ValueError("; ".join(errors))

    item.name = new_name
    item.description = new_description
    item.updated_at = datetime.now(timezone.utc).isoformat()

    db["items"][index] = item.to_dict()
    _save_db(db)
    return item


def delete_item(item_id: str) -> bool:
    """Delete an item by ID."""
    db = _load_db()
    index = _find_item_index(db["items"], item_id)
    if index is None:
        return False

    del db["items"][index]
    _save_db(db)
    return True
