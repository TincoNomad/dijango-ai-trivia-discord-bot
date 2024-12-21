"""
Test data for monitoring-related tests.
Contains constants and test data fixtures.
"""

from typing import TypedDict, List

class EndpointTestCase(TypedDict):
    endpoint: str
    method: str
    expected_status: int

class PerformanceThresholds(TypedDict):
    max_response_time: float
    batch_size: int
    max_memory_usage: int

ENDPOINTS_TO_TEST: List[EndpointTestCase] = [
    {'endpoint': '/api/users/', 'method': 'GET', 'expected_status': 200},
    {'endpoint': '/api/score/', 'method': 'POST', 'expected_status': 200},
    {'endpoint': '/api/trivia/', 'method': 'GET', 'expected_status': 200},
]

PERFORMANCE_THRESHOLDS: PerformanceThresholds = {
    'max_response_time': 1.0,  # segundos
    'batch_size': 1000,
    'max_memory_usage': 100 * 1024 * 1024  # 100MB
}

TEST_REQUEST_DATA = {
    'valid_request': {
        'name': 'test',
        'points': 100
    }
}

ERROR_MESSAGES = {
    'INVALID_REQUEST': 'Invalid request data',
    'LOG_CREATION_FAILED': 'Failed to create log entry',
    'CLEANUP_FAILED': 'Log cleanup operation failed'
} 