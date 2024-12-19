import pytest
from django.urls import reverse
from .test_score_base import BaseScoreTest, LeaderboardTestMixin
from .factories import LeaderBoardFactory, ScoreFactory
@pytest.mark.django_db
class TestLeaderboardOperations(BaseScoreTest, LeaderboardTestMixin):
    """Tests para operaciones de leaderboard"""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup para cada test"""
        self.setup_test_data()

    def setup_test_data(self):
        """Configurar datos iniciales"""
        self.url = '/api/leaderboards/'  # ✅ Cambiar a plural como en los otros tests

    def teardown_test_data(self):
        """Limpiar datos después del test"""
        pass

    def test_get_leaderboard_top_10(self, api_client, leaderboard_with_scores):
        """Test obtener top 10 scores de un leaderboard"""
        # Arrange
        leaderboard = leaderboard_with_scores

        # Act
        response = api_client.get(
            f"{self.url}?channel={leaderboard.discord_channel}"
        )

        # Assert
        self.assert_leaderboard_response(response, 200)
        assert len(response.data) == 10

    def test_get_nonexistent_leaderboard(self, api_client):
        """Test obtener leaderboard que no existe"""
        # Act
        response = api_client.get(f"{self.url}?channel=nonexistent")
        
        # Assert
        assert response.status_code == 404

    def test_get_leaderboard_ordering(self, api_client, test_user):
        """Test que los scores estén ordenados por puntos"""
        # Arrange
        leaderboard = LeaderBoardFactory(created_by=test_user)
        ScoreFactory.create_batch(size=5, leaderboard=leaderboard)

        # Act
        response = api_client.get(f"{self.url}?channel={leaderboard.discord_channel}")
        
        # Assert
        scores = response.data
        assert all(
            scores[i]['points'] >= scores[i+1]['points'] 
            for i in range(len(scores)-1)
        )

    def test_get_leaderboard_by_id(self, api_client, test_leaderboard):
        """Test obtener leaderboard por ID"""
        # Act
        response = api_client.get(f"{self.url}get_leaderboard/?id={test_leaderboard.id}")
        
        # Assert
        assert response.status_code == 200
        assert response.data['leaderboard_id'] == str(test_leaderboard.id)