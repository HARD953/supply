from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Category, Product, ProductFormat, Order, OrderItem
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductFormatSerializer,
    OrderSerializer,
    OrderItemSerializer
)
class CustomShopPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'  # Changement clé ici
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
class CategoryViewSetP(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    pagination_class = CustomShopPagination

    def get_queryset(self):
        queryset = Category.objects.all()
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)  # Adaptez selon vos champs
        return queryset

# class ProductViewSet(viewsets.ModelViewSet):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer

class ProductViewSetP(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]  # Accès réservé aux utilisateurs authentifiés
    pagination_class = CustomShopPagination

    def get_queryset(self):
        queryset = Product.objects.all()
        search_query = self.request.query_params.get('search', None)
        if search_query:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(name__icontains=search_query) | 
                Q(description__icontains=search_query)  # Adaptez selon vos champs
            )
        return queryset

    # Vue pour les produits des Fabricants
    @action(detail=False, methods=['get'], url_path='fabricant')
    def fabricant_products(self, request):
        queryset = Product.objects.filter(supplier__user_type='Fabricant')
        search_query = request.query_params.get('search', None)
        if search_query:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(name__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # Vue pour les produits des Grossistes
    @action(detail=False, methods=['get'], url_path='grossiste')
    def grossiste_products(self, request):
        queryset = Product.objects.filter(supplier__user_type='Grossiste')
        search_query = request.query_params.get('search', None)
        if search_query:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(name__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # Vue pour les produits des Semi-Grossistes
    @action(detail=False, methods=['get'], url_path='semi-grossiste')
    def semi_grossiste_products(self, request):
        queryset = Product.objects.filter(supplier__user_type='Semi-Grossiste')
        search_query = request.query_params.get('search', None)
        if search_query:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(name__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # Vue pour les produits des Détaillants
    @action(detail=False, methods=['get'], url_path='detaillant')
    def detaillant_products(self, request):
        queryset = Product.objects.filter(supplier__user_type='Détaillant')
        search_query = request.query_params.get('search', None)
        if search_query:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(name__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class ProductFormatViewSetP(viewsets.ModelViewSet):
    serializer_class = ProductFormatSerializer
    pagination_class = CustomShopPagination

    def get_queryset(self):
        queryset = ProductFormat.objects.all()
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(format__icontains=search_query)  # Adaptez selon vos champs
        return queryset

class OrderViewSetP(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]  # Requiert une authentification
    pagination_class = CustomShopPagination

    def get_queryset(self):
        queryset = Order.objects.filter(user=self.request.user)
        search_query = self.request.query_params.get('search', None)
        if search_query:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(id__icontains=search_query) |  # Recherche par ID de commande
                Q(status__icontains=search_query)  # Ou autre champ pertinent
            )
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class OrderItemViewSetP(viewsets.ModelViewSet):
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomShopPagination

    def get_queryset(self):
        queryset = OrderItem.objects.filter(order__user=self.request.user)
        search_query = self.request.query_params.get('search', None)
        if search_query:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(product__name__icontains=search_query) |  # Recherche par nom de produit
                Q(order__id__icontains=search_query)  # Ou ID de commande
            )
        return queryset