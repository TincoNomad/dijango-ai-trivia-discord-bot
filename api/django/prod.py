"""
Production Environment Settings

This module contains Django settings specific to the production environment.
It imports all base settings and overrides certain values for production use.

Key differences from development:
- Debug mode disabled
- Restricted allowed hosts
- Production-ready security settings
- Production API URL
"""

from .base import *

# Production security settings
DEBUG = False
ALLOWED_HOSTS = env('ALLOWED_HOSTS', default='your-production-domain.com,web').split(',')

# Production API URL
BASE_URL = env('API_BASE_URL', default='https://your-production-domain.com')

# Additional production-specific settings can be added here
