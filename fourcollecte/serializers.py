from rest_framework import serializers
from .models import SupplierCollecte, SupplierContact

class SupplierContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierContact
        fields = ['phone', 'email', 'address']

class SupplierSerializer(serializers.ModelSerializer):
    #contact = SupplierContactSerializer()

    class Meta:
        model = SupplierCollecte
        fields = '__all__'

    # def create(self, validated_data):
    #     contact_data = validated_data.pop('contact')
    #     supplier = SupplierCollecte.objects.create(**validated_data)
    #     SupplierContact.objects.create(supplier=supplier, **contact_data)
    #     return supplier

    # def update(self, instance, validated_data):
    #     contact_data = validated_data.pop('contact')
    #     contact = instance.contact

    #     # Mettre à jour les champs du fournisseur
    #     instance.name = validated_data.get('name', instance.name)
    #     instance.type = validated_data.get('type', instance.type)
    #     instance.image = validated_data.get('image', instance.image)
    #     instance.delivery_time = validated_data.get('delivery_time', instance.delivery_time)
    #     instance.order_frequency = validated_data.get('order_frequency', instance.order_frequency)
    #     instance.longitute = validated_data.get('delivery_time', instance.delivery_time)
    #     instance.order_frequency = validated_data.get('order_frequency', instance.order_frequency)
    #     instance.save()

    #     # Mettre à jour les coordonnées
    #     contact.phone = contact_data.get('phone', contact.phone)
    #     contact.email = contact_data.get('email', contact.email)
    #     contact.address = contact_data.get('address', contact.address)
    #     contact.save()

    #     return instance