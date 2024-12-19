import pytest
from .test_score_base import TestScoreBase
from .test_data import TEST_SCORE_DATA

@pytest.mark.django_db
class TestScoreCreation(TestScoreBase):
    """Tests para la creación de scores"""

    @pytest.fixture(autouse=True)
    def setup_method(self, test_user, test_leaderboard):
        """Setup para cada test"""
        self.url = '/api/score/'
        self.valid_data = TEST_SCORE_DATA['valid_score'].copy()
        self.valid_data['username'] = test_user.username
        self.valid_data['discord_channel'] = test_leaderboard.discord_channel

    def test_create_score_success(self, api_client_authenticated):
        """Test creación exitosa de score"""
        response = api_client_authenticated.post(
            self.url,
            data=self.valid_data,
            format='json'
        )
        assert response.status_code == 200

    def test_create_score_invalid_points(self, api_client_authenticated):
        """Test creación de score con puntos inválidos"""
        invalid_data = self.valid_data.copy()
        invalid_data['points'] = -100
        response = api_client_authenticated.post(
            self.url,
            data=invalid_data,
            format='json'
        )
        assert response.status_code == 400

    def test_create_score_missing_fields(self, api_client_authenticated):
        """Test creación de score sin campos requeridos"""
        invalid_data = {'name': 'Test'}
        response = api_client_authenticated.post(
            self.url,
            data=invalid_data,
            format='json'
        )
        assert response.status_code == 400