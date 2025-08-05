"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

# The main URL patterns for the Django project.
urlpatterns = [
    # Route for the Django admin interface.
    # The URL path 'admin/' is mapped to the built-in admin site URLs.
    path('admin/', admin.site.urls),

    # Route to include the API endpoints from the 'core' app.
    # All URLs starting with 'api/' will be handled by the URL configurations
    # defined in the 'core.api_urls' module.
    path('api/', include('core.api_urls')),
]
