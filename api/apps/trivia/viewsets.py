from rest_framework import viewsets, permissions
from django.db import models
from .models import Trivia, Theme, Question, Answer
from .serializers import TriviaSerializer, ThemeSerializer, TriviaListSerializer
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from rest_framework.exceptions import ValidationError as DRFValidationError
from api.utils.logging_utils import log_exception, logger
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from api.utils.jwt_utils import get_user_id_by_username
from django.db import transaction
import uuid


User = get_user_model()

class TriviaViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        if self.action == 'list':
            return TriviaListSerializer
        return TriviaSerializer
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return []
    
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.role == 'admin':
                logger.info(f"Admin access: {user.username} querying all trivias")
                return Trivia.objects.all()
            # Regular user: sees public trivias and their own private trivias
            logger.info(f"User access: {user.username} querying allowed trivias")
            return Trivia.objects.filter(
                models.Q(is_public=True) | 
                models.Q(is_public=False, created_by=user)
            )
        # User not authenticated: only sees public trivias
        logger.info("Anonymous access: querying public trivias")
        return Trivia.objects.filter(is_public=True)
    
    def perform_create(self, serializer):
        username = serializer.validated_data.get('username')
        try:
            user = User.objects.get(username=username)
            trivia = serializer.save(created_by=user, is_public=True)
            logger.info(
                f"Trivia created successfully: ID={trivia.id}, "
                f"Creator={username}, Title={trivia.title}"
            )
        except User.DoesNotExist:
            logger.error(f"Attempt to create trivia with non-existent user: {username}")
            raise ValidationError("User not found")
        except Exception as e:
            logger.error(
                f"Error creating trivia: User={username}, "
                f"Error={str(e)}"
            )
            raise
    
    @action(detail=False, methods=['get'])
    def get_trivia(self, request):
        """
        GET /api/trivias/get_trivia/?id=trivia-uuid
        Returns: Detailed information of a specific trivia
        """
        trivia_id = request.query_params.get('id')
        if not trivia_id:
            return Response(
                {"error": "ID query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            uuid.UUID(trivia_id)
        except ValueError:
            return Response(
                {"error": "Invalid UUID format"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            trivia = Trivia.objects.get(id=trivia_id)
            serializer = TriviaSerializer(trivia)
            return Response(serializer.data)
        except Trivia.DoesNotExist:
            return Response(
                {"error": "Trivia not found"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def difficulty(self, request):
        """Returns the available difficulty options"""
        try:
            difficulties = dict(Trivia.DIFFICULTY_CHOICES)
            return Response(difficulties, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting difficulty choices: {e}")
            return Response(
                {"error": "Error retrieving difficulty choices"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def list(self, request, *args, **kwargs):
        """
        GET /api/trivias/?username=discord_user
        Returns: List of trivias created by the specified user or all public trivias if no username
        """
        username = request.query_params.get('username')
        
        if username:
            try:
                user_id = get_user_id_by_username(username)
                if not user_id:
                    return Response(
                        {"error": f"No user found with username: {username}"},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                trivias = Trivia.objects.filter(created_by_id=user_id)
                serializer = TriviaListSerializer(trivias, many=True)
                return Response(serializer.data)
                
            except Exception as e:
                logger.error(f"Error getting trivias by user: {str(e)}")
                return Response(
                    {"error": "Internal server error"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return super().list(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'], url_path='filter')
    def filter_trivias(self, request):
        theme = request.query_params.get('theme')
        difficulty = request.query_params.get('difficulty')
        
        if not theme or not difficulty:
            logger.warning(
                f"Filtering attempt without required parameters: "
                f"theme={theme}, difficulty={difficulty}"
            )
            return Response(
                {"error": "The parameters 'theme' and 'difficulty' are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            difficulty = int(difficulty)
            uuid.UUID(theme)  # Validate UUID
            
            if not Theme.objects.filter(id=theme).exists():
                logger.warning(f"Filtering attempt with non-existent theme: {theme}")
                return Response(
                    {"error": "Theme not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            query = models.Q(theme=theme, difficulty=difficulty, is_public=True)
            filtered_trivias = Trivia.objects.filter(query).values('id', 'title')
            
            logger.info(
                f"Successful filtering: theme={theme}, difficulty={difficulty}, "
                f"results={len(filtered_trivias)}"
            )
            
            simplified_response = [
                {"id": str(trivia['id']), "title": trivia['title']} 
                for trivia in filtered_trivias
            ]
            
            return Response(simplified_response)
        except ValueError:
            logger.error(
                f"Invalid filter parameter format: "
                f"theme={theme}, difficulty={difficulty}"
            )
            return Response(
                {"error": "The 'difficulty' parameter must be a number"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @log_exception
    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                return super().create(request, *args, **kwargs)
        except IntegrityError:
            raise DRFValidationError(
                detail="A trivia with this title already exists. Please choose another title."
            )
        except ValidationError as e:
            raise DRFValidationError(detail=str(e))
    
    @action(detail=True, methods=['patch'])
    def update_questions(self, request, pk=None):
        """
        PATCH /api/trivias/{trivia_id}/update_questions/
        Updates only questions and answers for a trivia
        """
        try:
            trivia = self.get_object()
            questions_data = request.data.get('questions', [])
            
            # Update questions
            for question_data in questions_data:
                question_id = question_data.get('id')
                if question_id:
                    question = Question.objects.get(id=question_id, trivia=trivia)
                    # Update question fields
                    for key, value in question_data.items():
                        if key != 'answers':
                            setattr(question, key, value)
                    question.save()
                    
                    # Update answers if provided
                    if 'answers' in question_data:
                        for answer_data in question_data['answers']:
                            answer_id = answer_data.get('id')
                            if answer_id:
                                answer = Answer.objects.get(id=answer_id, question=question)
                                for key, value in answer_data.items():
                                    setattr(answer, key, value)
                                answer.save()
            
            return Response({'status': 'questions updated'})
        except Question.DoesNotExist:
            return Response(
                {'error': 'Question not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Answer.DoesNotExist:
            return Response(
                {'error': 'Answer not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error updating questions: {e}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    def perform_update(self, serializer):
        """
        Maneja el CUÁNDO y QUIÉN puede actualizar
        - Logging
        - Permisos
        - Contexto de la petición
        """
        try:
            serializer.save()
            logger.info(f"Trivia updated by {self.request.user}")
        except Exception as e:
            logger.error(f"Update failed: {str(e)}")
            raise

class ThemeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer
