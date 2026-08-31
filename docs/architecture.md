# Architecture

## JSON as the database
Since Docker/PostgreSQL was dropped, we use a simple JSON file as persistence layer:

- File: `data/db.json`
- Module: `accounts/json_db.py`
- Shape:
```json
{
  "users": [
    {
      "id": 1,
      "username": "ali",
      "email": "ali@example.com",
      "password_hash": "pbkdf2_sha256$...",
      "created_at": "2026-08-31T10:00:00"
    }
  ]
}
```

- Passwords are **never** stored in plain text — we use Django's `make_password` / `check_password`.
- `json_db.py` handles load/save with a thread lock so concurrent requests don't corrupt the file.

## Apps
- `accounts` — signup, signin, logout, simple session-based auth (Django sessions still use SQLite internally for sessions only; user records live in JSON).

## Future
- Add a `marketplace` app for listings (sell/buy clothes).
- Swap `json_db.py` for a real DB (PostgreSQL) later — views only talk to the db module, so the swap is easy.
