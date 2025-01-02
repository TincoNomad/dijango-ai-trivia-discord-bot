"""
Base test class for monitoring-related tests.
Contains common functionality and helper methods for:
- Log cleanup
- Sample data creation
- Log validation
- Common assertions
"""

from datetime import datetime
from typing import List, Tuple

from api.apps.monitoring.models import ErrorLog, RequestLog

from .factories import ErrorLogFactory, RequestLogFactory


class MonitoringBaseTest:
    """
    Base class for monitoring tests with common functionality.

    Provides utility methods for:
    - Log management
    - Test data creation
    - Log validation
    - Common assertions
    """

    @staticmethod
    def cleanup_logs():
        """
        Clean up all logs after tests.

        Removes all RequestLog and ErrorLog entries from the database.
        Should be called in test teardown.
        """
        RequestLog.objects.all().delete()
        ErrorLog.objects.all().delete()

    @staticmethod
    def create_sample_logs(
        num_requests: int = 5, num_errors: int = 3
    ) -> Tuple[List[RequestLog], List[ErrorLog]]:
        """
        Creates sample logs for testing.

        Args:
            num_requests: Number of request logs to create
            num_errors: Number of error logs to create

        Returns:
            Tuple[List[RequestLog], List[ErrorLog]]: Created logs
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

        Raises:
            AssertionError: If any validation fails
        """
        assert log.path is not None
        assert log.method in ["GET", "POST", "PUT", "DELETE"]
        assert isinstance(log.response_time, float)
        assert isinstance(log.status_code, int)

    def assert_log_format(self, log_entry):
        """
        Validates the correct format of a log entry.
        Centralizes common validations.

        Args:
            log_entry: The log entry to validate

        Raises:
            AssertionError: If any validation fails
        """
        assert isinstance(log_entry.timestamp, datetime)
        assert log_entry.method in ["GET", "POST", "PUT", "DELETE"]
        assert isinstance(log_entry.response_time, float)
        assert 200 <= log_entry.status_code < 600
