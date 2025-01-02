"""
Production Environment Settings

This module contains Django settings specific to the production environment.
It imports all base settings and overrides only the necessary values.

Note:
    Security settings are automatically enabled based on DEBUG=False in base.py
    Make sure your server has a valid SSL certificate installed.
"""

from .base import DATABASES, env

# Production security settings
DEBUG = False

# Allowed hosts should be strictly limited in production
ALLOWED_HOSTS = env("ALLOWED_HOSTS", default="your-production-domain.com,web").split(
    ","
)

# Define BASE_URL for production
BASE_URL = env("API_BASE_URL", default="https://your-production-domain.com")

# Configuración SSL para MySQL en producción
if env("ENVIRONMENT") == "production":
    DATABASES["default"]["OPTIONS"].update(
        {
            "ssl": {
                "ca": env("MYSQL_SSL_CA", default="/etc/mysql/certs/ca.pem"),
                "cert": env(
                    "MYSQL_SSL_CERT",
                    default="/etc/mysql/certs/client-cert.pem",
                ),
                "key": env("MYSQL_SSL_KEY", default="/etc/mysql/certs/client-key.pem"),
            }
        }
    )
