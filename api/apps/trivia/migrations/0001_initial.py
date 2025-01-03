# Generated by Django 5.1.2 on 2024-12-31 22:02

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Language",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=100, unique=True, verbose_name="Name"
                    ),
                ),
                (
                    "code",
                    models.CharField(
                        max_length=2, unique=True, verbose_name="Language Code"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Question",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "question_title",
                    models.CharField(
                        max_length=250,
                        null=True,
                        verbose_name="Question Title",
                    ),
                ),
                (
                    "points",
                    models.SmallIntegerField(
                        default=10, verbose_name="Points"
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True, verbose_name="Is Active"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Created"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Updated"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Theme",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=100, unique=True, verbose_name="Name"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Trivia",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "title",
                    models.CharField(max_length=250, verbose_name="Title"),
                ),
                (
                    "is_public",
                    models.BooleanField(
                        default=True,
                        help_text="Determines if the trivia is visible to all users",
                        verbose_name="Is Public",
                    ),
                ),
                (
                    "difficulty",
                    models.IntegerField(
                        choices=[
                            (1, "Beginner"),
                            (2, "Intermediate"),
                            (3, "Advanced"),
                        ],
                        verbose_name="Difficulty",
                    ),
                ),
                (
                    "url",
                    models.URLField(blank=True, null=True, verbose_name="URL"),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Created"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Updated"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Answer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "answer_title",
                    models.CharField(
                        max_length=2502, null=True, verbose_name="Answer Title"
                    ),
                ),
                (
                    "is_correct",
                    models.BooleanField(
                        default=False, verbose_name="Correct Answer"
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True, verbose_name="Is Active"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Created"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Updated"
                    ),
                ),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="answers",
                        to="trivia.question",
                        verbose_name="Question",
                    ),
                ),
            ],
        ),
    ]
