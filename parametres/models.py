from django.db import models
from django.core.validators import MinValueValidator

class Commune(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Commune"
        verbose_name_plural = "Communes"
        indexes = [models.Index(fields=['name'])]

class Quartier(models.Model):
    name = models.CharField(max_length=100)
    commune = models.ForeignKey(Commune, on_delete=models.CASCADE, related_name='quartiers')

    def __str__(self):
        return f"{self.name} ({self.commune.name})"

    class Meta:
        verbose_name = "Quartier"
        verbose_name_plural = "Quartiers"
        unique_together = ('name', 'commune')
        indexes = [models.Index(fields=['name', 'commune'])]

class Zone(models.Model):
    name = models.CharField(max_length=100)
    commune = models.ForeignKey(Commune, on_delete=models.CASCADE, related_name='zones', null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Zone"
        verbose_name_plural = "Zones"
        indexes = [models.Index(fields=['name'])]

class UserType(models.Model):
    name = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Type d'utilisateur"
        verbose_name_plural = "Types d'utilisateurs"
        indexes = [models.Index(fields=['name'])]

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='categorie/', blank=True, null=True)
    app = models.CharField(max_length=50, blank=True, null=True)  # Ex: "products", "collecte"

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        indexes = [models.Index(fields=['name', 'app'])]

class Certification(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Certification"
        verbose_name_plural = "Certifications"
        indexes = [models.Index(fields=['name'])]

class ShopType(models.Model):
    name = models.CharField(max_length=20, unique=True)
    code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Type de boutique"
        verbose_name_plural = "Types de boutiques"
        indexes = [models.Index(fields=['name', 'code'])]

class TypeCommerce(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Type de commerce"
        verbose_name_plural = "Types de commerce"
        indexes = [models.Index(fields=['name'])]

class TailleShop(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Taille de boutique"
        verbose_name_plural = "Tailles de boutiques"
        indexes = [models.Index(fields=['name'])]

class FrequenceApprovisionnement(models.Model):
    name = models.CharField(max_length=100, unique=True)
    days = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(0)])

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Fréquence d'approvisionnement"
        verbose_name_plural = "Fréquences d'approvisionnement"
        indexes = [models.Index(fields=['name'])]

class OrderStatus(models.Model):
    name = models.CharField(max_length=20, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Statut de commande"
        verbose_name_plural = "Statuts de commande"
        indexes = [models.Index(fields=['name', 'code'])]

class Taille(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Taille"
        verbose_name_plural = "Tailles"
        indexes = [models.Index(fields=['name'])]

class Couleur(models.Model):
    name = models.CharField(max_length=100, unique=True)
    hex_code = models.CharField(max_length=7, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Couleur"
        verbose_name_plural = "Couleurs"
        indexes = [models.Index(fields=['name'])]

class Module(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50)
    link = models.CharField(max_length=50)
    color = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Module"
        verbose_name_plural = "Modules"
        indexes = [models.Index(fields=['name'])]

