# Fashion Marketplace Website 🛍️

A buy & sell clothes website built with **Django** and a **JSON file database** (no Docker, no PostgreSQL).

## Tech Stack
- Python 3.14.7
- Django 5.x
- JSON file storage (`data/db.json`) instead of a SQL database

## Project Structure
```
fashion-marketplace-website/
├── config/            # Django project settings & urls
├── accounts/          # Sign up / Sign in / Logout app
├── templates/         # Simple HTML templates
├── static/            # CSS files
├── data/              # JSON "database" (db.json)
├── docs/              # Documentation
├── tests/             # Test files
├── manage.py
└── requirements.txt
```

## Setup (step by step)

### 1. Create a virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Linux/Mac
```

### 2. Install Django
```bash
pip install -r requirements.txt
```

### 3. Run the server
```bash
python manage.py runserver
```

### 4. Open in browser
- Home: http://127.0.0.1:8000/
- Sign up: http://127.0.0.1:8000/accounts/signup/
- Sign in: http://127.0.0.1:8000/accounts/signin/

## Documentation
See the [docs/](docs/) folder:
- [docs/setup.md](docs/setup.md) — detailed setup guide
- [docs/architecture.md](docs/architecture.md) — how the JSON database works

## Testing
```bash
python -m pytest tests/
```
