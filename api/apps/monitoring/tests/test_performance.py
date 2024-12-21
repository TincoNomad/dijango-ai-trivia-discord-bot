"""
Performance tests for monitoring functionality.
Tests response times and behavior under load.
"""

import pytest
import time
from concurrent.futures import ThreadPoolExecutor
from django.urls import reverse
from rest_framework.test import APIClient
from .test_base import MonitoringBaseTest
from .test_data import PERFORMANCE_THRESHOLDS
from api.apps.monitoring.models import RequestLog

@pytest.mark.django_db
class TestMonitoringPerformance(MonitoringBaseTest):
    """Test cases for monitoring performance"""

    @pytest.fixture(autouse=True)
    def setup(self, api_client, test_user):
        """Setup para cada test"""
        self.client = api_client
        self.test_user = test_user  # Guardar referencia al usuario
        self.cleanup_logs()
        yield
        self.cleanup_logs()

    def test_logging_response_time(self, api_client_authenticated):
        """Verificar que el logging no impacte significativamente el tiempo de respuesta"""
        # Arrange
        endpoint = reverse('trivia-list')  # Usar reverse para generar la URL correcta
        
        # Act
        start_time = time.time()
        api_client_authenticated.get(endpoint)
        total_time = time.time() - start_time
        
        # Assert
        assert total_time < PERFORMANCE_THRESHOLDS['max_response_time']
        log = RequestLog.objects.filter(path=endpoint).first()
        assert log is not None
        assert log.response_time < PERFORMANCE_THRESHOLDS['max_response_time']

    def test_concurrent_requests_logging(self, test_user):
        """Verificar comportamiento bajo múltiples requests simultáneos"""
        # Arrange
        num_requests = 10
        endpoint = reverse('trivia-list')  # Usar reverse para generar la URL correcta

        def make_request():
            client = APIClient()
            client.force_authenticate(user=test_user)
            return client.get(endpoint)

        # Act
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            [f.result() for f in futures]

        # Assert
        logs = RequestLog.objects.filter(path=endpoint)
        assert logs.count() == num_requests
        assert all(log.response_time < PERFORMANCE_THRESHOLDS['max_response_time'] 
                  for log in logs)

    def test_batch_log_creation(self):
        """Verificar rendimiento al crear múltiples logs"""
        # Arrange
        batch_size = PERFORMANCE_THRESHOLDS['batch_size']
        
        # Act
        start_time = time.time()
        requests, errors = self.create_sample_logs(
            num_requests=batch_size, 
            num_errors=batch_size//10
        )
        creation_time = time.time() - start_time
        
        # Assert
        assert creation_time < PERFORMANCE_THRESHOLDS['max_response_time'] * 10
        assert RequestLog.objects.count() == batch_size 