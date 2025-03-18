from rest_framework import viewsets
from .models import Category, Certification, Product
from .serializers import CategorySerializer, CertificationSerializer, ProductSerializer
from rest_framework.permissions import IsAuthenticated

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CertificationViewSet(viewsets.ModelViewSet):
    queryset = Certification.objects.all()
    serializer_class = CertificationSerializer

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]  # Restreint l'accès aux utilisateurs authentifiés
    
    def get_queryset(self):
        # Si l'utilisateur est authentifié, filtre par owner
        if self.request.user.is_authenticated:
            return Product.objects.filter(owner=self.request.user)
        # Sinon, retourne un queryset vide ou lève une erreur selon vos besoins
        return Product.objects.none()
    def perform_create(self, serializer):
        # Associe l'utilisateur connecté comme owner lors de la création
        serializer.save(owner=self.request.user)