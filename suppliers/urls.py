from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
# router.register(r'suppliers', SupplierViewSet, basename='supplier')
# router.register(r'commune', SupplierViewSetCommune, basename='supplier-commune')
# router.register(r'quartier', SupplierViewSetQuartier, basename='supplier-quartier')
# router.register(r'zone', SupplierViewSetZone, basename='supplier-zone')

urlpatterns = router.urls