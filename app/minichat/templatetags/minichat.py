from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape

import re

register = template.Library() 

simple_url_re = None
def lazy_simple_url_re():
    global simple_url_re
    if simple_url_re == None:
        simple_url_re = re.compile(r'((https?|ftp|file):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])', re.IGNORECASE)
    return simple_url_re

@stringfilter
def urlize2(value, arg, autoescape=True):
    """
    Look into value for url (http://....) and replace 
    those URL by <a href="url">arg</a>. 
    """
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
    value = esc(value)
    substitute = r'<a href="\1" rel="nofollow">%s</a>' % arg
    return mark_safe(lazy_simple_url_re().sub(substitute, value))

@stringfilter
def urlize3(value, autoescape=True):
    """
    Look into value for url and replace by a glyphicon. 
    """
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
    value = esc(value)
    substitute = r'<a href="\1" title="\1" data-toggle="tooltip" data-placement="top" data-container="body" class="fa fa-external-link" rel="nofollow"></a>'
    return mark_safe(lazy_simple_url_re().sub(substitute, value))



register.filter('urlize2', urlize2, needs_autoescape=True)
register.filter('urlize3', urlize3, needs_autoescape=True)
