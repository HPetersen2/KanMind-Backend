from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import UserProfile

class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = UserProfile
        fields = ['fullname', 'email', 'password', 'repeated_password']

    def validate(self, data):
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError("Passwörter stimmen nicht überein.")
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("E-Mail ist bereits vergeben.")
        return data

    def create(self, validated_data):
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        validated_data.pop('repeated_password')

        user = User.objects.create_user(username=email, email=email, password=password)

        profile = UserProfile.objects.create(user=user, **validated_data)

        token, _ = Token.objects.get_or_create(user=user)

        return {
            'token': token.key,
            'fullname': profile.fullname,
            'email': user.email,
            'user_id': user.id
        }
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Ungültige E-Mail oder Passwort.")

        user = authenticate(username=user.username, password=password)
        if not user:
            raise serializers.ValidationError("Ungültige E-Mail oder Passwort.")

        data['user'] = user
        return data