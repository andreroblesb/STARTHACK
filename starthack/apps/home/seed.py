# -*- encoding: utf-8 -*-
"""
Seed script to populate database with widgets and create test user
"""

import os
import django
import sys

# Add project directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.home.models import Widget, User
from django.db import transaction
from decimal import Decimal

def create_widgets():
    """Create widgets based on index.html configuration"""
    widgets = [
        {
            'name': 'Sustainability score',
            'cost': Decimal('5.99'),
            'source_id': 'sustainability-card-original',
            'active': True,  # Changed from active_by_default to active
            'position_x': 0,
            'position_y': 0,
            'width': 8,
            'height': 5
        },
        {
            'name': 'Top-k inefficient devices',
            'cost': Decimal('5.99'),
            'source_id': 'top-k-inefficient-card-original',
            'active': True,  # Changed from active_by_default to active
            'position_x': 8,
            'position_y': 0,
            'width': 4,
            'height': 5
        },
        {
            'name': 'Energy consumption per day-blocks',
            'cost': Decimal('5.99'),
            'source_id': 'energy-day-blocks-card-original',
            'active': True,  # Changed from active_by_default to active
            'position_x': 0,
            'position_y': 5,
            'width': 4,
            'height': 5
        },
        {
            'name': 'Top-k power consuming devices',
            'cost': Decimal('5.99'),
            'source_id': 'top-k-power-card-original',
            'active': True,  # Changed from active_by_default to active
            'position_x': 4,
            'position_y': 5,
            'width': 4,
            'height': 5
        },
        {
            'name': 'Predictive maintenance alerts',
            'cost': Decimal('5.99'),
            'source_id': 'maintenance-card-original',
            'active': False,  # Changed from active_by_default to active
            'position_x': 8,
            'position_y': 5,
            'width': 4,
            'height': 5
        },
        {
            'name': 'Device amortization',
            'cost': Decimal('5.99'),
            'source_id': 'amortization-card-original',
            'active': False,  # Changed from active_by_default to active
            'position_x': 0,
            'position_y': 10,
            'width': 4,
            'height': 5
        },
        {
            'name': 'Efficiency metrics',
            'cost': Decimal('5.99'),
            'source_id': 'efficiency-card-original',
            'active': False,  # Changed from active_by_default to active
            'position_x': 4,
            'position_y': 10,
            'width': 4,
            'height': 5
        },
        {
            'name': 'Energy advisor chatbot',
            'cost': Decimal('5.99'),
            'source_id': 'chatbot-card-original',
            'active': False,  # Changed from active_by_default to active
            'position_x': 8,
            'position_y': 10,
            'width': 4,
            'height': 5
        }
    ]
    
    created_widgets = []
    for widget_data in widgets:
        # Ensure no widget_id field is passed
        if 'widget_id' in widget_data:
            del widget_data['widget_id']
            
        widget, created = Widget.objects.update_or_create(
            source_id=widget_data['source_id'],
            defaults=widget_data
        )
        status = "Created" if created else "Updated"
        print(f"{status} widget: {widget.name}")
        created_widgets.append(widget)
    
    return created_widgets

def create_user(name, active_widgets):
    """Create a user with associated widget costs"""
    # Calculate total widget fee
    total_fee = sum(widget.cost for widget in active_widgets)
    costs_saved = total_fee * Decimal('0.15')  # 15% savings
    
    # Create and save user
    user = User.objects.create(
        name=name,
        widget_fee=total_fee,
        costs_saved=costs_saved
    )

    print(f"Created user: {name}")
    print(f"Monthly widget fee: {total_fee} CHF")
    print(f"Monthly savings: {costs_saved} CHF")

    return user


@transaction.atomic
def run_seed():
    """Main function to seed the database"""
    print("Creating widgets...")
    widgets = create_widgets()
    
    # Get only active widgets
    active_widgets = [widget for widget in widgets if widget.active]
    
    print("\nCreating user with widgets...")
    user = create_user(
        name='Michael Johnson',
        active_widgets=active_widgets
    )
    
    print("\nSeeding completed successfully!")
    print(f"User '{user.name}' has {len(active_widgets)} active widgets")

if __name__ == '__main__':
    print("Starting seeding process...")
    run_seed()
    print("Done!")
