from django import template
from django.utils.safestring import mark_safe

from ..markdown_extensions import DEFAULT_EXTENSIONS, EmbedExtension, InlineURLExtension

import markdown


register = template.Library()


@register.filter(name='markdown', is_safe=True)
def __markdown(value):
    extensions = DEFAULT_EXTENSIONS + [EmbedExtension(new_style=False), InlineURLExtension()]

    value = markdown.markdown(value, safe_mode='escape', output_format='html5', lazy_ol=False, extensions=extensions)

    return mark_safe(value)

