"""
User Admin Configuration Module

This module configures the Django admin interface for user management.
Extends the default Django UserAdmin with custom fields and displays.

Features:
- Custom user list display
- Role and verification filters
- Additional custom fields
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Admin configuration for CustomUser model.
    
    Extends Django's UserAdmin to include:
    - Role and verification status in list display
    - Custom field grouping
    - Additional filters
    """
    
    list_display = ('username', 'email', 'role', 'is_verified', 'login_attempts')
    list_filter = ('role', 'is_verified')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'is_verified', 'login_attempts')}),
    )
