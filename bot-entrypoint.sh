#!/bin/bash

# Discord Bot Service Entrypoint Script
# ------------------------------------
# Purpose: Initialize and start the Discord bot service
# Features:
# - Database connection verification
# - Service startup banner
# - Bot process management
# Author: Renzo Tincopa
# Last Updated: 2024

# Database connection check function
wait_for_db() {
    # Verify MySQL database is ready before starting bot
    # Retries connection until successful
    # Parameters: None
    # Returns: None (exits on success)
    echo "🔄 Waiting for MySQL..."
    while ! python -c "import MySQLdb; MySQLdb.connect(host='db', user='admin', password='admin', db='trivia_db')" 2>/dev/null; do
        sleep 1
    done
    echo "✅ MySQL connected"
}

# Service startup banner display
show_banner() {
    # Display visually distinctive startup message
    # Parameters: None
    # Returns: None
    echo "==================================="
    echo "🤖 Discord Bot Starting..."
    echo "==================================="
}

# Execution Steps
wait_for_db # Step 1: Ensure database is ready
show_banner # Step 2: Display startup message
export PYTHONUNBUFFERED=1 # Step 3: Configure Python output
python -m bot.main  # Step 4: Start bot process
