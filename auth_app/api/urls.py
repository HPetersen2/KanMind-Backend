from django.urls import path, include
from .views import UserProfileCreateView, LoginView

# URL patterns define the routing for the user-related endpoints.
urlpatterns = [
    # Route for user registration.
    # Maps the URL path 'registration/' to the UserProfileCreateView class-based view.
    # Named 'user-register' for easy reference in templates or reverse lookups.
    path('registration/', UserProfileCreateView.as_view(), name='user-register'),

    # Route for user login.
    # Maps the URL path 'login/' to the LoginView class-based view.
    # Named 'user-login' for consistent reference throughout the project.
    path('login/', LoginView.as_view(), name='user-login'),
]