"""
Trivia Test Base Module

This module provides base test functionality for trivia-related tests.
Includes:
- Common test fixtures
- Helper methods
- Assertion utilities
"""

import pytest
from api.apps.trivia.tests.factories import QuestionFactory, AnswerFactory
from api.apps.trivia.models import Trivia

@pytest.mark.django_db
class TestTriviaBase:
    """
    Base test class for trivia tests.
    
    Provides common functionality for:
    - Question creation
    - Data validation
    - Test cleanup
    """
    
    def create_question_with_answers(self, trivia):
        """
        Create a question with default answers.
        
        Args:
            trivia: Trivia instance to associate with
            
        Returns:
            Question: Created question with answers
        """
        question = QuestionFactory(trivia=trivia)
        AnswerFactory.create_batch(2, question=question)
        return question

    @staticmethod
    def assert_trivia_matches_input(trivia, input_data):
        """
        Validate trivia data against input.
        
        Args:
            trivia: Trivia instance to validate
            input_data: Expected data dictionary
        """
        assert trivia.title == input_data['title']
        assert trivia.difficulty == input_data['difficulty']
        assert trivia.theme.name == input_data['theme']
        assert trivia.questions.count() == len(input_data['questions'])

    @staticmethod
    def assert_trivia_update_successful(trivia, update_data):
        """
        Validate trivia update was successful.
        
        Args:
            trivia: Updated trivia instance
            update_data: Expected update data
        """
        for field, value in update_data.items():
            if field != 'username':  # Skip username as it's not a direct field
                assert getattr(trivia, field) == value, \
                    f"Field {field} was not updated correctly"

    @pytest.fixture(autouse=True)
    def teardown_method(self):
        """Clean up test data after each test"""
        yield
        Trivia.objects.all().delete()
