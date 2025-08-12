from django import template
from datetime import datetime

register = template.Library()

@register.filter(name='char_to_date')
def char_to_date(value):
    try:
        return datetime.strptime(value, '%Y-%m-%d %H:%M:%S').date()
    except (ValueError, TypeError):
        return None

@register.filter(name='to_int')
def to_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0



@register.filter
def is_int(value):
    return isinstance(value, int)