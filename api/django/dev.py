"""
Development Environment Settings

This module contains Django settings specific to the development environment.
It imports all base settings and overrides only the necessary values.

Note:
    Security settings are automatically adjusted based on DEBUG=True in base.py
"""

from .base import *

# Development server configurations
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'web']

# Development-specific settings
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Override BASE_URL if needed (optional, as it's already handled in base.py)
# BASE_URL = 'http://web:8000'