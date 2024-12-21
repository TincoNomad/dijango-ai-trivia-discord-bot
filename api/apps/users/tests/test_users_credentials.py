"""
Credentials Management Test Module

This module contains test cases for:
- User credential setup
- Password validation
- Email verification
- Authentication status updates
"""

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestUserCredentials:
    """Test cases for user credentials management"""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up test environment before each test"""
        self.url = reverse('update-credentials')
        self.new_credentials = {
            'username': 'newuser',
            'email': 'newemail@example.com',
            'password': 'newpassword123'
        }

    def test_successful_credentials_update(self, api_client):
        """
        Test successful credentials update.
        Should update user data and return 200.
        """
        # Create user without credentials
        user = User.objects.create_user(
            username=self.new_credentials['username'],
            email='',
            password=''
        )
        
        # Update credentials
        response = api_client.post(self.url, self.new_credentials, format='json')
        
        # Verify response and data update
        assert response.status_code == 200
        user.refresh_from_db()
        assert user.email == self.new_credentials['email']
        assert user.check_password(self.new_credentials['password'])