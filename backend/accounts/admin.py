from django.contrib import admin
from .models import Users, UserProfiles, Friendships, StreakRescues

@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'is_active']

@admin.register(UserProfiles)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'pesa_points', 'profession', 'streak_days']