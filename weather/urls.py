from django.urls import path
from . import views
from .views import (
    ChatbotAPIView,
    HealthTipsAPIView,
    WeatherDataAPIView,
    LocationSearchAPIView,
    DismissAlertAPIView,
    CurrentWeatherAPIView,
    WeatherForecastAPIView,
    SearchLocationsAPIView,
    TemperatureAlertAPIView
)
# Optional: Import class-based views (uncomment to use)
# from .views_class_based import (
#     DashboardView,
#     ChatView,
#     HealthTipsView,
#     AdminDashboardView,
#     AdminChatView
# )

urlpatterns = [
    path('', views.home, name='home'),
    path('signin/', views.signin, name='signin'),
    path('signup/', views.signup, name='signup'),

    # Admin URLs
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-chat/', views.admin_chat, name='admin_chat'),
    path('admin-alerts/', views.admin_weather_alerts, name='admin_weather_alerts'),
    path('admin-map/', views.admin_weather_map, name='admin_weather_map'),
    path('admin-users/', views.admin_users, name='admin_users'),
    path('admin-logs/', views.admin_logs, name='admin_logs'),
    path('admin-profile/', views.admin_profile, name='admin_profile'),

    # API URLs - Using Class-Based Views (Django Best Practice)
    path('api/chatbot/', ChatbotAPIView.as_view(), name='chatbot_api'),
    path('api/health-tips/', HealthTipsAPIView.as_view(), name='health_tips_api'),
    path('api/weather/', WeatherDataAPIView.as_view(), name='weather_data_api'),
    path('api/location/search/', LocationSearchAPIView.as_view(), name='location_search_api'),
    path('api/dismiss-alert/', DismissAlertAPIView.as_view(), name='dismiss_alert_api'),

    # Weather API endpoints
    path('api/weather/current/', CurrentWeatherAPIView.as_view(), name='current_weather_api'),
    path('api/weather/forecast/', WeatherForecastAPIView.as_view(), name='weather_forecast_api'),
    path('api/weather/search/', SearchLocationsAPIView.as_view(), name='search_locations_api'),
    path('api/temperature-alert/', TemperatureAlertAPIView.as_view(), name='temperature_alert_api'),

    # User URLs
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('chat/', views.user_chat, name='user_chat'),
    path('weather/', views.current_weather, name='current_weather'),
    path('forecast/', views.weather_forecast, name='weather_forecast'),
    path('map/', views.weather_map, name='weather_map'),
    path('history/', views.weather_history, name='weather_history'),
    path('health/', views.health_tips, name='health_tips'),
    path('alerts/', views.weather_alerts, name='weather_alerts'),
    path('settings/', views.user_settings, name='user_settings'),
    path('profile/', views.user_profile, name='user_profile'),
    path('logout/', views.user_logout, name='user_logout'),
]