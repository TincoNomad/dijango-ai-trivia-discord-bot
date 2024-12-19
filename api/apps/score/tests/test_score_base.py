import pytest
from .factories import ScoreFactory, LeaderBoardFactory

@pytest.mark.django_db
class TestScoreBase:
    """Clase base para tests de score con métodos helper comunes"""
    
    @pytest.fixture(autouse=True)
    def setup_method(self, test_user, test_theme):
        """Setup inicial para cada test"""
        self.user = test_user
    
    @staticmethod
    def create_leaderboard_with_scores(user, num_scores=5):
        """Helper para crear un leaderboard con scores"""
        leaderboard = LeaderBoardFactory(created_by=user)
        scores = ScoreFactory.create_batch(
            size=num_scores, 
            leaderboard=leaderboard
        )
        return leaderboard, scores 