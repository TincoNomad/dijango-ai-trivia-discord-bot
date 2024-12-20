"""Tests for user authentication."""

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from .test_data import TEST_USER_DATA
from rest_framework.test import APIClient

User = get_user_model()

@pytest.fixture
def api_client():
    """
    Fixture that provides a DRF API client for testing endpoints.
    Returns:
        APIClient: A test client for making API requests
    """
    return APIClient()

@pytest.mark.django_db
class TestUserAuthentication:
    """Test cases for user authentication"""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup para cada test"""
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.valid_credentials = TEST_USER_DATA['valid_user'].copy()

    @pytest.fixture
    def test_user(self):
        """Fixture que crea un usuario de prueba"""
        user = User.objects.create_user(
            username=self.valid_credentials['username'],
            email=self.valid_credentials['email'],
            password=self.valid_credentials['password'],
            role='admin'
        )
        user.is_staff = True
        user.is_superuser = True
        user.is_authenticated = True
        user.save()
        return user

    def test_successful_login(self, api_client, test_user):
        """Test login exitoso"""
        response = api_client.post(
            self.login_url,
            self.valid_credentials,
            format='json'
        )
        
        assert response.status_code == 200
        assert 'access' in response.data
        assert 'refresh' in response.data
        
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')
        me_response = api_client.get('/api/users/')
        assert me_response.status_code == 200

    def test_successful_logout(self, api_client, test_user):
        """Test logout exitoso"""
        # Login primero
        login_response = api_client.post(
            self.login_url,
            self.valid_credentials,
            format='json'
        )
        
        access_token = login_response.data['access']
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Logout
        response = api_client.post(self.logout_url)
        assert response.status_code == 205

    def test_login_with_empty_credentials(self, api_client):
        """Test login con credenciales vacías"""
        response = api_client.post(self.login_url, {}, format='json')
        assert response.status_code == 400
        # Verificar que ambos campos son requeridos
        assert 'username' in response.data
        assert 'password' in response.data
        assert 'This field is required.' in str(response.data['username'])
        assert 'This field is required.' in str(response.data['password'])