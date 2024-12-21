"""
Trivia Models Module

This module defines the database models for the trivia system.
Includes models for:
- Trivia management
- Theme categorization
- Question handling
- Answer tracking

Features:
- UUID primary keys
- Model validation
- Relationship constraints
- Multilingual support
"""

from django.db import models
from django.utils.translation import gettext as _
from django.conf import settings
from django.core.exceptions import ValidationError
import uuid

class Trivia(models.Model):
    """
    Model for trivia games.
    
    Features:
    - Difficulty levels
    - Public/private access
    - Theme categorization
    - Question limits
    
    Attributes:
        MAX_QUESTIONS (int): Maximum questions allowed (5)
        MIN_QUESTIONS (int): Minimum questions required (3)
        MAX_ANSWERS (int): Maximum answers per question (5)
        MIN_ANSWERS (int): Minimum answers per question (2)
    """
    
    MAX_QUESTIONS = 5
    MIN_QUESTIONS = 3
    MAX_ANSWERS = 5
    MIN_ANSWERS = 2
    DIFFICULTY_CHOICES = [
        (1, _('Beginner')),
        (2, _('Intermediate')),
        (3, _('Advanced')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_('Title'), max_length=250)
    is_public = models.BooleanField(
        _('Is Public'), 
        default=True, 
        help_text=_('Determines if the trivia is visible to all users')
    )
    difficulty = models.IntegerField(_('Difficulty'), choices=DIFFICULTY_CHOICES)
    theme = models.ForeignKey(
        'Theme', 
        on_delete=models.CASCADE, 
        related_name='trivias', 
        verbose_name=_('Theme')
    )
    url = models.URLField(_('URL'), null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL,  # If user is deleted, trivia remains
        related_name='trivias_created', 
        verbose_name=_('Created By'),
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(_('Created'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated'), auto_now=True)

    def clean(self):
        """
        Validate trivia data.
        
        Raises:
            ValidationError: If minimum question requirement not met
        """
        if self.questions.count() < 3:
            raise ValidationError(_('The trivia must have at least 3 questions.'))

    def __str__(self):
        """String representation of trivia"""
        return self.title

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['title'],
                name='unique_trivia_title'
            )
        ]

class Theme(models.Model):
    """
    Model for trivia themes.
    
    Features:
    - UUID primary key
    - Unique theme names
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('Name'), max_length=100, unique=True)

    def __str__(self):
        """String representation of theme"""
        return self.name

class Question(models.Model):
    """
    Model for trivia questions.
    
    Features:
    - Points system
    - Active/inactive status
    - Creation tracking
    """
    
    trivia = models.ForeignKey(
        Trivia, 
        related_name='questions', 
        verbose_name=_('Trivia'), 
        on_delete=models.CASCADE, 
        null=True
    )
    question_title = models.CharField(_('Question Title'), max_length=250, null=True)
    points = models.SmallIntegerField(_('Points'), default=10)
    is_active = models.BooleanField(_('Is Active'), default=True)
    created_at = models.DateTimeField(_('Created'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated'), auto_now=True)

    def __str__(self):
        """String representation of question"""
        return self.question_title

class Answer(models.Model):
    """
    Model for question answers.
    
    Features:
    - Correct answer marking
    - Active/inactive status
    - Creation tracking
    """
    
    trivia = models.ForeignKey(
        Trivia, 
        related_name='answers', 
        verbose_name=_('Trivia'), 
        on_delete=models.CASCADE, 
        null=True
    )
    question = models.ForeignKey(
        Question, 
        related_name='answers', 
        verbose_name=_('Question'), 
        on_delete=models.CASCADE
    )
    answer_title = models.CharField(_('Answer Title'), max_length=2502, null=True)
    is_correct = models.BooleanField(_('Correct Answer'), default=False)
    is_active = models.BooleanField(_('Is Active'), default=True)
    created_at = models.DateTimeField(_('Created'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated'), auto_now=True)

    def __str__(self):
        """String representation of answer"""
        return self.answer_title
