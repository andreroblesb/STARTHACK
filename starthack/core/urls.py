# core/urls.py
from django.urls import path, include
from django.conf.urls import handler404, handler500
from apps.home import views  # Import views from the home app

# URL patterns for the core
urlpatterns = [
    # Include the home app urls
    path('', include('apps.home.urls')),

    # You can add more global routes if needed
    # e.g., path('admin/', admin.site.urls), 
]

# Define custom error pages if neede