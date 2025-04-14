from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User, Module4, ModulePermission4

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'user_type', 'phone_number', 'commune', 'quartier', 'zone',
            'latitude', 'longitude', 'user_name', 'company_name', 'company_tax_id', 'website',
            'contact_person', 'business_address', 'image', 'registre', 'date_creation',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'username', 'password', 'email', 'user_type', 'phone_number', 'user_name',
            'company_name', 'company_tax_id', 'website', 'contact_person', 'business_address',
            'image', 'registre', 'date_creation', 'commune', 'quartier', 'zone', 'latitude',
            'longitude'
        ]

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.pop('password'))
        return super().create(validated_data)

class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module4
        fields = "__all__"

class PermissionSerializer(serializers.ModelSerializer):
    module = serializers.SlugRelatedField(slug_field='name', queryset=Module4.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = ModulePermission4
        fields = ['id', 'module', 'user', 'can_create', 'can_read', 'can_update', 'can_delete']

    def create(self, validated_data):
        module_name = validated_data.pop('module')
        user = validated_data.pop('user')
        
        try:
            module = Module4.objects.get(name=module_name)
        except Module4.DoesNotExist:
            raise serializers.ValidationError("Module does not exist.")

        return ModulePermission4.objects.create(
            module=module,
            user=user,
            **validated_data
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = instance.user.email
        return representation
    
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

class CurrentUserSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'user_type', 'phone_number', 'commune', 'quartier', 'zone',
            'latitude', 'longitude', 'user_name', 'company_name', 'company_tax_id', 'website',
            'contact_person', 'business_address', 'image', 'registre', 'date_creation',
            'created_at', 'updated_at', 'permissions'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_permissions(self, obj):
        # if obj.is_superuser:
        #     modules = Module4.objects.all()
        #     return [
        #         {
        #             'module': module.name,
        #             'can_create': True,
        #             'can_read': True,
        #             'can_update': True,
        #             'can_delete': True
        #         }
        #         for module in modules
        #     ]
        
        permissions = ModulePermission4.objects.filter(user=obj)
        print(obj)
        return [
            {
                'module': perm.module.name,
                'can_create': perm.can_create,
                'can_read': perm.can_read,
                'can_update': perm.can_update,
                'can_delete': perm.can_delete
            }
            for perm in permissions
        ]