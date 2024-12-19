"""
Test suite for the trivia app.
Contains base test class with common helper methods.
"""

import pytest
from api.apps.trivia.tests.factories import QuestionFactory, AnswerFactory
from api.apps.trivia.models import Trivia

@pytest.mark.django_db
class TestTriviaBase:
    """Base class for trivia tests with common helper methods"""
    
    def create_question_with_answers(self, trivia):
        """Helper method to create question with answers using factories"""
        question = QuestionFactory(trivia=trivia)
        AnswerFactory.create_batch(2, question=question)
        return question

    @staticmethod
    def assert_trivia_matches_input(trivia, input_data):
        """Helper method to validate trivia data matches input"""
        assert trivia.title == input_data['title']
        assert trivia.difficulty == input_data['difficulty']
        assert trivia.theme.name == input_data['theme']
        assert trivia.questions.count() == len(input_data['questions'])

    @staticmethod
    def assert_trivia_update_successful(trivia, update_data):
        """Helper method to validate trivia update was successful"""
        for field, value in update_data.items():
            if field != 'username':  # Skip username as it's not a direct field
                assert getattr(trivia, field) == value, \
                    f"Field {field} was not updated correctly"

    @pytest.fixture(autouse=True)
    def teardown_method(self):
        """Cleanup after each test"""
        yield
        Trivia.objects.all().delete()
