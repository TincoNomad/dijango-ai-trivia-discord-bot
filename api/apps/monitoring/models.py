"""
Monitoring Models Module

This module defines the database models for the monitoring system.
It includes models for:
- Request logging (HTTP requests)
- Error logging (Application errors)

Both models include appropriate indexes for efficient querying.
"""

from django.db import models
from django.utils import timezone

class RequestLog(models.Model):
    """
    Model for logging HTTP requests.
    
    Stores detailed information about HTTP requests including timing,
    method, path, status code, and associated data.
    
    Indexes are created on frequently queried fields for performance.
    """
    
    timestamp = models.DateTimeField(default=timezone.now)
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    response_time = models.FloatField()
    status_code = models.SmallIntegerField()
    user_id = models.CharField(max_length=255, null=True)
    ip_address = models.GenericIPAddressField(null=True)
    request_data = models.JSONField(null=True, blank=True)
    response_data = models.JSONField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['path']),
            models.Index(fields=['status_code'])
        ]
        
    def __str__(self):
        """String representation of the request log."""
        return f"{self.method} {self.path} - {self.status_code}"

class ErrorLog(models.Model):
    """
    Model for logging application errors.
    
    Stores detailed information about errors including type,
    message, traceback, and request context.
    
    Indexes are created on frequently queried fields for performance.
    """
    
    timestamp = models.DateTimeField(default=timezone.now)
    error_type = models.CharField(max_length=100)
    error_message = models.TextField()
    traceback = models.TextField()
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    user_id = models.CharField(max_length=255, null=True)
    request_data = models.JSONField(null=True, blank=True)
    url = models.URLField(max_length=255)
    
    class Meta:
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['error_type'])
        ]
