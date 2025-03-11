from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet,
    ProductViewSet,
    ProductFormatViewSet,
    OrderViewSet,
    OrderItemViewSet,
)
from .OrderStatView import order_statistics, product_sales_ranking, monthly_orders_evolution

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'product-formats', ProductFormatViewSet)
router.register(r'orders', OrderViewSet,basename='order')
router.register(r'order-items', OrderItemViewSet,basename='order-items')

urlpatterns = [
    path('', include(router.urls)),
    path('order-statistics/', order_statistics, name='order-statistics'),
    path('product-sales-ranking/', product_sales_ranking, name='product-sales-ranking'),
    path('monthly-orders-evolution/', monthly_orders_evolution, name='monthly-orders-evolution'),
]
