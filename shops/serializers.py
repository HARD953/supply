from rest_framework import serializers
from .models import Shop

class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = '__all__'


class ShopStatsByTypeSerializer(serializers.Serializer):
    typecommerce = serializers.CharField()
    total = serializers.IntegerField()

class ShopStatsByBrandSerializer(serializers.Serializer):
    type = serializers.CharField()
    total = serializers.IntegerField()

class ShopStatsByDateSerializer(serializers.Serializer):
    date = serializers.DateField()
    total = serializers.IntegerField()

class ShopStatsByMonthSerializer(serializers.Serializer):
    month = serializers.DateField()
    total = serializers.IntegerField()

class ShopStatsByYearSerializer(serializers.Serializer):
    year = serializers.DateField()
    total = serializers.IntegerField()