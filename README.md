# Fashion Marketplace Website

A buy & sell fashion marketplace. **Django** serves the landing page and a
**JSON API**; the sign in / sign up screens are a **React (Vite)** app that
consumes that API.

**Status: early.** Auth is built and tested. There is no product, cart, order,
or seller code yet — see [docs/ROADMAP.md](docs/ROADMAP.md).

## Tech Stack

| Layer     | Choice                                   |
| --------- | ---------------------------------------- |
| Backend   | Python 3.14, Django 6.1, DRF 3.18        |
| Database  | SQLite (`db.sqlite3`) via the Django ORM |
| Auth API  | DRF token auth (DRF's `authtoken` app)   |
| Frontend  | React 19 + Vite 8 (auth screens only)    |
| Styling   | Plain CSS using the VELLURÉ brand tokens |

> Earlier revisions of this README described a JSON-file database
> (`data/db.json`) and a React Native frontend. Neither existed in the code:
> the app actually used the Django ORM on SQLite, and the auth pages were
> server-rendered HTML forms. This document matches the real code.

## Brand

The landing page is **VELLURÉ** — a fictional Paris atelier, est. 1974. It is a
pre-rendered React/Tailwind marketing page and doubles as the design reference:
typography (`Cormorant Garamond` + `Jost`), the `bone` / `ink` / `gold` palette,
and the `.btn-editorial` / `.eyebrow` classes.

Its nav shows a hardcoded `Cart (0)` and a newsletter form that posts nowhere —
both are placeholders for future work.

VELLURÉ is the storefront brand. The marketplace is multi-seller: anyone can
list clothes.

## Project Structure

```
fashion-marketplace-website/
├── config/            # Django project settings & urls
├── accounts/          # Auth app
│   ├── api.py         #   JSON API views (signup/signin/logout/me)
│   ├── api_urls.py    #   /api/auth/* routes
│   ├── serializers.py #   DRF serializers & password validation
│   └── tests.py       #   21 API + page tests
├── frontend/          # React + Vite auth screens
│   └── src/
│       ├── App.jsx        # picks the screen from data-screen
│       ├── Signin.jsx     # /accounts/signin/
│       ├── Signup.jsx     # /accounts/signup/
│       ├── Logout.jsx     # /accounts/logout/
│       ├── api.js         # fetch client + error normalisation
│       └── index.css      # brand tokens (ink / bone / gold)
├── templates/
│   ├── landing.html  # pre-rendered landing page (unchanged)
│   └── auth.html     # shell that mounts the React bundle
├── static/
│   ├── auth/         # Vite build output (generated, git-ignored)
│   └── landing/      # landing page assets
├── docs/
│   └── ROADMAP.md    # build plan from here to launch
├── manage.py
└── requirements.txt
```

## Setup

You need **Python 3.14+** and **Node.js 20+**.

### 1. Backend

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux / macOS

pip install -r requirements.txt
python manage.py migrate
```

`migrate` creates `db.sqlite3`. It is **required** — signup fails with
`no such table: auth_user` without it.

### 2. Frontend

```bash
cd frontend
npm install
npm run build        # emits ../static/auth/auth.js + auth.css
```

`npm run build` must be re-run whenever you change anything in `frontend/`. A
fresh clone has no bundle, so the auth screens will be blank until you do.

### 3. Run

```bash
python manage.py runserver
```

Open <http://127.0.0.1:8000/>.

| Route                   | Description                              |
| ----------------------- | ---------------------------------------- |
| `/`                     | Landing page (Django-rendered)           |
| `/accounts/signin/`     | Sign in (React)                          |
| `/accounts/signup/`     | Sign up (React)                          |
| `/accounts/logout/`     | Sign out (React)                         |
| `/admin/`               | Django admin                             |

## Frontend development (hot reload)

Run Django and Vite side by side for fast iteration:

```bash
# terminal 1
python manage.py runserver

# terminal 2
cd frontend
npm run dev
```

Vite serves <http://localhost:5173> and proxies `/api` to Django on port 8000.
Use `?screen=signin`, `?screen=signup`, or `?screen=logout` to preview a screen
without visiting Django.

## JSON API

All endpoints accept and return `application/json`. Successful auth responses
return a `token`; send it back as `Authorization: Token <key>`.

| Method | Endpoint             | Auth required | Body / result                    |
| ------ | -------------------- | ------------- | -------------------------------- |
| POST   | `/api/auth/signup/`  | No            | `{username, email, password, confirm_password}` → `201 {token, user}` |
| POST   | `/api/auth/signin/`  | No            | `{username, password}` → `200 {token, user}` |
| POST   | `/api/auth/logout/`  | No            | `204`, deletes the token         |
| GET    | `/api/auth/me/`      | Yes           | `200 {id, username, email}`      |
| POST   | `/api/auth/token/`   | No            | `{username, password}` → `{token}` (DRF built-in) |

Validation errors return `400` with per-field messages:

```json
{
  "username": ["Username already taken."],
  "confirm_password": ["Passwords do not match."]
}
```

The React client stores the token in `localStorage` under `vellure.auth.token`.
A session cookie is also set, so Django admin and the server-rendered views work
in the same browser.

## Testing

```bash
python manage.py test accounts
```

21 tests cover signup validation, password hashing, duplicate usernames, signin,
token auth, logout invalidation, and the page shells. They run against a
throwaway database, so they never touch your `db.sqlite3`.

> The previous README suggested `python -m pytest tests/`. Pytest is not a
> project dependency and there is no test suite in `tests/`; the suite lives in
> `accounts/tests.py` and runs on Django's built-in runner.

## Configuration

Read from the environment, with development defaults:

| Variable                  | Default                          | Purpose                     |
| ------------------------- | -------------------------------- | --------------------------- |
| `DJANGO_SECRET_KEY`       | insecure dev key                 | **Set this in production**  |
| `DJANGO_DEBUG`            | `1`                              | Set to `0` in production    |
| `DJANGO_ALLOWED_HOSTS`    | `localhost,127.0.0.1`            | Comma-separated             |
| `DJANGO_DEFAULT_FROM_EMAIL` | `no-reply@vellure.example`     | Outgoing sender             |

## Roadmap

Full build plan in [docs/ROADMAP.md](docs/ROADMAP.md):

| Milestone | What |
|---|---|
| M1 | Profile & seller onboarding |
| M2 | Listings & images |
| M3 | Cart & orders |
| M4 | Payments & payout ledger (highest risk) |
| M5 | Seller dashboard |
| M6 | Deploy (SQLite → Postgres) |
| M7 | Hardening before real users |

M4 carries the most risk: **Stripe and Stripe Connect are not available in
Iran**, so the payout ledger has to be built directly. See the roadmap before
starting payments.

## Documentation

- [docs/ROADMAP.md](docs/ROADMAP.md) — build plan from here to launch
- [docs/setup.md](docs/setup.md) — detailed setup guide
- [docs/architecture.md](docs/architecture.md) — request flow and data storage
- [docs/tutorial.md](docs/tutorial.md) — build walkthrough

## Notes

- Passwords are hashed with PBKDF2-SHA256 — never stored in plain text.
- `db.sqlite3` and `static/auth/` are git-ignored. Deleting the database drops
  all users **and invalidates every issued API token**.
- **SQLite is for local development only** — it will not survive a deploy.