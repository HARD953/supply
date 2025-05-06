from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(User)
@admin.register(ModulePermission)
class ModulePermissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'module', 'can_create', 'can_read', 'can_update', 'can_delete')
    list_filter = ('module', 'can_create', 'can_read', 'can_update', 'can_delete')
    search_fields = ('user__username', 'module__name')