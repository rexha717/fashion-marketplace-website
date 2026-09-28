# Tutorial: How the Auth Flow Works

This walks through the current architecture: a Django JSON API plus a React
(Vite) bundle for the sign in / sign up screens.

> This document used to describe a JSON-file database (`data/db.json`) and told
> you to set `DATABASES = {}`. That setting **breaks the app**: the auth views
> query `User.objects`, which needs a real database, so every sign up and sign in
> returned HTTP 500. The JSON backend was never wired up and has been removed.

---

## Part 1 — Backend setup

### 1. Virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows (PowerShell: .venv\Scripts\Activate.ps1)
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure the database

`config/settings.py` must define a real database, because `accounts` uses
Django's built-in `User` model:
```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
```

Sessions use signed cookies, so they need no table — but that does **not** mean
the user table can be removed:
```python
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
```

### 4. Install the API apps
```python
INSTALLED_APPS = [
    ...,
    "rest_framework",
    "rest_framework.authtoken",
    "accounts",
]
```

### 5. Create the tables
```bash
python manage.py migrate
```
Without this, `authtoken_token` does not exist and the API cannot issue tokens.

---

## Part 2 — The JSON API

### 6. Serializers — `accounts/serializers.py`

Serializers turn JSON into validated data. `SignupSerializer` runs three checks
in order:
```python
def validate_username(self, value):        # free username
def validate(self, attrs):                 # passwords match
    if attrs["password"] != attrs["confirm_password"]:
        raise serializers.ValidationError({"confirm_password": [...]})
    validate_password(attrs["password"])   # Django's password rules
```

`create()` then uses `User.objects.create_user`, which **hashes** the password —
plaintext is never stored.

### 7. Views — `accounts/api.py`

Each view is a thin wrapper:
```python
class SigninView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SigninSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)   # -> 400 with field errors
        user = serializer.validated_data["user"]
        django_login(request, user)                 # session cookie
        return Response(_token_payload(user))       # -> 200 {token, user}
```

`raise_exception=True` is what produces the `400` responses the React screens
render inline.

### 8. Routes — `accounts/api_urls.py`, included in `config/urls.py`
```python
path("api/auth/", include("accounts.api_urls")),
```

---

## Part 3 — The React screens

### 9. Create the Vite app
```bash
cd frontend
npm install
```

### 10. One bundle, many routes

`templates/auth.html` renders a mount point describing which screen to show:
```html
<div id="root" data-screen="{{ screen }}"></div>
<script type="module" src="{% static 'auth/auth.js' %}" defer></script>
```

`App.jsx` reads that attribute and picks the component, so a single bundle serves
every auth route without a client-side router:
```jsx
const screen = document.getElementById('root')?.dataset.screen ?? 'signin'
```

### 11. Talking to the API — `src/api.js`

```jsx
const response = await fetch('/api/auth/signin/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', Authorization: `Token ${token}` },
  body: JSON.stringify({ username, password }),
})
```

DRF returns errors as `{"field": ["message"]}`. `normalizeErrors()` flattens that
into the same shape plus a `nonFieldErrors` bucket, so every screen renders
errors with one `<Alert errors={errors} />` component.

### 12. Build into Django
`vite.config.js` writes to `../static/auth` with fixed filenames so the template
can reference `auth.js` and `auth.css` directly:
```bash
npm run build
```

Django serves the bundle from the same origin, so no CORS setup is needed.

---

## Part 4 — Run and test

```bash
python manage.py runserver
```
- http://127.0.0.1:8000/ — landing page
- http://127.0.0.1:8000/accounts/signup/ — create an account
- http://127.0.0.1:8000/accounts/signin/ — sign in

Run the test suite:
```bash
python manage.py test accounts
```

---

## The front ↔ back contract

```
React screen ──fetch JSON──► DRF view ──► serializer ──► User model ──► SQLite
      ▲                                                                │
      └────────── {token, user}  or  400 {field: [messages]} ◄──────────┘
```
