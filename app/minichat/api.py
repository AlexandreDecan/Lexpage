from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.fields import CharField
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import APIException

from .models import Message

from profile.api import UserSerializer
from notifications import notify

from minichat.templatetags.minichat import urlize3
from commons.templatetags.markup_bbcode import smiley
from django.contrib.humanize.templatetags.humanize import naturalday
from django.template.defaultfilters import time
from django.contrib import messages

class BadSubstituteException(APIException):
    status_code = 400
    default_detail = 'Malformed substitute'


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


class PostedMessageSerializer(MessageSerializer):
    """A subclass of MessageSerializer that only contains the text field, because there is no need
    to be able to modify the other messages."""
    class Meta:
        model = Message
        fields = ('text',)


class LatestMessagesViewSet(ReadOnlyModelViewSet):
    """A viewset that returns the latest messages, 10 by 10."""
    queryset = Message.objects.order_by('-date')
    serializer_class = MessageSerializer
    pagination_class = LatestMessagesPagination

class MessagePostView(CreateAPIView):
    """
    Handle message submission.
    """
    model = Message
    permission_classes = (IsAuthenticated,)
    serializer_class = PostedMessageSerializer

    def patch(self, request):
        """Handles simple substitution"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid()
        validated_data = serializer.validated_data
        validated_data['user'] = self.request.user
        message = Message(**validated_data)
        substitute = message.substitute()
        if substitute:
            substitute.save()
            return Response(MessageSerializer(substitute).data)
        else:
            raise BadSubstituteException

    def get_queryset(self):
        qs = Message.objects.filter(user=self.request.user).order_by('-date')
        return qs

    def perform_create(self, serializer):
        message = serializer.save(user=self.request.user)

        # Notify users that are anchored in this message
        anchors = message.parse_anchors()
        for anchor in anchors:
            notify.minichat_warn(anchor, message)

        # Warn the user that we notified the other users
        if len(anchors) > 0:
            if len(anchors) > 1:
                anchors_text = ', '.join([x.get_username() for x in anchors[:-2]]) + ' et ' + anchors[-1].get_username()
            else:
                anchors_text = anchors[0].get_username()
            messages.success(self.request._request, 'Une notification a été envoyée à %s suite à votre message sur le minichat.' % anchors_text)

        return message

    class Meta:
        fields = ('text',)

