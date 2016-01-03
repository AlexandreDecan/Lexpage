from .models import Message
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ReadOnlyModelViewSet
from profile.api import UserSerializer
from rest_framework.pagination import PageNumberPagination

class LatestMessagesPagination(PageNumberPagination):
    """Custom pagination for the minichat.
    We use that to maybe later have a "load more" button to the minichat to get more history without
    going to the archives.
    To achieve that, we will need to set "page_query_param" and "max_page_size".
    """
    page_size = 10

class MessageSerializer(ModelSerializer):
    """A serializer for the minichat messages with the enhanced user serializer that comes in the
    profile app, so we get the username and the avatar in the same request that the minichat
    messages."""
    user = UserSerializer()
    class Meta:
        model = Message
        fields = ('user', 'text', 'date',)

class LatestMessagesViewSet(ReadOnlyModelViewSet):
    """A viewset that returns the latest messages, 10 by 10."""
    queryset = Message.objects.all().order_by('-date')
    serializer_class = MessageSerializer
    pagination_class = LatestMessagesPagination

