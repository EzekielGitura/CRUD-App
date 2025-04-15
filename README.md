# Simple CRUD Application

A lightweight Python CRUD (Create, Read, Update, Delete) application for managing items.

## Features

- Create, read, update, and delete items
- Command-line interface
- JSON file storage
- Unit tests

## Folder Structure

```
crud-app/
│
├── app/                      # Core application logic
│   ├── __init__.py           # Makes app a package
│   ├── main.py               # Entry point to start the app
│   ├── models.py             # Data structures or ORM classes
│   ├── crud.py               # Functions for Create, Read, Update, Delete
│   └── utils.py              # Helper functions (validation, formatting)
│
├── data/                     # Data storage (JSON file)
│   └── db.json               # "Database" file
│
├── tests/                    # Unit tests
│   ├── __init__.py
│   ├── test_crud.py
│   └── test_utils.py
│
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── .gitignore                # Files to exclude from version control
└── LICENSE                   # Open-source license
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/crud-app.git
   cd crud-app
   ```

2. Set up a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Run the application:

```
python -m app.main [command] [options]
```

### Available commands:

- **Create an item**:
  ```
  python -m app.main create --name "Item Name" --description "Item Description"
  ```

- **List all items**:
  ```
  python -m app.main list
  ```

- **Get an item by ID**:
  ```
  python -m app.main get --id "item-id"
  ```

- **Update an item**:
  ```
  python -m app.main update --id "item-id" --name "New Name" --description "New Description"
  ```

- **Delete an item**:
  ```
  python -m app.main delete --id "item-id"
  ```

- **Show help**:
  ```
  python -m app.main help
  ```

## Testing

Run the tests with:

```
python -m unittest discover tests
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request