from rest_framework import serializers
from .models import Shop
from accounts.models import User
from parametres.models import ShopType, TypeCommerce, TailleShop, FrequenceApprovisionnement

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username']

class ShopSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    type = serializers.CharField(source='type.name', read_only=True)
    type_id = serializers.PrimaryKeyRelatedField(
        queryset=ShopType.objects.all(), source='type', write_only=True
    )
    typecommerce = serializers.CharField(source='typecommerce.name', read_only=True, allow_null=True)
    typecommerce_id = serializers.PrimaryKeyRelatedField(
        queryset=TypeCommerce.objects.all(), source='typecommerce', write_only=True, allow_null=True
    )
    taille = serializers.CharField(source='taille.name', read_only=True, allow_null=True)
    taille_id = serializers.PrimaryKeyRelatedField(
        queryset=TailleShop.objects.all(), source='taille', write_only=True, allow_null=True
    )
    frequence_appr = serializers.CharField(source='frequence_appr.name', read_only=True, allow_null=True)
    frequence_appr_id = serializers.PrimaryKeyRelatedField(
        queryset=FrequenceApprovisionnement.objects.all(), source='frequence_appr', write_only=True, allow_null=True
    )

    class Meta:
        model = Shop
        fields = [
            'id', 'owner', 'name', 'image', 'type', 'type_id', 'typecommerce', 'typecommerce_id',
            'taille', 'taille_id', 'brand', 'frequence_appr', 'frequence_appr_id', 'address',
            'latitude', 'longitude', 'owner_name', 'owner_gender', 'owner_phone', 'owner_email',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['owner', 'created_at', 'updated_at']

class ShopSerializerSupplier(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['id', 'name']
        read_only_fields = ['id', 'name']

class ShopStatsByTypeSerializer(serializers.Serializer):
    typecommerce = serializers.CharField(source='typecommerce__name', read_only=True, allow_null=True)
    total = serializers.IntegerField()

class ShopStatsByBrandSerializer(serializers.Serializer):
    type = serializers.CharField(source='type__name', read_only=True, allow_null=True)
    total = serializers.IntegerField()

class ShopStatsByDateSerializer(serializers.Serializer):
    date = serializers.DateField()
    total = serializers.IntegerField()

class ShopStatsByMonthSerializer(serializers.Serializer):
    month = serializers.CharField()  # Format: YYYY-MM
    total = serializers.IntegerField()

class ShopStatsByYearSerializer(serializers.Serializer):
    year = serializers.CharField()  # Format: YYYY
    total = serializers.IntegerField()

from rest_framework import serializers

class OverviewSerializer(serializers.Serializer):
    total_shops = serializers.IntegerField()
    recent_shops = serializers.IntegerField()
    total_suppliers = serializers.IntegerField()
    timeframe_days = serializers.IntegerField()

class ShopStatsSerializer(serializers.Serializer):
    name = serializers.CharField()
    owner__username = serializers.CharField()
    type__name = serializers.CharField(allow_null=True)
    typecommerce__name = serializers.CharField(allow_null=True)
    taille__name = serializers.CharField(allow_null=True)
    frequence_appr__name = serializers.CharField(allow_null=True)
    total_products = serializers.IntegerField()
    total_sales = serializers.IntegerField(allow_null=True)
    total_orders = serializers.IntegerField()

class TypeCommerceStatsSerializer(serializers.Serializer):
    typecommerce__name = serializers.CharField(allow_null=True)
    total = serializers.IntegerField()
    total_products = serializers.IntegerField()
    total_orders = serializers.IntegerField()

class ShopTypeStatsSerializer(serializers.Serializer):
    type__name = serializers.CharField(allow_null=True)
    total = serializers.IntegerField()
    total_products = serializers.IntegerField()
    total_orders = serializers.IntegerField()

class TailleStatsSerializer(serializers.Serializer):
    taille__name = serializers.CharField(allow_null=True)
    total = serializers.IntegerField()
    total_products = serializers.IntegerField()
    total_orders = serializers.IntegerField()

class FrequenceApprStatsSerializer(serializers.Serializer):
    frequence_appr__name = serializers.CharField(allow_null=True)
    total = serializers.IntegerField()
    total_products = serializers.IntegerField()
    total_orders = serializers.IntegerField()

class OwnerStatsSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    user_type__name = serializers.CharField(allow_null=True)
    total_shops = serializers.IntegerField()
    total_products = serializers.IntegerField()
    total_sales = serializers.IntegerField(allow_null=True)
    total_orders = serializers.IntegerField()

class CommuneStatsSerializer(serializers.Serializer):
    commune__name = serializers.CharField(allow_null=True)
    total = serializers.IntegerField()
    total_products = serializers.IntegerField()
    total_orders = serializers.IntegerField()

class QuartierStatsSerializer(serializers.Serializer):
    quartier__name = serializers.CharField(allow_null=True)
    commune__name = serializers.CharField(allow_null=True)
    total = serializers.IntegerField()
    total_products = serializers.IntegerField()
    total_orders = serializers.IntegerField()

class ZoneStatsSerializer(serializers.Serializer):
    zone__name = serializers.CharField(allow_null=True)
    commune__name = serializers.CharField(allow_null=True)
    total = serializers.IntegerField()
    total_products = serializers.IntegerField()
    total_orders = serializers.IntegerField()