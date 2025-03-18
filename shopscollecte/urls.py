from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, CertificationViewSet, ProductViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'certifications', CertificationViewSet)
router.register(r'productscollecte', ProductViewSet, basename='productscollecte-supplier')

urlpatterns = [
    path('', include(router.urls)),
]