import time


from django.core.cache import cache

from rest_framework.response import Response
from rest_framework import status
from rest_framework.serializers import ModelSerializer
from rest_framework.generics import ListAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.fields import CharField

from .models import Notification


class NotificationSerializer(ModelSerializer):
    """A serializer for the Notifications"""
    show_and_dismiss_url = CharField(source='show_url')
    dismiss_url = CharField()
    show_url = CharField(source='action')

    class Meta:
        model = Notification
        fields = ('id', 'title', 'description', 'date', 'icon', 'show_url', 'show_and_dismiss_url', 'dismiss_url')


class NotificationApiView(DestroyAPIView):
    model = Notification
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        if response.status_code == 204:
            # Because of an old stupid bug in Firefox
            response.data = '1'
        return response


class NotificationsListApiView(ListAPIView):
    model = Notification
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    def list(self, request, *args, **kwargs):
        cached_hash = cache.get_or_set('cache-notifications-{}'.format(request.user.username), str(hash(time.time())), 60)
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
