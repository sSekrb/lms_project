from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Получить значение из словаря по ключу"""
    if dictionary and key:
        return dictionary.get(key)
    return None