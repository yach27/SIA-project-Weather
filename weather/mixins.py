"""
Django View Mixins for Weather Application
"""
from django.conf import settings
import logging
from .utils.weather_helpers import get_weather_for_chatbot

logger = logging.getLogger(__name__)


class WeatherAlertMixin:
    """
    Mixin to add weather alert functionality to views
    Handles session-based alert display (shows only once)
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Check if alert has been shown this session
        if not self.request.session.get('temp_alert_shown', False):
            # Get weather data and check for alert
            weather_alert = self._get_weather_alert()
            if weather_alert:
                context['temp_alert'] = weather_alert
                context['show_temp_alert'] = True
        else:
            context['show_temp_alert'] = False

        return context

    def _get_weather_alert(self):
        """
        Get temperature alert data from session or fetch new
        Returns alert data if extreme temperature, None otherwise
        """
        # Check if alert data already in session
        alert_data = self.request.session.get('temp_alert_data')
        if alert_data:
            return alert_data

        # Try to get weather data for user's location
        # This would typically come from user profile or geolocation
        try:
            # For now, return None - actual implementation would fetch weather
            # and check if temperature is extreme
            return None
        except Exception as e:
            logger.error(f"Error getting weather alert: {str(e)}")
            return None

    def mark_alert_shown(self):
        """Mark temperature alert as shown in session"""
        self.request.session['temp_alert_shown'] = True
        self.request.session.modified = True


class WeatherDataMixin:
    """
    Mixin to add weather data fetching to views
    Uses Django sessions to cache weather data
    """

    def get_weather_data(self, city=None, lat=None, lon=None, use_cache=True):
        """
        Fetch weather data with session caching

        Args:
            city: City name
            lat: Latitude
            lon: Longitude
            use_cache: Whether to use cached data from session

        Returns:
            dict: Weather data
        """
        cache_key = f'weather_data_{city or f"{lat},{lon}"}'

        # Check session cache first
        if use_cache and cache_key in self.request.session:
            logger.info(f"Using cached weather data for {city or f'{lat},{lon}'}")
            return self.request.session[cache_key]

        # Fetch fresh data
        weather_data = get_weather_for_chatbot(city=city, lat=lat, lon=lon)

        # Cache in session (expires when session expires)
        if weather_data.get('success'):
            self.request.session[cache_key] = weather_data
            self.request.session.modified = True

        return weather_data


class UserLocationMixin:
    """
    Mixin to handle user location from various sources
    Priority: Request param > Session > User Profile > Default
    """

    def get_user_location(self):
        """
        Get user location from various sources

        Returns:
            dict: {'city': str, 'lat': float, 'lon': float} or None
        """
        # 1. Check URL parameters
        city = self.request.GET.get('city')
        lat = self.request.GET.get('lat')
        lon = self.request.GET.get('lon')

        if city or (lat and lon):
            return {
                'city': city,
                'lat': float(lat) if lat else None,
                'lon': float(lon) if lon else None
            }

        # 2. Check session
        location = self.request.session.get('user_location')
        if location:
            return location

        # 3. Check user profile
        if self.request.user.is_authenticated:
            try:
                if hasattr(self.request.user, 'profile') and self.request.user.profile.location:
                    return {'city': self.request.user.profile.location}
            except:
                pass

        # 4. Default location (optional)
        return None

    def set_user_location(self, city=None, lat=None, lon=None):
        """Save user location to session"""
        self.request.session['user_location'] = {
            'city': city,
            'lat': lat,
            'lon': lon
        }
        self.request.session.modified = True
