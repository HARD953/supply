from django.db import models
from django.core.validators import MinValueValidator
from accounts.models import User
from parametres.models import Category, OrderStatus, Taille, Couleur

class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    supplier = models.ForeignKey(User, related_name='products', on_delete=models.PROTECT)
    last_order = models.DateField()
    image = models.ImageField(upload_to='products/', blank=True, null=True)

    def __str__(self):
        return self.name if self.name else "Produit sans nom"

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['supplier']),
            models.Index(fields=['last_order']),
        ]

class ProductFormat(models.Model):
    product = models.ForeignKey(Product, related_name='formats', on_delete=models.CASCADE)
    taille = models.ForeignKey(Taille, on_delete=models.SET_NULL, null=True, blank=True, related_name='product_formats')
    couleur = models.ForeignKey(Couleur, on_delete=models.SET_NULL, null=True, blank=True, related_name='product_formats')
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    stock = models.IntegerField(validators=[MinValueValidator(0)])
    min_stock = models.IntegerField(validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.product.name} - {self.taille.name if self.taille else 'N/A'} - {self.couleur.name if self.couleur else 'N/A'}"

    class Meta:
        verbose_name = "Format de produit"
        verbose_name_plural = "Formats de produits"
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['taille']),
            models.Index(fields=['couleur']),
        ]

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.ForeignKey(OrderStatus, on_delete=models.PROTECT, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Commande #{self.id} - {self.user.username}"

    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_format = models.ForeignKey(ProductFormat, on_delete=models.PROTECT, related_name='order_items')
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    price_at_order = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.quantity}x {self.product_format.product.name} ({self.product_format.taille.name if self.product_format.taille else 'N/A'})"

    class Meta:
        verbose_name = "Article de commande"
        verbose_name_plural = "Articles de commande"
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['product_format']),
        ]