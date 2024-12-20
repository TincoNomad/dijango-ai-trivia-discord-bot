"""Tests for user permissions."""

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
class TestUserPermissions:
    """Test cases for user permissions"""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup para cada test"""
        self.users_url = reverse('user-list')
        self.valid_credentials = TEST_USER_DATA['valid_user'].copy()

    @pytest.fixture
    def admin_user(self):
        """Fixture que crea un usuario admin"""
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

    def test_admin_access(self, api_client, admin_user):
        """Test acceso de administrador"""
        # Login
        response = api_client.post(
            reverse('login'),
            self.valid_credentials,
            format='json'
        )
        
        api_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}'
        )
        
        # Verificar acceso
        me_response = api_client.get('/api/users/')  # Usar la URL completa como en el test anterior
        assert me_response.status_code == 200

    def test_regular_user_restricted_access(self, api_client):
        """Test restricción de acceso para usuario regular"""
        # Crear usuario regular
        user_data = self.valid_credentials.copy()
        user_data['role'] = 'user'
        User.objects.create_user(**user_data)
        
        # Login
        login_response = api_client.post(
            reverse('login'),
            user_data,
            format='json'
        )
        
        api_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {login_response.data["access"]}'
        )
        
        # Verificar restricción
        response = api_client.post(self.users_url, {})
        assert response.status_code == 403