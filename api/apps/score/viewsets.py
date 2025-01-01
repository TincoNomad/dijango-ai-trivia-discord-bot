"""
Score ViewSets Module

This module provides API views for the scoring system.
Includes viewsets for:
- LeaderBoard management
- Score tracking and updates
- Trivia winner management

Features:
- CSRF protection
- Authentication handling
- Custom actions for specific operations
- Error handling and logging
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Score, TriviaWinner, LeaderBoard
from .serializers import ScoreSerializer, LeaderBoardSerializer, TriviaWinnerSerializer
from api.utils.logging_utils import log_exception, logger
from rest_framework import serializers
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from api.utils.throttling import CustomUserRateThrottle, CustomAnonRateThrottle
from api.utils.cache_utils import cache_viewset_action

@method_decorator(csrf_exempt, name='dispatch')
class LeaderBoardViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing leaderboards.
    
    Provides endpoints for:
    - Creating/retrieving leaderboards
    - Listing all leaderboards
    - Getting top scores for a leaderboard
    
    Features:
    - CSRF exemption
    - Error handling
    - Logging
    """
    
    serializer_class = LeaderBoardSerializer
    throttle_classes = [CustomUserRateThrottle, CustomAnonRateThrottle]

    def get_queryset(self):
        """Get all leaderboards"""
        return LeaderBoard.objects.all()

    def create(self, request, *args, **kwargs):
        """
        Create a new leaderboard or return existing one.
        
        POST /api/leaderboards/
        
        Request Body:
            {
                "discord_channel": "channel_name",
                "username": "username"
            }
            
        Returns:
            200: Leaderboard details
            400: Validation error details
        """
        try:
            serializer = self.get_serializer(data=request.data)  
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            return Response({
                'id': str(instance.id),
                'discord_channel': instance.discord_channel,
                'created_by': instance.created_by.username
            }, status=status.HTTP_200_OK)
        except serializers.ValidationError as e:
            discord_channel = request.data.get('discord_channel')
            existing_leaderboard = LeaderBoard.objects.filter(discord_channel=discord_channel).first()
            if existing_leaderboard:
                return Response({
                    'id': str(existing_leaderboard.id),
                    'discord_channel': existing_leaderboard.discord_channel,
                    'created_by': existing_leaderboard.created_by.username
                }, status=status.HTTP_200_OK)
            return Response({"error": str(e.detail)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creating leaderboard: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @cache_viewset_action()
    @action(detail=False, methods=['get'], url_path='all')
    def all_leaderboards(self, request):
        """
        Get all leaderboards with creator information.
        Cached to reduce database load for frequent leaderboard queries.
        
        Cache Strategy:
        - TTL: 15 minutes
        - Key: Global for all users
        - Invalidated: When new leaderboards are created
        """
        try:
            leaderboards = LeaderBoard.objects.all()
            response_data = [{
                'id': str(board.id),
                'discord_channel': board.discord_channel,
                'created_by': board.created_by.username,
                'created_at': board.created_at
            } for board in leaderboards]
            
            return Response(response_data)
        except Exception as e:
            logger.error(f"Error retrieving all leaderboards: {str(e)}")
            raise

    @cache_viewset_action()
    def list(self, request, *args, **kwargs):
        """
        List top 10 scores for a specific channel.
        Cached to optimize frequent leaderboard views.
        
        Cache Strategy:
        - TTL: 15 minutes
        - Key: Based on channel parameter
        - Invalidated: When scores are updated
        """
        discord_channel = request.query_params.get('channel') or request.query_params.get('discord_channel')
        if not discord_channel:
            return Response(
                {"error": "channel or discord_channel query parameter is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            leaderboard = LeaderBoard.objects.get(discord_channel=discord_channel)
            top_scores = Score.objects.filter(leaderboard=leaderboard).order_by('-points')[:10]
            
            return Response(ScoreSerializer(top_scores, many=True).data)
        except LeaderBoard.DoesNotExist:
            return Response(
                {"error": "LeaderBoard not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error retrieving leaderboard: {str(e)}")
            raise

    @action(detail=False, methods=['get'])
    def get_leaderboard(self, request):
        """
        GET /api/leaderboards/get_leaderboard/?id=leaderboard-uuid
        Returns: Top 10 scores of the specific leaderboard
        """
        leaderboard_id = request.query_params.get('id')
        if not leaderboard_id:
            return Response(
                {"error": "id query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            leaderboard = LeaderBoard.objects.get(pk=leaderboard_id)
            top_scores = Score.objects.filter(leaderboard=leaderboard).order_by('-points')[:10]
            
            return Response({
                'leaderboard_id': str(leaderboard.id),
                'discord_channel': leaderboard.discord_channel,
                'created_by': leaderboard.created_by.username,
                'scores': ScoreSerializer(top_scores, many=True).data
            })
        except LeaderBoard.DoesNotExist:
            return Response(
                {"error": "LeaderBoard not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

@method_decorator(csrf_exempt, name='dispatch')
class ScoreViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing scores.
    
    Provides endpoints for:
    - Creating/updating scores
    - Retrieving leaderboard scores
    - Score API information
    
    Features:
    - CSRF protection
    - Score validation
    - Error handling
    """
    
    serializer_class = ScoreSerializer
    throttle_classes = [CustomUserRateThrottle, CustomAnonRateThrottle]

    def get_queryset(self):
        return Score.objects.all()

    def create(self, request):
        try:
            data = request.data
            name = data.get('name')
            points = data.get('points')
            discord_channel = data.get('discord_channel')
            
            # Validate data
            if not all([name, points, discord_channel]):
                return Response({
                    "error": "Missing required fields"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate negative points
            if int(points) < 0:
                return Response({
                    "error": "Points cannot be negative"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get the leaderboard
            try:
                leaderboard = LeaderBoard.objects.get(discord_channel=discord_channel)
            except LeaderBoard.DoesNotExist:
                return Response({
                    "error": "No leaderboard exists for this channel"
                }, status=status.HTTP_404_NOT_FOUND)
                
            # Check if user already has a score in this leaderboard
            existing_score = Score.objects.filter(
                name=name,
                leaderboard=leaderboard
            ).first()
            
            if existing_score:
                # Update existing points
                update_mode = data.get('update_mode', 'add')  # 'add' o 'replace'
                
                if update_mode == 'add':
                    existing_score.points += int(points)
                else:
                    existing_score.points = int(points)
                existing_score.save()
                score = existing_score
            else:
                # Create new score
                score = Score.objects.create(
                    name=name,
                    points=int(points),
                    leaderboard=leaderboard
                )
            
            return Response({
                "message": "Score updated successfully",
                "data": {
                    "name": score.name,
                    "points": score.points
                }
            }, status=status.HTTP_200_OK)
                
        except Exception as e:
            logger.error(f"Error updating score: {str(e)}")
            return Response({
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @log_exception
    @action(detail=True, methods=['get'])
    def leaderboard(self, request, pk=None):
        """
        Gets the top 10 scores for a specific leaderboard.
        GET /api/scores/leaderboard/{leaderboard_id}/
        """
        try:
            leaderboard = LeaderBoard.objects.get(pk=pk)
            scores = Score.objects.filter(leaderboard=leaderboard).order_by('-points')[:10]
            serializer = self.get_serializer(scores, many=True)
            
            return Response({
                'leaderboard_name': leaderboard.name,
                'created_by': str(leaderboard.created_by.id),
                'scores': serializer.data
            })
        except LeaderBoard.DoesNotExist:
            return Response(
                {"error": "LeaderBoard not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error retrieving leaderboard: {str(e)}")
            raise

    @action(detail=False, methods=['get'])
    def get_scores(self, request):
        return Response({"message": "Score API"})

    @method_decorator(ensure_csrf_cookie)
    def list(self, request, *args, **kwargs):
        """
        GET /api/score/
        Returns API information and ensures CSRF token is sent
        """
        csrf_token = get_token(request)
        return Response({
            "message": "Score API endpoint",
            "csrf_token": csrf_token,  # Optional: send the token in the body
            "endpoints": {
                "update_score": "/api/score/update_score/"
            }
        }, status=status.HTTP_200_OK)

class TriviaWinnerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing trivia winners.
    
    Provides standard CRUD operations for trivia winners.
    Uses default ModelViewSet implementation.
    """
    
    queryset = TriviaWinner.objects.all()
    serializer_class = TriviaWinnerSerializer
    throttle_classes = [CustomUserRateThrottle]
