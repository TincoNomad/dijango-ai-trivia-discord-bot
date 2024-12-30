"""
Monitoring Views Module

This module would contain any view functions or classes needed for
the monitoring application's web interface.

Currently, all monitoring functionality is handled through:
- Admin interface (admin.py)
- Middleware (middleware.py)
- Management commands (management/commands/)
"""

# Views will be added here as needed

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import connections
from django.db.utils import OperationalError
import psutil
import time

@api_view(['GET'])
def health_check(request):
    """
    Comprehensive health check endpoint that verifies:
    - API response
    - Database connection
    - System resources
    - Response timing
    """
    start_time = time.time()
    health_data = {
        'status': 'healthy',
        'checks': {}
    }

    # Check database
    try:
        db_conn = connections['default']
        db_conn.cursor()
        health_data['checks']['database'] = 'connected'
    except OperationalError:
        health_data.update({
            'status': 'unhealthy',
            'checks': {'database': 'disconnected'}
        })
        return Response(health_data, status=503)

    # Check system resources
    health_data['checks'].update({
        'memory': f"{psutil.virtual_memory().percent}%",
        'cpu': f"{psutil.cpu_percent()}%",
        'disk': f"{psutil.disk_usage('/').percent}%"
    })

    # Add response time
    health_data['response_time'] = f"{(time.time() - start_time):.3f}s"

    return Response(health_data)
