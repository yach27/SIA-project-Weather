"""
API Views for Weather Application
Using Django's class-based views for better organization
"""
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
import logging

from ..services.chatbot_service import WeatherChatbotService
from ..services.weather_service import get_weather_service
from ..utils.weather_helpers import (
    extract_location_from_message,
    get_weather_for_chatbot,
    get_air_quality,
    get_geocode_from_location
)

logger = logging.getLogger(__name__)


class ChatbotAPIView(LoginRequiredMixin, View):
    """
    API endpoint for chatbot interactions
    Handles POST requests with user messages and returns AI responses
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Handle chatbot message

        Expected JSON payload:
        {
            "message": "user message",
            "conversation_history": [],  # optional
            "user_location": "City Name",  # optional
            "current_weather_data": {}  # optional
        }
        """
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            conversation_history = data.get('conversation_history', [])
            user_location = data.get('user_location')
            current_weather_data = data.get('current_weather_data')

            # Validate message
            if not user_message:
                return JsonResponse({
                    'success': False,
                    'error': 'Message is required'
                }, status=400)

            # Try to get location from user profile if not provided
            if not user_location:
                user_location = self._get_user_location(request.user)

            # Get chatbot response
            chatbot_service = WeatherChatbotService()
            result = chatbot_service.get_chatbot_response(
                user_message=user_message,
                conversation_history=conversation_history,
                user_location=user_location,
                current_weather_data=current_weather_data
            )

            if result['success']:
                return self._build_success_response(
                    result,
                    user_message,
                    current_weather_data
                )
            else:
                return self._build_fallback_response(result)

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            logger.error(f"Chatbot API error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Internal server error'
            }, status=500)

    def _get_user_location(self, user):
        """Get location from user profile"""
        try:
            if hasattr(user, 'profile') and user.profile.location:
                return user.profile.location
        except:
            pass
        return None

    def _build_success_response(self, result, user_message, current_weather_data):
        """Build successful response with weather data if available"""
        response_data = {
            'success': True,
            'response': result['response'],
            'model': result.get('model'),
            'usage': result.get('usage'),
            'weather_data': result.get('weather_data', False)
        }

        # Include current weather data from frontend if provided
        if current_weather_data:
            response_data['weather_info'] = current_weather_data
            return JsonResponse(response_data)

        # Extract and fetch weather info if needed
        if result.get('weather_data'):
            # Use detected location from chatbot service first
            location = result.get('detected_location')

            # Fall back to extracting from message if not detected by chatbot
            if not location:
                location = extract_location_from_message(user_message)

            if location:
                weather_info = self._fetch_weather_info(location)
                if weather_info and weather_info['success']:
                    response_data['weather_info'] = weather_info

        return JsonResponse(response_data)

    def _fetch_weather_info(self, location):
        """Fetch weather info for a location with fallback"""
        weather_info = get_weather_for_chatbot(city=location)

        if not weather_info['success']:
            # Try with common country suffixes
            for suffix in [',US', ',PH', ',JP', ',UK', ',CA']:
                weather_info = get_weather_for_chatbot(city=f'{location}{suffix}')
                if weather_info['success']:
                    break

        return weather_info if weather_info['success'] else None

    def _build_fallback_response(self, result):
        """Build fallback response when chatbot service fails"""
        return JsonResponse({
            'success': True,
            'response': result['fallback_response'],
            'fallback': True,
            'error': result.get('error')
        })


class HealthTipsAPIView(LoginRequiredMixin, View):
    """
    API endpoint for health tips generation
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Generate health tips based on weather data"""
        try:
            from ..services.health_tips_service import HealthTipsService

            data = json.loads(request.body)
            weather_data = {
                'temperature': data.get('temperature'),
                'feels_like': data.get('feels_like'),
                'condition': data.get('condition'),
                'humidity': data.get('humidity'),
                'wind_speed': data.get('wind_speed'),
                'air_quality': data.get('air_quality', 1)
            }

            service = HealthTipsService()
            tips = service.generate_health_tips(weather_data)

            return JsonResponse({
                'success': True,
                'tips': tips
            })

        except Exception as e:
            logger.error(f"Health tips API error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class WeatherDataAPIView(LoginRequiredMixin, View):
    """
    API endpoint to fetch weather data by location or coordinates
    All weather logic handled in Django backend
    """

    def get(self, request, *args, **kwargs):
        """
        Fetch weather data
        Query params: city OR (lat, lon)
        """
        city = request.GET.get('city')
        lat = request.GET.get('lat')
        lon = request.GET.get('lon')

        if not city and not (lat and lon):
            return JsonResponse({
                'success': False,
                'error': 'City name or coordinates required'
            }, status=400)

        try:
            # Get weather data using Django utility
            if lat and lon:
                weather_data = get_weather_for_chatbot(lat=float(lat), lon=float(lon))
            else:
                weather_data = get_weather_for_chatbot(city=city)

            if weather_data['success']:
                # Get air quality data if coordinates available
                if weather_data.get('coordinates'):
                    coords = weather_data['coordinates']
                    air_quality = get_air_quality(coords['lat'], coords['lon'])
                    weather_data['air_quality'] = air_quality

                return JsonResponse(weather_data)
            else:
                return JsonResponse({
                    'success': False,
                    'error': weather_data.get('error', 'Failed to fetch weather')
                }, status=404)

        except Exception as e:
            logger.error(f"Weather data API error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Internal server error'
            }, status=500)


class LocationSearchAPIView(LoginRequiredMixin, View):
    """
    API endpoint for location search/geocoding
    """

    def get(self, request, *args, **kwargs):
        """Search for a location and return coordinates"""
        query = request.GET.get('q', '').strip()

        if not query:
            return JsonResponse({
                'success': False,
                'error': 'Search query required'
            }, status=400)

        try:
            result = get_geocode_from_location(query)
            return JsonResponse(result)

        except Exception as e:
            logger.error(f"Location search API error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Search failed'
            }, status=500)


class DismissAlertAPIView(LoginRequiredMixin, View):
    """
    API endpoint to dismiss temperature alert
    GET: Check if alert was dismissed
    POST: Dismiss the alert (sets Django session flag)
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        """Check if alert was dismissed in Django session"""
        dismissed = request.session.get('temp_alert_dismissed', False)
        return JsonResponse({
            'success': True,
            'dismissed': dismissed
        })

    def post(self, request, *args, **kwargs):
        """Mark alert as dismissed in Django session"""
        try:
            # Set session flag - alert won't show again this session
            request.session['temp_alert_dismissed'] = True
            request.session.modified = True

            return JsonResponse({
                'success': True,
                'message': 'Alert dismissed'
            })

        except Exception as e:
            logger.error(f"Dismiss alert error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Failed to dismiss alert'
            }, status=500)


class CurrentWeatherAPIView(LoginRequiredMixin, View):
    """
    API endpoint to get current weather data
    Supports both GET (query params) and POST (JSON body)
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        """Get current weather using query parameters"""
        city = request.GET.get('city')
        lat = request.GET.get('lat')
        lon = request.GET.get('lon')
        return self._fetch_weather(city, lat, lon)

    def post(self, request, *args, **kwargs):
        """Get current weather using JSON body"""
        try:
            data = json.loads(request.body) if request.body else {}
            city = data.get('city')
            lat = data.get('lat')
            lon = data.get('lon')
            return self._fetch_weather(city, lat, lon)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)

    def _fetch_weather(self, city, lat, lon):
        """Common method to fetch weather data"""
        try:
            weather_service = get_weather_service()

            # Convert lat/lon to float if provided
            if lat and lon:
                try:
                    lat = float(lat)
                    lon = float(lon)
                except ValueError:
                    return JsonResponse({
                        'success': False,
                        'error': 'Invalid coordinates format'
                    }, status=400)

            # Get weather data
            result = weather_service.get_current_weather(city=city, lat=lat, lon=lon)
            return JsonResponse(result)

        except Exception as e:
            logger.error(f"Weather API error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Internal server error'
            }, status=500)


class WeatherForecastAPIView(LoginRequiredMixin, View):
    """
    API endpoint to get weather forecast data
    Supports both GET (query params) and POST (JSON body)
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        """Get weather forecast using query parameters"""
        city = request.GET.get('city')
        lat = request.GET.get('lat')
        lon = request.GET.get('lon')
        days = int(request.GET.get('days', 5))
        return self._fetch_forecast(city, lat, lon, days)

    def post(self, request, *args, **kwargs):
        """Get weather forecast using JSON body"""
        try:
            data = json.loads(request.body) if request.body else {}
            city = data.get('city')
            lat = data.get('lat')
            lon = data.get('lon')
            days = int(data.get('days', 5))
            return self._fetch_forecast(city, lat, lon, days)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)

    def _fetch_forecast(self, city, lat, lon, days):
        """Common method to fetch forecast data"""
        try:
            weather_service = get_weather_service()

            # Validate days parameter
            if days < 1 or days > 5:
                days = 5

            # Convert coordinates
            if lat and lon:
                try:
                    lat = float(lat)
                    lon = float(lon)
                except ValueError:
                    return JsonResponse({
                        'success': False,
                        'error': 'Invalid coordinates format'
                    }, status=400)

            # Get forecast data
            result = weather_service.get_weather_forecast(city=city, lat=lat, lon=lon, days=days)
            return JsonResponse(result)

        except Exception as e:
            logger.error(f"Weather forecast API error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Internal server error'
            }, status=500)


class SearchLocationsAPIView(LoginRequiredMixin, View):
    """
    API endpoint to search for locations
    Supports both GET (query params) and POST (JSON body)
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        """Search locations using query parameters"""
        query = request.GET.get('query', '').strip()
        limit = int(request.GET.get('limit', 5))
        return self._search_locations(query, limit)

    def post(self, request, *args, **kwargs):
        """Search locations using JSON body"""
        try:
            data = json.loads(request.body) if request.body else {}
            query = data.get('query', '').strip()
            limit = int(data.get('limit', 5))
            return self._search_locations(query, limit)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)

    def _search_locations(self, query, limit):
        """Common method to search locations"""
        try:
            if not query:
                return JsonResponse({
                    'success': False,
                    'error': 'Query parameter is required'
                }, status=400)

            # Limit the limit parameter
            if limit < 1 or limit > 10:
                limit = 5

            weather_service = get_weather_service()
            result = weather_service.search_locations(query=query, limit=limit)
            return JsonResponse(result)

        except Exception as e:
            logger.error(f"Location search API error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Internal server error'
            }, status=500)


class TemperatureAlertAPIView(LoginRequiredMixin, View):
    """
    API endpoint to get temperature alert with AI-generated recommendations
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Generate temperature alert based on weather data"""
        try:
            from ..services.temperature_alert_service import TemperatureAlertService

            # Check if alert was dismissed this session
            if request.session.get('temp_alert_dismissed', False):
                return JsonResponse({
                    'success': True,
                    'alert': None,
                    'message': 'Alert already dismissed this session'
                })

            data = json.loads(request.body)
            temperature = data.get('temperature')
            location = data.get('location', 'Unknown location')
            weather_condition = data.get('weather_condition', None)

            if temperature is None:
                return JsonResponse({
                    'success': False,
                    'error': 'Temperature is required'
                }, status=400)

            # Initialize temperature alert service
            alert_service = TemperatureAlertService()

            # Get AI-generated recommendations
            alert_data = alert_service.get_ai_recommendations(
                temperature=float(temperature),
                location=location,
                weather_condition=weather_condition
            )

            if alert_data:
                return JsonResponse({
                    'success': True,
                    'alert': alert_data
                })
            else:
                # No alert needed (comfortable temperature)
                return JsonResponse({
                    'success': True,
                    'alert': None,
                    'message': 'Temperature is comfortable, no alert needed'
                })

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            logger.error(f"Temperature alert API error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Internal server error'
            }, status=500)


class UserLocationAPIView(LoginRequiredMixin, View):
    """API to update/get user location"""

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        """Update user location"""
        try:
            from ..models import UserLocation
            data = json.loads(request.body)
            lat = data.get('latitude')
            lon = data.get('longitude')
            location_name = data.get('location_name', '')

            UserLocation.objects.update_or_create(
                user=request.user,
                defaults={
                    'latitude': lat,
                    'longitude': lon,
                    'location_name': location_name
                }
            )
            return JsonResponse({'success': True})
        except Exception as e:
            logger.error(f"User location update error: {e}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)


class AdminUserLocationsAPIView(LoginRequiredMixin, View):
    """API to get all active user locations for admin map"""

    def get(self, request):
        """Get all user locations"""
        if not (request.user.is_staff or request.user.is_superuser):
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        try:
            from ..models import UserLocation
            from django.contrib.auth import get_user_model
            User = get_user_model()

            locations = []
            for loc in UserLocation.objects.select_related('user').all():
                if not loc.user.is_superuser:  # Only show regular users (not superusers/admins)
                    locations.append({
                        'email': loc.user.email,
                        'username': loc.user.username,
                        'latitude': float(loc.latitude),
                        'longitude': float(loc.longitude),
                        'location_name': loc.location_name,
                        'updated_at': loc.updated_at.isoformat()
                    })

            return JsonResponse({'success': True, 'locations': locations})
        except Exception as e:
            logger.error(f"Admin user locations API error: {e}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
