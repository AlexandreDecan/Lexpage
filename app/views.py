#!/usr/bin/python

from django.shortcuts import render

from blog.models import BlogPost
from board.models import Thread

import datetime


HOMEPAGE_POST_NUMBER = 10  # Maximum number of posts to display
HOMEPAGE_THREAD_DELAY = 5  # Maximal delay since last message for a thread to be considered as active
HOMEPAGE_THREAD_NUMBER = 12  # Minimum number of threads to display
HOMEPAGE_THREAD_MAX_NUMBER = 30  # Maximum number of threads to display


def homepage(request):
    """
    Simple view corresponding to the homepage. It provides some blog posts
    and some board posts, including annotated threads).
    """
    context = {}

    # Latest posts
    context['post_list'] = BlogPost.published.all().reverse()[:HOMEPAGE_POST_NUMBER]

    # Latest threads
    date_limit = datetime.date.today() - datetime.timedelta(HOMEPAGE_THREAD_DELAY)

    threads = []
    for i, thread in enumerate(Thread.objects.order_by('-last_message__date')[:HOMEPAGE_THREAD_MAX_NUMBER]):
        # Stop if minimum number of threads is reached and there is no other active threads
        if i >= HOMEPAGE_THREAD_NUMBER and thread.last_message.date.date() <= date_limit:
            break

        # Annotate with flags
        thread.annotate_flag(request.user)
        threads.append(thread)

    context['thread_list'] = threads

    return render(request, 'homepage.html', context)
