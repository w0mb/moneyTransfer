from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class Status(models.Model):
    name = models.TextField(max_length=255, verbose_name="Название")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    def __str__(self):
        return self.name
class OperationType(models.Model):
    name = models.TextField(max_length=255, verbose_name="Название")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    def __str__(self):
        return self.name
class MoneyTransfer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    date_add = models.DateTimeField(auto_now_add = True, verbose_name = "Время создания записи")
    status = models.ForeignKey("Status", verbose_name="Статус", on_delete=models.PROTECT)
    type = models.ForeignKey("OperationType", verbose_name="Тип", on_delete=models.PROTECT)
    category = models.ForeignKey("Category", on_delete=models.PROTECT, verbose_name="Категория")
    subcategory = models.ForeignKey("Subcategory", on_delete=models.PROTECT, verbose_name="Подкатегория")
    summ = models.IntegerField(verbose_name="Сумма")
    comment = models.TextField(max_length=255, blank=True, verbose_name="Комментарий")

    def clean(self):
        if self.subcategory and self.category:
            if self.subcategory.category != self.category:
                raise ValidationError({
                    'subcategory': 'Подкатегория должна принадлежать выбранной категории.'
                })
        elif self.subcategory and not self.category:
            raise ValidationError({
                'category': 'Сначала выберите категорию.'
            })

    def save(self, *args, **kwargs):
        self.clean()  # важно вызвать clean перед сохранением
        super().save(*args, **kwargs)
    

class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    name = models.CharField(max_length=100, verbose_name="Название категории")
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
    
    def __str__(self):
        return self.name
class test(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")

    def __str__(self):
        return self.name
class Subcategory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    category = models.ForeignKey(Category, 
        on_delete=models.CASCADE, 
        related_name='subcategories',
        verbose_name="Категория"
    )

    name = models.CharField(max_length=100, verbose_name="Название подкатегории")
    
    class Meta:
        verbose_name = "Подкатегория"
        verbose_name_plural = "Подкатегории"
        unique_together = ['category', 'name']
    
    def __str__(self):
        return f"{self.name}"
    

