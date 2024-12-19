"""Tests for trivia update operations."""
import pytest
from django.urls import reverse
from .test_trivia_base import TestTriviaBase
from .factories import TriviaFactory, UserFactory
from .test_data import TEST_TRIVIA_DATA, ERROR_MESSAGES

@pytest.mark.django_db
class TestTriviaUpdates(TestTriviaBase):
    """Test cases for trivia update operations."""

    @pytest.fixture(autouse=True)
    def setup_method(self, test_user, test_theme):
        """Initial setup for each test."""
        self.user = test_user
        self.theme = test_theme
        # Crear trivia explícitamente con el usuario de prueba
        self.trivia = TriviaFactory.create(
            created_by=test_user,
            theme=test_theme
        )
        self.url = reverse('trivia-detail', args=[self.trivia.id])
        self.update_data = TEST_TRIVIA_DATA['update_data']['basic'].copy()
        self.update_data['username'] = test_user.username

    def test_trivia_update_should_succeed_when_user_is_authenticated_and_owner(
            self, api_client, test_user):
        """Test that trivia title can be updated by authenticated owner"""
        trivia = TriviaFactory.create_with_questions(created_by=test_user)
        url = reverse('trivia-detail', args=[trivia.id])
        
        api_client.force_authenticate(user=test_user)
        update_data = TEST_TRIVIA_DATA['update_data']['basic'].copy()
        update_data['username'] = test_user.username
        
        response = api_client.patch(url, update_data, format='json')
        assert response.status_code == 200, "Update should succeed"
        trivia.refresh_from_db()
        assert trivia.title == update_data['title'], "Title should be updated"

    def test_update_trivia_by_non_creator(self, api_client, test_user):
        """Test updating trivia by non-creator fails"""
        other_user = UserFactory.create_other_user()
        api_client.force_authenticate(user=other_user)
        
        response = api_client.patch(self.url, self.update_data, format='json')
        assert response.status_code == 403
        assert ERROR_MESSAGES['FORBIDDEN'] in str(response.data)

    def test_update_trivia_unauthorized(self, api_client):
        """Test trivia update without authentication."""
        response = api_client.patch(self.url, {'title': 'New Title'}, format='json')
        assert response.status_code == 401

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
