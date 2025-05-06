from django.db.models import Q
from .models import User
from rest_framework.exceptions import ValidationError

class DynamicUserFilter:
    def __init__(self, queryset=None):
        self.queryset = queryset or User.objects.all().select_related('user_type', 'commune', 'quartier', 'zone')
        self.filter_fields = {
            'username': 'username__icontains',
            'email': 'email__icontains',
            'user_type': 'user_type__id',
            'commune': 'commune__id',
            'quartier': 'quartier__id',
            'zone': 'zone__id',
            'is_active': 'is_active',
        }

    def apply_filters(self, filter_data):
        """
        Apply dynamic filters based on POST data.
        Args:
            filter_data (dict): Dictionary of filter parameters from POST request.
        Returns:
            QuerySet: Filtered queryset.
        """
        if not filter_data:
            return self.queryset

        query = Q()
        for key, value in filter_data.items():
            if key in self.filter_fields and value:
                try:
                    if key == 'is_active':
                        # Convert string 'true'/'false' to boolean
                        if value.lower() in ['true', 'false']:
                            value = value.lower() == 'true'
                        else:
                            raise ValidationError(f"Invalid value for is_active: {value}")
                    # Construct Q object for the filter
                    query &= Q(**{self.filter_fields[key]: value})
                except (ValueError, TypeError) as e:
                    raise ValidationError(f"Invalid value for {key}: {str(e)}")

        try:
            return self.queryset.filter(query)
        except Exception as e:
            raise ValidationError(f"Error applying filters: {str(e)}")