from rest_framework import viewsets
from .models import Category, Certification, Product
from .serializers import CategorySerializer, CertificationSerializer, ProductSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomShopPagination(PageNumberPagination):
    page_size = 10  # Nombre d'éléments par page
    page_size_query_param = 'page_size'  # Permet au client de spécifier la taille de la page
    max_page_size = 100  # Limite maximale pour la taille de la page
    def get_paginated_response(self, data):
        return Response({
            'total': self.page.paginator.count,  # Remplace "count" par "total"
            'next': self.get_next_link(),        # Lien vers la page suivante
            'previous': self.get_previous_link(), # Lien vers la page précédente
            'data': data                         # Remplace "results" par "data"
        })

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = CustomShopPagination  # Associe la pagination au ViewSet

class CertificationViewSet(viewsets.ModelViewSet):
    queryset = Certification.objects.all()
    serializer_class = CertificationSerializer
    pagination_class = CustomShopPagination  # Associe la pagination au ViewSet

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]  # Restreint l'accès aux utilisateurs authentifiés
    pagination_class = CustomShopPagination  # Associe la pagination au ViewSet

    def get_queryset(self):
        # Si l'utilisateur est authentifié, filtre par owner
        if self.request.user.is_authenticated:
            return Product.objects.filter(owner=self.request.user)
        # Sinon, retourne un queryset vide ou lève une erreur selon vos besoins
        return Product.objects.none()
    def perform_create(self, serializer):
        # Associe l'utilisateur connecté comme owner lors de la création
        serializer.save(owner=self.request.user)