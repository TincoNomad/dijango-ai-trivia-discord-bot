"""
Test data for monitoring-related tests.
Contains constants and test data fixtures.
"""

TEST_REQUEST_DATA = {
    'valid_request': {
        'path': '/api/test/endpoint',
        'method': 'GET',
        'response_time': 0.5,
        'status_code': 200,
        'user_id': 'test_user',
        'ip_address': '127.0.0.1'
    },
    'error_request': {
        'path': '/api/test/error',
        'method': 'POST',
        'error_type': 'ValidationError',
        'error_message': 'Invalid data provided',
        'user_id': 'test_user'
    }
}

ENDPOINTS_TO_TEST = [
    ('/api/users/', 'GET'),
    ('/api/score/', 'POST'),
    ('/api/trivia/', 'GET'),
    ('/api/nonexistent/', 'GET')
]

PERFORMANCE_THRESHOLDS = {
    'max_response_time': 1.0,  # segundos
    'batch_size': 1000,
    'max_memory_usage': 100 * 1024 * 1024  # 100MB
}

ERROR_MESSAGES = {
    'INVALID_REQUEST': 'Invalid request data',
    'LOG_CREATION_FAILED': 'Failed to create log entry',
    'CLEANUP_FAILED': 'Log cleanup operation failed'
} 