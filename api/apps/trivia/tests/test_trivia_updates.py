"""Tests for trivia update operations."""
import pytest
from django.urls import reverse
from .test_trivia_base import TestTriviaBase
from .factories import TriviaFactory
from .test_data import TEST_TRIVIA_DATA
from api.apps.trivia.models import Trivia

@pytest.mark.django_db(transaction=True)
class TestTriviaUpdates(TestTriviaBase):
    """Test cases for trivia update operations."""

    @pytest.fixture(autouse=True)
    def setup_method(self, test_user, test_theme):
        """Initial setup for each test."""
        test_user.role = 'admin'
        test_user.is_authenticated = True
        test_user.save()
        
        self.theme = test_theme
        self.trivia = Trivia.objects.create(
            title='Test Trivia',
            difficulty=1,
            theme=test_theme,
            created_by=test_user,
            is_public=True
        )
        self.url = reverse('trivia-detail', args=[self.trivia.id])

    def test_trivia_update_should_succeed_when_user_is_authenticated_and_owner(self, api_client_authenticated):
        """Test successful trivia update by owner."""
        data = {'title': 'Updated Title'}
        response = api_client_authenticated.patch(self.url, data, format='json')
        assert response.status_code == 200
        assert response.data['title'] == 'Updated Title'

    def test_update_trivia_unauthorized(self, api_client):
        """Test trivia update without authentication."""
        response = api_client.patch(self.url, {'title': 'New Title'}, format='json')
        assert response.status_code == 401

    def test_update_trivia_by_non_creator(self, api_client_authenticated, test_user):
        """Test trivia update by non-creator."""
        other_trivia = TriviaFactory()  # Created by different user
        url = reverse('trivia-detail', kwargs={'pk': other_trivia.id})
        response = api_client_authenticated.patch(url, {'title': 'New Title'}, format='json')
        assert response.status_code == 403

    def test_update_trivia_questions(self, api_client, test_user):
        """Test updating trivia questions"""
        # Create initial question with answers
        question = self.create_question_with_answers(self.trivia)
        
        # Authenticate user
        api_client.force_authenticate(user=test_user)
        
        # Update question data
        questions_data = TEST_TRIVIA_DATA['update_data']['questions'].copy()
        questions_data['questions'][0]['id'] = str(question.id)
        
        url = reverse('trivia-update-questions', args=[self.trivia.id])
        response = api_client.patch(url, questions_data, format='json')
        
        assert response.status_code == 200
        question.refresh_from_db()
        assert question.question_title == 'Updated Question'
