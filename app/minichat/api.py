from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.fields import CharField

from .models import Message

from profile.api import UserSerializer

from minichat.templatetags.minichat import urlize3
from commons.templatetags.markup_bbcode import smiley
from django.contrib.humanize.templatetags.humanize import naturalday
from django.template.defaultfilters import time


class MinichatTextField(CharField):
    def to_representation(self, value):
        return super().to_representation(smiley(urlize3(value)))

class MinichatDateField(CharField):
    def to_representation(self, value):
        message_date = naturalday(value, 'l j b.')
        message_time = time(value)
        return [message_date, message_time]

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

    def build_standard_field(self, field_name, model_field):
        field_class, field_kwargs = super(MessageSerializer, self).build_standard_field(field_name, model_field)
        if field_name == 'text':
            return MinichatTextField, field_kwargs
        elif field_name == 'date':
            return MinichatDateField, field_kwargs
        else:
            return field_class, field_kwargs

class LatestMessagesViewSet(ReadOnlyModelViewSet):
    """A viewset that returns the latest messages, 10 by 10."""
    queryset = Message.objects.order_by('-date')
    serializer_class = MessageSerializer
    pagination_class = LatestMessagesPagination

