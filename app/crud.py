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
_MONGO_CLIENT = None

if os.environ.get("CRUD_DB_PATH"):
    DB_PATH = os.environ["CRUD_DB_PATH"]
elif os.environ.get("VERCEL") or os.environ.get("VERCEL_ENV"):
    DB_PATH = str(Path(tempfile.gettempdir()) / "crud-app-db.json")
else:
    DB_PATH = str(PROJECT_ROOT / "data" / "db.json")


def _mongodb_uri() -> Optional[str]:
    return os.environ.get("MONGODB_URI") or os.environ.get("CRUD_MONGODB_URI")


def get_storage_status() -> Dict[str, Any]:
    """Describe the currently selected storage backend."""
    if _mongodb_uri():
        return {
            "backend": "mongodb",
            "persistent": True,
            "source": "MONGODB_URI or CRUD_MONGODB_URI",
        }

    if os.environ.get("VERCEL") or os.environ.get("VERCEL_ENV"):
        return {
            "backend": "json-file",
            "persistent": False,
            "path": DB_PATH,
            "note": "Configure MONGODB_URI for durable MongoDB Atlas storage.",
        }

    return {
        "backend": "json-file",
        "persistent": True,
        "path": DB_PATH,
    }


def _mongo_collection():
    global _MONGO_CLIENT

    try:
        from pymongo import MongoClient
        from pymongo.errors import ConfigurationError
    except ImportError as exc:
        raise RuntimeError(
            "MongoDB storage requires pymongo. Run `pip install -r requirements.txt`."
        ) from exc

    if _MONGO_CLIENT is None:
        _MONGO_CLIENT = MongoClient(_mongodb_uri(), serverSelectionTimeoutMS=5000)

    database_name = os.environ.get("MONGODB_DATABASE") or os.environ.get(
        "CRUD_MONGODB_DATABASE"
    )
    if database_name:
        database = _MONGO_CLIENT[database_name]
    else:
        try:
            database = _MONGO_CLIENT.get_default_database()
        except ConfigurationError:
            database = _MONGO_CLIENT["crud_app"]

    collection = database["items"]
    collection.create_index("created_at")
    return collection


def _item_from_document(document: Dict[str, Any]) -> Item:
    return Item(
        id=str(document["_id"]),
        name=document["name"],
        description=document["description"],
        created_at=document["created_at"],
        updated_at=document.get("updated_at"),
    )


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

    if _mongodb_uri():
        item = Item.create(str(uuid4()), name.strip(), description.strip())
        document = item.to_dict()
        document["_id"] = document.pop("id")
        _mongo_collection().insert_one(document)
        return item

    db = _load_db()
    item = Item.create(str(uuid4()), name.strip(), description.strip())
    db["items"].append(item.to_dict())
    _save_db(db)
    return item


def get_items(limit: Optional[int] = None, offset: int = 0) -> List[Item]:
    """Return all items, optionally sliced for simple pagination."""
    if _mongodb_uri():
        cursor = _mongo_collection().find().sort("created_at", -1)
        if offset:
            cursor = cursor.skip(offset)
        if limit is not None:
            cursor = cursor.limit(limit)

        return [_item_from_document(document) for document in cursor]

    items = [Item.from_dict(item) for item in _load_db()["items"]]

    if offset:
        items = items[offset:]
    if limit is not None:
        items = items[:limit]

    return items


def get_item_by_id(item_id: str) -> Optional[Item]:
    """Return one item by ID, or None when it does not exist."""
    if _mongodb_uri():
        document = _mongo_collection().find_one({"_id": str(item_id)})
        return _item_from_document(document) if document else None

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
    if _mongodb_uri():
        from pymongo import ReturnDocument

        collection = _mongo_collection()
        document = collection.find_one({"_id": str(item_id)})
        if not document:
            return None

        new_name = document["name"] if name is None else name.strip()
        new_description = (
            document["description"] if description is None else description.strip()
        )

        errors = validate_item_data({"name": new_name, "description": new_description})
        if errors:
            raise ValueError("; ".join(errors))

        updated_document = collection.find_one_and_update(
            {"_id": str(item_id)},
            {
                "$set": {
                    "name": new_name,
                    "description": new_description,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }
            },
            return_document=ReturnDocument.AFTER,
        )

        return _item_from_document(updated_document)

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
    if _mongodb_uri():
        result = _mongo_collection().delete_one({"_id": str(item_id)})
        return result.deleted_count > 0

    db = _load_db()
    index = _find_item_index(db["items"], item_id)
    if index is None:
        return False

    del db["items"][index]
    _save_db(db)
    return True
