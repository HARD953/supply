from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, ProductFormatViewSet, OrderViewSet, OrderItemViewSet, ProductStatsView, ShopStatsView

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'product-formats', ProductFormatViewSet, basename='product-format')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'order-items', OrderItemViewSet, basename='order-item')
router.register(r'stats-products', ProductStatsView, basename='product-stats')
router.register(r'stats-shops', ShopStatsView, basename='shop-stats')

urlpatterns = [
    path('', include(router.urls)),
]