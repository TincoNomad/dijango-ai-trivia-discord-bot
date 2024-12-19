import pytest
from django.urls import reverse
from .test_score_base import TestScoreBase

@pytest.mark.django_db
class TestLeaderboardOperations(TestScoreBase):
    """Tests para operaciones de leaderboard"""

    def test_get_leaderboard_top_10(self, api_client, test_user):
        """Test obtener top 10 scores de un leaderboard"""
        leaderboard, _ = self.create_leaderboard_with_scores(
            test_user, 
            num_scores=15
        )
        url = reverse('leaderboard-list')
        response = api_client.get(
            f"{url}?channel={leaderboard.discord_channel}"
        )
        assert response.status_code == 200
        assert len(response.data) == 10 

    def test_get_nonexistent_leaderboard(self, api_client):
        """Test obtener leaderboard que no existe"""
        url = reverse('leaderboard-list')
        response = api_client.get(f"{url}?channel=nonexistent")
        assert response.status_code == 404

    def test_get_leaderboard_ordering(self, api_client):
        """Test que los scores estén ordenados por puntos"""
        leaderboard, _ = self.create_leaderboard_with_scores(self.user, 5)
        url = reverse('leaderboard-list')
        response = api_client.get(f"{url}?channel={leaderboard.discord_channel}")
        
        scores = response.data
        assert all(
            scores[i]['points'] >= scores[i+1]['points'] 
            for i in range(len(scores)-1)
        )