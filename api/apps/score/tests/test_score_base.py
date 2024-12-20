from abc import ABC, abstractmethod
import pytest
from .factories import ScoreFactory, LeaderBoardFactory

class BaseScoreTest(ABC):
    """Clase base abstracta para tests de score"""
    
    @abstractmethod
    def setup_test_data(self):
        """Configurar datos de prueba"""
        pass

    @abstractmethod
    def teardown_test_data(self):
        """Limpiar datos después del test"""
        pass

class ScoreTestMixin:
    """Mixin con utilidades comunes para tests de Score"""
    
    def assert_score_response(self, response, expected_status, check_data=True):
        """Validar respuesta de score"""
        assert response.status_code == expected_status
        if expected_status == 200 and check_data:
            assert 'data' in response.data
            assert 'name' in response.data['data']
            assert 'points' in response.data['data']

class LeaderboardTestMixin:
    """Mixin con utilidades comunes para tests de Leaderboard"""
    
    def assert_leaderboard_response(self, response, expected_status):
        """Validar respuesta de leaderboard"""
        assert response.status_code == expected_status
        if expected_status == 200:
            # Para respuestas de lista de scores
            if isinstance(response.data, list):
                assert all('name' in score and 'points' in score 
                         for score in response.data)
            # Para respuestas de leaderboard individual
            else:
                assert 'discord_channel' in response.data
                assert 'created_by' in response.data

@pytest.mark.django_db
class TestScoreBase(BaseScoreTest):
    """Clase base para tests de score con métodos helper comunes"""
    
    def setup_test_data(self):
        """Configurar datos de prueba"""
        self.user = self.test_user
    
    def teardown_test_data(self):
        """Limpiar datos después del test"""
        pass

    @staticmethod
    def create_leaderboard_with_scores(user, num_scores=5):
        """Helper para crear un leaderboard con scores"""
        leaderboard = LeaderBoardFactory(created_by=user)
        scores = ScoreFactory.create_batch(
            size=num_scores, 
            leaderboard=leaderboard
        )
        return leaderboard, scores 