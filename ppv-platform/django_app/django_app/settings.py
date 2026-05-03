import os
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv(os.path.join(Path(__file__).resolve().parent.parent, '.env'))

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'changeme')
DEBUG = os.getenv('DJANGO_DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '*').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'core',
    'corsheaders',
]

AUTH_USER_MODEL = 'core.User'

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CORS settings for frontend integration
CORS_ALLOWED_ORIGINS = [
    'http://localhost:8080',
]
CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = 'django_app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'django_app.wsgi.application'

def _database_config_from_url(database_url):
    parsed = urlparse(database_url)
    return {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': parsed.path.lstrip('/') or 'ppv',
        'USER': parsed.username or 'ppvuser',
        'PASSWORD': parsed.password or 'ppvpass',
        'HOST': parsed.hostname or 'db',
        'PORT': str(parsed.port or 5432),
    }

database_url = os.getenv('DATABASE_URL')

DATABASES = {
    'default': {
        **(_database_config_from_url(database_url) if database_url else {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('PGDATABASE', os.getenv('POSTGRES_DB', 'ppv')),
            'USER': os.getenv('PGUSER', os.getenv('POSTGRES_USER', 'ppvuser')),
            'PASSWORD': os.getenv('PGPASSWORD', os.getenv('POSTGRES_PASSWORD', 'ppvpass')),
            'HOST': os.getenv('PGHOST', os.getenv('POSTGRES_HOST', 'db')),
            'PORT': os.getenv('PGPORT', os.getenv('POSTGRES_PORT', '5432')),
        }),
    }
}

REDIS_URL = os.getenv('REDIS_URL')

CACHES = {
    'default': ({
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'zinema-local-cache',
    } if not REDIS_URL else {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    })
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
