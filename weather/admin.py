from django.contrib import admin
from django.contrib.auth.models import User
from .models import (
    UserProfile, ChatSession, ChatMessage, WeatherAlert,
    AlertDelivery, SystemLog
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_type', 'phone_number', 'location', 'weather_alerts_enabled']
    list_filter = ['user_type', 'weather_alerts_enabled', 'created_at']
    search_fields = ['user__username', 'user__email', 'location']
    ordering = ['-created_at']

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user', 'started_at', 'is_active']
    list_filter = ['is_active', 'started_at']
    search_fields = ['session_id', 'user__username']
    ordering = ['-started_at']
    readonly_fields = ['session_id', 'started_at']

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'message_type', 'content_preview', 'timestamp']
    list_filter = ['message_type', 'timestamp']
    search_fields = ['content', 'session__user__username']
    ordering = ['-timestamp']
    readonly_fields = ['timestamp']

    def content_preview(self, obj):
        return f"{obj.content[:50]}..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'

@admin.register(WeatherAlert)
class WeatherAlertAdmin(admin.ModelAdmin):
    list_display = ['title', 'alert_type', 'severity', 'location', 'is_active', 'issued_at']
    list_filter = ['alert_type', 'severity', 'is_active', 'issued_at']
    search_fields = ['title', 'description', 'location']
    ordering = ['-issued_at']
    readonly_fields = ['issued_at']

@admin.register(AlertDelivery)
class AlertDeliveryAdmin(admin.ModelAdmin):
    list_display = ['alert', 'user', 'status', 'delivered_at']
    list_filter = ['status', 'delivered_at']
    search_fields = ['alert__title', 'user__username']
    ordering = ['-delivered_at']
    readonly_fields = ['delivered_at', 'read_at']

@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ['level', 'module', 'message_preview', 'timestamp']
    list_filter = ['level', 'module', 'timestamp']
    search_fields = ['message', 'module']
    ordering = ['-timestamp']
    readonly_fields = ['timestamp']

    def message_preview(self, obj):
        return f"{obj.message[:100]}..." if len(obj.message) > 100 else obj.message
    message_preview.short_description = 'Message Preview'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False