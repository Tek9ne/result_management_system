from django import template

register = template.Library()

@register.filter
def split(value, arg):
    return value.split(arg)

@register.filter
def get_item(list, index):
    try:
        return list[index]
    except IndexError:
        return ''