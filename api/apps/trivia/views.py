"""
Trivia Views Module

This module provides API views for trivia-related operations.
Includes views for:
- Question retrieval
- Public trivia access
- Error handling

Features:
- UUID validation
- Logging
- Response standardization
"""

from uuid import UUID

from rest_framework import status
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from api.utils.cache_utils import cache_response
from api.utils.logging_utils import log_exception, logger
from api.utils.throttling import CustomAnonRateThrottle, CustomUserRateThrottle

from .models import Trivia
from .serializers import TriviaSerializer


class GetQuestions(APIView):
    """
    View for retrieving trivia questions.

    Features:
    - Public access
    - UUID validation
    - Error logging
    - Rate limiting
    """

    permission_classes: list[BasePermission] = []
    throttle_classes = [CustomUserRateThrottle, CustomAnonRateThrottle]

    @log_exception
    @cache_response()
    def get(self, request, trivia_id: str, format=None):
        """
        Get questions for a specific trivia.
        Cached to improve performance and reduce database load.

        Cache Strategy:
        - TTL: 15 minutes
        - Key: Based on trivia_id
        - Invalidated: When questions are updated

        Args:
            request: HTTP request
            trivia_id: UUID of the trivia
            format: Response format (optional)

        Returns:
            Response: List of questions if found
            Response: Error details if not found or invalid
        """
        try:
            # Validate UUID
            try:
                trivia_uuid = UUID(trivia_id)
            except ValueError:
                logger.warning(f"Access attempt with invalid UUID: {trivia_id}")
                return Response(
                    {"error": "Invalid UUID format"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Try to get trivia
            try:
                trivia = Trivia.objects.get(id=trivia_uuid)
            except Trivia.DoesNotExist:
                logger.warning(f"Access attempt to non-existent trivia: {trivia_id}")
                return Response(
                    {"error": "Trivia not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Get questions
            serializer_trivia = TriviaSerializer(trivia)
            questions = serializer_trivia.data.get("questions", [])
            return Response(questions)

        except Exception as e:
            logger.error(
                f"Error retrieving questions: Trivia={trivia_id}, Error={str(e)}"
            )
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
