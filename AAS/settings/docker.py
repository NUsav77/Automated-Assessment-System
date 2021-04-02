# test configuration for docker compose
from .base import *


DEBUG = os.environ["DEBUG"]
SECRET_KEY = os.environ["SECRET_KEY"]
ALLOWED_HOSTS = ["0.0.0.0", "127.0.0.1"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ["DATABASE_NAME"],
        "USER": os.environ["DATABASE_USER"],
        "PASSWORD": os.environ["DATABASE_PASSWORD"],
        "HOST": os.environ["DATABASE_HOST"],
        "PORT": os.environ["DATABASE_PORT"],
    }
}


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ["EMAIL_HOST"]
EMAIL_PORT = os.environ["EMAIL_PORT"]
EMAIL_HOST_USER = os.environ["EMAIL_USER"]
EMAIL_HOST_PASSWORD = os.environ["EMAIL_PASSWORD"]
EMAIL_USE_TLS = os.environ["EMAIL_TLS"]
