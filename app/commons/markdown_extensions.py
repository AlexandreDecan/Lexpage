from django.template.defaultfilters import truncatechars

import markdown
import re

from helpers.regex import RE_URL, RE_HASHTAG


def shorten_link(link, length=25):
    return truncatechars(''.join(link.split('://')[1:]), length)


class EmbedExtension(markdown.Extension):
    """
    Support for [!embed](link)
    """
    class EmbedPattern(markdown.inlinepatterns.LinkPattern):
        def handleMatch(self, m):
            link = m.group(2)
            text = shorten_link(link)

            el = markdown.util.etree.Element('a')
            el.text = markdown.util.AtomicString(text)
            el.set('href', self.unescape(link))
            el.set('class', 'oembed')

            return el

    def extendMarkdown(self, md, md_globals):
        """ Modify inline patterns. """
        md.inlinePatterns.add('embed', EmbedExtension.EmbedPattern(r'\[!embed\]\((' + RE_URL + ')\)', md), '<link')


class InlineURLExtension(markdown.Extension):
    class InlineURLPattern(markdown.inlinepatterns.LinkPattern):
        def handleMatch(self, m):
            link = m.group(2)
            text = shorten_link(link)

            el = markdown.util.etree.Element('a')
            el.text = markdown.util.AtomicString(text)
            el.set('href', self.unescape(link))
            el.set('class', 'inline-url')

            return el

    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns.add('inlineurl', InlineURLExtension.InlineURLPattern('({})'.format(RE_URL), md), '_end')


class SpoilerExtension(markdown.Extension):
    """
    E.g.: $$hidden text$$

    """

    class SpoilerPattern(markdown.inlinepatterns.Pattern):
        def handleMatch(self, m):
            el = markdown.util.etree.Element('span')
            el.set('class', 'spoiler')
            el.set('onclick', '$(this).toggleClass(\'spoiler-show\');')

            subel = markdown.util.etree.SubElement(el, 'span')
            subel.text = m.group(2)

            return el

    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns.add('spoiler', SpoilerExtension.SpoilerPattern(r'\$\$(.*)\$\$', md), '_end')


class BBCodeQuoteExtension(markdown.Extension):
    """
    Support for [quote]text[/quote] and [quote=author]text[/quote]

    """
    class BBCodeQuotePostProcessor(markdown.postprocessors.Postprocessor):
        def run(self, text):
            RE_QUOTE = (r'(?:\n)*\[quote\](?:\n)?(.*?)(?:\n)?\[/quote\](?:\n)*', r'<blockquote>\1</blockquote>')
            RE_QUOTE_AUTHOR = (r'(?:\n)*\[quote=(.*?)\](?:\n)?(.*?)(?:\n)?\[/quote\](?:\n)*',
                               r'<blockquote><cite>\1</cite>\2</blockquote>')

            for reg, rep in [RE_QUOTE, RE_QUOTE_AUTHOR]:
                temp = ''
                while temp != text:
                    temp = text
                    text = re.sub(reg, rep, text, flags=re.DOTALL)

            return text

    def extendMarkdown(self, md, md_globals):
        md.postprocessors.add('BBCodeQuote', BBCodeQuoteExtension.BBCodeQuotePostProcessor(), '_end')


class HashtagExtension(markdown.Extension):
    """
    Convert #things into a link.
    Reverse function must be provided, ie. a function that receives a tag and produce an URI.

    Notice that this extension slightly changes the way headers are identified by
    Markdown: a space is needed between # and the text.
    """
    def __init__(self, reverse, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._reverse = reverse

    class HashtagPattern(markdown.inlinepatterns.Pattern):
        def __init__(self, reverse, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._reverse = reverse

        def handleMatch(self, m):
            tag = m.group(2)

            el = markdown.util.etree.Element('a')
            el.set('class', 'hashtag')
            el.set('href', self._reverse(tag))
            el.text = tag

            return el

    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns.add('hashtag', HashtagExtension.HashtagPattern(self._reverse, '({})'.format(RE_HASHTAG), md), '_end')
        md.parser.blockprocessors['hashheader'].RE = re.compile(r'(^|\n)(?P<level>#{1,6}) (?P<header>.*?)#*(\n|$)')
