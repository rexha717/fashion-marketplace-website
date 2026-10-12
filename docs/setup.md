# Setup Guide

## Requirements

- Python 3.14+
- Node.js 20+

## Steps

### 1. Backend

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux / macOS

pip install -r requirements.txt
python manage.py migrate
```

`migrate` creates `db.sqlite3` with the tables for users, API tokens, and
sessions. It is git-ignored and recreated from scratch whenever it is deleted.

**`migrate` is required.** Signup fails with `no such table: auth_user` without
it, and the auth screens will render but every submit will error.

### 2. Frontend

```bash
cd frontend
npm install
npm run build
```

The build writes `static/auth/auth.js` and `static/auth/auth.css`, which
`templates/auth.html` loads. Re-run this step after any frontend change —
`static/auth/` is git-ignored, so a fresh clone has no bundle and the auth
screens will show a blank page.

### 3. Run

```bash
python manage.py runserver
```

Then open <http://127.0.0.1:8000/>.

| Page | URL |
|---|---|
| Landing | <http://127.0.0.1:8000/> |
| Sign up | <http://127.0.0.1:8000/accounts/signup/> |
| Sign in | <http://127.0.0.1:8000/accounts/signin/> |
| Sign out | <http://127.0.0.1:8000/accounts/logout/> |
| Admin | <http://127.0.0.1:8000/admin/> |

The admin site needs a user:
```bash
python manage.py createsuperuser
```

## Frontend hot reload

```bash
# terminal 1
python manage.py runserver

# terminal 2
cd frontend
npm run dev
```

Vite runs on <http://localhost:5173> and proxies `/api` to Django. Append
`?screen=signup` (or `signin` / `logout`) to preview a screen.

## Tests

```bash
python manage.py test accounts
```

Tests run against a throwaway database, so they never touch your `db.sqlite3`.

Inspect the real data by hand:
```bash
python manage.py dbshell
sqlite> select username, email from auth_user;
sqlite> select user_id, created from authtoken_token;
```

## Adding your own model

Migrations are required for any new table:
```bash
python manage.py makemigrations
python manage.py migrate
```

## Resetting the database

Stop the server first, then delete the file:
```bash
rm db.sqlite3
python manage.py migrate
```

This drops all users, tokens, and sessions. API tokens live in the database, so
deleting it invalidates every issued token and every browser signed in with one.

## Production checklist

- Set `DJANGO_SECRET_KEY` to a real secret
- Set `DJANGO_DEBUG=0`
- Set `DJANGO_ALLOWED_HOSTS` to your real hostnames
- Run `python manage.py collectstatic --noinput`
- Serve `STATIC_ROOT` (`staticfiles/`) from your web server
- Serve over HTTPS so the session cookie can be marked secure
- Run `python manage.py check --deploy` until it reports no warnings
- **SQLite does not survive a normal deploy** — see [ROADMAP.md](ROADMAP.md) M6