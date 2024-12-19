import pytest
from .test_score_base import BaseScoreTest, ScoreTestMixin

@pytest.mark.django_db
class TestScoreCreation(BaseScoreTest, ScoreTestMixin):
    """Tests para la creación de scores"""

    @pytest.fixture(autouse=True)
    def setup_method(self, test_user, test_leaderboard):
        """Setup para cada test"""
        self.setup_test_data()
        self.url = '/api/score/'

    def setup_test_data(self):
        """Configurar datos iniciales"""
        pass

    def teardown_test_data(self):
        """Limpiar datos después del test"""
        pass

    def test_create_score_success(self, api_client_authenticated, valid_score_data):
        """Test creación exitosa de score"""
        # Arrange
        score_data = valid_score_data

        # Act
        response = api_client_authenticated.post(
            self.url,
            data=score_data,
            format='json'
        )

        # Assert
        self.assert_score_response(response, 200)
        assert response.data['data']['points'] == score_data['points']

    def test_create_score_invalid_points(self, api_client_authenticated, valid_score_data):
        """Test creación de score con puntos inválidos"""
        # Arrange
        invalid_data = valid_score_data.copy()
        invalid_data['points'] = -100

        # Act
        response = api_client_authenticated.post(
            self.url,
            data=invalid_data,
            format='json'
        )

        # Assert
        self.assert_score_response(response, 400, check_data=False)
        assert 'error' in response.data