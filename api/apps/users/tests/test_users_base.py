"""
Base test class for user-related tests.
Contains common functionality and helper methods.
"""

import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from .test_data import TEST_USER_DATA

User = get_user_model()

@pytest.mark.django_db
class BaseUserTest:
    """Clase base para tests de usuarios"""
    
    @pytest.fixture(autouse=True)
    def setup_base(self):
        """Setup básico para todos los tests"""
        self.api_client = APIClient()

    @staticmethod
    def create_and_authenticate_user(api_client, user_data):
        """Helper para crear y autenticar usuario"""
        # Crear usuario usando create_superuser si es admin
        if user_data.get('role') == 'admin' or user_data.get('is_superuser'):
            user = User.objects.create_superuser(
                username=user_data['username'],
                email=user_data.get('email', ''),
                password=user_data['password'],
                role='admin'
            )
        else:
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data.get('email', ''),
                password=user_data['password'],
                role=user_data.get('role', 'user')
            )

        # Asignar permisos adicionales si es necesario
        if user_data.get('is_staff'):
            user.is_staff = True
        if user_data.get('is_superuser'):
            user.is_superuser = True
        user.save()

        # Realizar login para obtener tokens
        login_url = reverse('login')
        response = api_client.post(
            login_url,
            {
                'username': user_data['username'],
                'password': user_data['password']
            },
            format='json'
        )

        if response.status_code == 200:
            access_token = response.data['access']
            api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        return user

    @staticmethod
    def assert_user_response_valid(response, expected_status=200):
        """Validar respuesta de usuario"""
        assert response.status_code == expected_status
        if expected_status == 200:
            if 'access' in response.data:
                assert 'access' in response.data
                assert 'refresh' in response.data
            else:
                assert 'id' in response.data
                assert 'username' in response.data

    @staticmethod
    def get_auth_tokens(response):
        """Extraer tokens de autenticación"""
        assert 'access' in response.data
        assert 'refresh' in response.data
        return response.data['access'], response.data['refresh']

    @pytest.fixture
    def authenticated_client(self):
        """Fixture para obtener un cliente autenticado"""
        client = APIClient()
        user_data = TEST_USER_DATA['valid_user'].copy()
        self.create_and_authenticate_user(client, user_data)
        return client
