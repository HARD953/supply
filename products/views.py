from django.db.models import Count, Sum, Q, F, Avg
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.renderers import JSONRenderer
from datetime import datetime, timedelta
from .models import Product, ProductFormat, Order, OrderItem
from shops.models import Shop
from accounts.models import User
from .serializers import ProductSerializer, ProductFormatSerializer, OrderSerializer, OrderItemSerializer, ProductStatsSerializer, ProductStatsSerializerShop

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

class ProductViewSet(BaseViewSet):
    queryset = Product.objects.all().select_related('category', 'supplier').prefetch_related('formats').order_by('name')
    serializer_class = ProductSerializer
    permission_classes = [ReadOnlyOrAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'supplier', 'name']
    search_fields = ['name', 'category__name']

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.user_type.name == 'Super_admin':
                print(user.user_type.name)
                return super().get_queryset()
            return Product.objects.filter(
                supplier__company_name=user.company_name
            ).select_related('category', 'supplier').prefetch_related('formats')
        return Product.objects.none()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsAdminUser]
        return super().get_permissions()

class ProductFormatViewSet(BaseViewSet):
    queryset = ProductFormat.objects.all().select_related('product', 'taille', 'couleur').order_by('product__name')
    serializer_class = ProductFormatSerializer
    permission_classes = [ReadOnlyOrAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product', 'taille', 'couleur']
    search_fields = ['product__name', 'taille__name', 'couleur__name']

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.user_type.name == 'Super_admin':
                return super().get_queryset()
            return ProductFormat.objects.filter(
                product__supplier__company_name=user.company_name
            ).select_related('product', 'taille', 'couleur')
        return ProductFormat.objects.none()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsAdminUser]
        return super().get_permissions()

class OrderViewSet(BaseViewSet):
    queryset = Order.objects.all().select_related('user', 'status').prefetch_related('items').order_by('-created_at')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'status', 'created_at']
    search_fields = ['user__username']

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.user_type.name == 'Super_admin':
                return super().get_queryset()
            return Order.objects.filter(
                user__company_name=user.company_name
            ).select_related('user', 'status').prefetch_related('items')
        return Order.objects.none()

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsAdminUser]
        return super().get_permissions()

class OrderItemViewSet(BaseViewSet):
    queryset = OrderItem.objects.all().select_related('order', 'product_format').order_by('order__created_at')
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['order', 'product_format']
    search_fields = ['product_format__product__name']

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.user_type.name == 'Super_admin':
                return super().get_queryset()
            return OrderItem.objects.filter(
                product_format__product__supplier__company_name=user.company_name
            ).select_related('order', 'product_format')
        return OrderItem.objects.none()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsAdminUser]
        return super().get_permissions()

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.renderers import JSONRenderer
from django.db.models import Count, Sum, Avg, F
from datetime import datetime, timedelta
from .models import Product, ProductFormat, User
from .serializers import ProductStatsSerializer, OverviewSerializer, CategoryStatsSerializer, SupplierStatsSerializer, CommerceStatsSerializer, CommuneStatsSerializer, UserTypeStatsSerializer


class ProductStatsView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = CustomShopPagination
    renderer_classes = [JSONRenderer]

    def get_base_querysets(self, request):
        """Retourne les querysets filtrés selon le type d'utilisateur."""
        user = request.user
        is_super_admin = user.user_type.name == 'Super_admin'

        product_queryset = Product.objects.all()
        product_format_queryset = ProductFormat.objects.all()
        user_queryset = User.objects.all()

        if not is_super_admin:
            product_queryset = product_queryset.filter(supplier__company_name=user.company_name)
            product_format_queryset = product_format_queryset.filter(product__supplier__company_name=user.company_name)
            user_queryset = user_queryset.filter(company_name=user.company_name)

        return product_queryset, product_format_queryset, user_queryset

    def get_days(self, request):
        """Retourne le nombre de jours à partir des query params."""
        return int(request.query_params.get('days', 30))

    def paginate_if_needed(self, data, request):
        """Applique la pagination si demandée."""
        if request.query_params.get('paginate') == 'true':
            paginator = self.pagination_class()
            return paginator.paginate_queryset(data, request), paginator
        return data, None

    @action(detail=False, methods=['get'], url_path='overview')
    def overview(self, request):
        """Statistiques générales."""
        product_queryset, product_format_queryset, user_queryset = self.get_base_querysets(request)
        days = self.get_days(request)

        total_products = product_queryset.count()
        total_formats = product_format_queryset.count()
        low_stock_formats = product_format_queryset.filter(stock__lte=F('min_stock')).count()
        total_suppliers = user_queryset.filter(products__isnull=False).distinct().count()
        stock_out_rate = (low_stock_formats / total_formats * 100) if total_formats > 0 else 0

        response_data = {
            'total_products': total_products,
            'total_formats': total_formats,
            'low_stock_formats': low_stock_formats,
            'total_suppliers': total_suppliers,
            'stock_out_rate': round(stock_out_rate, 2),
            'timeframe_days': days
        }

        serializer = OverviewSerializer(response_data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-category')
    def by_category(self, request):
        """Statistiques par catégorie."""
        product_queryset, _, _ = self.get_base_querysets(request)
        
        category_stats = product_queryset.values('category__name').annotate(
            total_products=Count('id'),
            total_formats=Count('formats'),
            total_stock=Sum('formats__stock')
        ).order_by('-total_products')

        category_stats, paginator = self.paginate_if_needed(list(category_stats), request)
        serializer = CategoryStatsSerializer(category_stats, many=True)

        if paginator:
            return paginator.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-supplier')
    def by_supplier(self, request):
        """Statistiques par fournisseur."""
        _, _, user_queryset = self.get_base_querysets(request)

        supplier_stats = user_queryset.filter(products__isnull=False).values(
            'username', 'email', 'user_type__name', 'commune__name', 'quartier__name', 'zone__name', 'typecommerce__name'
        ).annotate(
            total_products=Count('products'),
            total_formats=Count('products__formats'),
            total_stock=Sum('products__formats__stock'),
            avg_products=Avg('products__id')
        ).order_by('-total_products')

        supplier_stats, paginator = self.paginate_if_needed(list(supplier_stats), request)
        serializer = SupplierStatsSerializer(supplier_stats, many=True)

        if paginator:
            return paginator.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-commerce')
    def by_commerce(self, request):
        """Fournisseurs par type de commerce."""
        _, _, user_queryset = self.get_base_querysets(request)

        supplier_by_commerce = user_queryset.filter(products__isnull=False).values(
            'typecommerce__name'
        ).annotate(
            total=Count('id'),
            total_products=Count('products')
        ).order_by('-total')

        supplier_by_commerce, paginator = self.paginate_if_needed(list(supplier_by_commerce), request)
        serializer = CommerceStatsSerializer(supplier_by_commerce, many=True)

        if paginator:
            return paginator.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-commune')
    def by_commune(self, request):
        """Fournisseurs par commune."""
        _, _, user_queryset = self.get_base_querysets(request)

        supplier_by_commune = user_queryset.filter(products__isnull=False).values(
            'commune__name'
        ).annotate(
            total=Count('id'),
            total_products=Count('products')
        ).order_by('-total')[:10]

        supplier_by_commune, paginator = self.paginate_if_needed(list(supplier_by_commune), request)
        serializer = CommuneStatsSerializer(supplier_by_commune, many=True)

        if paginator:
            return paginator.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-user-type')
    def by_user_type(self, request):
        """Fournisseurs par type d'utilisateur."""
        _, _, user_queryset = self.get_base_querysets(request)

        supplier_by_user_type = user_queryset.filter(products__isnull=False).values(
            'user_type__name'
        ).annotate(
            total=Count('id'),
            total_products=Count('products')
        ).order_by('-total')

        supplier_by_user_type, paginator = self.paginate_if_needed(list(supplier_by_user_type), request)
        serializer = UserTypeStatsSerializer(supplier_by_user_type, many=True)

        if paginator:
            return paginator.get_paginated_response(serializer.data)
        return Response(serializer.data)
    
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from datetime import datetime, timedelta
from django.db.models import Sum, Count, Q, F
from .serializers import (
    OverviewSerializer, OrderStatusStatsSerializer, OrderUserStatsSerializer,
    UserTypeStatsSerializer, SupplierStatsSerializer, TopProductsSerializer,
    OrdersByProductSerializer, OrdersByCategorySerializer, OrdersByCommuneSerializer
)
from .models import Order, OrderItem, Product, User


class ShopStatsView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = CustomShopPagination
    renderer_classes = [JSONRenderer]

    def get_base_querysets(self, request):
        """Retourne les querysets filtrés selon le type d'utilisateur."""
        user = request.user
        is_super_admin = user.user_type.name == 'Super_admin'

        order_queryset = Order.objects.all()
        order_item_queryset = OrderItem.objects.all()
        product_queryset = Product.objects.all()
        user_queryset = User.objects.all()

        if not is_super_admin:
            order_queryset = order_queryset.filter(user__company_name=user.company_name)
            order_item_queryset = order_item_queryset.filter(
                product_format__product__supplier__company_name=user.company_name
            )
            product_queryset = product_queryset.filter(supplier__company_name=user.company_name)
            user_queryset = user_queryset.filter(company_name=user.company_name)

        return order_queryset, order_item_queryset, product_queryset, user_queryset

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
        """Statistiques générales des commandes."""
        order_queryset, order_item_queryset, _, user_queryset = self.get_base_querysets(request)
        days, start_date = self.get_days_and_start_date(request)

        total_orders = order_queryset.count()
        recent_orders = order_queryset.filter(created_at__gte=start_date).count()
        total_items = order_item_queryset.aggregate(total=Sum('quantity'))['total'] or 0
        total_amount = order_item_queryset.aggregate(
            total=Sum(F('quantity') * F('price_at_order'))
        )['total'] or 0
        total_order_users = user_queryset.filter(orders__isnull=False).distinct().count()
        total_suppliers = user_queryset.filter(products__isnull=False).distinct().count()

        response_data = {
            'total_orders': total_orders,
            'recent_orders': recent_orders,
            'total_items': total_items,
            'total_amount': float(total_amount) if total_amount else 0.0,
            'total_order_users': total_order_users,
            'total_suppliers': total_suppliers,
            'timeframe_days': days
        }

        serializer = OverviewSerializer(response_data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-order-status')
    def by_order_status(self, request):
        """Statistiques par statut de commande."""
        order_queryset, _, _, _ = self.get_base_querysets(request)
        days, start_date = self.get_days_and_start_date(request)

        order_status_stats = order_queryset.values('status__name').annotate(
            total=Count('id'),
            recent=Count('id', filter=Q(created_at__gte=start_date)),
            total_items=Sum('items__quantity'),
            total_amount=Sum(F('items__quantity') * F('items__price_at_order'))
        ).order_by('status__name')

        order_status_stats, paginator = self.paginate_if_needed(list(order_status_stats), request)
        serializer = OrderStatusStatsSerializer(order_status_stats, many=True)

        if paginator:
            return paginator.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-order-user')
    def by_order_user(self, request):
        """Statistiques par utilisateur des commandes."""
        _, _, _, user_queryset = self.get_base_querysets(request)
        days, start_date = self.get_days_and_start_date(request)

        order_user_stats = user_queryset.filter(orders__isnull=False).values(
            'username', 'email', 'user_type__name'
        ).annotate(
            total_orders=Count('orders'),
            recent_orders=Count('orders', filter=Q(orders__created_at__gte=start_date)),
            total_items=Sum('orders__items__quantity'),
            total_products=Count('orders__items__product_format__product', distinct=True),
            total_amount=Sum(F('orders__items__quantity') * F('orders__items__price_at_order'))
        ).order_by('-total_orders')[:5]

        order_user_stats, paginator = self.paginate_if_needed(list(order_user_stats), request)
        serializer = OrderUserStatsSerializer(order_user_stats, many=True)

        if paginator:
            return paginator.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-user-type')
    def order_users_by_user_type(self, request):
        """Utilisateurs des commandes par type d'utilisateur."""
        _, _, _, user_queryset = self.get_base_querysets(request)

        order_user_by_user_type = user_queryset.filter(orders__isnull=False).values(
            'user_type__name'
        ).annotate(
            total=Count('id'),
            total_orders=Count('orders'),
            total_items=Sum('orders__items__quantity'),
            total_products=Count('orders__items__product_format__product', distinct=True),
            total_amount=Sum(F('orders__items__quantity') * F('orders__items__price_at_order'))
        ).order_by('-total')

        order_user_by_user_type, paginator = self.paginate_if_needed(list(order_user_by_user_type), request)
        serializer = UserTypeStatsSerializer(order_user_by_user_type, many=True)

        if paginator:
            return paginator.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-supplier')
    def by_supplier(self, request):
        """Statistiques par fournisseur."""
        _, _, _, user_queryset = self.get_base_querysets(request)

        supplier_stats = user_queryset.filter(products__isnull=False).values(
            'username', 'email', 'user_type__name'
        ).annotate(
            total_sales=Sum('products__formats__order_items__quantity'),
            total_orders=Count('products__formats__order_items__order', distinct=True),
            total_amount=Sum(F('products__formats__order_items__quantity') * F('products__formats__order_items__price_at_order'))
        ).order_by('-total_orders')

        supplier_stats, paginator = self.paginate_if_needed(list(supplier_stats), request)
        serializer = SupplierStatsSerializer(supplier_stats, many=True)

        if paginator:
            return paginator.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='top-products')
    def top_products(self, request):
        """Top 5 produits les plus vendus."""
        _, _, product_queryset, _ = self.get_base_querysets(request)

        top_products = product_queryset.annotate(
            total_sold=Sum('formats__order_items__quantity')
        ).filter(total_sold__gt=0).values(
            'name', 'category__name', 'total_sold'
        ).order_by('-total_sold')[:5]

        top_products, paginator = self.paginate_if_needed(list(top_products), request)
        serializer = TopProductsSerializer(top_products, many=True)

        if paginator:
            return paginator.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-product')
    def orders_by_product(self, request):
        """Commandes par produit."""
        _, order_item_queryset, _, _ = self.get_base_querysets(request)

        orders_by_product = order_item_queryset.values(
            'product_format__product__name', 'product_format__product__category__name'
        ).annotate(
            total_orders=Count('order', distinct=True),
            total_items=Sum('quantity'),
            total_amount=Sum(F('quantity') * F('price_at_order'))
        ).order_by('-total_orders')

        orders_by_product, paginator = self.paginate_if_needed(list(orders_by_product), request)
        serializer = OrdersByProductSerializer(orders_by_product, many=True)

        if paginator:
            return paginator.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-category')
    def orders_by_category(self, request):
        """Commandes par catégorie de produit."""
        _, order_item_queryset, _, _ = self.get_base_querysets(request)

        orders_by_category = order_item_queryset.values(
            'product_format__product__category__name'
        ).annotate(
            total_orders=Count('order', distinct=True),
            total_items=Sum('quantity'),
            total_amount=Sum(F('quantity') * F('price_at_order'))
        ).order_by('-total_orders')

        orders_by_category, paginator = self.paginate_if_needed(list(orders_by_category), request)
        serializer = OrdersByCategorySerializer(orders_by_category, many=True)

        if paginator:
            return paginator.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-commune')
    def orders_by_commune(self, request):
        """Commandes par commune."""
        order_queryset, _, _, _ = self.get_base_querysets(request)

        orders_by_commune = order_queryset.values(
            'user__commune__name'
        ).annotate(
            total_orders=Count('id'),
            total_items=Sum('items__quantity'),
            total_amount=Sum(F('items__quantity') * F('items__price_at_order'))
        ).order_by('-total_orders')[:10]

        orders_by_commune, paginator = self.paginate_if_needed(list(orders_by_commune), request)
        serializer = OrdersByCommuneSerializer(orders_by_commune, many=True)

        if paginator:
            return paginator.get_paginated_response(serializer.data)
        return Response(serializer.data)