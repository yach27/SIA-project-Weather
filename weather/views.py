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
            conversation_history=conversation_history
        )

        if result['success']:
            response_data = {
                'success': True,
                'response': result['response'],
                'model': result.get('model'),
                'usage': result.get('usage'),
                'weather_data': result.get('weather_data', False)
            }

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
                        # Add coordinates to weather info
                        weather_service = get_weather_service()
                        coord_result = weather_service.get_current_weather(city=location)
                        if not coord_result['success']:
                            # Try with the same suffix that worked for weather data
                            for suffix in [',US', ',PH', ',JP', ',UK', ',CA']:
                                coord_result = weather_service.get_current_weather(city=f'{location}{suffix}')
                                if coord_result['success']:
                                    break

                        if coord_result['success']:
                            weather_info['coordinates'] = coord_result['data']['location']['coordinates']
                            weather_info['condition_main'] = coord_result['data']['current']['condition_main']
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

    context = {
        'current_temp': 25,  # Replace with actual weather API data
        'feels_like': 28,
        'humidity': 65,
        'humidity_status': 'Normal',
        'wind_speed': 12,
        'wind_direction': 'NW',
        'air_quality': 42,
        'air_quality_status': 'Good',
        'uv_index': 6,
        'uv_status': 'High',
        'visibility': 10,
        'visibility_status': 'Good',
        'pressure': 1013,
        'pressure_status': 'Normal',
        'sunrise': '06:45',
        'sunset': '18:30',
        'moon_phase': 75,
        'moon_phase_name': 'Waxing Gibbous',
        'current_condition': 'Partly Cloudy',
        'current_location': 'New York, NY',
        'active_alerts': [],  # Add actual alerts here
        'forecast_data': [],  # Add 7-day forecast data
        'health_tips': [],  # Add weather-based health tips
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
    """Health and safety tips based on weather"""
    if not request.user.is_authenticated:
        return redirect('signin')

    # Sample health tips data
    sample_tips = [
        {
            'title': 'Sun Protection',
            'description': 'UV index is high today. Wear sunscreen with SPF 30+ and protective clothing when outdoors.',
            'category': 'uv'
        },
        {
            'title': 'Stay Hydrated',
            'description': 'High temperatures and humidity levels require increased water intake. Drink fluids regularly.',
            'category': 'temperature'
        },
        {
            'title': 'Respiratory Care',
            'description': 'Humidity levels are moderate. Those with asthma should carry inhalers as a precaution.',
            'category': 'humidity'
        },
        {
            'title': 'Air Quality Alert',
            'description': 'Air quality is good today. Perfect conditions for outdoor activities and exercise.',
            'category': 'air'
        },
    ]

    # Sample default tips for template fallback
    default_tips = {
        'uv_tip': {
            'title': 'UV Protection',
            'description': 'Wear sunscreen with SPF 30+ when UV index is high (above 6).',
            'category': 'uv'
        },
        'hydration_tip': {
            'title': 'Stay Hydrated',
            'description': 'Drink plenty of water, especially during hot and humid weather.',
            'category': 'humidity'
        },
        'clothing_tip': {
            'title': 'Dress Appropriately',
            'description': 'Layer clothing for changing temperatures and carry an umbrella if rain is expected.',
            'category': 'temperature'
        },
        'air_quality_tip': {
            'title': 'Air Quality',
            'description': 'Limit outdoor activities when air quality index is poor (above 150).',
            'category': 'air'
        }
    }

    context = {
        'health_tips': sample_tips,
        **default_tips  # Spread the default tips for template access
    }
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
        r'(?:weather|temperature|temp|humidity|wind|forecast)\s+(?:in|at|for|of)\s+([A-Za-z\s]+?)(?:\?|$|,|\.|!)',
        r'(?:in|at|for|of)\s+([A-Za-z\s]+?)\s+(?:weather|temperature|temp|humidity|wind|forecast)',
        r'(?:what.*?|how.*?)\s+(?:weather|temperature|temp|humidity|wind|forecast).*?(?:in|at|for|of)\s+([A-Za-z\s]+?)(?:\?|$|,|\.|!)',
        r'([A-Za-z\s]+?)\s+(?:weather|temperature|temp|humidity|wind|forecast)(?:\?|$|,|\.|!)',
        r'weather\s+(?:in|at|for|of)\s+([A-Za-z\s]+?)(?:\?|$|,|\.|!)',
        r'(?:current|today.*?)\s+(?:weather|temperature|temp|humidity|wind|forecast).*?(?:in|at|for|of)\s+([A-Za-z\s]+?)(?:\?|$|,|\.|!)',
        r'(?:the\s+)?([A-Za-z\s]+?)\s+(?:weather|temperature|temp|humidity|wind|forecast)(?:\s+today|\s+now|$|\?|!|,|\.)',
        r'(?:the\s+)?(?:weather|temperature|temp|humidity|wind|forecast)\s+(?:of|in|at|for)\s+([A-Za-z\s]+?)(?=\s+(?:today|now|tomorrow)|$|\?|!|,|\.)',
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

            # Format for chatbot response
            return {
                'success': True,
                'location': f"{data['location']['name']}, {data['location']['country']}",
                'temperature': f"{data['current']['temperature']}°C",
                'feels_like': f"{data['current']['feels_like']}°C",
                'condition': data['current']['condition'],
                'humidity': f"{data['current']['humidity']}%",
                'wind_speed': f"{data['current']['wind_speed']} km/h",
                'pressure': f"{data['current']['pressure']} hPa",
                'visibility': f"{data['current']['visibility']} km",
                'sunrise': data['sun']['sunrise'],
                'sunset': data['sun']['sunset'],
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
