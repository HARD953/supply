# serializers.py
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'user_type', 'phone_number',
            'company_name', 'company_tax_id', 'website', 'email', 'image','latitude','longitude',
            'contact_person', 'business_address','registre','date_creation','commune','quartier','zone'
        ]

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'username', 'password', 'email', 'user_type', 'phone_number',
            'company_name', 'company_tax_id', 'website', 'email', 'latitude','longitude',
            'contact_person', 'business_address','image','registre','date_creation','commune','quartier','zone'
        ]

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
    
class UserSerializerCommune(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['commune']

class UserSerializerQuartier(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['quartier']

class UserSerializerZone(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['zone']