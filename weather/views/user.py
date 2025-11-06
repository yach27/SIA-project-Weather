"""
User Views
Handles user dashboard and weather-related pages
"""
from django.shortcuts import render, redirect


def user_dashboard(request):
    """User dashboard with weather overview"""
    if not request.user.is_authenticated:
        return redirect('signin')

    # Default context with placeholder data
    # Real data will be loaded via JavaScript using geolocation
    context = {
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
    }
    return render(request, 'user/dashboard.html', context)


def user_chat(request):
    """User chat interface with weather bot"""
    if not request.user.is_authenticated:
        return redirect('signin')

    context = {
        'messages': [],  # Add chat history here
    }
    return render(request, 'user/chat.html', context)


def current_weather(request):
    """Current weather detailed view"""
    if not request.user.is_authenticated:
        return redirect('signin')

    context = {}
    return render(request, 'user/current_weather.html', context)


def weather_forecast(request):
    """Weather forecast page"""
    if not request.user.is_authenticated:
        return redirect('signin')

    context = {}
    return render(request, 'user/forecast.html', context)


def weather_map(request):
    """Interactive weather map"""
    if not request.user.is_authenticated:
        return redirect('signin')

    context = {}
    return render(request, 'user/weather_map.html', context)


def weather_history(request):
    """Weather history and trends"""
    if not request.user.is_authenticated:
        return redirect('signin')

    context = {}
    return render(request, 'user/weather_history.html', context)


def health_tips(request):
    """Health and safety tips based on weather - AI-generated"""
    if not request.user.is_authenticated:
        return redirect('signin')

    context = {}
    return render(request, 'user/health_tips.html', context)


def weather_alerts(request):
    """Weather alerts and warnings"""
    if not request.user.is_authenticated:
        return redirect('signin')

    context = {}
    return render(request, 'user/weather_alerts.html', context)


def user_settings(request):
    """User settings and preferences"""
    if not request.user.is_authenticated:
        return redirect('signin')

    context = {}
    return render(request, 'user/settings.html', context)


def user_profile(request):
    """User profile page"""
    if not request.user.is_authenticated:
        return redirect('signin')

    context = {}
    return render(request, 'user/profile.html', context)


def user_profile_edit(request):
    """Edit user profile"""
    if not request.user.is_authenticated:
        return redirect('signin')

    if request.method == 'POST':
        from django.contrib import messages
        from django.core.files.storage import default_storage
        import os

        # Update user basic info
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        middle_name = request.POST.get('middle_name', '').strip()

        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.middle_name = middle_name

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
        return redirect('user_profile')

    return redirect('user_profile')


def user_profile_remove_image(request):
    """Remove user profile image"""
    from django.http import JsonResponse

    if not request.user.is_authenticated:
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
