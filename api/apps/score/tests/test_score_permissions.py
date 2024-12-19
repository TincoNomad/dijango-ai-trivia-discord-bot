import pytest
from django.urls import reverse
from .test_score_base import TestScoreBase
from .test_data import TEST_LEADERBOARD_DATA

@pytest.mark.django_db
class TestScorePermissions(TestScoreBase):
    """Tests para permisos de score"""

    @pytest.fixture(autouse=True)
    def setup_method(self, test_user):
        """Setup para cada test"""
        self.url = reverse('leaderboard-list')
        self.valid_data = TEST_LEADERBOARD_DATA['valid_leaderboard'].copy()
        self.valid_data['username'] = test_user.username

    def test_create_leaderboard_requires_auth(self, api_client):
        """Test que crear leaderboard requiere autenticación"""
        response = api_client.post(self.url, self.valid_data)
        assert response.status_code == 400

    def test_create_leaderboard_success(self, api_client_authenticated):
        """Test creación exitosa de leaderboard"""
        response = api_client_authenticated.post(
            self.url, 
            data=self.valid_data,
            format='json'
        )
        assert response.status_code == 200