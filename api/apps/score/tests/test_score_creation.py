"""
Score Creation Test Module

This module contains tests for score creation functionality.
Tests cover:
- Successful score creation
- Validation of score data
- Error handling
"""

import pytest

from .test_score_base import BaseScoreTest, ScoreTestMixin


@pytest.mark.django_db
class TestScoreCreation(BaseScoreTest, ScoreTestMixin):
    """Tests for score creation functionality"""

    @pytest.fixture(autouse=True)
    def setup_method(self, test_user, test_leaderboard):
        """Setup for each test case"""
        self.setup_test_data()
        self.url = "/api/score/"

    def setup_test_data(self):
        """Set up initial test data"""
        pass

    def teardown_test_data(self):
        """Clean up after test execution"""
        pass

    def test_create_score_success(self, api_client_authenticated, valid_score_data):
        """
        Test successful score creation.

        Verifies that a score can be created with valid data
        and returns the expected response.
        """
        # Arrange
        score_data = valid_score_data

        # Act
        response = api_client_authenticated.post(
            self.url, data=score_data, format="json"
        )

        # Assert
        self.assert_score_response(response, 200)
        assert response.data["data"]["points"] == score_data["points"]

    def test_create_score_invalid_points(
        self, api_client_authenticated, valid_score_data
    ):
        """
        Test score creation with invalid points.

        Verifies that attempting to create a score with negative points
        results in a validation error.
        """
        # Arrange
        invalid_data = valid_score_data.copy()
        invalid_data["points"] = -100

        # Act
        response = api_client_authenticated.post(
            self.url, data=invalid_data, format="json"
        )

        # Assert
        self.assert_score_response(response, 400, check_data=False)
        assert "error" in response.data
