from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ShopViewSet, ShopViewSetSupplier, ShopStatsByTypeView, ShopStatsByBrandView,
    ShopStatsByDateView, ShopStatsByMonthView, ShopStatsByYearView, ShopStatsView
)

router = DefaultRouter()
router.register(r'shops', ShopViewSet, basename='shop')
router.register(r'shops-supplier', ShopViewSetSupplier, basename='shop-supplier')
router.register(r'stats-shops-by-type', ShopStatsByTypeView, basename='stats-shops-by-type')
router.register(r'stats-shops-by-brand', ShopStatsByBrandView, basename='stats-shops-by-brand')
router.register(r'stats-shops-by-date', ShopStatsByDateView, basename='stats-shops-by-date')
router.register(r'stats-shops-by-month', ShopStatsByMonthView, basename='stats-shops-by-month')
router.register(r'stats-shops-by-year', ShopStatsByYearView, basename='stats-shops-by-year')
router.register(r'stat-shops', ShopStatsView, basename='stats-shops')

urlpatterns = [
    path('', include(router.urls)),
]