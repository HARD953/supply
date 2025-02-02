from rest_framework import viewsets
from .models import SupplierCollecte
from .serializers import SupplierSerializer

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = SupplierCollecte.objects.all()
    serializer_class = SupplierSerializer