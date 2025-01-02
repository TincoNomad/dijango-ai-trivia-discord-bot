"""
Django Settings Initialization Module

This module initializes the Django settings based on the environment
and defines the API endpoints URLs used throughout the application.

The module:
1. Determines the current environment (development/production)
2. Imports the appropriate BASE_URL
3. Constructs all API endpoint URLs using the BASE_URL

Usage:
    from api.django import TRIVIA_URL, SCORES_URL
"""

import os

# Determine environment and import appropriate settings
environment = os.environ.get("DJANGO_ENVIRONMENT", "development")
if environment == "production":
    from .prod import BASE_URL
else:
    from .dev import BASE_URL

# API Endpoints Configuration
# These URLs are constructed using the environment-specific BASE_URL
TRIVIA_URL = f"{BASE_URL}/api/trivias/"  # Base trivia endpoint (list & detail)
THEME_URL = f"{BASE_URL}/api/themes/"  # Theme management endpoint
DIFFICULTY_URL = f"{TRIVIA_URL}difficulty/"  # Difficulty settings endpoint
FILTER_URL = f"{TRIVIA_URL}filter/"  # Trivia filtering endpoint
QUESTIONS_URL = f"{BASE_URL}/api/questions/"  # Questions endpoint
LEADERBOARD_URL = f"{BASE_URL}/api/leaderboards/"  # Leaderboard endpoint
SCORES_URL = f"{BASE_URL}/api/score/"  # Score management endpoint

# Export all URL configurations
__all__ = [
    "BASE_URL",
    "TRIVIA_URL",
    "THEME_URL",
    "DIFFICULTY_URL",
    "FILTER_URL",
    "QUESTIONS_URL",
    "LEADERBOARD_URL",
    "SCORES_URL",
]
