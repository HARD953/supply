# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPES = [
        ('WHOLESALER', 'Grossiste'),
        ('SEMI_WHOLESALER', 'Semi-grossiste'),
        ('RETAILER', 'Détaillant'),
    ]
    
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    user_name = models.CharField(max_length=255, blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    company_tax_id = models.CharField(max_length=50, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    business_address = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='accounts_users/')

    def __str__(self):
        return self.username 