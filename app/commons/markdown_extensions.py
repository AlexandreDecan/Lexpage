from django import template
from django.utils.safestring import mark_safe
from django.template.defaultfilters import truncatechars

import markdown

from helpers.regex import RE_URL


DEFAULT_EXTENSIONS = ['markdown.extensions.{}'.format(e) for e in ('nl2br', 'smart_strong', 'smart_emphasis', 'sane_lists')]


class EmbedExtension(markdown.Extension):
    class OEmbedPattern(markdown.inlinepatterns.LinkPattern):
        def handleMatch(self, m):
            el = markdown.util.etree.Element('a')
            link = markdown.util.AtomicString(m.group(2))

            el.text = link
            el.set('href', self.sanitize_url(self.unescape(link)))
            el.set('class', 'oembed')

            return el

    def extendMarkdown(self, md, md_globals):
        """ Modify inline patterns. """
        md.inlinePatterns.add('embed', EmbedExtension.OEmbedPattern('\[!embed\]\((.*)\)', md), '<link')


class InlineURLExtension(markdown.Extension):
    class InlineURLPattern(markdown.inlinepatterns.LinkPattern):
        def handleMatch(self, m):
            link = m.group(2)
            text = truncatechars(
                ''.join(link.split('://')[1:]),
                25,
            )

            el = markdown.util.etree.Element('a')
            el.text = markdown.util.AtomicString(text)
            el.set('href', self.sanitize_url(self.unescape(link)))
            el.set('class', 'inline-url')

            return el

    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns.add('inlineurl', InlineURLExtension.InlineURLPattern('({})'.format(RE_URL), md), '<autolink')
