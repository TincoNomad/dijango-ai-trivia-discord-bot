from django.db import models
from django.utils.translation import gettext as _
from django.conf import settings
from django.core.exceptions import ValidationError
import uuid


# Course model representing different courses available
class Trivia(models.Model):
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
    is_public = models.BooleanField(_('Is Public'), default=True, help_text=_('Determines if the trivia is visible to all users'))
    difficulty = models.IntegerField(_('Difficulty'), choices=DIFFICULTY_CHOICES)
    theme = models.ForeignKey('Theme', on_delete=models.CASCADE, related_name='trivias', verbose_name=_('Theme'))
    url = models.URLField(_('URL'), null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL,  # If the user is deleted, the trivia remains
        related_name='trivias_created', 
        verbose_name=_('Created By'),
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(_('Created'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated'), auto_now=True)

    def clean(self):
        if self.questions.count() < 3:
            raise ValidationError(_('The trivia must have at least 3 questions.'))

    def __str__(self):
        return self.title

    class Meta:
        # Add uniqueness constraint
        constraints = [
            models.UniqueConstraint(
                fields=['title'],
                name='unique_trivia_title'
            )
        ]

class Theme(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('Name'), max_length=100, unique=True)

    def __str__(self):
        return self.name

# Question model representing questions for each course
class Question(models.Model):
    trivia = models.ForeignKey(Trivia, related_name='questions', verbose_name=_('Trivia'), on_delete=models.CASCADE, null=True)
    question_title = models.CharField(_('Question Title'), max_length=250, null=True)
    points = models.SmallIntegerField(_('Points'), default=10)
    is_active = models.BooleanField(_('Is Active'), default=True)
    created_at = models.DateTimeField(_('Created'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated'), auto_now=True)

    def __str__(self):
        return self.question_title

# Answer model representing answers for each question
class Answer(models.Model):
    trivia = models.ForeignKey(Trivia, related_name='answers', verbose_name=_('Trivia'), on_delete=models.CASCADE, null=True)
    question = models.ForeignKey(Question, related_name='answers', verbose_name=_('Question'), on_delete=models.CASCADE)
    answer_title = models.CharField(_('Answer Title'), max_length=2502, null=True)
    is_correct = models.BooleanField(_('Correct Answer'), default=False)
    is_active = models.BooleanField(_('Is Active'), default=True)
    created_at = models.DateTimeField(_('Created'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated'), auto_now=True)

    def __str__(self):
        return self.answer_title
