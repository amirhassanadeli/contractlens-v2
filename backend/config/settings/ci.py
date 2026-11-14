from .base import *


# Test settings only. Never use this module in production.
SECRET_KEY = "contractlens-ci-only-not-for-production"

DEBUG = False

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "testserver",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Faster password hashing for automated tests only.
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
