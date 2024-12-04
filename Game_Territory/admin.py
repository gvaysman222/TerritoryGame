from django.contrib import admin
from Game_Territory.models import UserProfile, Product, Order, CartItem, Cart, UserProfile
# Register your models here.

admin.site.register(UserProfile)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(CartItem)
admin.site.register(Cart)