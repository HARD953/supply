# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    user_type = models.CharField(max_length=20, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    commune = models.CharField(max_length=100, verbose_name="Commune", blank=True, null=True)
    quartier = models.CharField(max_length=100, verbose_name="Quartier", blank=True, null=True)
    zone = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)  # Allow null
    longitude = models.FloatField(blank=True, null=True)  # Allow null
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