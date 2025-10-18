from django.urls import path
from . import views

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
    path('api/chatbot/', views.chatbot_api, name='chatbot_api'),

    # Weather API endpoints
    path('api/weather/current/', views.get_current_weather_api, name='current_weather_api'),
    path('api/weather/forecast/', views.get_weather_forecast_api, name='weather_forecast_api'),
    path('api/weather/search/', views.search_locations_api, name='search_locations_api'),
    path('api/temperature-alert/', views.temperature_alert_api, name='temperature_alert_api'),

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
    path('logout/', views.user_logout, name='user_logout'),
]