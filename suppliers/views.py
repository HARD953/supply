from rest_framework import viewsets,permissions
from .models import Supplier
from .serializers import *

class SupplierViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

class SupplierViewSetCommune(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializerCommune

class SupplierViewSetQuartier(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializerQuartier

class SupplierViewSetZone(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializerZone