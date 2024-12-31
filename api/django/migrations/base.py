# from django.db.migrations.operations.base import Operation
from django.db import migrations
import logging

logger = logging.getLogger(__name__)

class BaseMigration(migrations.Migration):
    """Base migration class with additional functionality"""
    
    def __init__(self):
        self._pre_migration_checks = []
        self._post_migration_checks = []
        super().__init__()
    
    def apply(self, project_state, schema_editor, collect_sql=False):
        """Override apply to add pre/post checks"""
        # Pre-migration checks
        for check in self._pre_migration_checks:
            check(project_state, schema_editor)
            
        logger.info(f"Applying migration: {self.__class__.__name__}")
        
        # Apply migration
        state = super().apply(project_state, schema_editor, collect_sql)
        
        # Post-migration checks
        for check in self._post_migration_checks:
            check(state, schema_editor)
            
        return state