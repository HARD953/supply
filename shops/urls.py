from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    ShopViewSet,
    ShopViewSetSupplier,
    ShopStatsByTypeView,
    ShopStatsByDateView,
    ShopStatsByMonthView,
    ShopStatsByYearView,
    ShopStatsByBranView
)
from .viewsp import (
    ShopViewSetP,
    ShopViewSetSupplierP)

router = DefaultRouter()
router.register(r'shops', ShopViewSet, basename='shop')
router.register(r'suppliername', ShopViewSetSupplier, basename='shop-supplier')

urlpatterns = [
    path('stats/by-type/', ShopStatsByTypeView.as_view(), name='shop-stats-by-type'),
    path('stats/by-brand/', ShopStatsByBranView.as_view(), name='shop-stats-by-brand'),
    path('stats/by-date/', ShopStatsByDateView.as_view(), name='shop-stats-by-date'),
    path('stats/by-month/', ShopStatsByMonthView.as_view(), name='shop-stats-by-month'),
    path('stats/by-year/', ShopStatsByYearView.as_view(), name='shop-stats-by-year'),

    path('shops/paginate', ShopViewSetP.as_view({
    'get': 'list',
    'post': 'create',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
}), name='shopP'),
    path('suppliername/paginate', ShopViewSetSupplierP.as_view({
    'get': 'list',
    'post': 'create',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
}), name='shop-supplierP'),
]

urlpatterns += router.urls