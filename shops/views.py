from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from django.db.models.functions import TruncDate, TruncMonth, TruncYear
from rest_framework.renderers import JSONRenderer
from django.db.models import Count, Sum, Q, F, Avg
from datetime import datetime, timedelta
from .models import Shop
from .serializers import (
    ShopSerializer, ShopSerializerSupplier, ShopStatsByTypeSerializer,
    ShopStatsByDateSerializer, ShopStatsByMonthSerializer, ShopStatsByYearSerializer,
    ShopStatsByBrandSerializer, ShopStatsSerializer
)
from parametres.models import Module
from accounts.models import User

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

class ShopViewSet(BaseViewSet):
    serializer_class = ShopSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['type', 'typecommerce', 'taille', 'brand']
    search_fields = ['name', 'address', 'owner_name']
    module_name = 'Shops'

    def get_queryset(self):
        if self.request.user.is_staff:
            return Shop.objects.all().select_related('owner', 'type', 'typecommerce', 'taille', 'frequence_appr')
        return Shop.objects.filter(owner=self.request.user).select_related('owner', 'type', 'typecommerce', 'taille', 'frequence_appr')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsAdminUser]
        return super().get_permissions()

class ShopViewSetSupplier(BaseViewSet):
    serializer_class = ShopSerializerSupplier
    permission_classes = [ReadOnlyOrAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name']
    search_fields = ['name']
    module_name = 'Shops'

    def get_queryset(self):
        if self.request.user.is_staff:
            return Shop.objects.all().only('id', 'name')
        return Shop.objects.filter(owner=self.request.user).only('id', 'name')

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsAdminUser]
        return super().get_permissions()

class ShopStatsByTypeView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomShopPagination
    renderer_classes = [JSONRenderer]  # Forcer JSON
    module_name = 'Shops'

    def list(self, request):
        shop_stats = (
            Shop.objects.filter(owner=request.user)
            .values('typecommerce')
            .annotate(total=Count('id'))
            .order_by('typecommerce')
        )

        if request.query_params.get('paginate') == 'true':
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(shop_stats, request)
            serializer = ShopStatsByTypeSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = ShopStatsByTypeSerializer(shop_stats, many=True)
        return Response(serializer.data)

class ShopStatsByBrandView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomShopPagination
    renderer_classes = [JSONRenderer]  # Forcer JSON
    module_name = 'Shops'

    def list(self, request):
        shop_stats = (
            Shop.objects.filter(owner=request.user)
            .values('type')
            .annotate(total=Count('id'))
            .order_by('type')
        )

        if request.query_params.get('paginate') == 'true':
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(shop_stats, request)
            serializer = ShopStatsByBrandSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = ShopStatsByBrandSerializer(shop_stats, many=True)
        return Response(serializer.data)

class ShopStatsByDateView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomShopPagination
    renderer_classes = [JSONRenderer]  # Forcer JSON
    module_name = 'Shops'

    def list(self, request):
        shop_stats = (
            Shop.objects.filter(owner=request.user)
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(total=Count('id'))
            .order_by('date')
        )

        if request.query_params.get('paginate') == 'true':
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(shop_stats, request)
            serializer = ShopStatsByDateSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = ShopStatsByDateSerializer(shop_stats, many=True)
        return Response(serializer.data)

class ShopStatsByMonthView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomShopPagination
    renderer_classes = [JSONRenderer]  # Forcer JSON
    module_name = 'Shops'

    def list(self, request):
        shop_stats = (
            Shop.objects.filter(owner=request.user)
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(total=Count('id'))
            .order_by('month')
        )

        if request.query_params.get('paginate') == 'true':
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(shop_stats, request)
            serializer = ShopStatsByMonthSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = ShopStatsByMonthSerializer(shop_stats, many=True)
        return Response(serializer.data)

class ShopStatsByYearView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomShopPagination
    renderer_classes = [JSONRenderer]  # Forcer JSON
    module_name = 'Shops'

    def list(self, request):
        shop_stats = (
            Shop.objects.filter(owner=request.user)
            .annotate(year=TruncYear('created_at'))
            .values('year')
            .annotate(total=Count('id'))
            .order_by('year')
        )

        if request.query_params.get('paginate') == 'true':
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(shop_stats, request)
            serializer = ShopStatsByYearSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = ShopStatsByYearSerializer(shop_stats, many=True)
        return Response(serializer.data)

class ShopStatsView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = CustomShopPagination
    renderer_classes = [JSONRenderer]  # Forcer JSON

    def list(self, request):
        # Filtre temporel optionnel
        days = int(request.query_params.get('days', 30))
        start_date = datetime.now() - timedelta(days=days)

        # Statistiques générales
        total_shops = Shop.objects.count()
        recent_shops = Shop.objects.filter(created_at__gte=start_date).count()
        total_suppliers = User.objects.filter(shops__isnull=False).distinct().count()
        total_order_users = User.objects.filter(orders__isnull=False).distinct().count()

        # Statistiques par boutique
        shop_stats = Shop.objects.values(
            'name', 'owner__username', 'type__name', 'typecommerce__name', 'taille__name', 'frequence_appr__name'
        ).annotate(
            total_products=Count('owner__products'),
            total_sales=Sum('owner__products__formats__order_items__quantity'),
            total_orders=Count('owner__products__formats__order_items__order', distinct=True)
        ).order_by('-total_products')

        # Répartition des boutiques par type de commerce
        shop_by_typecommerce = Shop.objects.values('typecommerce__name').annotate(
            total=Count('id'),
            total_products=Count('owner__products'),
            total_orders=Count('owner__products__formats__order_items__order', distinct=True)
        ).order_by('-total')

        # Répartition des boutiques par type de boutique
        shop_by_type = Shop.objects.values('type__name').annotate(
            total=Count('id'),
            total_products=Count('owner__products'),
            total_orders=Count('owner__products__formats__order_items__order', distinct=True)
        ).order_by('-total')

        # Répartition des boutiques par taille
        shop_by_taille = Shop.objects.values('taille__name').annotate(
            total=Count('id'),
            total_products=Count('owner__products'),
            total_orders=Count('owner__products__formats__order_items__order', distinct=True)
        ).order_by('-total')

        # Répartition des boutiques par fréquence d'approvisionnement
        shop_by_frequence_appr = Shop.objects.values('frequence_appr__name').annotate(
            total=Count('id'),
            total_products=Count('owner__products'),
            total_orders=Count('owner__products__formats__order_items__order', distinct=True)
        ).order_by('-total')

        # Statistiques par fournisseur
        supplier_stats = User.objects.filter(shops__isnull=False).values(
            'username', 'email', 'user_type__name'
        ).annotate(
            total_shops=Count('shops'),
            total_products=Count('products'),
            total_sales=Sum('products__formats__order_items__quantity'),
            total_orders=Count('products__formats__order_items__order', distinct=True)
        ).order_by('-total_shops')

        # Statistiques par utilisateur des commandes
        order_user_stats = User.objects.filter(orders__isnull=False).values(
            'username', 'email', 'user_type__name'
        ).annotate(
            total_orders=Count('orders'),
            recent_orders=Count('orders', filter=Q(orders__created_at__gte=start_date)),
            total_items=Sum('orders__items__quantity'),
            total_products=Count('orders__items__product_format__product', distinct=True)
        ).order_by('-total_orders')[:5]

        # Répartition des utilisateurs des commandes par type d'utilisateur
        order_user_by_user_type = User.objects.filter(orders__isnull=False).values(
            'user_type__name'
        ).annotate(
            total=Count('id'),
            total_orders=Count('orders'),
            total_items=Sum('orders__items__quantity')
        ).order_by('-total')

        response_data = {
            'overview': {
                'total_shops': total_shops,
                'recent_shops': recent_shops,
                'total_suppliers': total_suppliers,
                'total_order_users': total_order_users,
                'timeframe_days': days
            },
            'by_shop': list(shop_stats),
            'shops_by_typecommerce': list(shop_by_typecommerce),
            'shops_by_type': list(shop_by_type),
            'shops_by_taille': list(shop_by_taille),
            'shops_by_frequence_appr': list(shop_by_frequence_appr),
            'by_supplier': list(supplier_stats),
            'by_order_user': list(order_user_stats),
            'order_users_by_user_type': list(order_user_by_user_type)
        }

        # Pagination conditionnelle pour les sections paginables
        paginable_sections = [
            'by_shop', 'shops_by_typecommerce', 'shops_by_type', 'shops_by_taille',
            'shops_by_frequence_appr', 'by_supplier', 'by_order_user', 'order_users_by_user_type'
        ]
        if request.query_params.get('paginate') == 'true':
            paginator = self.pagination_class()
            for section in paginable_sections:
                response_data[section] = paginator.paginate_queryset(response_data[section], request)
            return paginator.get_paginated_response(response_data)

        serializer = ShopStatsSerializer(response_data)
        return Response(serializer.data)