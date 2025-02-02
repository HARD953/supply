from django.db import models

class Shop(models.Model):
    SHOP_TYPES = [
        ('BRANDED', 'Brandée'),
        ('NON_BRANDED', 'Non brandée'),
    ]
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='shops/')
    type = models.CharField(max_length=20, choices=SHOP_TYPES)
    typecommerce = models.CharField(max_length=20, choices=SHOP_TYPES)
    brand = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    owner_name = models.CharField(max_length=100)
    owner_gender = models.CharField(max_length=10)
    owner_phone = models.CharField(max_length=15)
    owner_email = models.EmailField()

    def __str__(self):
        return self.name