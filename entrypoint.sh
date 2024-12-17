#!/bin/bash

wait_for_db() {
    echo "Waiting for MySQL to be ready..."
    while ! python -c "import MySQLdb; MySQLdb.connect(host='db', user='admin', password='admin', db='trivia_db')" 2>/dev/null; do
        echo "MySQL not ready... waiting"
        sleep 1
    done
    echo "¡MySQL is ready!"
}

show_banner() {
    echo "==================================="
    echo "🚀 Starting Django server..."
    echo "📊 Database: MySQL connected"
    echo "🌐 Web server: http://localhost:8000"
    echo "==================================="
}

wait_for_db
show_banner
export PYTHONUNBUFFERED=1
python manage.py runserver 0.0.0.0:8000