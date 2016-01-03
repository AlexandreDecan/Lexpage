from rest_framework.serializers import ModelSerializer
from .models import User, Profile

class ProfileSerializer(ModelSerializer):
    class Meta:
        model = Profile
        fields = ('avatar',)

class UserSerializer(ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ('username', 'profile', 'get_absolute_url',)

