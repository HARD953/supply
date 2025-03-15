from django.db import models
from django.core.validators import MinValueValidator
from accounts.models import User  # Assurez-vous d'importer votre modèle User
from suppliers.models import Supplier  # Assurez-vous d'importer votre modèle Supplier

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    supplier = models.ForeignKey(User, related_name='products', on_delete=models.PROTECT)
    last_order = models.DateField()

    def __str__(self):
        return self.name if self.name else "Produit sans nom"

class ProductFormat(models.Model):
    product = models.ForeignKey(Product, related_name='formats', on_delete=models.CASCADE)
    taille = models.CharField(max_length=100, null=True, blank=True)  # Ex: "M", "L", "XL"
    couleur = models.CharField(max_length=100, null=True, blank=True)  # Ex: "Rouge", "Bleu"
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    stock = models.IntegerField()
    min_stock = models.IntegerField()

    def __str__(self):
        return f"{self.product.name} - {self.taille} - {self.couleur}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('PROCESSING', 'En cours de traitement'),
        ('COMPLETED', 'Terminée'),
        ('CANCELLED', 'Annulée'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Commande #{self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_format = models.ForeignKey(ProductFormat, on_delete=models.PROTECT)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])  # Validation de la quantité
    price_at_order = models.DecimalField(max_digits=10, decimal_places=2)  # Prix au moment de la commande

    def __str__(self):
        return f"{self.quantity}x {self.product_format.product.name} ({self.product_format.taille})"