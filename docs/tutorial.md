# Tutorial: Setting Up Django and Connecting the Front-End to the Back-End

This tutorial takes you from zero to a working sign up / sign in flow.
The simple HTML pages are already in `templates/signup.html` and `templates/signin.html`.

---

## Part 1 — Install Django

### 1. Create a virtual environment (one time)
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows (PowerShell: .venv\Scripts\Activate.ps1)
```
You should see `(.venv)` at the start of your terminal line.

### 2. Install Django
```bash
pip install django
pip freeze > requirements.txt   # save versions
```

---

## Part 2 — Create the Django project

### 3. Create the project files
```bash
django-admin startproject config .
```
> The trailing `.` is important — it creates the project in the current folder instead of a nested one.

You now have:
```
config/        <- settings, urls, wsgi (the "project")
manage.py      <- command-line tool
```

### 4. Create the accounts app
```bash
python manage.py startapp accounts
```
An "app" is a module of your website. `accounts` will handle sign up / sign in.

### 5. Register the app + templates folder
Open `config/settings.py` and edit:

```python
INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "accounts",              # <- add this
]

TEMPLATES = [
    {
        ...
        "DIRS": [BASE_DIR / "templates"],   # <- add this so Django finds your HTML
        ...
    },
]
```

Since we are **not** using a database, also set:
```python
DATABASES = {}   # no SQL database
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"  # sessions without DB
```

---

## Part 3 — Connect the front-end to the back-end

The HTML forms already "talk" to Django through two things:

| HTML attribute | Example | Meaning for Django |
|---|---|---|
| `action` | `/accounts/signup/` | Which **URL** receives the form |
| `name` | `name="username"` | The **key** in `request.POST` |
| `method` | `post` | Data sent as `request.POST` (needs `{% csrf_token %}` in Django templates) |

### 6. Create the URL routes — `accounts/urls.py` (new file)
```python
from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("signin/", views.signin, name="signin"),
]
```

### 7. Include those routes — `config/urls.py`
```python
from django.urls import path, include

urlpatterns = [
    path("accounts/", include("accounts.urls")),
]
```
Now `/accounts/signup/` works — exactly what the HTML `action` points at.

### 8. Write the views — `accounts/views.py`
```python
from django.shortcuts import render, redirect

def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")   # matches name="username" in HTML
        email = request.POST.get("email")
        password = request.POST.get("password")
        # TODO: validate + save to JSON file
        return redirect("signin")
    return render(request, "signup.html")          # shows the HTML page on GET

def signin(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        # TODO: check user in JSON file, then: request.session["user_id"] = ...
        return redirect("/")
    return render(request, "signin.html")
```

**How the flow works:**
1. Browser `GET /accounts/signup/` → `signup()` runs → `render(...)` sends your HTML page.
2. User fills the form and submits → browser `POST /accounts/signup/` → same view runs,
   `request.method == "POST"` is True → read `request.POST["username"]` etc.
3. After processing, `redirect(...)` sends the user elsewhere.

### 9. Storing users in a JSON file
Create `accounts/json_db.py` that loads/saves `data/db.json` using Python's built-in `json` module:
```python
import json
from pathlib import Path

DB = Path("data/db.json")

def load():
    return json.loads(DB.read_text()) if DB.exists() else {"users": []}

def save(data):
    DB.parent.mkdir(exist_ok=True)
    DB.write_text(json.dumps(data, indent=2))
```
Hash passwords with Django helpers — never store plain text:
```python
from django.contrib.auth.hashers import make_password, check_password
make_password("secret123")   # when saving
check_password("secret123", stored_hash)  # when signing in  -> True/False
```

---

## Part 4 — Run it

### 10. Start the server
```bash
python manage.py runserver
```
(No `migrate` needed — there's no database.)

### 11. Test
- http://127.0.0.1:8000/accounts/signup/ → sign up page
- http://127.0.0.1:8000/accounts/signin/ → sign in page
- Submit a form → watch the terminal log the POST request

---

## Quick recap of the front ↔ back contract
```
HTML form  --action URL-->  urls.py  --path match-->  views.py
                                                        request.POST["name attr"]
                                                        return render(...) or redirect(...)
```
