# Frontend — auth screens

React 19 + Vite 8 bundle for the sign in / sign up / sign out screens. The
landing page stays server-rendered by Django.

## Commands

```bash
npm install
npm run dev     # dev server on :5173, proxies /api to Django on :8000
npm run build   # emits ../static/auth/auth.js + auth.css
npm run lint
```

`npm run build` is required before `python manage.py runserver` can serve the
screens — Django mounts the built bundle from `static/auth/`.

## Layout

| File              | Purpose                                                |
| ----------------- | ------------------------------------------------------ |
| `src/App.jsx`     | Reads `data-screen` off `#root` and picks a screen      |
| `src/Signin.jsx`  | Sign in form                                            |
| `src/Signup.jsx`  | Sign up form                                            |
| `src/Logout.jsx`  | Calls the logout endpoint, then clears the token        |
| `src/api.js`      | `fetch` client, token storage, error normalisation      |
| `src/components.jsx` | Shared `Brand`, `Field`, `Alert` components          |
| `src/index.css`   | VELLURÉ brand tokens (`--ink`, `--bone`, `--gold`)      |

## Dev preview

Vite serves `index.html` directly, so you can preview a screen without Django
routing:

```
http://localhost:5173/?screen=signin
http://localhost:5173/?screen=signup
http://localhost:5173/?screen=logout
```

See the root [README](../README.md) for the API contract.
