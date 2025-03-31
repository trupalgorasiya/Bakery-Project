from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Custom filter to get an item from a dictionary by key."""
    if dictionary is None:
        return None
    return dictionary.get(key, None)

from django import template

register = template.Library()

@register.filter(name='mul')
def multiply(value, arg):
    return value * arg


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, [])