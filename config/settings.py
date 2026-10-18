from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "")
DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() in {"true", "1", "yes"}
ALLOWED_HOSTS = [host.strip() for host in os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",") if host.strip()]
if not DEBUG:
    required = {"DJANGO_SECRET_KEY": SECRET_KEY, "DJANGO_ALLOWED_HOSTS": ALLOWED_HOSTS, "DB_NAME": os.getenv("DB_NAME"), "DB_USER": os.getenv("DB_USER"), "DB_PASSWORD": os.getenv("DB_PASSWORD"), "DB_HOST": os.getenv("DB_HOST"), "DB_PORT": os.getenv("DB_PORT")}
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise RuntimeError("Missing production configuration: " + ", ".join(missing))
if not SECRET_KEY:
    SECRET_KEY = "unsafe-development-key-set-DJANGO_SECRET_KEY"

INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "rest_framework", "rest_framework_simplejwt.token_blacklist",
    "accounts", "patients", "doctors", "mappings",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware", "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware", "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware", "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "config.urls"
TEMPLATES = [{"BACKEND":"django.template.backends.django.DjangoTemplates","DIRS":[],"APP_DIRS":True,"OPTIONS":{"context_processors":["django.template.context_processors.request","django.contrib.auth.context_processors.auth","django.contrib.messages.context_processors.messages"]}}]
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"
DATABASES = {"default": {"ENGINE":"django.db.backends.postgresql","NAME":os.getenv("DB_NAME","healthcare_db"),"USER":os.getenv("DB_USER","postgres"),"PASSWORD":os.getenv("DB_PASSWORD",""),"HOST":os.getenv("DB_HOST","localhost"),"PORT":os.getenv("DB_PORT","5432"),"CONN_MAX_AGE":60}}
AUTH_USER_MODEL = "accounts.User"
AUTH_PASSWORD_VALIDATORS = [
 {"NAME":"django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
 {"NAME":"django.contrib.auth.password_validation.MinimumLengthValidator"},
 {"NAME":"django.contrib.auth.password_validation.CommonPasswordValidator"},
 {"NAME":"django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LANGUAGE_CODE="en-us"
TIME_ZONE="UTC"
USE_I18N=True
USE_TZ=True
STATIC_URL="static/"
DEFAULT_AUTO_FIELD="django.db.models.BigAutoField"
REST_FRAMEWORK = {
 "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework_simplejwt.authentication.JWTAuthentication"],
 "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
 "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
 "PAGE_SIZE": 20,
 "DEFAULT_THROTTLE_CLASSES": ["rest_framework.throttling.AnonRateThrottle", "rest_framework.throttling.UserRateThrottle"],
 "DEFAULT_THROTTLE_RATES": {"anon":"100/hour", "user":"1000/hour"},
}
from datetime import timedelta
SIMPLE_JWT = {"ACCESS_TOKEN_LIFETIME":timedelta(minutes=15),"REFRESH_TOKEN_LIFETIME":timedelta(days=1),"ROTATE_REFRESH_TOKENS":True,"BLACKLIST_AFTER_ROTATION":True,"AUTH_HEADER_TYPES":("Bearer",)}
if not DEBUG:
    SECURE_CONTENT_TYPE_NOSNIFF=True
    SESSION_COOKIE_SECURE=True
    CSRF_COOKIE_SECURE=True
    SECURE_SSL_REDIRECT=True
