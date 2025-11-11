from django.urls import path
from . import views

urlpatterns = [
    # Главная страница - просмотр переводов
    path("", views.index, name="index"),
    
    # Переводы
    path('transfer/add/', views.transfer_add, name='transfer_add'),
    path('transfer/update/<int:pk>/', views.transfer_update, name='transfer_update'),
    path('transfer/delete/<int:pk>/', views.transfer_delete, name='transfer_delete'),
    
    # Справочник
    path('reference/', views.reference, name='reference'),
    path('reference/add/', views.reference_add, name='reference_add'),
    
    # Редактирование справочной информации
    path('status/edit/<int:pk>/', views.status_edit, name='status_edit'),
    path('status/delete/<int:pk>/', views.status_delete, name='status_delete'),
    path('type/edit/<int:pk>/', views.type_edit, name='type_edit'),
    path('type/delete/<int:pk>/', views.type_delete, name='type_delete'),
    path('category/edit/<int:pk>/', views.category_edit, name='category_edit'),
    path('category/delete/<int:pk>/', views.category_delete, name='category_delete'),

    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path("register/", views.register_user, name="register"),

]