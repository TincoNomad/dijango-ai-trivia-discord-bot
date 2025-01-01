"""
Environment Configuration Module

Purpose: 
    Manages environment variables and configuration settings
    for the Trivia application.

Features:
    - Environment detection
    - Debug configuration
    - Security key management
    - Database credentials
    - API settings

Author: Renzo Tincopa
Last Updated: 2024
"""

import environ
import os

# Initialize environ with default values
env = environ.Env(
    # Environment & Debug settings
    ENVIRONMENT=(str, 'development'),  # Current environment
    DEBUG=(bool, True),               # Debug mode flag
    
    # Security settings
    SECRET_KEY=(str, None),          # Django secret key
    SIGNING_KEY=(str, None),         # JWT signing key
    
    # Database configuration
    DB_NAME=(str, 'trivia_db'),      # Database name
    DB_USER=(str, 'admin'),          # Database user
    DB_PASSWORD=(str, 'admin'),      # Database password
    
    # API configuration
    API_VERSION=(str, 'v1'),         # API version
    API_TIMEOUT=(int, 30),           # API timeout in seconds
)

# Read the .env file from project root
environ.Env.read_env(os.path.join(os.path.dirname(__file__), '.env'))

# Environment detection
IS_DEVELOPMENT = env('ENVIRONMENT') == 'development'
IS_PRODUCTION = env('ENVIRONMENT') == 'production'
IS_TESTING = env('ENVIRONMENT') == 'testing'

# Validation
assert env('SECRET_KEY'), 'SECRET_KEY must be set'
assert env('SIGNING_KEY'), 'SIGNING_KEY must be set'
