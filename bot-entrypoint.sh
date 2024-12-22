#!/bin/bash

wait_for_db() {
    echo "🔄 Waiting for MySQL..."
    while ! python -c "import MySQLdb; MySQLdb.connect(host='db', user='admin', password='admin', db='trivia_db')" 2>/dev/null; do
        sleep 1
    done
    echo "✅ MySQL connected"
}

show_banner() {
    echo "==================================="
    echo "🤖 Discord Bot Starting..."
    echo "==================================="
}

wait_for_db
show_banner
export PYTHONUNBUFFERED=1
python -m bot.main 