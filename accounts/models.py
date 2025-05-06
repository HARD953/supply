from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import MinLengthValidator
from parametres.models import UserType, Commune, Quartier, Zone, Module,TypeCommerce

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not username:
            raise ValueError('The Username field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', UserType.objects.get_or_create(name='Admin')[0])

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True, validators=[MinLengthValidator(3)])
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    gender = models.CharField(max_length=10, blank=True)
    user_type = models.ForeignKey(UserType, on_delete=models.PROTECT, related_name='users')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    date_creation = models.DateField(blank=True, null=True)  # Changé en DateField
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    commune = models.ForeignKey(Commune, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    quartier = models.ForeignKey(Quartier, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    zone = models.ForeignKey(Zone, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    typecommerce = models.ForeignKey(TypeCommerce, on_delete=models.SET_NULL, null=True, blank=True)
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['created_at']),
            models.Index(fields=['user_type']),
            models.Index(fields=['commune']),
            models.Index(fields=['quartier']),
        ]

class ModulePermission(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='module_permissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='module_permission_assignments')
    can_create = models.BooleanField(default=False)
    can_read = models.BooleanField(default=False)
    can_update = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.module.name}"

    class Meta:
        verbose_name = "Permission de module"
        verbose_name_plural = "Permissions de modules"
        constraints = [
            models.UniqueConstraint(fields=['module', 'user'], name='unique_module_user_permission')
        ]
        indexes = [models.Index(fields=['module', 'user'])]