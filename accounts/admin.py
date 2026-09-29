from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Профіль", {"fields": ("role", "avatar")}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Профіль", {"fields": ("role", "avatar")}),)
    list_display = ("username", "email", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")

