from django.db import connections
from django.db.utils import OperationalError
from django.core.cache import cache
import psutil
import time

class HealthService:
    @staticmethod
    def check_health():
        start_time = time.time()
        health_status = {
            'status': 'healthy',
            'checks': {
                'database': True,
                'cache': True,
                'disk': True,
                'memory': True
            },
            'details': {}
        }

        # Check database
        try:
            db_conn = connections['default']
            db_conn.cursor()
            health_status['details']['database'] = 'connected'
        except OperationalError:
            health_status['checks']['database'] = False
            health_status['details']['database'] = 'disconnected'
            health_status['status'] = 'unhealthy'

        # Check cache
        try:
            cache.set('health_check', 'ok', 1)
            if cache.get('health_check') == 'ok':
                health_status['details']['cache'] = 'working'
        except Exception:
            health_status['checks']['cache'] = False
            health_status['details']['cache'] = 'not working'
            health_status['status'] = 'unhealthy'

        # System resources
        health_status['details'].update({
            'memory_usage': f"{psutil.virtual_memory().percent}%",
            'cpu_usage': f"{psutil.cpu_percent()}%",
            'disk_usage': f"{psutil.disk_usage('/').percent}%"
        })

        # Response time
        health_status['response_time'] = f"{(time.time() - start_time):.3f}s"

        return health_status