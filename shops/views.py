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
    renderer_classes = [JSONRenderer]

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
        user = self.request.user
        if user.is_authenticated:
            if user.user_type.name.lower() == 'super_admin':
                return Shop.objects.all().select_related('owner', 'type', 'typecommerce', 'taille', 'frequence_appr')
            return Shop.objects.filter(
                owner=user
            ).select_related('owner', 'type', 'typecommerce', 'taille', 'frequence_appr')
        return Shop.objects.none()

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
        user = self.request.user
        if user.is_authenticated:
            if user.user_type.name.lower() == 'super_admin':
                return Shop.objects.all().only('id', 'name')
            return Shop.objects.filter(
                owner=user
            ).only('id', 'name')
        return Shop.objects.none()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsAdminUser]
        return super().get_permissions()

class ShopStatsByTypeView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomShopPagination
    renderer_classes = [JSONRenderer]
    module_name = 'Shops'

    def list(self, request):
        user = request.user
        is_super_admin = user.user_type.name.lower() == 'super_admin'
        shop_queryset = Shop.objects.all()

        if not is_super_admin:
            shop_queryset = shop_queryset.filter(owner=user)

        shop_stats = (
            shop_queryset.values('typecommerce')
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
    renderer_classes = [JSONRenderer]
    module_name = 'Shops'

    def list(self, request):
        user = request.user
        is_super_admin = user.user_type.name.lower() == 'super_admin'
        shop_queryset = Shop.objects.all()

        if not is_super_admin:
            shop_queryset = shop_queryset.filter(owner=user)

        shop_stats = (
            shop_queryset.values('type')
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
    renderer_classes = [JSONRenderer]
    module_name = 'Shops'

    def list(self, request):
        user = request.user
        is_super_admin = user.user_type.name.lower() == 'super_admin'
        shop_queryset = Shop.objects.all()

        if not is_super_admin:
            shop_queryset = shop_queryset.filter(owner=user)

        shop_stats = (
            shop_queryset.annotate(date=TruncDate('created_at'))
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
    renderer_classes = [JSONRenderer]
    module_name = 'Shops'

    def list(self, request):
        user = request.user
        is_super_admin = user.user_type.name.lower() == 'super_admin'
        shop_queryset = Shop.objects.all()

        if not is_super_admin:
            shop_queryset = shop_queryset.filter(owner=user)

        shop_stats = (
            shop_queryset.annotate(month=TruncMonth('created_at'))
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
    renderer_classes = [JSONRenderer]
    module_name = 'Shops'

    def list(self, request):
        user = request.user
        is_super_admin = user.user_type.name.lower() == 'super_admin'
        shop_queryset = Shop.objects.all()

        if not is_super_admin:
            shop_queryset = shop_queryset.filter(owner=user)

        shop_stats = (
            shop_queryset.annotate(year=TruncYear('created_at'))
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

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from datetime import datetime, timedelta
from django.db.models import Count, Sum, Q
from .serializers import (
    OverviewSerializer, ShopStatsSerializer, TypeCommerceStatsSerializer,
    ShopTypeStatsSerializer, TailleStatsSerializer, FrequenceApprStatsSerializer,
    OwnerStatsSerializer, CommuneStatsSerializer, QuartierStatsSerializer, ZoneStatsSerializer
)
from .models import Shop


class ShopStatsView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = CustomShopPagination
    renderer_classes = [JSONRenderer]

    def get_base_querysets(self, request):
        """Retourne les querysets filtrés selon le type d'utilisateur."""
        user = request.user
        is_super_admin = user.user_type.name.lower() == 'super_admin'

        shop_queryset = Shop.objects.all()
        user_queryset = User.objects.all()

        if not is_super_admin:
            shop_queryset = shop_queryset.filter(owner=user)
            user_queryset = user_queryset.filter(shops__owner=user).distinct()

        return shop_queryset, user_queryset

    def get_days_and_start_date(self, request):
        """Retourne le nombre de jours et la date de début."""
        days = int(request.query_params.get('days', 30))
        start_date = datetime.now() - timedelta(days=days)
        return days, start_date

    def paginate_if_needed(self, data, request):
        """Applique la pagination si demandée."""
        if request.query_params.get('paginate') == 'true':
            paginator = self.pagination_class()
            return paginator.paginate_queryset(data, request), paginator
        return data, None

    @action(detail=False, methods=['get'], url_path='overview')
    def overview(self, request):
        """Statistiques générales des boutiques."""
        shop_queryset, user_queryset = self.get_base_querysets(request)
        days, start_date = self.get_days_and_start_date(request)

        total_shops = shop_queryset.count()
        recent_shops = shop_queryset.filter(created_at__gte=start_date).count()
        total_suppliers = user_queryset.filter(shops__isnull=False).distinct().count()

        response_data = {
            'total_shops': total_shops,
            'recent_shops': recent_shops,
            'total_suppliers': total_suppliers,
            'timeframe_days': days
        }

        serializer = OverviewSerializer(response_data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-shop')
    def by_shop(self, request):
        """Statistiques par boutique."""
        shop_queryset, _ = self.get_base_querysets(request)

        shop_stats = shop_queryset.values(
            'name', 'owner__username', 'type__name', 'typecommerce__name', 'taille__name', 'frequence_appr__name'
        ).annotate(
            total_products=Count('owner__products'),
            total_sales=Sum('owner__products__formats__order_items__quantity'),
            total_orders=Count('owner__products__formats__order_items__order', distinct=True)
        ).order_by('-total_products')

        shop_stats, paginator = self.paginate_if_needed(list(shop_stats), request)
        serializer = ShopStatsSerializer(shop_stats, many=True)

        if paginator:
            return paginator.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-typecommerce')
    def shops_by_typecommerce(self, request):
        """Boutiques par type de commerce."""
        shop_queryset, _ = self.get_base_querysets(request)

        shop_by_typecommerce = shop_queryset.values('typecommerce__name').annotate(
            total=Count('id'),
            total_products=Count('owner__products'),
            total_orders=Count('owner__products__formats__order_items__order', distinct=True)
        ).order_by('-total')

        shop_by_typecommerce, paginator = self.paginate_if_needed(list(shop_by_typecommerce), request)
        serializer = TypeCommerceStatsSerializer(shop_by_typecommerce, many=True)

        if paginator:
            return paginator.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-type')
    def shops_by_type(self, request):
        """Boutiques par type de boutique."""
        shop_queryset, _ = self.get_base_querysets(request)

        shop_by_type = shop_queryset.values('type__name').annotate(
            total=Count('id'),
            total_products=Count('owner__products'),
            total_orders=Count('owner__products__formats__order_items__order', distinct=True)
        ).order_by('-total')

        shop_by_type, paginator = self.paginate_if_needed(list(shop_by_type), request)
        serializer = ShopTypeStatsSerializer(shop_by_type, many=True)

        if paginator:
            return paginator.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-taille')
    def shops_by_taille(self, request):
        """Boutiques par taille."""
        shop_queryset, _ = self.get_base_querysets(request)

        shop_by_taille = shop_queryset.values('taille__name').annotate(
            total=Count('id'),
            total_products=Count('owner__products'),
            total_orders=Count('owner__products__formats__order_items__order', distinct=True)
        ).order_by('-total')

        shop_by_taille, paginator = self.paginate_if_needed(list(shop_by_taille), request)
        serializer = TailleStatsSerializer(shop_by_taille, many=True)

        if paginator:
            return paginator.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-frequence-appr')
    def shops_by_frequence_appr(self, request):
        """Boutiques par fréquence d'approvisionnement."""
        shop_queryset, _ = self.get_base_querysets(request)

        shop_by_frequence_appr = shop_queryset.values('frequence_appr__name').annotate(
            total=Count('id'),
            total_products=Count('owner__products'),
            total_orders=Count('owner__products__formats__order_items__order', distinct=True)
        ).order_by('-total')

        shop_by_frequence_appr, paginator = self.paginate_if_needed(list(shop_by_frequence_appr), request)
        serializer = FrequenceApprStatsSerializer(shop_by_frequence_appr, many=True)

        if paginator:
            return paginator.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-owner')
    def by_owner(self, request):
        """Statistiques par propriétaire de boutique."""
        shop_queryset, user_queryset = self.get_base_querysets(request)

        owner_stats = user_queryset.filter(shops__isnull=False).values(
            'username', 'email', 'user_type__name'
        ).annotate(
            total_shops=Count('shops'),
            total_products=Count('products'),
            total_sales=Sum('products__formats__order_items__quantity'),
            total_orders=Count('products__formats__order_items__order', distinct=True)
        ).order_by('-total_shops')

        owner_stats, paginator = self.paginate_if_needed(list(owner_stats), request)
        serializer = OwnerStatsSerializer(owner_stats, many=True)

        if paginator:
            return paginator.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-commune')
    def by_commune(self, request):
        """Boutiques par commune."""
        shop_queryset, _ = self.get_base_querysets(request)

        commune_stats = shop_queryset.values('commune__name').annotate(
            total=Count('id'),
            total_products=Count('owner__products'),
            total_orders=Count('owner__products__formats__order_items__order', distinct=True)
        ).order_by('-total')

        commune_stats, paginator = self.paginate_if_needed(list(commune_stats), request)
        serializer = CommuneStatsSerializer(commune_stats, many=True)

        if paginator:
            return paginator.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-quartier')
    def by_quartier(self, request):
        """Boutiques par quartier."""
        shop_queryset, _ = self.get_base_querysets(request)

        quartier_stats = shop_queryset.values('quartier__name', 'commune__name').annotate(
            total=Count('id'),
            total_products=Count('owner__products'),
            total_orders=Count('owner__products__formats__order_items__order', distinct=True)
        ).order_by('-total')

        quartier_stats, paginator = self.paginate_if_needed(list(quartier_stats), request)
        serializer = QuartierStatsSerializer(quartier_stats, many=True)

        if paginator:
            return paginator.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-zone')
    def by_zone(self, request):
        """Boutiques par zone."""
        shop_queryset, _ = self.get_base_querysets(request)

        zone_stats = shop_queryset.values('zone__name', 'commune__name').annotate(
            total=Count('id'),
            total_products=Count('owner__products'),
            total_orders=Count('owner__products__formats__order_items__order', distinct=True)
        ).order_by('-total')

        zone_stats, paginator = self.paginate_if_needed(list(zone_stats), request)
        serializer = ZoneStatsSerializer(zone_stats, many=True)

        if paginator:
            return paginator.get_paginated_response(serializer.data)
        return Response(serializer.data)