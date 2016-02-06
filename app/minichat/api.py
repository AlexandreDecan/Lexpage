import time
import datetime

from rest_framework.response import Response
from rest_framework import status
from rest_framework.serializers import ModelSerializer, ValidationError
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.fields import CharField
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import APIException

from django.core.cache import cache
from .models import Message

from profile.api import UserSerializer

from minichat.templatetags.minichat import urlize3
from commons.templatetags.markup_bbcode import smiley


class BadSubstituteException(APIException):
    status_code = 400
    default_detail = 'Malformed substitute'


class MinichatTextField(CharField):
    def to_representation(self, value):
        return super().to_representation(smiley(urlize3(value)))


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
        else:
            return field_class, field_kwargs


class PostedMessageSerializer(MessageSerializer):
    """A subclass of MessageSerializer that only contains the text field, because there is no need
    to be able to modify the other messages."""
    class Meta:
        model = Message
        fields = ('text',)


class MinichatLatestMessagesView(ListAPIView):
    model = Message
    serializer_class = MessageSerializer

    def get_queryset(self):
        return Message.objects.order_by('-date')[:20]

    def list(self, request, *args, **kwargs):
        cached_hash = cache.get_or_set('cache-minichat', str(hash(time.time())), 60)
        if request.query_params.get('hash', None) == cached_hash:
            # Manually set the response with content to prevent a bug in Firefox
            response = Response('1', content_type='text/html', status=status.HTTP_304_NOT_MODIFIED)
        else:
            response = super().list(request, *args, **kwargs)
            response.data = {
                'results': response.data,
                'hash': cached_hash
            }
        return response


class MinichatMessagePostView(CreateAPIView):
    """
    Handle message submission.
    We need CreateAPIView because there is ONE method we do not overwrite: get_success_headers
    """
    model = Message
    permission_classes = (IsAuthenticated,)
    serializer_class = PostedMessageSerializer

    def post(self, request, *args, **kwargs):
        """Handles simple substitution and message posting"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        validated_data['user'] = self.request.user
        message = Message(**validated_data)
        substitute = message.substitute()
        if substitute:
            if datetime.datetime.now() - substitute.date <= datetime.timedelta(minutes=5):
                substitute.save()
                headers = self.get_success_headers(serializer.data)
                data = serializer.data

                data['substituted'] = PostedMessageSerializer(substitute).data
                return Response(data, status=status.HTTP_200_OK, headers=headers)
            else:
                # Notice that ValidationError comes from rest_framework.serializers, not Django!
                raise ValidationError('Un message ne peut être modifié que dans les 5 minutes qui suivent sa création.')
        else:
            self.perform_create(serializer)
            data_with_anchors = serializer.data
            data_with_anchors['anchors'] = [anchor.get_username() for anchor in message.parse_anchors()]
            headers = self.get_success_headers(serializer.data)
            return Response(data_with_anchors, status=status.HTTP_201_CREATED, headers=headers)

    class Meta:
        fields = ('text',)

