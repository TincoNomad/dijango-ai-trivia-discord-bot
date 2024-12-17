import jwt
from django.conf import settings
import logging
from rest_framework import permissions

logger = logging.getLogger(__name__)


def get_user_from_token(token):
    """
    Decode the JWT token and extract the user.
    
    Args:
        token (str): The JWT token to decode.
    
    Returns:
        User: The user object if successfully decoded, None otherwise.
    """
    try:
        algorithm = settings.SIMPLE_JWT.get('ALGORITHM', 'HS256')
        signing_key = settings.SIMPLE_JWT.get('SIGNING_KEY', settings.SECRET_KEY)
        
        logger.debug(f"Attempting to decode token with algorithm: {algorithm}")
        payload = jwt.decode(token, signing_key, algorithms=[algorithm])
        
        # Importar User model aquí para evitar importación circular
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Obtener el usuario completo
        user = User.objects.filter(id=payload.get('id')).first()
        logger.info(f"Successfully decoded token. User: {user}")
        
        return user
    except jwt.ExpiredSignatureError:
        logger.error("Token has expired")
    except jwt.InvalidTokenError:
        logger.error("Invalid token")
    except Exception as e:
        logger.exception(f"Unexpected error occurred while decoding token: {str(e)}")
    
    return None

def auth_jwt(request):
    """
    Extract the user_id from the Authorization header in the request.
    
    Args:
        request: The request object containing the headers.
    
    Returns:
        int: The user_id if successfully extracted and decoded, None otherwise.
    """
    auth_header = request.headers.get('Authorization')
    logger.debug(f"Authorization header: {auth_header}")
    
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        logger.debug(f"Extracted token: {token[:10]}...")  # Log first 10 characters of token
        user_id = get_user_from_token(token)
        if user_id is not None:
            logger.info(f"Successfully authenticated user with ID: {user_id}")
            return user_id
        else:
            logger.warning("Could not extract user_id from token")
    else:
        logger.warning("No valid Authorization header found")
    return None

def get_user_id_by_username(username):
    """
    Find the user ID based on the username.
    
    Args:
        username (str): The username to search for.
    
    Returns:
        UUID: The user ID if found, None otherwise.
    """
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        user = User.objects.filter(username=username).first()
        if user:
            logger.info(f"User found: {username} with ID: {user.id}")
            return user.id
        
        logger.warning(f"No user found with username: {username}")
        return None
        
    except Exception as e:
        logger.exception(f"Error finding user by username: {str(e)}")
        return None

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow GET requests for all authenticated users
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return request.user.is_authenticated
        # For other methods (POST, PUT, DELETE), check if the user is admin
        return request.user.is_authenticated and request.user.role == 'admin'

    def has_object_permission(self, request, view, obj):
        # Similar to has_permission but for specific objects
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.role == 'admin'

