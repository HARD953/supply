from rest_framework import serializers
from .models import (
    Commune, Quartier, Zone, UserType, Category, Certification,
    ShopType, TypeCommerce, TailleShop, FrequenceApprovisionnement,
    OrderStatus, Taille, Couleur, Module
)
from accounts.models import User

class CommuneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commune
        fields = ['id', 'name', 'code']

class QuartierSerializer(serializers.ModelSerializer):
    commune = serializers.PrimaryKeyRelatedField(queryset=Commune.objects.all())
    commune_name = serializers.CharField(source='commune.name', read_only=True)

    class Meta:
        model = Quartier
        fields = ['id', 'name', 'commune', 'commune_name']

class ZoneSerializer(serializers.ModelSerializer):
    commune = serializers.PrimaryKeyRelatedField(queryset=Commune.objects.all(), allow_null=True)
    commune_name = serializers.CharField(source='commune.name', read_only=True, allow_null=True)

    class Meta:
        model = Zone
        fields = ['id', 'name', 'commune', 'commune_name']

class UserTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserType
        fields = ['id', 'name', 'description']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'image','app']

class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = ['id', 'name', 'description']

class ShopTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopType
        fields = ['id', 'name', 'code']

class TypeCommerceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeCommerce
        fields = ['id', 'name', 'description']

class TailleShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = TailleShop
        fields = ['id', 'name']

class FrequenceApprovisionnementSerializer(serializers.ModelSerializer):
    class Meta:
        model = FrequenceApprovisionnement
        fields = ['id', 'name', 'days']

class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatus
        fields = ['id', 'name', 'code', 'description']

class TailleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Taille
        fields = ['id', 'name']

class CouleurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Couleur
        fields = ['id', 'name', 'hex_code']

class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['id', 'name', 'description', 'icon', 'link', 'color']

