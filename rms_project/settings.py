import os
from pathlib import Path
import pymysql

pymysql.install_as_MySQLdb()

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Security settings
SECRET_KEY = 'django-insecure-+fpb4rj_u@9ii(@dp=c*m34*b$j5#tx)-@d9+c2x1#iek_!@k7'
DEBUG = False  # Set to False for live hosting
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'miihive.pythonanywhere.com']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'results.apps.ResultsConfig',
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

ROOT_URLCONF = 'rms_project.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'rms_project.wsgi.application'

# Database (Update with PythonAnywhere MySQL credentials)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'miihive$result_management_db',
        'USER': 'miihive',  # Replace with your PythonAnywhere database user (likely 'miihive', not 'root')
        'PASSWORD': 'Onehouse12@@', 
        'HOST': 'miihive.mysql.pythonanywhere-services.com',
        'PORT': '3306',
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
TIME_ZONE = 'Africa/Lagos'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Session and security settings
SESSION_COOKIE_AGE = 1209600
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
CSRF_COOKIE_SECURE = False  # Set to True for HTTPS in production
SESSION_COOKIE_SECURE = False  # Set to True for HTTPS in production
SECURE_SSL_REDIRECT = False  # Set to True for HTTPS in production

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Prints emails to console for testing
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'test@gmail.com'  # Can be fake for console backend
EMAIL_HOST_PASSWORD = 'your-app-specific-password'  # Can be fake for console backend
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'

# To use real emails with 2FA:
# 1. Set EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# 2. Enable 2-Step Verification at https://myaccount.google.com/security
# 3. Go to "App passwords", select "Mail" and "Other (Django RMS)"
# 4. Copy the 16-character password and paste it into EMAIL_HOST_PASSWORD

# 2FA settings
ENABLE_2FA = False  # Keep False until launch; set to True to enable 2FA for admins and teachers

# Login settings
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/home/'

# Development settings (remove in production)
if DEBUG:
    import mimetypes
    mimetypes.add_type("application/javascript", ".js", True)
    mimetypes.add_type("text/css", ".css", True)

# Timestamp for reference
# Last Updated: August 03, 2025 08:33 AM CEST