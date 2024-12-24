"""
Production Environment Settings

This module contains Django settings specific to the production environment.
It imports all base settings and overrides only the necessary values.

Note:
    Security settings are automatically enabled based on DEBUG=False in base.py
    Make sure your server has a valid SSL certificate installed.
"""

from .base import *

# Production security settings
DEBUG = False

# Allowed hosts should be strictly limited in production
ALLOWED_HOSTS = env('ALLOWED_HOSTS', default='your-production-domain.com,web').split(',')

# Override BASE_URL if needed (optional, as it's already handled in base.py)
# BASE_URL = env('API_BASE_URL', default='https://your-production-domain.com')
