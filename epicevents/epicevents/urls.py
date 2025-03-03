"""
URL configuration for epicevents project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('usermodel.urls')),
    path('api/', include('client.urls')),
    path('api/', include('contract.urls')),
    path('api/', include('event.urls'))
]
