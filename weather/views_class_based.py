"""
Class-Based Views for Weather Application
Using Django best practices
"""
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from .mixins import WeatherAlertMixin, WeatherDataMixin, UserLocationMixin
import logging

logger = logging.getLogger(__name__)


class DashboardView(LoginRequiredMixin, WeatherAlertMixin, WeatherDataMixin, UserLocationMixin, TemplateView):
    """
    User dashboard with weather data
    Handles weather alerts using Django sessions (shows only once)
    """
    template_name = 'user/dashboard.html'
    login_url = 'signin'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add default data that will be loaded via JavaScript
        context.update({
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
        })

        return context

    def post(self, request, *args, **kwargs):
        """Handle POST requests (e.g., dismissing alerts)"""
        if 'dismiss_alert' in request.POST:
            self.mark_alert_shown()
            return redirect('user_dashboard')
        return self.get(request, *args, **kwargs)


class ChatView(LoginRequiredMixin, WeatherAlertMixin, TemplateView):
    """
    User chat interface with weather bot
    Uses Django sessions for alert management
    """
    template_name = 'user/chat.html'
    login_url = 'signin'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['messages'] = []
        return context


class HealthTipsView(LoginRequiredMixin, TemplateView):
    """
    Health and safety tips based on weather
    """
    template_name = 'user/health_tips.html'
    login_url = 'signin'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class AdminDashboardView(LoginRequiredMixin, WeatherDataMixin, TemplateView):
    """
    Admin dashboard with system overview
    """
    template_name = 'admin/dashboard_home.html'
    login_url = 'signin'

    def dispatch(self, request, *args, **kwargs):
        # Check if user is admin
        if not request.user.is_staff:
            return redirect('user_dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add admin-specific data
        from django.contrib.auth import get_user_model
        User = get_user_model()

        context.update({
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
        })

        return context


class AdminChatView(LoginRequiredMixin, TemplateView):
    """
    Admin chatbot testing interface
    """
    template_name = 'admin/chat.html'
    login_url = 'signin'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('user_dashboard')
        return super().dispatch(request, *args, **kwargs)
