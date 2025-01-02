"""
Leaderboard Operations Test Module

This module contains integration tests for leaderboard operations.
Tests cover:
- Top scores retrieval
- Leaderboard creation
- Error handling
- Score ordering
"""

import pytest

from .factories import LeaderBoardFactory, ScoreFactory
from .test_score_base import BaseScoreTest, LeaderboardTestMixin


@pytest.mark.django_db
class TestLeaderboardOperations(BaseScoreTest, LeaderboardTestMixin):
    """Tests for leaderboard operations"""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup for each test"""
        self.setup_test_data()

    def setup_test_data(self):
        """Set up initial test data"""
        self.url = "/api/leaderboards/"

    def teardown_test_data(self):
        """Clean up test data"""
        pass

    def test_get_leaderboard_top_10(self, api_client, leaderboard_with_scores):
        """Test retrieving top 10 scores from a leaderboard"""
        # Arrange
        leaderboard = leaderboard_with_scores

        # Act
        response = api_client.get(f"{self.url}?channel={leaderboard.discord_channel}")

        # Assert
        self.assert_leaderboard_response(response, 200)
        assert len(response.data) == 10

    def test_get_nonexistent_leaderboard(self, api_client):
        """Test retrieving a non-existent leaderboard"""
        # Act
        response = api_client.get(f"{self.url}?channel=nonexistent")

        # Assert
        assert response.status_code == 404

    def test_get_leaderboard_ordering(self, api_client, test_user):
        """Test that scores are ordered by points"""
        # Arrange
        leaderboard = LeaderBoardFactory(created_by=test_user)
        ScoreFactory.create_batch(size=5, leaderboard=leaderboard)

        # Act
        response = api_client.get(f"{self.url}?channel={leaderboard.discord_channel}")

        # Assert
        scores = response.data
        assert all(
            scores[i]["points"] >= scores[i + 1]["points"]
            for i in range(len(scores) - 1)
        )

    def test_get_leaderboard_by_id(self, api_client, test_leaderboard):
        """Test retrieving leaderboard by ID"""
        # Act
        response = api_client.get(
            f"{self.url}get_leaderboard/?id={test_leaderboard.id}"
        )

        # Assert
        assert response.status_code == 200
        assert response.data["leaderboard_id"] == str(test_leaderboard.id)
