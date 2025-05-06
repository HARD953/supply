from rest_framework import serializers
from django.db import transaction
from .models import Product, ProductFormat, Order, OrderItem
from parametres.models import Category, OrderStatus, Taille, Couleur
from accounts.models import User

from rest_framework import serializers

class ProductStatsSerializer(serializers.Serializer):
    overview = serializers.DictField()
    by_category = serializers.ListField()
    by_order_status = serializers.ListField()
    top_products = serializers.ListField()
    by_supplier = serializers.ListField()
    suppliers_by_commerce = serializers.ListField()
    suppliers_by_commune = serializers.ListField()
    suppliers_by_user_type = serializers.ListField()
    by_order_user = serializers.ListField()
    order_users_by_user_type = serializers.ListField()

    class Meta:
        fields = [
            'overview', 'by_category', 'by_order_status', 'top_products',
            'by_supplier', 'suppliers_by_commerce', 'suppliers_by_commune',
            'suppliers_by_user_type', 'by_order_user', 'order_users_by_user_type'
        ]


from rest_framework import serializers

class ProductStatsSerializerShop(serializers.Serializer):
    overview = serializers.DictField()
    by_order_status = serializers.ListField()
    by_order_user = serializers.ListField()
    order_users_by_user_type = serializers.ListField()
    by_supplier = serializers.ListField()
    by_shop = serializers.ListField()
    top_products = serializers.ListField()
    shops_by_typecommerce = serializers.ListField()

    class Meta:
        fields = [
            'overview', 'by_order_status', 'by_order_user', 'order_users_by_user_type',
            'by_supplier', 'by_shop', 'top_products', 'shops_by_typecommerce'
        ]

class ProductFormatSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    taille = serializers.CharField(source='taille.name', read_only=True, allow_null=True)
    taille_id = serializers.PrimaryKeyRelatedField(
        queryset=Taille.objects.all(), source='taille', write_only=True, allow_null=True
    )
    couleur = serializers.CharField(source='couleur.name', read_only=True, allow_null=True)
    couleur_id = serializers.PrimaryKeyRelatedField(
        queryset=Couleur.objects.all(), source='couleur', write_only=True, allow_null=True
    )

    class Meta:
        model = ProductFormat
        fields = [
            'id', 'product', 'product_name', 'taille', 'taille_id', 'couleur', 'couleur_id',
            'price', 'image', 'stock', 'min_stock'
        ]
        read_only_fields = ['product_name']

class ProductSerializer(serializers.ModelSerializer):
    formats = ProductFormatSerializer(many=True, required=False)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )
    supplier_email = serializers.CharField(source='supplier.email', read_only=True)
    supplier_username = serializers.CharField(source='supplier.username', read_only=True)
    supplier = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'category', 'category_id', 'category_name', 'supplier', 'supplier_email',
            'supplier_username', 'last_order', 'image', 'formats'
        ]
        read_only_fields = ['supplier_email', 'supplier_username']

    def validate_supplier(self, value):
        try:
            if not value.user_type.name == "Fournisseur":
                raise serializers.ValidationError("Le fournisseur doit avoir le type 'Fournisseur'.")
        except AttributeError:
            raise serializers.ValidationError("Le type d'utilisateur 'Fournisseur' n'existe pas.")
        return value

    def create(self, validated_data):
        formats_data = validated_data.pop('formats', [])
        product = Product.objects.create(**validated_data)
        for format_data in formats_data:
            ProductFormat.objects.create(product=product, **format_data)
        return product

    def update(self, instance, validated_data):
        formats_data = validated_data.pop('formats', [])
        instance.name = validated_data.get('name', instance.name)
        instance.category = validated_data.get('category', instance.category)
        instance.supplier = validated_data.get('supplier', instance.supplier)
        instance.last_order = validated_data.get('last_order', instance.last_order)
        instance.image = validated_data.get('image', instance.image)
        instance.save()

        existing_formats = {format.id: format for format in instance.formats.all()}
        format_ids = []
        for format_data in formats_data:
            format_id = format_data.get('id')
            if format_id and format_id in existing_formats:
                format_instance = existing_formats[format_id]
                for field in ['taille', 'couleur', 'price', 'image', 'stock', 'min_stock']:
                    setattr(format_instance, field, format_data.get(field, getattr(format_instance, field)))
                format_instance.save()
                format_ids.append(format_id)
            else:
                format_instance = ProductFormat.objects.create(product=instance, **format_data)
                format_ids.append(format_instance.id)

        for format_id in existing_formats:
            if format_id not in format_ids:
                existing_formats[format_id].delete()

        return instance

class OrderItemSerializer(serializers.ModelSerializer):
    product_format = ProductFormatSerializer(read_only=True)
    product_format_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductFormat.objects.all(), source='product_format', write_only=True
    )

    class Meta:
        model = OrderItem
        fields = ['id', 'product_format', 'product_format_id', 'quantity', 'price_at_order']
        read_only_fields = ['price_at_order']

    def validate(self, data):
        product_format = data['product_format']
        quantity = data['quantity']
        if quantity > product_format.stock:
            raise serializers.ValidationError(
                f"La quantité commandée ({quantity}) dépasse le stock disponible ({product_format.stock})."
            )
        return data

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    status = serializers.PrimaryKeyRelatedField(queryset=OrderStatus.objects.all())

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'created_at', 'updated_at', 'items']
        read_only_fields = ['user', 'created_at', 'updated_at']

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        validated_data['user'] = self.context['request'].user
        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            product_format = item_data['product_format']
            quantity = item_data['quantity']
            OrderItem.objects.create(
                order=order,
                product_format=product_format,
                quantity=quantity,
                price_at_order=product_format.price
            )
            product_format.stock -= quantity
            product_format.save()

        return order

    @transaction.atomic
    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        instance.status = validated_data.get('status', instance.status)
        instance.save()

        if items_data is not None:
            for item in instance.items.all():
                item.product_format.stock += item.quantity
                item.product_format.save()
                item.delete()

            for item_data in items_data:
                product_format = item_data['product_format']
                quantity = item_data['quantity']
                OrderItem.objects.create(
                    order=instance,
                    product_format=product_format,
                    quantity=quantity,
                    price_at_order=product_format.price
                )
                product_format.stock -= quantity
                product_format.save()

        return instance