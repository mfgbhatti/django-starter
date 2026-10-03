# Django Starter

A small, opinionated Django project to start new apps from. No CSS framework, two dependencies (`django`, `django-environ`), and a custom user that logs in with an email address.

## What's included

- **`BaseUser`**: Django's `AbstractUser` with a unique, lowercase `email` used as the login (`USERNAME_FIELD`). `username` and every other stock field is kept, and `createsuperuser` asks for both email and username.
- **`accounts` app**: login and logout views, an email login form (with a distinct "deactivated account" message), admin wired to `BaseUser`, and tests.
- **Settings from `.env`** (see `src/.env.dist`): secure by default. `DEBUG` is off, a real `SECRET_KEY` is required, and HTTPS hardening switches on whenever `DEBUG` is off.
- **Plain CSS** in `src/sitestatic/css/app.css`, plus `403`/`404`/`500` pages.
- **GitHub Actions**: tests on push and pull request, and a release on `v*` tags.

## Project layout

```
.
├── clean.sh               # rename the starter to your project (run once)
├── pyproject.toml
├── uv.lock
└── src/
    ├── manage.py
    ├── .env.dist          # copy to .env
    ├── django_starter/    # project config: settings, urls, wsgi/asgi, home view
    ├── accounts/          # BaseUser, login/logout, admin, tests
    ├── templates/         # base.html, home.html, error pages
    └── sitestatic/        # your CSS/JS (collectstatic writes to assets/)
```

## Getting started

1. Make it yours (once):
   ```sh
   ./clean.sh
   ```
   It asks for a project name, replaces `django-starter` / `django_starter` everywhere, renames `src/django_starter/`, and can create a local `.env` for you.

2. Install, migrate, run (Python 3.14+ and [uv](https://docs.astral.sh/uv/)):
   ```sh
   uv sync
   uv run python src/manage.py migrate
   uv run python src/manage.py createsuperuser
   uv run python src/manage.py runserver
   ```
   If you skipped the `.env` step: `cp src/.env.dist src/.env`, set `DEBUG=True` and a `SECRET_KEY`.

3. Run the tests from `src/` (Django's test discovery starts in the current directory):
   ```sh
   cd src && uv run python manage.py test
   ```

## Adding your own apps

Create the app, add it to `LOCAL_APPS` in `settings.py`, and include its URLs in the project `urls.py`. Keep `AUTH_USER_MODEL = "accounts.BaseUser"` from the first migration. Switching to a custom user later is painful.
