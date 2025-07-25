from django.urls import path, include
from .views import UserProfileCreateView, LoginView

urlpatterns = [
    path('registration/', UserProfileCreateView.as_view(), name='user-register'),
    path('login/', LoginView.as_view(), name='user-login'),
]