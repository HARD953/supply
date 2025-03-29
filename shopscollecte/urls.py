from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, CertificationViewSet, ProductViewSet
from .viewsp import CategoryViewSetP, CertificationViewSetP, ProductViewSetP

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'certifications', CertificationViewSet)
router.register(r'productscollecte', ProductViewSet, basename='productscollecte-supplier')

urlpatterns = [
    path('', include(router.urls)),
    path('categories/paginate', CategoryViewSetP.as_view({
    'get': 'list',
    'post': 'create',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
}), name='categoriesP'),
    path('certifications/paginate', CertificationViewSetP.as_view({
    'get': 'list',
    'post': 'create',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
}), name='certificationsP'),
    path('productscollecte/paginate', ProductViewSetP.as_view({
    'get': 'list',
    'post': 'create',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
}), name='productscollecteP'),
]