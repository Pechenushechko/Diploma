import os
from pathlib import Path
from mongoengine import connect
from zoneinfo import ZoneInfo
from datetime import datetime
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-m&+*&i+aqlgrk9c#ode02_ty00&836gnr53_m)s-z(l-@0ky#-'

# SECURITY WARNING: don't run with debug turned on in production!
SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = os.environ.get('DEBUG') == 'True'
ALLOWED_HOSTS = ['*']


TIME_ZONE = "Asia/Almaty"
USE_TZ = True

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
        'product_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'product_changes.log'),
            'formatter': 'standard',
        },
    },
    'loggers': {
        'product': {
            'handlers': ['product_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Application definition

INSTALLED_APPS = [
    'store',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'zooguru.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'store/templates/store'],
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

WSGI_APPLICATION = 'zooguru.wsgi.application'

# MongoDB подключение
connect(
    db='zooguru_db',
    alias='default',
    host='mongodb+srv://admin:admin@cluster.yngnitc.mongodb.net/zooguru_db?retryWrites=true&w=majority',
)

# # Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation

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


# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Media files

MEDIA_URL = '/media/'
import os

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')



# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'

STATICFILES_DIRS = [ BASE_DIR / 'static' ]

# Default primary key field type

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
