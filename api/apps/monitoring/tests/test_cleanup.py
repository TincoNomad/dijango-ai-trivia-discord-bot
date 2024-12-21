"""
Tests for log cleanup functionality.
Tests retention and cleanup of logs.
"""

import pytest
from django.core.management import call_command
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from .test_base import MonitoringBaseTest
from api.apps.monitoring.models import RequestLog, ErrorLog

@pytest.mark.django_db
class TestLogCleanup(MonitoringBaseTest):
    """Test cases for log cleanup operations"""

    def test_cleanup_old_request_logs(self):
        """Verificar limpieza de logs antiguos de requests"""
        # Arrange
        retention_days = settings.MONITORING['REQUEST_LOG_RETENTION_DAYS']
        old_date = timezone.now() - timedelta(days=retention_days + 1)
        
        # Crear logs antiguos y recientes
        old_log = RequestLog.objects.create(
            path='/test/',
            method='GET',
            response_time=0.1,
            status_code=200,
            timestamp=old_date
        )
        recent_log = RequestLog.objects.create(
            path='/test/',
            method='GET',
            response_time=0.1,
            status_code=200
        )
        
        # Act
        call_command('cleanup_logs')
        
        # Assert
        assert not RequestLog.objects.filter(id=old_log.id).exists()
        assert RequestLog.objects.filter(id=recent_log.id).exists()

    def test_cleanup_old_error_logs(self):
        """Verificar limpieza de logs antiguos de errores"""
        # Arrange
        retention_days = settings.MONITORING['ERROR_LOG_RETENTION_DAYS']
        old_date = timezone.now() - timedelta(days=retention_days + 1)
        
        # Crear logs antiguos y recientes
        old_error = ErrorLog.objects.create(
            error_type='404',
            error_message='Not Found',
            path='/test/',
            method='GET',
            timestamp=old_date
        )
        recent_error = ErrorLog.objects.create(
            error_type='404',
            error_message='Not Found',
            path='/test/',
            method='GET'
        )
        
        # Act
        call_command('cleanup_logs')
        
        # Assert
        assert not ErrorLog.objects.filter(id=old_error.id).exists()
        assert ErrorLog.objects.filter(id=recent_error.id).exists()

    def test_cleanup_batch_processing(self):
        """Verificar que la limpieza funcione correctamente en lotes"""
        # Arrange
        retention_days = settings.MONITORING['REQUEST_LOG_RETENTION_DAYS']
        old_date = timezone.now() - timedelta(days=retention_days + 1)
        
        # Crear muchos logs antiguos
        batch_size = 1500  # Más grande que el tamaño del lote
        logs = []
        for _ in range(batch_size):
            logs.append(RequestLog(
                path='/test/',
                method='GET',
                response_time=0.1,
                status_code=200,
                timestamp=old_date
            ))
        RequestLog.objects.bulk_create(logs)
        
        # Act
        call_command('cleanup_logs')
        
        # Assert
        assert RequestLog.objects.count() == 0 