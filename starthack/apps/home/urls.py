# apps/home/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='index'),  # Landing page URL
    path('login/', views.login_page, name='login'),  # Login page URL
    path('home/', views.home, name='home'),  # Dashboard index page URL
    path('register/', views.register, name='register'),  # Register page URL
    path('remove-widget/', views.remove_widget, name='remove_widget'),  # Remove widget URL
]
