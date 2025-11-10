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
    admin_weather_map,
    admin_users,
    admin_get_user_details,
    admin_edit_user,
    admin_delete_user,
    admin_logs,
    admin_profile,
    admin_profile_edit,
    admin_profile_remove_image,
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
    user_settings,
    user_profile,
    user_profile_edit,
    user_profile_remove_image,
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
    AdminChatHistoryAPIView,
    SendWeatherAlertAPIView,
    UserNotificationsAPIView,
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
    'admin_weather_map',
    'admin_users',
    'admin_get_user_details',
    'admin_edit_user',
    'admin_delete_user',
    'admin_logs',
    'admin_profile',
    'admin_profile_edit',
    'admin_profile_remove_image',
    # User
    'user_dashboard',
    'user_chat',
    'current_weather',
    'weather_forecast',
    'weather_map',
    'weather_history',
    'health_tips',
    'user_settings',
    'user_profile',
    'user_profile_edit',
    'user_profile_remove_image',
    # API Views
    'ChatbotAPIView',
    'HealthTipsAPIView',
    'WeatherDataAPIView',
    'LocationSearchAPIView',
    'DismissAlertAPIView',
    'CurrentWeatherAPIView',
    'WeatherForecastAPIView',
    'SearchLocationsAPIView',
    'TemperatureAlertAPIView',
    'UserLocationAPIView',
    'AdminUserLocationsAPIView',
    'AdminChatHistoryAPIView',
    'SendWeatherAlertAPIView',
    'UserNotificationsAPIView',
]


