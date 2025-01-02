"""
Base Score Test Module

This module provides base classes and mixins for score-related tests.
Includes:
- Abstract base test class
- Score test utilities
- Leaderboard test utilities
"""

from abc import ABC, abstractmethod

import pytest

from .factories import LeaderBoardFactory, ScoreFactory


class BaseScoreTest(ABC):
    """Abstract base class for score tests"""

    @abstractmethod
    def setup_test_data(self):
        """Set up test data"""
        pass

    @abstractmethod
    def teardown_test_data(self):
        """Clean up test data"""
        pass


class ScoreTestMixin:
    """Mixin with common utilities for Score tests"""

    def assert_score_response(self, response, expected_status, check_data=True):
        """
        Validate score response.

        Args:
            response: API response to validate
            expected_status: Expected HTTP status code
            check_data: Whether to check response data structure
        """
        assert response.status_code == expected_status
        if expected_status == 200 and check_data:
            assert "data" in response.data
            assert "name" in response.data["data"]
            assert "points" in response.data["data"]


class LeaderboardTestMixin:
    """Mixin with common utilities for Leaderboard tests"""

    def assert_leaderboard_response(self, response, expected_status):
        """
        Validate leaderboard response.

        Args:
            response: API response to validate
            expected_status: Expected HTTP status code
        """
        assert response.status_code == expected_status
        if expected_status == 200:
            # For score list responses
            if isinstance(response.data, list):
                assert all(
                    "name" in score and "points" in score for score in response.data
                )
            # For individual leaderboard responses
            else:
                assert "discord_channel" in response.data
                assert "created_by" in response.data


@pytest.mark.django_db
class TestScoreBase(BaseScoreTest):
    """Base class for score tests with common helper methods"""

    def setup_test_data(self):
        """Set up test data"""
        self.user = self.test_user

    def teardown_test_data(self):
        """Clean up test data"""
        pass

    @staticmethod
    def create_leaderboard_with_scores(user, num_scores=5):
        """
        Helper method to create a leaderboard with scores.

        Args:
            user: User who creates the leaderboard
            num_scores: Number of scores to create

        Returns:
            tuple: (leaderboard, list of scores)
        """
        leaderboard = LeaderBoardFactory(created_by=user)
        scores = ScoreFactory.create_batch(size=num_scores, leaderboard=leaderboard)
        return leaderboard, scores
