from rest_framework.serializers import ModelSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated

from .models import User, Profile, ActiveUser


class BadQueryPrefixException(APIException):
    status_code = 400
    default_detail = 'Malformed query: the query should start with the prefix.'


class ProfileSerializer(ModelSerializer):
    class Meta:
        model = Profile
        fields = ('avatar',)


class UserSerializer(ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ('username', 'profile', 'get_absolute_url',)


class UsernamesListView(APIView):
    """
    Return a list of available users whose username starts with the value in `query`.
    """
    permission_classes = (IsAuthenticated,)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_request_parameters(self, request):
        """
        Returns the prefix, its length and the query as a tuple.
        """
        prefix = request.query_params.get('prefix', '')
        prefix_length = len(prefix)
        query = request.query_params.get('query', None)

        if query and not query.startswith(prefix):
            raise BadQueryPrefixException()

        return (prefix, prefix_length, query)

    def get_queryset(self):
        prefix, prefix_length, query = self.get_request_parameters(self.request)
        if query and len(query) > prefix_length+1:
            qs = ActiveUser.objects.filter(username__istartswith=query[prefix_length:])
        else:
            qs = ActiveUser.objects.none()

        return qs

    def get(self, request, format=None):
        prefix, _, query = self.get_request_parameters(request)

        qs = self.get_queryset()
        usernames = ['%s%s' % (prefix, user.username) for user in qs]

        return Response({
            'query': query,
            'suggestions': usernames
        })

