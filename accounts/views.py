from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from .models import User, Module4, ModulePermission4
from .serializers import (
    UserSerializer, UserRegistrationSerializer, UserSerializerCommune,
    UserSerializerQuartier, UserSerializerZone, ModuleSerializer,
    PermissionSerializer, CurrentUserSerializer
)

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            user = User.objects.get(email=request.data['email'])
            response.data.update({
                'user_id': user.pk,
                'email': user.email,
                'user_type': user.user_type,
                'username': user.username,
            })
        return response

class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

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

class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Compte créé avec succès."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = CurrentUserSerializer(request.user.user_name)
        return Response(serializer.data)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsAdminUser]
        return super().get_permissions()

class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module4.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class PermissionViewSet(viewsets.ModelViewSet):
    queryset = ModulePermission4.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class UserViewSetCommune(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializerCommune
    permission_classes = [IsAuthenticated]

class UserViewSetQuartier(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializerQuartier
    permission_classes = [IsAuthenticated]

class UserViewSetZone(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializerZone
    permission_classes = [IsAuthenticated]