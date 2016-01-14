from rest_framework.serializers import ModelSerializer
from rest_framework.generics import ListAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.fields import CharField
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict


from .models import Notification

class NotificationPagination(PageNumberPagination):
    """Custom pagination for the notifications.
    We use that to limit the number of notification shown to the user.
    We also add page number and page count to the reponse.
    """
    page_size = 5

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('current_page', self.page.number),
            ('total_pages', self.page.paginator.num_pages),
            ('results', data)
        ]))

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


class NotificationsListApiView(ListAPIView):
    model = Notification
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = NotificationPagination

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)
