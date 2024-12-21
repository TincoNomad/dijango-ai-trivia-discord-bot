"""
Test data for monitoring-related tests.

Contains:
- Test case definitions
- Performance thresholds
- Sample request data
- Error messages
- Endpoint configurations
"""

from typing import TypedDict, List

class EndpointTestCase(TypedDict):
    """Type definition for endpoint test cases"""
    endpoint: str
    method: str
    expected_status: int

class PerformanceThresholds(TypedDict):
    """Type definition for performance thresholds"""
    max_response_time: float
    batch_size: int
    max_memory_usage: int

ENDPOINTS_TO_TEST: List[EndpointTestCase] = [
    {'endpoint': '/api/users/', 'method': 'GET', 'expected_status': 200},
    {'endpoint': '/api/score/', 'method': 'POST', 'expected_status': 200},
    {'endpoint': '/api/trivia/', 'method': 'GET', 'expected_status': 200},
]

PERFORMANCE_THRESHOLDS: PerformanceThresholds = {
    'max_response_time': 1.0,  # seconds
    'batch_size': 1000,
    'max_memory_usage': 100 * 1024 * 1024  # 100MB
}

# Test data constants
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

TEST_CASES = {
    'monitoring': {
        'endpoints': [
            {'url': '/api/users/', 'method': 'GET', 'expected_status': 200},
            {'url': '/api/score/', 'method': 'POST', 'expected_status': 200},
        ],
        'performance': {
            'max_response_time': 1.0,
            'batch_size': 1000
        }
    }
} 