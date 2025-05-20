from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, ModulePermissionViewSet, StatsView,
    CustomTokenObtainPairView, UserLogoutView
)
from rest_framework_simplejwt.views import TokenRefreshView
from .views import UserByTypeViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'permissions', ModulePermissionViewSet, basename='module-permission')
router.register(r'usertype', UserByTypeViewSet, basename='usertype')
# router.register(r'super_admin', ByUserTypeView, basename='super_admin')
# router.register(r'admin', ByUserTypeView, basename='admin')
# router.register(r'fabricant', ByUserTypeView, basename='fabricant')
# router.register(r'grossiste', ByUserTypeView, basename='grossiste')
# router.register(r'semi_grossiste', ByUserTypeView, basename='semi_grossiste')
# router.register(r'detaillant', ByUserTypeView, basename='detaillant')
router.register(r'stats', StatsView, basename='stats')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]   