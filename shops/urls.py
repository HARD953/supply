from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    ShopViewSet,
    ShopStatsByTypeView,
    ShopStatsByDateView,
    ShopStatsByMonthView,
    ShopStatsByYearView,
    ShopStatsByBranView
)

router = DefaultRouter()
router.register(r'shops', ShopViewSet)

urlpatterns = [
    path('stats/by-type/', ShopStatsByTypeView.as_view(), name='shop-stats-by-type'),
     path('stats/by-brand/', ShopStatsByBranView.as_view(), name='shop-stats-by-brand'),
    path('stats/by-date/', ShopStatsByDateView.as_view(), name='shop-stats-by-date'),
    path('stats/by-month/', ShopStatsByMonthView.as_view(), name='shop-stats-by-month'),
    path('stats/by-year/', ShopStatsByYearView.as_view(), name='shop-stats-by-year'),
]

urlpatterns += router.urls