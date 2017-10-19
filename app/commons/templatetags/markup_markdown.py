from django import template
from django.utils.safestring import mark_safe

from .. import markdown_extensions
import markdown


register = template.Library()


def create_markdown_filter(*extra_extensions):
    def _wrapped(value):
        extensions = ['markdown.extensions.{}'.format(e) for e in ('nl2br', 'smart_strong', 'sane_lists')]
        extensions += extra_extensions
        return mark_safe(markdown.markdown(value, safe_mode='escape', output_format='html5', lazy_ol=False, extensions=extensions))
    return _wrapped


register.filter(name='markdown', is_safe=True)(create_markdown_filter(
    markdown_extensions.EmbedExtension(),
    markdown_extensions.InlineURLExtension()
))
