from django.db import models
from django.core.validators import MinValueValidator
from shops.models import Shop
from accounts.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Certification(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    owner = models.ForeignKey(User, related_name='Shopscollecte', on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    stock = models.IntegerField(validators=[MinValueValidator(0)])
    frequence_appr = models.CharField(max_length=100, blank=True, null=True)
    reorder_frequency = models.IntegerField(validators=[MinValueValidator(0)], help_text="Fréquence de réapprovisionnement en jours")
    supplier = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="Fournisseur"
    )

    def __str__(self):
        return self.name

# class Product(models.Model):
#     name = models.CharField(max_length=100)
#     category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
#     price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
#     image = models.ImageField(upload_to='products/', null=True, blank=True)
#     stock = models.IntegerField(validators=[MinValueValidator(0)])
#     reorder_frequency = models.IntegerField(validators=[MinValueValidator(0)], help_text="Fréquence de réapprovisionnement en jours")
#     certifications = models.ManyToManyField(Certification, related_name='products', blank=True)

#     def __str__(self):
#         return self.name