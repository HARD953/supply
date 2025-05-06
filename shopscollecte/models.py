from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User
from shops.models import Shop
from parametres.models import Category, FrequenceApprovisionnement

class ProductCollecte(models.Model):
    owner = models.ForeignKey(User, related_name='shopscollecte', on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    stock = models.IntegerField(validators=[MinValueValidator(0)])
    frequence_appr = models.ForeignKey(FrequenceApprovisionnement, on_delete=models.SET_NULL, null=True, blank=True)
    reorder_frequency = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(365)],
        help_text="Fréquence de réapprovisionnement en jours (0-365)"
    )
    supplier = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Produit collecté"
        verbose_name_plural = "Produits collectés"
        indexes = [
            models.Index(fields=['owner']),
            models.Index(fields=['supplier']),
            models.Index(fields=['created_at']),
            models.Index(fields=['category']),
        ]