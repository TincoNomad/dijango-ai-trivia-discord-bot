"""Tests for user credentials management."""

import pytest
from django.urls import reverse
from .test_users_base import BaseUserTest

@pytest.mark.django_db
class TestUserCredentials(BaseUserTest):
    """Test cases for user credentials management"""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup para cada test"""
        self.credentials_url = reverse('update-credentials')

    def test_successful_credentials_update(self, api_client):
        """Test actualización exitosa de credenciales"""
        # Crear usuario sin credenciales
        user = self.create_and_authenticate_user(
            api_client,
            {'username': 'testuser', 'password': '', 'email': ''}
        )
        
        # Actualizar credenciales
        new_credentials = {
            'username': user.username,
            'email': 'new@example.com',
            'password': 'newpassword123'
        }
        
        response = api_client.post(
            self.credentials_url,
            new_credentials,
            format='json'
        )
        
        assert response.status_code == 200
        access_token, refresh_token = self.get_auth_tokens(response)
        assert access_token and refresh_token 