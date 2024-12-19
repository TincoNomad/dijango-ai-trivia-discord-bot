"""
Test suite for the trivia app.
Contains test cases for trivia-related functionality.
"""

import pytest
from django.urls import reverse
from api.apps.trivia.models import Trivia, Theme
from api.apps.users.models import CustomUser
from .test_data import TEST_TRIVIA_DATA, ERROR_MESSAGES
import uuid
from api.apps.trivia.tests.factories import QuestionFactory, AnswerFactory, TriviaFactory, InvalidTriviaFactory, UserFactory, PrivateTriviaFactory, ConcurrentTriviaFactory
from concurrent.futures import ThreadPoolExecutor
import threading
from rest_framework.test import APIClient

@pytest.mark.django_db
class TestTriviaBase:
    """Base class for trivia tests with common helper methods"""
    
    def create_question_with_answers(self, trivia):
        """Helper method to create question with answers using factories"""
        question = QuestionFactory(trivia=trivia)
        AnswerFactory.create_batch(2, question=question)
        return question

    @staticmethod
    def assert_trivia_matches_input(trivia, input_data):
        """Helper method to validate trivia data matches input"""
        assert trivia.title == input_data['title']
        assert trivia.difficulty == input_data['difficulty']
        assert trivia.theme.name == input_data['theme']
        assert trivia.questions.count() == len(input_data['questions'])

@pytest.mark.django_db
class TestTriviaCreation(TestTriviaBase):
    """
    Test cases for trivia creation.
    
    This class contains all test cases related to creating new trivias,
    including validations and error cases.
    """

    @pytest.fixture(autouse=True)
    def setup_method(self, test_user, test_theme):
        """
        Initial setup for each test.
        
        Args:
            test_user: Test user fixture
            test_theme: Test theme fixture
        """
        self.url = reverse('trivia-list')
        self.valid_data = TEST_TRIVIA_DATA['valid_trivia'].copy()
        self.user = test_user
        self.theme = test_theme

    @staticmethod
    def assert_trivia_matches_input(trivia, input_data):
        """
        Helper method to validate trivia data matches input.
        
        Args:
            trivia: Trivia instance to validate
            input_data: Dictionary containing input data
        """
        assert trivia.title == input_data['title'], "Title should match input"
        assert trivia.difficulty == input_data['difficulty'], "Difficulty should match input"
        assert trivia.theme.name == input_data['theme'], "Theme should match input"
        assert trivia.questions.count() == len(input_data['questions']), \
            "Question count should match input"

    def test_trivia_creation_should_succeed_with_valid_data(self, api_client_authenticated):
        """Test successful trivia creation"""
        trivia_data = TEST_TRIVIA_DATA['valid_trivia'].copy()
        trivia_data['theme'] = self.theme.id
        trivia_data['username'] = self.user.username
        
        response = api_client_authenticated.post(self.url, trivia_data, format='json')
        assert response.status_code == 201

    def test_trivia_creation_should_fail_with_duplicate_title(self, api_client_authenticated):
        """Test duplicate title handling"""
        # Crear primera trivia
        trivia = TriviaFactory.create()
        
        # Intentar crear trivia con el mismo título
        duplicate_data = {
            'title': trivia.title,
            'difficulty': trivia.difficulty,
            'theme': trivia.theme.id,
            'is_public': trivia.is_public,
            'questions': [
                {
                    'question_title': 'Test Question',
                    'answers': [
                        {'answer_title': 'Answer 1', 'is_correct': True},
                        {'answer_title': 'Answer 2', 'is_correct': False}
                    ]
                }
            ]
        }
        
        response = api_client_authenticated.post(self.url, duplicate_data, format='json')
        assert response.status_code == 400
        assert ERROR_MESSAGES['DUPLICATE_TITLE'] in str(response.data)

    def test_create_trivia_invalid_difficulty(self, api_client_authenticated):
        """Test creating trivia with invalid difficulty fails"""
        invalid_trivia = InvalidTriviaFactory.build()
        invalid_data = {
            'title': invalid_trivia.title,
            'difficulty': invalid_trivia.difficulty,  # Este es 5, que es inválido
            'theme': self.theme.id,
            'is_public': invalid_trivia.is_public,
            'questions': [
                {
                    'question_title': 'Test Question',
                    'answers': [
                        {'answer_title': 'Answer 1', 'is_correct': True},
                        {'answer_title': 'Answer 2', 'is_correct': False}
                    ]
                }
            ]
        }
        
        response = api_client_authenticated.post(self.url, invalid_data, format='json')
        assert response.status_code == 400
        assert ERROR_MESSAGES['INVALID_DIFFICULTY'] in str(response.data)

    def test_trivia_creation_should_fail_when_user_not_authenticated(self, api_client):
        """
        Test that unauthenticated users cannot create trivia.
        
        Steps:
        1. Remove authentication credentials
        2. Attempt to create trivia
        3. Verify unauthorized error response
        
        Assertions:
        - Request fails with 400 status
        - Error message indicates user validation failure
        """
        api_client.credentials()
        api_client.force_authenticate(user=None)
        
        invalid_data = self.valid_data.copy()
        invalid_data['username'] = 'nonexistent_user'
        
        response = api_client.post(self.url, invalid_data, format='json')
        assert response.status_code == 400, "Should fail with validation error"
        assert "No user exists with this username" in str(response.data), \
            "Should indicate user validation failure"

    @pytest.mark.parametrize("test_data,expected_status,expected_error", [
        ({
            'title': 'Test Trivia',
            'difficulty': 1,
            'theme': 'Python',
            'username': 'testuser',
            'questions': []
        }, 400, ERROR_MESSAGES['NO_QUESTIONS']),
        ({
            'title': 'Test Trivia',
            'difficulty': 5,
            'theme': 'Python',
            'username': 'testuser',
            'questions': TEST_TRIVIA_DATA['valid_trivia']['questions']
        }, 400, ERROR_MESSAGES['INVALID_DIFFICULTY']),
        ({
            'title': '',
            'difficulty': 1,
            'theme': 'Python',
            'username': 'testuser',
            'questions': TEST_TRIVIA_DATA['valid_trivia']['questions']
        }, 400, 'This field may not be blank.'),
    ])
    def test_trivia_creation_validations(self, api_client, test_data, expected_status, expected_error):
        """
        Test different validation scenarios for trivia creation.
        
        Args:
            api_client: Test API client
            test_data: Test data for each case
            expected_status: Expected HTTP status code
            expected_error: Expected error message
        
        Test cases:
        1. Trivia without questions
        2. Trivia with invalid difficulty
        3. Trivia with empty title
        
        Assertions:
        - Correct status code
        - Appropriate error message
        """
        response = api_client.post(self.url, test_data, format='json')
        assert response.status_code == expected_status, \
            f"Status code should be {expected_status}"
        assert expected_error in str(response.data), \
            f"Response should contain error: {expected_error}"

@pytest.mark.django_db
class TestTriviaQueries(TestTriviaBase):
    """
    Test cases for trivia query operations.
    
    This class contains all test cases related to retrieving and filtering trivias,
    including public/private access and theme-based filtering.
    """

    @pytest.fixture(autouse=True)
    def setup_method(self, test_theme):
        """
        Initial setup for each test.
        
        Args:
            test_theme: Test theme fixture
        """
        self.theme = test_theme

    @staticmethod
    def assert_filter_response_valid(response):
        """
        Helper method to validate filter response.
        
        Args:
            response: API response to validate
        """
        # Status validation
        assert response.status_code == 200, "Should return successful response"
        
        # Data structure validation
        assert isinstance(response.data, list), "Should return list of trivias"
        
        # Data content validation
        for trivia in response.data:
            TestTriviaQueries.assert_trivia_structure_valid(trivia)

    @staticmethod
    def assert_trivia_structure_valid(trivia_data):
        """
        Helper method to validate trivia data structure.
        
        Args:
            trivia_data: Dictionary containing trivia data
        """
        required_fields = ['id', 'title', 'difficulty', 'theme', 'is_public']
        for field in required_fields:
            assert field in trivia_data, f"Missing required field: {field}"

    def test_list_public_trivias(self, api_client, test_user):
        """
        Test listing of public trivias.
        
        Steps:
        1. Create sample public trivias
        2. Request trivia list endpoint
        3. Verify response
        
        Assertions:
        - Successful response (200)
        - Only public trivias are returned
        """
        response = api_client.get(reverse('trivia-list'))
        assert response.status_code == 200, "Should return successful response"

    def test_filter_trivias_by_theme(self, api_client):
        """Test filtering trivias by theme and difficulty"""
        # Given: URL with filter parameters
        url = reverse('trivia-filter-trivias')
        
        # When: Send GET request with filters
        response = api_client.get(f"{url}?theme={self.theme.id}&difficulty=1")
        
        # Then: Response validation
        self.assert_filter_response_valid(response)

@pytest.mark.django_db(transaction=True)
class TestTriviaUpdates(TestTriviaBase):
    """
    Test cases for trivia update operations.
    
    This class tests all aspects of updating existing trivias, including
    permission checks, validation, and partial updates.
    """

    @pytest.fixture(autouse=True)
    def setup_method(self, test_user, test_theme):
        """
        Initial setup for each test.
        
        Args:
            test_user: Test user fixture
            test_theme: Test theme fixture
            
        Creates:
        - Test user with admin role
        - Sample trivia for testing updates
        """
        test_user.role = 'admin'
        test_user.is_authenticated = True
        test_user.save()
        
        self.theme = test_theme
        self.trivia = Trivia.objects.create(
            title='Test Trivia',
            difficulty=1,
            theme=test_theme,
            created_by=test_user,
            is_public=True
        )
        self.url = reverse('trivia-detail', args=[self.trivia.id])

    @staticmethod
    def assert_trivia_update_successful(trivia, update_data):
        """
        Helper method to validate trivia update.
        
        Args:
            trivia: Updated trivia instance
            update_data: Dictionary containing update data
        """
        assert trivia.title == update_data['title'], "Title should be updated"
        assert trivia.difficulty == update_data['difficulty'], "Difficulty should be updated"
        assert trivia.is_public == update_data['is_public'], "Public status should be updated"

    def test_trivia_update_should_succeed_when_user_is_authenticated_and_owner(self, api_client, test_user):
        """Test that trivia title can be updated by authenticated owner"""
        trivia = TriviaFactory.create_with_questions(created_by=test_user)
        url = reverse('trivia-detail', args=[trivia.id])
        
        api_client.force_authenticate(user=test_user)
        update_data = TEST_TRIVIA_DATA['update_data']['basic'].copy()
        update_data['username'] = test_user.username
        
        response = api_client.patch(url, update_data, format='json')
        assert response.status_code == 200, "Update should succeed"
        trivia.refresh_from_db()
        assert trivia.title == update_data['title'], "Title should be updated"

    def test_update_trivia_unauthorized(self, api_client):
        """
        Test unauthorized trivia update attempt.
        
        Steps:
        1. Attempt update without authentication
        2. Verify unauthorized response
        
        Assertions:
        - Unauthorized response (401)
        - Appropriate error message
        """
        response = api_client.patch(
            self.url,
            TEST_TRIVIA_DATA['update_data']['basic'],
            format='json'
        )
        assert response.status_code == 401, "Should return unauthorized status"
        assert ERROR_MESSAGES['UNAUTHORIZED'] in str(response.data), \
            "Should return unauthorized error message"

    def test_update_trivia_by_non_creator(self, api_client):
        """Test updating trivia by non-creator fails"""
        other_user = CustomUser.objects.create_user(
            username='other_user',
            password='testpass123'
        )
        api_client.force_authenticate(user=other_user)
        response = api_client.patch(
            self.url,
            TEST_TRIVIA_DATA['update_data']['basic'],
            format='json'
        )
        assert response.status_code == 403
        assert ERROR_MESSAGES['FORBIDDEN'] in str(response.data)

    def test_update_trivia_questions(self, api_client, test_user):
        """Test updating trivia questions"""
        # Create initial question with answers
        question = self.create_question_with_answers(self.trivia)
        
        # Authenticate user
        api_client.force_authenticate(user=test_user)
        
        # Update question data
        questions_data = TEST_TRIVIA_DATA['update_data']['questions'].copy()
        questions_data['questions'][0]['id'] = str(question.id)
        
        url = reverse('trivia-update-questions', args=[self.trivia.id])
        response = api_client.patch(url, questions_data, format='json')
        
        assert response.status_code == 200
        question.refresh_from_db()
        assert question.question_title == 'Updated Question'

    def test_full_trivia_update(self, api_client, test_user):
        """Test full trivia update with PATCH"""
        api_client.force_authenticate(user=test_user)
        update_data = {
            'title': 'Fully Updated Trivia',
            'difficulty': 2,
            'is_public': False,
            'username': test_user.username
        }
        
        response = api_client.patch(self.url, update_data, format='json')
        
        assert response.status_code == 200, "Should return successful response"
        self.trivia.refresh_from_db()
        self.assert_trivia_update_successful(self.trivia, update_data)

    def test_delete_trivia_unauthorized(self, api_client):
        """Test deleting trivia without authentication fails"""
        response = api_client.delete(self.url)
        assert response.status_code == 401, "Should return unauthorized status"
        assert ERROR_MESSAGES['UNAUTHORIZED'] in str(response.data)

    def test_delete_trivia_by_non_creator(self, api_client):
        """Test deleting trivia by non-creator fails"""
        other_user = CustomUser.objects.create_user(
            username='other_user',
            password='testpass123'
        )
        api_client.force_authenticate(user=other_user)
        response = api_client.delete(self.url)
        assert response.status_code == 403, "Should return forbidden status"
        assert ERROR_MESSAGES['FORBIDDEN'] in str(response.data)

@pytest.mark.django_db
class TestTriviaEdgeCases(TestTriviaBase):
    """
    Tests for trivia edge cases and boundary conditions.
    
    This class focuses on testing boundary conditions, limits,
    and potential edge cases in trivia operations.
    """

    @pytest.fixture(autouse=True)
    def setup_method(self, test_user, test_theme):
        """
        Initial setup for each test.
        
        Args:
            test_user: Test user fixture
            test_theme: Test theme fixture
        """
        self.url = reverse('trivia-list')
        self.valid_data = TEST_TRIVIA_DATA['valid_trivia'].copy()
        self.user = test_user
        self.theme = test_theme

    def test_trivia_with_maximum_questions(self, api_client_authenticated):
        """
        Test creating trivia with maximum allowed questions.
        
        Steps:
        1. Prepare trivia data with 6 questions (exceeding limit of 5)
        2. Attempt to create trivia
        3. Verify rejection
        
        Assertions:
        - Request fails (400)
        - Appropriate error message about maximum questions
        """
        data = self.valid_data.copy()
        base_questions = TEST_TRIVIA_DATA['valid_trivia']['questions']
        data['questions'] = base_questions * 2  # 6 questions (3 * 2)
        
        response = api_client_authenticated.post(self.url, data, format='json')
        assert response.status_code == 400, "Should reject exceeding maximum questions"
        assert "Maximum 5 questions allowed" in str(response.data), \
            "Should indicate maximum questions limit"

    def test_trivia_with_minimum_questions(self, api_client_authenticated):
        """
        Test creating trivia with less than minimum required questions.
        
        Steps:
        1. Prepare trivia data with 2 questions (below minimum of 3)
        2. Attempt to create trivia
        3. Verify rejection
        
        Assertions:
        - Request fails (400)
        - Appropriate error message about minimum questions
        """
        data = self.valid_data.copy()
        data['questions'] = TEST_TRIVIA_DATA['valid_trivia']['questions'][:2]
        
        response = api_client_authenticated.post(self.url, data, format='json')
        assert response.status_code == 400, "Should reject insufficient questions"
        assert ERROR_MESSAGES['NO_QUESTIONS'] in str(response.data), \
            "Should indicate minimum questions requirement"

    def test_question_with_maximum_answers(self, api_client_authenticated):
        """
        Test creating question with maximum allowed answers.
        
        Steps:
        1. Prepare question data with 6 answers (exceeding limit of 5)
        2. Attempt to create trivia
        3. Verify rejection
        
        Assertions:
        - Request fails (400)
        - Appropriate error message about maximum answers
        """
        data = self.valid_data.copy()
        question = data['questions'][0]
        base_answer = question['answers'][0]
        question['answers'] = [base_answer.copy() for _ in range(6)]
        
        response = api_client_authenticated.post(self.url, data, format='json')
        assert response.status_code == 400, "Should reject exceeding maximum answers"
        assert "can have maximum 5 answers" in str(response.data), \
            "Should indicate maximum answers limit"

@pytest.mark.django_db
class TestQuestions(TestTriviaBase):
    """
    Test cases for question-related operations.
    
    This class focuses on testing question retrieval, validation,
    and error handling for question operations.
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup for each test case"""
        self.url = reverse('trivia-get-trivia')
    
    def test_get_questions_invalid_trivia(self, api_client):
        """
        Test retrieving questions with invalid trivia ID.
        
        Steps:
        1. Request questions with invalid UUID
        2. Verify error response
        
        Assertions:
        - Request fails (400)
        - Appropriate error message about invalid UUID
        """
        response = api_client.get(f"{self.url}?id=invalid-uuid")
        assert response.status_code == 400, "Should reject invalid UUID"
        assert "Invalid UUID format" in str(response.data['error']), \
            "Should indicate invalid UUID format"

    def test_get_questions_valid_trivia(self, api_client, trivia_with_questions):
        """
        Test retrieving questions for valid trivia.
        
        Steps:
        1. Create sample trivia with questions
        2. Request questions
        3. Verify response
        
        Assertions:
        - Successful response (200)
        - Questions data present in response
        """
        response = api_client.get(f"{self.url}?id={trivia_with_questions.id}")
        assert response.status_code == 200, "Should return successful response"
        assert len(response.data['questions']) > 0, "Should return questions data"

@pytest.mark.django_db
class TestThemes:
    """
    Test cases for theme-related operations.
    
    This class tests theme listing, filtering, and edge cases
    related to theme operations.
    """

    def test_list_themes(self, api_client):
        """
        Test listing all available themes.
        
        Steps:
        1. Request themes list endpoint
        2. Verify successful response
        
        Assertions:
        - Successful response (200)
        - Themes data returned
        """
        url = reverse('theme-list')
        response = api_client.get(url)
        assert response.status_code == 200, "Should return successful response"

    def test_list_empty_themes(self, api_client):
        """
        Test listing themes when none exist.
        
        Steps:
        1. Delete all existing themes
        2. Request themes list
        3. Verify empty response
        
        Assertions:
        - Successful response (200)
        - Empty list returned
        """
        Theme.objects.all().delete()
        url = reverse('theme-list')
        response = api_client.get(url)
        assert response.status_code == 200, "Should return successful response"
        assert len(response.data) == 0, "Should return empty list"

    def test_filter_trivias_nonexistent_theme(self, api_client):
        """
        Test filtering trivias with non-existent theme.
        
        Steps:
        1. Generate valid but non-existent UUID
        2. Attempt to filter trivias by this theme
        3. Verify error response
        
        Assertions:
        - Not found response (404)
        - Appropriate error message
        """
        nonexistent_uuid = str(uuid.uuid4())
        url = reverse('trivia-filter-trivias')
        response = api_client.get(f"{url}?theme={nonexistent_uuid}&difficulty=1")
        assert response.status_code == 404, "Should return not found status"
        assert "Theme not found" in str(response.data['error']), \
            "Should indicate theme not found"

@pytest.mark.django_db
class TestTriviaPermissions(TestTriviaBase):
    """Test cases for trivia permissions"""

    @pytest.fixture(autouse=True)
    def setup_method(self, test_user, test_theme):
        """Setup for each test case"""
        self.user = test_user
        self.theme = test_theme

    @pytest.mark.parametrize("is_authenticated, expected_count", [
        (True, 2),    # User authenticated: sees public + own private
        (False, 1)    # User not authenticated: sees only public
    ])
    def test_trivia_visibility_by_authentication(self, api_client, test_user, is_authenticated, expected_count):
        """Test visibility of trivias based on authentication status."""
        
        # Create trivias
        other_user = UserFactory.create_other_user()
        trivias = {
            'public': TriviaFactory(
                title='Public Trivia',
                created_by=other_user,
                is_public=True
            ),
            'private': PrivateTriviaFactory(
                title='Own Private Trivia',
                created_by=test_user,
                is_public=False
            )
        }
        
        if is_authenticated:
            test_user.is_authenticated = True
            test_user.save()
            api_client.force_authenticate(user=test_user)
            
            response = api_client.get(reverse('trivia-list'))

            response_data = {t['title']: t for t in response.data}
            assert trivias['public'].title in response_data, \
                "User authenticated should see the public trivia" 
            assert trivias['private'].title in response_data, \
                "User authenticated should see their private trivia"
            
        else:
            # User not authenticated
            response = api_client.get(reverse('trivia-list'))
            
            # Verify that only sees the public trivia
            response_data = {t['title']: t for t in response.data}
            assert trivias['public'].title in response_data, \
                "User not authenticated should see the public trivia"
            assert trivias['private'].title not in response_data, \
                "User not authenticated should not see private trivias"

        assert response.status_code == 200
        assert len(response.data) == expected_count, \
            f"Usuario {'autenticado' if is_authenticated else 'no autenticado'} " \
            f"should see {expected_count} trivias"

@pytest.mark.django_db
class TestTriviaAdvanced(TestTriviaBase):
    """Pruebas avanzadas para demostrar manejo de concurrencia y rendimiento."""

    @pytest.fixture(autouse=True)
    def setup_method(self, test_user, test_theme):
        """Setup for each test case"""
        self.url = reverse('trivia-list')
        self.user = test_user
        self.theme = test_theme
        # Crear datos válidos que respeten los límites
        self.valid_data = {
            'title': 'Performance Test Trivia',
            'difficulty': 1,
            'theme': self.theme.id,
            'username': self.user.username,
            'questions': [
                {
                    'question_title': f'Question {i}',
                    'answers': [
                        {'answer_title': f'Answer {j} for Q{i}', 
                         'is_correct': j == 0}
                        for j in range(3)  # Solo 3 respuestas por pregunta
                    ]
                }
                for i in range(3)  # Solo 3 preguntas
            ]
        }

    def test_concurrent_trivia_creation(self, api_client_authenticated):
        """Prueba la creación simultánea de trivias por diferentes usuarios."""
        
        def create_trivia():
            # Crear un usuario único para cada hilo
            thread_user = UserFactory()
            thread_user.save()
            
            client = APIClient()
            thread_id = threading.get_ident()
            client.force_authenticate(user=thread_user)
            
            data = ConcurrentTriviaFactory.create_concurrent_data(
                user=thread_user,  # Usar el usuario específico del hilo
                theme=self.theme,
                thread_id=thread_id
            )
            
            response = client.post(self.url, data, format='json')
            return response

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(create_trivia) for _ in range(3)]
            responses = [f.result() for f in futures]

        successful_creations = [r for r in responses if r.status_code == 201]
        assert len(successful_creations) > 0, ERROR_MESSAGES['CONCURRENT_ERROR']

    def test_trivia_creation_performance(self, api_client_authenticated):
        """Verifica el rendimiento en la creación de trivias."""
        import time

        data = self.valid_data.copy()
        start_time = time.time()
        response = api_client_authenticated.post(self.url, data, format='json')
        end_time = time.time()

        assert response.status_code == 201, \
            f"La creación falló con error: {response.data}"
        assert end_time - start_time < 2.0, \
            f"La creación tardó {end_time - start_time:.2f} segundos"

    def test_trivia_list_performance(self, api_client_authenticated):
        """Verifica que la lista de trivias se carga en tiempo razonable."""
        import time

        # Crear algunas trivias válidas para la prueba
        for i in range(3):
            data = self.valid_data.copy()
            data['title'] = f'Performance Test Trivia {i}'
            api_client_authenticated.post(self.url, data, format='json')

        start_time = time.time()
        response = api_client_authenticated.get(self.url)
        end_time = time.time()

        assert response.status_code == 200
        assert end_time - start_time < 1.0, \
            f"La respuesta tardó {end_time - start_time:.2f} segundos"
