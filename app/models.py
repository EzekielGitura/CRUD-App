from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional


@dataclass
class Item:
    """A single item managed by the CRUD app."""

    id: str
    name: str
    description: str
    created_at: str
    updated_at: Optional[str] = None

    @classmethod
    def create(cls, item_id: str, name: str, description: str) -> "Item":
        return cls(
            id=item_id,
            name=name,
            description=description,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Item":
        return cls(
            id=str(data["id"]),
            name=data["name"],
            description=data["description"],
            created_at=data["created_at"],
            updated_at=data.get("updated_at"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
