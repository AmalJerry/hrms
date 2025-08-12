from django import template
import datetime
register = template.Library()


@register.filter(name='data_type')
def data_type(value):

    return type(value).__name__


@register.filter(name='duration_to_timedelta')
def duration_to_timedelta(value):
    hours, minutes, seconds = map(float, value.split(':'))
    return datetime.timedelta(hours=hours, minutes=minutes, seconds=round(seconds))


@register.filter
def is_int(value):
    return isinstance(value, int)

@register.filter
def to_int(value):
    return int(value)

@register.filter(name='split')
def split(value , key):

    return value.split(key)


register = template.Library()

@register.filter(name='char_to_date')
def char_to_date(value):
    try:
        return datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S').date()
    except (ValueError, TypeError):
        return None


register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, "")