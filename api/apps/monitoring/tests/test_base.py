"""
Base test class for monitoring-related tests.
Contains common functionality and helper methods.
"""

from typing import Tuple, List
from api.apps.monitoring.models import RequestLog, ErrorLog
from .factories import RequestLogFactory, ErrorLogFactory
from datetime import datetime

class MonitoringBaseTest:
    """Base class for monitoring tests with common functionality"""

    @staticmethod
    def cleanup_logs():
        """Clean up all logs after tests"""
        RequestLog.objects.all().delete()
        ErrorLog.objects.all().delete()

    @staticmethod
    def create_sample_logs(
        num_requests: int = 5,
        num_errors: int = 3
    ) -> Tuple[List[RequestLog], List[ErrorLog]]:
        """
        Creates sample logs for testing.
        
        Args:
            num_requests: Number of request logs to create
            num_errors: Number of error logs to create
            
        Returns:
            Tuple containing lists of created request and error logs
        """
        requests = RequestLogFactory.create_batch(size=num_requests)
        errors = ErrorLogFactory.create_batch(size=num_errors)
        return requests, errors

    @staticmethod
    def assert_valid_log(log: RequestLog) -> None:
        """
        Validates that a log entry contains all required fields.
        
        Args:
            log: The log entry to validate
        """
        assert log.path is not None
        assert log.method in ['GET', 'POST', 'PUT', 'DELETE']
        assert isinstance(log.response_time, float)
        assert isinstance(log.status_code, int)

    def assert_log_format(self, log_entry):
        """
        Valida el formato correcto de un log.
        Centraliza las validaciones comunes.
        """
        assert isinstance(log_entry.timestamp, datetime)
        assert log_entry.method in ['GET', 'POST', 'PUT', 'DELETE']
        assert isinstance(log_entry.response_time, float)
        assert 200 <= log_entry.status_code < 600