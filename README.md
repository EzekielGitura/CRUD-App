# Simple CRUD Application

A small Python CRUD project with two entry points:

- A command-line app for local use
- A Vercel-compatible serverless API

Local development can use a JSON file. Vercel deployments can use MongoDB Atlas through `MONGODB_URI` or `CRUD_MONGODB_URI`.

## What It Does

- Creates, reads, updates, and deletes items
- Stores local data in `data/db.json`
- Uses MongoDB Atlas when a database connection string is configured
- Exposes REST-style item routes under `/api`
- Includes unit tests for the CRUD and utility functions

Each item has:

- `id`
- `name`
- `description`
- `created_at`
- `updated_at`

## Project Structure

```text
crud-app/
|-- api/
|   `-- index.py      # Vercel Python serverless function
|-- app/
|   |-- __init__.py
|   |-- main.py       # CLI entry point
|   |-- models.py     # Item model
|   |-- crud.py       # JSON/MongoDB-backed CRUD functions
|   `-- utils.py      # Validation, formatting, and search helpers
|-- data/
|   `-- db.json       # Local JSON data store
|-- public/
|   `-- favicon.jpg   # Browser favicon served through /favicon.ico
|-- tests/
|   |-- test_crud.py
|   `-- test_utils.py
|-- vercel.json
|-- requirements.txt # Python deploy dependency for MongoDB
`-- README.md
```

## Local Setup

Install dependencies:

```powershell
pip install -r requirements.txt
```

Run the tests:

```powershell
python -m unittest discover tests
```

## CLI Usage

Create an item:

```powershell
python -m app.main create --name "Item Name" --description "Item Description"
```

List all items:

```powershell
python -m app.main list
```

Get an item by ID:

```powershell
python -m app.main get --id "item-id"
```

Update an item:

```powershell
python -m app.main update --id "item-id" --name "New Name" --description "New Description"
```

Delete an item:

```powershell
python -m app.main delete --id "item-id"
```

## API Routes

When deployed to Vercel, `/` returns a small API overview and the CRUD API is available under `/api`.

```text
GET    /api
GET    /api/items
POST   /api/items
GET    /api/items/{id}
PUT    /api/items/{id}
PATCH  /api/items/{id}
DELETE /api/items/{id}
```

Example create request:

```powershell
curl -X POST https://your-project.vercel.app/api/items `
  -H "Content-Type: application/json" `
  -d "{\"name\":\"Item Name\",\"description\":\"Item Description\"}"
```

## Vercel Deployment

This project is prepared for Vercel with:

- `api/index.py` for the Python serverless function
- `vercel.json` for API rewrites
- `.vercelignore` to keep local-only files out of deployments
- MongoDB Atlas connection string support for persistent storage

Deploy with the Vercel CLI:

```powershell
npm install -g vercel
vercel
```

Or import the GitHub repository from the Vercel dashboard.

## Storage Note

Local CLI usage writes to `data/db.json`.

For durable Vercel data, connect MongoDB Atlas and make sure Vercel has one of these environment variables:

```text
MONGODB_URI
CRUD_MONGODB_URI
```

Recommended setup:

1. Open the project in Vercel.
2. Go to Storage or Marketplace.
3. Add MongoDB Atlas.
4. Leave the custom prefix empty if this is your only MongoDB resource.
5. If you use a custom prefix, use `CRUD` in the dashboard or `CRUD_` with the Vercel CLI.
6. Confirm Vercel has `MONGODB_URI` or `CRUD_MONGODB_URI`.
7. Redeploy the project.

After redeploying, `/api` should report:

```json
{
  "storage": {
    "backend": "mongodb",
    "persistent": true
  }
}
```

Without one of those environment variables, Vercel falls back to temporary JSON storage. That is fine for a smoke test, but not for long-lived CRUD data.

You can override the JSON file path locally with:

```powershell
$env:CRUD_DB_PATH="C:\path\to\db.json"
```
