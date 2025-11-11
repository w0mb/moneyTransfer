import django_filters
from .models import MoneyTransfer

class MoneyTransferFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name='date_add', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='date_add', lookup_expr='lte')
    
    class Meta:
        model = MoneyTransfer
        fields = {
            'category': ['exact'],
            'subcategory': ['exact'],
            'status': ['exact'],
            'type': ['exact'],
        }