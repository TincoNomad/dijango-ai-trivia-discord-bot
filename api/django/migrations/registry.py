class MigrationRegistry:
    _migrations = {}
    
    @classmethod
    def register(cls, app_label, migration_name):
        def decorator(migration_class):
            cls._migrations[f"{app_label}.{migration_name}"] = migration_class
            return migration_class
        return decorator
    
    @classmethod
    def get_migration(cls, app_label, migration_name):
        return cls._migrations.get(f"{app_label}.{migration_name}")