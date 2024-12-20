"""
Test data for user-related tests.
Contains constants and test data fixtures.
"""

TEST_USER_DATA = {
    'valid_user': {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123',
        'role': 'admin'
    },
    'new_user': {
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'newpass123',
        'role': 'user'
    }
}

ERROR_MESSAGES = {
    'INVALID_EMAIL': 'Enter a valid email address.',
    'PASSWORD_REQUIRED': 'Password field is required.',
    'FORBIDDEN': 'You do not have permission to perform this action.',
    'INVALID_CREDENTIALS': 'Invalid credentials provided.',
    'USER_NOT_FOUND': 'User not found.',
}