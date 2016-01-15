from rest_framework import serializers, viewsets, mixins
from profile.api import UserSerializer
from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    author = UserSerializer()

    class Meta:
        model = Message
        fields = ('author', 'text', 'date',)


class MessageViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = MessageSerializer
    queryset = Message.objects
