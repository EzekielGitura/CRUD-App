# Simple CRUD Application

A small Python CRUD project with two entry points:

- A command-line app for local use
- A Vercel-compatible serverless API

The project uses only the Python standard library.

## What It Does

- Creates, reads, updates, and deletes items
- Stores local data in `data/db.json`
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
|   |-- crud.py       # JSON-backed CRUD functions
|   `-- utils.py      # Validation, formatting, and search helpers
|-- data/
|   `-- db.json       # Local JSON data store
|-- public/
|   `-- favicon.jpg   # Browser favicon served through /favicon.ico
|-- tests/
|   |-- test_crud.py
|   `-- test_utils.py
|-- vercel.json
|-- requirements.txt
`-- README.md
```

## Local Setup

No third-party packages are required.

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
- `vercel.json` for API rewrites and function bundle exclusions
- `.vercelignore` to keep local-only files out of deployments

Deploy with the Vercel CLI:

```powershell
npm install -g vercel
vercel
```

Or import the GitHub repository from the Vercel dashboard.

## Storage Note

Local CLI usage writes to `data/db.json`.

On Vercel, the function writes to temporary storage because serverless deployments do not provide persistent writable project files. This is enough for a deployment smoke test, but production CRUD data should use a real database such as Postgres, Supabase, Neon, or another hosted store.

You can override the JSON file path locally with:

```powershell
$env:CRUD_DB_PATH="C:\path\to\db.json"
```
