import datetime
from django import template
from django.template.defaultfilters import date as _date

register = template.Library()


@register.filter(name='split')
def split(value, key):
    """
        Returns the value turned into a list.
    """
    return value.split(key)


@register.filter(name='shorttimesince')
def shorttimesince(date, other_date=None):
    other_date = datetime.datetime.now() if other_date is None else other_date
    delta = (other_date - date).total_seconds()

    if delta < 60:
        return '<1m'
    elif delta < 60 * 60:
        return '{:d}m'.format(int(delta // 60))
    elif delta < 60 * 60 * 24:
        return '{:d}h'.format(int(delta // 60 // 60))
    elif delta < 60 * 60 * 24 * 30:
        return '{:d}j'.format(int(delta // 60 // 60 // 24))
    elif delta < 60 * 60 * 24 * 365:
        return _date(date, 'j b')
    else:
        return _date(date, 'b Y')
