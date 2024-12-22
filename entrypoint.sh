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
    echo "🚀 Django API Server"
    echo "🌐 http://0.0.0.0:8000"
    echo "==================================="
}

wait_for_db
show_banner
export PYTHONUNBUFFERED=1
python manage.py runserver 0.0.0.0:8000