from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import (
    UserStatsSerializer, ShopStatsSerializer, ProductStatsSerializer,
    OrderStatsSerializer, ProductCollecteStatsSerializer, ModuleStatsSerializer
)
from accounts.models import User
from shops.models import Shop
from products.models import Product, Order
from shopscollecte.models import ProductCollecte
from parametres.models import Module
from accounts.models import ModulePermission


class ModulePermissionRequired:
    def has_permission(self, request, view):
        if request.user.is_staff:
            return True
        module_name = getattr(view, 'module_name', None)
        if not module_name:
            return False
        try:
            permission = ModulePermission.objects.get(user=request.user, module__name=module_name)
            return permission.can_read
        except ModulePermission.DoesNotExist:
            return False

    def has_object_permission(self, request, view, obj):
        # Since views are list-based and don't require object-level checks,
        # reuse has_permission for consistency
        return self.has_permission(request, view)


class BaseStatsView(APIView):
    permission_classes = [IsAuthenticated, ModulePermissionRequired]
    module_name = 'Statistiques'


class UserStatsView(BaseStatsView):
    def get(self, request):
        try:
            queryset = User.objects.all()
            if not request.user.is_staff:
                queryset = queryset.filter(id=request.user.id)
            serializer = UserStatsSerializer(queryset)
            data = serializer.data
            return Response(data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ShopStatsView(BaseStatsView):
    def get(self, request):
        try:
            queryset = Shop.objects.all()
            if not request.user.is_staff:
                queryset = queryset.filter(owner=request.user)
            serializer = ShopStatsSerializer(queryset)
            data = serializer.data
            return Response(data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ProductStatsView(BaseStatsView):
    def get(self, request):
        try:
            queryset = Product.objects.all()
            if not request.user.is_staff:
                queryset = queryset.filter(supplier=request.user)
            serializer = ProductStatsSerializer(queryset)
            data = serializer.data
            return Response(data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ProductCollecteStatsView(BaseStatsView):
    def get(self, request):
        try:
            queryset = ProductCollecte.objects.all()
            if not request.user.is_staff:
                queryset = queryset.filter(owner=request.user)
            serializer = ProductCollecteStatsSerializer(queryset)
            data = serializer.data
            return Response(data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class OrderStatsView(BaseStatsView):
    def get(self, request):
        try:
            queryset = Order.objects.all()
            if not request.user.is_staff:
                queryset = queryset.filter(user=request.user)
            serializer = OrderStatsSerializer(queryset)
            data = serializer.data
            return Response(data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ModuleStatsView(BaseStatsView):
    def get(self, request):
        if not request.user.is_staff:
            return Response(
                {"error": "Only admin users can access module statistics."},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = ModuleStatsSerializer(None)
        data = serializer.data
        return Response(data)