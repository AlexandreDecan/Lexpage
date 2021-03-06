from django import template
from django.utils.safestring import mark_safe
from html.entities import codepoint2name

from helpers.regex import RE_URL
from ..markdown_extensions import shorten_link

import re


register = template.Library()


# tagname : (regex, html, clean)
_simple_tags = [
    # b
    (r'\[b\](.*?)\[/b\]', r'<b>\1</b>', r'\1'),
    # u
    (r'\[u\](.*?)\[/u\]', r'<u>\1</u>', r'\1'),
    # i
    (r'\[i\](.*?)\[/i\]', r'<em>\1</em>', r'\1'),
    # strike
    (r'\[strike\](.*?)\[/strike\]', r'<strike>\1</strike>', r'\1'),

    # color=
    (r'\[color=(.*?)\](.*?)\[/color\]', r'<span style="color:\1;">\2</span>', r'\2'),
    # font=
    (r'\[font=(.*?)\](.*?)\[/font\]', r'<span style="font-family:\1;">\2</span>', r'\2'),
    # size=
    (r'\[size=(.*?)\](.*?)\[/size\]', r'<span style="font-size:\1;">\2</span>', r'\2'),
    # align=
    (r'\[align=(.*?)\](.*?)\[/align\]', r'<div align="\1">\2</div>', r'\2'),

    # url

    (r'(^|\s|\(|\[)('+RE_URL+')($|\s|\)|\])', (lambda m: '{1}<a href="{2}">{0}</a>{3}'.format(shorten_link(m.group(2)), *m.groups())), r'\1\2\3'),
    (r'\[url\]('+RE_URL+')\[/url\]', (lambda m: '<a href="{1}">{0}</a>'.format(shorten_link(m.group(1)), *m.groups())), r'\1'),
    (r'\[url=('+RE_URL+')\](.*?)\[/url\]', r'<a href="\1">\2</a>', r'\2'),

    # img
    (r'\[img\]('+RE_URL+')\[/img\]', r'<img src="\1"/>', r'\1'),

    # embed
    (r'\[embed\]('+RE_URL+')\[/embed\]', r'<a class="oembed" href="\1">\1</a>', r'\1'),
]

_advanced_tags = [
    # code
    (r'\[code\]([^\n]*?)\[/code\]', r'<code>\1</code>', r'\1'),
    (r'(?:\n)*\[code\](?:\n)?(.*?)(?:\n)?\[/code\](?:\n)*', r'<pre><code>\1</code></pre>', r'\1'),

    # quote
    (r'(?:\n)*\[quote\](?:\n)?(.*?)(?:\n)?\[/quote\](?:\n)*', r'<blockquote>\1</blockquote>', r' \1 '),
    (r'(?:\n)*\[quote=(.*?)\](?:\n)?(.*?)(?:\n)?\[/quote\](?:\n)*', r'<blockquote><cite>\1</cite>\2</blockquote>', r' \1: \2 '),
 
    # sign=
    (r'\[sign=(.*?)\](.*?)\[/sign\]', r'<div class="smiley-sign"><div class="smiley-sign-text">\2</div><div class="smiley-sign-smiley">\1</div></div>', r'\2'),

    # spoiler
    (r'\[spoiler\](.*?)\[/spoiler\]', '<span class="spoiler" onclick="$(this).toggleClass(\'spoiler-show\');"><span>\\1</span></span>', r'\1'),
]


def htmlentities(value):
    t = []
    for c in value:
        if ord(c) in codepoint2name:
            t.append('&' + codepoint2name[ord(c)] + ';')
        else:
            t.append(c)
    return ''.join(t)


@register.filter
def bbcode(value):
    value = htmlentities(value)
    value = value.replace('\r\n', '\n')  # Limit spacing

    # Convert BBcode to html
    for reg, rep, _ in _simple_tags:
        value = re.sub(reg, rep, value)

    # Convert special tags
    for reg, rep, _ in _advanced_tags:
        temp = ''
        while temp != value:
            temp = value
            value = re.sub(reg, rep, value, flags=re.DOTALL)

    value = value.replace('\n', '<br/>')

    return mark_safe(value)

