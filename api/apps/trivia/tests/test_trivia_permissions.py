"""Tests for trivia permissions."""
import pytest
from django.urls import reverse
from .factories import TriviaFactory, UserFactory, PrivateTriviaFactory
from .test_trivia_base import TestTriviaBase

@pytest.mark.django_db
class TestTriviaPermissions(TestTriviaBase):
    """Test cases for trivia permissions."""

    @pytest.fixture(autouse=True)
    def setup_method(self, test_user, test_theme):
        """Setup for each test case"""
        self.user = test_user
        self.theme = test_theme

    @pytest.mark.parametrize("is_authenticated, expected_count", [
        (True, 2),    # User authenticated: sees public + own private
        (False, 1)    # User not authenticated: sees only public
    ])
    def test_trivia_visibility_by_authentication(self, api_client, test_user, 
                                               is_authenticated, expected_count):
        """Test visibility of trivias based on authentication status."""
        other_user = UserFactory.create_other_user()
        
        # Crear trivia pública
        TriviaFactory(
            title='Public Trivia',
            created_by=other_user,
            is_public=True,
            theme=self.theme
        )
        
        # Crear trivia privada
        PrivateTriviaFactory(
            title='Private Trivia',
            created_by=test_user,
            theme=self.theme
        )

        if is_authenticated:
            api_client.force_authenticate(user=test_user)

        response = api_client.get(reverse('trivia-list'))
        assert response.status_code == 200
        assert len(response.data) == expected_count
