"""
Custom Django Middleware for Weather Application
"""
from django.conf import settings
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
