from django.db import models
from accounts.models import User

class Shop(models.Model):
    owner = models.ForeignKey(User, related_name='Shop', on_delete=models.PROTECT)
    SHOP_TYPES = [
        ('BRANDED', 'Brandée'),
        ('NON_BRANDED', 'Non brandée'),
    ]
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='shops/')
    type = models.CharField(max_length=20, choices=SHOP_TYPES)
    typecommerce = models.CharField(max_length=20, blank=True)
    categorie = models.CharField(max_length=20, blank=True)
    taille = models.CharField(max_length=20, blank=True)
    brand = models.CharField(max_length=100, blank=True, null=True)
    frequence_appr = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    owner_name = models.CharField(max_length=100)
    owner_gender = models.CharField(max_length=10)
    owner_phone = models.CharField(max_length=15)
    owner_email = models.EmailField()

    def __str__(self):
        return self.name