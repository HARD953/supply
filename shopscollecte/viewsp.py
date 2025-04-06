from rest_framework import viewsets
from .models import Category, Certification, Product
from .serializers import CategorySerializer, CertificationSerializer, ProductSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

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
    pagination_class = CustomShopPagination  # Associe la pagination au ViewSet

    def get_queryset(self):
        queryset = Category.objects.all()
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)  # Adaptez selon vos champs
        return queryset

class CertificationViewSetP(viewsets.ModelViewSet):
    serializer_class = CertificationSerializer
    pagination_class = CustomShopPagination  # Associe la pagination au ViewSet

    def get_queryset(self):
        queryset = Certification.objects.all()
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)  # Adaptez selon vos champs
        return queryset

class ProductViewSetP(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]  # Restreint l'accès aux utilisateurs authentifiés
    pagination_class = CustomShopPagination  # Associe la pagination au ViewSet

    def get_queryset(self):
        # Si l'utilisateur est authentifié, filtre par owner
        if self.request.user.is_authenticated:
            queryset = Product.objects.filter(owner=self.request.user)
            search_query = self.request.query_params.get('search', None)
            if search_query:
                from django.db.models import Q
                queryset = queryset.filter(
                    Q(name__icontains=search_query) | 
                    Q(description__icontains=search_query)  # Adaptez selon vos champs
                )
            return queryset
        # Sinon, retourne un queryset vide ou lève une erreur selon vos besoins
        return Product.objects.none()

    def perform_create(self, serializer):
        # Associe l'utilisateur connecté comme owner lors de la création
        serializer.save(owner=self.request.user)