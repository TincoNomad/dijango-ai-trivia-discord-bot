"""
Trivia Query Test Module

This module contains test cases for:
- Trivia listing operations
- Filter functionality
- Query validation
- Response format verification
"""

import pytest
from django.urls import reverse
from .test_trivia_base import TestTriviaBase

@pytest.mark.django_db
class TestTriviaQueries(TestTriviaBase):
    """Test cases for trivia query operations"""

    @pytest.fixture(autouse=True)
    def setup_method(self, test_theme):
        """Set up test environment"""
        self.theme = test_theme

    @staticmethod
    def assert_filter_response_valid(response):
        """
        Validate filter response format.
        
        Args:
            response: API response to validate
        """
        assert response.status_code == 200
        assert isinstance(response.data, list)
        for trivia in response.data:
            TestTriviaQueries.assert_trivia_structure_valid(trivia)

    @staticmethod
    def assert_trivia_structure_valid(trivia_data):
        """
        Validate trivia data structure.
        
        Args:
            trivia_data: Trivia data to validate
        """
        required_fields = ['id', 'title', 'difficulty', 'theme', 'is_public']
        for field in required_fields:
            assert field in trivia_data

    def test_list_public_trivias(self, api_client, test_user):
        """Test listing of public trivias"""
        response = api_client.get(reverse('trivia-list'))
        assert response.status_code == 200

    def test_filter_trivias_by_theme(self, api_client):
        """Test filtering trivias by theme and difficulty"""
        url = reverse('trivia-filter-trivias')
        response = api_client.get(f"{url}?theme={self.theme.id}&difficulty=1")
        self.assert_filter_response_valid(response)

    def test_get_questions_invalid_trivia(self, api_client):
        """Test retrieving questions with invalid trivia ID"""
        url = reverse('trivia-get-trivia')
        response = api_client.get(f"{url}?id=invalid-uuid")
        assert response.status_code == 400
        assert "Invalid UUID format" in str(response.data['error'])

    def test_get_questions_valid_trivia(self, api_client, trivia_with_questions):
        """Test retrieving questions for valid trivia"""
        url = reverse('trivia-get-trivia')
        response = api_client.get(f"{url}?id={trivia_with_questions.id}")
        assert response.status_code == 200
        assert len(response.data['questions']) > 0
