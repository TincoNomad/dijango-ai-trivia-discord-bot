"""Tests for advanced trivia operations."""
import pytest
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from django.urls import reverse
from rest_framework.test import APIClient
from .test_trivia_base import TestTriviaBase
from .factories import UserFactory

@pytest.mark.django_db(transaction=True)
class TestTriviaAdvanced(TestTriviaBase):
    """Pruebas avanzadas para demostrar manejo de concurrencia y rendimiento."""

    @pytest.fixture(autouse=True)
    def setup_method(self, test_user, test_theme):
        """Setup for each test case"""
        self.url = reverse('trivia-list')
        self.user = test_user
        self.theme = test_theme
        self.valid_data = {
            'title': 'Performance Test Trivia',
            'difficulty': 1,
            'theme': self.theme.id,
            'username': self.user.username,
            'questions': [
                {
                    'question_title': f'Question {i}',
                    'answers': [
                        {'answer_title': f'Answer {j} for Q{i}', 
                         'is_correct': j == 0}
                        for j in range(3)
                    ]
                }
                for i in range(3)
            ]
        }

    def test_concurrent_trivia_creation(self, api_client_authenticated):
        """Prueba la creación simultánea de trivias."""
        def create_trivia():
            thread_user = UserFactory(
                username=f'user_{threading.get_ident()}_{uuid.uuid4().hex[:8]}'
            )
            client = APIClient()
            client.force_authenticate(user=thread_user)
            
            data = self.valid_data.copy()
            data.update({
                'username': thread_user.username,
                'title': f'Concurrent Trivia {threading.get_ident()}'
            })
            
            return client.post(self.url, data, format='json')

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(create_trivia) for _ in range(3)]
            responses = [f.result() for f in futures]

        successful_creations = [r for r in responses if r.status_code == 201]
        assert len(successful_creations) > 0
