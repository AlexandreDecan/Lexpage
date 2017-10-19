from django import template
from django.utils.safestring import mark_safe
from django.conf import settings

import os

register = template.Library()

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
        smiley_other = [(x[:-4],x[-3:]) for x in os.listdir(local_smiley_dir) if x[-3:] == 'gif']
    except FileNotFoundError:
        smiley_other = []

    # Convert special smiley's
    for s, name in smiley_list:
        value = value.replace(s, '<img src="%s"/>' % os.path.join(online_smiley_dir, name+".gif"))

    # Convert other smiley's
    for name, ext in smiley_other:
        value = value.replace(':%s:' % name, '<img src="%s"/>' % os.path.join(online_smiley_dir, name+'.'+ext))

    return value


@register.filter
def smiley(value):
    return mark_safe(replace_smiley(value))
