from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, ByUserTypeView, ModulePermissionViewSet, StatsView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'permissions', ModulePermissionViewSet, basename='module-permission')
router.register(r'by-user-type', ByUserTypeView, basename='by-user-type')
router.register(r'stats', StatsView, basename='stats')

urlpatterns = [
    path('', include(router.urls)),
]