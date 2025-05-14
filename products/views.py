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

class ProductStatsView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = CustomShopPagination
    renderer_classes = [JSONRenderer]

    def list(self, request):
        user = request.user
        days = int(request.query_params.get('days', 30))
        start_date = datetime.now() - timedelta(days=days)

        # Base querysets filtrés pour non-super_admin
        is_super_admin = user.user_type.name == 'Super_admin'
        print("is_super_admin")
        product_queryset = Product.objects.all()
        product_format_queryset = ProductFormat.objects.all()
        user_queryset = User.objects.all()

        if not is_super_admin:
            product_queryset = product_queryset.filter(supplier__company_name=user.company_name)
            product_format_queryset = product_format_queryset.filter(product__supplier__company_name=user.company_name)
            user_queryset = user_queryset.filter(company_name=user.company_name)

        # Statistiques générales
        total_products = product_queryset.count()
        total_formats = product_format_queryset.count()
        low_stock_formats = product_format_queryset.filter(stock__lte=F('min_stock')).count()
        total_suppliers = user_queryset.filter(products__isnull=False).distinct().count()

        # Statistiques par catégorie
        category_stats = product_queryset.values('category__name').annotate(
            total_products=Count('id'),
            total_formats=Count('formats'),
            total_stock=Sum('formats__stock')
        ).order_by('-total_products')

        # Statistiques par fournisseur
        supplier_stats = user_queryset.filter(products__isnull=False).values(
            'username', 'email', 'user_type__name', 'commune__name', 'quartier__name', 'zone__name', 'typecommerce__name'
        ).annotate(
            total_products=Count('products'),
            total_formats=Count('products__formats'),
            total_stock=Sum('products__formats__stock'),
            avg_products=Avg('products__id')
        ).order_by('-total_products')

        # Répartition des fournisseurs par type de commerce
        supplier_by_commerce = user_queryset.filter(products__isnull=False).values(
            'typecommerce__name'
        ).annotate(
            total=Count('id'),
            total_products=Count('products')
        ).order_by('-total')

        # Répartition des fournisseurs par commune
        supplier_by_commune = user_queryset.filter(products__isnull=False).values(
            'commune__name'
        ).annotate(
            total=Count('id'),
            total_products=Count('products')
        ).order_by('-total')[:10]

        # Répartition des fournisseurs par type d'utilisateur
        supplier_by_user_type = user_queryset.filter(products__isnull=False).values(
            'user_type__name'
        ).annotate(
            total=Count('id'),
            total_products=Count('products')
        ).order_by('-total')

        # Taux de produits en rupture
        stock_out_rate = (low_stock_formats / total_formats * 100) if total_formats > 0 else 0

        response_data = {
            'overview': {
                'total_products': total_products,
                'total_formats': total_formats,
                'low_stock_formats': low_stock_formats,
                'total_suppliers': total_suppliers,
                'stock_out_rate': round(stock_out_rate, 2),
                'timeframe_days': days
            },
            'by_category': list(category_stats),
            'by_supplier': list(supplier_stats),
            'suppliers_by_commerce': list(supplier_by_commerce),
            'suppliers_by_commune': list(supplier_by_commune),
            'suppliers_by_user_type': list(supplier_by_user_type)
        }

        paginable_sections = ['by_category', 'by_supplier', 'suppliers_by_commerce', 'suppliers_by_commune', 'suppliers_by_user_type']
        if request.query_params.get('paginate') == 'true':
            paginator = self.pagination_class()
            for section in paginable_sections:
                response_data[section] = paginator.paginate_queryset(response_data[section], request)
            return paginator.get_paginated_response(response_data)

        serializer = ProductStatsSerializer(response_data)
        return Response(serializer.data)

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from datetime import datetime, timedelta
from django.db.models import Sum, Count, Q, F
from .serializers import ProductStatsSerializerShop
from .models import Order, OrderItem, Product, ProductFormat

class ShopStatsView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = CustomShopPagination
    renderer_classes = [JSONRenderer]

    def list(self, request):
        user = request.user
        days = int(request.query_params.get('days', 30))
        start_date = datetime.now() - timedelta(days=days)

        # Base querysets filtrés pour non-super_admin
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

        # Statistiques générales
        total_orders = order_queryset.count()
        recent_orders = order_queryset.filter(created_at__gte=start_date).count()
        total_items = order_item_queryset.aggregate(total=Sum('quantity'))['total'] or 0
        total_amount = order_item_queryset.aggregate(
            total=Sum(F('quantity') * F('price_at_order'))
        )['total'] or 0
        total_order_users = user_queryset.filter(orders__isnull=False).distinct().count()
        total_suppliers = user_queryset.filter(products__isnull=False).distinct().count()

        # Statistiques des commandes par statut
        order_status_stats = order_queryset.values('status__name').annotate(
            total=Count('id'),
            recent=Count('id', filter=Q(created_at__gte=start_date)),
            total_items=Sum('items__quantity'),
            total_amount=Sum(F('items__quantity') * F('items__price_at_order'))
        ).order_by('status__name')

        # Statistiques par utilisateur des commandes
        order_user_stats = user_queryset.filter(orders__isnull=False).values(
            'username', 'email', 'user_type__name'
        ).annotate(
            total_orders=Count('orders'),
            recent_orders=Count('orders', filter=Q(orders__created_at__gte=start_date)),
            total_items=Sum('orders__items__quantity'),
            total_products=Count('orders__items__product_format__product', distinct=True),
            total_amount=Sum(F('orders__items__quantity') * F('orders__items__price_at_order'))
        ).order_by('-total_orders')[:5]

        # Répartition des utilisateurs des commandes par type d'utilisateur
        order_user_by_user_type = user_queryset.filter(orders__isnull=False).values(
            'user_type__name'
        ).annotate(
            total=Count('id'),
            total_orders=Count('orders'),
            total_items=Sum('orders__items__quantity'),
            total_products=Count('orders__items__product_format__product', distinct=True),
            total_amount=Sum(F('orders__items__quantity') * F('orders__items__price_at_order'))
        ).order_by('-total')

        # Statistiques par fournisseur
        supplier_stats = user_queryset.filter(products__isnull=False).values(
            'username', 'email', 'user_type__name'
        ).annotate(
            total_sales=Sum('products__formats__order_items__quantity'),
            total_orders=Count('products__formats__order_items__order', distinct=True),
            total_amount=Sum(F('products__formats__order_items__quantity') * F('products__formats__order_items__price_at_order'))
        ).order_by('-total_orders')

        # Top produits
        top_products = product_queryset.annotate(
            total_sold=Sum('formats__order_items__quantity')
        ).filter(total_sold__gt=0).values(
            'name', 'category__name', 'total_sold'
        ).order_by('-total_sold')[:5]

        # Orders by product
        orders_by_product = order_item_queryset.values(
            'product_format__product__name', 'product_format__product__category__name'
        ).annotate(
            total_orders=Count('order', distinct=True),
            total_items=Sum('quantity'),
            total_amount=Sum(F('quantity') * F('price_at_order'))
        ).order_by('-total_orders')

        # Orders by product category
        orders_by_category = order_item_queryset.values(
            'product_format__product__category__name'
        ).annotate(
            total_orders=Count('order', distinct=True),
            total_items=Sum('quantity'),
            total_amount=Sum(F('quantity') * F('price_at_order'))
        ).order_by('-total_orders')

        # Orders by commune
        orders_by_commune = order_queryset.values(
            'user__commune__name'
        ).annotate(
            total_orders=Count('id'),
            total_items=Sum('items__quantity'),
            total_amount=Sum(F('items__quantity') * F('items__price_at_order'))
        ).order_by('-total_orders')[:10]

        response_data = {
            'overview': {
                'total_orders': total_orders,
                'recent_orders': recent_orders,
                'total_items': total_items,
                'total_amount': float(total_amount) if total_amount else 0.0,
                'total_order_users': total_order_users,
                'total_suppliers': total_suppliers,
                'timeframe_days': days
            },
            'by_order_status': list(order_status_stats),
            'by_order_user': list(order_user_stats),
            'order_users_by_user_type': list(order_user_by_user_type),
            'by_supplier': list(supplier_stats),
            'top_products': list(top_products),
            'orders_by_product': list(orders_by_product),
            'orders_by_category': list(orders_by_category),
            'orders_by_commune': list(orders_by_commune)
        }

        paginable_sections = ['by_order_status', 'by_order_user', 'order_users_by_user_type', 'by_supplier', 'orders_by_product', 'orders_by_category', 'orders_by_commune']
        if request.query_params.get('paginate') == 'true':
            paginator = self.pagination_class()
            for section in paginable_sections:
                response_data[section] = paginator.paginate_queryset(response_data[section], request)
            return paginator.get_paginated_response(response_data)

        serializer = ProductStatsSerializerShop(response_data)
        return Response(serializer.data)