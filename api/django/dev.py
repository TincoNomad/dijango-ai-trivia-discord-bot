"""
Development Environment Settings

This module contains Django settings specific to the development environment.
It imports all base settings and overrides certain values for development use.

Key differences from production:
- Debug mode enabled
- Local hosts allowed
- Console email backend
- Simplified security settings
"""

from .base import *

# Development server configurations
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Development API URL
BASE_URL = 'http://127.0.0.1:8000'

# Development-specific settings
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'