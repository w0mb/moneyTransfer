from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from .models import Status, OperationType, Category, Subcategory, MoneyTransfer


class SubcategoryInline(admin.TabularInline):
    """Inline для отображения подкатегорий внутри категории"""
    model = Subcategory
    extra = 1
    fields = ['name']
    verbose_name = "Подкатегория"
    verbose_name_plural = "Подкатегории"


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    """Админка для статусов"""
    list_display = ['id', 'name', 'moneytransfers_count']
    list_display_links = ['id', 'name']
    search_fields = ['name']
    ordering = ['name']
    
    def moneytransfers_count(self, obj):
        return obj.moneytransfer_set.count()
    moneytransfers_count.short_description = 'Кол-во переводов'


@admin.register(OperationType)
class OperationTypeAdmin(admin.ModelAdmin):
    """Админка для типов операций"""
    list_display = ['id', 'name', 'moneytransfers_count']
    list_display_links = ['id', 'name']
    search_fields = ['name']
    ordering = ['name']
    
    def moneytransfers_count(self, obj):
        return obj.moneytransfer_set.count()
    moneytransfers_count.short_description = 'Кол-во переводов'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Админка для категорий"""
    list_display = ['id', 'name', 'subcategories_count', 'moneytransfers_count']
    list_display_links = ['id', 'name']
    search_fields = ['name']
    ordering = ['name']
    inlines = [SubcategoryInline]
    
    def subcategories_count(self, obj):
        return obj.subcategories.count()
    subcategories_count.short_description = 'Подкатегорий'
    
    def moneytransfers_count(self, obj):
        return MoneyTransfer.objects.filter(category=obj).count()
    moneytransfers_count.short_description = 'Переводов'


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    """Админка для подкатегорий"""
    list_display = ['id', 'name', 'category', 'moneytransfers_count']
    list_display_links = ['id', 'name']
    list_filter = ['category']
    search_fields = ['name', 'category__name']
    ordering = ['category__name', 'name']
    
    def moneytransfers_count(self, obj):
        return obj.moneytransfer_set.count()
    moneytransfers_count.short_description = 'Переводов'


class MoneyTransferForm(forms.ModelForm):
    """Форма для валидации денежных переводов в админке"""
    class Meta:
        model = MoneyTransfer
        fields = '__all__'
    
    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        subcategory = cleaned_data.get('subcategory')
        
        # Проверяем, что подкатегория принадлежит выбранной категории
        if subcategory and category:
            if subcategory.category != category:
                raise ValidationError({
                    'subcategory': 'Выбранная подкатегория не принадлежит выбранной категории.'
                })
        
        return cleaned_data


@admin.register(MoneyTransfer)
class MoneyTransferAdmin(admin.ModelAdmin):
    """Админка для денежных переводов"""
    form = MoneyTransferForm
    
    list_display = [
        'id',
        'date_add_display',
        'status',
        'type',
        'category_display',
        'subcategory_display',
        'summ_display',
        'comment_preview'
    ]
    
    list_display_links = ['id', 'date_add_display']
    
    list_filter = [
        'status',
        'type',
        'category',
        'subcategory',
        'date_add'
    ]
    
    search_fields = [
        'comment',
        'category__name',
        'subcategory__name',
        'status__name',
        'type__name'
    ]
    
    date_hierarchy = 'date_add'
    ordering = ['-date_add']
    list_per_page = 25
    
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'date_add',
                'type',
                'status', 
                'summ'
            )
        }),
        ('Категории', {
            'fields': ('category', 'subcategory'),
            'description': 'Выберите категорию и соответствующую подкатегорию'
        }),
        ('Дополнительно', {
            'fields': ('comment',),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['date_add']
    
    # Кастомные методы для отображения
    def date_add_display(self, obj):
        return obj.date_add.strftime('%d.%m.%Y %H:%M')
    date_add_display.short_description = 'Дата создания'
    date_add_display.admin_order_field = 'date_add'
    
    def category_display(self, obj):
        return obj.category.name
    category_display.short_description = 'Категория'
    category_display.admin_order_field = 'category__name'
    
    def subcategory_display(self, obj):
        return obj.subcategory.name
    subcategory_display.short_description = 'Подкатегория'
    subcategory_display.admin_order_field = 'subcategory__name'
    
    def summ_display(self, obj):
        return f"{obj.summ} руб."
    summ_display.short_description = 'Сумма'
    summ_display.admin_order_field = 'summ'
    
    def comment_preview(self, obj):
        if obj.comment:
            return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
        return '-'
    comment_preview.short_description = 'Комментарий'
    
    # Действия для админки
    actions = ['mark_as_business', 'mark_as_personal']
    
    def mark_as_business(self, request, queryset):
        """Пометить выбранные переводы как бизнес"""
        business_status = Status.objects.get(name='Бизнес')
        updated = queryset.update(status=business_status)
        self.message_user(request, f'{updated} переводов помечены как "Бизнес"')
    mark_as_business.short_description = 'Пометить как "Бизнес"'
    
    def mark_as_personal(self, request, queryset):
        """Пометить выбранные переводы как личные"""
        personal_status = Status.objects.get(name='Личное')
        updated = queryset.update(status=personal_status)
        self.message_user(request, f'{updated} переводов помечены как "Личное"')
    mark_as_personal.short_description = 'Пометить как "Личное"'


# Настройка заголовков админки
admin.site.site_header = "💰 Управление денежными переводами"
admin.site.site_title = "Money Transfer Admin"
admin.site.index_title = "Панель управления"