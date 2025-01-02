"""
Base Test Module for Users

This module provides base test functionality for user-related tests.
Includes:
- Common test fixtures
- Authentication helpers
- Response validation
- User creation utilities
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from .test_data import TEST_USER_DATA

User = get_user_model()


@pytest.mark.django_db
class BaseUserTest:
    """
    Base test class for user-related tests.

    Provides common functionality for:
    - User creation and authentication
    - Response validation
    - API client setup
    """

    @pytest.fixture(autouse=True)
    def setup_base(self):
        """Set up basic test environment"""
        self.api_client = APIClient()

    @staticmethod
    def create_and_authenticate_user(api_client, user_data):
        """
        Create and authenticate a user for testing.

        Args:
            api_client: API client instance
            user_data: User data dictionary

        Returns:
            User: Created and authenticated user
        """
        # Create user with appropriate permissions
        if user_data.get("role") == "admin" or user_data.get("is_superuser"):
            user = User.objects.create_superuser(
                username=user_data["username"],
                email=user_data.get("email", ""),
                password=user_data["password"],
                role="admin",
            )
        else:
            user = User.objects.create_user(
                username=user_data["username"],
                email=user_data.get("email", ""),
                password=user_data["password"],
                role=user_data.get("role", "user"),
            )

        # Set additional permissions
        if user_data.get("is_staff"):
            user.is_staff = True
        if user_data.get("is_superuser"):
            user.is_superuser = True
        user.save()

        # Perform login and get tokens
        login_url = reverse("login")
        response = api_client.post(
            login_url,
            {
                "username": user_data["username"],
                "password": user_data["password"],
            },
            format="json",
        )

        if response.status_code == 200:
            access_token = response.data["access"]
            api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        return user

    @staticmethod
    def assert_user_response_valid(response, expected_status=200):
        """
        Validate user API response.

        Args:
            response: API response to validate
            expected_status: Expected HTTP status code
        """
        assert response.status_code == expected_status
        if expected_status == 200:
            if "access" in response.data:
                assert "access" in response.data
                assert "refresh" in response.data
            else:
                assert "id" in response.data
                assert "username" in response.data

    @staticmethod
    def get_auth_tokens(response):
        """
        Extract authentication tokens from response.

        Args:
            response: API response containing tokens

        Returns:
            tuple: (access_token, refresh_token)
        """
        assert "access" in response.data
        assert "refresh" in response.data
        return response.data["access"], response.data["refresh"]

    @pytest.fixture
    def authenticated_client(self):
        """
        Fixture providing an authenticated API client.

        Returns:
            APIClient: Authenticated client instance
        """
        client = APIClient()
        user_data = TEST_USER_DATA["valid_user"].copy()
        self.create_and_authenticate_user(client, user_data)
        return client

    @staticmethod
    def authenticate_user(api_client, credentials):
        """
        Authenticate a user with given credentials.

        Args:
            api_client: API client instance
            credentials: User credentials

        Returns:
            Response: Authentication response
        """
        response = api_client.post(reverse("login"), credentials, format="json")
        if response.status_code == 200:
            api_client.credentials(
                HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}'
            )
        return response

    @staticmethod
    def create_test_user(role="user", **kwargs):
        """
        Create a test user with given role and attributes.

        Args:
            role: User role
            **kwargs: Additional user attributes

        Returns:
            User: Created test user
        """
        user_data = {
            "username": f"test_{role}",
            "email": f"test_{role}@example.com",
            "password": "testpass123",
            "role": role,
            **kwargs,
        }
        return User.objects.create_user(**user_data)
