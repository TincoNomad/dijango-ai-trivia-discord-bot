"""
Trivia Creation Test Module

This module contains test cases for:
- Basic trivia creation
- Validation handling
- Error scenarios
- Constraint checking
"""

import pytest
from django.urls import reverse

from .factories import TriviaFactory
from .test_data import ERROR_MESSAGES, TEST_TRIVIA_DATA
from .test_trivia_base import TestTriviaBase


@pytest.mark.django_db
class TestTriviaCreation(TestTriviaBase):
    """Test cases for trivia creation functionality"""

    @pytest.fixture(autouse=True)
    def setup_method(self, test_user, test_theme):
        """Set up test environment"""
        self.url = reverse("trivia-list")
        self.valid_data = TEST_TRIVIA_DATA["valid_trivia"].copy()
        self.valid_data["theme"] = test_theme.id
        self.valid_data["username"] = test_user.username
        self.user = test_user
        self.theme = test_theme

    def test_trivia_creation_should_succeed_with_valid_data(
        self, api_client_authenticated
    ):
        """Test successful trivia creation with valid data"""
        response = api_client_authenticated.post(
            self.url, self.valid_data, format="json"
        )
        assert response.status_code == 201

    def test_trivia_creation_should_fail_with_duplicate_title(
        self, api_client_authenticated, test_user
    ):
        """Test duplicate title validation"""
        # Create first trivia
        trivia = TriviaFactory.create(created_by=test_user)

        # Attempt to create trivia with same title
        duplicate_data = self.valid_data.copy()
        duplicate_data.update({"title": trivia.title, "username": test_user.username})

        response = api_client_authenticated.post(
            self.url, duplicate_data, format="json"
        )
        assert response.status_code == 400
        assert ERROR_MESSAGES["DUPLICATE_TITLE"] in str(response.data)

    def test_trivia_creation_should_fail_when_user_not_authenticated(self, api_client):
        """
        Test that unauthenticated users cannot create trivia.
        """
        api_client.credentials()
        api_client.force_authenticate(user=None)

        invalid_data = self.valid_data.copy()
        invalid_data["username"] = "nonexistent_user"

        response = api_client.post(self.url, invalid_data, format="json")
        assert response.status_code == 400, "Should fail with validation error"
        assert "No user exists with this username" in str(
            response.data
        ), "Should indicate user validation failure"

    def test_create_trivia_invalid_difficulty(self, api_client_authenticated):
        """Test trivia creation with invalid difficulty."""
        data = self.valid_data.copy()
        data["difficulty"] = 5
        response = api_client_authenticated.post(self.url, data, format="json")
        assert response.status_code == 400
        assert ERROR_MESSAGES["INVALID_DIFFICULTY"] in str(response.data)

    def test_trivia_with_maximum_questions(self, api_client_authenticated):
        """Test creating trivia with maximum allowed questions."""
        data = self.valid_data.copy()
        base_questions = TEST_TRIVIA_DATA["valid_trivia"]["questions"]
        data["questions"] = base_questions * 2  # 6 questions (3 * 2)

        response = api_client_authenticated.post(self.url, data, format="json")
        assert response.status_code == 400
        assert "Maximum 5 questions allowed" in str(response.data)

    def test_trivia_with_minimum_questions(self, api_client_authenticated):
        """Test creating trivia with less than minimum required questions."""
        data = self.valid_data.copy()
        data["questions"] = TEST_TRIVIA_DATA["valid_trivia"]["questions"][:2]

        response = api_client_authenticated.post(self.url, data, format="json")
        assert response.status_code == 400
        assert ERROR_MESSAGES["NO_QUESTIONS"] in str(response.data)

    def test_question_with_maximum_answers(self, api_client_authenticated):
        """Test creating question with maximum allowed answers."""
        data = self.valid_data.copy()
        question = data["questions"][0]
        base_answer = question["answers"][0]
        question["answers"] = [base_answer.copy() for _ in range(6)]

        response = api_client_authenticated.post(self.url, data, format="json")
        assert response.status_code == 400
        assert "can have maximum 5 answers" in str(response.data)
