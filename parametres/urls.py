from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CommuneViewSet, QuartierViewSet, ZoneViewSet, UserTypeViewSet,
    CategoryViewSet, CertificationViewSet, ShopTypeViewSet,
    TypeCommerceViewSet, TailleShopViewSet, FrequenceApprovisionnementViewSet,
    OrderStatusViewSet, TailleViewSet, CouleurViewSet, ModuleViewSet
)

router = DefaultRouter()
router.register(r'communes', CommuneViewSet, basename='commune')
router.register(r'quartiers', QuartierViewSet, basename='quartier')
router.register(r'zones', ZoneViewSet, basename='zone')
router.register(r'user-types', UserTypeViewSet, basename='user-type')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'certifications', CertificationViewSet, basename='certification')
router.register(r'shop-types', ShopTypeViewSet, basename='shop-type')
router.register(r'type-commerces', TypeCommerceViewSet, basename='type-commerce')
router.register(r'taille-shops', TailleShopViewSet, basename='taille-shop')
router.register(r'frequences-approvisionnement', FrequenceApprovisionnementViewSet, basename='frequence-approvisionnement')
router.register(r'order-statuses', OrderStatusViewSet, basename='order-status')
router.register(r'tailles', TailleViewSet, basename='taille')
router.register(r'couleurs', CouleurViewSet, basename='couleur')
router.register(r'modules', ModuleViewSet, basename='module')

urlpatterns = [
    path('', include(router.urls)),
]