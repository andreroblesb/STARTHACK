from django.db import models
from decimal import Decimal

# Widget Model
class Widget(models.Model):
    name = models.CharField(max_length=100, unique=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    source_id = models.CharField(max_length=100, unique=True)  # Ensure unique HTML source ID
    active = models.BooleanField(default=False)
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)
    width = models.IntegerField(default=4)
    height = models.IntegerField(default=5)

    def __str__(self):
        return f"{self.name} (${self.cost})"

# Many-to-Many Relationship Model
class User(models.Model):  # Inherit from models.Model
    name = models.CharField(max_length=100)
    widget_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    costs_saved = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return f"{self.name} (${self.widget_fee})"
    def __str__(self):
        return f"{self.name} (${self.widget_fee})"