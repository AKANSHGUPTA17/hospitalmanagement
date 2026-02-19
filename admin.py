from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'full_name', 'email', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering = ['-created_at']

    fieldsets = UserAdmin.fieldsets + (
        ('Hospital Info', {'fields': ('role', 'phone', 'profile_picture')}),
    )

    def full_name(self, obj):
        return obj.get_full_name()
    full_name.short_description = 'Full Name'
