""" Module contains login url endpoint"""

from django.urls import path
from .views import TeamLoginView

urlpatterns = [
    path('login/', TeamLoginView.as_view(), name='team-login'),
]