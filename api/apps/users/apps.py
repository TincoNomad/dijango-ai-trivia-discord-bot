"""
Users Application Configuration

This module defines the Django application configuration for user management.
Handles the setup and configuration of the users application.
"""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    Configuration class for the users application.

    Attributes:
        default_auto_field (str): The default primary key field type
        name (str): The Python package name of the application
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "api.apps.users"
