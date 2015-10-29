from django.template.base import Library

from django.utils.timezone import now

register = Library()


@register.filter()
def timedelta(value, arg=None):
    delta = now() - value
    if not arg:
        return delta
    else:
        delta_s = (delta.seconds + delta.days * 24 * 3600)
        if arg == 's':
            return delta_s
        elif arg == 'm':
            return delta_s/60
        elif arg == 'h':
            return delta_s/3600
        elif arg == 'd':
            return delta_s/(3600*24)
        else:
            return getattr(delta, arg)
    
