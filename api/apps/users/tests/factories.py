"""
User Test Factories Module

This module provides factory classes for creating test data.
Uses Factory Boy to generate:
- Regular users
- Admin users
- Unauthenticated users
- Batch user creation
"""

import factory
from django.contrib.auth import get_user_model

from api.utils.logging_utils import log_exception

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating test User instances.

    Features:
    - Automatic username generation
    - Default password setting
    - Role-based user creation
    - Batch creation support
    """

    class Meta:
        model = User
        django_get_or_create = ("username",)

    username = factory.Sequence(lambda n: f"testuser_{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")
    role = "user"
    is_active = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """
        Override default creation method.

        Creates user with appropriate permissions based on role.

        Args:
            model_class: The model class to create
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments

        Returns:
            User: Created user instance
        """
        manager = cls._get_manager(model_class)

        # Extract important flags
        is_superuser = kwargs.pop("is_superuser", False)
        is_staff = kwargs.pop("is_staff", False)
        role = kwargs.get("role", "user")
        password = kwargs.pop("password", "testpass123")

        # Create user based on permissions
        if is_superuser or role == "admin":
            user = manager.create_superuser(*args, password=password, **kwargs)
        else:
            user = manager.create_user(*args, password=password, **kwargs)

        # Assign additional permissions
        user.is_staff = is_staff or is_superuser
        user.is_superuser = is_superuser
        user.save()

        return user

    @classmethod
    @log_exception
    def create_admin(cls, **kwargs):
        """
        Create an admin user.

        Returns:
            User: Created admin user instance
        """
        kwargs.update({"role": "admin", "is_staff": True, "is_superuser": True})
        return cls.create(**kwargs)

    @classmethod
    @log_exception
    def create_regular_user(cls, **kwargs):
        """
        Create a regular user.

        Returns:
            User: Created regular user instance
        """
        kwargs.update({"role": "user", "is_staff": False, "is_superuser": False})
        return cls.create(**kwargs)

    @classmethod
    @log_exception
    def create_unauthenticated_user(cls, **kwargs):
        """
        Create an unauthenticated user.

        Returns:
            User: Created unauthenticated user instance
        """
        kwargs.update({"is_authenticated": False, "password": "", "email": ""})
        return cls.create(**kwargs)

    @classmethod
    @log_exception
    def create_batch_users(cls, size=3, **kwargs):
        """
        Create multiple users.

        Args:
            size: Number of users to create
            **kwargs: Additional user attributes

        Returns:
            list[User]: List of created users
        """
        return cls.create_batch(size=size, **kwargs)
