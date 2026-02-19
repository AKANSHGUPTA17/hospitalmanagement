from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from .forms import LoginForm, UserCreationForm, UserEditForm
from .models import User
from apps.authentication.decorators import admin_required


class LoginView(View):
    template_name = 'auth/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard:index')
        form = LoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                next_url = request.GET.get('next', 'dashboard:index')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
        return render(request, self.template_name, {'form': form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.info(request, 'You have been logged out.')
        return redirect('auth:login')


@login_required
def profile_view(request):
    return render(request, 'auth/profile.html', {'user': request.user})


@login_required
def change_password_view(request):
    from django.contrib.auth.forms import PasswordChangeForm
    from django.contrib.auth import update_session_auth_hash
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully.')
            return redirect('auth:profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'auth/change_password.html', {'form': form})


@admin_required
def user_list(request):
    users = User.objects.all().order_by('-created_at')
    return render(request, 'auth/user_list.html', {'users': users})


@admin_required
def user_create(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            messages.success(request, f'User {user.username} created successfully.')
            return redirect('auth:user_list')
    else:
        form = UserCreationForm()
    return render(request, 'auth/user_form.html', {'form': form, 'title': 'Create User'})


@admin_required
def user_edit(request, pk):
    user = User.objects.get(pk=pk)
    if request.method == 'POST':
        form = UserEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully.')
            return redirect('auth:user_list')
    else:
        form = UserEditForm(instance=user)
    return render(request, 'auth/user_form.html', {'form': form, 'title': 'Edit User'})


@admin_required
def user_toggle(request, pk):
    user = User.objects.get(pk=pk)
    user.is_active = not user.is_active
    user.save()
    status = 'activated' if user.is_active else 'deactivated'
    messages.success(request, f'User {user.username} has been {status}.')
    return redirect('auth:user_list')
