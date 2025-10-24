"""
Production settings for Housing Evaluation System.
"""

import os

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Allowed hosts configuration
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if host.strip()
]

# Email configuration for production (Mailgun via Anymail)
EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"
ANYMAIL = {
    "MAILGUN_API_KEY": os.environ.get("MAILGUN_API_KEY", ""),
    "MAILGUN_SENDER_DOMAIN": os.environ.get("MAILGUN_DOMAIN", "checklist.casa"),
}
DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL", "Checklist.casa <noreply@checklist.casa>"
)
SERVER_EMAIL = os.environ.get("SERVER_EMAIL", "server@checklist.casa")

# Email timeout settings
EMAIL_TIMEOUT = 30

# Static files configuration for production
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files security
MEDIA_ROOT = BASE_DIR / "media"
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
FILE_UPLOAD_PERMISSIONS = 0o644

# Database optimization for production
DATABASES["default"].update(
    {
        "CONN_MAX_AGE": 60,
        "OPTIONS": {
            "timeout": 20,
        },
    }
)

# Cache configuration (using database cache for simplicity)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "cache_table",
        "TIMEOUT": 300,
        "OPTIONS": {
            "MAX_ENTRIES": 1000,
        },
    }
}

# Session configuration
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
SESSION_CACHE_ALIAS = "default"

# Logging configuration for production
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console", "mail_admins"],
            "level": "INFO",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["console", "mail_admins"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console", "mail_admins"],
            "level": "ERROR",
            "propagate": False,
        },
        "projects": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# Admin configuration
ADMINS = [
    ("Admin", os.environ.get("ADMIN_EMAIL", "admin@checklist.casa")),
]
MANAGERS = ADMINS

# Error reporting
SILENCED_SYSTEM_CHECKS: list[str] = []

# Performance optimizations
USE_TZ = True
USE_I18N = False  # Disable if not using internationalization
USE_L10N = False  # Disable if not using localization

# CSRF and security settings for production
CSRF_TRUSTED_ORIGINS = [
    "https://checklist.casa",
]

# Performance optimizations
CONN_MAX_AGE = 60
