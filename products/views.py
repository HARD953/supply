from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Category, Product, ProductFormat, Order, OrderItem
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductFormatSerializer,
    OrderSerializer,
    OrderItemSerializer
)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

# class ProductViewSet(viewsets.ModelViewSet):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]  # Accès réservé aux utilisateurs authentifiés

    # Vue par défaut : tous les produits
    def get_queryset(self):
        return Product.objects.all()

    # Vue pour les produits des Fabricants
    @action(detail=False, methods=['get'], url_path='fabricant')
    def fabricant_products(self, request):
        queryset = Product.objects.filter(supplier__user_type='Fabricant')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # Vue pour les produits des Grossistes
    @action(detail=False, methods=['get'], url_path='grossiste')
    def grossiste_products(self, request):
        queryset = Product.objects.filter(supplier__user_type='Grossiste')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # Vue pour les produits des Semi-Grossistes
    @action(detail=False, methods=['get'], url_path='semi-grossiste')
    def semi_grossiste_products(self, request):
        queryset = Product.objects.filter(supplier__user_type='Semi-Grossiste')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # Vue pour les produits des Détaillants
    @action(detail=False, methods=['get'], url_path='detaillant')
    def detaillant_products(self, request):
        queryset = Product.objects.filter(supplier__user_type='Détaillant')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class ProductFormatViewSet(viewsets.ModelViewSet):
    queryset = ProductFormat.objects.all()
    serializer_class = ProductFormatSerializer

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]  # Requiert une authentification
    
    def get_queryset(self):
        # Retourne uniquement les commandes de l'utilisateur connecté
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Associe automatiquement l'utilisateur connecté lors de la création
        serializer.save(user=self.request.user)

class OrderItemViewSet(viewsets.ModelViewSet):
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Retourne uniquement les items des commandes de l'utilisateur connecté
        return OrderItem.objects.filter(order__user=self.request.user)