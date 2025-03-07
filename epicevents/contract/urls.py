""" Module contains url endpoints for Contract"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContractViewSet, SearchContractViewSet

router = DefaultRouter()
router.register('contracts', SearchContractViewSet, basename='contracts')
router.register(r'clients/(?P<client_id>[^/.]+)/contracts', ContractViewSet,
                basename='client-contracts')

urlpatterns = [
    path('', include(router.urls))
]
