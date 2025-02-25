from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from client.models import Client
from .models import Roles, CustomUsers

# Register your models here.
@admin.register(Roles)
class RolesAdmin(admin.ModelAdmin):
    list_display = ('id', 'role_name')


@admin.register(CustomUsers)
class CustomUsersAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')

    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', )}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('role',)}),
    )

admin.site.register(Client)
