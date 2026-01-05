from django.contrib.auth.models import User

from rest_framework import serializers

from .models import Profile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ["id", "user", "email_verified"]
