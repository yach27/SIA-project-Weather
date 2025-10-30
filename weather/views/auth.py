"""
Authentication Views
Handles user login, registration, and logout
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def home(request):
    """Landing page"""
    return render(request, 'weather/home.html')


def signin(request):
    """User sign in page"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Try to find user by email (since Django uses username by default)
        from django.contrib.auth.models import User
        try:
            user_obj = User.objects.filter(email=email).first()
            if user_obj:
                username = user_obj.username
            else:
                # Try to authenticate with email as username
                username = email
        except User.DoesNotExist:
            # Try to authenticate with email as username
            username = email

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Redirect based on user type
            if user.is_staff or user.is_superuser:
                return redirect('admin_dashboard')
            else:
                return redirect('user_dashboard')
        else:
            messages.error(request, 'Invalid email or password')

    return render(request, 'weather/signin.html')


def signup(request):
    """User registration page"""
    # Signup logic here
    return render(request, 'weather/signup.html')


def user_logout(request):
    """User logout"""
    # Log the logout activity BEFORE logging out (only for regular users, not superusers/admins)
    if request.user.is_authenticated and not request.user.is_superuser:
        from ..models import ActivityLog

        # Get client IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')

        # Get user agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]

        # Create logout log
        try:
            ActivityLog.objects.create(
                user=request.user,
                activity_type='logout',
                description=f'User {request.user.email} logged out',
                ip_address=ip_address,
                user_agent=user_agent,
                metadata=None
            )
        except Exception as e:
            print(f"Failed to log logout activity: {e}")

    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('signin')
