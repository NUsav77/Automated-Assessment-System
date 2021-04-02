from decouple import config

from .base import *

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", cast=bool)
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# For local.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        "TEST_NAME": BASE_DIR / "db-test.sqlite3",
    }
}

# Don't tell me about my weak passwords, development is OK with it.
AUTH_PASSWORD_VALIDATORS = []


EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
# When testing use this one.
# see https://simpleisbetterthancomplex.com/questions/2017/07/07/mocking-emails.html
# EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
