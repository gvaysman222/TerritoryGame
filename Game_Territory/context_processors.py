def user_roles(request):
    if request.user.is_authenticated:
        return {
            'is_admin': request.user.is_superuser,
            'is_manager': request.user.groups.filter(name='manager').exists()
        }
    return {
        'is_admin': False,
        'is_manager': False
    }

def cart_item_count(request):
    cart = request.session.get("cart", {})  # Корзина хранится в сессии
    total_items = sum(cart.values())  # Суммируем количество товаров
    return {"cart_item_count": total_items}
