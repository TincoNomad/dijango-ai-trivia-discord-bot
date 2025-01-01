from django.views.decorators.cache import cache_page
from django.conf import settings
from functools import wraps
from django.utils.decorators import method_decorator
from django.core.cache import cache

def cache_response(timeout=None):
    """
    Custom cache decorator for both function and method views
    
    Usage:
    @cache_response()  # Uses default CACHE_TTL
    @cache_response(timeout=300)  # Custom timeout in seconds
    """
    def decorator(view_func):
        if timeout is None:
            cache_timeout = settings.CACHE_TTL
        else:
            cache_timeout = timeout

        @wraps(view_func)
        def _wrapped_view(*args, **kwargs):
            return cache_page(cache_timeout)(view_func)(*args, **kwargs)
        return _wrapped_view
    return decorator

def cache_viewset_action():
    """
    Decorator specifically for ViewSet methods
    """
    return method_decorator(cache_page(settings.CACHE_TTL))

def cache_query_result(cache_key: str, timeout=None):
    """
    Decorator for caching expensive model queries
    
    Usage:
    @classmethod
    @cache_query_result('all_questions')
    def get_all_questions(cls):
        return cls.objects.all()
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            data = cache.get(cache_key)
            if data is None:
                data = func(*args, **kwargs)
                cache.set(cache_key, data, timeout or settings.CACHE_TTL)
            return data
        return wrapper
    return decorator

def invalidate_cache(cache_key: str):
    """
    Helper function to invalidate specific cache
    """
    cache.delete(cache_key)