# Architecture

## Overview

Django is the single backend. It serves the pre-rendered landing page and a JSON
API; a React bundle mounted into `templates/auth.html` renders the auth screens
and talks to that API.

```
                    ┌──────────────────────────────┐
  Browser ────────► │  Django                      │
   /                │   /                → landing  │
   /accounts/signin │   /accounts/signin → auth.html + React bundle
   /accounts/signup │   /accounts/signup → auth.html + React bundle
   /accounts/logout │   /accounts/logout → auth.html + React bundle
   /api/auth/*      │   JSON API (DRF)
                    │       │
                    │   SQLite (db.sqlite3)
                    └──────────────────────────────┘
```

## Data storage

Persistence is **SQLite through the Django ORM** — `db.sqlite3`, configured in
`config/settings.py`. There is no JSON file backend.

> Earlier revisions of this doc claimed users were stored in `data/db.json` via
> `accounts/json_db.py`. That module was never imported by any view and no
> `data/` directory exists, so it has been removed. User records have always
> lived in `auth_user` in SQLite.

Tables in use:

- `auth_user` — accounts, with PBKDF2-hashed passwords (Django's default hasher)
- `authtoken_token` — one API token per user, issued on signup/signin
- `django_migrations` — schema history

Sessions are stored in **signed cookies** (`SESSION_ENGINE =
django.contrib.sessions.backends.signed_cookies`), so there is no session table.
The API token is the durable credential; the cookie keeps `/admin/` and the
server-rendered views working in the same browser.

## Auth flow

`accounts/api.py`:

1. **signup** — `SignupSerializer` validates the username is free, the passwords
   match, and the password passes `AUTH_PASSWORD_VALIDATORS`. The user is created
   with `create_user` (hashes the password), a session is started, and an
   `authtoken` row is issued.
2. **signin** — `authenticate()` verifies the credentials, then a session is
   started and a token issued.
3. **logout** — deletes the `authtoken` row (so the token is rejected afterwards)
   and flushes the session.
4. **me** — returns the current user for a valid `Authorization: Token <key>`.

`accounts/views.py` held the original server-rendered form views. Those pages
were superseded by the React screens, so the view and its two templates
(`templates/signin.html`, `templates/signup.html`) have been removed. The API is
the only active auth path.

## Apps

- `accounts` — auth API, serializers, and page shells

## Frontend

`frontend/` is a Vite + React app that builds to `static/auth/`:

- `App.jsx` reads `data-screen` off `#root` (set by `templates/auth.html`) to pick
  a screen, so a single bundle serves every auth route with no client router.
- `api.js` wraps `fetch`, attaches the token header, and flattens DRF's error
  payloads into `{ field: [messages] }` so screens can render them uniformly.
- `index.css` defines the brand tokens (`--ink`, `--bone`, `--gold`, `--veil`)
  extracted from the landing page stylesheet.

Django serves the built bundle from the same origin, so the API needs no CORS
configuration.

## Future

- Add a `marketplace` app for listings (sell/buy clothes)
- Swap SQLite for PostgreSQL when the schema grows
