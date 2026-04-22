"""
Configuration Django pour PhytoScan AI.
Compatible développement local et déploiement sur Render.
Dépendances externes : aucune (utilise uniquement os.environ).
"""
import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def env(key, default='', cast=None):
    """Lit une variable d'environnement avec valeur par défaut et cast optionnel."""
    value = os.environ.get(key, default)
    if cast is bool:
        return value.lower() in ('true', '1', 'yes') if isinstance(value, str) else bool(value)
    if cast is list:
        return [v.strip() for v in value.split(',') if v.strip()]
    return value


# ── Sécurité ───────────────────────────────────────────────────────────────
SECRET_KEY = env('SECRET_KEY', 'django-insecure-dev-key-change-in-production')
DEBUG = env('DEBUG', 'True', cast=bool)

RENDER_EXTERNAL_HOSTNAME = env('RENDER_EXTERNAL_HOSTNAME', '')

ALLOWED_HOSTS = env('ALLOWED_HOSTS', 'localhost,127.0.0.1', cast=list)

if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

if not DEBUG:
    ALLOWED_HOSTS.append('.onrender.com')

# ── Clé API Groq (chatbot PhytoBot) ───────────────────────────────────────
GROQ_API_KEY = env('GROQ_API_KEY', '')

# ── Applications ───────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'core',
    'detection',
    'chatbot',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'phytoscan.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.site_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'phytoscan.wsgi.application'

# ── Base de données ────────────────────────────────────────────────────────
# Développement : SQLite.
# Production Render : PostgreSQL via DATABASE_URL (injectée automatiquement).
DATABASE_URL = env('DATABASE_URL', '')

if DATABASE_URL:
    match = re.match(
        r'(?:postgresql|postgres)://([^:]+):([^@]+)@([^:/]+):?(\d*)/(.+)',
        DATABASE_URL
    )
    if match:
        db_user, db_password, db_host, db_port, db_name = match.groups()
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': db_name,
                'USER': db_user,
                'PASSWORD': db_password,
                'HOST': db_host,
                'PORT': db_port or '5432',
                'CONN_MAX_AGE': 600,
                'OPTIONS': {'connect_timeout': 10},
            }
        }
    else:
        raise ValueError(f"DATABASE_URL invalide : {DATABASE_URL}")
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ── Validation des mots de passe ───────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── Internationalisation ───────────────────────────────────────────────────
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Dakar'
USE_I18N = True
USE_TZ = True

# ── Fichiers statiques (WhiteNoise) ────────────────────────────────────────
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
WHITENOISE_USE_FINDERS = True
WHITENOISE_MAX_AGE = 31536000

# ── Fichiers média ─────────────────────────────────────────────────────────
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ── Upload ─────────────────────────────────────────────────────────────────
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Sécurité HTTPS — production Render uniquement ──────────────────────────
if not DEBUG:
    # SECURE_SSL_REDIRECT désactivé intentionnellement :
    # Render gère la redirection HTTPS au niveau de son proxy.
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'