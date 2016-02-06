import django
import random
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.http import etag

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


def _etag_func(request, *args, **kwargs):
    username = request.user.username
    return cache.get_or_set('etag-notifications-{}'.format(username), lambda: str(random.random()), 60)


class NotificationsListApiView(ListAPIView):
    model = Notification
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    @method_decorator(etag(_etag_func))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
