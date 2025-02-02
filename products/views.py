from rest_framework import viewsets
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
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer