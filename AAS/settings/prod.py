from .base import *

DEBUG = False
SECRET_KEY = config("SECRET_KEY")
ALLOWED_HOSTS = [
    "automatedassessmentsystem.com",
]
# Email address that will send
DEFAULT_FROM_EMAIL = "admin@automatedassessmentsystem.com"
SERVER_EMAIL = DEFAULT_FROM_EMAIL
SITE_URL = "http://automatedassessmentsystem.com"
# Where we store static assets.
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# Run every 5 minutes this method.
INSTALLED_APPS.append("django_crontab")
CRONJOBS = [("*/5 * * * *", "AAS.automatedassessmentsystem.cron.grader")]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": config("DATABASE_NAME"),
        "USER": config("DATABASE_USER"),
        "PASSWORD": config("DATABASE_PASSWORD"),
        "HOST": config("DATABASE_HOST"),
        "PORT": config("DATABASE_PORT"),
    }
}


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST")
EMAIL_PORT = 587
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True
