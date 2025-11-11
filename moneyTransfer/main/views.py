from django.forms import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Sum
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import MoneyTransfer, Category, OperationType, Status, Subcategory
from .forms import CategoryForm, MoneyTransferForm, StatusForm, SubcategoryForm, TypeForm

def login_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user=user)
            return redirect("index")
    return render(request, "main/login.html")

def logout_user(request):
    logout(request)
    return redirect("login")

def register_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")
        
        if not username or not password or not email:
            messages.error(request, "Все поля обязательны для заполнения")
            return render(request, "main/register_form.html")
        
    
        if User.objects.filter(username=username).exists():
            messages.error(request, "Пользователь с таким именем уже существует")
            return render(request, "main/register_form.html")
        
        try:
            User.objects.create_user(
                username=username,
                password=password,
                email=email
            )
            messages.success(request, "Пользователь успешно создан! Теперь вы можете войти.")
            return redirect("login")
        except Exception as e:
            messages.error(request, f"Ошибка при создании пользователя: {str(e)}")
    
    return render(request, "main/register_form.html")
def get_paginated_queryset(request, queryset, prefix='', default_per_page=5):

    per_page = int(request.GET.get(f'{prefix}per_page', default_per_page))
    page_number = request.GET.get(f'{prefix}page', 1)
    
    paginator = Paginator(queryset, per_page)
    
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    
    return page


def apply_transfer_filters(queryset, filters):
    if filters.get('category'):
        queryset = queryset.filter(category_id=filters['category'])
    
    if filters.get('subcategory'):
        queryset = queryset.filter(subcategory_id=filters['subcategory'])
    
    if filters.get('status'):
        queryset = queryset.filter(status_id=filters['status'])
    
    if filters.get('type'):
        queryset = queryset.filter(type_id=filters['type'])
    
    if filters.get('date_from'):
        queryset = queryset.filter(date_add__date__gte=filters['date_from'])
    
    if filters.get('date_to'):
        queryset = queryset.filter(date_add__date__lte=filters['date_to'])

    sum_order = filters.get('sum_order')
    if sum_order == "asc":
        queryset = queryset.order_by('summ')
    elif sum_order == 'desc':
        queryset = queryset.order_by('-summ')
    else:
        queryset = queryset.order_by('-date_add')
    
    return queryset


def get_transfer_filters(request):
    filters = {
        'category': request.GET.get('category', ''),
        'subcategory': request.GET.get('subcategory', ''),
        'status': request.GET.get('status', ''),
        'type': request.GET.get('type', ''),
        'date_from': request.GET.get('date_from', ''),
        'date_to': request.GET.get('date_to', ''),
        'sum_order': request.GET.get('sum_order', ''),
    }
    return filters

@login_required
def index(request):
    transfers = MoneyTransfer.objects.select_related(
        'category', 
        'subcategory', 
        'type', 
        'status'
    ).filter(user=request.user)
    
    current_filters = get_transfer_filters(request)

    transfers = apply_transfer_filters(transfers, current_filters)

    total = transfers.aggregate(total=Sum('summ'))['total'] or 0
    if current_filters is None:
        transfers = transfers.order_by('-date_add')
    
    per_page = int(request.GET.get('per_page', 10))
    if per_page not in [10, 25, 50, 100]: per_page = 10
    
    paginator = Paginator(transfers, per_page)
    page_number = request.GET.get('page', 1)
    
    transfers_page = paginator.page(page_number)
    
    categories = Category.objects.filter(user=request.user) 
    subcategories = Subcategory.objects.filter(user=request.user) 
    status_choices = Status.objects.filter(user=request.user) 
    type_choices = OperationType.objects.filter(user=request.user) 

    sum_order_choices = [
        {'value': '', 'display': 'По дате (новые)'},
        {'value': 'asc', 'display': 'По сумме (по возрастанию)'},
        {'value': 'desc', 'display': 'По сумме (по убыванию)'},
    ]
    context = {
        'tab': 'transfers',
        'transfers': transfers_page,
        'categories': categories,
        'subcategories': subcategories,
        'status_choices': status_choices,
        'type_choices': type_choices,
        'current_filters': current_filters,
        'total': total,
        'sum_order_choices': sum_order_choices,
    }
    
    return render(request, "main/index.html", context)

@login_required
def transfer_add(request):
    if request.method == 'POST':
        form = MoneyTransferForm(request.POST)
        
        if form.is_valid():
            try:
                transfer = form.save(commit=False)
                transfer.user = request.user
                transfer.full_clean()
                transfer.save()
                return redirect('index')
            except ValidationError as e:
                for field, messages in e.message_dict.items():
                    for msg in messages:
                        form.add_error(field, msg)
    else:
        form = MoneyTransferForm()
        form.fields['category'].queryset = Category.objects.filter(user=request.user)
        form.fields['subcategory'].queryset = Subcategory.objects.filter(user=request.user)
        form.fields['type'].queryset = OperationType.objects.filter(user=request.user)
        form.fields['status'].queryset = Status.objects.filter(user=request.user)
    
    context = {
        'form': form,
        'page_title': 'Новый перевод',
    }
    
    return render(request, 'main/moneytransfer_form.html', context)

@login_required
def transfer_update(request, pk):
    transfer = get_object_or_404(MoneyTransfer, pk=pk)
    
    if request.method == 'POST':
        form = MoneyTransferForm(request.POST, instance=transfer)
        
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = MoneyTransferForm(instance=transfer)
        form.fields['category'].queryset = Category.objects.filter(user=request.user)
        form.fields['subcategory'].queryset = Subcategory.objects.filter(user=request.user)
        form.fields['type'].queryset = OperationType.objects.filter(user=request.user)
        form.fields['status'].queryset = Status.objects.filter(user=request.user)
    
    context = {
        'form': form,
        'transfer': transfer,
        'page_title': f'Редактирование перевода #{transfer.id}',
    }
    
    return render(request, 'main/moneytransfer_form.html', context)

@login_required
def transfer_delete(request, pk):
    transfer = get_object_or_404(MoneyTransfer, pk=pk)
    
    if request.method == 'POST':
        transfer.delete()
        return redirect('index')
    
    return redirect('index')

@login_required
def reference(request):
    categories_queryset = Category.objects.prefetch_related('subcategories').filter(user=request.user) 
    subcategories_queryset = Subcategory.objects.select_related('category').filter(user=request.user) 
    statuses_queryset = Status.objects.filter(user=request.user) 
    types_queryset = OperationType.objects.filter(user=request.user) 
    
    categories_page = get_paginated_queryset(request, categories_queryset, 'cat_', 5)
    subcategories_page = get_paginated_queryset(request, subcategories_queryset, 'sub_', 5)
    statuses_page = get_paginated_queryset(request, statuses_queryset, 'stat_', 5)
    types_page = get_paginated_queryset(request, types_queryset, 'type_', 5)
    
    context = {
        'tab': 'reference',
        'categories': categories_page,
        'subcategories': subcategories_page,
        'statuses': statuses_page,
        'types': types_page,
    }
    
    return render(request, "main/reference.html", context)

@login_required
def reference_add(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_status':
            form = StatusForm(request.POST)
            if form.is_valid():
                status = form.save(commit=False)
                status.user = request.user
                status.save()
        
        elif action == 'add_type':
            form = TypeForm(request.POST)
            if form.is_valid():
                operation_type = form.save(commit=False)
                operation_type.user = request.user
                operation_type.save()
        
        elif action == 'add_category':
            form = CategoryForm(request.POST)
            if form.is_valid():
                category = form.save(commit=False)
                category.user = request.user
                category.save()
        
        elif action == 'add_subcategory':
            form = SubcategoryForm(request.POST)
            if form.is_valid():
                subcategory = form.save(commit=False)
                subcategory.user = request.user
                subcategory.save()
        
        return redirect('reference_add')
    
    status_form = StatusForm()
    type_form = TypeForm()
    category_form = CategoryForm()
    subcategory_form = SubcategoryForm()

    subcategory_form.fields['category'].queryset = Category.objects.filter(user=request.user)

    status_list = Status.objects.filter(user=request.user).order_by('name')
    type_list = OperationType.objects.filter(user=request.user).order_by('name')
    categories = Category.objects.filter(user=request.user) 
    subcategories = Subcategory.objects.filter(user=request.user) 
    
    context = {
        'status_form': status_form,
        'type_form': type_form,
        'category_form': category_form,
        'subcategory_form': subcategory_form,
        'status_list': status_list,
        'type_list': type_list,
        'status_count': status_list.count(),
        'type_count': type_list.count(),
        'category_count': categories.count(),
        'subcategory_count': subcategories.count(),
        'page_title': 'Справочник',
    }
    
    return render(request, 'main/reference_add.html', context)

@login_required
def status_edit(request, pk):
    status = get_object_or_404(Status, pk=pk)
    
    if request.method == 'POST':
        form = StatusForm(request.POST, instance=status)
        
        if form.is_valid():
            form.save()
            return redirect('reference')
    else:
        form = StatusForm(instance=status)
    
    context = {
        'form': form,
        'object': status,
        'object_type': 'статус',
        'form_type': 'status',
        'page_title': f'Редактирование статуса: {status.name}',
    }
    
    return render(request, 'main/reference_edit.html', context)

@login_required
def status_delete(request, pk):
    status = get_object_or_404(Status, pk=pk)
    
    if request.method == 'GET':
        status.delete()
    
    referer = request.META.get('HTTP_REFERER', 'reference')
    return redirect(referer)

@login_required
def type_edit(request, pk):
    type_obj = get_object_or_404(OperationType, pk=pk)
    
    if request.method == 'POST':
        form = TypeForm(request.POST, instance=type_obj)
        
        if form.is_valid():
            form.save()
            return redirect('reference')
    else:
        form = TypeForm(instance=type_obj)
    
    context = {
        'form': form,
        'object': type_obj,
        'object_type': 'тип операции',
        'form_type': 'type',
        'page_title': f'Редактирование типа: {type_obj.name}',
    }
    
    return render(request, 'main/reference_edit.html', context)

@login_required
def type_delete(request, pk):
    type_obj = get_object_or_404(OperationType, pk=pk)
    
    if request.method == 'POST':
        type_obj.delete()
    
    referer = request.META.get('HTTP_REFERER', 'reference')
    return redirect(referer)

@login_required
def category_edit(request, pk):
    category = Category.objects.filter(pk=pk).first()
    
    if category:
        obj = category
        form_class = CategoryForm
        title = f'Редактировать категорию: {obj.name}'
    else:
        subcategory = Subcategory.objects.filter(pk=pk).first()
        
        if subcategory:
            obj = subcategory
            form_class = SubcategoryForm
            title = f'Редактировать подкатегорию: {obj.name}'
        else:
            return redirect('reference')
    
    if request.method == 'POST':
        form = form_class(request.POST, instance=obj)
        
        if form.is_valid():
            form.save()
            return redirect('reference')
    else:
        form = form_class(instance=obj)
        if form_class == SubcategoryForm:
            form.fields['category'].queryset = Category.objects.filter(user=request.user)
    
    context = {
        'form': form,
        'edit_object': obj,
        'page_title': title,
        'back_url': 'reference',
    }
    
    return render(request, 'main/category_form.html', context)

@login_required
def category_delete(request, pk):
    obj = Category.objects.filter(pk=pk).first()
    
    if not obj:
        obj = Subcategory.objects.filter(pk=pk).first()
    
    if not obj:
        return redirect('reference')
    
    obj.delete()
    
    referer = request.META.get('HTTP_REFERER', 'reference')
    return redirect(referer)
