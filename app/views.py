#!/usr/bin/python

from django.shortcuts import render
from django.core.paginator import Paginator

from blog.models import BlogPost
from board.models import Thread
from board.views import BoardLatestsView


HOMEPAGE_POST_NUMBER = 10  # Maximum number of posts to display


def homepage(request):
    """
    Simple view corresponding to the homepage. It provides some blog posts
    and some board posts, including annotated threads).
    """
    context = {}

    # Latest posts
    context['post_list'] = BlogPost.published.all().reverse()[:HOMEPAGE_POST_NUMBER]

    # Latest threads
    threads_paginator = Paginator(
        object_list=Thread.objects.order_by('-last_message__date'),
        per_page=BoardLatestsView.paginate_by,
        orphans=BoardLatestsView.paginate_orphans,
        allow_empty_first_page=True,
    )
    threads = threads_paginator.page(1)

    for thread in threads.object_list:
        thread.annotate_flag(request.user)

    context['threads'] = threads

    return render(request, 'homepage.html', context)
