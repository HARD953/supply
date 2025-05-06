from django.db import models
from django.core.validators import MinValueValidator
from accounts.models import User
from parametres.models import ShopType, TypeCommerce, TailleShop, FrequenceApprovisionnement

class Shop(models.Model):
    owner = models.ForeignKey(User, related_name='shops', on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='shops/', blank=True, null=True)
    type = models.ForeignKey(ShopType, on_delete=models.PROTECT)
    typecommerce = models.ForeignKey(TypeCommerce, on_delete=models.SET_NULL, null=True, blank=True)
    taille = models.ForeignKey(TailleShop, on_delete=models.SET_NULL, null=True, blank=True)
    brand = models.CharField(max_length=100, blank=True, null=True)
    frequence_appr = models.ForeignKey(FrequenceApprovisionnement, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    owner_name = models.CharField(max_length=100)
    owner_gender = models.CharField(max_length=10)
    owner_phone = models.CharField(max_length=15)
    owner_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Boutique"
        verbose_name_plural = "Boutiques"
        indexes = [
            models.Index(fields=['owner']),
            models.Index(fields=['created_at']),
            models.Index(fields=['type']),
            models.Index(fields=['typecommerce']),
            models.Index(fields=['taille']),
        ]