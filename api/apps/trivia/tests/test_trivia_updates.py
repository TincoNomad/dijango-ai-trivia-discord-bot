"""
Trivia Update Test Module

This module contains test cases for:
- Trivia data updates
- Question modifications
- Permission validation
- Update constraints
"""

import pytest
from django.urls import reverse

from api.apps.trivia.models import Trivia

from .factories import UserFactory
from .test_data import ERROR_MESSAGES, TEST_TRIVIA_DATA
from .test_trivia_base import TestTriviaBase


@pytest.mark.django_db
class TestTriviaUpdates(TestTriviaBase):
    """Test cases for trivia update operations"""

    @pytest.fixture(autouse=True)
    def setup_method(self, test_user, test_theme):
        """Set up test environment"""
        # Configure admin user
        test_user.role = "admin"
        test_user.is_authenticated = True
        test_user.save()

        # Create trivia directly with user
        self.theme = test_theme
        self.trivia = Trivia.objects.create(
            title="Test Trivia",
            difficulty=1,
            theme=test_theme,
            created_by=test_user,
            is_public=True,
        )
        self.url = reverse("trivia-detail", args=[self.trivia.id])
        self.update_data = TEST_TRIVIA_DATA["update_data"]["basic"].copy()
        self.update_data["username"] = test_user.username

    def test_trivia_update_should_succeed_when_user_is_authenticated_and_owner(
        self, api_client, test_user
    ):
        """Test successful trivia update by authenticated owner"""
        api_client.force_authenticate(user=test_user)
        update_data = TEST_TRIVIA_DATA["update_data"]["basic"].copy()
        update_data["username"] = test_user.username

        response = api_client.patch(self.url, update_data, format="json")
        assert response.status_code == 200
        self.trivia.refresh_from_db()
        assert self.trivia.title == update_data["title"]

    def test_update_trivia_by_non_creator(self, api_client, test_user):
        """Test update restriction for non-creator users"""
        other_user = UserFactory.create_other_user()
        api_client.force_authenticate(user=other_user)

        response = api_client.patch(self.url, self.update_data, format="json")
        assert response.status_code == 403
        assert ERROR_MESSAGES["FORBIDDEN"] in str(response.data)

    def test_update_trivia_unauthorized(self, api_client):
        """Test update restriction for unauthenticated users"""
        response = api_client.patch(self.url, {"title": "New Title"}, format="json")
        assert response.status_code == 401

    def test_update_trivia_questions(self, api_client, test_user):
        """Test question update functionality"""
        # Create initial question with answers
        question = self.create_question_with_answers(self.trivia)

        # Authenticate user
        api_client.force_authenticate(user=test_user)

        # Update question data
        questions_data = TEST_TRIVIA_DATA["update_data"]["questions"].copy()
        questions_data["questions"][0]["id"] = str(question.id)

        url = reverse("trivia-update-questions", args=[self.trivia.id])
        response = api_client.patch(url, questions_data, format="json")

        assert response.status_code == 200
        question.refresh_from_db()
        assert question.question_title == "Updated Question"
