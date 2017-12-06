from commons import search
from django.shortcuts import render
from django.views.generic import View
from commons.forms_search import SearchForm

import commons.search as search


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

            self.search = search.SEARCH[target]

            self.query = search.get_query_for_fields(self.search, query)
            self.query &= search.get_query_for_author(self.search, author)
            self.query &= search.get_query_for_date(self.search, date_start, date_end)

        return self.render(request)

    def get(self, request, *args, **kwargs):
        self.form = SearchForm()
        return self.render(request)

    def render(self, request):
        context = {'form': self.form}

        if hasattr(self, 'query'):
            # We have a query, compute the queryset
            results = self.search['manager'].all().filter(self.query).order_by('-' + self.search['date_field'])
            result_list = []
            for result in results:
                setattr(result, 'search_title', self.search['display_title'](result))
                setattr(result, 'search_summary', self.search['display_summary'](result))

                setattr(result, 'search_author', self.search['display_author'](result))
                setattr(result, 'search_date', self.search['display_date'](result))
                result_list.append(result)
            context['result_title'] = self.search['title']
            context['result_list'] = result_list

        return render(request, 'commons/search.html', context)
