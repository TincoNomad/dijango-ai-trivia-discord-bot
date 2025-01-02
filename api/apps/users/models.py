"""
User Models Module

This module defines the custom user model and related functionality.
Extends Django's AbstractUser to add:
- Custom fields for user roles
- Email verification
- Login attempt tracking
"""

import uuid

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext as _


class CustomUser(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.

    Adds additional fields and functionality:
    - UUID primary key
    - Role-based access control
    - Email verification
    - Login attempt tracking

    Attributes:
        id (UUID): Unique identifier
        role (str): User role (user/admin)
        is_verified (bool): Email verification status
        login_attempts (int): Failed login attempt counter
    """

    ROLES = [("user", _("Regular User")), ("admin", _("Administrator"))]

    # Base fields
    email = models.EmailField(_("email address"), blank=True, null=True)
    password = models.CharField(_("password"), max_length=128, blank=True, null=True)

    # Username with custom validation
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[\w#]+$",
                message=_(
                    "Enter a valid username. This value may contain only letters, "
                    "numbers, underscore and # characters."
                ),
            ),
        ],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )

    # Custom fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_verified = models.BooleanField(_("Email Verified"), default=False)
    login_attempts = models.IntegerField(_("Login Attempts"), default=0)
    role = models.CharField(_("Role"), max_length=20, choices=ROLES, default="user")
    created_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_users",
        verbose_name=_("Created By"),
    )
    is_authenticated = models.BooleanField(_("Is Authenticated"), default=False)

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def save(self, *args, **kwargs):
        """
        Override save method to handle authentication status.
        Sets is_authenticated to False if no password is set.
        """
        if not self.password:
            self.is_authenticated = False
        super().save(*args, **kwargs)
