from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import UserProfile

class UserRegistrationSerializer(serializers.ModelSerializer):
    # Define an email field that is write-only (not returned in responses).
    email = serializers.EmailField(write_only=True)
    # Define password and repeated_password fields, both write-only to avoid exposing them.
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        # This serializer is based on the UserProfile model.
        model = UserProfile
        # Specifies the fields that will be handled by this serializer.
        fields = ['fullname', 'email', 'password', 'repeated_password']

    def validate(self, data):
        # Custom validation method that runs before creating the user.
        
        # Check if the password and repeated password match.
        if data['password'] != data['repeated_password']:
            # Raise validation error if passwords do not match.
            raise serializers.ValidationError("Passwords do not match.")
        
        # Check if a User with the given email already exists.
        if User.objects.filter(email=data['email']).exists():
            # Raise validation error if email is already taken.
            raise serializers.ValidationError("Email is already in use.")
        
        # Return the validated data if all checks pass.
        return data

    def create(self, validated_data):
        """Extract email and password from the validated data,
        and remove repeated_password as it is no longer needed."""
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        validated_data.pop('repeated_password')

        # Create a new User instance using the email as username.
        user = User.objects.create_user(username=email, email=email, password=password)

        # Create the associated UserProfile instance with the remaining validated data.
        profile = UserProfile.objects.create(user=user, **validated_data)

        # Generate or retrieve an authentication token for the new user.
        token, _ = Token.objects.get_or_create(user=user)

        # Return a dictionary containing the token and some user info.
        return {
            'token': token.key,
            'fullname': profile.fullname,
            'email': user.email,
            'user_id': user.id
        }
    
class LoginSerializer(serializers.Serializer):
    # Define fields for email and password input.
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        # Extract the email and password from the incoming data.
        email = data.get('email')
        password = data.get('password')

        # Attempt to retrieve the User object associated with the given email.
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Raise validation error if user with this email does not exist.
            raise serializers.ValidationError("Invalid email or password.")

        # Authenticate the user with the retrieved username and provided password.
        user = authenticate(username=user.username, password=password)
        if not user:
            # Raise validation error if authentication fails.
            raise serializers.ValidationError("Invalid email or password.")

        # Add the authenticated user to the validated data for further processing.
        data['user'] = user
        return data