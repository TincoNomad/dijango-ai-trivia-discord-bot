"""
Score Serializers Module

This module provides serializers for the scoring system models.
Includes serializers for:
- LeaderBoard management
- Score tracking
- Trivia winner recording

Features:
- Data validation
- Custom creation logic
- Error handling
"""

from rest_framework import serializers
from .models import Score, LeaderBoard, TriviaWinner
from django.contrib.auth import get_user_model
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class LeaderBoardSerializer(serializers.ModelSerializer):
    """
    Serializer for LeaderBoard model.
    
    Handles creation and validation of leaderboards, including:
    - Username validation
    - Discord channel validation
    - Existing leaderboard checks
    
    Attributes:
        username (CharField): Username of the leaderboard creator (write-only)
    """
    
    username = serializers.CharField(write_only=True)
    
    class Meta:
        model = LeaderBoard
        fields: list[str] = ['id', 'discord_channel', 'username']

    def create(self, validated_data: Dict[str, Any]) -> LeaderBoard:
        """
        Create or retrieve a leaderboard.
        
        Args:
            validated_data: Dictionary containing validated data
                - discord_channel: Channel identifier
                - username: Creator's username
        
        Returns:
            LeaderBoard: Created or existing leaderboard instance
            
        Raises:
            ValidationError: If user doesn't exist or creation fails
        """
        discord_channel = validated_data.get('discord_channel')
        username = validated_data.pop('username')
        User = get_user_model()
        
        logger.info(f"Attempting to create/get leaderboard for channel: {discord_channel}, username: {username}")
        
        # Check if leaderboard already exists
        existing_leaderboard = LeaderBoard.objects.filter(discord_channel=discord_channel).first()
        if existing_leaderboard:
            logger.info(f"Found existing leaderboard for channel: {discord_channel}")
            return existing_leaderboard
            
        try:
            # Find user
            user = User.objects.get(username=username)
            logger.info(f"Found user: {username}")
            
            # Create new leaderboard
            leaderboard = LeaderBoard.objects.create(
                discord_channel=discord_channel,
                created_by=user
            )
            logger.info(f"Created new leaderboard for channel: {discord_channel}")
            return leaderboard
            
        except User.DoesNotExist:
            logger.error(f"No user exists with this username: {username}")
            raise serializers.ValidationError({
                "username": "No user exists with this username"
            })
        except Exception as e:
            logger.error(f"Error creating leaderboard: {str(e)}")
            raise serializers.ValidationError({
                "error": f"Error creating leaderboard: {str(e)}"
            })

    def validate_discord_channel(self, value: str) -> str:
        """
        Validate the discord channel value.
        
        Args:
            value: Discord channel identifier
            
        Returns:
            str: Validated channel identifier
            
        Raises:
            ValidationError: If channel is empty
        """
        if not value:
            raise serializers.ValidationError("Discord channel is required")
        return value

    def validate_username(self, value: str) -> str:
        """
        Validate the username value.
        
        Args:
            value: Username to validate
            
        Returns:
            str: Validated username
            
        Raises:
            ValidationError: If username is empty
        """
        if not value:
            raise serializers.ValidationError("Username is required")
        return value

class ScoreSerializer(serializers.ModelSerializer):
    """
    Serializer for Score model.
    
    Handles score data validation including:
    - Points validation
    - Discord channel format validation
    """
    
    class Meta:
        model = Score
        fields = ['name', 'points']

    def validate_points(self, value):
        """
        Validate points value.
        
        Args:
            value: Points to validate
            
        Returns:
            int: Validated points value
            
        Raises:
            ValidationError: If points are negative or not an integer
        """
        if not isinstance(value, int) or value < 0:
            raise serializers.ValidationError("Points must be a positive integer")
        return value

    def validate_discord_channel(self, value):
        """
        Validate discord channel format.
        
        Args:
            value: Channel identifier to validate
            
        Returns:
            str: Validated channel identifier
            
        Raises:
            ValidationError: If channel doesn't start with #
        """
        if not value.startswith('#'):
            raise serializers.ValidationError("Discord channel must start with #")
        return value

class TriviaWinnerSerializer(serializers.ModelSerializer):
    """
    Serializer for TriviaWinner model.
    
    Handles trivia winner data serialization with:
    - Automatic date_won field
    - Read-only fields configuration
    """
    
    class Meta:
        model = TriviaWinner
        fields = ['id', 'name', 'trivia_name', 'score', 'date_won']
        read_only_fields = ['date_won']