from rest_framework import permissions
from .models import ModulePermission4

class ModulePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        module_name = view.kwargs.get('module_name')  # Passé dans l'URL ou défini dans la vue

        if request.user.is_superuser:
            return True

        try:
            ModulePermission4 = ModulePermission4.objects.get(module__name=module_name, user=request.user)
            if request.method == 'POST':
                return ModulePermission4.can_create
            elif request.method == 'GET':
                return ModulePermission4.can_read
            elif request.method in ['PUT', 'PATCH']:
                return ModulePermission4.can_update
            elif request.method == 'DELETE':
                return ModulePermission4.can_delete
        except ModulePermission4.DoesNotExist:
            return False