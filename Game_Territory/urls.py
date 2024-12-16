# store/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'Game_Territory'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('products/', views.product_list, name='product_list'),
    path('products/new/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_update, name='product_update'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('order/new/', views.create_order, name='create_order'),
    path('users/', views.manage_users, name='manage_users'),
    path('users/<int:user_id>/update_role/<str:role>/', views.update_user_role, name='update_user_role'),
    path('order/<int:order_id>/pay/', views.process_payment, name='process_payment'),
    path('statistics/orders/', views.order_statistics, name='order_statistics'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('order/success/', views.order_success, name='order_success'),
    path('orders/history/', views.order_history, name='order_history'),
    path('orders/manage/', views.manage_orders, name='manage_orders'),
    path('catalog/', views.product_list, name='product_list'),   # Каталог
    path('stores/', views.stores, name='stores'),                # Магазины
    path('gaming_zones/', views.gaming_zones, name='gaming_zones'),  # Игротеки
    path('contacts/', views.contacts, name='contacts'),          # Контакты
    # Основные категории
    path('board_games/', views.board_games, name='board_games'),
    path('wargames/', views.wargames, name='wargames'),
    path('warhammer/', views.warhammer, name='warhammer'),
    path('infinity/', views.infinity, name='infinity'),
    path('mtg/', views.mtg, name='mtg'),
    path('discounts/', views.discounts, name='discounts'),
    path('login/', auth_views.LoginView.as_view(template_name='Game_Territory/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='Game_Territory:home'), name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('user_management/', views.user_management, name='user_management'),
    path('order_management/', views.order_management, name='order_management'),
    path('manage/products/', views.manage_products, name='manage_products'),
    path('no_access/', views.no_access, name='no_access'),
    path('users/<int:user_id>/update_role/<str:role>/', views.update_user_role, name='update_user_role'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('view_cart/', views.view_cart, name='view_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('checkout/', views.checkout, name='checkout'),
    path('about/', views.about, name='about'),
    path('personal_info/', views.personal_info, name='personal_info'),
    path('my_orders/', views.my_orders, name='my_orders'),
    path('admin_panel/', views.admin_panel, name='admin_panel'),
    path("edit_profile/", views.edit_profile, name="edit_profile"),
    path("change_password/", views.change_password, name="change_password"),
    path('delivery_info/', views.delivery_info, name='delivery_info'),
    path('catalog/search/', views.search_products, name='search_products'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)