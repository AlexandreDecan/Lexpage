'''
[!embed](url) -> link with class="oembed".
'''

from __future__ import absolute_import
from __future__ import unicode_literals
from . import Extension
from ..inlinepatterns import LinkPattern, util

OEMBED_PATTERN = '\[!embed\]\((.*)\)'

class LexpageOEmbedPattern(LinkPattern):
    def handleMatch(self, m):
        el = util.etree.Element("a")
        el.text = m.group(2)
        href = m.group(2)

        el.set("href", self.sanitize_url(self.unescape(href.strip())))
        el.set("class", "oembed")

        return el  



class LexpageOEmbedExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        """ Modify inline patterns. """
        md.inlinePatterns.add('embed', LexpageOEmbedPattern(OEMBED_PATTERN, md), '<link')


def makeExtension(configs=None):
    return LexpageOEmbedExtension()
