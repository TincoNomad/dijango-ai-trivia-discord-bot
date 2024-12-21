"""
Monitoring Middleware Module

This module provides middleware for logging HTTP requests and errors.
It tracks:
- Request timing
- Request/response data
- Error information
- User information
- IP addresses

The middleware automatically creates log entries for both successful
and failed requests.
"""

from asyncio.log import logger
import time
import json
from .models import RequestLog, ErrorLog
from api.utils.logging_utils import log_exception

class MonitoringMiddleware:
    """
    Middleware for monitoring and logging HTTP requests and responses.
    
    This middleware:
    1. Times request duration
    2. Captures request and response data
    3. Logs successful requests and errors
    4. Tracks user and IP information
    """

    def __init__(self, get_response):
        """
        Initialize the middleware.
        
        Args:
            get_response: The next middleware or view in the chain
        """
        self.get_response = get_response

    @log_exception
    def __call__(self, request):
        """
        Process the request and create appropriate log entries.
        
        Args:
            request: The HTTP request object
            
        Returns:
            response: The HTTP response object
        """
        start_time = time.time()
        
        # Attempt to parse request body as JSON
        try:
            request_data = json.loads(request.body) if request.body else None
        except json.JSONDecodeError:
            request_data = None
        
        response = self.get_response(request)
        
        # Attempt to parse response content as JSON
        try:
            response_data = json.loads(response.content) if response.content else None
        except json.JSONDecodeError:
            response_data = None
        
        duration = time.time() - start_time
        
        try:
            # Log errors (status code >= 400)
            if response.status_code >= 400:
                ErrorLog.objects.create(
                    error_type=str(response.status_code),
                    error_message=getattr(response, 'reason_phrase', 'Unknown'),
                    path=request.path,
                    method=request.method,
                    user_id=getattr(request.user, 'id', None) if request.user.is_authenticated else None,
                    request_data=request_data,
                    url=request.build_absolute_uri()
                )
            # Log successful requests
            else:
                RequestLog.objects.create(
                    path=request.path,
                    method=request.method,
                    response_time=duration,
                    status_code=response.status_code,
                    user_id=getattr(request.user, 'id', None) if request.user.is_authenticated else None,
                    ip_address=self.get_client_ip(request),
                    request_data=request_data,
                    response_data=response_data
                )
        except Exception as e:
            # Log any errors in the monitoring process itself
            logger.error(f"Error in MonitoringMiddleware: {str(e)}")
            
        return response
    
    def get_client_ip(self, request):
        """
        Extract the client IP address from the request.
        
        Handles both direct client IPs and forwarded IPs.
        
        Args:
            request: The HTTP request object
            
        Returns:
            str: The client's IP address
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
