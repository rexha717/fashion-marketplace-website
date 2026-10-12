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

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        "OPTIONS": {"timeout": 20},
    }
}
```

`timeout` is set to 20 seconds. SQLite locks the whole file on write, and
`runserver` handles each request in its own thread. Under the default 5-second
timeout, two overlapping writes raise `database is locked`. Raising the timeout
makes the second writer wait for the first instead of failing.

Tables in use:

| Table | Purpose |
|---|---|
| `auth_user` | accounts, PBKDF2-hashed passwords (Django's default hasher) |
| `authtoken_token` | one API token per user, issued on signup/signin |
| `django_session` | server-side sessions |
| `django_migrations` | schema history |

### Sessions

Sessions live in the **`django_session` table**, not in cookies. The earlier
`SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"` setting is
gone — it was only there because the project once had no database, and it pushed
the entire session into a client-side cookie.

The API token is the durable credential for the React client, which stores it in
`localStorage`. The session cookie additionally keeps `/admin/` and the
server-rendered views working in the same browser.

### Passwords

Django hashes with PBKDF2-SHA256 at sign up:

```
pbkdf2_sha256$1500000$<salt>$<hash>
```

`User.objects.create_user()` hashes for you. Never use `User.objects.create()`
for a signup path — that stores an unusable raw password.

### The old JSON layer

`accounts/json_db.py` and `data/db.json` were removed. That module was never
imported by any view, and user records had already lived in `auth_user` in
SQLite.

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

## URL routing

`config/urls.py` defines the account routes inline and mounts the API under
`/api/auth/`:

```python
path("accounts/signup/", auth_screen, {"screen": "signup"}, name="signup"),
path("accounts/signin/", auth_screen, {"screen": "signin"}, name="signin"),
path("accounts/logout/", auth_screen, {"screen": "logout"}, name="logout"),
path("api/auth/", include("accounts.api_urls")),
```

An earlier revision wrapped these in `include(([...], "accounts"))`, which put
the names in an `accounts` namespace and made the bare names unreversible.

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

`static/auth/` is git-ignored and rebuilt with `npm run build`. For frontend
work, `npm run dev` serves on port 5173 and proxies `/api` to Django on 8000.

## Future

- Add a `marketplace` app for listings (sell/buy clothes) — see
  [ROADMAP.md](ROADMAP.md).
- Swap SQLite for PostgreSQL when the schema grows or you deploy. The code only
  goes through the ORM, so no view changes are needed.