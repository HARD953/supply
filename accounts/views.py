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

class ByUserTypeView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = CustomShopPagination
    renderer_classes = [JSONRenderer]  # Forcer JSON

    def list(self, request):
        # Récupérer le paramètre user_type depuis les query_params
        user_type_filter = request.query_params.get('user_type', None)

        # Construire la requête initiale
        if user_type_filter:
            # Filtrer par user_type si le paramètre est fourni
            user_types_data = User.objects.filter(user_type__name=user_type_filter).values('user_type__name').annotate(total=Count('id')).order_by('user_type__name')
        else:
            # Pas de filtre si aucun user_type n'est fourni
            user_types_data = User.objects.values('user_type__name').annotate(total=Count('id')).order_by('user_type__name')

        result = []

        # Gestion de la pagination
        if request.query_params.get('paginate') == 'true':
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(user_types_data, request)
        else:
            page = user_types_data

        # Construire la réponse
        for user_type in page:
            user_type_name = user_type['user_type__name']
            users = User.objects.filter(user_type__name=user_type_name).select_related('user_type', 'commune', 'quartier', 'zone')
            serializer = UserSerializer(users, many=True, context={'request': request})
            result.append({
                'user_type': user_type_name,
                'total': user_type['total'],
                'users': serializer.data
            })

        # Retourner la réponse paginée ou non
        if request.query_params.get('paginate') == 'true':
            return paginator.get_paginated_response(result)
        return Response(result)

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