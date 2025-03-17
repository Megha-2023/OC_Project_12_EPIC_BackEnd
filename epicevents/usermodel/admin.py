from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from client.models import Client
from contract.models import Contract
from event.models import Event
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


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'company_name', 'client_status', 'sales_contact')

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_client_id', 'sales_contact', 'amount', 'date_created', 'contract_status')

    def get_client_id(self, obj):
        return obj.client.id

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_contract_id', 'support_contact', 'date_created',
                    'event_date', 'event_completed')
    
    def get_contract_id(self, obj):
        return obj.contract.id

