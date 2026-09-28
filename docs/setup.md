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

`migrate` creates `db.sqlite3`. It is git-ignored and recreated from scratch
whenever it is deleted.

### 2. Frontend

```bash
cd frontend
npm install
npm run build
```

The build writes `static/auth/auth.js` and `static/auth/auth.css`, which
`templates/auth.html` loads. Re-run this step after any frontend change.

### 3. Run

```bash
python manage.py runserver
```

Then open <http://127.0.0.1:8000/>.

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

## Production checklist

- Set `DJANGO_SECRET_KEY` to a real secret
- Set `DJANGO_DEBUG=0`
- Set `DJANGO_ALLOWED_HOSTS` to your real hostnames
- Run `python manage.py collectstatic --noinput`
- Serve `STATIC_ROOT` (`staticfiles/`) from your web server
- Serve over HTTPS so the session cookie can be marked secure
