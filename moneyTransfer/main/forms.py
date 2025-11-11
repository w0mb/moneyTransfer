from django import forms
from django.core.exceptions import ValidationError

from .models import MoneyTransfer, Category, OperationType, Status, Subcategory


class MoneyTransferForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = "Выберите категорию (или подкатегорию)"
        self.fields['subcategory'].empty_label = "Выберите подкатегорию"
        self.fields['type'].empty_label = "Выберите тип"
        self.fields['status'].empty_label = "Выберите статус"
    class Meta:
        model = MoneyTransfer
        fields = ['type', 'status', 'subcategory', 'category', 'summ', 'comment']
        
        widgets = {
            'type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'subcategory': forms.Select(attrs={'class': 'form-select'}),
            'summ': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Сумма'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Комментарий (необязательно)'
            }),
        }
        
        labels = {
            'type': 'Тип операции',
            'status': 'Статус',
            'category': 'Категория / Подкатегория',
            'summ': 'Сумма',
            'comment': 'Комментарий',
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Новая категория'
            })
        }


class StatusForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = ['name']
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Новый статус'
            })
        }


class TypeForm(forms.ModelForm):
    class Meta:
        model = OperationType
        fields = ['name']
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Новый тип'
            })
        }


class SubcategoryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['category'].empty_label = "— Выберите категорию (или подкатегорию) —"
    
    class Meta:
        model = Subcategory
        fields = ['category', 'name']
        
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Новая подкатегория'
            }),
        }
