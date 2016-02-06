from django import template
from django.utils.safestring import mark_safe
from html.entities import codepoint2name
from django.conf import settings

import re, os

register = template.Library()


# tagname : (regex, html, clean)
tag = [
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

    # img
    (r'\[img\](.*?)\[/img\]', r'<img src="\1"/>', r'\1'),

    # embed
    (r'\[embed\](.*?)\[/embed\]', r'<a class="oembed" href="\1">\1</a>', r'\1'),

    # url
    (r'\[url\](.*?)\[/url\]', r'<a href="\1">\1</a>', r'\1'),
    (r'\[url=(.*?)\](.*?)\[/url\]', r'<a href="\1">\2</a>', r'\2'),
    #(r'([^"])((?:https?|ftp|file):\/\/[-a-zA-Z0-9+&@#\/%?=~_|!:,.;]*[-a-zA-Z0-9+&@#\/%=~_|])([^"])', r'\1<a href="\2">\2</a>\3', r'\1\2\3'),

    # spoiler
    (r'\[spoiler\](.*?)\[/spoiler\]', '<span class="spoiler" onclick="$(this).toggleClass(\'spoiler-show\');"><span>\\1</span></span>', r'\1'),
]

advancedtag = [
    # code
    (r'\[code\]([^\n]*?)\[/code\]', r'<code>\1</code>', r'\1'),
    (r'(?:\n)*\[code\](?:\n)?(.*?)(?:\n)?\[/code\](?:\n)*', r'<pre><code>\1</code></pre>', r'\1'),

    # quote
    (r'(?:\n)*\[quote\](?:\n)?(.*?)(?:\n)?\[/quote\](?:\n)*', r'<blockquote>\1</blockquote>', r' \1 '),
    (r'(?:\n)*\[quote=(.*?)\](?:\n)?(.*?)(?:\n)?\[/quote\](?:\n)*', r'<blockquote><cite>\1</cite>\2</blockquote>', r' \1: \2 '),
 
    # sign=
    (r'\[sign=(.*?)\](.*?)\[/sign\]', r'<div class="sign sign-base"><div class="text">\2</div><div class="smiley">\1</div></div>', r'\2'),
]




taglist = None
advancedtaglist = None
def load_regex():
    """
    Compile the regex if they are not available in taglist and
    advancedtaglist.
    """
    global taglist
    global advancedtaglist

    if taglist == None:
        taglist = [(re.compile(x, re.MULTILINE|re.DOTALL),y,z) \
                    for x,y,z in tag]
    if advancedtaglist == None:
        advancedtaglist = [(re.compile(x, re.MULTILINE|re.DOTALL),y,z) \
                    for x,y,z in advancedtag]


@register.filter
def smiley(value):
    return mark_safe(replace_smiley(value))


smiley_list = [
    (':-)', 'smile'),
    (';-)', 'wink'),
    (':-p', 'tongue'),
    (':-D', 'bigsmile'),
    (':-((', 'angry2'),
    (':-(', 'angry'),
    (':\'((', 'bawling'),
    (':\'(', 'sad'),
    (':-/', 'upset'),
    ('o.O', 'odd'),
    ('o_O', 'odd'),
    (':o)', 'blush'),
    (':-x', 'kiss'),
    (':-X', 'kiss2'),
    ('8-)', 'showoff'),
]

def replace_smiley(value):
    # List of available smileys in smileys directory
    local_smiley_dir = os.path.join(settings.STATIC_ROOT, 'images', 'smiley')

    online_smiley_dir = os.path.join(settings.STATIC_URL, 'images', 'smiley')

    try:
        smiley_other = [(x[:-4],x[-3:]) for x in os.listdir(local_smiley_dir) \
                        if x[-3:] == 'gif']
    except FileNotFoundError:
        smiley_other = []

    # Convert special smiley's
    for s,name in smiley_list:
        value = value.replace(s, '<img src="%s"/>' % os.path.join(online_smiley_dir, name+".gif"))

    # Convert other smiley's
    for name, ext in smiley_other:
        value = value.replace(':%s:' % name, \
            '<img src="%s"/>' % os.path.join(online_smiley_dir, name+'.'+ext))

    return value


def htmlentities(value):
    t = []
    for c in value:
        if ord(c) in codepoint2name:
            t.append('&' + codepoint2name[ord(c)] + ';')
        else:
            t.append(c)
    return ''.join(t)


@register.filter
def bbcode(value, replace_smiley=True):
    load_regex()

    value = htmlentities(value)

    # Avoid too much spacing
    value = value.replace('\r\n', '\n')

    # Convert BBcode to html
    for reg,rep,_ in taglist:
        value = reg.sub(rep, value)

    # Convert special tags
    for reg,rep,_ in advancedtaglist:
        temp = ''
        while temp != value:
            temp = value
            value = reg.sub(rep, value)

    # Smileys
    if replace_smiley:
        value = smiley(value)

    # \n to <br/>
    value = value.replace('\n', '<br/>')

    return mark_safe(value)


@register.filter
def stripbbcode(value):
    load_regex()

    value = htmlentities(value)

    # Convert BBcode to nothing
    for reg,_,rep in taglist:
        value = reg.sub(rep, value)

    # Convert special tags
    for reg,_,rep in advancedtaglist:
        temp = ''
        while temp != value:
            temp = value
            value = reg.sub(rep, value)


    return mark_safe(value) 
