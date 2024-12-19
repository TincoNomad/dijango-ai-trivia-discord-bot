import pytest
from django.urls import reverse
from .test_score_base import BaseScoreTest, LeaderboardTestMixin

@pytest.mark.django_db
class TestScorePermissions(BaseScoreTest, LeaderboardTestMixin):
    """Tests para permisos de score"""

    @pytest.fixture(autouse=True)
    def setup_method(self, test_user):
        """Setup para cada test"""
        self.setup_test_data()
        self.url = '/api/leaderboards/'  # ✅ Corregir URL (plural)

    def setup_test_data(self):
        """Configurar datos iniciales"""
        pass

    def teardown_test_data(self):
        """Limpiar datos después del test"""
        pass

    def test_create_leaderboard_requires_auth(self, api_client, valid_score_data):
        """Test que crear leaderboard requiere autenticación"""
        # Act
        response = api_client.post(self.url, valid_score_data)
        
        # Assert
        self.assert_leaderboard_response(response, 400)

    def test_create_leaderboard_success(self, api_client_authenticated, valid_score_data):
        """Test creación exitosa de leaderboard con autenticación"""
        # Act
        response = api_client_authenticated.post(
            self.url,
            data=valid_score_data,
            format='json'
        )

        # Assert
        self.assert_leaderboard_response(response, 200)