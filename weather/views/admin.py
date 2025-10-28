"""
Admin Views
Handles admin dashboard and management pages
"""
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import models
from datetime import timedelta


def admin_dashboard(request):
    """Admin dashboard home"""
    if not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)):
        return redirect('signin')

    context = {}
    return render(request, 'admin/dashboard_home.html', context)


def admin_chat(request):
    """Admin chatbot testing page"""
    if not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)):
        return redirect('signin')

    context = {}
    return render(request, 'admin/chat.html', context)


def admin_weather_alerts(request):
    """Admin weather alerts management"""
    if not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)):
        return redirect('signin')

    context = {}
    return render(request, 'admin/weather_alerts.html', context)


def admin_weather_map(request):
    """Admin weather map view"""
    if not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)):
        return redirect('signin')

    context = {}
    return render(request, 'admin/weather_map.html', context)


def admin_users(request):
    """Admin users management page - shows real users from database"""
    if not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)):
        return redirect('signin')

    User = get_user_model()

    # Get all users excluding staff/admin
    all_users = User.objects.filter(is_staff=False, is_superuser=False).order_by('-date_joined')

    # Calculate stats
    total_users = all_users.count()
    active_users = all_users.filter(is_active=True).count()

    # Users who joined today
    today = timezone.now().date()
    new_today = all_users.filter(date_joined__date=today).count()

    # Inactive users (not logged in for 30+ days or inactive accounts)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    inactive_users = all_users.filter(
        models.Q(last_login__lt=thirty_days_ago) | models.Q(is_active=False)
    ).count()

    context = {
        'total_users': total_users,
        'active_users': active_users,
        'new_today': new_today,
        'inactive_users': inactive_users,
        'users': all_users[:25],  # First 25 users for initial load
    }
    return render(request, 'admin/users.html', context)
