import os

# Import base URL from environment-specific settings
environment = os.environ.get('DJANGO_ENVIRONMENT', 'development')
if environment == 'production':
    from .prod import BASE_URL
else:
    from .dev import BASE_URL

# Define API URLs using the imported BASE_URL
TRIVIA_URL = f"{BASE_URL}/api/trivias/"
THEME_URL = f"{BASE_URL}/api/themes/"
DIFFICULTY_URL = f"{TRIVIA_URL}difficulty/"
FILTER_URL = f"{TRIVIA_URL}filter/"
GET_TRIVIA_URL = f"{TRIVIA_URL}get_trivia/"
GET_QUESTIONS_URL = f"{TRIVIA_URL}get_questions/"
LEADERBOARD_URL = f"{BASE_URL}/api/leaderboards/"
SCORE_URL = f"{BASE_URL}/api/score/"

__all__ = [
    'BASE_URL', 'TRIVIA_URL', 'THEME_URL', 
    'DIFFICULTY_URL', 'FILTER_URL', 'GET_TRIVIA_URL',
    'GET_QUESTIONS_URL', 'LEADERBOARD_URL', 'SCORE_URL'
]
