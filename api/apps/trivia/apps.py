"""
Trivia Application Configuration

This module defines the Django application configuration for the trivia system.
Handles the setup and configuration of the trivia game application.
"""

from django.apps import AppConfig


class TriviaConfig(AppConfig):
    """
    Configuration class for the trivia application.
    
    Attributes:
        default_auto_field (str): The default primary key field type
        name (str): The Python package name of the application
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api.apps.trivia'
