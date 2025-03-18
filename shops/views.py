from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from django.db.models.functions import TruncDate, TruncMonth, TruncYear
from .models import Shop
from rest_framework.permissions import IsAuthenticated
from .serializers import (
    ShopSerializer, 
    ShopSerializerSupplier,
    ShopStatsByTypeSerializer,
    ShopStatsByDateSerializer,
    ShopStatsByMonthSerializer,
    ShopStatsByYearSerializer,
    ShopStatsByBrandSerializer
)

class ShopViewSet(viewsets.ModelViewSet):
    serializer_class = ShopSerializer
    permission_classes = [IsAuthenticated]  # Restreint l'accès aux utilisateurs authentifiés
    
    def get_queryset(self):
        # Si l'utilisateur est authentifié, filtre par owner
        if self.request.user.is_authenticated:
            return Shop.objects.filter(owner=self.request.user)
        # Sinon, retourne un queryset vide ou lève une erreur selon vos besoins
        return Shop.objects.none()
    def perform_create(self, serializer):
        # Associe l'utilisateur connecté comme owner lors de la création
        serializer.save(owner=self.request.user)

class ShopViewSetSupplier(viewsets.ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializerSupplier
    # permission_classes = [IsAuthenticated]
    
    # def get_queryset(self):
    #     if self.request.user.is_authenticated:
    #         return Shop.objects.filter(owner=self.request.user)
    #     return Shop.objects.none()

class ShopStatsByTypeView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=401)
        shop_stats = (Shop.objects
                     .filter(owner=request.user)
                     .values('typecommerce')
                     .annotate(total=Count('id'))
                     .order_by('typecommerce'))
        serializer = ShopStatsByTypeSerializer(shop_stats, many=True)
        return Response(serializer.data)

class ShopStatsByBranView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=401)
        shop_stats = (Shop.objects
                     .filter(owner=request.user)
                     .values('type')
                     .annotate(total=Count('id'))
                     .order_by('type'))
        serializer = ShopStatsByBrandSerializer(shop_stats, many=True)
        return Response(serializer.data)

class ShopStatsByDateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=401)
        shop_stats = (Shop.objects
                     .filter(owner=request.user)
                     .annotate(date=TruncDate('created_at'))
                     .values('date')
                     .annotate(total=Count('id'))
                     .order_by('date'))
        serializer = ShopStatsByDateSerializer(shop_stats, many=True)
        return Response(serializer.data)

class ShopStatsByMonthView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=401)
        shop_stats = (Shop.objects
                     .filter(owner=request.user)
                     .annotate(month=TruncMonth('created_at'))
                     .values('month')
                     .annotate(total=Count('id'))
                     .order_by('month'))
        serializer = ShopStatsByMonthSerializer(shop_stats, many=True)
        return Response(serializer.data)

class ShopStatsByYearView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=401)
        shop_stats = (Shop.objects
                     .filter(owner=request.user)
                     .annotate(year=TruncYear('created_at'))
                     .values('year')
                     .annotate(total=Count('id'))
                     .order_by('year'))
        serializer = ShopStatsByYearSerializer(shop_stats, many=True)
        return Response(serializer.data)