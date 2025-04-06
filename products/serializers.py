from rest_framework import serializers
from .models import Category, Product, ProductFormat, Order, OrderItem
from django.db import transaction
from suppliers.models import Supplier  # Assurez-vous d'importer votre modèle Supplier

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name']

class ProductFormatSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    class Meta:
        model = ProductFormat
        fields = ['id', 'product_name', 'product','taille', 'couleur', 'price', 'image', 'stock', 'min_stock']

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['name']

class ProductSerializer(serializers.ModelSerializer):
    formats = ProductFormatSerializer(many=True, required=False)
    category_name = serializers.CharField(source='category.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.company_name', read_only=True)
    supplier_commune = serializers.CharField(source='supplier.commune', read_only=True)
    supplier_quartier = serializers.CharField(source='supplier.quartier', read_only=True)
    supplier_zone = serializers.CharField(source='supplier.zone', read_only=True)
    supplier_phone = serializers.CharField(source='supplier.phone_number', read_only=True)
    supplier_type = serializers.CharField(source='supplier.type', read_only=True)
    supplier_longitude = serializers.CharField(source='supplier.longitude', read_only=True)
    supplier_latitude = serializers.CharField(source='supplier.latitude', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'category_name', 'supplier', 'supplier_name', 'supplier_commune','supplier_quartier','supplier_zone','last_order', 'formats','supplier_latitude','supplier_longitude','supplier_type','supplier_phone']
        extra_kwargs = {
            'category': {'write_only': True},
            'supplier': {'write_only': True},
        }

    def create(self, validated_data):
        formats_data = validated_data.pop('formats', [])
        product = Product.objects.create(**validated_data)
        for format_data in formats_data:
            ProductFormat.objects.create(product=product, **format_data)
        return product

    def update(self, instance, validated_data):
        formats_data = validated_data.pop('formats', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        existing_formats = {format.id: format for format in instance.formats.all()}
        for format_data in formats_data:
            format_id = format_data.get('id', None)
            if format_id and format_id in existing_formats:
                format_instance = existing_formats[format_id]
                for field in ['taille', 'couleur', 'price', 'image', 'stock', 'min_stock']:
                    setattr(format_instance, field, format_data.get(field, getattr(format_instance, field)))
                format_instance.save()
            else:
                ProductFormat.objects.create(product=instance, **format_data)

        format_ids = [format_data.get('id') for format_data in formats_data if format_data.get('id')]
        for format_id, format_instance in existing_formats.items():
            if format_id not in format_ids:
                format_instance.delete()

        return instance

class OrderItemSerializer(serializers.ModelSerializer):
    # Champs du ProductFormat
    format_id = serializers.IntegerField(source='product_format.id')
    taille = serializers.CharField(source='product_format.taille')
    couleur = serializers.CharField(source='product_format.couleur')
    price = serializers.DecimalField(source='product_format.price', max_digits=10, decimal_places=2)
    image = serializers.ImageField(source='product_format.image')
    stock = serializers.IntegerField(source='product_format.stock')
    
    # Champs du Product
    product_id = serializers.IntegerField(source='product_format.product.id')
    product_name = serializers.CharField(source='product_format.product.name')
    
    # Champs de la Category
    category_id = serializers.IntegerField(source='product_format.product.category.id')
    category_name = serializers.CharField(source='product_format.product.category.name')

    # Champ pour la création/modification
    product_format_id = serializers.PrimaryKeyRelatedField(
        source='product_format',
        queryset=ProductFormat.objects.all(),
        write_only=True
    )

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'product_format_id',  # Pour l'écriture
            'format_id',         # Pour la lecture
            'product_id',
            'product_name',
            'category_id',
            'category_name',
            'taille',
            'couleur',
            'price',
            'image',
            'stock',
            'quantity',
            'price_at_order'
        ]
        read_only_fields = [
            'format_id', 'product_id', 'product_name', 
            'category_id', 'category_name', 'taille', 
            'couleur', 'price', 'image', 'stock',
            'price_at_order'
        ]

    def validate(self, data):
        product_format = data['product_format']
        quantity = data['quantity']

        if quantity > product_format.stock:
            raise serializers.ValidationError("La quantité commandée dépasse le stock disponible.")
        
        return data

    
from rest_framework import serializers
from .models import Category, Product, ProductFormat, Order, OrderItem
from django.db import transaction

class OrderItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product_format', 'quantity']

class OrderItemReadSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='product_format.product.supplier.name', read_only=True)
    # Champs du ProductFormat
    format_id = serializers.IntegerField(source='product_format.id')
    taille = serializers.CharField(source='product_format.taille')
    couleur = serializers.CharField(source='product_format.couleur')
    price = serializers.DecimalField(source='product_format.price', max_digits=10, decimal_places=2)
    image = serializers.ImageField(source='product_format.image')
    stock = serializers.IntegerField(source='product_format.stock')
    
    # Champs du Product
    product_id = serializers.IntegerField(source='product_format.product.id')
    product_name = serializers.CharField(source='product_format.product.name')
    
    # Champs de la Category
    category_id = serializers.IntegerField(source='product_format.product.category.id')
    category_name = serializers.CharField(source='product_format.product.category.name')

    class Meta:
        model = OrderItem
        fields = [
            'supplier_name',
            'id',
            'format_id',
            'product_id',
            'product_name',
            'category_id',
            'category_name',
            'taille',
            'couleur',
            'price',
            'image',
            'stock',
            'quantity',
            'price_at_order'
        ]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True, write_only=True)
    items_detail = OrderItemReadSerializer(source='items', many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id','status', 'created_at', 'updated_at', 'items', 'items_detail']
        read_only_fields = ['created_at', 'updated_at','user']

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        
        for item_data in items_data:
            product_format = item_data['product_format']
            quantity = item_data['quantity']
            
            if quantity > product_format.stock:
                raise serializers.ValidationError(
                    f"Stock insuffisant pour {product_format.product.name} ({product_format.taille})"
                )
            
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
        if 'status' in validated_data:
            instance.status = validated_data.get('status')
            instance.save()

        if 'items' in validated_data:
            items_data = validated_data.pop('items')
            
            # Supprimer les anciens items
            for item in instance.items.all():
                # Restaurer le stock
                item.product_format.stock += item.quantity
                item.product_format.save()
                item.delete()

            # Créer les nouveaux items
            for item_data in items_data:
                product_format = item_data['product_format']
                quantity = item_data['quantity']

                if quantity > product_format.stock:
                    raise serializers.ValidationError(
                        f"Stock insuffisant pour {product_format.product.name}"
                    )
                
                OrderItem.objects.create(
                    order=instance,
                    product_format=product_format,
                    quantity=quantity,
                    price_at_order=product_format.price
                )
                
                product_format.stock -= quantity
                product_format.save()

        return instance