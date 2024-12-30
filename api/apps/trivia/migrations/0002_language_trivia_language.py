# Generated by Django 5.1.2 on 2024-12-30 17:57

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trivia', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Name')),
                ('code', models.CharField(max_length=2, unique=True, verbose_name='Language Code')),
            ],
        ),
        migrations.AddField(
            model_name='trivia',
            name='language',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='trivias', to='trivia.language', verbose_name='Language'),
        ),
    ]
