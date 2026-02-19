from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('auth:login')
        if not request.user.is_admin:
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('dashboard:index')
        return view_func(request, *args, **kwargs)
    return wrapper


def doctor_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('auth:login')
        if not (request.user.is_doctor or request.user.is_admin):
            messages.error(request, 'Access denied. Doctor privileges required.')
            return redirect('dashboard:index')
        return view_func(request, *args, **kwargs)
    return wrapper


def receptionist_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('auth:login')
        if not (request.user.is_receptionist or request.user.is_admin):
            messages.error(request, 'Access denied.')
            return redirect('dashboard:index')
        return view_func(request, *args, **kwargs)
    return wrapper


def staff_required(view_func):
    """Allow any authenticated staff member"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('auth:login')
        return view_func(request, *args, **kwargs)
    return wrapper
