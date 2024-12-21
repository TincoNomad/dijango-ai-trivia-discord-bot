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
ALLOWED_HOSTS = ['your-production-domain.com']

# Production API URL
BASE_URL = 'https://your-production-url.com'

# Additional production-specific settings can be added here
