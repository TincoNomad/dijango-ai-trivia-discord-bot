"""
JWT Authentication Utilities Module

This module provides utility functions for JWT (JSON Web Token) handling and authentication.
It includes functions for:
- Token decoding and user extraction
- User authentication from request headers
- Username to user ID conversion
- Custom permission classes

The module uses Django's settings for JWT configuration and includes detailed logging.
"""

import jwt
from django.conf import settings
import logging
from rest_framework import permissions

logger = logging.getLogger(__name__)


def get_user_from_token(token):
    """
    Decode a JWT token and extract the associated user.
    
    Args:
        token (str): The JWT token to decode.
    
    Returns:
        User: The user object if successfully decoded and found.
        None: If token is invalid, expired, or user not found.
    
    Raises:
        jwt.ExpiredSignatureError: If the token has expired.
        jwt.InvalidTokenError: If the token is invalid.
    """
    try:
        algorithm = settings.SIMPLE_JWT.get('ALGORITHM', 'HS256')
        signing_key = settings.SIMPLE_JWT.get('SIGNING_KEY', settings.SECRET_KEY)
        
        logger.debug(f"Attempting to decode token with algorithm: {algorithm}")
        payload = jwt.decode(token, signing_key, algorithms=[algorithm])
        
        # Import User model here to avoid circular imports
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Retrieve full user object
        user = User.objects.filter(id=payload.get('id')).first()
        logger.info(f"Successfully decoded token for user: {user}")
        
        return user
    except jwt.ExpiredSignatureError:
        logger.error("Token has expired")
    except jwt.InvalidTokenError:
        logger.error("Invalid token format or signature")
    except Exception as e:
        logger.exception(f"Unexpected error in token decoding: {str(e)}")
    
    return None

def auth_jwt(request):
    """
    Authenticate a user from the request's Authorization header.
    
    Extracts the JWT token from the Authorization header and validates it.
    
    Args:
        request: The HTTP request object containing headers.
    
    Returns:
        int: The authenticated user_id if successful.
        None: If authentication fails or no valid token is found.
    """
    auth_header = request.headers.get('Authorization')
    logger.debug(f"Processing Authorization header: {auth_header}")
    
    if auth_header and auth_header.startswith('Bearer '):
        # Extract token from header
        token = auth_header.split(' ')[1]
        logger.debug(f"Processing token: {token[:10]}...")  # Log first 10 chars for security
        
        user_id = get_user_from_token(token)
        if user_id is not None:
            logger.info(f"Authentication successful for user ID: {user_id}")
            return user_id
        else:
            logger.warning("Failed to extract user_id from token")
    else:
        logger.warning("No valid Authorization header found")
    return None

def get_user_id_by_username(username):
    """
    Retrieve a user's ID using their username.
    
    Args:
        username (str): The username to search for.
    
    Returns:
        UUID: The user's ID if found.
        None: If no user is found with the given username.
    
    Note:
        This function uses the custom user model defined in Django settings.
    """
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        user = User.objects.filter(username=username).first()
        if user:
            logger.info(f"Found user ID {user.id} for username: {username}")
            return user.id
        
        logger.warning(f"No user found with username: {username}")
        return None
        
    except Exception as e:
        logger.exception(f"Error in username lookup: {str(e)}")
        return None

class IsAdminUser(permissions.BasePermission):
    """
    Custom permission class to restrict access to admin users.
    
    Allows:
    - GET requests for all authenticated users
    - POST/PUT/DELETE requests only for admin users
    
    This permission can be used both at the view level and object level.
    """
    
    def has_permission(self, request, view):
        """
        Check if the user has permission to access the view.
        
        Args:
            request: The HTTP request object.
            view: The view being accessed.
            
        Returns:
            bool: True if permission is granted, False otherwise.
        """
        # Allow GET requests for authenticated users
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return request.user.is_authenticated
        # Require admin role for other methods
        return request.user.is_authenticated and request.user.role == 'admin'

    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to access a specific object.
        
        Args:
            request: The HTTP request object.
            view: The view being accessed.
            obj: The object being accessed.
            
        Returns:
            bool: True if permission is granted, False otherwise.
        """
        # Same logic as has_permission
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.role == 'admin'

