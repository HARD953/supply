from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    user_type = models.CharField(max_length=20, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    commune = models.CharField(max_length=100, verbose_name="Commune", blank=True, null=True)
    quartier = models.CharField(max_length=100, verbose_name="Quartier", blank=True, null=True)
    zone = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    user_name = models.CharField(max_length=255, blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    company_tax_id = models.CharField(max_length=50, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    business_address = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='accounts_users/', blank=True, null=True)
    email = models.EmailField(unique=True)
    registre = models.CharField(max_length=100, blank=True, null=True)
    date_creation = models.CharField(max_length=15, blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

class Module4(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    icon=models.CharField(max_length=50)
    link=models.CharField(max_length=50)

    def __str__(self):
        return self.name

class ModulePermission4(models.Model):
    module = models.ForeignKey(Module4, on_delete=models.CASCADE, related_name='module_permissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='module_permission_assignments')
    can_create = models.BooleanField(default=False)
    can_read = models.BooleanField(default=False)
    can_update = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.module.name}"

    class Meta:
        unique_together = ('module', 'user')