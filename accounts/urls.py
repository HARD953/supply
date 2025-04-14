from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CustomTokenObtainPairView, UserLogoutView, UserRegistrationView,
    CurrentUserView, UserViewSet, UserViewSetCommune, UserViewSetQuartier,
    UserViewSetZone, ModuleViewSet, PermissionViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'commune', UserViewSetCommune, basename='user-commune')
router.register(r'quartier', UserViewSetQuartier, basename='user-quartier')
router.register(r'zone', UserViewSetZone, basename='user-zone')
router.register(r'modules', ModuleViewSet, basename='modules')
router.register(r'permissions', PermissionViewSet, basename='permissions')

urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', UserLogoutView.as_view(), name='user-logout'),
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('current-user/', CurrentUserView.as_view(), name='current-user'),
    path('', include(router.urls)),
]