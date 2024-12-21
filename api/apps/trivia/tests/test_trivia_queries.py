"""
Trivia Query Test Module

This module contains test cases for:
- Trivia listing operations (GET /api/trivias/)
- Trivia detail retrieval (GET /api/trivias/{id}/)
- Questions retrieval (GET /api/questions/{id}/)
- Filter functionality
- Response format verification
"""

import pytest
from django.urls import reverse
from .test_trivia_base import TestTriviaBase
from .factories import TriviaFactory, QuestionFactory, AnswerFactory, UserFactory

@pytest.mark.django_db
class TestTriviaQueries(TestTriviaBase):
    """Test cases for trivia query operations"""

    @pytest.fixture(autouse=True)
    def setup_method(self, test_theme):
        """Set up test environment"""
        self.theme = test_theme

    def test_list_trivias(self, api_client, test_user):
        """Test GET /api/trivias/ endpoint"""
        # Create test trivia
        trivia = TriviaFactory.create(theme=self.theme, created_by=test_user)
        
        # Get trivia list
        url = reverse('trivia-list')
        response = api_client.get(url)
        
        # Verify response
        assert response.status_code == 200
        assert isinstance(response.data, list)
        trivia_data = next(t for t in response.data if t['id'] == str(trivia.id))
        
        # Verify basic fields
        assert 'title' in trivia_data
        assert 'difficulty' in trivia_data
        assert 'theme' in trivia_data
        assert 'created_by' in trivia_data
        # Verify questions not included in list view
        assert 'questions' not in trivia_data

    def test_get_trivia_detail(self, api_client, test_user):
        """Test GET /api/trivias/{id}/ endpoint"""
        # Create trivia with questions
        trivia = TriviaFactory.create(theme=self.theme, created_by=test_user)
        question = QuestionFactory.create(trivia=trivia)
        AnswerFactory.create_batch(2, question=question)
        
        # Get trivia detail
        url = reverse('trivia-detail', args=[trivia.id])
        response = api_client.get(url)
        
        # Verify response
        assert response.status_code == 200
        assert response.data['id'] == str(trivia.id)
        assert 'title' in response.data
        assert 'difficulty' in response.data
        assert 'theme' in response.data
        assert 'created_by' in response.data
        assert 'created_at' in response.data
        # Verify questions included in detail view
        assert 'questions' in response.data
        assert len(response.data['questions']) > 0
        assert 'answers' in response.data['questions'][0]

    def test_get_trivia_questions(self, api_client, test_user):
        """Test GET /api/questions/{id}/ endpoint"""
        # Create trivia with questions
        trivia = TriviaFactory.create(theme=self.theme, created_by=test_user)
        question = QuestionFactory.create(trivia=trivia)
        AnswerFactory.create_batch(2, question=question)
        
        # Get questions
        url = reverse('get-questions', args=[trivia.id])
        response = api_client.get(url)
        
        # Verify response
        assert response.status_code == 200
        assert isinstance(response.data, list)
        assert len(response.data) > 0
        # Verify question fields
        question_data = response.data[0]
        assert 'question_title' in question_data
        assert 'points' in question_data
        assert 'answers' in question_data
        # Verify answer fields
        assert len(question_data['answers']) >= 2
        assert 'answer_title' in question_data['answers'][0]
        assert 'is_correct' in question_data['answers'][0]

    def test_get_questions_invalid_trivia(self, api_client):
        """Test retrieving questions with invalid trivia ID"""
        url = reverse('get-questions', args=['invalid-uuid'])
        response = api_client.get(url)
        assert response.status_code == 400
        assert "Invalid UUID format" in str(response.data['error'])

    def test_get_questions_nonexistent_trivia(self, api_client):
        """Test retrieving questions for non-existent trivia"""
        import uuid
        url = reverse('get-questions', args=[str(uuid.uuid4())])
        response = api_client.get(url)
        assert response.status_code == 404
        assert "Trivia not found" in str(response.data['error'])

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

    def test_list_trivias_by_username(self, api_client, test_user):
        """Test GET /api/trivias/?username=<username> endpoint"""
        # Create test trivias with different users
        trivia1 = TriviaFactory.create(theme=self.theme, created_by=test_user)
        other_user = UserFactory.create(username='other_user')
        trivia2 = TriviaFactory.create(theme=self.theme, created_by=other_user)
        
        # Get trivias for test_user
        url = reverse('trivia-list')
        response = api_client.get(f"{url}?username={test_user.username}")
        
        # Verify response
        assert response.status_code == 200
        assert isinstance(response.data, list)
        
        # Should only include trivias from test_user
        trivia_ids = [t['id'] for t in response.data]
        assert str(trivia1.id) in trivia_ids
        assert str(trivia2.id) not in trivia_ids
        
        # Verify each trivia has basic fields
        for trivia in response.data:
            assert 'title' in trivia
            assert 'difficulty' in trivia
            assert 'theme' in trivia
            assert 'created_by' in trivia
            assert 'questions' not in trivia  # List view shouldn't include questions

    def test_list_trivias_nonexistent_username(self, api_client):
        """Test trivia listing with non-existent username"""
        url = reverse('trivia-list')
        response = api_client.get(f"{url}?username=nonexistent_user")
        assert response.status_code == 404
        assert "No user found with username" in str(response.data['error'])
