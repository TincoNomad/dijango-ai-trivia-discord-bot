"""
Score Admin Configuration Module

This module configures the Django admin interface for score-related models.
Provides customized admin views for:
- Score management
- LeaderBoard administration
"""

from django.contrib import admin

from . import models


@admin.register(models.Score)
class ScoreAdmin(admin.ModelAdmin):
    """
    Admin configuration for Score model.

    Features:
    - Display key score information
    - Filter by Discord channel
    - Search by name and channel
    """

    list_display = ["name", "points", "leaderboard", "created_at"]
    list_filter = ["leaderboard__discord_channel"]
    search_fields = ["name", "leaderboard__discord_channel"]


@admin.register(models.LeaderBoard)
class LeaderBoardAdmin(admin.ModelAdmin):
    """
    Admin configuration for LeaderBoard model.

    Features:
    - Display channel and creation info
    - Search by Discord channel
    - Filter by creation date
    """

    list_display = ["discord_channel", "created_by", "created_at"]
    search_fields = ["discord_channel"]
    list_filter = ["created_at"]
