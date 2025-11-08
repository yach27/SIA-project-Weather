"""
Admin Views
Handles admin dashboard and management pages
"""
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import models
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib import messages
from datetime import timedelta
from ..models import ActivityLog, SystemLog, UserLocation, ChatMessage


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
    from ..models import UserLocation

    # Get all users excluding staff/admin with their locations
    all_users = User.objects.filter(
        is_staff=False,
        is_superuser=False
    ).select_related('current_location').order_by('-date_joined')

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


def admin_profile(request):
    """Admin profile page"""
    if not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)):
        return redirect('signin')

    # Get admin activity stats
    admin_activities = ActivityLog.objects.filter(
        user=request.user
    ).order_by('-timestamp')[:10]

    # Count total actions
    total_actions = ActivityLog.objects.filter(user=request.user).count()

    # Get recent chat history count
    from ..models import AdminChatHistory
    total_chats = AdminChatHistory.objects.filter(admin_user=request.user).count()

    context = {
        'recent_activities': admin_activities,
        'total_actions': total_actions,
        'total_chats': total_chats,
    }
    return render(request, 'admin/profile.html', context)


def admin_profile_edit(request):
    """Edit admin profile"""
    if not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)):
        return redirect('signin')

    if request.method == 'POST':
        from django.contrib import messages
        from django.core.files.storage import default_storage
        import os

        # Update user basic info
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()

        request.user.first_name = first_name
        request.user.last_name = last_name

        # Handle profile image upload
        if 'profile_pic' in request.FILES:
            uploaded_file = request.FILES['profile_pic']

            # Delete old image if exists
            if request.user.profile_pic:
                old_file_path = os.path.join('media', request.user.profile_pic)
                if default_storage.exists(old_file_path):
                    default_storage.delete(old_file_path)

            # Save new image
            file_path = default_storage.save(f'profile_images/{uploaded_file.name}', uploaded_file)
            request.user.profile_pic = file_path

        request.user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('admin_profile')

    return redirect('admin_profile')


def admin_profile_remove_image(request):
    """Remove admin profile image"""
    if not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)):
        return JsonResponse({'success': False, 'error': 'Unauthorized'})

    if request.method == 'POST':
        from django.core.files.storage import default_storage
        import os

        try:
            if request.user.profile_pic:
                # Delete file from storage
                old_file_path = os.path.join('media', request.user.profile_pic)
                if default_storage.exists(old_file_path):
                    default_storage.delete(old_file_path)

                # Clear database field
                request.user.profile_pic = None
                request.user.save()
                return JsonResponse({'success': True})
            return JsonResponse({'success': False, 'error': 'No image to remove'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request'})


# User Management Actions
def admin_get_user_details(request, user_id):
    """Get user details for viewing in modal"""
    if not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)):
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(id=user_id)

        # Get user's current location if exists
        location = None
        coordinates = None
        try:
            user_location = UserLocation.objects.filter(user=user).order_by('-timestamp').first()
            if user_location:
                location = user_location.location_name or f"{user_location.latitude}, {user_location.longitude}"
                coordinates = f"{user_location.latitude:.4f}, {user_location.longitude:.4f}"
        except:
            pass

        user_data = {
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name or '',
                'middle_name': user.middle_name if hasattr(user, 'middle_name') else '',
                'last_name': user.last_name or '',
                'email': user.email,
                'phone_number': user.phone_number if hasattr(user, 'phone_number') else '',
                'is_active': user.is_active,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'date_joined': user.date_joined.strftime('%B %d, %Y'),
                'last_login': user.last_login.strftime('%B %d, %Y at %I:%M %p') if user.last_login else 'Never',
                'location': location or '--',
                'coordinates': coordinates or '--',
            }
        }
        return JsonResponse(user_data)
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def admin_edit_user(request, user_id):
    """Edit user information"""
    if not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)):
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

    try:
        import json
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(id=user_id)

        data = json.loads(request.body)

        # Update user fields
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)

        # Update custom fields if they exist
        if hasattr(user, 'middle_name'):
            user.middle_name = data.get('middle_name', user.middle_name)
        if hasattr(user, 'phone_number'):
            user.phone_number = data.get('phone_number', user.phone_number)

        # Update role
        role = data.get('role', 'user')
        user.is_staff = role == 'admin'
        user.is_superuser = role == 'admin'

        # Update status
        is_active = data.get('is_active', 'true')
        user.is_active = is_active == 'true' or is_active == True

        # Update password if provided
        new_password = data.get('new_password')
        if new_password and new_password.strip():
            user.set_password(new_password)

        user.save()

        # Log the action
        ActivityLog.objects.create(
            user=request.user,
            activity_type='user_edit',
            description=f'Edited user: {user.username}'
        )

        return JsonResponse({'success': True, 'message': 'User updated successfully'})
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def admin_delete_user(request, user_id):
    """Delete a user account"""
    if not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)):
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(id=user_id)

        # Prevent self-deletion
        if user.id == request.user.id:
            return JsonResponse({'success': False, 'error': 'Cannot delete your own account'}, status=400)

        username = user.username

        # Log the action before deleting
        ActivityLog.objects.create(
            user=request.user,
            activity_type='user_delete',
            description=f'Deleted user: {username}'
        )

        # Delete the user
        user.delete()

        return JsonResponse({'success': True, 'message': f'User {username} deleted successfully'})
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
