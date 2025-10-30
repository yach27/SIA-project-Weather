"""
Weather App Views
Organized into logical modules 
"""

# Authentication views
from .auth import (
    home,
    signin,
    signup,
    user_logout,
)

# Admin views
from .admin import (
    admin_dashboard,
    admin_chat,
    admin_weather_alerts,
    admin_weather_map,
    admin_users,
    admin_logs,
)

# User views
from .user import (
    user_dashboard,
    user_chat,
    current_weather,
    weather_forecast,
    weather_map,
    weather_history,
    health_tips,
    weather_alerts,
    user_settings,
)

# API views (Class-Based Views)
from .api import (
    ChatbotAPIView,
    HealthTipsAPIView,
    WeatherDataAPIView,
    LocationSearchAPIView,
    DismissAlertAPIView,
    CurrentWeatherAPIView,
    WeatherForecastAPIView,
    SearchLocationsAPIView,
    TemperatureAlertAPIView,
    UserLocationAPIView,
    AdminUserLocationsAPIView,
)

__all__ = [
    # Auth
    'home',
    'signin',
    'signup',
    'user_logout',
    # Admin
    'admin_dashboard',
    'admin_chat',
    'admin_weather_alerts',
    'admin_weather_map',
    'admin_users',
    'admin_logs',
    # User
    'user_dashboard',
    'user_chat',
    'current_weather',
    'weather_forecast',
    'weather_map',
    'weather_history',
    'health_tips',
    'weather_alerts',
    'user_settings',
]


