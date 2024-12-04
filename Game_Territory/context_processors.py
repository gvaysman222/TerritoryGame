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
