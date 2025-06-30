from django.contrib.auth.models import User
from rest_framework import serializers
from user_auth_app.models import UserProfile

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['firstName', 'lastName', 'email', 'user_id']