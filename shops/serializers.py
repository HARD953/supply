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

class ShopStatsSerializer(serializers.Serializer):
    overview = serializers.DictField()
    by_shop = serializers.ListField()
    shops_by_typecommerce = serializers.ListField()
    shops_by_type = serializers.ListField()
    shops_by_taille = serializers.ListField()
    shops_by_frequence_appr = serializers.ListField()
    by_supplier = serializers.ListField()
    by_order_user = serializers.ListField()
    order_users_by_user_type = serializers.ListField()

    class Meta:
        fields = [
            'overview', 'by_shop', 'shops_by_typecommerce', 'shops_by_type',
            'shops_by_taille', 'shops_by_frequence_appr', 'by_supplier',
            'by_order_user', 'order_users_by_user_type'
        ]