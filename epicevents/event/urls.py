from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet

router = DefaultRouter()
router.register(r'clients/(?P<client_id>[^/.]+)/contracts/(?P<contract_id>[^/.]+)/events', EventViewSet,
                basename='contracts-events')

urlpatterns = [
    path('', include(router.urls))
]
