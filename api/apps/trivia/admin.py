"""
Trivia Admin Configuration Module

This module configures the Django admin interface for trivia-related models.
Includes admin configurations for:
- Trivia management
- Theme management
- Question management
- Answer management

Features:
- Inline editing for questions and answers
- Custom list displays
- Field grouping
"""

from django.contrib import admin

from . import models

#Table union Question + Answers
class AnswerInlineModel(admin.TabularInline):
    """
    Inline admin for answers within questions.
    Allows editing answers directly in question admin.
    """
    model = models.Answer
    fields = [
        'answer_title',
        'is_correct',
    ]
    extra = 0

#Table union Trivia + Question
class QuestionInLineModel(admin.TabularInline):
    """
    Inline admin for questions within trivias.
    Allows editing questions directly in trivia admin.
    """
    model = models.Question
    fields = [
        'question_title',
    ]
    extra = 0

#Trivias
@admin.register(models.Trivia)
class TriviaAdmin(admin.ModelAdmin):
    """
    Admin configuration for Trivia model.
    
    Features:
    - Basic trivia information fields
    - Inline question editing
    - Custom list display
    """
    fields = [
        'title',
        'difficulty',
        'theme',
        'url',
    ]
    list_display = [
        'title',
        'difficulty',
        'theme',
    ]
    inlines = [QuestionInLineModel,]

#Themes
@admin.register(models.Theme)
class ThemeAdmin(admin.ModelAdmin):
    """
    Admin configuration for Theme model.
    Simple display of theme names.
    """
    list_display = ['name']

#Questions
@admin.register(models.Question)
class QuestionAdmin(admin.ModelAdmin):
    """
    Admin configuration for Question model.
    
    Features:
    - Question details fields
    - Inline answer editing
    - Update tracking
    """
    fields = [
        'trivia',
        'question_title',
    ]
    list_display = [
        'question_title',
        'trivia',
        'updated_at',
    ]
    inlines = [AnswerInlineModel,]

#Answers
@admin.register(models.Answer)
class AnswerAdmin(admin.ModelAdmin):
    """
    Admin configuration for Answer model.
    
    Features:
    - Answer details display
    - Correct answer indication
    - Question relationship
    """
    list_display = [
        'answer_title',
        'is_correct',
        'question',
    ]
    
