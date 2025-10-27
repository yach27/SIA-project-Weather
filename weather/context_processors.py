"""Context processors for weather app"""
from django.conf import settings


def api_keys(request):
    """Make API keys available in all templates"""
    return {
        'OPENWEATHER_API_KEY': settings.OPENWEATHER_API_KEY,
    }
