"""
Admin Views
Handles admin dashboard and management pages
"""
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import models
from django.core.paginator import Paginator
from datetime import timedelta
from ..models import ActivityLog, SystemLog


def admin_dashboard(request):
    """Admin dashboard home with real-time data"""
    if not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)):
        return redirect('signin')

    User = get_user_model()
    from ..models import UserLocation

    # Get stats
    total_users = User.objects.filter(is_superuser=False).count()

    # Get currently active users (logged in within last 24 hours and not logged out)
    # Exclude superusers/admins
    from django.db.models import Max, Q

    # Only consider activities from last 24 hours
    last_24_hours = timezone.now() - timedelta(days=1)

    # Get last login/logout activity for each NON-ADMIN user in last 24 hours
    last_activities = ActivityLog.objects.filter(
        activity_type__in=['login', 'logout'],
        timestamp__gte=last_24_hours,
        user__is_superuser=False  # Exclude admins
    ).values('user').annotate(
        last_time=Max('timestamp')
    )

    # Count users whose last activity was login (not logout) within 24 hours
    active_users = 0
    for activity in last_activities:
        last_log = ActivityLog.objects.filter(
            user_id=activity['user'],
            timestamp=activity['last_time']
        ).first()
        if last_log and last_log.activity_type == 'login':
            active_users += 1

    active_today = active_users

    # Get recent activity (last 5 activities from last 24 hours)
    recent_activities = ActivityLog.objects.filter(
        timestamp__gte=timezone.now() - timedelta(days=1)
    ).select_related('user').order_by('-timestamp')[:5]

    # Get user locations with real-time data
    user_locations = UserLocation.objects.filter(
        user__is_superuser=False
    ).select_related('user').order_by('-updated_at')[:5]

    context = {
        'users_count': total_users,
        'active_sessions': active_today,
        'alerts_count': 0,  # We can add this later if needed
        'recent_activities': recent_activities,
        'user_locations': user_locations,
    }
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


def admin_logs(request):
    """Admin logs monitoring page - shows activity and system logs"""
    if not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)):
        return redirect('signin')

    # Get filter parameters
    log_type = request.GET.get('type', 'activity')  # 'activity' or 'system'
    activity_filter = request.GET.get('activity', 'all')
    user_filter = request.GET.get('user', 'all')
    date_filter = request.GET.get('date', '7')  # days

    # Date range
    days = int(date_filter) if date_filter.isdigit() else 7
    start_date = timezone.now() - timedelta(days=days)

    if log_type == 'activity':
        # Activity Logs
        logs = ActivityLog.objects.filter(timestamp__gte=start_date).select_related('user')

        # Filter by activity type
        if activity_filter != 'all':
            logs = logs.filter(activity_type=activity_filter)

        # Filter by user
        if user_filter != 'all' and user_filter.isdigit():
            logs = logs.filter(user_id=user_filter)

        # Get statistics
        total_activities = logs.count()
        unique_users = logs.values('user').distinct().count()

        # Activity breakdown
        activity_breakdown = logs.values('activity_type').annotate(
            count=models.Count('id')
        ).order_by('-count')

        stats = {
            'total': total_activities,
            'unique_users': unique_users,
            'breakdown': activity_breakdown,
        }
    else:
        # System Logs
        logs = SystemLog.objects.filter(timestamp__gte=start_date)

        # Filter by level
        if activity_filter != 'all':
            logs = logs.filter(level=activity_filter)

        # Get statistics
        total_logs = logs.count()
        errors = logs.filter(level='error').count()
        warnings = logs.filter(level='warning').count()

        # Log level breakdown
        level_breakdown = logs.values('level').annotate(
            count=models.Count('id')
        ).order_by('-count')

        stats = {
            'total': total_logs,
            'errors': errors,
            'warnings': warnings,
            'breakdown': level_breakdown,
        }

    # Pagination
    paginator = Paginator(logs, 10)  # 10 logs per page
    page_number = request.GET.get('page', 1)
    logs_page = paginator.get_page(page_number)

    # Get all users for filter dropdown
    User = get_user_model()
    all_users = User.objects.filter(is_active=True).order_by('email')

    context = {
        'logs': logs_page,
        'log_type': log_type,
        'activity_filter': activity_filter,
        'user_filter': user_filter,
        'date_filter': date_filter,
        'stats': stats,
        'all_users': all_users,
        'activity_types': ActivityLog.ACTIVITY_TYPES,
        'log_levels': SystemLog.LOG_LEVELS,
    }
    return render(request, 'admin/logs.html', context)
