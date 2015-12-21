#!/usr/bin/python

from django.shortcuts import render_to_response
from django.template import RequestContext

from blog.models import BlogPost
from board.models import Thread
from django.conf import settings

import base64
import hashlib
import micawber

import datetime


HOMEPAGE_POST_NUMBER = 10    # Maximum number of posts to display
HOMEPAGE_THREAD_DELAY = 3   # Number of days before expiration


def homepage(request):
    """
    Simple view corresponding to the homepage. It provides some blog posts
    and some board posts, including annotated threads).
    """
    context = {}

    # Last posts to display
    context['post_list'] = BlogPost.published.all().reverse()[:HOMEPAGE_POST_NUMBER]

    # Last threads to display
    date_limit = datetime.date.today() - datetime.timedelta(HOMEPAGE_THREAD_DELAY)
    date_limit = datetime.datetime(date_limit.year, date_limit.month, date_limit.day)
    threads = Thread.objects.all().filter(last_message__date__gte=date_limit).order_by('-date_created')

    # Annotate with flags
    for thread in threads:
        thread.annotate_flag(request.user)
    context['thread_list'] = threads

    return render_to_response('homepage.html',
                              context,
                              context_instance=RequestContext(request))

def render_rich_content(request, url_checksum, url_b64):
    """ Retrieve rich text content.
    Params:
        url_checksum: md5sum(settings.RICH_TEXT_CHECKSUM, url)
        url_b64: b64 of the URL

    url_checksum should prevent malicous usage to crawl the web."""
    m = hashlib.md5()
    m.update(bytes(settings.RICH_TEXT_CONTENT_SALT))
    m.update(bytes(url_b64))
    computed_checksum = m.digest()
    if computed_checksum != url_checksum:
        raise ValueError

    real_url = base64.b64decode(url_b64)
    provider = micawber.bootstrap_basic()
    provider.request(real_url)


