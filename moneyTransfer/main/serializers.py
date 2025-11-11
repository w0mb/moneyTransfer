from rest_framework import serializers
from .models import MoneyTransfer, Category, Subcategory

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'type']

class SubcategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Subcategory
        fields = ['id', 'name', 'category', 'category_name']

class MoneyTransferSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    subcategory_name = serializers.CharField(source='subcategory.name', read_only=True)
    
    class Meta:
        model = MoneyTransfer
        fields = [
            'id', 'date_add', 'date_operation', 'status', 'type', 
            'category', 'category_name', 'subcategory', 'subcategory_name',
            'amount', 'comment'
        ]