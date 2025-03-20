# apps/home/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.home.models import Widget, User  # Changed imports to match updated models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
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
    
    return render(request, 'home/index.html', context)

def register(request):
    return render(request, 'home/register.html')  # Rendering the register page from 'home/templates/home/'

@csrf_exempt  # ⚠️ Use CSRF token instead if possible
def remove_widget(request):
    try:
        data = json.loads(request.body)
        widget_id = data.get("widget_id")
        print("WTF", widget_id)

        if not widget_id:
            return JsonResponse({"success": False, "error": "No widget_id provided"}, status=400)

        widget = Widget.objects.filter(source_id=widget_id).first()

        if not widget:
            return JsonResponse({"success": False, "error": "Widget not found"}, status=404)

        # ✅ Deactivate the widget instead of deleting it
        widget.active = False
        widget.save()

        return JsonResponse({"success": True, "message": f"Widget {widget_id} removed."})
    
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)
    
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

@csrf_exempt
def add_widget(request):
    try:
        data = json.loads(request.body)  # Parse JSON from AJAX request
        widget_id = data.get("widget_id")

        # Modify this based on your actual model name
        from .models import Widget  # ✅ Import your model

        widget = Widget.objects.filter(source_id=widget_id).first()

        if widget:
            widget.active = True  # ✅ Activate the widget
            widget.save()

            return JsonResponse({"success": True, "message": f"Widget {widget_id} added."})
        else:
            return JsonResponse({"success": False, "error": "Widget not found."}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
