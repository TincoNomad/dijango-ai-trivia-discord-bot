"""
Test Factory Module

This module provides factory classes for test data generation.
Uses Factory Boy to create:
- Users
- Themes
- Trivias
- Questions
- Answers

Features:
- Automated data generation
- Relationship handling
- Test scenario variations
"""

import factory
from django.contrib.auth import get_user_model

from api.apps.trivia.models import Answer, Question, Theme, Trivia

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating test User instances"""

    class Meta:
        model = User
        django_get_or_create = ("username",)
        skip_postgeneration_save = True

    username = factory.Sequence(lambda n: f"testuser{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = "testpass123"
    role = "admin"
    is_authenticated = True
    is_active = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override the _create method to properly handle user creation"""
        manager = cls._get_manager(model_class)
        if "is_authenticated" in kwargs:
            kwargs.pop("is_authenticated")
        return manager.create_user(*args, **kwargs)

    @classmethod
    def create_other_user(cls):
        """Create a different user for testing permissions"""
        return cls.create(
            username="other_user",
            email="other@example.com",
            password="testpass123",
        )


class ThemeFactory(factory.django.DjangoModelFactory):
    """Factory for creating test Theme instances"""

    class Meta:
        model = Theme
        django_get_or_create = ("name",)
        skip_postgeneration_save = True

    name = factory.Sequence(lambda n: f"Theme {n}")


class TriviaFactory(factory.django.DjangoModelFactory):
    """Factory for creating test Trivia instances"""

    class Meta:
        model = Trivia
        skip_postgeneration_save = True

    title = factory.Sequence(lambda n: f"Test Trivia {n}")
    difficulty = 1
    theme = factory.SubFactory(ThemeFactory)
    created_by = factory.SubFactory(UserFactory)
    is_public = True

    @classmethod
    def create_with_questions(cls, **kwargs):
        """Create a trivia with default questions"""
        trivia = cls.create(**kwargs)
        question = QuestionFactory(trivia=trivia)
        AnswerFactory.create_batch(2, question=question)
        return trivia

    @factory.post_generation
    def questions(self, create, extracted, **kwargs):
        """
        Create questions and answers for the trivia.

        Args:
            create: Bool indicating if object should be created
            extracted: Optional list of question data
            kwargs: Additional arguments
        """
        if not create:
            return

        if extracted:
            for question_data in extracted:
                question = QuestionFactory(trivia=self)
                for answer_data in question_data.get("answers", []):
                    AnswerFactory(question=question, **answer_data)

    @classmethod
    def create_with_specific_questions(
        cls, question_count, answers_per_question=2, **kwargs
    ):
        """Create a trivia with specific number of questions and answers"""
        trivia = cls.create(**kwargs)
        for _ in range(question_count):
            question = QuestionFactory(trivia=trivia)
            AnswerFactory.create_batch(answers_per_question, question=question)
        return trivia


class PrivateTriviaFactory(TriviaFactory):
    """Factory for creating private trivias"""

    class Meta:
        model = Trivia
        skip_postgeneration_save = True

    is_public = False


class MaxQuestionsTrivia(TriviaFactory):
    """Factory for creating trivias with maximum number of questions"""

    class Meta:
        model = Trivia
        skip_postgeneration_save = True

    @factory.post_generation
    def questions(self, create, extracted, **kwargs):
        """Create the maximum number of questions allowed"""
        if not create:
            return

        for _ in range(5):  # Maximum number of questions
            question = QuestionFactory(trivia=self)
            AnswerFactory.create_batch(2, question=question)


class MinimalTriviaFactory(TriviaFactory):
    """Factory for creating trivias with minimum number of questions"""

    class Meta:
        model = Trivia
        skip_postgeneration_save = True

    @factory.post_generation
    def questions(self, create, extracted, **kwargs):
        """Create less than the minimum required number of questions"""
        if not create:
            return

        QuestionFactory.create_batch(2, trivia=self)


class InvalidTriviaFactory(TriviaFactory):
    """Factory for creating invalid trivias"""

    class Meta:
        model = Trivia
        skip_postgeneration_save = True

    difficulty = 5  # Invalid difficulty


class QuestionFactory(factory.django.DjangoModelFactory):
    """Factory for creating test Question instances"""

    class Meta:
        model = Question
        skip_postgeneration_save = True

    question_title = factory.Sequence(lambda n: f"Test Question {n}")
    trivia = factory.SubFactory(TriviaFactory)


class AnswerFactory(factory.django.DjangoModelFactory):
    """Factory for creating test Answer instances"""

    class Meta:
        model = Answer
        skip_postgeneration_save = True

    answer_title = factory.Sequence(lambda n: f"Test Answer {n}")
    is_correct = False
    is_active = True
    question = factory.SubFactory(QuestionFactory)


class PerformanceTestTriviaFactory(TriviaFactory):
    """Factory for performance tests"""

    @classmethod
    def create_batch_with_questions(cls, size=50, **kwargs):
        """Create multiple trivias with questions for performance tests"""
        trivias = []
        for _ in range(size):
            trivia = cls.create(**kwargs)
            # Create 3 questions with 4 answers each
            for _ in range(3):
                question = QuestionFactory(trivia=trivia)
                AnswerFactory.create_batch(4, question=question)
            trivias.append(trivia)
        return trivias


class ConcurrentTriviaFactory(TriviaFactory):
    """Factory for concurrent tests"""

    @classmethod
    def create_concurrent_data(cls, user, theme, thread_id):
        """Create data for concurrent trivia creation"""
        return {
            "title": f"Concurrent Trivia {thread_id}",
            "difficulty": 1,
            "theme": theme.id,
            "username": user.username,
            "questions": [
                {
                    "question_title": f"Question {i} Thread {thread_id}",
                    "answers": [
                        {
                            "answer_title": f"Correct Answer {i}",
                            "is_correct": True,
                        },
                        {
                            "answer_title": f"Wrong Answer {i}",
                            "is_correct": False,
                        },
                    ],
                }
                for i in range(1, 4)
            ],
        }
