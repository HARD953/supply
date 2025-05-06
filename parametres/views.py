from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from .models import (
    Commune, Quartier, Zone, UserType, Category, Certification,
    ShopType, TypeCommerce, TailleShop, FrequenceApprovisionnement,
    OrderStatus, Taille, Couleur, Module
)
from .serializers import (
    CommuneSerializer, QuartierSerializer, ZoneSerializer, UserTypeSerializer,
    CategorySerializer, CertificationSerializer, ShopTypeSerializer,
    TypeCommerceSerializer, TailleShopSerializer, FrequenceApprovisionnementSerializer,
    OrderStatusSerializer, TailleSerializer, CouleurSerializer, ModuleSerializer
)
from rest_framework.renderers import JSONRenderer

class CustomShopPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'
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

class ReadOnlyOrAuthenticated(IsAuthenticated):
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return super().has_permission(request, view)

class BaseViewSet(viewsets.ModelViewSet):
    pagination_class = CustomShopPagination

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        if request.query_params.get('paginate') == 'true':
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(queryset, request)
            serializer = self.get_serializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        return Response(serializer.data)

class CommuneViewSet(BaseViewSet):
    queryset = Commune.objects.all().order_by('name')
    serializer_class = CommuneSerializer
    permission_classes = [ReadOnlyOrAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'code']
    search_fields = ['name', 'code']
    renderer_classes = [JSONRenderer]  # Forcer JSON

class QuartierViewSet(BaseViewSet):
    queryset = Quartier.objects.all().order_by('name')
    serializer_class = QuartierSerializer
    permission_classes = [ReadOnlyOrAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'commune']
    search_fields = ['name']
    renderer_classes = [JSONRenderer]  # Forcer JSON

class ZoneViewSet(BaseViewSet):
    queryset = Zone.objects.all().order_by('name')
    serializer_class = ZoneSerializer
    permission_classes = [ReadOnlyOrAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'commune']
    search_fields = ['name']
    renderer_classes = [JSONRenderer]  # Forcer JSON

class UserTypeViewSet(BaseViewSet):
    queryset = UserType.objects.all().order_by('name')
    serializer_class = UserTypeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name']
    search_fields = ['name', 'description']
    renderer_classes = [JSONRenderer]  # Forcer JSON

class CategoryViewSet(BaseViewSet):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [ReadOnlyOrAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'app']
    search_fields = ['name', 'description']
    renderer_classes = [JSONRenderer]  # Forcer JSON

class CertificationViewSet(BaseViewSet):
    queryset = Certification.objects.all().order_by('name')
    serializer_class = CertificationSerializer
    permission_classes = [ReadOnlyOrAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name']
    search_fields = ['name', 'description']
    renderer_classes = [JSONRenderer]  # Forcer JSON

class ShopTypeViewSet(BaseViewSet):
    queryset = ShopType.objects.all().order_by('name')
    serializer_class = ShopTypeSerializer
    permission_classes = [ReadOnlyOrAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'code']
    search_fields = ['name', 'code']
    renderer_classes = [JSONRenderer]  # Forcer JSON

class TypeCommerceViewSet(BaseViewSet):
    queryset = TypeCommerce.objects.all().order_by('name')
    serializer_class = TypeCommerceSerializer
    permission_classes = [ReadOnlyOrAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name']
    search_fields = ['name', 'description']
    renderer_classes = [JSONRenderer]  # Forcer JSON

class TailleShopViewSet(BaseViewSet):
    queryset = TailleShop.objects.all().order_by('name')
    serializer_class = TailleShopSerializer
    permission_classes = [ReadOnlyOrAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name']
    search_fields = ['name']
    renderer_classes = [JSONRenderer]  # Forcer JSON

class FrequenceApprovisionnementViewSet(BaseViewSet):
    queryset = FrequenceApprovisionnement.objects.all().order_by('name')
    serializer_class = FrequenceApprovisionnementSerializer
    permission_classes = [ReadOnlyOrAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'days']
    search_fields = ['name']
    renderer_classes = [JSONRenderer]  # Forcer JSON

class OrderStatusViewSet(BaseViewSet):
    queryset = OrderStatus.objects.all().order_by('name')
    serializer_class = OrderStatusSerializer
    permission_classes = [ReadOnlyOrAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'code']
    search_fields = ['name', 'code', 'description']
    renderer_classes = [JSONRenderer]  # Forcer JSON

class TailleViewSet(BaseViewSet):
    queryset = Taille.objects.all().order_by('name')
    serializer_class = TailleSerializer
    permission_classes = [ReadOnlyOrAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name']
    search_fields = ['name']
    renderer_classes = [JSONRenderer]  # Forcer JSON

class CouleurViewSet(BaseViewSet):
    queryset = Couleur.objects.all().order_by('name')
    serializer_class = CouleurSerializer
    permission_classes = [ReadOnlyOrAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'hex_code']
    search_fields = ['name', 'hex_code']
    renderer_classes = [JSONRenderer]  # Forcer JSON

class ModuleViewSet(BaseViewSet):
    queryset = Module.objects.all().order_by('name')
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'link']
    search_fields = ['name', 'description']
    renderer_classes = [JSONRenderer]  # Forcer JSON