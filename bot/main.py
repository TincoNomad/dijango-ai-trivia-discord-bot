"""
Bot Entry Point

Configures and launches the Discord bot with required intents.

Usage:
    python -m bot.main
"""

import discord
from env import env
from bot.discord_client import DiscordClient

# Set up Discord bot connection
intents = discord.Intents.default()
intents.message_content = True

# Initialize bot with command prefix '$'
client = DiscordClient(command_prefix='$', intents=intents)

# Run the Discord bot
client.run(env('DISCORD_KEY')) #type: ignore