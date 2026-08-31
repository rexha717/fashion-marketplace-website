# Setup Guide

## Requirements
- Python 3.14.7
- pip

## Steps

### 1. Virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install django
```

### 3. Run
```bash
python manage.py runserver
```

No migrations are needed — we don't use a SQL database. User data is stored in
`data/db.json`, which is created automatically on first sign up.

## Resetting the "database"
Delete `data/db.json` and the app will recreate it on the next sign up.
