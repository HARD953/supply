from rest_framework import serializers
from django.db.models import Count, Sum, Avg, F, Q
from django.utils import timezone
from accounts.models import User
from shops.models import Shop
from products.models import Product, ProductFormat, Order, OrderItem
from shopscollecte.models import ProductCollecte
from parametres.models import UserType, ShopType, TypeCommerce, TailleShop, Category, OrderStatus, Module
from accounts.models import ModulePermission
from datetime import timedelta

class UserStatsSerializer(serializers.Serializer):
    total_users = serializers.SerializerMethodField()
    users_by_type = serializers.SerializerMethodField()
    avg_shops_per_user = serializers.SerializerMethodField()
    active_users = serializers.SerializerMethodField()

    def get_total_users(self, obj):
        queryset = self.instance or User.objects.all()
        return queryset.count()

    def get_users_by_type(self, obj):
        queryset = self.instance or User.objects.all()
        return [
            {'user_type': item['user_type__name'] or 'Inconnu', 'count': item['count']}
            for item in (
                queryset.select_related('user_type')
                .values('user_type__name')
                .annotate(count=Count('id'))
                .order_by('-count')
            )
        ]

    def get_avg_shops_per_user(self, obj):
        queryset = self.instance or User.objects.all()
        avg = queryset.annotate(shop_count=Count('shops')).aggregate(avg_shops=Avg('shop_count'))['avg_shops']
        return round(float(avg), 2) if avg is not None else 0.0

    def get_active_users(self, obj):
        queryset = self.instance or User.objects.all()
        threshold = timezone.now() - timedelta(days=30)
        active_users = set()
        # Users with recently created shops
        try:
            active_users.update(
                User.objects.filter(
                    id__in=Shop.objects.filter(created_at__gte=threshold).values('owner_id')
                ).values_list('id', flat=True)
            )
        except FieldError:
            pass  # Skip if created_at is missing for Shop
        # Users with recently active products (using last_order)
        try:
            active_users.update(
                User.objects.filter(
                    id__in=Product.objects.filter(last_order__gte=threshold).values('supplier_id')
                ).values_list('id', flat=True)
            )
        except FieldError:
            pass  # Skip if last_order is missing or not a timestamp
        # Users with recent orders
        try:
            active_users.update(
                User.objects.filter(
                    id__in=Order.objects.filter(created_at__gte=threshold).values('user_id')
                ).values_list('id', flat=True)
            )
        except FieldError:
            pass  # Skip if created_at is missing for Order
        active_count = len(active_users)
        total_count = queryset.count()
        return {'active': active_count, 'inactive': total_count - active_count}

class ShopStatsSerializer(serializers.Serializer):
    total_shops = serializers.SerializerMethodField()
    shops_by_type = serializers.SerializerMethodField()
    shops_by_commerce = serializers.SerializerMethodField()
    shops_by_taille = serializers.SerializerMethodField()
    avg_products_per_shop = serializers.SerializerMethodField()
    avg_revenue_per_shop = serializers.SerializerMethodField()
    low_stock_shops = serializers.SerializerMethodField()

    def get_total_shops(self, obj):
        queryset = self.instance or Shop.objects.all()
        return queryset.count()

    def get_shops_by_type(self, obj):
        queryset = self.instance or Shop.objects.all()
        return [
            {'type': item['type__name'] or 'Inconnu', 'count': item['count']}
            for item in (
                queryset.select_related('type')
                .values('type__name')
                .annotate(count=Count('id'))
                .order_by('-count')
            )
        ]

    def get_shops_by_commerce(self, obj):
        queryset = self.instance or Shop.objects.all()
        return [
            {'typecommerce': item['typecommerce__name'] or 'Inconnu', 'count': item['count']}
            for item in (
                queryset.select_related('typecommerce')
                .values('typecommerce__name')
                .annotate(count=Count('id'))
                .order_by('-count')
            )
        ]

    def get_shops_by_taille(self, obj):
        queryset = self.instance or Shop.objects.all()
        return [
            {'taille': item['taille__name'] or 'Inconnu', 'count': item['count']}
            for item in (
                queryset.select_related('taille')
                .values('taille__name')
                .annotate(count=Count('id'))
                .order_by('-count')
            )
        ]

    def get_avg_products_per_shop(self, obj):
        queryset = self.instance or Shop.objects.all()
        avg = queryset.annotate(product_count=Count('products')).aggregate(avg_products=Avg('product_count'))['avg_products']
        return round(float(avg), 2) if avg is not None else 0.0

    def get_avg_revenue_per_shop(self, obj):
        queryset = self.instance or Shop.objects.all()
        avg = OrderItem.objects.filter(
            product_format__product__in=Product.objects.filter(supplier__shops__in=queryset)
        ).aggregate(
            avg_revenue=Avg(F('price_at_order') * F('quantity'))
        )['avg_revenue']
        return round(float(avg), 2) if avg is not None else 0.0

    def get_low_stock_shops(self, obj):
        queryset = self.instance or Shop.objects.all()
        low_stock = ProductCollecte.objects.filter(
            supplier__in=queryset, stock__lte=F('stock') * 0.2
        ).values('supplier__name').annotate(count=Count('id')).order_by('-count')[:5]
        return [
            {'shop': item['supplier__name'], 'low_stock_products': item['count']}
            for item in low_stock
        ]

class ProductStatsSerializer(serializers.Serializer):
    total_products = serializers.SerializerMethodField()
    products_by_category = serializers.SerializerMethodField()
    total_stock = serializers.SerializerMethodField()
    top_products_ordered = serializers.SerializerMethodField()
    stock_by_format = serializers.SerializerMethodField()
    avg_price_per_category = serializers.SerializerMethodField()
    stock_order_correlation = serializers.SerializerMethodField()
    most_profitable_products = serializers.SerializerMethodField()

    def get_total_products(self, obj):
        queryset = self.instance or Product.objects.all()
        return queryset.count()

    def get_products_by_category(self, obj):
        queryset = self.instance or Product.objects.all()
        return [
            {
                'category': item['category__name'] or 'Inconnu',
                'app': item['category__app'] or 'Inconnu',
                'count': item['count']
            }
            for item in (
                queryset.select_related('category')
                .values('category__name', 'category__app')
                .annotate(count=Count('id'))
                .order_by('-count')
            )
        ]

    def get_total_stock(self, obj):
        queryset = self.instance or Product.objects.all()
        format_queryset = ProductFormat.objects.filter(product__in=queryset)
        total = format_queryset.aggregate(total=Sum('stock'))['total']
        return total if total is not None else 0

    def get_top_products_ordered(self, obj):
        queryset = self.instance or Product.objects.all()
        return [
            {
                'product': item['product_format__product__name'] or 'Inconnu',
                'taille': item['product_format__taille__name'] or 'N/A',
                'couleur': item['product_format__couleur__name'] or 'N/A',
                'total_ordered': item['total_ordered']
            }
            for item in (
                OrderItem.objects.filter(product_format__product__in=queryset)
                .select_related('product_format__product', 'product_format__taille', 'product_format__couleur')
                .values('product_format__product__name', 'product_format__taille__name', 'product_format__couleur__name')
                .annotate(total_ordered=Sum('quantity'))
                .order_by('-total_ordered')[:5]
            )
        ]

    def get_stock_by_format(self, obj):
        queryset = self.instance or Product.objects.all()
        return [
            {
                'product': item['product__name'] or 'Inconnu',
                'taille': item['taille__name'] or 'N/A',
                'couleur': item['couleur__name'] or 'N/A',
                'total_stock': item['total_stock'],
                'min_stock': item['min_stock']
            }
            for item in (
                ProductFormat.objects.filter(product__in=queryset)
                .select_related('product', 'taille', 'couleur')
                .values('product__name', 'taille__name', 'couleur__name')
                .annotate(total_stock=Sum('stock'), min_stock=Sum('min_stock'))
                .order_by('-total_stock')
            )
        ]

    def get_avg_price_per_category(self, obj):
        queryset = self.instance or Product.objects.all()
        return [
            {
                'category': item['product__category__name'] or 'Inconnu',
                'avg_price': round(float(item['avg_price']), 2)
            }
            for item in (
                ProductFormat.objects.filter(product__in=queryset)
                .select_related('product__category')
                .values('product__category__name')
                .annotate(avg_price=Avg('price'))
                .order_by('-avg_price')
            )
        ]

    def get_stock_order_correlation(self, obj):
        queryset = self.instance or Product.objects.all()
        data = ProductFormat.objects.filter(product__in=queryset).values(
            'stock', 'product__id'
        ).annotate(total_ordered=Sum('order_items__quantity'))
        if not data:
            return 0.0
        import numpy as np
        stocks = [item['stock'] for item in data]
        orders = [item['total_ordered'] or 0 for item in data]
        correlation = np.corrcoef(stocks, orders)[0, 1]
        return round(float(correlation), 2) if not np.isnan(correlation) else 0.0

    def get_most_profitable_products(self, obj):
        queryset = self.instance or Product.objects.all()
        return [
            {
                'product': item['product_format__product__name'] or 'Inconnu',
                'total_revenue': round(float(item['total_revenue']), 2)
            }
            for item in (
                OrderItem.objects.filter(product_format__product__in=queryset)
                .values('product_format__product__name')
                .annotate(total_revenue=Sum(F('price_at_order') * F('quantity')))
                .order_by('-total_revenue')[:5]
            )
        ]

class ProductCollecteStatsSerializer(serializers.Serializer):
    total_products_collecte = serializers.SerializerMethodField()
    products_by_category = serializers.SerializerMethodField()
    total_stock = serializers.SerializerMethodField()
    avg_price_per_category = serializers.SerializerMethodField()
    stock_by_supplier = serializers.SerializerMethodField()
    reorder_alerts = serializers.SerializerMethodField()
    top_suppliers = serializers.SerializerMethodField()

    def get_total_products_collecte(self, obj):
        queryset = self.instance or ProductCollecte.objects.all()
        return queryset.count()

    def get_products_by_category(self, obj):
        queryset = self.instance or ProductCollecte.objects.all()
        return [
            {'category': item['category__name'] or 'Inconnu', 'count': item['count']}
            for item in (
                queryset.select_related('category')
                .values('category__name')
                .annotate(count=Count('id'))
                .order_by('-count')
            )
        ]

    def get_total_stock(self, obj):
        queryset = self.instance or ProductCollecte.objects.all()
        total = queryset.aggregate(total=Sum('stock'))['total']
        return total if total is not None else 0

    def get_avg_price_per_category(self, obj):
        queryset = self.instance or ProductCollecte.objects.all()
        return [
            {
                'category': item['category__name'] or 'Inconnu',
                'avg_price': round(float(item['avg_price']), 2)
            }
            for item in (
                queryset.select_related('category')
                .values('category__name')
                .annotate(avg_price=Avg('price'))
                .order_by('-avg_price')
            )
        ]

    def get_stock_by_supplier(self, obj):
        queryset = self.instance or ProductCollecte.objects.all()
        return [
            {
                'supplier': item['supplier__name'] or 'Inconnu',
                'total_stock': item['total_stock']
            }
            for item in (
                queryset.select_related('supplier')
                .values('supplier__name')
                .annotate(total_stock=Sum('stock'))
                .order_by('-total_stock')
            )
        ]

    def get_reorder_alerts(self, obj):
        queryset = self.instance or ProductCollecte.objects.all()
        alerts = queryset.filter(
            stock__lte=F('stock') * 0.2,
            reorder_frequency__gt=0
        ).values('name', 'supplier__name', 'stock', 'reorder_frequency')[:5]
        return [
            {
                'product': item['name'],
                'supplier': item['supplier__name'] or 'Inconnu',
                'stock': item['stock'],
                'reorder_frequency': item['reorder_frequency']
            }
            for item in alerts
        ]

    def get_top_suppliers(self, obj):
        queryset = self.instance or ProductCollecte.objects.all()
        return [
            {
                'supplier': item['supplier__name'] or 'Inconnu',
                'total_value': round(float(item['total_value']), 2)
            }
            for item in (
                queryset.values('supplier__name')
                .annotate(total_value=Sum(F('price') * F('stock')))
                .order_by('-total_value')[:5]
            )
        ]

class OrderStatsSerializer(serializers.Serializer):
    total_orders = serializers.SerializerMethodField()
    orders_by_status = serializers.SerializerMethodField()
    total_order_value = serializers.SerializerMethodField()
    orders_by_user = serializers.SerializerMethodField()
    avg_order_value = serializers.SerializerMethodField()
    conversion_rate = serializers.SerializerMethodField()
    abandoned_orders = serializers.SerializerMethodField()

    def get_total_orders(self, obj):
        queryset = self.instance or Order.objects.all()
        return queryset.count()

    def get_orders_by_status(self, obj):
        queryset = self.instance or Order.objects.all()
        return [
            {'status': item['status__name'] or 'Inconnu', 'count': item['count']}
            for item in (
                queryset.select_related('status')
                .values('status__name')
                .annotate(count=Count('id'))
                .order_by('-count')
            )
        ]

    def get_total_order_value(self, obj):
        queryset = self.instance or Order.objects.all()
        total = OrderItem.objects.filter(order__in=queryset).aggregate(
            total=Sum(F('price_at_order') * F('quantity'))
        )['total']
        return round(float(total), 2) if total is not None else 0.0

    def get_orders_by_user(self, obj):
        queryset = self.instance or Order.objects.all()
        return [
            {
                'user': item['user__username'] or 'Inconnu',
                'count': item['count'],
                'total_value': round(float(item['total_value']), 2) if item['total_value'] else 0.0
            }
            for item in (
                queryset.select_related('user')
                .values('user__username')
                .annotate(
                    count=Count('id'),
                    total_value=Sum(F('items__price_at_order') * F('items__quantity'))
                )
                .order_by('-count')
            )
        ]

    def get_avg_order_value(self, obj):
        queryset = self.instance or Order.objects.all()
        avg = OrderItem.objects.filter(order__in=queryset).aggregate(
            avg=Avg(F('price_at_order') * F('quantity'))
        )['avg']
        return round(float(avg), 2) if avg is not None else 0.0

    def get_conversion_rate(self, obj):
        queryset = self.instance or Order.objects.all()
        total_orders = queryset.count()
        completed_orders = queryset.filter(status__name='Terminé').count()
        return round((completed_orders / total_orders * 100) if total_orders else 0.0, 2)

    def get_abandoned_orders(self, obj):
        queryset = self.instance or Order.objects.all()
        abandoned = queryset.filter(status__name__in=['Annulé', 'En attente']).values('status__name').annotate(count=Count('id'))
        return [
            {'status': item['status__name'], 'count': item['count']}
            for item in abandoned
        ]

class ModuleStatsSerializer(serializers.Serializer):
    total_modules = serializers.SerializerMethodField()
    permissions_by_module = serializers.SerializerMethodField()
    users_by_permission = serializers.SerializerMethodField()
    permission_usage = serializers.SerializerMethodField()

    def get_total_modules(self, obj):
        return Module.objects.count()

    def get_permissions_by_module(self, obj):
        return [
            {
                'module': item['module__name'] or 'Inconnu',
                'create_count': item['create_count'],
                'read_count': item['read_count'],
                'update_count': item['update_count'],
                'delete_count': item['delete_count']
            }
            for item in (
                ModulePermission.objects.select_related('module')
                .values('module__name')
                .annotate(
                    create_count=Count('id', filter=Q(can_create=True)),
                    read_count=Count('id', filter=Q(can_read=True)),
                    update_count=Count('id', filter=Q(can_update=True)),
                    delete_count=Count('id', filter=Q(can_delete=True))
                )
                .order_by('-create_count')
            )
        ]

    def get_users_by_permission(self, obj):
        return [
            {
                'user': item['user__username'] or 'Inconnu',
                'modules_count': item['modules_count'],
                'create_count': item['create_count'],
                'read_count': item['read_count']
            }
            for item in (
                ModulePermission.objects.select_related('user', 'module')
                .values('user__username')
                .annotate(
                    modules_count=Count('module'),
                    create_count=Count('id', filter=Q(can_create=True)),
                    read_count=Count('id', filter=Q(can_read=True))
                )
                .order_by('-modules_count')
            )
        ]

    def get_permission_usage(self, obj):
        total_users = User.objects.count()
        if not total_users:
            return {'create': 0.0, 'read': 0.0, 'update': 0.0, 'delete': 0.0}
        perms = ModulePermission.objects.aggregate(
            create=Count('id', filter=Q(can_create=True)),
            read=Count('id', filter=Q(can_read=True)),
            update=Count('id', filter=Q(can_update=True)),
            delete=Count('id', filter=Q(can_delete=True))
        )
        return {
            'create': round(perms['create'] / total_users * 100, 2),
            'read': round(perms['read'] / total_users * 100, 2),
            'update': round(perms['update'] / total_users * 100, 2),
            'delete': round(perms['delete'] / total_users * 100, 2)
        }