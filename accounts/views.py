from django.db.models import Count, Q
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.renderers import JSONRenderer
from rest_framework import generics
from .models import User, ModulePermission
from .serializers import (
    UserSerializer, UserRegistrationSerializer, CurrentUserSerializer,
    ModulePermissionSerializer
)
from datetime import datetime, timedelta

from parametres.models import UserType

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

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().select_related('user_type', 'commune', 'quartier', 'zone').order_by('username')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['username', 'email', 'user_type', 'commune', 'quartier', 'zone', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    pagination_class = CustomShopPagination
    renderer_classes = [JSONRenderer]  # Forcer JSON

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsAdminUser]
        elif self.action == 'register':
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    def get_queryset(self):
        if not self.request.user.is_staff:
            return User.objects.filter(id=self.request.user.id).select_related('user_type', 'commune', 'quartier', 'zone')
        return super().get_queryset()

    def get_serializer_class(self):
        if self.action == 'register':
            return UserRegistrationSerializer
        elif self.action == 'current':
            return CurrentUserSerializer
        return super().get_serializer_class()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        if request.query_params.get('paginate') == 'true':
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(queryset, request)
            serializer = self.get_serializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Compte créé avec succès."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def current(self, request):
        serializer = CurrentUserSerializer(request.user, context={'request': request})
        return Response(serializer.data)

class ModulePermissionViewSet(viewsets.ModelViewSet):
    queryset = ModulePermission.objects.all().select_related('module', 'user').order_by('user__username')
    serializer_class = ModulePermissionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['module', 'user']
    search_fields = ['module__name', 'user__username']
    pagination_class = CustomShopPagination
    renderer_classes = [JSONRenderer]  # Forcer JSON

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        if request.query_params.get('paginate') == 'true':
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(queryset, request)
            serializer = self.get_serializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        return Response(serializer.data)



class UserByTypeViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = CustomShopPagination
    renderer_classes = [JSONRenderer]

    def get_users_by_type(self, user_type_name, request):
        """
        Helper method to fetch users by user type with pagination.
        """
        # Filter users by user_type
        users = User.objects.filter(user_type__name=user_type_name).select_related(
            'user_type', 'commune', 'quartier', 'zone'
        )

        # Handle pagination
        paginate = request.query_params.get('paginate') == 'true'
        if paginate:
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(users, request)
        else:
            page = users

        # Serialize the data
        serializer = UserSerializer(page, many=True, context={'request': request})

        if paginate:
            return paginator.get_paginated_response(serializer.data)
        return Response(serializer.data)

    def list(self, request):
        """
        Default endpoint to return all users grouped by user_type.
        """
        # Get all user types
        user_types = UserType.objects.all()

        # Initialize result list
        result = []

        # Iterate through each user type
        for user_type in user_types:
            users = User.objects.filter(user_type=user_type).select_related(
                'user_type', 'commune', 'quartier', 'zone'
            )
            serializer = UserSerializer(users, many=True, context={'request': request})
            result.extend(serializer.data)  # Extend to flatten the list

        # Handle pagination
        paginate = request.query_params.get('paginate') == 'true'
        if paginate:
            paginator = self.pagination_class()
            # Since we're not using a queryset directly, we need to handle pagination manually
            page = paginator.paginate_queryset(result, request)
            return paginator.get_paginated_response(page)
        return Response(result)

    @action(detail=False, methods=['get'], url_path='super_admin')
    def super_admin(self, request):
        """Endpoint for super_admin users."""
        return self.get_users_by_type('super_admin', request)

    @action(detail=False, methods=['get'], url_path='admin')
    def admin(self, request):
        """Endpoint for admin users."""
        return self.get_users_by_type('admin', request)

    @action(detail=False, methods=['get'], url_path='fabricant')
    def fabricant(self, request):
        """Endpoint for fabricant users."""
        return self.get_users_by_type('fabricant', request)

    @action(detail=False, methods=['get'], url_path='grossiste')
    def grossiste(self, request):
        """Endpoint for grossiste users."""
        return self.get_users_by_type('Grossiste', request)

    @action(detail=False, methods=['get'], url_path='semi_grossiste')
    def semi_grossiste(self, request):
        """Endpoint for semi_grossiste users."""
        return self.get_users_by_type('semi_grossiste', request)

    @action(detail=False, methods=['get'], url_path='detaillant')
    def detaillant(self, request):
        """Endpoint for detaillant users."""
        return self.get_users_by_type('detaillant', request)

class StatsView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = CustomShopPagination
    renderer_classes = [JSONRenderer]  # Forcer JSON

    def list(self, request):
        days = int(request.query_params.get('days', 30))
        start_date = datetime.now() - timedelta(days=days)

        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        new_users = User.objects.filter(created_at__gte=start_date).count()

        user_types_stats = User.objects.values('user_type__name').annotate(
            total=Count('id'),
            active=Count('id', filter=Q(is_active=True)),
            recent=Count('id', filter=Q(created_at__gte=start_date))
        ).order_by('user_type__name')

        commune_stats = User.objects.values('commune__name').annotate(
            total=Count('id'),
            active=Count('id', filter=Q(is_active=True))
        ).order_by('-total')[:10]

        commerce_stats = User.objects.values('typecommerce__name').annotate(
            total=Count('id')
        ).order_by('-total')

        activity_rate = (active_users / total_users * 100) if total_users > 0 else 0

        if request.query_params.get('paginate') == 'true':
            paginator = self.pagination_class()
            user_types_paginated = paginator.paginate_queryset(user_types_stats, request)
            commune_paginated = paginator.paginate_queryset(commune_stats, request)
            commerce_paginated = paginator.paginate_queryset(commerce_stats, request)

            response_data = {
                'overview': {
                    'total_users': total_users,
                    'active_users': active_users,
                    'new_users_last_30_days': new_users,
                    'activity_rate': round(activity_rate, 2),
                    'timeframe_days': days
                },
                'by_user_type': user_types_paginated,
                'by_commune': commune_paginated,
                'by_commerce_type': commerce_paginated
            }
            return paginator.get_paginated_response(response_data)
        else:
            response_data = {
                'overview': {
                    'total_users': total_users,
                    'active_users': active_users,
                    'new_users_last_30_days': new_users,
                    'activity_rate': round(activity_rate, 2),
                    'timeframe_days': days
                },
                'by_user_type': list(user_types_stats),
                'by_commune': list(commune_stats),
                'by_commerce_type': list(commerce_stats)
            }
            return Response(response_data)

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            try:
                user = User.objects.get(email=request.data['email'])
                response.data.update({
                    'user_id': user.pk,
                    'email': user.email,
                    'username': user.username,
                    'user_type': user.user_type.name if user.user_type else None,
                    'company_name': user.company_name if user.company_name else None,
                })
            except User.DoesNotExist:
                return Response({"error": "Utilisateur non trouvé."}, status=status.HTTP_404_NOT_FOUND)
        return response
from rest_framework.views import APIView
class UserLogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get('refresh_token')
            if not refresh_token:
                return Response({"error": "Refresh token requis."}, status=status.HTTP_400_BAD_REQUEST)
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Déconnexion réussie."}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Token invalide ou expiré."}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        return Response({"error": "Méthode GET non autorisée. Utilisez POST."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)