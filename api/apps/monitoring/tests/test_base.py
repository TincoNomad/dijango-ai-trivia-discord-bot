"""
Base test class for monitoring-related tests.
Contains common functionality and helper methods.
"""

import pytest
from django.utils import timezone
from datetime import timedelta
from api.apps.monitoring.models import RequestLog, ErrorLog
from .factories import RequestLogFactory, ErrorLogFactory

class MonitoringBaseTest:
    """Clase base para tests de monitoreo"""

    @staticmethod
    def create_sample_logs(num_requests=5, num_errors=3):
        """Helper para crear logs de prueba"""
        requests = RequestLogFactory.create_batch(size=num_requests)
        errors = ErrorLogFactory.create_batch(size=num_errors)
        return requests, errors

    @staticmethod
    def create_old_logs(days_old=30):
        """Helper para crear logs antiguos"""
        old_date = timezone.now() - timedelta(days=days_old)
        return RequestLogFactory.create(timestamp=old_date)

    @staticmethod
    def assert_log_fields(log_entry, expected_data):
        """Validar campos de un log"""
        for field, value in expected_data.items():
            assert getattr(log_entry, field) == value

    @staticmethod
    def cleanup_logs():
        """Limpiar todos los logs después de las pruebas"""
        RequestLog.objects.all().delete()
        ErrorLog.objects.all().delete()