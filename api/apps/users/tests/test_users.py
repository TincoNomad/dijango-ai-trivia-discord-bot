"""
Test suite for the users app.

This module contains test cases for user-related functionality including:
- User registration
- Authentication (login/logout)
- Credential management

Each test class includes setup and teardown methods, and uses
parameterized testing where appropriate.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse
from .test_data import TEST_USER_DATA, ERROR_MESSAGES

User = get_user_model()

@pytest.fixture
def api_client():
    """
    Fixture that provides a DRF API client for testing endpoints.
    Returns:
        APIClient: A test client for making API requests
    """
    return APIClient()

@pytest.fixture
def test_user():
    """
    Fixture that creates a test user in the database.
    """
    user = User.objects.create_user(
        username=TEST_USER_DATA['valid_user']['username'],
        email=TEST_USER_DATA['valid_user']['email'],
        password=TEST_USER_DATA['valid_user']['password'],
        role='admin'
    )
    user.is_authenticated = True
    user.save()
    return user

@pytest.mark.django_db
class TestUserRegistration:
    """Test cases for user registration functionality"""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup method run before each test"""
        self.url = reverse('register')
        # Ensure correct data is sent for registration
        self.valid_data = {
            'username': TEST_USER_DATA['new_user']['username'],
            'email': TEST_USER_DATA['new_user']['email'],
            'password': TEST_USER_DATA['new_user']['password'],
            'role': 'admin'  # Ensure role is included
        }

    def teardown_method(self):
        """Cleanup after each test"""
        User.objects.filter(username=self.valid_data['username']).delete()

    def test_successful_registration(self, api_client):
        """Test successful user registration"""
        print("\nTest data:", self.valid_data)
        
        response = api_client.post(self.url, self.valid_data, format='json')
        print("Response:", response.status_code)
        print("Response data:", response.data)
        
        user = User.objects.get(username=self.valid_data['username'])
        print("User password:", user.password)
        print("User data:", {
            'username': user.username,
            'email': user.email,
            'is_authenticated': user.is_authenticated,
            'has_usable_password': user.has_usable_password()
        })
        
        assert response.status_code == 201
        assert user.email == self.valid_data['email']
        assert user.check_password(self.valid_data['password'])
    
    @pytest.mark.parametrize("invalid_email", [
        "not-an-email",
        "@no-username.com",
        "spaces in@email.com",
        "missing.domain@"
    ])
    def test_invalid_email_registration(self, api_client, invalid_email):
        """
        Test registration with various invalid email formats.
        Should return 400 status code with email error.
        """
        data = self.valid_data.copy()
        data['email'] = invalid_email
        response = api_client.post(self.url, data, format='json')
        
        assert response.status_code == 400
        assert 'email' in response.data
        assert ERROR_MESSAGES['INVALID_EMAIL'] in str(response.data['email'])

@pytest.mark.django_db
class TestUserLogin:
    """Test cases for user login functionality"""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup method run before each test"""
        self.url = reverse('login')
        self.valid_credentials = {
            'username': TEST_USER_DATA['valid_user']['username'],
            'password': TEST_USER_DATA['valid_user']['password']
        }

    def test_successful_login(self, api_client, test_user):
        """Test successful login with valid credentials"""
        response = api_client.post(self.url, self.valid_credentials, format='json')
        
        assert response.status_code == 200
        assert 'access' in response.data
        assert 'refresh' in response.data
        
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')
        me_response = api_client.get('/api/users/')  # Usar la URL del viewset
        assert me_response.status_code == 200

    def test_login_with_empty_credentials(self, api_client):
        """Test login with empty credentials"""
        response = api_client.post(self.url, {}, format='json')
        assert response.status_code == 400
        assert ERROR_MESSAGES['PASSWORD_REQUIRED'] in str(response.data)

@pytest.mark.django_db
class TestUserLogout:
    """Test cases for user logout functionality"""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup method run before each test"""
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.valid_credentials = {
            'username': TEST_USER_DATA['valid_user']['username'],
            'password': TEST_USER_DATA['valid_user']['password']
        }

    def test_successful_logout(self, api_client, test_user):
        """Test successful logout"""
        # Login primero
        login_response = api_client.post(
            self.login_url,
            self.valid_credentials,
            format='json'
        )
        
        access_token = login_response.data['access']
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        response = api_client.post(self.logout_url)
        assert response.status_code == 205

@pytest.mark.django_db
class TestCredentialsUpdate:
    """Test cases for user credentials update functionality"""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup method run before each test"""
        self.url = reverse('update-credentials')
        self.new_credentials = {
            'username': 'newuser',
            'email': 'newemail@example.com',
            'password': 'newpassword123'
        }

    def test_successful_credentials_update(self, api_client):
        """
        Test successful credentials update for a new user.
        Should return 200 status code and update user data.
        """
        # Create user without credentials
        user = User.objects.create_user(
            username=self.new_credentials['username'],
            email='',
            password=''
        )
        
        response = api_client.post(self.url, self.new_credentials, format='json')
        
        assert response.status_code == 200
        user.refresh_from_db()
        assert user.email == self.new_credentials['email']
        assert user.check_password(self.new_credentials['password'])
