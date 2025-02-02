# serializers.py
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'user_type', 'phone_number', 'address',
            'company_name', 'company_tax_id', 'website', 'contact_email', 
            'contact_person', 'business_address'
        ]

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'username', 'password', 'email', 'user_type', 'phone_number', 'address',
            'company_name', 'company_tax_id', 'website', 'contact_email', 
            'contact_person', 'business_address','image'
        ]

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)