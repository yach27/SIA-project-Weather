"""
Test script to verify notifications API
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'weather_chatbot.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import RequestFactory
from weather.views.api import UserNotificationsAPIView

User = get_user_model()

# Get the jhunbert user
user = User.objects.get(username='jhunbert')
print(f"Testing API for user: {user.username} (ID: {user.id})")

# Create a mock request
factory = RequestFactory()
request = factory.get('/api/notifications/')
request.user = user

# Create view instance and call get
view = UserNotificationsAPIView()
response = view.get(request)

print(f"\nResponse status: {response.status_code}")
print(f"Response content: {response.content.decode()}")

# Parse JSON
import json
data = json.loads(response.content.decode())
print(f"\nParsed data:")
print(f"- Success: {data.get('success')}")
print(f"- Unread count: {data.get('unread_count')}")
print(f"- Notifications: {len(data.get('notifications', []))}")

if data.get('notifications'):
    print("\nNotifications details:")
    for notif in data.get('notifications', []):
        print(f"  - ID: {notif['id']}, Title: {notif['title']}")
