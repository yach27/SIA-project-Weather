from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json
import logging
from .services.chatbot_service import WeatherChatbotService
from .services.weather_service import get_weather_service
from .services.temperature_alert_service import TemperatureAlertService
from .services.health_tips_service import HealthTipsService

logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'weather/home.html')

def signin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Try to find user by email (since Django uses username by default)
        from django.contrib.auth.models import User
        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            # Try to authenticate with email as username
            username = email

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Redirect to admin dashboard if user is staff/admin
            if user.is_staff or user.is_superuser:
                return redirect('admin_dashboard')
            else:
                return redirect('user_dashboard')  # Redirect regular users to user dashboard
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'weather/signin.html')

def signup(request):
    return render(request, 'weather/signup.html')

def admin_dashboard(request):
    # Ensure only staff/admin users can access
    if not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)):
        return redirect('signin')

    # Dashboard metrics
    context = {
        'users_count': 0,  # Add actual count logic here
        'active_sessions': 0,  # Add actual count logic here
        'alerts_count': 2,  # Active alerts count
        'users_notified': 2081,  # Users notified today
        'delivery_rate': 94,  # Delivery rate percentage
    }

    return render(request, 'admin/dashboard_home.html', context)

def admin_chat(request):
    # Ensure only staff/admin users can access
    if not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)):
        return redirect('signin')

    # Sample chatbot data - replace with actual chatbot message history
    context = {
        'messages': [],  # Add actual chatbot conversation history here
    }

    return render(request, 'admin/chat.html', context)

def admin_weather_alerts(request):
    # Ensure only staff/admin users can access
    if not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)):
        return redirect('signin')

    # Mock data for active alerts (replace with actual database queries)
    context = {
        'active_alerts': [
            {
                'id': 1,
                'title': 'Severe Thunderstorm Warning',
                'message': 'Strong thunderstorms with damaging winds and hail expected in the area.',
                'severity': 'severe',
                'target_areas': ['New York', 'Chicago'],
                'sent_at': '2024-12-15 14:30',
                'expires_at': '2024-12-15 20:00',
                'users_notified': 1247,
                'status': 'active'
            },
            {
                'id': 2,
                'title': 'Winter Weather Advisory',
                'message': 'Light snow and freezing temperatures expected overnight.',
                'severity': 'moderate',
                'target_areas': ['Philadelphia'],
                'sent_at': '2024-12-15 12:15',
                'expires_at': '2024-12-16 08:00',
                'users_notified': 834,
                'status': 'active'
            }
        ],
        'alert_stats': {
            'total_sent_today': 15,
            'total_active': 2,
            'users_notified_today': 2081,
            'delivery_rate': 94
        }
    }

    return render(request, 'admin/weather_alerts.html', context)

def admin_weather_map(request):
    # Ensure only staff/admin users can access
    if not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)):
        return redirect('signin')

    context = {}
    return render(request, 'admin/weather_map.html', context)

def admin_users(request):
    # Ensure only staff/admin users can access
    if not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)):
        return redirect('signin')

    context = {}
    return render(request, 'admin/users.html', context)

@csrf_exempt
@require_http_methods(["POST"])
def chatbot_api(request):
    """
    API endpoint for chatbot interactions

    Expected JSON payload:
    {
        "message": "user message",
        "conversation_history": [] // optional
    }
    """
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'Authentication required'
        }, status=401)

    try:
        # Parse request data
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        conversation_history = data.get('conversation_history', [])
        user_location = data.get('user_location', None)  # Get location from frontend
        current_weather_data = data.get('current_weather_data', None)  # Get current weather from map

        # If no location provided, try to get from user profile
        if not user_location:
            try:
                if hasattr(request.user, 'profile') and request.user.profile.location:
                    user_location = request.user.profile.location
            except:
                pass

        if not user_message:
            return JsonResponse({
                'success': False,
                'error': 'Message is required'
            }, status=400)

        # Initialize chatbot service
        chatbot_service = WeatherChatbotService()

        # Get response from chatbot
        result = chatbot_service.get_chatbot_response(
            user_message=user_message,
            conversation_history=conversation_history,
            user_location=user_location,
            current_weather_data=current_weather_data
        )

        if result['success']:
            response_data = {
                'success': True,
                'response': result['response'],
                'model': result.get('model'),
                'usage': result.get('usage'),
                'weather_data': result.get('weather_data', False)
            }

            # If current weather data was provided from frontend, include it in response
            if current_weather_data:
                response_data['weather_info'] = current_weather_data
                return JsonResponse(response_data)

            # If weather data was used, include the structured weather info
            if result.get('weather_data'):
                # Extract location from the user message to get weather data for frontend
                location = extract_location_from_message(user_message)
                if location:
                    weather_info = get_weather_for_chatbot(city=location)
                    if not weather_info['success']:
                        # Try with common country suffixes
                        for suffix in [',US', ',PH', ',JP', ',UK', ',CA']:
                            weather_info = get_weather_for_chatbot(city=f'{location}{suffix}')
                            if weather_info['success']:
                                break

                    if weather_info['success']:
                        # Weather info now includes coordinates and condition_main
                        response_data['weather_info'] = weather_info

            return JsonResponse(response_data)
        else:
            # Use fallback response
            return JsonResponse({
                'success': True,
                'response': result['fallback_response'],
                'fallback': True,
                'error': result.get('error')
            })

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

# User Views
def user_dashboard(request):
    """User dashboard with weather overview"""
    if not request.user.is_authenticated:
        return redirect('signin')

    # Default context with placeholder data
    # Real data will be loaded via JavaScript using geolocation
    context = {
        'current_temp': None,
        'feels_like': None,
        'humidity': None,
        'humidity_status': 'Loading...',
        'wind_speed': None,
        'wind_direction': 'Loading...',
        'air_quality': None,
        'air_quality_status': 'Loading...',
        'uv_index': None,
        'uv_status': 'Loading...',
        'visibility': None,
        'visibility_status': 'Loading...',
        'pressure': None,
        'pressure_status': 'Loading...',
        'sunrise': '--:--',
        'sunset': '--:--',
        'moon_phase': 0,
        'moon_phase_name': 'Loading...',
        'current_condition': 'Loading...',
        'current_location': 'Detecting location...',
        'active_alerts': [],
        'forecast_data': [],
        'health_tips': [],
    }
    return render(request, 'user/dashboard.html', context)

def user_chat(request):
    """User chat interface with weather bot"""
    if not request.user.is_authenticated:
        return redirect('signin')

    context = {
        'messages': [],  # Add chat history here
    }
    return render(request, 'user/chat.html', context)

def current_weather(request):
    """Current weather detailed view"""
    if not request.user.is_authenticated:
        return redirect('signin')

    context = {}
    return render(request, 'user/current_weather.html', context)

def weather_forecast(request):
    """7-day weather forecast"""
    if not request.user.is_authenticated:
        return redirect('signin')

    context = {}
    return render(request, 'user/forecast.html', context)

def weather_map(request):
    """Interactive weather map"""
    if not request.user.is_authenticated:
        return redirect('signin')

    context = {}
    return render(request, 'user/weather_map.html', context)

def weather_history(request):
    """Weather history and trends"""
    if not request.user.is_authenticated:
        return redirect('signin')

    context = {}
    return render(request, 'user/weather_history.html', context)

def health_tips(request):
    """Health and safety tips based on weather - AI-generated"""
    if not request.user.is_authenticated:
        return redirect('signin')

    context = {}
    return render(request, 'user/health_tips.html', context)

def weather_alerts(request):
    """Weather alerts and notifications"""
    if not request.user.is_authenticated:
        return redirect('signin')

    # Sample alert data for testing
    sample_alerts = [
        {
            'title': 'Thunderstorm Warning',
            'description': 'Severe thunderstorms expected in your area with heavy rain and strong winds.',
            'severity': 'severe',
            'issued_at': timezone.now(),
            'expires_at': timezone.now() + timezone.timedelta(hours=6)
        },
        {
            'title': 'Heat Advisory',
            'description': 'High temperatures expected. Stay hydrated and avoid outdoor activities.',
            'severity': 'moderate',
            'issued_at': timezone.now(),
            'expires_at': timezone.now() + timezone.timedelta(hours=12)
        }
    ]

    context = {
        'active_alerts': sample_alerts,
    }
    return render(request, 'user/weather_alerts.html', context)

def user_settings(request):
    """User settings and preferences"""
    if not request.user.is_authenticated:
        return redirect('signin')

    context = {}
    return render(request, 'user/settings.html', context)

def user_logout(request):
    """User logout"""
    from django.contrib.auth import logout
    logout(request)
    return redirect('home')

# Weather API endpoints for chatbot
@csrf_exempt
@require_http_methods(["GET", "POST"])
def get_current_weather_api(request):
    """
    API endpoint to get current weather data

    For GET: Uses query parameters ?city=Manila or ?lat=14.5995&lon=120.9842
    For POST: Uses JSON body {"city": "Manila"} or {"lat": 14.5995, "lon": 120.9842}
    """
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'Authentication required'
        }, status=401)

    try:
        weather_service = get_weather_service()

        # Get parameters
        if request.method == 'GET':
            city = request.GET.get('city')
            lat = request.GET.get('lat')
            lon = request.GET.get('lon')
        else:  # POST
            data = json.loads(request.body) if request.body else {}
            city = data.get('city')
            lat = data.get('lat')
            lon = data.get('lon')

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

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Weather API error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET", "POST"])
def get_weather_forecast_api(request):
    """
    API endpoint to get weather forecast data

    Parameters: city, lat, lon, days (optional, default=5)
    """
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'Authentication required'
        }, status=401)

    try:
        weather_service = get_weather_service()

        # Get parameters
        if request.method == 'GET':
            city = request.GET.get('city')
            lat = request.GET.get('lat')
            lon = request.GET.get('lon')
            days = int(request.GET.get('days', 5))
        else:  # POST
            data = json.loads(request.body) if request.body else {}
            city = data.get('city')
            lat = data.get('lat')
            lon = data.get('lon')
            days = int(data.get('days', 5))

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

@csrf_exempt
@require_http_methods(["GET", "POST"])
def search_locations_api(request):
    """
    API endpoint to search for locations

    Parameters: query (required), limit (optional, default=5)
    """
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'Authentication required'
        }, status=401)

    try:
        weather_service = get_weather_service()

        # Get parameters
        if request.method == 'GET':
            query = request.GET.get('query', '').strip()
            limit = int(request.GET.get('limit', 5))
        else:  # POST
            data = json.loads(request.body) if request.body else {}
            query = data.get('query', '').strip()
            limit = int(data.get('limit', 5))

        if not query:
            return JsonResponse({
                'success': False,
                'error': 'Query parameter is required'
            }, status=400)

        # Limit the limit parameter
        if limit < 1 or limit > 10:
            limit = 5

        # Search locations
        result = weather_service.search_locations(query=query, limit=limit)

        return JsonResponse(result)

    except Exception as e:
        logger.error(f"Location search API error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)

def extract_location_from_message(message: str) -> str:
    """
    Extract location from user message using the same patterns as chatbot service
    """
    import re

    message_lower = message.lower()
    location_patterns = [
        # Pattern: "weather today of X" - Most specific first
        r'(?:weather|temperature|temp)\s+(?:today|now|tonight|tomorrow)\s+(?:in|at|for|of)\s+([A-Za-z\s]+?)(?:\?|$|,|\.|!)',
        # Pattern: "weather in/of/at X"
        r'(?:weather|temperature|temp|humidity|wind|forecast)\s+(?:in|at|for|of)\s+([A-Za-z\s]+?)(?:\?|$|,|\.|!)',
        # Pattern: "in/of X weather"
        r'(?:in|at|for|of)\s+([A-Za-z\s]+?)\s+(?:weather|temperature|temp|humidity|wind|forecast)',
        # Pattern: "what/how is weather in X"
        r'(?:what.*?|how.*?)\s+(?:weather|temperature|temp|humidity|wind|forecast).*?(?:in|at|for|of)\s+([A-Za-z\s]+?)(?:\?|$|,|\.|!)',
        # Pattern: "X weather"
        r'([A-Za-z\s]+?)\s+(?:weather|temperature|temp|humidity|wind|forecast)(?:\?|$|,|\.|!)',
        # Pattern: "current/today weather in X"
        r'(?:current|today.*?)\s+(?:weather|temperature|temp|humidity|wind|forecast).*?(?:in|at|for|of)\s+([A-Za-z\s]+?)(?:\?|$|,|\.|!)',
        # Pattern: "the X weather"
        r'(?:the\s+)?([A-Za-z\s]+?)\s+(?:weather|temperature|temp|humidity|wind|forecast)(?:\s+today|\s+now|$|\?|!|,|\.)',
        # Pattern: "weather of/in X"
        r'(?:the\s+)?(?:weather|temperature|temp|humidity|wind|forecast)\s+(?:of|in|at|for)\s+([A-Za-z\s]+?)(?=\s+(?:today|now|tomorrow)|$|\?|!|,|\.)',
        # Follow-up patterns
        r'(?:how about|what about)\s+(?:the\s+)?(?:weather\s+(?:in|of|for)\s+)?([A-Za-z\s]+?)(?:\s+weather|$|\?|!|,|\.)',
        r'(?:and|also)\s+(?:the\s+)?(?:weather\s+(?:in|of|for)\s+)?([A-Za-z\s]+?)(?:\s+weather|$|\?|!|,|\.)',
    ]

    # Check for weather context or follow-up queries
    weather_keywords = ['weather', 'temperature', 'temp', 'forecast', 'rain', 'sunny', 'cloudy', 'wind', 'humidity', 'today', 'now', 'tomorrow']
    is_weather_context = any(keyword in message_lower for keyword in weather_keywords)
    is_location_followup = any(phrase in message_lower for phrase in ['how about', 'what about', 'and', 'also'])

    if not (is_weather_context or is_location_followup):
        return None

    # Try to extract location using patterns
    for pattern in location_patterns:
        match = re.search(pattern, message_lower)
        if match:
            location = match.group(1).strip()
            # Remove time words from location
            time_words = ['today', 'now', 'tomorrow', 'tonight', 'morning', 'afternoon', 'evening']
            for word in time_words:
                location = location.replace(word, '').strip()
            if len(location) > 2:  # Valid location name
                return location

    # If no pattern match, look for capitalized words (place names)
    words = message.split()
    for i, word in enumerate(words):
        if word and word[0].isupper() and len(word) > 2:
            location_parts = [word]
            for j in range(i + 1, len(words)):
                if j < len(words) and words[j] and words[j][0].isupper():
                    location_parts.append(words[j])
                else:
                    break
            location = ' '.join(location_parts)
            if len(location) > 2:
                return location

    return None

def get_weather_for_chatbot(city: str = None, lat: float = None, lon: float = None) -> dict:
    """
    Helper function to get weather data specifically for chatbot responses
    Returns formatted weather data that can be easily used in chatbot responses
    """
    try:
        weather_service = get_weather_service()
        result = weather_service.get_current_weather(city=city, lat=lat, lon=lon)

        if result['success']:
            data = result['data']

            # Format for chatbot response with coordinates
            return {
                'success': True,
                'location': f"{data['location']['name']}, {data['location']['country']}",
                'temperature': f"{data['current']['temperature']}°C",
                'feels_like': f"{data['current']['feels_like']}°C",
                'condition': data['current']['condition'],
                'condition_main': data['current']['condition_main'],
                'humidity': f"{data['current']['humidity']}%",
                'wind_speed': f"{data['current']['wind_speed']} km/h",
                'pressure': f"{data['current']['pressure']} hPa",
                'visibility': f"{data['current']['visibility']} km",
                'sunrise': data['sun']['sunrise'],
                'sunset': data['sun']['sunset'],
                'coordinates': data['location']['coordinates'],
                'summary': f"Current weather in {data['location']['name']}: {data['current']['condition']}, {data['current']['temperature']}°C (feels like {data['current']['feels_like']}°C). Humidity: {data['current']['humidity']}%, Wind: {data['current']['wind_speed']} km/h."
            }
        else:
            return {
                'success': False,
                'error': result.get('error', 'Unable to get weather data')
            }

    except Exception as e:
        logger.error(f"Error in get_weather_for_chatbot: {str(e)}")
        return {
            'success': False,
            'error': 'Weather service unavailable'
        }

@csrf_exempt
@require_http_methods(["POST"])
def temperature_alert_api(request):
    """
    API endpoint to get temperature alert with AI-generated recommendations

    Expected JSON payload:
    {
        "temperature": 35,
        "location": "Manila, Philippines",
        "weather_condition": "Clear" // optional
    }
    """
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'Authentication required'
        }, status=401)

    try:
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

@csrf_exempt
@require_http_methods(["POST"])
def health_tips_api(request):
    """
    API endpoint to get AI-generated health tips based on weather data

    Expected JSON payload:
    {
        "temperature": 30,
        "feels_like": 33,
        "condition": "Sunny",
        "humidity": 65,
        "wind_speed": 12,
        "air_quality": 1
    }
    """
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'Authentication required'
        }, status=401)

    try:
        weather_data = json.loads(request.body)

        # Initialize health tips service
        tips_service = HealthTipsService()

        # Generate health tips
        tips = tips_service.generate_health_tips(weather_data)

        return JsonResponse({
            'success': True,
            'tips': tips
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Health tips API error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)
