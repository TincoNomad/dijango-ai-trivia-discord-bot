"""
Monitoring Admin Configuration Module

This module configures the Django admin interface for monitoring models.
It includes customized admin views for:
- Request logs (HTTP requests tracking)
- Error logs (Application errors tracking)

Both admin views provide filtering, searching and read-only display of log entries.
"""

from django.contrib import admin
from .models import RequestLog, ErrorLog

@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for RequestLog model.
    
    Features:
    - List display with key request information
    - Filtering by method, status code and timestamp
    - Search functionality for paths and user IDs
    - All fields are read-only to prevent modifications
    """
    
    list_display = [
        'timestamp', 'method', 'path', 
        'status_code', 'response_time', 'user_id'
    ]
    list_filter = ['method', 'status_code', 'timestamp']
    search_fields = ['path', 'user_id']
    readonly_fields = [
        'timestamp', 'method', 'path', 'status_code', 
        'response_time', 'user_id', 'ip_address', 
        'request_data', 'response_data'
    ]

@admin.register(ErrorLog)
class ErrorLogAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for ErrorLog model.
    
    Features:
    - List display with key error information
    - Filtering by error type, method and timestamp
    - Search functionality for paths, messages and user IDs
    - All fields are read-only to prevent modifications
    """
    
    list_display = ['timestamp', 'error_type', 'method', 'path', 'user_id']
    list_filter = ['error_type', 'method', 'timestamp']
    search_fields = ['path', 'error_message', 'user_id']
    readonly_fields = [
        'timestamp', 'error_type', 'error_message', 
        'traceback', 'path', 'method', 'user_id', 
        'request_data', 'url'
    ]
