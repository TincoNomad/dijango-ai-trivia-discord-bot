#!/bin/bash

# Entrypoint script for Discord bot service
# Ensures database is ready before starting bot

wait_for_db() {
    # Verify database connection before bot startup
    echo "🔄 Waiting for MySQL..."
    while ! python -c "import MySQLdb; MySQLdb.connect(host='db', user='admin', password='admin', db='trivia_db')" 2>/dev/null; do
        sleep 1
    done
    echo "✅ MySQL connected"
}

show_banner() {
    # Display bot startup banner
    echo "==================================="
    echo "🤖 Discord Bot Starting..."
    echo "==================================="
}

wait_for_db
show_banner
export PYTHONUNBUFFERED=1
python -m bot.main 