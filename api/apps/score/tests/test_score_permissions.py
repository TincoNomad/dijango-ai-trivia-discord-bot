"""
Score Permissions Test Module

This module contains tests for score-related permissions.
Tests cover:
- Authentication requirements
- Authorization checks
- Permission validations
"""

import pytest

from .test_score_base import BaseScoreTest, LeaderboardTestMixin


@pytest.mark.django_db
class TestScorePermissions(BaseScoreTest, LeaderboardTestMixin):
    """Tests for score and leaderboard permissions"""

    @pytest.fixture(autouse=True)
    def setup_method(self, test_user):
        """Setup for each test case"""
        self.setup_test_data()
        self.url = "/api/leaderboards/"

    def setup_test_data(self):
        """Set up initial test data"""
        pass

    def teardown_test_data(self):
        """Clean up after test execution"""
        pass

    def test_create_leaderboard_requires_auth(self, api_client, valid_score_data):
        """
        Test authentication requirement for leaderboard creation.

        Verifies that attempting to create a leaderboard without
        authentication results in an error.
        """
        # Act
        response = api_client.post(self.url, valid_score_data)

        # Assert
        self.assert_leaderboard_response(response, 400)

    def test_create_leaderboard_success(
        self, api_client_authenticated, valid_score_data
    ):
        """
        Test successful leaderboard creation with authentication.

        Verifies that an authenticated user can successfully
        create a leaderboard.
        """
        # Act
        response = api_client_authenticated.post(
            self.url, data=valid_score_data, format="json"
        )

        # Assert
        self.assert_leaderboard_response(response, 200)
