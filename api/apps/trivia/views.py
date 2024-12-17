from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import BasePermission
from .serializers import TriviaSerializer
from .models import Trivia
from api.utils.logging_utils import log_exception, logger
from django.shortcuts import get_object_or_404
from uuid import UUID
from rest_framework import status

class GetQuestions(APIView):
    permission_classes: list[BasePermission] = []
    
    @log_exception
    def get(self, request, trivia_id: str, format=None):
        try:
            # Validate UUID
            trivia_uuid = UUID(trivia_id)
            
            trivia = get_object_or_404(Trivia, id=trivia_uuid, is_public=True)
            logger.info(
                f"Successful questions query: Trivia={trivia_id}, "
                f"Title={trivia.title}"
            )
            
            serializer_trivia = TriviaSerializer(trivia)
            questions = serializer_trivia.data.get('questions', [])
            return Response(questions)
        except ValueError:
            logger.warning(f"Access attempt with invalid UUID: {trivia_id}")
            return Response(
                {"error": "Invalid UUID format"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Trivia.DoesNotExist:
            logger.warning(f"Access attempt to non-existent trivia: {trivia_id}")
            return Response(
                {"error": "Trivia not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(
                f"Error retrieving questions: Trivia={trivia_id}, "
                f"Error={str(e)}"
            )
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
