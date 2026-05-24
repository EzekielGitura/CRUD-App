import json
from http.server import BaseHTTPRequestHandler
from typing import Any, Dict, Optional
from urllib.parse import urlparse

from app import crud


def _item_to_dict(item) -> Dict[str, Any]:
    return item.to_dict()


class handler(BaseHTTPRequestHandler):
    def _send_no_content(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def _send_json(self, status: int, payload: Dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,PUT,PATCH,DELETE,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> Optional[Dict[str, Any]]:
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}

        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except json.JSONDecodeError:
            return None

        return payload if isinstance(payload, dict) else None

    def _path_parts(self):
        path = urlparse(self.path).path
        parts = [part for part in path.split("/") if part]

        if parts and parts[0] == "api":
            parts = parts[1:]
        if parts and parts[0] == "index.py":
            parts = parts[1:]

        return parts

    def do_OPTIONS(self):
        self._send_json(200, {"ok": True})

    def do_GET(self):
        parts = self._path_parts()

        if parts == ["favicon.ico"]:
            self._send_no_content()
            return

        if not parts:
            self._send_json(
                200,
                {
                    "name": "CRUD API",
                    "routes": [
                        "GET /api/items",
                        "POST /api/items",
                        "GET /api/items/{id}",
                        "PUT /api/items/{id}",
                        "PATCH /api/items/{id}",
                        "DELETE /api/items/{id}",
                    ],
                    "storage": crud.get_storage_status(),
                },
            )
            return

        if parts == ["items"]:
            items = [_item_to_dict(item) for item in crud.get_items()]
            self._send_json(200, {"items": items, "total": len(items)})
            return

        if len(parts) == 2 and parts[0] == "items":
            item = crud.get_item_by_id(parts[1])
            if item is None:
                self._send_json(404, {"error": "Item not found"})
                return

            self._send_json(200, {"item": _item_to_dict(item)})
            return

        self._send_json(404, {"error": "Route not found"})

    def do_POST(self):
        parts = self._path_parts()
        if parts != ["items"]:
            self._send_json(404, {"error": "Route not found"})
            return

        data = self._read_json()
        if data is None:
            self._send_json(400, {"error": "Request body must be a JSON object"})
            return

        try:
            item = crud.create_item(data.get("name"), data.get("description"))
        except ValueError as exc:
            self._send_json(400, {"error": str(exc)})
            return

        self._send_json(201, {"item": _item_to_dict(item)})

    def do_PUT(self):
        self._update_item()

    def do_PATCH(self):
        self._update_item()

    def _update_item(self):
        parts = self._path_parts()
        if len(parts) != 2 or parts[0] != "items":
            self._send_json(404, {"error": "Route not found"})
            return

        data = self._read_json()
        if data is None:
            self._send_json(400, {"error": "Request body must be a JSON object"})
            return

        if "name" not in data and "description" not in data:
            self._send_json(400, {"error": "Provide name, description, or both"})
            return
        if ("name" in data and data["name"] is None) or (
            "description" in data and data["description"] is None
        ):
            self._send_json(400, {"error": "Fields cannot be null"})
            return

        try:
            item = crud.update_item(
                parts[1],
                name=data.get("name"),
                description=data.get("description"),
            )
        except ValueError as exc:
            self._send_json(400, {"error": str(exc)})
            return

        if item is None:
            self._send_json(404, {"error": "Item not found"})
            return

        self._send_json(200, {"item": _item_to_dict(item)})

    def do_DELETE(self):
        parts = self._path_parts()
        if len(parts) != 2 or parts[0] != "items":
            self._send_json(404, {"error": "Route not found"})
            return

        if not crud.delete_item(parts[1]):
            self._send_json(404, {"error": "Item not found"})
            return

        self._send_json(200, {"message": "Item deleted successfully"})
