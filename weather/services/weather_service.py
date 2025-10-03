"""
Weather API Service for Django Application
Handles OpenWeatherMap API calls and data processing
"""

import requests
import logging
from django.conf import settings
from typing import Dict, Optional, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class WeatherAPIService:
    """Service class to handle all weather-related API calls"""

    def __init__(self):
        self.api_key = getattr(settings, 'OPENWEATHER_API_KEY', None)
        self.base_url = getattr(settings, 'OPENWEATHER_BASE_URL', 'https://api.openweathermap.org/data/2.5')

        if not self.api_key:
            logger.error("OpenWeatherMap API key not found in settings")
            raise ValueError("OpenWeatherMap API key is required")

    def get_current_weather(self, city: str = None, lat: float = None, lon: float = None) -> Dict:
        """
        Get current weather data for a location

        Args:
            city: City name (e.g., "Manila,PH" or "New York,US")
            lat: Latitude (if using coordinates)
            lon: Longitude (if using coordinates)

        Returns:
            Dict containing weather data or error information
        """
        try:
            # Build query parameters
            params = {
                'appid': self.api_key,
                'units': 'metric'  # Celsius, meters/sec, etc.
            }

            # Add location parameter
            if city:
                params['q'] = city
            elif lat is not None and lon is not None:
                params['lat'] = lat
                params['lon'] = lon
            else:
                return {
                    'success': False,
                    'error': 'Either city name or coordinates (lat, lon) must be provided'
                }

            # Make API request
            url = f"{self.base_url}/weather"
            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'data': self._format_current_weather(data)
                }
            elif response.status_code == 404:
                return {
                    'success': False,
                    'error': 'Location not found'
                }
            else:
                return {
                    'success': False,
                    'error': f'API error: {response.status_code}'
                }

        except requests.exceptions.Timeout:
            logger.error("Weather API request timeout")
            return {
                'success': False,
                'error': 'Request timeout - please try again'
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Weather API request error: {str(e)}")
            return {
                'success': False,
                'error': 'Unable to fetch weather data'
            }
        except Exception as e:
            logger.error(f"Unexpected error in get_current_weather: {str(e)}")
            return {
                'success': False,
                'error': 'An unexpected error occurred'
            }

    def get_weather_forecast(self, city: str = None, lat: float = None, lon: float = None, days: int = 5) -> Dict:
        """
        Get weather forecast data for a location

        Args:
            city: City name
            lat: Latitude
            lon: Longitude
            days: Number of days for forecast (max 5 for free tier)

        Returns:
            Dict containing forecast data or error information
        """
        try:
            params = {
                'appid': self.api_key,
                'units': 'metric'
            }

            if city:
                params['q'] = city
            elif lat is not None and lon is not None:
                params['lat'] = lat
                params['lon'] = lon
            else:
                return {
                    'success': False,
                    'error': 'Either city name or coordinates must be provided'
                }

            url = f"{self.base_url}/forecast"
            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'data': self._format_forecast_data(data, days)
                }
            else:
                return {
                    'success': False,
                    'error': f'API error: {response.status_code}'
                }

        except Exception as e:
            logger.error(f"Error in get_weather_forecast: {str(e)}")
            return {
                'success': False,
                'error': 'Unable to fetch forecast data'
            }

    def get_air_quality(self, lat: float, lon: float) -> Dict:
        """
        Get air quality data for coordinates

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            Dict containing air quality data or error information
        """
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key
            }

            url = f"http://api.openweathermap.org/data/2.5/air_pollution"
            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'data': self._format_air_quality_data(data)
                }
            else:
                return {
                    'success': False,
                    'error': f'API error: {response.status_code}'
                }

        except Exception as e:
            logger.error(f"Error in get_air_quality: {str(e)}")
            return {
                'success': False,
                'error': 'Unable to fetch air quality data'
            }

    def search_locations(self, query: str, limit: int = 5) -> Dict:
        """
        Search for locations using geocoding API

        Args:
            query: Search query (city name)
            limit: Maximum number of results

        Returns:
            Dict containing location search results
        """
        try:
            params = {
                'q': query,
                'limit': limit,
                'appid': self.api_key
            }

            url = f"http://api.openweathermap.org/geo/1.0/direct"
            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'data': [self._format_location_data(location) for location in data]
                }
            else:
                return {
                    'success': False,
                    'error': f'API error: {response.status_code}'
                }

        except Exception as e:
            logger.error(f"Error in search_locations: {str(e)}")
            return {
                'success': False,
                'error': 'Unable to search locations'
            }

    def _format_current_weather(self, data: Dict) -> Dict:
        """Format current weather data for consistent output"""
        try:
            return {
                'location': {
                    'name': data.get('name', 'Unknown'),
                    'country': data.get('sys', {}).get('country', ''),
                    'coordinates': {
                        'lat': data.get('coord', {}).get('lat'),
                        'lon': data.get('coord', {}).get('lon')
                    }
                },
                'current': {
                    'temperature': round(data.get('main', {}).get('temp', 0)),
                    'feels_like': round(data.get('main', {}).get('feels_like', 0)),
                    'humidity': data.get('main', {}).get('humidity', 0),
                    'pressure': data.get('main', {}).get('pressure', 0),
                    'visibility': data.get('visibility', 0) / 1000,  # Convert to km
                    'wind_speed': round(data.get('wind', {}).get('speed', 0) * 3.6),  # Convert to km/h
                    'wind_direction': data.get('wind', {}).get('deg', 0),
                    'cloud_cover': data.get('clouds', {}).get('all', 0),
                    'condition': data.get('weather', [{}])[0].get('description', '').title(),
                    'condition_main': data.get('weather', [{}])[0].get('main', ''),
                    'icon': data.get('weather', [{}])[0].get('icon', ''),
                    'precipitation': data.get('rain', {}).get('1h', 0) if 'rain' in data else 0
                },
                'sun': {
                    'sunrise': datetime.fromtimestamp(data.get('sys', {}).get('sunrise', 0)).strftime('%H:%M'),
                    'sunset': datetime.fromtimestamp(data.get('sys', {}).get('sunset', 0)).strftime('%H:%M')
                },
                'timestamp': datetime.fromtimestamp(data.get('dt', 0)).isoformat()
            }
        except Exception as e:
            logger.error(f"Error formatting weather data: {str(e)}")
            return {}

    def _format_forecast_data(self, data: Dict, days: int) -> Dict:
        """Format forecast data for consistent output"""
        try:
            forecast_list = data.get('list', [])
            daily_forecasts = []

            # Group by day (every 8th item is roughly one day in 3-hour intervals)
            for i in range(0, min(len(forecast_list), days * 8), 8):
                item = forecast_list[i]
                daily_forecasts.append({
                    'date': datetime.fromtimestamp(item.get('dt', 0)).strftime('%Y-%m-%d'),
                    'temperature': {
                        'min': round(item.get('main', {}).get('temp_min', 0)),
                        'max': round(item.get('main', {}).get('temp_max', 0)),
                        'avg': round(item.get('main', {}).get('temp', 0))
                    },
                    'condition': item.get('weather', [{}])[0].get('description', '').title(),
                    'condition_main': item.get('weather', [{}])[0].get('main', ''),
                    'icon': item.get('weather', [{}])[0].get('icon', ''),
                    'humidity': item.get('main', {}).get('humidity', 0),
                    'wind_speed': round(item.get('wind', {}).get('speed', 0) * 3.6),
                    'precipitation_probability': item.get('pop', 0) * 100
                })

            return {
                'location': {
                    'name': data.get('city', {}).get('name', 'Unknown'),
                    'country': data.get('city', {}).get('country', ''),
                    'coordinates': data.get('city', {}).get('coord', {})
                },
                'forecast': daily_forecasts
            }
        except Exception as e:
            logger.error(f"Error formatting forecast data: {str(e)}")
            return {}

    def _format_air_quality_data(self, data: Dict) -> Dict:
        """Format air quality data for consistent output"""
        try:
            aqi_labels = ['Good', 'Fair', 'Moderate', 'Poor', 'Very Poor']

            if data.get('list') and len(data['list']) > 0:
                air_data = data['list'][0]
                aqi = air_data.get('main', {}).get('aqi', 1)

                return {
                    'aqi': aqi,
                    'aqi_label': aqi_labels[aqi - 1] if 1 <= aqi <= 5 else 'Unknown',
                    'components': air_data.get('components', {}),
                    'timestamp': datetime.fromtimestamp(air_data.get('dt', 0)).isoformat()
                }
            return {}
        except Exception as e:
            logger.error(f"Error formatting air quality data: {str(e)}")
            return {}

    def _format_location_data(self, data: Dict) -> Dict:
        """Format location search data for consistent output"""
        return {
            'name': data.get('name', ''),
            'country': data.get('country', ''),
            'state': data.get('state', ''),
            'lat': data.get('lat'),
            'lon': data.get('lon')
        }

# Convenience function for easy access
def get_weather_service() -> WeatherAPIService:
    """Get a configured weather service instance"""
    return WeatherAPIService()