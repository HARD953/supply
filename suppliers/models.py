from django.db import models

class Supplier(models.Model):
    SUPPLIER_TYPES = [
        ('MANUFACTURER', 'Fabricant'),
        ('DISTRIBUTOR', 'Distributeur'),
        ('WHOLESALER', 'Grossiste'),
    ]
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=SUPPLIER_TYPES)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    average_delivery_time = models.IntegerField()  # in days
    order_frequency = models.CharField(max_length=100)
    commune = models.CharField(max_length=100, verbose_name="Commune")
    quartier = models.CharField(max_length=100, verbose_name="Quartier")
    zone = models.CharField(max_length=100, verbose_name="Zone")

    def __str__(self):
        return self.name