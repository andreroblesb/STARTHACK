# Generated by Django 3.2.16 on 2025-03-20 16:58

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_rename_user_userwidget_user_profile'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('widget_fee', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
                ('costs_saved', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
            ],
        ),
        migrations.RemoveField(
            model_name='userwidget',
            name='user_profile',
        ),
        migrations.RemoveField(
            model_name='userwidget',
            name='widget',
        ),
        migrations.RenameField(
            model_name='widget',
            old_name='active_by_default',
            new_name='active',
        ),
        migrations.DeleteModel(
            name='UserProfile',
        ),
        migrations.DeleteModel(
            name='UserWidget',
        ),
    ]
