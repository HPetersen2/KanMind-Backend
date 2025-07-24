from django.urls import path, include
from .views import UserProfileList

urlpatterns = [
    path('registration/', UserProfileList.as_view()),
]