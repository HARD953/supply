from rest_framework import serializers
from .models import Supplier

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'type', 'phone_number', 'email', 'address', 'average_delivery_time', 'order_frequency']