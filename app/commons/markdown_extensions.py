from django.template.defaultfilters import truncatechars

import markdown

from helpers.regex import RE_URL


DEFAULT_EXTENSIONS = ['markdown.extensions.{}'.format(e) for e in ('nl2br', 'smart_strong', 'sane_lists')]


class EmbedExtension(markdown.Extension):
    class EmbedPattern(markdown.inlinepatterns.LinkPattern):
        def handleMatch(self, m):
            el = markdown.util.etree.Element('a')
            link = markdown.util.AtomicString(m.group(2))

            el.text = link
            el.set('href', self.sanitize_url(self.unescape(link)))
            el.set('class', 'oembed')

            return el

    def __init__(self, new_style=True, *args, **kwargs):
        """
        Create an Embed extension for Markdown. Parameter ``new_style``which defaults to true
        means that we capture [[URL]] instead of [!embed](url).
        """
        super().__init__(*args, **kwargs)
        self._re = r'\[\[(.*)\]\]' if new_style else r'\[!embed\]\((.*)\)'

    def extendMarkdown(self, md, md_globals):
        """ Modify inline patterns. """
        md.inlinePatterns.add('embed', EmbedExtension.EmbedPattern(self._re, md), '<link')


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


class SpoilerExtension(markdown.Extension):
    class SpoilerPattern(markdown.inlinepatterns.Pattern):
        def handleMatch(self, m):
            el = markdown.util.etree.Element('span')
            el.set('class', 'spoiler')
            el.set('onclick', '$(this).toggleClass(\'spoiler-show\');')

            subel = markdown.util.etree.SubElement(el, 'span')
            subel.text = m.group(2)

            return el

    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns.add('spoiler', SpoilerExtension.SpoilerPattern(r'\$\$(.*)\$\$', md), '<strong')


class BBCodeQuoteExtension(markdown.Extension):
    pass

