"""
Custom Django Middleware for Weather Application
"""
from django.conf import settings
from .models import ActivityLog
import requests
import logging

logger = logging.getLogger(__name__)


class WeatherAlertMiddleware:
    """
    Middleware to check and set weather alerts in session
    Only shows alert once per session using Django sessions
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only process for authenticated users
        if request.user.is_authenticated:
            # Check if we should fetch weather alert
            if not request.session.get('weather_alert_checked', False):
                self._check_and_set_alert(request)

        response = self.get_response(request)
        return response

    def _check_and_set_alert(self, request):
        """
        Check if temperature alert is needed and store in session
        This runs only once per session
        """
        try:
            # Get user's location from session or geolocation
            # For now, we'll mark as checked and let the view handle it
            request.session['weather_alert_checked'] = False
            # The actual alert will be set by the view when weather data is fetched

        except Exception as e:
            logger.error(f"Error in weather alert middleware: {str(e)}")


class WeatherDataMiddleware:
    """
    Middleware to add weather data to request context
    Fetches once per session and caches in Django session
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Add weather alert status to context for templates
        if request.user.is_authenticated:
            # Check if alert should be shown
            request.show_temp_alert = not request.session.get('temp_alert_shown', False)
            request.temp_alert_data = request.session.get('temp_alert_data')

        response = self.get_response(request)
        return response


class ActivityLoggingMiddleware:
    """
    Middleware to automatically log user activities in real-time
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Only log for authenticated users
        if not request.user.is_authenticated:
            return response

        # Skip logging for superuser/admin users
        if request.user.is_superuser:
            return response

        # Skip logging for static files and media
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return response

        # Skip logging for API health checks
        if request.path == '/api/dismiss-alert/' and request.method == 'GET':
            return response

        # Get client IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')

        # Get user agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]

        # Determine activity type and description based on path and method
        activity_type = None
        description = None
        metadata = {}

        # Map routes to activity types
        if request.path == '/signin/' and request.method == 'POST' and response.status_code == 302:
            activity_type = 'login'
            description = f'User {request.user.email} logged in'

        # Note: logout is handled in the view itself, not here
        # because user is logged out before middleware runs

        elif request.path == '/signup/' and request.method == 'POST' and response.status_code == 302:
            activity_type = 'signup'
            description = f'New user {request.user.email} registered'

        elif request.path.startswith('/api/chatbot/') and request.method == 'POST':
            activity_type = 'chat'
            description = 'User sent a message to chatbot'
            metadata['endpoint'] = request.path

        elif request.path.startswith('/api/weather/') and request.method in ['GET', 'POST']:
            activity_type = 'weather_query'
            description = 'User queried weather data'
            metadata['endpoint'] = request.path

        elif (request.path == '/alerts/' or request.path == '/admin-alerts/') and request.method == 'GET':
            activity_type = 'alert_view'
            description = 'User viewed weather alerts'

        elif request.path == '/settings/' and request.method == 'POST':
            activity_type = 'settings_change'
            description = 'User updated account settings'

        elif request.path in ['/map/', '/admin-map/'] and request.method == 'GET':
            activity_type = 'map_view'
            description = 'User accessed weather map'
            metadata['path'] = request.path

        elif request.path.startswith('/api/') and request.method == 'POST':
            activity_type = 'api_call'
            description = f'API request to {request.path}'
            metadata['method'] = request.method
            metadata['endpoint'] = request.path

        # Log the activity if we determined one
        if activity_type and description:
            try:
                ActivityLog.objects.create(
                    user=request.user,
                    activity_type=activity_type,
                    description=description,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    metadata=metadata if metadata else None
                )
            except Exception as e:
                # Don't break the request if logging fails
                logger.error(f"Failed to log activity: {e}")

        return response
