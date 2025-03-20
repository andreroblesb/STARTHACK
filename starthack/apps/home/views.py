# apps/home/views.py

from django.shortcuts import render

def landing_page(request):
    return render(request, 'landing/index.html')  # Rendering the landing page from 'home/templates/home/'

def login_page(request):
    return render(request, 'home/login.html')  # Rendering login page from 'home/templates/home/'

def index(request):
    return render(request, 'home/index.html')  # Rendering the dashboard index page from 'home/templates/home/'

def register(request):
    return render(request, 'home/register.html')  # Rendering the register page from 'home/templates/home/'

