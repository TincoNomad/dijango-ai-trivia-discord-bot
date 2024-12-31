from functools import wraps
from django.db import connection

def check_db_connection(migration_operation):
    @wraps(migration_operation)
    def wrapper(*args, **kwargs):
        if not connection.is_usable():
            raise Exception("Database connection is not available")
        return migration_operation(*args, **kwargs)
    return wrapper

def log_migration_operation(migration_operation):
    @wraps(migration_operation)
    def wrapper(*args, **kwargs):
        print(f"Executing migration operation: {migration_operation.__name__}")
        result = migration_operation(*args, **kwargs)
        print(f"Completed migration operation: {migration_operation.__name__}")
        return result
    return wrapper