from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent / '.env')

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev-only-change-in-production')

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
CSRF_TRUSTED_ORIGINS = os.environ.get(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:5173,http://localhost:3000'
).split(',')

# Railway injects RAILWAY_PUBLIC_DOMAIN with the service's public hostname.
# Add it to the allowed hosts and CSRF trusted origins so the deployed app
# accepts requests to its own domain without hard-coding it here.
RAILWAY_PUBLIC_DOMAIN = os.environ.get('RAILWAY_PUBLIC_DOMAIN')
if RAILWAY_PUBLIC_DOMAIN:
    ALLOWED_HOSTS.append(RAILWAY_PUBLIC_DOMAIN)
    CSRF_TRUSTED_ORIGINS.append(f'https://{RAILWAY_PUBLIC_DOMAIN}')

# Railway's deploy healthcheck probes the container internally with
# Host: healthcheck.railway.app, which is neither localhost nor the public
# domain. Allow it so the healthcheck (and therefore the deploy) passes.
if os.environ.get('RAILWAY_ENVIRONMENT'):
    ALLOWED_HOSTS.append('healthcheck.railway.app')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'questions',
    'progress',
    'users',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'securityplus.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'securityplus.wsgi.application'

# Database: Railway provides a single DATABASE_URL connection string; local
# dev uses the discrete DB_* variables (see docker-compose.yml / .env).
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600),
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.postgresql'),
            'NAME': os.environ.get('DB_NAME', 'securityplus'),
            'USER': os.environ.get('DB_USER', 'secplus_user'),
            'PASSWORD': os.environ.get('DB_PASSWORD', 'secplus_dev_password'),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# The combined production image builds the React SPA and drops it here (see the
# root Dockerfile, which copies the Vite dist/ to /app/frontend_build). When the
# dir is present we serve its hashed assets via whitenoise under /static/ and the
# index.html via the SPA fallback view (securityplus.views.spa_index).
FRONTEND_BUILD_DIR = BASE_DIR.parent / 'frontend_build'
STATICFILES_DIRS = [FRONTEND_BUILD_DIR] if FRONTEND_BUILD_DIR.exists() else []

# Whitenoise: compress static files at collectstatic time. We intentionally do
# NOT use the *Manifest* variant — Vite already content-hashes its asset
# filenames, and manifest storage would re-hash them without rewriting the
# references inside index.html, breaking the SPA. Compression alone is safe.
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage'},
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

# CORS — allow React dev server in development
CORS_ALLOWED_ORIGINS = os.environ.get(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:5173,http://localhost:3000'
).split(',')
CORS_ALLOW_CREDENTIALS = True

# Session cookie config
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'

# Secure cookies default ON in production (DEBUG=False) and OFF in dev. They are
# env-overridable so the converged local docker-compose stack can run DEBUG=False
# while still serving cookies over plain HTTP (it sets both to 'False').
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', str(not DEBUG)) == 'True'
CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', str(not DEBUG)) == 'True'

# Railway terminates TLS at its edge proxy and forwards plain HTTP with an
# X-Forwarded-Proto header. Trust it so Django knows the original request was
# HTTPS (required for secure cookies and correct scheme detection).
#
# Only trust this header when actually running behind that proxy. If we trusted
# it unconditionally, a client hitting the app directly could spoof
# X-Forwarded-Proto: https and defeat scheme detection. Gate on the Railway
# environment marker (or an explicit opt-in for other reverse proxies). (BE-16)
TRUST_PROXY_SSL_HEADER = bool(os.environ.get('RAILWAY_ENVIRONMENT')) or \
    os.environ.get('TRUST_PROXY_SSL_HEADER') == 'True'
if TRUST_PROXY_SSL_HEADER:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Fail fast rather than silently shipping insecure defaults to production. If
# DEBUG is off we must have a real SECRET_KEY and a non-default DB password.
# (BE-10) Catches a misconfigured deploy at boot instead of at exploit time.
if not DEBUG:
    from django.core.exceptions import ImproperlyConfigured

    if SECRET_KEY == 'django-insecure-dev-only-change-in-production':
        raise ImproperlyConfigured(
            'SECRET_KEY must be set to a real secret when DEBUG=False.'
        )
    _db_password = DATABASES['default'].get('PASSWORD')
    if not DATABASE_URL and _db_password == 'secplus_dev_password':
        raise ImproperlyConfigured(
            'DB_PASSWORD must not be the dev default when DEBUG=False.'
        )

# Logging: a dependency-free console config so request errors and app-level
# audit lines (answer submissions, login failures) are visible in the Railway
# logs. Level is env-overridable via LOG_LEVEL. (BE-09 / W9)
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[{asctime}] {levelname} {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': LOG_LEVEL,
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}
