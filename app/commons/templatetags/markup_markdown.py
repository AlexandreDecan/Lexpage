from django import template
from django.utils.safestring import mark_safe

import markdown
from markdown.inlinepatterns import LinkPattern

register = template.Library()


class OEmbedExtension(markdown.Extension):
    class OEmbedPattern(LinkPattern):
        def handleMatch(self, m):
            el = markdown.util.etree.Element('a')
            el.text = m.group(2)
            href = m.group(2)

            el.set('href', self.sanitize_url(self.unescape(href.strip())))
            el.set('class', 'oembed')

            return el

    def extendMarkdown(self, md, md_globals):
        """ Modify inline patterns. """
        md.inlinePatterns.add('embed', OEmbedExtension.OEmbedPattern('\[!embed\]\((.*)\)', md), '<link')


@register.filter(name='markdown', is_safe=True)
def __markdown(value):
    extensions = ['def_list', 'fenced_code', 'footnotes', 'tables', 'nl2br',
                  'smart_strong', 'sane_lists', OEmbedExtension()]

    value = markdown.markdown(value, safe_mode='escape', output_format='html5', lazy_ol=False, extensions=extensions)

    return mark_safe(value)

