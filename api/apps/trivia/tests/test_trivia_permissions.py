"""Tests for trivia permissions."""
import pytest
from django.urls import reverse
from .test_trivia_base import TestTriviaBase
from .factories import TriviaFactory, UserFactory, PrivateTriviaFactory

@pytest.mark.django_db
class TestTriviaPermissions(TestTriviaBase):
    """Test cases for trivia permissions."""

    @pytest.fixture(autouse=True)
    def setup_method(self, test_user, test_theme):
        """Setup for each test case"""
        self.url = reverse('trivia-list')
        self.user = test_user
        self.theme = test_theme

    @pytest.mark.parametrize("is_authenticated, expected_count", [
        (True, 2),    # User authenticated: sees public + own private
        (False, 1)    # User not authenticated: sees only public
    ])
    def test_trivia_visibility_by_authentication(self, api_client, test_user, 
                                               is_authenticated, expected_count):
        """Test visibility of trivias based on authentication status."""
        
        # Create trivias
        other_user = UserFactory.create_other_user()
        trivias = {
            'public': TriviaFactory(
                title='Public Trivia',
                created_by=other_user,
                is_public=True
            ),
            'private': PrivateTriviaFactory(
                title='Own Private Trivia',
                created_by=test_user,
                is_public=False
            )
        }
        
        if is_authenticated:
            test_user.is_authenticated = True
            test_user.save()
            api_client.force_authenticate(user=test_user)
            
            response = api_client.get(reverse('trivia-list'))

            response_data = {t['title']: t for t in response.data}
            assert trivias['public'].title in response_data, \
                "User authenticated should see the public trivia" 
            assert trivias['private'].title in response_data, \
                "User authenticated should see their private trivia"
            
        else:
            # User not authenticated
            response = api_client.get(reverse('trivia-list'))
            
            # Verify that only sees the public trivia
            response_data = {t['title']: t for t in response.data}
            assert trivias['public'].title in response_data, \
                "User not authenticated should see the public trivia"
            assert trivias['private'].title not in response_data, \
                "User not authenticated should not see private trivias"

        assert response.status_code == 200
        assert len(response.data) == expected_count
