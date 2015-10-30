from django.shortcuts import render
from django.views.generic import View
from django.db.models import Q

from .forms_search import SearchForm
from blog.models import BlogPost
from board.models import Message, Thread
from profile.models import ActiveUser

import re

"""
This file needs a complete rewriting!

We should provide a better way to abstract the search through the models, to 
populate the results according to the choices done, and to display useful 
data instead of the title (eg.)...
"""

SEARCH = [
    {   'title': 'Billets',
        'manager': BlogPost.published,
        'search_fields': ['title', 'abstract', 'text'],
        'author_field': 'author',
        'date_field': 'date_published',
        'display_title': lambda x: x.title,
        'display_author': lambda x: x.author,
        'display_date': lambda x: x.date_published,
        'display_summary': lambda x: x.abstract,
    },
    {   'title': 'Titre des discussions', 
        'manager': Thread.objects, 
        'search_fields': ['title',],
        'author_field': None,
        'date_field': 'date_created',
        'display_title': lambda x: x.title,
        'display_author': lambda x: None,
        'display_date': lambda x: None,
        'display_summary': lambda x: 'Dernier message : '+x.last_message.text,   
    },    
    {   'title': 'Messages des discussions', 
        'manager': Message.objects, 
        'search_fields': ['text',],
        'author_field': 'author',
        'date_field': 'date',
        'display_title': lambda x: x.thread,
        'display_author': lambda x: x.author,
        'display_date': lambda x: x.date,
        'display_summary': lambda x: x.text,   
    },
    {   'title': 'Noms des utilisateurs', 
        'manager': ActiveUser.objects,
        'search_fields': ['username',],
        'author_field': None, 
        'date_field': 'date_joined', 
        'display_title': lambda x: x.username, 
        'display_author': lambda x: None, 
        'display_date': lambda x: x.date_joined, 
        'display_summary': lambda x: None,
    }
]


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
    query = None # Query to search for every search term        
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None # Query to search for a given term in each field
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
    return Q(**{'%s__username__icontains' % field: query_text})


def get_query_for_date(search_cfg, date_start, date_end):
    field = search_cfg['date_field']
    return Q(**{'%s__gte' % field: date_start, 
            '%s__lte' % field: date_end})


class SearchView(View):
    def post(self, request, *args, **kwargs):
        self.form = SearchForm(request.POST)

        if self.form.is_valid():
            # Compute the query and store it
            query = self.form.cleaned_data['query_text']
            target = self.form.cleaned_data['target']
            author = self.form.cleaned_data['author']
            date_start = self.form.cleaned_data['date_start']
            date_end = self.form.cleaned_data['date_end']

            self.search = SEARCH[target]

            self.query = get_query_for_fields(self.search, query)
            self.query &= get_query_for_author(self.search, author)
            self.query &= get_query_for_date(self.search, date_start, date_end)

        return self.render(request)

    def get(self, request, *args, **kwargs):
        self.form = SearchForm()
        return self.render(request)

    def render(self, request):
        context = {'form': self.form}

        if hasattr(self, 'query'):
            # We have a query, compute the queryset
            results = self.search['manager'].all().filter(self.query).order_by('-'+self.search['date_field'])
            result_list = []
            for result in results:
                setattr(result, 'search_title', self.search['display_title'](result))
                setattr(result, 'search_summary', self.search['display_summary'](result))

                setattr(result, 'search_author', self.search['display_author'](result))
                setattr(result, 'search_date', self.search['display_date'](result))
                result_list.append(result)
            context['result_title'] = self.search['title']
            context['result_list'] = result_list
        
        return render(self.request, 'commons/search.html', context)
        




