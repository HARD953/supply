from rest_framework import viewsets
from .models import Shop
from .serializers import ShopSerializer,ShopSerializerSupplier

class ShopViewSet(viewsets.ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer

class ShopViewSetSupplier(viewsets.ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializerSupplier

from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from django.db.models.functions import TruncDate, TruncMonth, TruncYear
from .models import Shop
from .serializers import (
    ShopStatsByTypeSerializer,
    ShopStatsByDateSerializer,
    ShopStatsByMonthSerializer,
    ShopStatsByYearSerializer,
    ShopStatsByBrandSerializer
)

class ShopStatsByTypeView(APIView):
    def get(self, request):
        shop_stats = Shop.objects.values('typecommerce').annotate(total=Count('id')).order_by('typecommerce')
        serializer = ShopStatsByTypeSerializer(shop_stats, many=True)
        return Response(serializer.data)
    
class ShopStatsByBranView(APIView):
    def get(self, request):
        shop_stats = Shop.objects.values('type').annotate(total=Count('id')).order_by('type')
        serializer = ShopStatsByBrandSerializer(shop_stats, many=True)
        return Response(serializer.data)

class ShopStatsByDateView(APIView):
    def get(self, request):
        shop_stats = Shop.objects.annotate(date=TruncDate('created_at')).values('date').annotate(total=Count('id')).order_by('date')
        serializer = ShopStatsByDateSerializer(shop_stats, many=True)
        return Response(serializer.data)

class ShopStatsByMonthView(APIView):
    def get(self, request): 
        shop_stats = Shop.objects.annotate(month=TruncMonth('created_at')).values('month').annotate(total=Count('id')).order_by('month')
        serializer = ShopStatsByMonthSerializer(shop_stats, many=True)
        return Response(serializer.data)

class ShopStatsByYearView(APIView):
    def get(self, request):
        shop_stats = Shop.objects.annotate(year=TruncYear('created_at')).values('year').annotate(total=Count('id')).order_by('year')
        serializer = ShopStatsByYearSerializer(shop_stats, many=True)
        return Response(serializer.data)