from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import APIException
from .models import BlogPost


class EmptyQueryException(APIException):
    status_code = 400
    default_detail = 'Empty query'


class TagsListView(APIView):
    """
    Autocomplete-feature for the tags.
    """

    def get_queryset(self):
        query = self.request.query_params.get('query', None)

        if not query:
            raise EmptyQueryException

        return BlogPost.published.filter(tags__icontains=query)

    def get(self, request):
        query = request.query_params.get('query', None)
        posts = self.get_queryset()
        suggestions = []
        count = {}

        # Count the number of posts for each tag...
        for post in posts:
            for tag in [x for x in post.tags.split(' ') if query in x]:
                count[tag] = count.setdefault(tag, 0) + 1

        # ... and sort it
        ordered_count = list(count.items())
        ordered_count.sort(key=lambda x: x[1], reverse=True)
        for tag, nb in ordered_count:
            suggestion = {'value': tag, 'data': nb}
            suggestions.append(suggestion)

        return Response({
            'query': query,
            'suggestions': suggestions,
        })

