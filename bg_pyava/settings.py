"""
Django settings for bg_pyava project.

Generated by 'django-admin startproject' using Django 4.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-6n@4s5ij7jdtbfpttgk)vt(9f1!kisraq#50hsyiokba6he%48'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    'back.apps.BackConfig',
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
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bg_pyava.urls'

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

WSGI_APPLICATION = 'bg_pyava.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Local Memory Cache

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_TZ = True

USE_L10N = False

DATETIME_FORMAT = 'Y-m-d H:i:s'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


LOGGING = {
    # 日志记录配置版本信息
    'version': 1,
    # 启用已有日志配置信息
    'disable_existing_loggers': False,
    # 配置日志格式化对象：定义消息格式
    'formatters': {
        # 定义标准消息格式
        'standard': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        # 定义简化消息格式，用于控制台操作
        'simple': {
            'format': '{levelname} [{asctime}] {message}',
            'style': '{',
        },
    },
    # 配置过滤器
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    # 配置定义处理程序
    'handlers': {
        # 配置控制台日志处理程序
        'console': {
            # 记录INFO级别及以上日志
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            # 使用建议日志格式消息
            'formatter': 'simple'
        },
        # 配置文件日志处理程序
        'file': {
            # 记录DEBUG级别及以上日志
            'level': 'INFO',
            'filters': ['require_debug_false'],
            # 使用标准消息格式进行记录
            'formatter': 'standard',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'log/info.log',
            # 备份文件数量
            'backupCount': 10,
            # 设置每个文件存储的最大体积
            'maxBytes': 1024 * 1024 * 10,
            'encoding': 'utf-8'
        },
        # 配置邮件处理程序
        'error': {
            # 记录ERROR级别及以上日志
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            # 使用标准消息格式进行记录
            'formatter': 'standard',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'log/error.log',
            # 备份文件数量
            'backupCount': 10,
            # 设置每个文件存储的最大体积
            'maxBytes': 1024 * 1024 * 10,
        }
    },
    # 配置日志记录器对象
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'propagate': True,
            'level': 'DEBUG'
        },
        'django.request': {
            'handlers': ['error', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'back': {
            'handlers': ['error', 'console'],
            'level': 'ERROR',
        }
    }
}


# 本地应用程序配置

# 代理服务器的访问相对路径
AGENT_PATH = 'Local'
