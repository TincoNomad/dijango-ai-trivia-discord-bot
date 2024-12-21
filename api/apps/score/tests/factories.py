"""
Test Factories Module

This module provides factory classes for creating test data.
Uses Factory Boy to generate:
- LeaderBoard instances
- Score instances
"""

import factory
from api.apps.score.models import Score, LeaderBoard

class LeaderBoardFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating test LeaderBoard instances.
    
    Generates:
    - Unique discord channel names
    - Associated user through UserFactory
    """
    
    class Meta:
        model = LeaderBoard
        
    discord_channel = factory.Sequence(lambda n: f'channel_{n}')
    created_by = factory.SubFactory('api.apps.score.tests.factories.UserFactory')

class ScoreFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating test Score instances.
    
    Generates:
    - Unique player names
    - Random point values
    - Associated leaderboard
    """
    
    class Meta:
        model = Score
        
    name = factory.Sequence(lambda n: f'player_{n}')
    points = factory.Faker('random_int', min=0, max=1000)
    leaderboard = factory.SubFactory(LeaderBoardFactory) 