from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet,
    ProductViewSet,
    ProductFormatViewSet,
    OrderViewSet,
    OrderItemViewSet,
)
from .viewnp import (
    CategoryViewSetP,
    ProductViewSetP,
    ProductFormatViewSetP,
    OrderViewSetP,
    OrderItemViewSetP,
)
from .OrderStatView import order_statistics, product_sales_ranking, monthly_orders_evolution

router = DefaultRouter()
router.register(r'categories', CategoryViewSet,basename='categorie')
router.register(r'products', ProductViewSet,basename='product')
router.register(r'product-formats', ProductFormatViewSet,basename='products-f')
router.register(r'orders', OrderViewSet,basename='order')
router.register(r'order-items', OrderItemViewSet,basename='order-items')

urlpatterns = [
    path('', include(router.urls)),
    path('order-statistics/', order_statistics, name='order-statistics'),
    path('product-sales-ranking/', product_sales_ranking, name='product-sales-ranking'),
    path('monthly-orders-evolution/', monthly_orders_evolution, name='monthly-orders-evolution'),
    #paginate
path('categories/paginate', CategoryViewSetP.as_view({
    'get': 'list',
    'post': 'create',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
}), name='paginate-c'),

path('products/paginate', ProductViewSetP.as_view({
    'get': 'list',
    'post': 'create',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
}), name='paginate-pr'),

path('product-formats/paginate', ProductFormatViewSetP.as_view({
    'get': 'list',
    'post': 'create',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
}), name='paginate-prf'),

path('orders/paginate', OrderViewSetP.as_view({
    'get': 'list',
    'post': 'create',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
}), name='paginate-o'),

path('order-items/paginate', OrderItemViewSetP.as_view({
    'get': 'list',
    'post': 'create',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
}), name='paginate-orders-i'),
]
