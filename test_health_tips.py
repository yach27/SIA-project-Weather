"""
Quick test script for health tips service
Run: python test_health_tips.py
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'weather_chatbot.settings')
django.setup()

from weather.services.health_tips_service import HealthTipsService

# Test data
weather_data = {
    'temperature': 30,
    'feels_like': 33,
    'condition': 'sunny',
    'humidity': 65,
    'wind_speed': 12,
    'air_quality': 1
}

print("=" * 60)
print("Testing Health Tips Service")
print("=" * 60)
print(f"\nWeather Data: {weather_data}\n")

# Create service and generate tips
service = HealthTipsService()
print(f"API Key configured: {service.api_key[:20]}..." if service.api_key else "No API key found")
print(f"Model: {service.model}\n")

print("Generating health tips...")
tips = service.generate_health_tips(weather_data)

print(f"\nReceived {len(tips)} tips:\n")
for i, tip in enumerate(tips, 1):
    print(f"{i}. [{tip['category'].upper()}] {tip['title']}")
    print(f"   {tip['description']}\n")

print("=" * 60)
