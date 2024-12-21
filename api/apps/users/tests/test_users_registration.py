"""
Test suite for user registration functionality.

This module contains test cases for:
- User registration
- Email validation
- Registration error handling
"""

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from .test_data import TEST_USER_DATA, ERROR_MESSAGES

User = get_user_model()

@pytest.mark.django_db
class TestUserRegistration:
    """Test cases for user registration process"""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up test environment before each test"""
        self.url = reverse('register')
        self.valid_data = {
            'username': TEST_USER_DATA['new_user']['username'],
            'email': TEST_USER_DATA['new_user']['email'],
            'password': TEST_USER_DATA['new_user']['password'],
            'role': 'admin'
        }

    def teardown_method(self):
        """Clean up after each test"""
        User.objects.filter(username=self.valid_data['username']).delete()

    def test_successful_registration(self, api_client):
        """
        Test successful user registration.
        Should create user and return 201.
        """
        response = api_client.post(self.url, self.valid_data, format='json')
        
        assert response.status_code == 201, "El registro debería ser exitoso"
        user = User.objects.get(username=self.valid_data['username'])
        assert user.email == self.valid_data['email'], "El email no coincide"
        assert user.check_password(self.valid_data['password']), "La contraseña no fue guardada correctamente"

    @pytest.mark.parametrize("invalid_email", [
        "not-an-email",
        "@no-username.com",
        "spaces in@email.com",
        "missing.domain@"
    ])
    def test_invalid_email_registration(self, api_client, invalid_email):
        """
        Test registration with invalid email formats.
        Should return 400 with email validation error.
        """
        data = self.valid_data.copy()
        data['email'] = invalid_email
        response = api_client.post(self.url, data, format='json')
        
        assert response.status_code == 400
        assert 'email' in response.data
        assert ERROR_MESSAGES['INVALID_EMAIL'] in str(response.data['email'])