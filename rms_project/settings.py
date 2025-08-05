import os
     from pathlib import Path
     import pymysql

     pymysql.install_as_MySQLdb()

     # Build paths inside the project
     BASE_DIR = Path(__file__).resolve().parent.parent

     # Security settings
     SECRET_KEY = 'django-insecure-+fpb4rj_u@9ii(@dp=c*m34*b$j5#tx)-@d9+c2x1#iek_!@k7'  
     DEBUG = False  # Production setting
     ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com', 'rms.yourdomain.com']

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
             'DIRS': [BASE_DIR / 'results' / 'templates'],
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

     # Database (cPanel MySQL)
     DATABASES = {
         'default': {
             'ENGINE': 'django.db.backends.mysql',
             'NAME': 'yourusername_rms_db',
             'USER': 'yourusername_rms_user',
             'PASSWORD': 'your-cpanel-password',
             'HOST': 'localhost',
             'PORT': '3306',
             'OPTIONS': {
                 'charset': 'utf8mb4',
                 'connect_timeout': 60,
                 'init_command': "SET sql_mode='STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION'"
             }
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
     STATICFILES_DIRS = [
         BASE_DIR / 'results' / 'static',
     ]
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
     CSRF_COOKIE_SECURE = True  # Enable for HTTPS
     SESSION_COOKIE_SECURE = True  # Enable for HTTPS
     SECURE_SSL_REDIRECT = True  # Enable for HTTPS

     # Email settings
     EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
     EMAIL_HOST = 'smtp.gmail.com'
     EMAIL_PORT = 587
     EMAIL_USE_TLS = True
     EMAIL_HOST_USER = 'your-email@gmail.com'
     EMAIL_HOST_PASSWORD = 'your-app-specific-password'
     DEFAULT_FROM_EMAIL = 'your-email@gmail.com'

     # 2FA settings
     ENABLE_2FA = False

     # Login settings
     LOGIN_URL = '/results/login/'
     LOGIN_REDIRECT_URL = '/results/home/'

     # Timestamp
     # Last Updated: August 05, 2025 02:54 PM CEST