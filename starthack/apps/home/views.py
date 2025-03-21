# apps/home/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.home.models import Widget, User  # Changed imports to match updated models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from decimal import Decimal
import json

def landing_page(request):
    return render(request, 'landing/index.html')  # Rendering the landing page from 'home/templates/home/'

def login_page(request):
    return render(request, 'home/login.html')  # Rendering login page from 'home/templates/home/'

# @login_required
def home(request):
    # Initialize widgets dictionary
    context = {
        'widgets': {},
        'error': None
    }
    
    try:
        # Get all widgets from database
        widgets = Widget.objects.all()
        
        # Build widgets dictionary with complete information
        for widget in widgets:
            key_name = widget.name.lower().replace(' ', '_').replace('-', '_')
            context['widgets'][key_name + '_widget'] = {
                'id': widget.id,
                'name': widget.name,
                'source_id': widget.source_id,
                'active': widget.active,
                'position_x': widget.position_x,
                'position_y': widget.position_y,
                'width': widget.width,
                'height': widget.height,
                'cost': widget.cost
            }
        
        # Get user profile information if available
        try:
            user = User.objects.first()
            if user:
                context['user_profile'] = {
                    'name': user.name,
                    'widget_fee': user.widget_fee,
                    'cost_saving': user.costs_saved
                }
        except User.DoesNotExist:
            pass
            
    except Exception as e:
        context['error'] = str(e)
    
    print(context)
    # Count active widgets
    active_count = sum(1 for widget in context['widgets'].values() if widget['active'])
    print(f"Number of active widgets: {active_count}")
    
    # retrieve fee acumulated
    try:
        user = User.objects.first()
        if user:
            context['fee'] = float(user.widget_fee)
    except User.DoesNotExist:
        context['fee'] = 0
    
    return render(request, 'home/index.html', context)

def register(request):
    return render(request, 'home/register.html')  # Rendering the register page from 'home/templates/home/'

@csrf_exempt  # ⚠️ Use CSRF token instead if possible
@transaction.atomic
def remove_widget(request):
    try:
        data = json.loads(request.body)
        widget_id = data.get("widget_id")

        widget = Widget.objects.select_for_update().filter(source_id=widget_id).first()
        user = User.objects.select_for_update().first()

        if widget and user:
            if widget.active:  # Only update if widget is currently active
                widget.active = False
                widget.save()
                
                # Update fee using Decimal
                user.widget_fee = user.widget_fee - Decimal(str(widget.cost))
                user.save()

            return JsonResponse({
                "success": True,
                "message": f"Widget {widget_id} removed.",
                "new_fee": float(user.widget_fee),
                "widget_id": widget_id
            })
        else:
            return JsonResponse({"success": False, "error": "Widget or user not found."}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)
    
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

@csrf_exempt
@transaction.atomic
def add_widget(request):
    try:
        data = json.loads(request.body)
        widget_id = data.get("widget_id")

        widget = Widget.objects.select_for_update().filter(source_id=widget_id).first()
        user = User.objects.select_for_update().first()

        if widget and user:
            if not widget.active:  # Only update if widget isn't already active
                widget.active = True
                widget.save()
                
                # Update fee using Decimal
                user.widget_fee = user.widget_fee + Decimal(str(widget.cost))
                user.save()

            return JsonResponse({
                "success": True,
                "message": f"Widget {widget_id} added.",
                "new_fee": float(user.widget_fee),
                "widget_id": widget_id
            })
        else:
            return JsonResponse({"success": False, "error": "Widget or user not found."}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
