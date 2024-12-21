"""
Score Application Configuration

This module defines the Django application configuration for the scoring system.
Handles the setup and configuration of the score tracking application.
"""

from django.apps import AppConfig


class ScoreConfig(AppConfig):
    """
    Configuration class for the score application.
    
    Attributes:
        default_auto_field (str): The default primary key field type
        name (str): The Python package name of the application
    """
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api.apps.score'
