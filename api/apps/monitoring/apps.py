"""
Monitoring Application Configuration

This module defines the Django application configuration for the monitoring system.
It handles the setup and configuration of the monitoring application.
"""

from django.apps import AppConfig


class MonitoringConfig(AppConfig):
    """
    Configuration class for the monitoring application.
    
    Attributes:
        default_auto_field (str): The default primary key field type
        name (str): The Python package name of the application
    """
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api.apps.monitoring'
