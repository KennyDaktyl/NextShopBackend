import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get("SECRET_KEY")


CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3010",
    "http://127.0.0.1:3010",
    "http://51.75.64.242:3010",
    "https://new-serwiswrybnej-api.resto-app.pl",
]
CSRF_TRUSTED_ORIGINS = ["https://new-serwiswrybnej-api.resto-app.pl"]
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_HEADERS = [
    "authorization",
    "content-type",
    "x-requested-with",
    "accept",
    "origin",
    "user-agent",
    "access-control-allow-origin",
]
CORS_EXPOSE_HEADERS = [
    "Content-Type",
    "X-CSRFToken",
]
CORS_ALLOW_METHODS = [
    "GET",
    "OPTIONS",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
]

if os.environ.get("ENVIRONMENT") in ["local", "dev"]:
    DEBUG = True
    ALLOWED_HOSTS = ["*"]
    CORS_ALLOW_CREDENTIALS = True
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000", 
        "http://127.0.0.1:3000", 
        "https://23cf-91-236-86-24.ngrok-free.app"
    ]

    SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
    SESSION_COOKIE_AGE = 86400
    SESSION_COOKIE_NAME = "sessionid"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    CSRF_COOKIE_SECURE = False
else:
    DEBUG = False
    ALLOWED_HOSTS = [
        "serwiswrybnej.pl",
        "51.75.64.242",
        "new-serwiswrybnej-api.resto-app.pl",
    ]
    
    SECURE_HSTS_SECONDS = 31536000  
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True  
    SECURE_HSTS_PRELOAD = True  
    SECURE_SSL_REDIRECT = True 

    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_AGE = 86400
    SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3010",
        "http://127.0.0.1:3010",
        "http://51.75.64.242:3010",
        "https://new-serwiswrybnej-api.resto-app.pl",
    ]

    CSRF_TRUSTED_ORIGINS = ["https://new-serwiswrybnej-api.resto-app.pl"]

    CORS_ALLOW_CREDENTIALS = True

    CORS_ALLOW_HEADERS = [
        "authorization",
        "content-type",
        "x-requested-with",
        "accept",
        "origin",
        "user-agent",
        "access-control-allow-origin",
    ]

    CORS_EXPOSE_HEADERS = [
        "Content-Type",
        "X-CSRFToken",
    ]

    CORS_ALLOW_METHODS = [
        "GET",
        "OPTIONS",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
    ]

SITE_ID = 1

INSTALLED_APPS = [
    "web.apps.WebConfig",
    "rest_framework",
    "django.contrib.sites",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "drf_yasg",
    "djoser",
    "corsheaders",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
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
    EMAIL_USE_SSL = os.environ.get("EMAIL_USE_SSL", "").lower() == "false"


STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_ENDPOINT_SECRET = os.environ.get("STRIPE_ENDPOINT_SECRET")

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

AUTHENTICATION_BACKENDS = ("django.contrib.auth.backends.ModelBackend",)

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=60),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
}


DJOSER = {
    "LOGIN_FIELD": "username",
    "USER_CREATE_PASSWORD_RETYPE": True,
    "USERNAME_CHANGED_EMAIL_CONFIRMATION": True,
    "PASSWORD_CHANGED_EMAIL_CONFIRMATION": True,
    "SET_USERNAME_RETYPE": True,
    "SET_PASSWORD_RETYPE": True,
    "PASSWORD_RESET_CONFIRM_RETYPE": True,
    "PASSWORD_RESET_CONFIRM_URL": "password/reset/confirm/{uid}/{token}",
    "USERNAME_RESET_CONFIRM_URL": "email/reset/confirm/{uid}/{token}",
    "ACTIVATION_URL": "auth/{uid}/{token}",
    "ACTIVATION_EXPIRATION_DAYS": 3,
    "SEND_ACTIVATION_EMAIL": True,
    "SEND_CONFIRMATION_EMAIL": True,
    "SERIALIZERS": {
        "user_create": "web.accounts.serializers.UserSerializer",
        "user": "web.accounts.serializers.LoginSerializer",
        "current_user": "web.accounts.serializers.LoginSerializer",
        "user_delete": "djoser.serializers.UserDeleteSerializer",
    },
    "PERMISSIONS": {
        "user_create": ["rest_framework.permissions.AllowAny"],
    },
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "django.log",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "DEBUG",
    },
    "loggers": {
        # 'django': {
        #     'handlers': ['console', 'file'],
        #     'level': 'DEBUG',
        #     'propagate': True,
        # },
        "web": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
