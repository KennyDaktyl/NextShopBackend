import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get("SECRET_KEY")

if os.environ.get("ENVIRONMENT") == "local":
    DEBUG = True
    ALLOWED_HOSTS = []
else:
    DEBUG = False
    ALLOWED_HOSTS = ["serwiswrybnej.pl"]


INSTALLED_APPS = [
    "web.apps.WebConfig",
    "account", 
    "django.contrib.sites",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
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

ROOT_URLCONF = "serwiswrybnej.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "serwiswrybnej.wsgi.application"

DATABASES = {
    "default": {
        "NAME": os.environ.get("POSTGRES_DB"),
        "ENGINE": "django.db.backends.postgresql",
        "USER": os.environ.get("DB_USER"),
        "PASSWORD": os.environ.get("DB_PASSWORD"),
        "HOST": os.environ.get("DB_HOST"),
        "PORT": "5432",
    },
}

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

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
STATICFILES_DIRS = (os.path.join(SITE_ROOT, "static/"),)

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media/")

TIME_ZONE = "Europe/Warsaw"
TIME_FORMAT = "%H:%M"
USE_I18N = True
USE_TZ = False
DATETIME_FORMAT = "Y-m-d H:M"
DATE_INPUT_FORMATS = "Y-m-d H:M:S"

LANGUAGE_CODE = "pl"
LANGUAGES = [
    ("pl", "Polski"),
    ("en", "English"),
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

EMAIL_USE_TLS = True
EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_HOST_USER = os.environ.get("EMAIL_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_PORT = os.environ.get("EMAIL_PORT")
SERVER_EMAIL = os.environ.get("EMAIL_HOST")
DEFAULT_FROM_EMAIL = os.environ.get("EMAIL_USER")
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
if os.environ.get("ENVIRONMENT") in ["production", "staging", "dev"]:
    EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "").lower() == "true"
    EMAIL_USE_SSL = os.environ.get("EMAIL_USE_SSL", "").lower() == "true"
