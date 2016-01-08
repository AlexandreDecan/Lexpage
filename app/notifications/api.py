from rest_framework.serializers import ModelSerializer
from rest_framework.generics import ListAPIView, DestroyAPIView
from .models import Notification
from rest_framework.permissions import IsAuthenticated
from rest_framework.fields import CharField

class NotificationSerializer(ModelSerializer):
    """A serializer for the Notifications"""
    show_url = CharField()
    dismiss_url = CharField()

    class Meta:
        model = Notification
        fields = ('id', 'title', 'description', 'action', 'recipient', 'app', 'key', 'date', 'show_url', 'dismiss_url')


class NotificationApiView(DestroyAPIView):
    model = Notification
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

class NotificationsListApiView(ListAPIView):
    model = Notification
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)
