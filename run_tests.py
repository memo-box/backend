#!/usr/bin/env python
import os
import sys
import django
from dotenv import load_dotenv

# Set test environment variables directly
os.environ.update({
    'DJANGO_SETTINGS_MODULE': 'memobox.settings',
    'SECRET_KEY': 'django-insecure-test-key-not-for-production',
    'DEBUG': 'True',
    'ALLOWED_HOSTS': 'localhost,127.0.0.1',
    'DATABASE_URL': 'sqlite:///test_db.sqlite3',
    'JWT_ACCESS_TOKEN_LIFETIME': '60',
    'JWT_REFRESH_TOKEN_LIFETIME': '1',
    'STATIC_URL': '/static/',
    'MEDIA_URL': '/media/',
    'EMAIL_BACKEND': 'django.core.mail.backends.console.EmailBackend',
    'EMAIL_HOST': 'localhost',
    'EMAIL_PORT': '25',
    'EMAIL_USE_TLS': 'False',
    'EMAIL_HOST_USER': 'test@example.com',
    'EMAIL_HOST_PASSWORD': 'testpass',
    'OPENAI_API_KEY': 'test-key-not-for-production',
    'OPENAI_MODEL': 'gpt-4-mini',
})

# Initialize Django
django.setup()

if __name__ == '__main__':
    import pytest
    sys.exit(pytest.main(sys.argv[1:]))
