"""
User ViewSets Module

This module provides API views for user management operations.
Includes viewsets for:
- User CRUD operations
- User search and filtering
- Admin-only operations

Features:
- Authentication required
- Admin role validation
- Logging of all operations
"""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser
from .serializers import UserSerializer
from api.utils.jwt_utils import IsAdminUser
from api.utils.logging_utils import log_exception, logger
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users.
    
    Provides endpoints for:
    - User creation and updates
    - User listing and retrieval
    - User deletion
    
    All operations require admin privileges.
    """
    
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    @log_exception
    def get_queryset(self):
        """
        Get list of users created by the current admin.
        
        Returns:
            QuerySet: Filtered users for the current admin
        """
        logger.debug(f"Retrieving users for admin: {self.request.user.username}")
        return CustomUser.objects.filter(created_by=self.request.user)
    
    @log_exception
    def perform_create(self, serializer):
        """
        Create a new user and assign current admin as creator.
        
        Args:
            serializer: Validated user serializer
            
        Raises:
            Exception: If user creation fails
        """
        try:
            user = serializer.save(created_by=self.request.user)
            logger.info(f"New user created by admin {self.request.user.username}: {user.username}")
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise
    
    @log_exception
    def perform_update(self, serializer):
        """
        Update existing user details.
        
        Args:
            serializer: Validated user serializer
            
        Raises:
            Exception: If user update fails
        """
        try:
            user = serializer.save()
            logger.info(f"User updated by admin {self.request.user.username}: {user.username}")
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            raise
    
    @log_exception
    def perform_destroy(self, instance):
        """
        Delete a user.
        
        Args:
            instance: User instance to delete
            
        Raises:
            Exception: If user deletion fails
        """
        try:
            username = instance.username
            instance.delete()
            logger.info(f"User deleted by admin {self.request.user.username}: {username}")
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            raise

    @action(detail=False, methods=['get'])
    def get_user(self, request):
        """
        Retrieve user information by ID.
        
        GET /api/users/get_user/?id=user-uuid
        
        Returns:
            Response: User details if found
            Response: Error message if not found
        """
        user_id = request.query_params.get('id')
        if not user_id:
            return Response(
                {"error": "id query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = CustomUser.objects.get(id=user_id)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
