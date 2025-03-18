from rest_framework import serializers
from .models import Category, Certification, Product

class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = ['id', 'name']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class ProductSerializer(serializers.ModelSerializer):
    # category = CategorySerializer(read_only=True)
    # category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), write_only=True)
    # certifications = CertificationSerializer(many=True, read_only=True)
    # # certification_ids = serializers.PrimaryKeyRelatedField(queryset=Certification.objects.all(), write_only=True, many=True)

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['owner']

    # def create(self, validated_data):
    #     certification_ids = validated_data.pop('certification_ids', [])
    #     product = Product.objects.create(**validated_data)
    #     product.certifications.set(certification_ids)
    #     return product

    # def update(self, instance, validated_data):
    #     certification_ids = validated_data.pop('certification_ids', [])
    #     instance = super().update(instance, validated_data)
    #     instance.certifications.set(certification_ids)
    #     return instance