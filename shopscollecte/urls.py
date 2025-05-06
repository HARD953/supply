from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductCollecteViewSet, ProductCollecteStatsView

router = DefaultRouter()
router.register(r'products-collecte', ProductCollecteViewSet, basename='products-collecte')
router.register(r'stats-collecte', ProductCollecteStatsView, basename='stats-collecte')

urlpatterns = [
    path('', include(router.urls)),
]