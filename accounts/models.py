# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPES = [
        ('WHOLESALER', 'Grossiste'),
        ('SEMI_WHOLESALER', 'Semi-grossiste'),
        ('RETAILER', 'Détaillant'),
        ('All', 'All')
    ]
    
    user_type = models.CharField(max_length=20, choices=USER_TYPES)

    phone_number = models.CharField(max_length=15)
    commune = models.CharField(max_length=100, verbose_name="Commune")
    quartier = models.CharField(max_length=100, verbose_name="Quartier")
    zone = models.CharField(max_length=100, verbose_name="Zone")
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.TextField()
    user_name = models.CharField(max_length=255, blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    company_tax_id = models.CharField(max_length=50, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    # Supprimer la redéfinition du champ email ici, car il existe déjà dans AbstractUser
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    business_address = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='accounts_users/')
    email = models.EmailField(unique=True)
    registre = models.CharField(max_length=100)
    date_creation = models.CharField(max_length=15)
    USERNAME_FIELD = 'email'
    # Définir explicitement REQUIRED_FIELDS sans email
    REQUIRED_FIELDS = ['username']  # username est requis car AbstractUser l'exige

    def __str__(self):
        return self.username