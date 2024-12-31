from django.conf import settings
import logging
from django.db import transaction
from contextlib import nullcontext
# from .base import BaseMigration
# from .registry import MigrationRegistry

logger = logging.getLogger(__name__)

class MigrationHandler:
    def __init__(self):
        self.config = settings.MIGRATIONS_CONFIG
        self.setup_logging()
        
    def setup_logging(self):
        if self.config['logging']['enabled']:
            logging.basicConfig(
                level=self.config['logging']['level'],
                format='%(asctime)s [%(levelname)s] %(message)s'
            )
    
    def run_migration(self, migration_instance):
        if self.config['validation']['check_db_connection']:
            self.check_database()
            
        batch_size = self.config['performance']['batch_size']
        use_transactions = self.config['performance']['use_transactions']
        
        logger.info(f"Running migration {migration_instance.__class__.__name__}")
        
        try:
            with transaction.atomic() if use_transactions else nullcontext():
                # Process migration in batches if supported
                if hasattr(migration_instance, 'process_in_batches'):
                    return migration_instance.process_in_batches(batch_size)
                return migration_instance.apply()
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}")
            raise

    def check_database(self):
        from django.db import connection
        if not connection.is_usable():
            raise Exception("Database connection is not available")