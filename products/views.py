from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Category, Product, ProductFormat, Order, OrderItem
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

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

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