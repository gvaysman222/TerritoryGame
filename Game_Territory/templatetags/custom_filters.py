# Game_Territory/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={'class': css_class})

@register.filter
def multiply(value, arg):
    """Умножает value на arg."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
