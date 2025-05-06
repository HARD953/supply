from django.contrib import admin
from .models import (
    Commune, Quartier, Zone, UserType, Category, Certification,
    ShopType, TypeCommerce, TailleShop, FrequenceApprovisionnement,
    OrderStatus, Taille, Couleur, Module
)

@admin.register(Commune)
class CommuneAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

@admin.register(Quartier)
class QuartierAdmin(admin.ModelAdmin):
    list_display = ('name', 'commune')
    list_filter = ('commune',)
    search_fields = ('name',)

@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'commune')
    list_filter = ('commune',)
    search_fields = ('name',)

@admin.register(UserType)
class UserTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'app', 'description')
    list_filter = ('app',)
    search_fields = ('name',)

@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(ShopType)
class ShopTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

@admin.register(TypeCommerce)
class TypeCommerceAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(TailleShop)
class TailleShopAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(FrequenceApprovisionnement)
class FrequenceApprovisionnementAdmin(admin.ModelAdmin):
    list_display = ('name', 'days')
    search_fields = ('name',)

@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'description')
    search_fields = ('name', 'code')

@admin.register(Taille)
class TailleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Couleur)
class CouleurAdmin(admin.ModelAdmin):
    list_display = ('name', 'hex_code')
    search_fields = ('name', 'hex_code')

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'link', 'color')
    search_fields = ('name',)

