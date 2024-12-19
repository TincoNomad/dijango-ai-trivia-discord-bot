"""Tests for trivia creation."""
import pytest
from django.urls import reverse
from .test_trivia_base import TestTriviaBase
from .test_data import TEST_TRIVIA_DATA, ERROR_MESSAGES

@pytest.mark.django_db
class TestTriviaCreation(TestTriviaBase):
    """Test cases for trivia creation."""

    @pytest.fixture(autouse=True)
    def setup_method(self, test_user, test_theme):
        """Initial setup for each test."""
        self.url = reverse('trivia-list')
        self.valid_data = TEST_TRIVIA_DATA['valid_trivia'].copy()
        self.user = test_user
        self.theme = test_theme

    def test_trivia_creation_should_succeed_with_valid_data(self, api_client_authenticated):
        """Test successful trivia creation"""
        trivia_data = TEST_TRIVIA_DATA['valid_trivia'].copy()
        trivia_data['theme'] = self.theme.id
        trivia_data['username'] = self.user.username
        
        response = api_client_authenticated.post(self.url, trivia_data, format='json')
        assert response.status_code == 201

    def test_trivia_creation_should_fail_with_duplicate_title(self, api_client_authenticated):
        """Test trivia creation with duplicate title."""
        # Create first trivia
        api_client_authenticated.post(self.url, self.valid_data, format='json')
        # Try to create duplicate
        response = api_client_authenticated.post(self.url, self.valid_data, format='json')
        assert response.status_code == 400
        assert ERROR_MESSAGES['DUPLICATE_TITLE'] in str(response.data)

    def test_create_trivia_invalid_difficulty(self, api_client_authenticated):
        """Test trivia creation with invalid difficulty."""
        data = self.valid_data.copy()
        data['difficulty'] = 5
        response = api_client_authenticated.post(self.url, data, format='json')
        assert response.status_code == 400
        assert ERROR_MESSAGES['INVALID_DIFFICULTY'] in str(response.data)

    def test_trivia_creation_should_fail_when_user_not_authenticated(self, api_client):
        """Test trivia creation without authentication."""
        response = api_client.post(self.url, self.valid_data, format='json')
        assert response.status_code == 401

    def test_trivia_with_maximum_questions(self, api_client_authenticated):
        """Test creating trivia with maximum allowed questions."""
        data = self.valid_data.copy()
        base_questions = TEST_TRIVIA_DATA['valid_trivia']['questions']
        data['questions'] = base_questions * 2  # 6 questions (3 * 2)
        
        response = api_client_authenticated.post(self.url, data, format='json')
        assert response.status_code == 400
        assert "Maximum 5 questions allowed" in str(response.data)

    def test_trivia_with_minimum_questions(self, api_client_authenticated):
        """Test creating trivia with less than minimum required questions."""
        data = self.valid_data.copy()
        data['questions'] = TEST_TRIVIA_DATA['valid_trivia']['questions'][:2]
        
        response = api_client_authenticated.post(self.url, data, format='json')
        assert response.status_code == 400
        assert ERROR_MESSAGES['NO_QUESTIONS'] in str(response.data)

    def test_question_with_maximum_answers(self, api_client_authenticated):
        """Test creating question with maximum allowed answers."""
        data = self.valid_data.copy()
        question = data['questions'][0]
        base_answer = question['answers'][0]
        question['answers'] = [base_answer.copy() for _ in range(6)]
        
        response = api_client_authenticated.post(self.url, data, format='json')
        assert response.status_code == 400
        assert "can have maximum 5 answers" in str(response.data)
