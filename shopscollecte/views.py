from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.renderers import JSONRenderer
from django.db.models import Count, Sum, Q, F
from datetime import datetime, timedelta
from .models import ProductCollecte
from .serializers import ProductCollecteSerializer, ProductCollecteStatsSerializer
from parametres.models import Module
from accounts.models import User
from shops.models import Shop

class CustomShopPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 100

    def get_page_size(self, request):
        try:
            limit = int(request.query_params.get(self.page_size_query_param, self.page_size))
            if limit <= 0:
                return self.page_size
            return min(limit, self.max_page_size)
        except (ValueError, TypeError):
            return self.page_size

    def get_paginated_response(self, data):
        return Response({
            'total': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'data': data
        })

class ReadOnlyOrAuthenticated(IsAuthenticated):
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return super().has_permission(request, view)

class BaseViewSet(viewsets.ModelViewSet):
    pagination_class = CustomShopPagination
    renderer_classes = [JSONRenderer]  # Forcer JSON

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        if request.query_params.get('paginate') == 'true':
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(queryset, request)
            serializer = self.get_serializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        return Response(serializer.data)

class ProductCollecteViewSet(BaseViewSet):
    serializer_class = ProductCollecteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'supplier', 'name']
    search_fields = ['name', 'category__name', 'supplier__name']
    module_name = 'ProductsCollecte'

    def get_queryset(self):
        if self.request.user.is_staff:
            return ProductCollecte.objects.all().select_related('owner', 'category', 'frequence_appr', 'supplier')
        return ProductCollecte.objects.filter(owner=self.request.user).select_related('owner', 'category', 'frequence_appr', 'supplier')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsAdminUser]
        return super().get_permissions()

class ProductCollecteStatsView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = CustomShopPagination
    renderer_classes = [JSONRenderer]  # Forcer JSON

    def list(self, request):
        # Filtre temporel optionnel
        days = int(request.query_params.get('days', 30))
        start_date = datetime.now() - timedelta(days=days)

        # Statistiques générales
        total_products = ProductCollecte.objects.count()
        recent_products = ProductCollecte.objects.filter(created_at__gte=start_date).count()
        total_stock = ProductCollecte.objects.aggregate(total=Sum('stock'))['total'] or 0
        total_value = ProductCollecte.objects.aggregate(
            total=Sum(F('stock') * F('price'))
        )['total'] or 0
        total_owners = User.objects.filter(shopscollecte__isnull=False).distinct().count()
        total_suppliers = Shop.objects.filter(products__isnull=False).distinct().count()

        # Statistiques par propriétaire
        owner_stats = User.objects.filter(shopscollecte__isnull=False).values(
            'username', 'email', 'user_type__name'
        ).annotate(
            total_products=Count('shopscollecte'),
            total_stock=Sum('shopscollecte__stock'),
            total_value=Sum(F('shopscollecte__stock') * F('shopscollecte__price')),
            avg_reorder_frequency=Sum('shopscollecte__reorder_frequency') / Count('shopscollecte')
        ).order_by('-total_products')

        # Statistiques par boutique fournisseur
        supplier_stats = Shop.objects.filter(products__isnull=False).values(
            'name', 'owner__username', 'typecommerce__name'
        ).annotate(
            total_products=Count('products'),
            total_stock=Sum('products__stock'),
            total_value=Sum(F('products__stock') * F('products__price')),
            avg_reorder_frequency=Sum('products__reorder_frequency') / Count('products')
        ).order_by('-total_products')

        # Répartition par catégorie
        category_stats = ProductCollecte.objects.values('category__name').annotate(
            total_products=Count('id'),
            total_stock=Sum('stock'),
            total_value=Sum(F('stock') * F('price'))
        ).order_by('-total_products')

        # Répartition par fréquence d'approvisionnement
        frequence_appr_stats = ProductCollecte.objects.values('frequence_appr__name').annotate(
            total_products=Count('id'),
            total_stock=Sum('stock'),
            total_value=Sum(F('stock') * F('price'))
        ).order_by('-total_products')

        response_data = {
            'overview': {
                'total_products': total_products,
                'recent_products': recent_products,
                'total_stock': total_stock,
                'total_value': float(total_value) if total_value else 0.0,
                'total_owners': total_owners,
                'total_suppliers': total_suppliers,
                'timeframe_days': days
            },
            'by_owner': list(owner_stats),
            'by_supplier': list(supplier_stats),
            'by_category': list(category_stats),
            'by_frequence_appr': list(frequence_appr_stats)
        }

        # Pagination conditionnelle pour les sections paginables
        paginable_sections = ['by_owner', 'by_supplier', 'by_category', 'by_frequence_appr']
        if request.query_params.get('paginate') == 'true':
            paginator = self.pagination_class()
            for section in paginable_sections:
                response_data[section] = paginator.paginate_queryset(response_data[section], request)
            return paginator.get_paginated_response(response_data)

        serializer = ProductCollecteStatsSerializer(response_data)
        return Response(serializer.data)