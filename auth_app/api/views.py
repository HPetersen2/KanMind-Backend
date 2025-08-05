from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import UserProfile
from .serializers import UserRegistrationSerializer, LoginSerializer

class UserProfileCreateView(generics.CreateAPIView):
    # Defines the queryset for this view as all UserProfile instances.
    queryset = UserProfile.objects.all()
    # Specifies the serializer class to be used for input validation and serialization.
    serializer_class = UserRegistrationSerializer
    # Allows unrestricted access to this endpoint (no authentication required).
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        # Override the default create method to customize the response.

        # Instantiate the serializer with the incoming request data.
        serializer = self.get_serializer(data=request.data)
        # Validate the input data, raising an exception if invalid.
        serializer.is_valid(raise_exception=True)
        # Save the new user and user profile, capturing the returned data.
        data = serializer.save()
        # Return a successful HTTP 201 Created response with the user data.
        return Response(data, status=status.HTTP_201_CREATED)
    

class LoginView(generics.GenericAPIView):
    # Specify the serializer that handles login validation.
    serializer_class = LoginSerializer
    # Allow any user (including unauthenticated) to access this endpoint.
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # Handle POST requests for user login.

        # Instantiate the serializer with the incoming login data.
        serializer = self.get_serializer(data=request.data)
        # Validate the credentials; raise error if invalid.
        serializer.is_valid(raise_exception=True)

        # Retrieve the authenticated User object from the validated data.
        user = serializer.validated_data['user']
        # Get or create an authentication token for the user.
        token, _ = Token.objects.get_or_create(user=user)
        # Retrieve the UserProfile associated with this user.
        profile = UserProfile.objects.get(user=user)

        # Return a HTTP 200 OK response with the authentication token and user details.
        return Response({
            'token': token.key,
            'fullname': profile.fullname,
            'email': user.email,
            'user_id': user.id
        }, status=status.HTTP_200_OK)