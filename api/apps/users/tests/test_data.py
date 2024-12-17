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
        'email': 'newuser@example.com',
        'password': 'newpass123',
        'role': 'admin'
    },
    'invalid_email_user': {
        'username': 'newuser',
        'email': 'invalid-email',
        'password': 'newpass123'
    }
}

ERROR_MESSAGES = {
    'INVALID_EMAIL': 'Enter a valid email address.',
    'DUPLICATE_USERNAME': 'A user with that username already exists.',
    'PASSWORD_REQUIRED': 'This field is required.',
    'USER_NOT_FOUND': 'User not found',
    'INVALID_CREDENTIALS': 'No active account found with the given credentials'
}