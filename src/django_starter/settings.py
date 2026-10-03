"""
Django settings for django_starter project.

All environment-specific values come from `.env` (see `.env.dist`).
For the full list of settings and their values, see
https://docs.djangoproject.com/en/6.1/ref/settings/
"""

from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

from django_starter.env import env


BASE_DIR = Path(__file__).resolve().parent.parent
env.read_env(BASE_DIR / ".env")

# Secure by default: DEBUG must be switched on explicitly (local dev only).
DEBUG = env.bool("DEBUG", default=False)
# Empty by default, so with DEBUG off Django rejects every host until you
# list yours in .env (comma separated).
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

# A real key is mandatory unless DEBUG is on. The dev key below is only ever
# used for local development and must never protect a real deployment.
_DEV_SECRET_KEY = "django-insecure-dev-only-key-not-for-production"
SECRET_KEY = env("SECRET_KEY", default="")
if not SECRET_KEY or SECRET_KEY.startswith("[["):
    if not DEBUG:
        raise ImproperlyConfigured(
            "SECRET_KEY is missing or still the placeholder. Set a strong "
            "SECRET_KEY in .env (or set DEBUG=True for local development)."
        )
    SECRET_KEY = _DEV_SECRET_KEY

# Login & Logout URLs (URL names or paths both work)
LOGIN_URL = env("LOGIN_URL", default="accounts:login")
LOGIN_REDIRECT_URL = env("LOGIN_REDIRECT_URL", default="/")
LOGOUT_REDIRECT_URL = env("LOGOUT_REDIRECT_URL", default="accounts:login")

# Session -- with SAVE_EVERY_REQUEST this is an idle timeout, in seconds.
SESSION_COOKIE_AGE = env.int("SESSION_COOKIE_AGE", default=60 * 25)  # 25 minutes
SESSION_SAVE_EVERY_REQUEST = env.bool("SESSION_SAVE_EVERY_REQUEST", default=True)
SESSION_EXPIRE_AT_BROWSER_CLOSE = env.bool(
    "SESSION_EXPIRE_AT_BROWSER_CLOSE", default=True
)
AUTH_USER_MODEL = "accounts.BaseUser"

# HTTPS hardening: on whenever DEBUG is off, each individually overridable.
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=not DEBUG)
SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=not DEBUG)
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=not DEBUG)
# Start low; raise (e.g. to a year) once you're sure HTTPS works everywhere.
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=0 if DEBUG else 3600)
# Only enable behind a reverse proxy that sets X-Forwarded-Proto and strips
# it from client requests; otherwise SECURE_SSL_REDIRECT would loop.
if env.bool("BEHIND_PROXY", default=False):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

LOCAL_APPS = [
    "accounts.apps.AccountsConfig",
]

VENDORS = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    *VENDORS,
    *LOCAL_APPS,
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "django_starter.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "django_starter.wsgi.application"


# Database
# https://docs.djangoproject.com/en/6.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / env("DATABASE_NAME", default="db.sqlite3"),
    }
}

# Pinned explicitly so migrations can't drift if Django's default changes.
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Password validation
# https://docs.djangoproject.com/en/6.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/6.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.1/howto/static-files/

STATIC_URL = "static/"

STATICFILES_DIRS = [BASE_DIR / "sitestatic"]  # source files

STATIC_ROOT = BASE_DIR / "assets"  # collectstatic output

# Email
# https://docs.djangoproject.com/en/6.1/topics/email/#topic-email-configuration

EMAIL_BACKEND = env(
    "EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)
