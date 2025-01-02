"""
Theme Test Module

This module contains test cases for:
- Theme listing
- Theme validation
- Theme-related error handling
"""

import uuid

import pytest
from django.urls import reverse

from api.apps.trivia.models import Theme


@pytest.mark.django_db
class TestThemes:
    """Test cases for theme-related operations"""

    def test_list_themes(self, api_client):
        """Test listing all available themes"""
        url = reverse("theme-list")
        response = api_client.get(url)
        assert response.status_code == 200

    def test_list_empty_themes(self, api_client):
        """Test listing themes when none exist"""
        Theme.objects.all().delete()
        url = reverse("theme-list")
        response = api_client.get(url)
        assert response.status_code == 200
        assert len(response.data) == 0

    def test_filter_trivias_nonexistent_theme(self, api_client):
        """Test filtering trivias with non-existent theme"""
        nonexistent_uuid = str(uuid.uuid4())
        url = reverse("trivia-filter-trivias")
        response = api_client.get(f"{url}?theme={nonexistent_uuid}&difficulty=1")
        assert response.status_code == 404
        assert "Theme not found" in str(response.data["error"])
