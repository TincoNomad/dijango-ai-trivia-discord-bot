"""
Celery Tasks Module

This module contains Celery task definitions for asynchronous processing
in the Trivia API application.

Current Tasks:
- cleanup_logs_task: Automated log file maintenance

Note:
    Celery must be running to execute these tasks.
    See base.py for Celery activation instructions.

Usage:
    from api.tasks.task import cleanup_logs_task

    # Async execution
    cleanup_logs_task.delay()

    # Scheduled execution (via Celery Beat)
    # Configure in settings.CELERY_BEAT_SCHEDULE
"""

from celery import shared_task
from django.core.management import call_command


@shared_task(name="cleanup_logs_task")
def cleanup_logs_task():
    """
    Execute the log cleanup management command asynchronously.

    This task removes old log entries based on retention settings
    defined in Django settings (MONITORING configuration).

    Returns:
        bool: True if cleanup completed successfully

    Raises:
        CommandError: If cleanup command fails
    """
    call_command("cleanup_logs")
    return True
