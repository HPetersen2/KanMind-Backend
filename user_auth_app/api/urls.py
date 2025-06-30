from django.urls import path
from .views import UserView


urlpatterns = [
    path('user/<int:pk>/', UserView.as_view(),  name='usertest')
]
