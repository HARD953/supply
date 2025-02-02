from django.db import models

class SupplierCollecte(models.Model):
    SUPPLIER_TYPES = [
        ('WHOLESALER', 'Grossiste'),
        ('MANUFACTURER', 'Fabricant'),
        ('IMPORTER', 'Importateur'),
        ('LOCAL_DISTRIBUTOR', 'Distributeur local'),
        ('AGRICULTURAL_PRODUCER', 'Producteur agricole'),
    ]
    
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50, choices=SUPPLIER_TYPES)
    image = models.ImageField(upload_to='suppliers/', null=True, blank=True)
    delivery_time = models.IntegerField(help_text="Délai de livraison moyen en jours")
    order_frequency = models.CharField(max_length=100, help_text="Fréquence des commandes")

    def __str__(self):
        return self.name

class SupplierContact(models.Model):
    supplier = models.OneToOneField(SupplierCollecte, on_delete=models.CASCADE, related_name='contact')
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()

    def __str__(self):
        return f"Contact for {self.supplier.name}"