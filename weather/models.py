from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Add profile_pic field to User model (since it exists in auth_user table)
User.add_to_class('profile_pic', models.CharField(max_length=255, blank=True, null=True))

class UserProfile(models.Model):
    """
    Extended profile for Django's default User model
    """

    USER_TYPES = (
        ('user', 'Regular User'),
        ('admin', 'Administrator'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='user')
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    # User preferences
    weather_alerts_enabled = models.BooleanField(default=True)
    safety_tips_enabled = models.BooleanField(default=True)
    notification_frequency = models.CharField(
        max_length=20,
        choices=[
            ('realtime', 'Real-time'),
            ('hourly', 'Hourly'),
            ('daily', 'Daily'),
        ],
        default='daily'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_active = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'user_profiles'

    def __str__(self):
        return f"{self.user.username} ({self.get_user_type_display()})"

    def is_admin_user(self):
        """Check if user is an administrator"""
        return self.user_type == 'admin' or self.user.is_superuser

    def is_regular_user(self):
        """Check if user is a regular user"""
        return self.user_type == 'user'

    def update_last_active(self):
        """Update the last active timestamp"""
        self.last_active = timezone.now()
        self.save(update_fields=['last_active'])


class ChatSession(models.Model):
    """
    Model to store chat sessions between users and the weather bot
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    session_id = models.CharField(max_length=100, unique=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'chat_sessions'
        ordering = ['-started_at']

    def __str__(self):
        return f"Chat Session {self.session_id} - {self.user.email}"


class ChatMessage(models.Model):
    """
    Model to store individual chat messages
    """

    MESSAGE_TYPES = (
        ('user', 'User Message'),
        ('bot', 'Bot Response'),
        ('system', 'System Message'),
    )

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    # Weather data (if applicable)
    weather_data = models.JSONField(null=True, blank=True)
    location_queried = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'chat_messages'
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.get_message_type_display()} - {self.timestamp}"


class WeatherAlert(models.Model):
    """
    Model to store weather alerts sent to users
    """

    ALERT_TYPES = (
        ('warning', 'Weather Warning'),
        ('watch', 'Weather Watch'),
        ('advisory', 'Weather Advisory'),
        ('emergency', 'Emergency Alert'),
    )

    SEVERITY_LEVELS = (
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('high', 'High'),
        ('extreme', 'Extreme'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    alert_type = models.CharField(max_length=15, choices=ALERT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    location = models.CharField(max_length=100)

    # Alert timing
    issued_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    # Admin who created the alert
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_alerts'
    )

    # Users who received this alert
    recipients = models.ManyToManyField(User, through='AlertDelivery', related_name='received_alerts')

    class Meta:
        db_table = 'weather_alerts'
        ordering = ['-issued_at']

    def __str__(self):
        return f"{self.title} - {self.location}"


class AlertDelivery(models.Model):
    """
    Model to track alert delivery to individual users
    """

    DELIVERY_STATUS = (
        ('pending', 'Pending'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed'),
    )

    alert = models.ForeignKey(WeatherAlert, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=DELIVERY_STATUS, default='pending')
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'alert_deliveries'
        unique_together = ['alert', 'user']

    def __str__(self):
        return f"Alert {self.alert.title} to {self.user.email} - {self.status}"


class SystemLog(models.Model):
    """
    Model to store system logs for admin monitoring
    """

    LOG_LEVELS = (
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    )

    level = models.CharField(max_length=10, choices=LOG_LEVELS)
    message = models.TextField()
    module = models.CharField(max_length=50)  # e.g., 'weather_api', 'chat_bot', 'alerts'
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    # Additional context data
    extra_data = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = 'system_logs'
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.level.upper()}] {self.module}: {self.message[:50]}..."


class ActivityLog(models.Model):
    """
    Model to track user activities for admin monitoring
    """

    ACTIVITY_TYPES = (
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('signup', 'User Signup'),
        ('chat', 'Chat Message'),
        ('weather_query', 'Weather Query'),
        ('alert_view', 'Alert Viewed'),
        ('settings_change', 'Settings Changed'),
        ('map_view', 'Map Viewed'),
        ('api_call', 'API Call'),
        ('error', 'Error Occurred'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    # Additional context
    metadata = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = 'activity_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['activity_type', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.get_activity_type_display()} at {self.timestamp}"


class UserLocation(models.Model):
    """Track user location for display on admin map"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='current_location')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    location_name = models.CharField(max_length=200, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_locations'

    def __str__(self):
        return f"{self.user.email} at ({self.latitude}, {self.longitude})"


class AdminChatHistory(models.Model):
    """Store admin chat conversations with AI"""
    admin_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_chat_history')
    session_id = models.CharField(max_length=100, blank=True, null=True)  # Group messages in same conversation thread
    message = models.TextField()
    response = models.TextField()
    user_mentioned = models.CharField(max_length=100, blank=True, null=True)  # Username if querying about a user
    weather_data = models.JSONField(null=True, blank=True)  # Weather data if fetched
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'admin_chat_history'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.admin_user.username} - {self.timestamp}"
