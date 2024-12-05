# store/views.py
from django.contrib.auth import login
from .forms import RegisterForm
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProductForm, OrderForm, ProfileForm, AvatarForm
from .models import Product, Order, CartItem, Cart, UserProfile, OrderItem
from .decorators import role_required
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import user_passes_test, login_required
from django.http import HttpResponse
from matplotlib import pyplot as plt
from io import BytesIO
from django.core.mail import send_mail
from django.contrib import messages
from django.shortcuts import render, redirect
from django.db.models import Sum
import random
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

@login_required
def personal_info(request):
    # Проверяем, является ли пользователь администратором или менеджером
    is_admin = request.user.is_superuser
    is_manager = request.user.groups.filter(name='manager').exists()

    # Инициализируем формы
    password_form = PasswordChangeForm(request.user)
    profile_form = None

    if request.method == 'POST':
        # Определяем, какая форма была отправлена
        if 'password_form' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Обновляем сессию
                messages.success(request, 'Ваш пароль успешно изменён!')
                return redirect('Game_Territory:personal_info')
            else:
                messages.error(request, 'Пожалуйста, исправьте ошибки в форме смены пароля.')
        elif 'profile_form' in request.POST:
            # Обновляем имя, фамилию и email
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            email = request.POST.get('email', '').strip()

            if first_name and last_name and email:
                request.user.first_name = first_name
                request.user.last_name = last_name
                request.user.email = email
                request.user.save()
                messages.success(request, 'Личная информация успешно обновлена!')
                return redirect('Game_Territory:personal_info')
            else:
                messages.error(request, 'Пожалуйста, заполните все поля формы.')

    return render(request, 'Game_Territory/personal_info.html', {
        'password_form': password_form,
        'is_admin': is_admin,
        'is_manager': is_manager,
    })

@login_required
def my_orders(request):
    orders = Order.objects.filter(customer=request.user).prefetch_related('items__product')
    return render(request, 'Game_Territory/my_orders.html', {'orders': orders, 'active_tab': 'my_orders'})

@login_required
def admin_panel(request):
    # Проверяем, является ли пользователь администратором или менеджером
    is_admin = request.user.is_superuser
    is_manager = request.user.groups.filter(name='manager').exists()

    if not is_admin and not is_manager:
        # Если пользователь не администратор и не менеджер, редирект на профиль
        return redirect('Game_Territory:profile')

    return render(request, 'Game_Territory/admin_panel.html', {
        'is_admin': is_admin,
        'is_manager': is_manager,
        'active_tab': 'admin_panel',  # Активная вкладка
    })

def about(request):
    return render(request, 'Game_Territory/about.html')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Используем get_or_create для избежания дублирования
            UserProfile.objects.get_or_create(user=user)
            login(request, user)
            return redirect('Game_Territory:home')
    else:
        form = RegisterForm()
    return render(request, 'Game_Territory/register.html', {'form': form})

@role_required('manager')
def manage_products(request):
    return render(request, 'Game_Territory/manage_products.html')


def product_list(request):
    products = Product.objects.all()
    return render(request, 'Game_Territory/product_list.html', {'products': products})

@role_required('manager')
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('store:product_list')
    else:
        form = ProductForm()
    return render(request, 'Game_Territory/product_form.html', {'form': form})

@role_required('manager')
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('store:product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'Game_Territory/product_form.html', {'form': form})

@role_required('manager')
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('store:product_list')
    return render(request, 'Game_Territory/product_confirm_delete.html', {'product': product})



@user_passes_test(lambda u: u.userprofile.role == 'admin')
def manage_users(request):
    users = User.objects.all()
    return render(request, 'Game_Territory/manage_users.html', {'users': users})

@user_passes_test(lambda u: u.userprofile.role == 'admin')
def update_user_role(request, user_id, role):
    user = get_object_or_404(User, id=user_id)
    user.userprofile.role = role
    user.userprofile.save()
    return redirect('store:manage_users')

def process_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    order.is_paid = True
    order.status = 'processed'
    order.save()
    return redirect('store:order_success')


@role_required('manager')
def order_statistics(request):
    orders = Order.objects.all()
    order_status_counts = orders.values('status').annotate(count=models.Count('status'))

    statuses = [item['status'] for item in order_status_counts]
    counts = [item['count'] for item in order_status_counts]

    plt.figure(figsize=(8, 4))
    plt.bar(statuses, counts)
    plt.title('Статистика заказов')
    plt.xlabel('Статус')
    plt.ylabel('Количество')

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)

    return HttpResponse(buffer, content_type='image/png')

# def add_to_cart(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     cart, created = Cart.objects.get_or_create(user=request.user)
#     cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
#     cart_item.quantity += 1
#     cart_item.save()
#     return redirect('store:cart_detail')

def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'Game_Territory/cart_detail.html', {'cart': cart})

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()

    messages.success(request, f'Товар "{product_name}" удалён из корзины.')
    return redirect('Game_Territory:view_cart')


@login_required
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, f'Количество товара "{cart_item.product.name}" обновлено.')
        else:
            cart_item.delete()
            messages.success(request, f'Товар "{cart_item.product.name}" удалён из корзины.')

    return redirect('Game_Territory:view_cart')


def order_success(request):
    return render(request, 'Game_Territory/order_success.html')


def create_order(request):
    # Получаем корзину пользователя
    cart = get_object_or_404(Cart, user=request.user)
    if cart.items.count() == 0:
        return redirect('Game_Territory:cart_detail')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Создаем заказ
            order = form.save(commit=False)
            order.customer = request.user
            order.save()

            # Создаем OrderItem для каждого товара в корзине
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                )

            # Очищаем корзину
            cart.items.all().delete()

            # Уведомление по email
            send_mail(
                'Подтверждение заказа',
                f'Спасибо за ваш заказ №{order.id}! Мы уведомим вас о статусе доставки.',
                'from@example.com',
                [request.user.email],
                fail_silently=False,
            )

            messages.success(request, 'Ваш заказ был успешно оформлен!')
            return redirect('Game_Territory:order_success')
    else:
        form = OrderForm()

    return render(request, 'Game_Territory/order_form.html', {'form': form})

@login_required
def order_history(request):
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'Game_Territory/order_history.html', {'orders': orders})

@role_required('manager')
def manage_orders(request):
    status = request.GET.get('status')
    if status:
        orders = Order.objects.filter(status=status)
    else:
        orders = Order.objects.all()
    return render(request, 'Game_Territory/manage_orders.html', {'orders': orders, 'status': status})


def home(request):
    # Получаем все товары из каталога
    all_products = list(Product.objects.all())

    # Случайно выбираем до 6 товаров
    popular_products = random.sample(all_products, min(len(all_products), 6))

    return render(request, 'Game_Territory/home.html', {'popular_products': popular_products})


def stores(request):
    return render(request, 'Game_Territory/stores.html')#сделать

def gaming_zones(request):
    return render(request, 'Game_Territory/gaming_zones.html')#сделать

def contacts(request):
    return render(request, 'Game_Territory/contacts.html')#сделать

# Представления для категорий
def board_games(request):
    return render(request, 'Game_Territory/board_games.html')#сделать

def wargames(request):
    return render(request, 'Game_Territory/wargames.html')#сделать

def warhammer(request):
    return render(request, 'Game_Territory/warhammer.html')#сделать

def infinity(request):
    return render(request, 'Game_Territory/infinity.html')#сделать

def mtg(request):
    return render(request, 'Game_Territory/mtg.html')#сделать

def discounts(request):
    return render(request, 'Game_Territory/discounts.html')#сделать



@login_required
def profile(request):
    # Проверяем, является ли пользователь администратором или менеджером
    is_admin = request.user.is_superuser
    is_manager = request.user.groups.filter(name='manager').exists()

    # Инициализируем формы
    password_form = PasswordChangeForm(request.user)
    profile_form = None

    if request.method == 'POST':
        # Определяем, какая форма была отправлена
        if 'password_form' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Обновляем сессию
                messages.success(request, 'Ваш пароль успешно изменён!')
                return redirect('Game_Territory:personal_info')
            else:
                messages.error(request, 'Пожалуйста, исправьте ошибки в форме смены пароля.')
        elif 'profile_form' in request.POST:
            # Обновляем имя, фамилию и email
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            email = request.POST.get('email', '').strip()

            if first_name and last_name and email:
                request.user.first_name = first_name
                request.user.last_name = last_name
                request.user.email = email
                request.user.save()
                messages.success(request, 'Личная информация успешно обновлена!')
                return redirect('Game_Territory:personal_info')
            else:
                messages.error(request, 'Пожалуйста, заполните все поля формы.')

    return render(request, 'Game_Territory/personal_info.html', {
        'password_form': password_form,
        'is_admin': is_admin,
        'is_manager': is_manager,
    })

@login_required
def edit_profile(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()

        # Обновляем информацию о пользователе
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email
        request.user.save()

        messages.success(request, "Ваш профиль успешно обновлен!")
        return redirect("Game_Territory:personal_info")

    return redirect("Game_Territory:personal_info")

@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            # Обновляем сессию, чтобы не разлогинивать пользователя
            update_session_auth_hash(request, user)
            messages.success(request, "Пароль успешно изменен!")
            return redirect("Game_Territory:personal_info")
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки ниже.")
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, "Game_Territory/change_password.html", {"form": form})

@user_passes_test(lambda u: u.is_superuser)  # Проверка, является ли пользователь администратором
def user_management(request):
    users = User.objects.all()
    user_data = []

    # Создаем данные с группами для каждого пользователя
    for user in users:
        user_data.append({
            'user': user,
            'is_manager': user.groups.filter(name="manager").exists(),
            'is_superuser': user.is_superuser
        })

    return render(request, 'Game_Territory/user_management.html', {
        'user_data': user_data,
    })

# Представление для управления заказами (доступно администратору и менеджеру)
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='manager').exists())  # Проверка на админа или менеджера
def order_management(request):
    orders = Order.objects.all()
    return render(request, 'Game_Territory/order_management.html', {'orders': orders})

def is_manager_or_admin(user):
    return user.is_superuser or user.groups.filter(name='manager').exists()

@user_passes_test(is_manager_or_admin, login_url='Game_Territory:no_access')
def manage_products(request):
    products = Product.objects.all()  # Получаем все товары
    return render(request, 'Game_Territory/manage_products.html', {'products': products})

@user_passes_test(is_manager_or_admin, login_url='Game_Territory:no_access')
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('Game_Territory:manage_products')
    else:
        form = ProductForm()
    return render(request, 'Game_Territory/product_form.html', {'form': form})

@user_passes_test(is_manager_or_admin, login_url='Game_Territory:no_access')
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('Game_Territory:manage_products')
    else:
        form = ProductForm(instance=product)
    return render(request, 'Game_Territory/product_form.html', {'form': form})

@user_passes_test(is_manager_or_admin, login_url='Game_Territory:no_access')
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('Game_Territory:manage_products')
    return render(request, 'Game_Territory/product_confirm_delete.html', {'product': product})

def no_access(request):
    return render(request, 'Game_Territory/no_access.html')


def update_user_role(request, user_id, role):
    if request.user.is_superuser:  # Только администратор может менять роли
        user = get_object_or_404(User, id=user_id)
        manager_group, created = Group.objects.get_or_create(name='manager')

        if role == 'manager':
            user.groups.add(manager_group)
            messages.success(request, f'{user.username} назначен менеджером.')
        elif role == 'user':
            user.groups.remove(manager_group)
            messages.success(request, f'{user.username} теперь является пользователем.')

        return redirect('Game_Territory:user_management')
    else:
        return redirect('Game_Territory:no_access')


def delete_user(request, user_id):
    if request.user.is_superuser:  # Только администратор может удалять пользователей
        user = get_object_or_404(User, id=user_id)
        user.delete()
        messages.success(request, f'Пользователь {user.username} был удалён.')
        return redirect('Game_Territory:user_management')
    else:
        return redirect('Game_Territory:no_access')

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'Game_Territory/product_detail.html', {'product': product})


# Добавление товара в корзину
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        cart_item.quantity += 1
    else:
        cart_item.quantity = 1
    cart_item.save()

    messages.success(request, f'Товар "{product.name}" добавлен в корзину.')
    return redirect('Game_Territory:view_cart')


# Отображение корзины
@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    for item in cart_items:
        print(f"Товар: {item.product.name}, Цена: {item.product.price}, Количество: {item.quantity}")
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    return render(request, 'Game_Territory/view_cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })


# Оформление заказа
@login_required
def checkout(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = cart.items.all()

    if not cart_items:
        return HttpResponse("Корзина пуста", status=400)

    total_price = sum(item.product.price * item.quantity for item in cart_items)

    if request.method == 'POST':
        delivery_method = request.POST.get('delivery_method')
        address = request.POST.get('address') if delivery_method == 'delivery' else None

        # Создаем заказ
        order = Order.objects.create(
            customer=request.user,
            status='pending',
            delivery_method=delivery_method,
            address=address,
            is_paid=False
        )

        # Добавляем товары в заказ
        for item in cart_items:
            order.products.add(item.product)

        # Очищаем корзину
        cart.items.all().delete()

        return redirect('Game_Territory:order_detail', order_id=order.id)

    return render(request, 'Game_Territory/checkout.html', {'cart_items': cart_items, 'total_price': total_price})


# Детали заказа
@login_required
def order_detail(request, order_id):
    order = Order.objects.get(id=order_id)
    return render(request, 'Game_Territory/order_detail.html', {'order': order})