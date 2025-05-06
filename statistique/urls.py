from django.urls import path
from .views import (
    UserStatsView, ShopStatsView, ProductStatsView,
    OrderStatsView, ProductCollecteStatsView, ModuleStatsView
)

urlpatterns = [
    path('users-stat/', UserStatsView.as_view(), name='user-stats'),
    path('shops-stat/', ShopStatsView.as_view(), name='shop-stats'),
    path('products-stat/', ProductStatsView.as_view(), name='product-stats'),
    path('products-collecte-stat/', ProductCollecteStatsView.as_view(), name='product-collecte-stats'),
    path('orders-stat/', OrderStatsView.as_view(), name='order-stats'),
    path('modules-stat/', ModuleStatsView.as_view(), name='module-stats'),
]