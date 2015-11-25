import blog.models
import board.models
import profile.models
import minichat.models
import slogan.models

import re
from django.db.models import Q


SEARCH = [{
    'title': 'Discussions - Messages',
    'manager': board.models.Message.objects,
    'search_fields': ['text', ],
    'author_field': 'author__username',
    'date_field': 'date',
    'display_title': lambda x: x.thread.title,
    'display_author': lambda x: x.author.username,
    'display_date': lambda x: x.date,
    'display_summary': lambda x: x.text,
}, {
    'title': 'Discussions - Titres',
    'manager': board.models.Thread.objects,
    'search_fields': ['title', ],
    'author_field': None,
    'date_field': 'date_created',
    'display_title': lambda x: x.title,
    'display_author': lambda x: None,
    'display_date': lambda x: None,
    'display_summary': lambda x: 'Dernier message : ' + x.last_message.text,
}, {
    'title': 'Billets',
    'manager': blog.models.BlogPost.published,
    'search_fields': ['title', 'abstract', 'text'],
    'author_field': 'author__username',
    'date_field': 'date_published',
    'display_title': lambda x: x.title,
    'display_author': lambda x: x.author.username,
    'display_date': lambda x: x.date_published,
    'display_summary': lambda x: x.abstract,
}, {
    'title': 'Minichat',
    'manager': minichat.models.Message.objects,
    'search_fields': ['text'],
    'author_field': 'user__username',
    'date_field': 'date',
    'display_title': lambda x: 'Posté par %s' % x.user.username,
    'display_author': lambda x: None,
    'display_date': lambda x: x.date,
    'display_summary': lambda x: x.text,
}, {
    'title': 'Slogans',
    'manager': slogan.models.Slogan.visible,
    'search_fields': ['slogan'],
    'author_field': 'author',
    'date_field': 'date',
    'display_title': lambda x: x.slogan,
    'display_author': lambda x: x.author,
    'display_date': lambda x: x.date,
    'display_summary': lambda x: None,
}, {
    'title': 'Lexpagiens',
    'manager': profile.models.ActiveUser.objects,
    'search_fields': ['username', ],
    'author_field': 'username',
    'date_field': 'date_joined',
    'display_title': lambda x: x.username,
    'display_author': lambda x: None,
    'display_date': lambda x: x.date_joined,
    'display_summary': lambda x: None,
}]


def normalize_query(query_string, findterms=None, normspace=None):
    """ Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.
        Example:

        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']

    """
    if findterms is None:
        findterms = re.compile(r'"([^"]+)"|(\S+)').findall
    if normspace is None:
        normspace = re.compile(r'\s{2,}').sub
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]


def get_query(query_string, search_fields):
    """ Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.

    """
    query = None  # Query to search for every search term
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None  # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query


def get_query_for_fields(search_cfg, query_text):
    fields = search_cfg['search_fields']
    return get_query(query_text, fields)


def get_query_for_author(search_cfg, query_text):
    field = search_cfg['author_field']
    if not field or query_text == '':
        return Q()
    return Q(**{'%s__icontains' % field: query_text})


def get_query_for_date(search_cfg, date_start, date_end):
    field = search_cfg['date_field']
    return Q(**{'%s__gte' % field: date_start,
                '%s__lte' % field: date_end})

