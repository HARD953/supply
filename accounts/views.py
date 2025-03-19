# views.py
from rest_framework import status, permissions, generics, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import *
from rest_framework.views import APIView

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Récupérer l'utilisateur à partir du token
            token_data = response.data
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(email=request.data['email'])
            
            response.data.update({
                'user_id': user.pk,
                'email': user.email,
                'user_type': user.email,
                'username': user.username,
            })
        
        return response

class UserLogoutView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response(
                    {"message": "Déconnexion réussie."},
                    status=status.HTTP_200_OK
                )
            return Response(
                {"error": "Refresh token requis pour la déconnexion."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception:
            return Response(
                {"error": "Token invalide ou expiré."},
                status=status.HTTP_400_BAD_REQUEST
            )

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Compte créé avec succès."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return super().get_permissions()
    
class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class UserViewSetCommune(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializerCommune

class UserViewSetQuartier(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializerQuartier

class UserViewSetZone(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializerZone