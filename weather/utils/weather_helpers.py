"""
Weather Helper Utilities
Centralized weather data fetching and processing
"""
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def get_weather_for_chatbot(city: str = None, lat: float = None, lon: float = None) -> dict:
    """
    Fetch weather data from OpenWeather API for chatbot responses

    Args:
        city: City name (e.g., "London" or "London,UK")
        lat: Latitude coordinate
        lon: Longitude coordinate

    Returns:
        dict: Weather information with success status
    """
    api_key = settings.OPENWEATHER_API_KEY
    base_url = "https://api.openweathermap.org/data/2.5/weather"

    try:
        # Build request parameters
        if lat and lon:
            params = {
                'lat': lat,
                'lon': lon,
                'units': 'metric',
                'appid': api_key
            }
        elif city:
            params = {
                'q': city,
                'units': 'metric',
                'appid': api_key
            }
        else:
            return {'success': False, 'error': 'No location provided'}

        # Make API request
        response = requests.get(base_url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        # Format weather information
        from datetime import datetime

        # Format sunrise and sunset times
        sunrise_timestamp = data['sys']['sunrise']
        sunset_timestamp = data['sys']['sunset']
        sunrise_time = datetime.fromtimestamp(sunrise_timestamp).strftime('%I:%M %p')
        sunset_time = datetime.fromtimestamp(sunset_timestamp).strftime('%I:%M %p')

        # Get visibility (optional field, default to 10km if not present)
        visibility_meters = data.get('visibility', 10000)
        visibility_km = round(visibility_meters / 1000, 1)

        return {
            'success': True,
            'location': f"{data['name']}, {data['sys']['country']}",
            'temperature': f"{round(data['main']['temp'])}°C",
            'feels_like': f"{round(data['main']['feels_like'])}°C",
            'condition': data['weather'][0]['description'].capitalize(),
            'condition_main': data['weather'][0]['main'],
            'humidity': f"{data['main']['humidity']}%",
            'wind_speed': f"{round(data['wind']['speed'] * 3.6)} km/h",
            'pressure': f"{data['main']['pressure']} hPa",
            'visibility': f"{visibility_km} km",
            'sunrise': sunrise_time,
            'sunset': sunset_time,
            'coordinates': {
                'lat': data['coord']['lat'],
                'lon': data['coord']['lon']
            }
        }

    except requests.exceptions.Timeout:
        logger.error("Weather API timeout")
        return {'success': False, 'error': 'Weather service timeout'}
    except requests.exceptions.RequestException as e:
        logger.error(f"Weather API error: {str(e)}")
        return {'success': False, 'error': 'Failed to fetch weather data'}
    except Exception as e:
        logger.error(f"Unexpected error in get_weather_for_chatbot: {str(e)}")
        return {'success': False, 'error': 'Internal error'}


def extract_location_from_message(message: str) -> str | None:
    """
    Extract location name from user message

    Args:
        message: User's message string

    Returns:
        str: Extracted location name or None
    """
    # Common patterns for location queries
    patterns = [
        'weather in ',
        'weather at ',
        'temperature in ',
        'temperature at ',
        'forecast for ',
        'climate in ',
        'how is the weather in ',
        'what is the weather in ',
        "what's the weather in ",
    ]

    message_lower = message.lower()

    for pattern in patterns:
        if pattern in message_lower:
            # Extract location after the pattern
            start_idx = message_lower.index(pattern) + len(pattern)
            location = message[start_idx:].strip()

            # Clean up location (remove punctuation, take first part if multiple words)
            location = location.split('?')[0].split('.')[0].split(',')[0].strip()

            if location:
                return location

    return None


def get_air_quality(lat: float, lon: float) -> dict:
    """
    Fetch air quality data from OpenWeather API

    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate

    Returns:
        dict: Air quality information
    """
    api_key = settings.OPENWEATHER_API_KEY
    url = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data and data.get('list'):
            aqi = data['list'][0]['main']['aqi']
            components = data['list'][0]['components']

            return {
                'success': True,
                'aqi': aqi,
                'status': _get_aqi_status(aqi),
                'components': components
            }

    except Exception as e:
        logger.error(f"Air quality API error: {str(e)}")

    return {'success': False, 'aqi': '--', 'status': 'Unavailable'}


def _get_aqi_status(aqi: int) -> str:
    """Convert AQI number to status string"""
    statuses = {
        1: 'Good',
        2: 'Fair',
        3: 'Moderate',
        4: 'Poor',
        5: 'Very Poor'
    }
    return statuses.get(aqi, 'Unknown')


def get_geocode_from_location(location: str) -> dict:
    """
    Get coordinates from location name using OpenWeather Geocoding API

    Args:
        location: City name or location string

    Returns:
        dict: Coordinates with success status
    """
    api_key = settings.OPENWEATHER_API_KEY
    url = f"https://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={api_key}"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data and len(data) > 0:
            return {
                'success': True,
                'lat': data[0]['lat'],
                'lon': data[0]['lon'],
                'name': data[0]['name'],
                'country': data[0].get('country', '')
            }

    except Exception as e:
        logger.error(f"Geocoding API error: {str(e)}")

    return {'success': False}
