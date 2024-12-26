"""
Throttling Classes Module

This module provides custom rate limiting classes for the API.
"""

from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

class CustomUserRateThrottle(UserRateThrottle):
    """Rate limiting for authenticated users"""
    def wait(self):
        wait_time = super().wait()
        if wait_time is None:
            return None
        return {
            'message': f'Rate limit exceeded. Please wait {int(wait_time)} seconds before trying again.',
            'wait_seconds': int(wait_time)
        }

class CustomAnonRateThrottle(AnonRateThrottle):
    """Rate limiting for anonymous users"""
    def wait(self):
        wait_time = super().wait()
        if wait_time is None:
            return None
        return {
            'message': f'Rate limit exceeded. Please wait {int(wait_time)} seconds before trying again.',
            'wait_seconds': int(wait_time)
        }

class StrictUserRateThrottle(UserRateThrottle):
    """Stricter rate limiting for sensitive operations"""
    rate = '30/hour'

    def wait(self):
        wait_time = super().wait()
        if wait_time is None:
            return None
        return {
            'message': f'Too many attempts. Please wait {int(wait_time)} seconds before trying again.',
            'wait_seconds': int(wait_time)
        }

class AuthRateThrottle(AnonRateThrottle):
    """Rate limiting for authentication endpoints"""
    rate = '5/minute'

    def wait(self):
        wait_time = super().wait()
        if wait_time is None:
            return None
        return {
            'message': f'Too many login attempts. Please wait {int(wait_time)} seconds before trying again.',
            'wait_seconds': int(wait_time)
        } 