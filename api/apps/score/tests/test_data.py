"""
Test Data Module

This module contains test data constants used across test cases.
Includes sample data for:
- Score creation and updates
- Leaderboard operations
"""

TEST_SCORE_DATA = {
    "valid_score": {
        "name": "TestPlayer",
        "points": 100,
        "discord_channel": "test-channel",
    },
    "update_data": {"points": 150, "update_mode": "add"},  # or 'replace'
}

TEST_LEADERBOARD_DATA = {
    "valid_leaderboard": {
        "discord_channel": "test-channel",
        "username": "testuser",
    }
}
