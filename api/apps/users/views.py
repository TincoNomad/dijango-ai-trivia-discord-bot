"""
User Views Module

This module provides API views for user authentication and management.
Includes views for:
- User registration
- Login/Logout handling
- User creation
- Credential setup
- User profile access

Features:
- JWT token authentication
- Error logging
- Response standardization
"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserSerializer, SetupCredentialsSerializer
from api.utils.logging_utils import log_exception, logger
from rest_framework.views import APIView
from api.apps.users.models import CustomUser

class RegisterView(generics.CreateAPIView):
    """
    View for user registration.
    
    Creates new users with admin role.
    Includes automatic logging of registration events.
    """
    
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        """
        Create a new user with admin role.
        
        Args:
            serializer: Validated user serializer
            
        Returns:
            User: Created user instance
            
        Raises:
            Exception: If user creation fails
        """
        try:
            user = serializer.save(role='admin')
            logger.info(f"New user registered: {user.username}")
            return user
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise

class LoginView(TokenObtainPairView):
    """
    View for user login.
    
    Handles:
    - Credential validation
    - Token generation
    - Password verification
    """
    
    @log_exception
    def post(self, request, *args, **kwargs):
        """
        Process login request.
        
        Verifies user exists and has password set.
        
        Returns:
            Response: JWT tokens if successful
            Response: Error details if login fails
        """
        try:
            username = request.data.get('username')
            user = CustomUser.objects.filter(username=username).first()
            
            if user and not user.password:
                return Response(
                    {"detail": "Password not configured for this user"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            response = super().post(request, *args, **kwargs)
            logger.info(f"User logged in: {username}")
            return response
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            raise

class LogoutView(generics.GenericAPIView):
    """
    View for user logout.
    
    Requires authentication.
    Logs logout events.
    """
    
    permission_classes = [permissions.IsAuthenticated]

    @log_exception
    def post(self, request):
        """
        Process logout request.
        
        Returns:
            Response: Success status if logout successful
            Response: Error status if logout fails
        """
        try:
            logger.info(f"User logged out: {request.user.username}")
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response(status=status.HTTP_400_BAD_REQUEST)

class CreateUserView(APIView):
    """
    View for creating new users.
    
    Creates users with basic information,
    requiring later credential setup.
    """
    
    def post(self, request):
        """
        Create a new user with basic information.
        
        Returns:
            Response: Created user details and status
            Response: Error details if creation fails
        """
        data = {
            'username': request.data.get('username'),
            'role': 'user'
        }
        
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'User created successfully',
                'id': user.id,
                'username': user.username,
                'status': 'PENDING_SETUP'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SetupCredentialsView(APIView):
    """
    View for setting up user credentials.
    
    Handles initial setup of:
    - Email
    - Password
    - Authentication status
    """

    @log_exception
    def post(self, request):
        """
        Process credential setup request.
        
        Returns:
            Response: Success message and new tokens
            Response: Error details if setup fails
        """
        try:
            serializer = SetupCredentialsSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            user = CustomUser.objects.get(username=request.data['username'])
            result = serializer.update(user, serializer.validated_data)

            return Response({
                'message': 'Credentials configured successfully',
                'refresh': result['refresh'],
                'access': result['access'],
            })
        except CustomUser.DoesNotExist:
            return Response(
                {'detail': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error setting up credentials: {str(e)}")
            raise

class MeView(APIView):
    """
    View for retrieving current user information.
    
    Requires authentication.
    Returns serialized user data.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """
        Get current user information.
        
        Returns:
            Response: Serialized user data
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
