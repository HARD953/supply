from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User, ModulePermission
from parametres.models import Module, UserType, Commune, Quartier, Zone

# Sérialiseur principal pour les utilisateurs
class UserSerializer(serializers.ModelSerializer):
    user_type = serializers.CharField(source='user_type.name', read_only=True)
    user_type_id = serializers.PrimaryKeyRelatedField(
        queryset=UserType.objects.all(), source='user_type', write_only=True
    )
    commune = serializers.CharField(source='commune.name', read_only=True, allow_null=True)
    commune_id = serializers.PrimaryKeyRelatedField(
        queryset=Commune.objects.all(), source='commune', allow_null=True, write_only=True
    )
    quartier = serializers.CharField(source='quartier.name', read_only=True, allow_null=True)
    quartier_id = serializers.PrimaryKeyRelatedField(
        queryset=Quartier.objects.all(), source='quartier', allow_null=True, write_only=True
    )
    zone = serializers.CharField(source='zone.name', read_only=True, allow_null=True)
    zone_id = serializers.PrimaryKeyRelatedField(
        queryset=Zone.objects.all(), source='zone', allow_null=True, write_only=True
    )

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'phone', 'gender',
            'user_type', 'user_type_id', 'commune', 'commune_id', 'quartier', 'quartier_id',
            'zone', 'zone_id', 'is_active', 'is_staff', 'created_at', 'updated_at',
            'company_name', 'date_creation', 'latitude', 'longitude', 'typecommerce'
        ]
        read_only_fields = ['created_at', 'updated_at', 'is_staff']

    def validate(self, data):
        quartier = data.get('quartier')
        commune = data.get('commune')
        if quartier and commune and quartier.commune != commune:
            raise serializers.ValidationError("Le quartier doit appartenir à la commune sélectionnée.")
        return data

# Sérialiseur pour l'enregistrement des utilisateurs
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    user_type = serializers.CharField(source='user_type.name', read_only=True)
    user_type_id = serializers.PrimaryKeyRelatedField(
        queryset=UserType.objects.all(), source='user_type', write_only=True
    )
    commune = serializers.CharField(source='commune.name', read_only=True, allow_null=True)
    commune_id = serializers.PrimaryKeyRelatedField(
        queryset=Commune.objects.all(), source='commune', allow_null=True, write_only=True
    )
    quartier = serializers.CharField(source='quartier.name', read_only=True, allow_null=True)
    quartier_id = serializers.PrimaryKeyRelatedField(
        queryset=Quartier.objects.all(), source='quartier', allow_null=True, write_only=True
    )
    zone = serializers.CharField(source='zone.name', read_only=True, allow_null=True)
    zone_id = serializers.PrimaryKeyRelatedField(
        queryset=Zone.objects.all(), source='zone', allow_null=True, write_only=True
    )

    class Meta:
        model = User
        fields = [
            'username', 'password', 'email', 'first_name', 'last_name', 'phone', 'gender',
            'user_type', 'user_type_id', 'commune', 'commune_id', 'quartier', 'quartier_id',
            'zone', 'zone_id', 'company_name', 'date_creation', 'latitude', 'longitude', 'typecommerce'
        ]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Cet email est déjà utilisé.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Ce nom d'utilisateur est déjà pris.")
        return value

    def validate(self, data):
        quartier = data.get('quartier')
        commune = data.get('commune')
        if quartier and commune and quartier.commune != commune:
            raise serializers.ValidationError("Le quartier doit appartenir à la commune sélectionnée.")
        return data

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.pop('password'))
        return User.objects.create(**validated_data)

# Sérialiseur pour l'utilisateur connecté
class CurrentUserSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()
    user_type = serializers.CharField(source='user_type.name', read_only=True)
    commune = serializers.CharField(source='commune.name', read_only=True, allow_null=True)
    quartier = serializers.CharField(source='quartier.name', read_only=True, allow_null=True)
    zone = serializers.CharField(source='zone.name', read_only=True, allow_null=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'phone', 'gender',
            'user_type', 'commune', 'quartier', 'zone', 'is_active', 'is_staff',
            'created_at', 'updated_at', 'permissions', 'company_name', 'date_creation',
            'latitude', 'longitude', 'typecommerce'
        ]
        read_only_fields = ['created_at', 'updated_at', 'is_staff', 'permissions']

    def get_permissions(self, obj):
        permissions = ModulePermission.objects.filter(user=obj).select_related('module')
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

# Le reste du code (ModulePermissionSerializer et UserViewSet) reste inchangé

class ModulePermissionSerializer(serializers.ModelSerializer):
    module = serializers.SlugRelatedField(slug_field='name', queryset=Module.objects.all())
    user = serializers.SlugRelatedField(slug_field='email', queryset=User.objects.all())

    class Meta:
        model = ModulePermission
        fields = ['id', 'module', 'user', 'can_create', 'can_read', 'can_update', 'can_delete']

    def create(self, validated_data):
        module_name = validated_data.pop('module')
        user_email = validated_data.pop('user')
        module = Module.objects.get(name=module_name)
        user = User.objects.get(username=user_email)
        return ModulePermission.objects.create(module=module, user=user, **validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['module'] = instance.module.name
        representation['user'] = instance.user.email
        return representation
    
class StatsSerializer(serializers.Serializer):
    overview = serializers.DictField()
    by_user_type = serializers.ListField()
    by_commune = serializers.ListField()
    by_commerce_type = serializers.ListField()

    class Meta:
        fields = ['overview', 'by_user_type', 'by_commune', 'by_commerce_type']

        