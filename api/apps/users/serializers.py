"""
User Serializers Module

This module provides serializers for user-related operations.
Includes serializers for:
- User registration and updates
- Token generation and validation
- Credential setup
"""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for CustomUser model.
    
    Handles user creation and updates with:
    - Password hashing
    - Optional email and role fields
    - Data validation
    """
    
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'password', 'role')
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': False},
            'role': {'required': False}
        }

    def create(self, validated_data):
        """Create a new user with encrypted password"""
        return CustomUser.objects.create_user(**validated_data)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer.
    
    Extends default JWT serializer to add:
    - User authentication status
    - Credential setup requirements
    - Custom token claims
    """
    
    def validate(self, attrs):
        """
        Validate user credentials and generate tokens.
        
        Returns:
            dict: Token data with authentication status
        
        Raises:
            ValidationError: If user not found or invalid credentials
        """
        username = attrs.get('username')
        user = CustomUser.objects.filter(username=username).first()
        
        if not user:
            raise serializers.ValidationError({"detail": "User not found"})
            
        # For users with existing credentials
        if user.is_authenticated:
            return super().validate(attrs)
        
        # For users without credentials
        self.user = user
        refresh = self.get_token(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'needs_setup': True,
            'message': 'Email and password setup required'
        }

    @classmethod
    def get_token(cls, user):
        """
        Generate token with custom claims.
        
        Args:
            user: The user to generate token for
            
        Returns:
            Token: JWT token with custom claims
        """
        token = super().get_token(user)
        token['has_password'] = bool(user.password)
        token['has_email'] = bool(user.email)
        token['is_authenticated'] = user.is_authenticated
        return token

class SetupCredentialsSerializer(serializers.Serializer):
    """
    Serializer for setting up user credentials.
    
    Handles:
    - Initial email and password setup
    - Credential validation
    - Authentication status update
    """
    
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, attrs):
        """
        Validate setup credentials request.
        
        Args:
            attrs: The credential data to validate
            
        Returns:
            dict: Validated data
            
        Raises:
            ValidationError: If user not found or already authenticated
        """
        username = attrs.get('username')
        user = CustomUser.objects.filter(username=username).first()

        if not user:
            raise serializers.ValidationError({"detail": "User not found"})

        if user.is_authenticated:
            raise serializers.ValidationError({"detail": "User is already authenticated"})

        return attrs

    def update(self, user, validated_data):
        """
        Update user credentials and generate new tokens.
        
        Args:
            user: The user to update
            validated_data: The validated credential data
            
        Returns:
            dict: Updated user data and tokens
        """
        email = validated_data.get('email')
        password = validated_data.get('password')

        user.email = email
        user.set_password(password)
        user.is_authenticated = True
        user.save()

        refresh = RefreshToken.for_user(user)
        
        return {
            'user': user,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
