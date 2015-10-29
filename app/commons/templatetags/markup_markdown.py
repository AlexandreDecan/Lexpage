from django import template
from django.utils.safestring import mark_safe
from django.utils.encoding import force_text

from . import markdown


register = template.Library()


from .markdown.extensions import def_list, fenced_code, footnotes, tables, \
                                nl2br, smart_strong, sane_lists, lexpage_oembed

extensions = [def_list.makeExtension(), 
                fenced_code.makeExtension(),
                footnotes.makeExtension(),
                tables.makeExtension(),
                nl2br.makeExtension(),
                smart_strong.makeExtension(),
                sane_lists.makeExtension(),
                lexpage_oembed.makeExtension()]


@register.filter(name='markdown', is_safe=True)
def __markdown(value):
    # value = force_text(value)
    value = markdown.markdown(value, safe_mode='escape', output_format='html5', lazy_ol=False, extensions=extensions)

    return mark_safe(value)

