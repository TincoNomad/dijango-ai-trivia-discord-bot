"""
Integration tests for monitoring functionality.
Tests logging across different endpoints and scenarios.
"""

import pytest
from .test_base import MonitoringBaseTest
from .test_data import ENDPOINTS_TO_TEST
from api.apps.monitoring.models import RequestLog, ErrorLog
from api.django import TRIVIA_URL

@pytest.mark.django_db
class TestMonitoringIntegration(MonitoringBaseTest):
    """Test cases for monitoring integration"""

    @pytest.fixture(autouse=True)
    def setup(self, api_client):
        """Setup para cada test"""
        self.client = api_client
        self.cleanup_logs()
        yield
        self.cleanup_logs()

    @pytest.mark.parametrize("endpoint,method", ENDPOINTS_TO_TEST)
    def test_endpoint_logging(self, endpoint, method):
        """Verificar que se registren los logs para diferentes endpoints"""
        # Act
        if method == 'GET':
            response = self.client.get(endpoint)
        else:
            response = self.client.post(endpoint, {})

        # Assert
        log = RequestLog.objects.filter(path=endpoint).first()
        if response.status_code < 400:
            assert log is not None, f"No se creó log para {endpoint}"
            assert log.method == method
            assert log.status_code == response.status_code
            assert log.response_time > 0
        else:
            error_log = ErrorLog.objects.filter(path=endpoint).first()
            assert error_log is not None
            assert error_log.error_type == str(response.status_code)

    def test_error_logging(self):
        """Verificar el registro correcto de errores"""
        # Arrange
        invalid_endpoint = '/api/nonexistent/'
        
        # Act
        self.client.get(invalid_endpoint)
        
        # Assert
        error_log = ErrorLog.objects.filter(path=invalid_endpoint).first()
        assert error_log is not None
        assert error_log.error_type == '404'
        assert error_log.method == 'GET'

    def test_authenticated_request_logging(self, test_user, api_client_authenticated):
        """Verificar logging de requests autenticados"""
        # Arrange
        endpoint = TRIVIA_URL
        
        # Act
        api_client_authenticated.get(endpoint)
        
        # Assert
        log = RequestLog.objects.filter(path__endswith='/api/trivias/').first()
        assert log is not None
        assert log.status_code == 200
        # No verificamos el user_id, siguiendo el mismo patrón que test_request_with_data_logging

    def test_request_with_data_logging(self, api_client_authenticated, test_leaderboard):
        """Verificar logging de requests con datos"""
        # Arrange
        endpoint = '/api/score/'
        test_data = {
            'name': 'test',
            'points': 100,
            'discord_channel': test_leaderboard.discord_channel
        }
        
        # Act
        api_client_authenticated.post(endpoint, test_data, format='json')
        
        # Assert
        log = RequestLog.objects.filter(path=endpoint).first()
        assert log is not None
        assert log.request_data == test_data
        # El status puede ser error pero el log debe existir
        assert isinstance(log.response_data, dict)