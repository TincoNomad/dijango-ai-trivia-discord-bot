"""
Test suite for user permissions and access control.

This module contains test cases for:
- Admin access rights
- Regular user restrictions
- Role-based access control
"""

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from .test_data import TEST_USER_DATA

User = get_user_model()

@pytest.mark.django_db
class TestUserPermissions:
    """Test cases for user permissions and access control"""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up test environment before each test"""
        self.users_url = reverse('user-list')
        self.valid_credentials = TEST_USER_DATA['valid_user'].copy()

    @pytest.fixture
    def admin_user(self):
        """Create an admin user with full privileges"""
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
        """
        Test admin user access rights.
        Should allow full access to admin endpoints.
        """
        # Login as admin
        response = api_client.post(
            reverse('login'),
            self.valid_credentials,
            format='json'
        )
        
        api_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}'
        )
        
        # Verify admin access
        me_response = api_client.get('/api/users/')
        assert me_response.status_code == 200

    def test_regular_user_restricted_access(self, api_client):
        """
        Test regular user access restrictions.
        Should prevent access to admin-only endpoints.
        """
        # Create regular user
        user_data = self.valid_credentials.copy()
        user_data['role'] = 'user'
        User.objects.create_user(**user_data)
        
        # Login as regular user
        login_response = api_client.post(
            reverse('login'),
            user_data,
            format='json'
        )
        
        api_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {login_response.data["access"]}'
        )
        
        # Verify access restriction
        response = api_client.post(self.users_url, {})
        assert response.status_code == 403