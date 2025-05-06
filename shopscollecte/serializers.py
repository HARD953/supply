from rest_framework import serializers
from .models import ProductCollecte
from accounts.models import User
from shops.models import Shop
from parametres.models import Category, FrequenceApprovisionnement

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username']

class ProductCollecteSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    category = serializers.CharField(source='category.name', read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )
    category_name = serializers.CharField(source='category.name', read_only=True)
    frequence_appr = serializers.CharField(source='frequence_appr.name', read_only=True, allow_null=True)
    frequence_appr_id = serializers.PrimaryKeyRelatedField(
        queryset=FrequenceApprovisionnement.objects.all(), source='frequence_appr', write_only=True, allow_null=True
    )
    supplier = serializers.CharField(source='supplier.name', read_only=True)
    supplier_id = serializers.PrimaryKeyRelatedField(
        queryset=Shop.objects.all(), source='supplier', write_only=True
    )
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)

    class Meta:
        model = ProductCollecte
        fields = [
            'id', 'owner', 'name', 'category', 'category_id', 'category_name', 'price', 'image',
            'stock', 'frequence_appr', 'frequence_appr_id', 'reorder_frequency', 'supplier',
            'supplier_id', 'supplier_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['owner', 'created_at', 'updated_at', 'category_name', 'supplier_name']

from rest_framework import serializers

class ProductCollecteStatsSerializer(serializers.Serializer):
    overview = serializers.DictField()
    by_owner = serializers.ListField()
    by_supplier = serializers.ListField()
    by_category = serializers.ListField()
    by_frequence_appr = serializers.ListField()

    class Meta:
        fields = [
            'overview', 'by_owner', 'by_supplier', 'by_category', 'by_frequence_appr'
        ]