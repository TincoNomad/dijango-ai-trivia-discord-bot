"""
Test Data Module

This module provides test data constants and fixtures.
Includes:
- User test data
- Error messages
- Test case configurations
"""

TEST_USER_DATA = {
    "valid_user": {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "role": "admin",
    },
    "new_user": {
        "username": "newuser",
        "email": "new@example.com",
        "password": "newpass123",
        "role": "user",
    },
}

ERROR_MESSAGES = {
    "INVALID_EMAIL": "Enter a valid email address.",
    "PASSWORD_REQUIRED": "Password field is required.",
    "FORBIDDEN": "You do not have permission to perform this action.",
    "INVALID_CREDENTIALS": "Invalid credentials provided.",
    "USER_NOT_FOUND": "User not found.",
}

TEST_CASES = {
    "registration": {
        "valid": {...},
        "invalid_email": [...],
        "invalid_password": [...],
    },
    "authentication": {
        "valid": {...},
        "invalid": [...],
    },
}
