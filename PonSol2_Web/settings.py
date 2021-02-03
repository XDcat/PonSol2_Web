"""
Django settings for PonSol2_Web project.

Generated by 'django-admin startproject' using Django 3.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '^036eglnkjc@dby*3px-wqu-ellinvc@8ow2cv40pzzn!tp6t2'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    "ponsol2web.apps.Ponsol2WebConfig",
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

ROOT_URLCONF = 'PonSol2_Web.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
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

WSGI_APPLICATION = 'PonSol2_Web.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    "default": {
        'ENGINE': 'django.db.backends.mysql',
        "OPTIONS": {
            'read_default_file': os.path.join(BASE_DIR, "my.config")
        },
    },
    'other': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'

LOGGING = {
    "version": 1,  # 目前只有 1 有效，用于以后兼容性
    "incremental": False,  # 是否在运行中时修改配置, 默认 False
    "disable_existing_loggers": True,  # 是否禁用任何非根的所有 Logger, 默认 False
    "formatters": {  # 格式化生成器(格式器)
        "default": {
            "format": "%(name)s %(asctime)s [%(filename)s %(funcName)s()] <%(levelname)s>: %(message)s",
        },
        "brief": {
            "format": "%(name)s [%(funcName)s()] <%(levelname)s>: %(message)s",
        }
    },
    "filters": {},  # 过滤器，需要自定义类，一般不会用到
    "handlers": {
        "console": {  # 控制台
            "class": "logging.StreamHandler",
            "formatter": "brief",
            "level": "DEBUG",
            "stream": "ext://sys.stdout",
        },
        "file_debug": {  # 输出到文件
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default",
            "level": "DEBUG",
            "filename": os.path.join(BASE_DIR, "debug.log"),  # 必选, 文件名称
            "encoding": "utf8",
            "maxBytes": 10485760,  # 日志文件最大个数 1024B * 1024 * 10 = 10MB
            "backupCount": 10,  # 日志文件最大个数
        },
        "file_info": {  # 输出到文件
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default",
            "level": "INFO",
            "filename": os.path.join(BASE_DIR, "info.log"),  # 必选, 文件名称
            "encoding": "utf8",
            "maxBytes": 10485760,  # 日志文件最大个数 1024B * 1024 * 10 = 10MB
            "backupCount": 10,  # 日志文件最大个数
        },
    },
    "loggers": {
        "ponsol2_web": {
            "level": "DEBUG",
            "handlers": ["console", "file_debug", "file_info"],
            "propagate": False,  # 是否传给父级
        }
    },
}

# 邮箱设置
EMAIL_HOST = "smtp.111.com"
EMAIL_PORT = "465"
EMAIL_HOST_USER = "zenglianjie@111.com"
EMAIL_HOST_PASSWORD = "SKJDzcNpEhN7g3Fq"
EMAIL_USE_SSL = True
EMAIL_TIMEOUT = 5
