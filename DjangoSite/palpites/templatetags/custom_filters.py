from django import template

register = template.Library()

@register.filter(name='neg')
def negate(value):
    return -value
